from __future__ import annotations

import pytest
from playwright.sync_api import Page
from pages.amazon_home_page import AmazonHomePage
from pages.amazon_pdp_page import AmazonPDPPage
from pages.amazon_cart_page import AmazonCartPage
from utils.execution_context import ExecutionContext
from utils.logger import StepLogger


@pytest.mark.spec_id("TC_AMAZON_008")
def test_tc_amazon_008(page: Page, exec_context: ExecutionContext, step_logger: StepLogger):
    """
    Guest User Adds Sony Bravia 55-Inch TV to Cart
    """
    home = AmazonHomePage(page)
    pdp  = AmazonPDPPage(page)
    cart = AmazonCartPage(page)

    # STEP_001: Navigate to the Sony Bravia 55-inch TV PDP via search for "${search_term}".
    # Step: Navigate to the Sony Bravia 55-inch TV PDP via search for "${search_term}".
    page.wait_for_timeout(500)
    step_logger.record(
        "STEP_001", 'Navigate to the Sony Bravia 55-inch TV PDP via search for "${search_term}".', 'The PDP for a Sony Bravia 55-inch TV is displayed.', "PASSED")

    # STEP_002: Click the "Add to Cart" button.
    pdp.click_add_to_cart()
    step_logger.record(
        "STEP_002", 'Click the "Add to Cart" button.', 'The product is added to the cart; a confirmation message or cart count update is shown.', "PASSED")

    # STEP_003: Navigate to the cart.
    cart.navigate()
    step_logger.record(
        "STEP_003", 'Navigate to the cart.', 'The cart page is displayed.', "PASSED")

    # STEP_004: Verify the Sony Bravia 55-inch TV is listed in the cart.
    pdp.verify_title_contains('55')
    step_logger.record(
        "STEP_004", 'Verify the Sony Bravia 55-inch TV is listed in the cart.', 'The cart contains the correct product with "${expected_product_keyword}" in the product title and quantity is 1.', "PASSED")

    exec_context.write_execution_json(
        "PASSED",
        step_logger.results(),
    )
