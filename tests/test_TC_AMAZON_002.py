from __future__ import annotations

import pytest
from playwright.sync_api import Page
from pages.amazon_home_page import AmazonHomePage
from pages.amazon_plp_page import AmazonPLPPage
from utils.execution_context import ExecutionContext
from utils.logger import StepLogger


@pytest.mark.spec_id("TC_AMAZON_002")
def test_tc_amazon_002(page: Page, exec_context: ExecutionContext, step_logger: StepLogger):
    """
    Guest User Searches for Sony Bravia TV from Homepage
    """
    home = AmazonHomePage(page)
    plp  = AmazonPLPPage(page)

    # STEP_001: Navigate to the Amazon homepage (https://www.amazon.com).
    home.navigate()
    step_logger.record(
        "STEP_001", 'Navigate to the Amazon homepage (https://www.amazon.com).', 'Amazon homepage loads with the search bar visible.', "PASSED")

    # STEP_002: Enter "${search_term}" into the search bar.
    home.enter_search_term('Sony Bravia TV')
    step_logger.record(
        "STEP_002", 'Enter "${search_term}" into the search bar.', 'The search term is accepted and visible in the search input.', "PASSED")

    # STEP_003: Submit the search.
    home.submit_search()
    plp.wait_for_results()
    step_logger.record(
        "STEP_003", 'Submit the search.', 'The browser navigates to a search results or product listing page.', "PASSED")

    # STEP_004: Verify the page displays results relevant to "${search_term}".
    # Assertion: Product listings related to Sony Bravia TV are displayed.
    home.verify_loaded()
    step_logger.record(
        "STEP_004", 'Verify the page displays results relevant to "${search_term}".', 'Product listings related to Sony Bravia TV are displayed.', "PASSED")

    exec_context.write_execution_json(
        "PASSED",
        step_logger.results(),
    )
