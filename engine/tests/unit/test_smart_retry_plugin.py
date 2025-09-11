"""Unit tests for Smart Retry Plugin."""

import pytest
import time
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

# Add internal-plugins to path
internal_plugins_path = os.path.join(project_root, "internal-plugins")
sys.path.insert(0, internal_plugins_path)

from unittest.mock import Mock, patch, MagicMock

# Import directly from the smart_retry module
from smart_retry.plugin import (
    SmartRetryPlugin, 
    SmartRetryProcessor, 
    SmartRetryStep
)


class TestSmartRetryPlugin:
    """Test suite for Smart Retry plugin."""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance."""
        return SmartRetryPlugin()
    
    @pytest.fixture
    def processor(self):
        """Create processor instance."""
        return SmartRetryProcessor()
    
    @pytest.fixture
    def mock_page(self):
        """Create mock page object."""
        page = Mock()
        page.url = "https://example.com"
        page.query_selector_all = Mock(return_value=[])
        return page
    
    @pytest.fixture
    def mock_context(self):
        """Create mock context object."""
        return Mock()
    
    def test_plugin_metadata(self, plugin):
        """Test plugin metadata is correct."""
        metadata = plugin.metadata
        assert metadata.name == "smart-retry"
        assert metadata.version == "1.0.0"
        assert "SmartRetryStep" in metadata.supported_step_types
        assert metadata.enabled is True
    
    def test_plugin_get_processors(self, plugin):
        """Test plugin returns correct processors."""
        processors = plugin.get_processors()
        assert len(processors) == 1
        assert isinstance(processors[0], SmartRetryProcessor)
    
    def test_processor_can_handle(self, processor):
        """Test processor can handle SmartRetryStep."""
        step = SmartRetryStep(**{
            "@max-attempts": 3,
            "@backoff": "exponential",
            "@base-delay": 1000,
            "@step": {"@xpath": "//div", "@fields": {"text": "./text()"}}
        })
        assert processor.can_handle(step) is True
        
        # Test with non-SmartRetryStep
        other_step = Mock()
        assert processor.can_handle(other_step) is False
    
    def test_exponential_backoff_calculation(self, processor):
        """Test exponential backoff delay calculation."""
        step = SmartRetryStep(**{
            "@max-attempts": 3,
            "@backoff": "exponential",
            "@base-delay": 1000,
            "@max-delay": 10000,
            "@jitter": False,
            "@step": {"@xpath": "//div", "@fields": {}}
        })
        
        # Test exponential growth
        delay1 = processor._calculate_delay(step, 1)
        delay2 = processor._calculate_delay(step, 2)
        delay3 = processor._calculate_delay(step, 3)
        
        assert delay1 == 1000  # base_delay * 2^0
        assert delay2 == 2000  # base_delay * 2^1
        assert delay3 == 4000  # base_delay * 2^2
    
    def test_linear_backoff_calculation(self, processor):
        """Test linear backoff delay calculation."""
        step = SmartRetryStep(**{
            "@max-attempts": 3,
            "@backoff": "linear",
            "@base-delay": 1000,
            "@max-delay": 10000,
            "@jitter": False,
            "@step": {"@xpath": "//div", "@fields": {}}
        })
        
        delay1 = processor._calculate_delay(step, 1)
        delay2 = processor._calculate_delay(step, 2)
        delay3 = processor._calculate_delay(step, 3)
        
        assert delay1 == 1000  # base_delay * 1
        assert delay2 == 2000  # base_delay * 2
        assert delay3 == 3000  # base_delay * 3
    
    def test_fixed_backoff_calculation(self, processor):
        """Test fixed backoff delay calculation."""
        step = SmartRetryStep(**{
            "@max-attempts": 3,
            "@backoff": "fixed",
            "@base-delay": 2000,
            "@jitter": False,
            "@step": {"@xpath": "//div", "@fields": {}}
        })
        
        delay1 = processor._calculate_delay(step, 1)
        delay2 = processor._calculate_delay(step, 2)
        
        assert delay1 == 2000
        assert delay2 == 2000
    
    def test_max_delay_cap(self, processor):
        """Test that delays are capped at max_delay."""
        step = SmartRetryStep(**{
            "@max-attempts": 10,
            "@backoff": "exponential",
            "@base-delay": 1000,
            "@max-delay": 5000,
            "@jitter": False,
            "@step": {"@xpath": "//div", "@fields": {}}
        })
        
        # Large attempt number should be capped
        delay = processor._calculate_delay(step, 10)
        assert delay == 5000  # Should be capped at max_delay
    
    def test_jitter_adds_randomization(self, processor):
        """Test that jitter adds randomization to delays."""
        step = SmartRetryStep(**{
            "@max-attempts": 3,
            "@backoff": "fixed",
            "@base-delay": 1000,
            "@jitter": True,
            "@step": {"@xpath": "//div", "@fields": {}}
        })
        
        # Get multiple delays with jitter
        delays = [processor._calculate_delay(step, 1) for _ in range(10)]
        
        # With jitter, not all delays should be the same
        assert len(set(delays)) > 1
        # But all should be within 10% of base delay
        for delay in delays:
            assert 900 <= delay <= 1100
    
    def test_error_classification(self, processor):
        """Test error classification for retry decisions."""
        # Timeout errors
        assert processor._classify_error(TimeoutError("timeout")) == "timeout"
        assert processor._classify_error(Exception("Request timeout")) == "timeout"
        
        # Network errors
        assert processor._classify_error(ConnectionError("connection failed")) == "network"
        assert processor._classify_error(Exception("Network error")) == "network"
        
        # 5xx errors
        assert processor._classify_error(Exception("HTTP 502 Bad Gateway")) == "5xx"
        assert processor._classify_error(Exception("503 Service Unavailable")) == "5xx"
        
        # Server errors
        assert processor._classify_error(Exception("500 Internal Server Error")) == "server-error"
        
        # Not found
        assert processor._classify_error(Exception("404 Not Found")) == "not-found"
        
        # Auth errors
        assert processor._classify_error(Exception("403 Forbidden")) == "auth"
        assert processor._classify_error(Exception("401 Unauthorized")) == "auth"
        
        # Unknown
        assert processor._classify_error(Exception("Something else")) == "unknown"
    
    def test_should_retry_error(self, processor):
        """Test retry decision based on error type."""
        step = SmartRetryStep(**{
            "@max-attempts": 3,
            "@retry-on": ["timeout", "network"],
            "@step": {"@xpath": "//div", "@fields": {}}
        })
        
        assert processor._should_retry_error("timeout", step.retry_on_errors) is True
        assert processor._should_retry_error("network", step.retry_on_errors) is True
        assert processor._should_retry_error("auth", step.retry_on_errors) is False
        assert processor._should_retry_error("unknown", step.retry_on_errors) is False
    
    @patch('smart_retry.plugin.SmartRetryProcessor._execute_target_step')
    def test_successful_execution_first_try(self, mock_execute, processor, mock_context, mock_page):
        """Test successful execution on first attempt."""
        step = SmartRetryStep(**{
            "@max-attempts": 3,
            "@backoff": "exponential",
            "@base-delay": 1000,
            "@step": {"@xpath": "//div", "@fields": {"text": "./text()"}}
        })
        
        mock_execute.return_value = [{"text": "Success"}]
        
        results = processor.execute(mock_context, mock_page, step)
        
        assert results == [{"text": "Success"}]
        assert mock_execute.call_count == 1
    
    @patch('smart_retry.plugin.SmartRetryProcessor._execute_target_step')
    @patch('time.sleep')
    def test_retry_on_failure(self, mock_sleep, mock_execute, processor, mock_context, mock_page):
        """Test retry logic on failures."""
        step = SmartRetryStep(**{
            "@max-attempts": 3,
            "@backoff": "fixed",
            "@base-delay": 1000,
            "@retry-on": ["timeout"],
            "@jitter": False,
            "@step": {"@xpath": "//div", "@fields": {"text": "./text()"}}
        })
        
        # Fail twice, then succeed
        mock_execute.side_effect = [
            TimeoutError("Timeout"),
            TimeoutError("Timeout"),
            [{"text": "Success"}]
        ]
        
        results = processor.execute(mock_context, mock_page, step)
        
        assert results == [{"text": "Success"}]
        assert mock_execute.call_count == 3
        # Sleep should be called twice (not on last attempt)
        assert mock_sleep.call_count == 2
        # Check delay values
        mock_sleep.assert_any_call(1.0)  # 1000ms = 1s
    
    @patch('smart_retry.plugin.SmartRetryProcessor._execute_target_step')
    def test_all_attempts_fail(self, mock_execute, processor, mock_context, mock_page):
        """Test behavior when all retry attempts fail."""
        step = SmartRetryStep(**{
            "@max-attempts": 2,
            "@backoff": "fixed",
            "@base-delay": 100,
            "@retry-on": ["network"],
            "@step": {"@xpath": "//div", "@fields": {}}
        })
        
        mock_execute.side_effect = ConnectionError("Network error")
        
        results = processor.execute(mock_context, mock_page, step)
        
        assert results == []  # Should return empty list on failure
        assert mock_execute.call_count == 2
    
    @patch('smart_retry.plugin.SmartRetryProcessor._execute_target_step')
    def test_non_retryable_error(self, mock_execute, processor, mock_context, mock_page):
        """Test that non-retryable errors don't trigger retries."""
        step = SmartRetryStep(**{
            "@max-attempts": 3,
            "@backoff": "fixed",
            "@base-delay": 1000,
            "@retry-on": ["timeout"],  # Only retry timeouts
            "@step": {"@xpath": "//div", "@fields": {}}
        })
        
        # Auth error should not be retried
        mock_execute.side_effect = Exception("403 Forbidden")
        
        results = processor.execute(mock_context, mock_page, step)
        
        assert results == []
        assert mock_execute.call_count == 1  # Should not retry
    
    def test_metrics_tracking(self, processor, mock_context, mock_page):
        """Test that metrics are properly tracked."""
        step = SmartRetryStep(**{
            "@max-attempts": 1,
            "@backoff": "fixed",
            "@base-delay": 100,
            "@step": {"@xpath": "//div", "@fields": {}}
        })
        
        with patch.object(processor, '_execute_target_step', return_value=[{"text": "Success"}]):
            processor.execute(mock_context, mock_page, step)
        
        metrics = processor.get_retry_metrics()
        assert "fixed_1" in metrics
        assert metrics["fixed_1"]["successes"] == 1
        assert metrics["fixed_1"]["failures"] == 0
        assert metrics["fixed_1"]["total_attempts"] == 1
    
    def test_plugin_finalize(self, plugin):
        """Test plugin cleanup."""
        processor = plugin.get_processors()[0]
        processor.retry_metrics = {"test": {"successes": 1}}
        
        plugin.finalize()
        
        # Should clear processor reference
        plugin.finalize()  # Should not error even if called twice