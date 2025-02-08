import logging
from playwright.sync_api import sync_playwright
from .extractor import XPathExtractor
from .models import ExtractionQuery, ExtractStep, FollowStep, PaginationSpec


logger = logging.getLogger(__name__)


def extract_fields(element, fields):
    result = {}
    for field, xpath in fields.items():
        # Locate the element using XPath
        target_element = element.query_selector(f"xpath={xpath}")
        if target_element:
            # Extract text or attribute based on the field
            if field == "image_url":  # Special handling for image URLs
                result[field] = target_element.get_attribute("src")
            else:  # Default to text content
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


def execute_step(page, step):
    results = []
    elements = page.query_selector_all(f"xpath={step.xpath}")
    logger.debug(f"Found {len(elements)} elements with XPath: {step.xpath}")

    extractor = XPathExtractor()
    for element in elements:
        item = extractor.extract_fields(element, step.fields)
        if step.follow:
            link = extractor.extract_value(element, step.follow.xpath, "href")
            if link:
                with page.context.new_page() as new_page:
                    logger.info(f"Following link: {link}")
                    new_page.goto(link)
                    for follow_step in step.follow.steps:
                        item.update(execute_step(new_page, follow_step))
        results.append(item)
    return results


def execute_query(query: ExtractionQuery):
    try:
        with sync_playwright() as p:
            logger.info("Launching browser...")
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            logger.info(f"Navigating to URL: {query.url}")
            page.goto(query.url)

            # Check for CAPTCHA
            if check_for_captcha(page):
                logger.warning("CAPTCHA detected. Please solve it manually.")
                input("Press Enter to continue after solving CAPTCHA...")

            results = []
            page_count = 0

            while True:
                for step in query.steps:
                    logger.info(f"Executing step with XPath: {step.xpath}")
                    results.extend(execute_step(page, step))

                # Handle pagination
                if not query.pagination or page_count >= query.pagination.limit - 1:
                    logger.info("Pagination limit reached or no pagination specified.")
                    break

                next_link = page.query_selector(f"xpath={query.pagination.xpath}")
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

                # Check for CAPTCHA after each page navigation
                if check_for_captcha(page):
                    logger.warning("CAPTCHA detected. Please solve it manually.")
                    input("Press Enter to continue after solving CAPTCHA...")

            logger.info("Closing browser...")
            browser.close()
            return results
    except Exception as e:
        logger.error(f"An error occurred during query execution: {e}", exc_info=True)
        raise

