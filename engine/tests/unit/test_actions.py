import pytest
from pydantic import ValidationError
from engine.web_engine.models import ClickAction, ScrollAction, WaitAction, FillAction, HoverAction


def test_click_action_creation():
    action = ClickAction(**{
        "@type": "click",
        "@selector": ".btn-submit"
    })
    
    assert action.type == "click"
    assert action.selector == ".btn-submit"
    assert action.xpath is None


def test_click_action_with_xpath():
    action = ClickAction(**{
        "@type": "click",
        "@selector": "dummy",  # Required field
        "@xpath": "//button[@class='submit']"
    })
    
    assert action.type == "click"
    assert action.xpath == "//button[@class='submit']"
    assert action.selector == "dummy"


def test_click_action_invalid_no_selector():
    with pytest.raises(ValidationError):
        ClickAction(**{"@type": "click"})


def test_scroll_action_creation():
    action = ScrollAction(**{
        "@type": "scroll",
        "@direction": "down",
        "@pixels": 500
    })
    
    assert action.type == "scroll"
    assert action.direction == "down"
    assert action.pixels == 500


def test_scroll_action_with_element():
    action = ScrollAction(**{
        "@type": "scroll",
        "@direction": "up",
        "@pixels": 300,
        "@selector": ".content"
    })
    
    assert action.type == "scroll"
    assert action.direction == "up"
    assert action.pixels == 300
    assert action.selector == ".content"


def test_scroll_action_invalid_direction():
    with pytest.raises(ValidationError):
        ScrollAction(**{
            "@type": "scroll",
            "@direction": "invalid",
            "@pixels": 500
        })


def test_wait_action_timeout():
    action = WaitAction(**{
        "@type": "wait",
        "@until": "timeout",
        "@timeout": 5000
    })
    
    assert action.type == "wait"
    assert action.until == "timeout"
    assert action.timeout == 5000


def test_wait_action_element():
    action = WaitAction(**{
        "@type": "wait",
        "@until": "element",
        "@selector": ".loading",
        "@timeout": 10000
    })
    
    assert action.type == "wait"
    assert action.until == "element"
    assert action.selector == ".loading"
    assert action.timeout == 10000


def test_wait_action_network_idle():
    action = WaitAction(**{
        "@type": "wait",
        "@until": "network-idle",
        "@timeout": 15000
    })
    
    assert action.type == "wait"
    assert action.until == "network-idle"
    assert action.timeout == 15000


def test_wait_action_invalid_until():
    with pytest.raises(ValidationError):
        WaitAction(**{
            "@type": "wait",
            "@until": "invalid",
            "@timeout": 5000
        })


def test_fill_action_creation():
    action = FillAction(**{
        "@type": "fill",
        "@selector": "input[name='username']",
        "@value": "testuser"
    })
    
    assert action.type == "fill"
    assert action.selector == "input[name='username']"
    assert action.value == "testuser"


def test_fill_action_with_xpath():
    action = FillAction(**{
        "@type": "fill",
        "@selector": "dummy",  # Required field
        "@xpath": "//input[@name='password']",
        "@value": "secretpass"
    })
    
    assert action.type == "fill"
    assert action.xpath == "//input[@name='password']"
    assert action.value == "secretpass"


def test_fill_action_invalid_no_value():
    with pytest.raises(ValidationError):
        FillAction(**{
            "@type": "fill",
            "@selector": "input[name='test']"
        })


def test_hover_action_creation():
    action = HoverAction(**{
        "@type": "hover",
        "@selector": ".dropdown-trigger"
    })
    
    assert action.type == "hover"
    assert action.selector == ".dropdown-trigger"


def test_hover_action_with_xpath():
    action = HoverAction(**{
        "@type": "hover",
        "@selector": "dummy",  # Required field
        "@xpath": "//div[@class='menu-item']"
    })
    
    assert action.type == "hover"
    assert action.xpath == "//div[@class='menu-item']"


def test_hover_action_invalid_no_selector():
    with pytest.raises(ValidationError):
        HoverAction(**{"@type": "hover"})


def test_action_model_creation():
    click_action = ClickAction(**{"@type": "click", "@selector": ".btn"})
    scroll_action = ScrollAction(**{"@type": "scroll", "@direction": "down", "@pixels": 100})
    wait_action = WaitAction(**{"@type": "wait", "@until": "timeout", "@timeout": 1000})
    fill_action = FillAction(**{"@type": "fill", "@selector": "input", "@value": "test"})
    hover_action = HoverAction(**{"@type": "hover", "@selector": ".item"})
    
    assert isinstance(click_action, ClickAction)
    assert isinstance(scroll_action, ScrollAction)
    assert isinstance(wait_action, WaitAction)
    assert isinstance(fill_action, FillAction)
    assert isinstance(hover_action, HoverAction)


def test_invalid_action_type():
    # Test that invalid action type raises ValidationError during creation
    with pytest.raises(ValidationError):
        ClickAction(**{"@type": "invalid", "@selector": ".test"})