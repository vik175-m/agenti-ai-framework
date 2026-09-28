# TC_AMAZON_006

## Metadata

- ID: TC_AMAZON_006
- Title: Sony Bravia TV PDP Displays Correct Product Information and Purchase Options
- Module: AmazonShopping
- Priority: High
- Type: UI
- Tags: regression, guest, pdp, sony-bravia, product-info

## Preconditions

- Amazon website (https://www.amazon.com) is accessible.
- User is on a Sony Bravia TV product detail page.
- User is browsing as a guest.

## Test Data

- search_term: Sony Bravia TV

## Steps

### STEP_001

**Action**

Navigate to a Sony Bravia TV product detail page via search.

**Expected Result**

The PDP for a Sony Bravia TV is displayed.

### STEP_002

**Action**

Verify the product title is displayed.

**Expected Result**

A product title containing "Sony" or "Bravia" is visible at the top of the PDP.

### STEP_003

**Action**

Verify product images are displayed.

**Expected Result**

At least one product image is visible on the PDP.

### STEP_004

**Action**

Verify the price is displayed.

**Expected Result**

A price value is visible on the PDP.

### STEP_005

**Action**

Verify availability or stock status is shown.

**Expected Result**

In-stock status, delivery estimate, or availability message is displayed.

### STEP_006

**Action**

Verify purchase controls are available.

**Expected Result**

An "Add to Cart" or equivalent purchase button is visible and enabled.
