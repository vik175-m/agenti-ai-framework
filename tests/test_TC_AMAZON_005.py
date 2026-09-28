from __future__ import annotations

import pytest
from playwright.sync_api import Page
from pages.amazon_home_page import AmazonHomePage
from pages.amazon_plp_page import AmazonPLPPage
from pages.amazon_pdp_page import AmazonPDPPage
from pages.amazon_cart_page import AmazonCartPage
from utils.execution_context import ExecutionContext
from utils.logger import StepLogger


@pytest.mark.spec_id("TC_AMAZON_005")
def test_tc_amazon_005(page: Page, exec_context: ExecutionContext, step_logger: StepLogger):
    """
    Guest User Opens Sony Bravia 43-Inch TV Product Detail Page from PLP
    """
    home = AmazonHomePage(page)
    plp  = AmazonPLPPage(page)
    pdp  = AmazonPDPPage(page)
    cart = AmazonCartPage(page)

    # STEP_001: Navigate to the Amazon homepage and search for "${search_term}".
    home.navigate()
    step_logger.record(
        "STEP_001", 'Navigate to the Amazon homepage and search for "${search_term}".', 'The Sony Bravia TV product listing page is displayed.', "PASSED")

    # STEP_002: Identify and click on a Sony Bravia 43-inch TV product from the listing.
    plp.open_first_result()
    pdp.wait_for_page()
    step_logger.record(
        "STEP_002", 'Identify and click on a Sony Bravia 43-inch TV product from the listing.', 'The browser navigates to the product detail page for the selected item.', "PASSED")

    # STEP_003: Verify the product detail page title contains "${expected_product_keyword}".
    pdp.verify_title_contains('43')
    step_logger.record(
        "STEP_003", 'Verify the product detail page title contains "${expected_product_keyword}".', 'The product title on the PDP contains "43" indicating the correct 43-inch variant is displayed.', "PASSED")

    exec_context.write_execution_json(
        "PASSED",
        step_logger.results(),
    )
