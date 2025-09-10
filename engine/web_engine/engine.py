import logging
from .extractor import XPathExtractor
from .models import ExtractionQuery, ExtractStep, ConditionalStep
from .base.browser import BrowserClient
from .actions import ActionProcessor
from .conditionals import ConditionalProcessor
from .processors import StepProcessorRegistry
from .extract_processor import ExtractStepProcessor
from .follow_processor import FollowStepProcessor
from .javascript_processor import JavaScriptStepProcessor
from .plugins.jsonld_extractor import JsonLdExtractorProcessor
from .plugins.api_extractor import ApiExtractorProcessor
from .plugins.ai_selector import AISelectorProcessor
from .plugin_manager import PluginManager

logger = logging.getLogger(__name__)


def extract_fields(element, fields):
    result = {}

    for field, xpath in fields.items():
        # Locate the element using XPath
        target_element = element.query_selector(f"xpath={xpath}")

        if target_element:
            # Automatically detect attribute extraction (`@src`, `@href`)
            if xpath.endswith("/@src") or xpath.endswith("/@href"):
                attribute = xpath.split("/@")[-1]  # Extract attribute name
                result[field] = target_element.get_attribute(attribute)
            else:
                result[field] = target_element.text_content().strip()
        else:
            logger.warning(f"Field '{field}' not found with XPath: {xpath}")

    return result


def check_for_captcha(page):
    """Check if a CAPTCHA challenge is present on the page."""
    captcha_selectors = [
        "#captcha",  # Common CAPTCHA element
        ".g-recaptcha",  # Google reCAPTCHA
        "iframe[src*='recaptcha']"  # reCAPTCHA iframe
    ]
    for selector in captcha_selectors:
        if page.query_selector(selector):
            logger.info("CAPTCHA detected on the page.")
            return True
    return False


def execute_step(context, page, step: ExtractStep):  # Ensure step is an ExtractStep object
    results = []

    elements = page.query_selector_all(f"xpath={step.xpath}")
    logger.debug(f"Found {len(elements)} elements with XPath: {step.xpath}")

    extractor = XPathExtractor()

    for element in elements:
        item = extractor.extract_fields(element, step.fields)

        if step.follow:
            link = extractor.extract_value(element, step.follow.xpath, base_url=page.url)

            if link:
                logger.info(f"Following link: {link}")

                with context.new_page() as new_page:
                    new_page.goto(link)
                    new_page.wait_for_load_state("domcontentloaded")

                    for follow_step in step.follow.steps:  # ✅ Use model attribute instead of dict
                        follow_results = execute_step(context, new_page, follow_step)

                        if isinstance(follow_results, dict) and follow_results:
                            item.update(follow_results)

                        elif isinstance(follow_results, list) and follow_results:
                            structured_list = [result for result in follow_results if isinstance(result, dict)]

                            if structured_list:
                                key = follow_step.name or follow_step.xpath  # ✅ Correct access
                                item.setdefault(key, []).extend(structured_list)

        results.append(item)

    return results if results else {}


def execute_query(query: ExtractionQuery, browser_client: BrowserClient):
    """Executes the web extraction query using Playwright."""
    try:
        with browser_client as client:  # Use the injected PlaywrightClient
            logger.info("Launching browser...")

            browser = client.browser  # Use the PlaywrightClient's browser
            page = client.page         # Use the PlaywrightClient's page
            action_processor = ActionProcessor()  # Initialize action processor
            
            # Initialize step processor registry
            step_registry = StepProcessorRegistry()
            
            # Register built-in processors
            step_registry.register(ExtractStepProcessor())
            step_registry.register(ConditionalProcessor())
            step_registry.register(FollowStepProcessor())
            step_registry.register(JavaScriptStepProcessor())
            step_registry.register(JsonLdExtractorProcessor())
            step_registry.register(ApiExtractorProcessor())
            step_registry.register(AISelectorProcessor())
            
            # Initialize plugin manager and load plugins
            plugin_manager = PluginManager(step_registry)
            try:
                plugin_results = plugin_manager.discover_and_load_plugins(auto_load=True)
                loaded_plugins = sum(1 for success in plugin_results.values() if success)
                if loaded_plugins > 0:
                    logger.info(f"Loaded {loaded_plugins} plugins successfully")
            except Exception as e:
                logger.warning(f"Plugin loading failed: {e}")
                # Continue without plugins

            logger.info(f"Navigating to URL: {query.url}")
            page.goto(query.url)

            # Check for CAPTCHA
            if check_for_captcha(page):
                logger.warning("CAPTCHA detected. Please solve it manually.")
                input("Press Enter to continue after solving CAPTCHA...")

            # Execute pre-extraction actions if defined
            if query.actions:
                logger.info(f"Executing {len(query.actions)} pre-extraction actions")
                action_processor.execute_actions(page, query.actions)

            results = []
            page_count = 0

            while True:
                for step in query.steps:
                    logger.info(f"Executing step: {type(step).__name__}")
                    step_results = step_registry.process_step(client.browser.new_context(), page, step)
                    if isinstance(step_results, list):
                        results.extend(step_results)
                    elif isinstance(step_results, dict) and step_results:
                        results.append(step_results)

                # Use `.pagination` method/property instead of dict access
                pagination = query.pagination
                if not pagination or page_count >= pagination.limit - 1:
                    logger.info("Pagination limit reached or not specified.")
                    break

                next_page_xpath = pagination.xpath
                next_link = page.query_selector(f"xpath={next_page_xpath}")
                if not next_link:
                    logger.warning("Next page link not found.")
                    break

                next_url = next_link.get_attribute("href")
                if not next_url:
                    logger.warning("Next page URL not found.")
                    break

                logger.info(f"Navigating to next page: {next_url}")
                page.goto(next_url)
                page_count += 1

                # Check for CAPTCHA after navigation
                if check_for_captcha(page):
                    logger.warning("CAPTCHA detected. Please solve it manually.")
                    input("Press Enter to continue after solving CAPTCHA...")

            logger.info("Closing browser...")
            browser.close()
            return results

    except Exception as e:
        logger.error(f"An error occurred during query execution: {e}", exc_info=True)
        raise
