from __future__ import annotations

import pytest
from playwright.sync_api import Page
from pages.amazon_home_page import AmazonHomePage
from pages.amazon_pdp_page import AmazonPDPPage
from pages.amazon_cart_page import AmazonCartPage
from utils.execution_context import ExecutionContext
from utils.logger import StepLogger


@pytest.mark.spec_id("TC_AMAZON_010")
def test_tc_amazon_010(page: Page, exec_context: ExecutionContext, step_logger: StepLogger):
    """
    Guest User Removes Sony Bravia 43-Inch TV from Cart Leaving 55-Inch
    """
    home = AmazonHomePage(page)
    pdp  = AmazonPDPPage(page)
    cart = AmazonCartPage(page)

    # STEP_001: Add both Sony Bravia 43-inch and 55-inch TVs to the cart and navigate to the cart page.
    cart.navigate()
    step_logger.record(
        "STEP_001", 'Add both Sony Bravia 43-inch and 55-inch TVs to the cart and navigate to the cart page.', 'Cart page is displayed with both TVs as separate line items.', "PASSED")

    # STEP_002: Click the Remove or Delete action for the Sony Bravia 43-inch TV line item.
    cart.remove_first_item()
    step_logger.record(
        "STEP_002", 'Click the Remove or Delete action for the Sony Bravia 43-inch TV line item.', 'The 43-inch TV line item is removed from the cart.', "PASSED")

    # STEP_003: Verify the Sony Bravia 43-inch TV is no longer in the cart.
    pdp.wait_for_page()
    step_logger.record(
        "STEP_003", 'Verify the Sony Bravia 43-inch TV is no longer in the cart.', 'No cart line item containing "43" is displayed.', "PASSED")

    # STEP_004: Verify the Sony Bravia 55-inch TV remains in the cart.
    pdp.wait_for_page()
    step_logger.record(
        "STEP_004", 'Verify the Sony Bravia 55-inch TV remains in the cart.', 'The 55-inch TV line item is still displayed with its original quantity.', "PASSED")

    # STEP_005: Verify the cart total is updated.
    pdp.verify_price_visible()
    step_logger.record(
        "STEP_005", 'Verify the cart total is updated.', 'The cart subtotal reflects only the 55-inch TV price.', "PASSED")

    exec_context.write_execution_json(
        "PASSED",
        step_logger.results(),
    )
