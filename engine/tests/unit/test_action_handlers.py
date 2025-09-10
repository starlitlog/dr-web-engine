import pytest
from unittest.mock import MagicMock, patch
from engine.web_engine.actions import (
    ClickActionHandler, ScrollActionHandler, WaitActionHandler, FillActionHandler, HoverActionHandler, ActionProcessor
)
from engine.web_engine.models import (
    ClickAction, ScrollAction, WaitAction, FillAction, HoverAction
)


class TestClickHandler:
    def test_can_handle_click_action(self):
        handler = ClickActionHandler()
        action = ClickAction(**{"@type": "click", "@selector": ".btn"})
        
        assert handler.can_handle(action) is True

    def test_cannot_handle_other_actions(self):
        handler = ClickActionHandler()
        action = ScrollAction(**{"@type": "scroll", "@direction": "down", "@pixels": 100})
        
        assert handler.can_handle(action) is False

    def test_execute_with_selector(self):
        handler = ClickActionHandler()
        page = MagicMock()
        element = MagicMock()
        page.query_selector.return_value = element
        action = ClickAction(**{"@type": "click", "@selector": ".btn-submit"})
        
        handler.execute(page, action)
        
        page.query_selector.assert_called_once_with(".btn-submit")
        element.click.assert_called_once()

    def test_execute_with_xpath(self):
        handler = ClickActionHandler()
        page = MagicMock()
        element = MagicMock()
        page.query_selector.return_value = element
        action = ClickAction(**{"@type": "click", "@selector": "dummy", "@xpath": "//button[@class='submit']"})
        
        handler.execute(page, action)
        
        page.query_selector.assert_called_once_with("xpath=//button[@class='submit']")
        element.click.assert_called_once()


class TestScrollHandler:
    def test_can_handle_scroll_action(self):
        handler = ScrollActionHandler()
        action = ScrollAction(**{"@type": "scroll", "@direction": "down", "@pixels": 500})
        
        assert handler.can_handle(action) is True

    def test_cannot_handle_other_actions(self):
        handler = ScrollActionHandler()
        action = ClickAction(**{"@type": "click", "@selector": ".btn"})
        
        assert handler.can_handle(action) is False

    def test_execute_page_scroll_down(self):
        handler = ScrollActionHandler()
        page = MagicMock()
        action = ScrollAction(**{"@type": "scroll", "@direction": "down", "@pixels": 500})
        
        handler.execute(page, action)
        
        page.evaluate.assert_called_once_with("window.scrollBy(0, 500)")

    def test_execute_page_scroll_up(self):
        handler = ScrollActionHandler()
        page = MagicMock()
        action = ScrollAction(**{"@type": "scroll", "@direction": "up", "@pixels": 300})
        
        handler.execute(page, action)
        
        page.evaluate.assert_called_once_with("window.scrollBy(0, -300)")

    def test_execute_element_scroll_with_selector(self):
        handler = ScrollActionHandler()
        page = MagicMock()
        element = MagicMock()
        page.query_selector.return_value = element
        action = ScrollAction(**{
            "@type": "scroll",
            "@direction": "down",
            "@pixels": 200,
            "@selector": ".content"
        })
        
        handler.execute(page, action)
        
        page.query_selector.assert_called_once_with(".content")
        element.scroll_into_view_if_needed.assert_called_once()

    def test_execute_element_scroll_with_xpath(self):
        # Test pixel scrolling with xpath (should ignore xpath and use pixels)
        handler = ScrollActionHandler()
        page = MagicMock()
        action = ScrollAction(**{
            "@type": "scroll",
            "@direction": "up",
            "@pixels": 150,
            "@xpath": "//div[@class='content']"
        })
        
        handler.execute(page, action)
        
        # Should use pixel scrolling, not element scrolling
        page.evaluate.assert_called_once_with("window.scrollBy(0, -150)")


class TestWaitHandler:
    def test_can_handle_wait_action(self):
        handler = WaitActionHandler()
        action = WaitAction(**{"@type": "wait", "@until": "timeout", "@timeout": 5000})
        
        assert handler.can_handle(action) is True

    def test_cannot_handle_other_actions(self):
        handler = WaitActionHandler()
        action = ClickAction(**{"@type": "click", "@selector": ".btn"})
        
        assert handler.can_handle(action) is False

    def test_execute_timeout_wait(self):
        handler = WaitActionHandler()
        page = MagicMock()
        action = WaitAction(**{"@type": "wait", "@until": "timeout", "@timeout": 3000})
        
        handler.execute(page, action)
        
        page.wait_for_timeout.assert_called_once_with(3000)

    def test_execute_element_wait_with_selector(self):
        handler = WaitActionHandler()
        page = MagicMock()
        action = WaitAction(**{
            "@type": "wait",
            "@until": "element",
            "@selector": ".loading",
            "@timeout": 10000
        })
        
        handler.execute(page, action)
        
        page.wait_for_selector.assert_called_once_with(".loading", timeout=10000)

    def test_execute_element_wait_with_xpath(self):
        handler = WaitActionHandler()
        page = MagicMock()
        action = WaitAction(**{
            "@type": "wait",
            "@until": "element",
            "@xpath": "//div[@class='loaded']",
            "@timeout": 8000
        })
        
        handler.execute(page, action)
        
        page.wait_for_selector.assert_called_once_with("xpath=//div[@class='loaded']", timeout=8000)

    def test_execute_network_idle_wait(self):
        handler = WaitActionHandler()
        page = MagicMock()
        action = WaitAction(**{"@type": "wait", "@until": "network-idle", "@timeout": 15000})
        
        handler.execute(page, action)
        
        page.wait_for_load_state.assert_called_once_with("networkidle", timeout=15000)


class TestFillHandler:
    def test_can_handle_fill_action(self):
        handler = FillActionHandler()
        action = FillAction(**{"@type": "fill", "@selector": "input", "@value": "test"})
        
        assert handler.can_handle(action) is True

    def test_cannot_handle_other_actions(self):
        handler = FillActionHandler()
        action = ClickAction(**{"@type": "click", "@selector": ".btn"})
        
        assert handler.can_handle(action) is False

    def test_execute_with_selector(self):
        handler = FillActionHandler()
        page = MagicMock()
        element = MagicMock()
        page.query_selector.return_value = element
        action = FillAction(**{
            "@type": "fill",
            "@selector": "input[name='username']",
            "@value": "testuser"
        })
        
        handler.execute(page, action)
        
        page.query_selector.assert_called_once_with("input[name='username']")
        element.fill.assert_called_once_with("testuser")

    def test_execute_with_xpath(self):
        handler = FillActionHandler()
        page = MagicMock()
        element = MagicMock()
        page.query_selector.return_value = element
        action = FillAction(**{
            "@type": "fill",
            "@selector": "dummy",  # Required field
            "@xpath": "//input[@name='password']",
            "@value": "secret"
        })
        
        handler.execute(page, action)
        
        page.query_selector.assert_called_once_with("xpath=//input[@name='password']")
        element.fill.assert_called_once_with("secret")


class TestHoverHandler:
    def test_can_handle_hover_action(self):
        handler = HoverActionHandler()
        action = HoverAction(**{"@type": "hover", "@selector": ".menu"})
        
        assert handler.can_handle(action) is True

    def test_cannot_handle_other_actions(self):
        handler = HoverActionHandler()
        action = ClickAction(**{"@type": "click", "@selector": ".btn"})
        
        assert handler.can_handle(action) is False

    def test_execute_with_selector(self):
        handler = HoverActionHandler()
        page = MagicMock()
        element = MagicMock()
        page.query_selector.return_value = element
        action = HoverAction(**{"@type": "hover", "@selector": ".dropdown-trigger"})
        
        handler.execute(page, action)
        
        page.query_selector.assert_called_once_with(".dropdown-trigger")
        element.hover.assert_called_once()

    def test_execute_with_xpath(self):
        handler = HoverActionHandler()
        page = MagicMock()
        element = MagicMock()
        page.query_selector.return_value = element
        action = HoverAction(**{
            "@type": "hover", 
            "@selector": "dummy",  # Required field
            "@xpath": "//div[@class='menu-item']"
        })
        
        handler.execute(page, action)
        
        page.query_selector.assert_called_once_with("xpath=//div[@class='menu-item']")
        element.hover.assert_called_once()


class TestActionProcessor:
    def test_initialization(self):
        processor = ActionProcessor()
        
        assert len(processor.handlers) == 6  # Updated for JavaScript handler
        assert any(isinstance(h, ClickActionHandler) for h in processor.handlers)
        assert any(isinstance(h, ScrollActionHandler) for h in processor.handlers)
        assert any(isinstance(h, WaitActionHandler) for h in processor.handlers)
        assert any(isinstance(h, FillActionHandler) for h in processor.handlers)
        assert any(isinstance(h, HoverActionHandler) for h in processor.handlers)

    def test_execute_actions_empty_list(self):
        processor = ActionProcessor()
        page = MagicMock()
        
        processor.execute_actions(page, [])
        
        # Should not raise any errors

    def test_execute_actions_none(self):
        processor = ActionProcessor()
        page = MagicMock()
        
        processor.execute_actions(page, None)
        
        # Should not raise any errors

    @patch('engine.web_engine.actions.logger')
    def test_execute_actions_with_valid_actions(self, mock_logger):
        processor = ActionProcessor()
        page = MagicMock()
        click_element = MagicMock()
        page.query_selector.return_value = click_element
        
        actions = [
            ClickAction(**{"@type": "click", "@selector": ".btn"}),
            WaitAction(**{"@type": "wait", "@until": "timeout", "@timeout": 1000})
        ]
        
        processor.execute_actions(page, actions)
        
        # Check that the initial log message was called
        assert any(call[0][0] == "Executing 2 actions" for call in mock_logger.info.call_args_list)
        assert mock_logger.debug.call_count == 2
        # Check that click was executed via element
        page.query_selector.assert_called_with(".btn")
        click_element.click.assert_called_once()
        # Check that wait was executed
        page.wait_for_timeout.assert_called_once_with(1000)

    def test_execute_action_no_handler(self):
        processor = ActionProcessor()
        page = MagicMock()
        
        # Create a mock action that no handler can handle
        mock_action = MagicMock()
        mock_action.type = "unsupported"
        
        # Should not raise, just log warning
        processor.execute_action(page, mock_action)
        # Test passes if no exception is raised

    def test_execute_action_finds_correct_handler(self):
        processor = ActionProcessor()
        page = MagicMock()
        element = MagicMock()
        page.query_selector.return_value = element
        
        action = ClickAction(**{"@type": "click", "@selector": ".test"})
        processor.execute_action(page, action)
        
        page.query_selector.assert_called_once_with(".test")
        element.click.assert_called_once()