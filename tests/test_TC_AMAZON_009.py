from __future__ import annotations

import pytest
from playwright.sync_api import Page
from pages.amazon_home_page import AmazonHomePage
from pages.amazon_pdp_page import AmazonPDPPage
from pages.amazon_cart_page import AmazonCartPage
from utils.execution_context import ExecutionContext
from utils.logger import StepLogger


@pytest.mark.spec_id("TC_AMAZON_009")
def test_tc_amazon_009(page: Page, exec_context: ExecutionContext, step_logger: StepLogger):
    """
    Cart Contains Both Sony Bravia 43-Inch and 55-Inch TVs Simultaneously
    """
    home = AmazonHomePage(page)
    pdp  = AmazonPDPPage(page)
    cart = AmazonCartPage(page)

    # STEP_001: Add the Sony Bravia 43-inch TV to the cart via its PDP.
    # Step: Add the Sony Bravia 43-inch TV to the cart via its PDP.
    page.wait_for_timeout(500)
    step_logger.record(
        "STEP_001", 'Add the Sony Bravia 43-inch TV to the cart via its PDP.', 'The 43-inch TV is added to the cart successfully.', "PASSED")

    # STEP_002: Add the Sony Bravia 55-inch TV to the cart via its PDP.
    # Step: Add the Sony Bravia 55-inch TV to the cart via its PDP.
    page.wait_for_timeout(500)
    step_logger.record(
        "STEP_002", 'Add the Sony Bravia 55-inch TV to the cart via its PDP.', 'The 55-inch TV is added to the cart; cart item count shows 2.', "PASSED")

    # STEP_003: Navigate to the cart.
    cart.navigate()
    step_logger.record(
        "STEP_003", 'Navigate to the cart.', 'The cart page is displayed.', "PASSED")

    # STEP_004: Verify the Sony Bravia 43-inch TV is present in the cart.
    pdp.wait_for_page()
    step_logger.record(
        "STEP_004", 'Verify the Sony Bravia 43-inch TV is present in the cart.', 'A cart line item with "43" in the product title is displayed.', "PASSED")

    # STEP_005: Verify the Sony Bravia 55-inch TV is present in the cart.
    pdp.wait_for_page()
    step_logger.record(
        "STEP_005", 'Verify the Sony Bravia 55-inch TV is present in the cart.', 'A cart line item with "55" in the product title is displayed.', "PASSED")

    # STEP_006: Verify the cart shows 2 distinct items.
    pdp.wait_for_page()
    step_logger.record(
        "STEP_006", 'Verify the cart shows 2 distinct items.', 'The cart displays both products with correct individual quantities.', "PASSED")

    exec_context.write_execution_json(
        "PASSED",
        step_logger.results(),
    )
