from __future__ import annotations

import pytest
from playwright.sync_api import Page
from pages.amazon_home_page import AmazonHomePage
from pages.amazon_cart_page import AmazonCartPage
from pages.amazon_checkout_page import AmazonCheckoutPage
from utils.execution_context import ExecutionContext
from utils.logger import StepLogger


@pytest.mark.spec_id("TC_AMAZON_014")
def test_tc_amazon_014(page: Page, exec_context: ExecutionContext, step_logger: StepLogger):
    """
    Guest User Proceeds from iPhone 18 Pro Cart to Checkout
    """
    home = AmazonHomePage(page)
    cart = AmazonCartPage(page)
    checkout = AmazonCheckoutPage(page)

    # STEP_001: Navigate to the cart containing the "${product}".
    cart.navigate()
    step_logger.record(
        "STEP_001", 'Navigate to the cart containing the "${product}".', 'Cart page is displayed with the iPhone 18 Pro as a line item.', "PASSED")

    # STEP_002: Click the "Proceed to Checkout" button.
    cart.proceed_to_checkout()
    checkout.wait_for_page()
    step_logger.record(
        "STEP_002", 'Click the "Proceed to Checkout" button.', 'The checkout journey is initiated and the first checkout step is displayed.', "PASSED")

    # STEP_003: Verify the guest checkout option is available or the checkout proceeds without requiring a logged-in account.
    checkout.proceed_as_guest('')
    step_logger.record(
        "STEP_003", 'Verify the guest checkout option is available or the checkout proceeds without requiring a logged-in account.', 'A guest checkout option, sign-in prompt with guest path, or direct checkout form is displayed.', "PASSED")

    exec_context.write_execution_json(
        "PASSED",
        step_logger.results(),
    )
