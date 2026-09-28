# TC_AMAZON_009

## Metadata

- ID: TC_AMAZON_009
- Title: Cart Contains Both Sony Bravia 43-Inch and 55-Inch TVs Simultaneously
- Module: AmazonShopping
- Priority: High
- Type: UI
- Tags: regression, guest, cart, sony-bravia, multi-item

## Preconditions

- Amazon website (https://www.amazon.com) is accessible.
- User is browsing as a guest.
- Sony Bravia 43-inch TV has been added to the cart.
- Sony Bravia 55-inch TV has been added to the cart.

## Test Data

- product_43: Sony Bravia 43 inch TV
- product_55: Sony Bravia 55 inch TV

## Steps

### STEP_001

**Action**

Add the Sony Bravia 43-inch TV to the cart via its PDP.

**Expected Result**

The 43-inch TV is added to the cart successfully.

### STEP_002

**Action**

Add the Sony Bravia 55-inch TV to the cart via its PDP.

**Expected Result**

The 55-inch TV is added to the cart; cart item count shows 2.

### STEP_003

**Action**

Navigate to the cart.

**Expected Result**

The cart page is displayed.

### STEP_004

**Action**

Verify the Sony Bravia 43-inch TV is present in the cart.

**Expected Result**

A cart line item with "43" in the product title is displayed.

### STEP_005

**Action**

Verify the Sony Bravia 55-inch TV is present in the cart.

**Expected Result**

A cart line item with "55" in the product title is displayed.

### STEP_006

**Action**

Verify the cart shows 2 distinct items.

**Expected Result**

The cart displays both products with correct individual quantities.
