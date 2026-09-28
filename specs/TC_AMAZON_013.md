# TC_AMAZON_013

## Metadata

- ID: TC_AMAZON_013
- Title: Guest User Searches for iPhone 18 Pro and Adds It to Cart
- Module: AmazonShopping
- Priority: High
- Type: UI
- Tags: smoke, guest, pdp, cart, iphone, add-to-cart

## Preconditions

- Amazon website (https://www.amazon.com) is accessible.
- User is browsing as a guest.
- Cart is empty.

## Test Data

- search_term: iPhone 18 Pro
- expected_product_keyword: iPhone 18 Pro

## Steps

### STEP_001

**Action**

Navigate to the Amazon homepage and search for "${search_term}".

**Expected Result**

Search results or product listing page for iPhone 18 Pro is displayed.

### STEP_002

**Action**

Open the relevant iPhone 18 Pro product detail page from the listing.

**Expected Result**

The PDP for iPhone 18 Pro is displayed with the correct product title.

### STEP_003

**Action**

Click the "Add to Cart" button.

**Expected Result**

iPhone 18 Pro is added to the cart; a confirmation or cart count update is shown.

### STEP_004

**Action**

Navigate to the cart.

**Expected Result**

The cart page is displayed.

### STEP_005

**Action**

Verify the iPhone 18 Pro is listed in the cart.

**Expected Result**

A cart line item containing "${expected_product_keyword}" is displayed with quantity 1.
