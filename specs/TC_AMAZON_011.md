# TC_AMAZON_011

## Metadata

- ID: TC_AMAZON_011
- Title: Guest User Removes Sony Bravia 55-Inch TV from Cart Leaving 43-Inch
- Module: AmazonShopping
- Priority: Medium
- Type: UI
- Tags: regression, guest, cart, sony-bravia, remove-item, 55-inch

## Preconditions

- Amazon website (https://www.amazon.com) is accessible.
- User is browsing as a guest.
- Cart contains both Sony Bravia 43-inch TV and Sony Bravia 55-inch TV.

## Test Data

- product_to_remove: Sony Bravia 55 inch TV
- product_remaining: Sony Bravia 43 inch TV

## Steps

### STEP_001

**Action**

Add both Sony Bravia 43-inch and 55-inch TVs to the cart and navigate to the cart page.

**Expected Result**

Cart page is displayed with both TVs as separate line items.

### STEP_002

**Action**

Click the Remove or Delete action for the Sony Bravia 55-inch TV line item.

**Expected Result**

The 55-inch TV line item is removed from the cart.

### STEP_003

**Action**

Verify the Sony Bravia 55-inch TV is no longer in the cart.

**Expected Result**

No cart line item containing "55" is displayed.

### STEP_004

**Action**

Verify the Sony Bravia 43-inch TV remains in the cart.

**Expected Result**

The 43-inch TV line item is still displayed with its original quantity.

### STEP_005

**Action**

Verify the cart total is updated.

**Expected Result**

The cart subtotal reflects only the 43-inch TV price.
