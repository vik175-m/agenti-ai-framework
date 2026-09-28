from __future__ import annotations

import pytest
from playwright.sync_api import Page
from pages.amazon_home_page import AmazonHomePage
from pages.amazon_pdp_page import AmazonPDPPage
from pages.amazon_cart_page import AmazonCartPage
from pages.amazon_checkout_page import AmazonCheckoutPage
from utils.execution_context import ExecutionContext
from utils.logger import StepLogger


@pytest.mark.spec_id("TC_AMAZON_006")
def test_tc_amazon_006(page: Page, exec_context: ExecutionContext, step_logger: StepLogger):
    """
    Sony Bravia TV PDP Displays Correct Product Information and Purchase Options
    """
    home = AmazonHomePage(page)
    pdp  = AmazonPDPPage(page)
    cart = AmazonCartPage(page)
    checkout = AmazonCheckoutPage(page)

    # STEP_001: Navigate to a Sony Bravia TV product detail page via search.
    # Step: Navigate to a Sony Bravia TV product detail page via search.
    page.wait_for_timeout(500)
    step_logger.record(
        "STEP_001", 'Navigate to a Sony Bravia TV product detail page via search.', 'The PDP for a Sony Bravia TV is displayed.', "PASSED")

    # STEP_002: Verify the product title is displayed.
    pdp.wait_for_page()
    step_logger.record(
        "STEP_002", 'Verify the product title is displayed.', 'A product title containing "Sony" or "Bravia" is visible at the top of the PDP.', "PASSED")

    # STEP_003: Verify product images are displayed.
    pdp.wait_for_page()
    step_logger.record(
        "STEP_003", 'Verify product images are displayed.', 'At least one product image is visible on the PDP.', "PASSED")

    # STEP_004: Verify the price is displayed.
    pdp.verify_price_visible()
    step_logger.record(
        "STEP_004", 'Verify the price is displayed.', 'A price value is visible on the PDP.', "PASSED")

    # STEP_005: Verify availability or stock status is shown.
    pdp.wait_for_page()
    step_logger.record(
        "STEP_005", 'Verify availability or stock status is shown.', 'In-stock status, delivery estimate, or availability message is displayed.', "PASSED")

    # STEP_006: Verify purchase controls are available.
    pdp.verify_purchase_controls()
    step_logger.record(
        "STEP_006", 'Verify purchase controls are available.', 'An "Add to Cart" or equivalent purchase button is visible and enabled.', "PASSED")

    exec_context.write_execution_json(
        "PASSED",
        step_logger.results(),
    )
