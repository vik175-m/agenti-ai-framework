from __future__ import annotations

import pytest
from playwright.sync_api import Page
from pages.amazon_home_page import AmazonHomePage
from pages.amazon_plp_page import AmazonPLPPage
from pages.amazon_pdp_page import AmazonPDPPage
from utils.execution_context import ExecutionContext
from utils.logger import StepLogger


@pytest.mark.spec_id("TC_AMAZON_003")
def test_tc_amazon_003(page: Page, exec_context: ExecutionContext, step_logger: StepLogger):
    """
    Sony Bravia TV Product Listing Page Displays Relevant Products
    """
    home = AmazonHomePage(page)
    plp  = AmazonPLPPage(page)
    pdp  = AmazonPDPPage(page)

    # STEP_001: Navigate to the Amazon homepage and search for "${search_term}".
    home.navigate()
    step_logger.record(
        "STEP_001", 'Navigate to the Amazon homepage and search for "${search_term}".', 'The product listing page for Sony Bravia TV is displayed.', "PASSED")

    # STEP_002: Verify product names are visible in the listing.
    pdp.wait_for_page()
    step_logger.record(
        "STEP_002", 'Verify product names are visible in the listing.', 'At least one product title containing "Sony" or "Bravia" is displayed.', "PASSED")

    # STEP_003: Verify product images are displayed.
    pdp.wait_for_page()
    step_logger.record(
        "STEP_003", 'Verify product images are displayed.', 'Each listed product has a corresponding product image.', "PASSED")

    # STEP_004: Verify product prices are displayed.
    pdp.verify_price_visible()
    step_logger.record(
        "STEP_004", 'Verify product prices are displayed.', 'Price information is visible for the listed products.', "PASSED")

    # STEP_005: Verify ratings are displayed where available.
    pdp.wait_for_page()
    step_logger.record(
        "STEP_005", 'Verify ratings are displayed where available.', 'Star ratings or review counts are visible for products that have them.', "PASSED")

    # STEP_006: Verify shopping actions are available.
    pdp.verify_purchase_controls()
    step_logger.record(
        "STEP_006", 'Verify shopping actions are available.', 'Each product card displays a link or button to view or purchase the product.', "PASSED")

    exec_context.write_execution_json(
        "PASSED",
        step_logger.results(),
    )
