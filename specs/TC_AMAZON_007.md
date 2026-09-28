# TC_AMAZON_007

## Metadata

- ID: TC_AMAZON_007
- Title: Guest User Adds Sony Bravia 43-Inch TV to Cart
- Module: AmazonShopping
- Priority: High
- Type: UI
- Tags: smoke, guest, pdp, cart, sony-bravia, 43-inch, add-to-cart

## Preconditions

- Amazon website (https://www.amazon.com) is accessible.
- User is on the Sony Bravia 43-inch TV product detail page.
- User is browsing as a guest.
- Cart is empty.

## Test Data

- search_term: Sony Bravia 43 inch TV
- expected_product_keyword: 43

## Steps

### STEP_001

**Action**

Navigate to the Sony Bravia 43-inch TV PDP via search for "${search_term}".

**Expected Result**

The PDP for a Sony Bravia 43-inch TV is displayed.

### STEP_002

**Action**

Click the "Add to Cart" button.

**Expected Result**

The product is added to the cart; a confirmation message or cart count update is shown.

### STEP_003

**Action**

Navigate to the cart.

**Expected Result**

The cart page is displayed.

### STEP_004

**Action**

Verify the Sony Bravia 43-inch TV is listed in the cart.

**Expected Result**

The cart contains the correct product with "${expected_product_keyword}" in the product title and quantity is 1.
