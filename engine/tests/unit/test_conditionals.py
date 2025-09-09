import pytest
from unittest.mock import MagicMock, patch
from engine.web_engine.conditionals import ConditionEvaluator, ConditionalProcessor
from engine.web_engine.models import ConditionSpec, ConditionalStep, ExtractStep


class TestConditionEvaluator:
    def test_exists_condition_true(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        element = MagicMock()
        page.query_selector.return_value = element
        
        condition = ConditionSpec(**{"@exists": "#premium-content"})
        result = evaluator.evaluate(page, condition)
        
        assert result is True
        page.query_selector.assert_called_once_with("#premium-content")
    
    def test_exists_condition_false(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        page.query_selector.return_value = None
        
        condition = ConditionSpec(**{"@exists": "#premium-content"})
        result = evaluator.evaluate(page, condition)
        
        assert result is False
        page.query_selector.assert_called_once_with("#premium-content")
    
    def test_exists_condition_xpath(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        element = MagicMock()
        page.query_selector.return_value = element
        
        condition = ConditionSpec(**{"@exists": "//div[@class='premium']"})
        result = evaluator.evaluate(page, condition)
        
        assert result is True
        page.query_selector.assert_called_once_with("xpath=//div[@class='premium']")
    
    def test_not_exists_condition_true(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        page.query_selector.return_value = None
        
        condition = ConditionSpec(**{"@not-exists": "#ads"})
        result = evaluator.evaluate(page, condition)
        
        assert result is True
        page.query_selector.assert_called_once_with("#ads")
    
    def test_not_exists_condition_false(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        element = MagicMock()
        page.query_selector.return_value = element
        
        condition = ConditionSpec(**{"@not-exists": "#ads"})
        result = evaluator.evaluate(page, condition)
        
        assert result is False
        page.query_selector.assert_called_once_with("#ads")
    
    def test_contains_condition_page_text_true(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        page.text_content.return_value = "Welcome to our premium content section"
        
        condition = ConditionSpec(**{"@contains": "premium content"})
        result = evaluator.evaluate(page, condition)
        
        assert result is True
        page.text_content.assert_called_once()
    
    def test_contains_condition_page_text_false(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        page.text_content.return_value = "Welcome to our basic content section"
        
        condition = ConditionSpec(**{"@contains": "premium content"})
        result = evaluator.evaluate(page, condition)
        
        assert result is False
        page.text_content.assert_called_once()
    
    def test_contains_condition_element_text_true(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        element = MagicMock()
        element.text_content.return_value = "Premium User Badge"
        page.query_selector.return_value = element
        
        condition = ConditionSpec(**{
            "@contains": "Premium",
            "@selector": ".user-badge"
        })
        result = evaluator.evaluate(page, condition)
        
        assert result is True
        page.query_selector.assert_called_once_with(".user-badge")
        element.text_content.assert_called_once()
    
    def test_contains_condition_element_text_false(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        element = MagicMock()
        element.text_content.return_value = "Basic User Badge"
        page.query_selector.return_value = element
        
        condition = ConditionSpec(**{
            "@contains": "Premium",
            "@selector": ".user-badge"
        })
        result = evaluator.evaluate(page, condition)
        
        assert result is False
    
    def test_count_condition_exact_true(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        elements = [MagicMock(), MagicMock(), MagicMock()]  # 3 elements
        page.query_selector_all.return_value = elements
        
        condition = ConditionSpec(**{
            "@count": 3,
            "@selector": ".item"
        })
        result = evaluator.evaluate(page, condition)
        
        assert result is True
        page.query_selector_all.assert_called_once_with(".item")
    
    def test_count_condition_exact_false(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        elements = [MagicMock(), MagicMock()]  # 2 elements
        page.query_selector_all.return_value = elements
        
        condition = ConditionSpec(**{
            "@count": 3,
            "@selector": ".item"
        })
        result = evaluator.evaluate(page, condition)
        
        assert result is False
    
    def test_min_count_condition_true(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        elements = [MagicMock(), MagicMock(), MagicMock()]  # 3 elements
        page.query_selector_all.return_value = elements
        
        condition = ConditionSpec(**{
            "@min-count": 2,
            "@selector": ".item"
        })
        result = evaluator.evaluate(page, condition)
        
        assert result is True
    
    def test_min_count_condition_false(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        elements = [MagicMock()]  # 1 element
        page.query_selector_all.return_value = elements
        
        condition = ConditionSpec(**{
            "@min-count": 2,
            "@selector": ".item"
        })
        result = evaluator.evaluate(page, condition)
        
        assert result is False
    
    def test_max_count_condition_true(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        elements = [MagicMock(), MagicMock()]  # 2 elements
        page.query_selector_all.return_value = elements
        
        condition = ConditionSpec(**{
            "@max-count": 3,
            "@selector": ".item"
        })
        result = evaluator.evaluate(page, condition)
        
        assert result is True
    
    def test_max_count_condition_false(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        elements = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]  # 4 elements
        page.query_selector_all.return_value = elements
        
        condition = ConditionSpec(**{
            "@max-count": 3,
            "@selector": ".item"
        })
        result = evaluator.evaluate(page, condition)
        
        assert result is False
    
    def test_no_condition_defaults_false(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        
        condition = ConditionSpec()
        result = evaluator.evaluate(page, condition)
        
        assert result is False
    
    def test_condition_evaluation_error_returns_false(self):
        evaluator = ConditionEvaluator()
        page = MagicMock()
        page.query_selector.side_effect = Exception("Page error")
        
        condition = ConditionSpec(**{"@exists": "#test"})
        result = evaluator.evaluate(page, condition)
        
        assert result is False


class TestConditionalProcessor:
    def test_process_conditional_then_branch(self):
        processor = ConditionalProcessor()
        processor.evaluator = MagicMock()
        processor.evaluator.evaluate.return_value = True
        
        page = MagicMock()
        
        then_step = ExtractStep(**{
            "@xpath": "//div[@class='premium']",
            "@fields": {"title": ".//h2/text()"}
        })
        
        conditional = ConditionalStep(**{
            "@if": {"@exists": "#premium-section"},
            "@then": [then_step]
        })
        
        with patch.object(processor, '_execute_steps') as mock_execute:
            mock_execute.return_value = [{"title": "Premium Content"}]
            
            results = processor.process_conditional(page, conditional)
            
            mock_execute.assert_called_once_with(page, [then_step])
            assert results == [{"title": "Premium Content"}]
    
    def test_process_conditional_else_branch(self):
        processor = ConditionalProcessor()
        processor.evaluator = MagicMock()
        processor.evaluator.evaluate.return_value = False
        
        page = MagicMock()
        
        then_step = ExtractStep(**{
            "@xpath": "//div[@class='premium']",
            "@fields": {"title": ".//h2/text()"}
        })
        
        else_step = ExtractStep(**{
            "@xpath": "//div[@class='basic']",
            "@fields": {"title": ".//h2/text()"}
        })
        
        conditional = ConditionalStep(**{
            "@if": {"@exists": "#premium-section"},
            "@then": [then_step],
            "@else": [else_step]
        })
        
        with patch.object(processor, '_execute_steps') as mock_execute:
            mock_execute.return_value = [{"title": "Basic Content"}]
            
            results = processor.process_conditional(page, conditional)
            
            mock_execute.assert_called_once_with(page, [else_step])
            assert results == [{"title": "Basic Content"}]
    
    def test_process_conditional_no_else_branch(self):
        processor = ConditionalProcessor()
        processor.evaluator = MagicMock()
        processor.evaluator.evaluate.return_value = False
        
        page = MagicMock()
        
        then_step = ExtractStep(**{
            "@xpath": "//div[@class='premium']",
            "@fields": {"title": ".//h2/text()"}
        })
        
        conditional = ConditionalStep(**{
            "@if": {"@exists": "#premium-section"},
            "@then": [then_step]
        })
        
        results = processor.process_conditional(page, conditional)
        
        assert results == []
    
    @patch('engine.web_engine.engine.execute_step')
    def test_execute_steps_extract_step(self, mock_execute_step):
        processor = ConditionalProcessor()
        page = MagicMock()
        page.context = MagicMock()
        
        mock_execute_step.return_value = [{"title": "Test"}]
        
        extract_step = ExtractStep(**{
            "@xpath": "//div[@class='item']",
            "@fields": {"title": ".//h2/text()"}
        })
        
        results = processor._execute_steps(page, [extract_step])
        
        mock_execute_step.assert_called_once_with(page.context, page, extract_step)
        assert results == [{"title": "Test"}]
    
    def test_execute_steps_nested_conditional(self):
        processor = ConditionalProcessor()
        page = MagicMock()
        
        nested_then_step = ExtractStep(**{
            "@xpath": "//div[@class='nested']",
            "@fields": {"content": ".//p/text()"}
        })
        
        nested_conditional = ConditionalStep(**{
            "@if": {"@exists": "#nested"},
            "@then": [nested_then_step]
        })
        
        with patch.object(processor, 'process_conditional') as mock_process:
            mock_process.return_value = [{"nested": "result"}]
            
            results = processor._execute_steps(page, [nested_conditional])
            
            mock_process.assert_called_once_with(page, nested_conditional)
            assert results == [{"nested": "result"}]
    
    def test_can_handle_conditional_step(self):
        processor = ConditionalProcessor()
        
        then_step = ExtractStep(**{
            "@xpath": "//div[@class='test']",
            "@fields": {"title": ".//h2/text()"}
        })
        
        conditional = ConditionalStep(**{
            "@if": {"@exists": "#test"},
            "@then": [then_step]
        })
        
        assert processor.can_handle(conditional) is True
    
    def test_cannot_handle_extract_step(self):
        processor = ConditionalProcessor()
        
        extract_step = ExtractStep(**{
            "@xpath": "//div",
            "@fields": {"title": ".//h2"}
        })
        
        assert processor.can_handle(extract_step) is False