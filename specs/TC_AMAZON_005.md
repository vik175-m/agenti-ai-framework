# TC_AMAZON_005

## Metadata

- ID: TC_AMAZON_005
- Title: Guest User Opens Sony Bravia 43-Inch TV Product Detail Page from PLP
- Module: AmazonShopping
- Priority: High
- Type: UI
- Tags: smoke, guest, plp, pdp, sony-bravia, 43-inch

## Preconditions

- Amazon website (https://www.amazon.com) is accessible.
- User is on the Sony Bravia TV product listing page.
- User is browsing as a guest.

## Test Data

- search_term: Sony Bravia 43 inch TV
- expected_product_keyword: 43

## Steps

### STEP_001

**Action**

Navigate to the Amazon homepage and search for "${search_term}".

**Expected Result**

The Sony Bravia TV product listing page is displayed.

### STEP_002

**Action**

Identify and click on a Sony Bravia 43-inch TV product from the listing.

**Expected Result**

The browser navigates to the product detail page for the selected item.

### STEP_003

**Action**

Verify the product detail page title contains "${expected_product_keyword}".

**Expected Result**

The product title on the PDP contains "43" indicating the correct 43-inch variant is displayed.
