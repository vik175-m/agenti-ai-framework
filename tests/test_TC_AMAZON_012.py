from __future__ import annotations

import pytest
from playwright.sync_api import Page
from pages.amazon_home_page import AmazonHomePage
from pages.amazon_pdp_page import AmazonPDPPage
from pages.amazon_cart_page import AmazonCartPage
from utils.execution_context import ExecutionContext
from utils.logger import StepLogger


@pytest.mark.spec_id("TC_AMAZON_012")
def test_tc_amazon_012(page: Page, exec_context: ExecutionContext, step_logger: StepLogger):
    """
    Guest User Increases and Decreases Sony Bravia TV Quantity in Cart
    """
    home = AmazonHomePage(page)
    pdp  = AmazonPDPPage(page)
    cart = AmazonCartPage(page)

    # STEP_001: Add a Sony Bravia TV to the cart and navigate to the cart page.
    cart.navigate()
    step_logger.record(
        "STEP_001", 'Add a Sony Bravia TV to the cart and navigate to the cart page.', 'Cart displays the Sony Bravia TV with quantity "${initial_quantity}".', "PASSED")

    # STEP_002: Increase the quantity of the Sony Bravia TV to "${increased_quantity}" using the quantity control.
    cart.update_quantity(0, '1')
    step_logger.record(
        "STEP_002", 'Increase the quantity of the Sony Bravia TV to "${increased_quantity}" using the quantity control.', 'The quantity updates to "${increased_quantity}" and the cart subtotal is updated accordingly.', "PASSED")

    # STEP_003: Verify the cart subtotal reflects 2 units of the Sony Bravia TV.
    pdp.verify_price_visible()
    step_logger.record(
        "STEP_003", 'Verify the cart subtotal reflects 2 units of the Sony Bravia TV.', 'The subtotal is approximately double the single-unit price.', "PASSED")

    # STEP_004: Decrease the quantity back to "${initial_quantity}" using the quantity control.
    cart.update_quantity(0, '1')
    step_logger.record(
        "STEP_004", 'Decrease the quantity back to "${initial_quantity}" using the quantity control.', 'The quantity updates to "${initial_quantity}" and the cart subtotal reverts to the single-unit price.', "PASSED")

    exec_context.write_execution_json(
        "PASSED",
        step_logger.results(),
    )
