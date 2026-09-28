# TC_AMAZON_015

## Metadata

- ID: TC_AMAZON_015
- Title: Guest User Increases and Decreases iPhone 18 Pro Quantity During Checkout
- Module: AmazonShopping
- Priority: Medium
- Type: UI
- Tags: regression, guest, checkout, iphone, quantity, order-total

## Preconditions

- Amazon website (https://www.amazon.com) is accessible.
- User is browsing as a guest.
- User is in the checkout journey with iPhone 18 Pro in the cart.

## Test Data

- product: iPhone 18 Pro
- initial_quantity: 1
- increased_quantity: 2

## Steps

### STEP_001

**Action**

Enter the checkout journey with "${product}" in the cart (quantity "${initial_quantity}").

**Expected Result**

The checkout page or cart review step displays iPhone 18 Pro with quantity "${initial_quantity}".

### STEP_002

**Action**

Increase the quantity of iPhone 18 Pro to "${increased_quantity}" during the cart/checkout stage.

**Expected Result**

The quantity updates to "${increased_quantity}" and the displayed order total is updated.

### STEP_003

**Action**

Verify the order total reflects "${increased_quantity}" units.

**Expected Result**

The order total is approximately double the single-unit price.

### STEP_004

**Action**

Decrease the quantity back to "${initial_quantity}".

**Expected Result**

The quantity updates to "${initial_quantity}" and the order total reverts to the single-unit price.
