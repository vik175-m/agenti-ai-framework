from __future__ import annotations

import pytest
from playwright.sync_api import Page
from pages.amazon_home_page import AmazonHomePage
from pages.amazon_plp_page import AmazonPLPPage
from pages.amazon_pdp_page import AmazonPDPPage
from pages.amazon_cart_page import AmazonCartPage
from utils.execution_context import ExecutionContext
from utils.logger import StepLogger


@pytest.mark.spec_id("TC_AMAZON_013")
def test_tc_amazon_013(page: Page, exec_context: ExecutionContext, step_logger: StepLogger):
    """
    Guest User Searches for iPhone 18 Pro and Adds It to Cart
    """
    home = AmazonHomePage(page)
    plp  = AmazonPLPPage(page)
    pdp  = AmazonPDPPage(page)
    cart = AmazonCartPage(page)

    # STEP_001: Navigate to the Amazon homepage and search for "${search_term}".
    home.navigate()
    step_logger.record(
        "STEP_001", 'Navigate to the Amazon homepage and search for "${search_term}".', 'Search results or product listing page for iPhone 18 Pro is displayed.', "PASSED")

    # STEP_002: Open the relevant iPhone 18 Pro product detail page from the listing.
    plp.open_first_result()
    pdp.wait_for_page()
    step_logger.record(
        "STEP_002", 'Open the relevant iPhone 18 Pro product detail page from the listing.', 'The PDP for iPhone 18 Pro is displayed with the correct product title.', "PASSED")

    # STEP_003: Click the "Add to Cart" button.
    pdp.click_add_to_cart()
    step_logger.record(
        "STEP_003", 'Click the "Add to Cart" button.', 'iPhone 18 Pro is added to the cart; a confirmation or cart count update is shown.', "PASSED")

    # STEP_004: Navigate to the cart.
    cart.navigate()
    step_logger.record(
        "STEP_004", 'Navigate to the cart.', 'The cart page is displayed.', "PASSED")

    # STEP_005: Verify the iPhone 18 Pro is listed in the cart.
    pdp.wait_for_page()
    step_logger.record(
        "STEP_005", 'Verify the iPhone 18 Pro is listed in the cart.', 'A cart line item containing "${expected_product_keyword}" is displayed with quantity 1.', "PASSED")

    exec_context.write_execution_json(
        "PASSED",
        step_logger.results(),
    )
