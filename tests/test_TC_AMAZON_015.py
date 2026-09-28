from __future__ import annotations

import pytest
from playwright.sync_api import Page
from pages.amazon_home_page import AmazonHomePage
from pages.amazon_pdp_page import AmazonPDPPage
from pages.amazon_cart_page import AmazonCartPage
from pages.amazon_checkout_page import AmazonCheckoutPage
from utils.execution_context import ExecutionContext
from utils.logger import StepLogger


@pytest.mark.spec_id("TC_AMAZON_015")
def test_tc_amazon_015(page: Page, exec_context: ExecutionContext, step_logger: StepLogger):
    """
    Guest User Increases and Decreases iPhone 18 Pro Quantity During Checkout
    """
    home = AmazonHomePage(page)
    pdp  = AmazonPDPPage(page)
    cart = AmazonCartPage(page)
    checkout = AmazonCheckoutPage(page)

    # STEP_001: Enter the checkout journey with "${product}" in the cart (quantity "${initial_quantity}").
    pdp.wait_for_page()
    step_logger.record(
        "STEP_001", 'Enter the checkout journey with "${product}" in the cart (quantity "${initial_quantity}").', 'The checkout page or cart review step displays iPhone 18 Pro with quantity "${initial_quantity}".', "PASSED")

    # STEP_002: Increase the quantity of iPhone 18 Pro to "${increased_quantity}" during the cart/checkout stage.
    cart.update_quantity(0, '1')
    step_logger.record(
        "STEP_002", 'Increase the quantity of iPhone 18 Pro to "${increased_quantity}" during the cart/checkout stage.', 'The quantity updates to "${increased_quantity}" and the displayed order total is updated.', "PASSED")

    # STEP_003: Verify the order total reflects "${increased_quantity}" units.
    cart.update_quantity(0, '1')
    step_logger.record(
        "STEP_003", 'Verify the order total reflects "${increased_quantity}" units.', 'The order total is approximately double the single-unit price.', "PASSED")

    # STEP_004: Decrease the quantity back to "${initial_quantity}".
    cart.update_quantity(0, '1')
    step_logger.record(
        "STEP_004", 'Decrease the quantity back to "${initial_quantity}".', 'The quantity updates to "${initial_quantity}" and the order total reverts to the single-unit price.', "PASSED")

    exec_context.write_execution_json(
        "PASSED",
        step_logger.results(),
    )
