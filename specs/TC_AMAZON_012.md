# TC_AMAZON_012

## Metadata

- ID: TC_AMAZON_012
- Title: Guest User Increases and Decreases Sony Bravia TV Quantity in Cart
- Module: AmazonShopping
- Priority: Medium
- Type: UI
- Tags: regression, guest, cart, sony-bravia, quantity, cart-update

## Preconditions

- Amazon website (https://www.amazon.com) is accessible.
- User is browsing as a guest.
- Cart contains one Sony Bravia TV with quantity 1.

## Test Data

- search_term: Sony Bravia TV
- initial_quantity: 1
- increased_quantity: 2

## Steps

### STEP_001

**Action**

Add a Sony Bravia TV to the cart and navigate to the cart page.

**Expected Result**

Cart displays the Sony Bravia TV with quantity "${initial_quantity}".

### STEP_002

**Action**

Increase the quantity of the Sony Bravia TV to "${increased_quantity}" using the quantity control.

**Expected Result**

The quantity updates to "${increased_quantity}" and the cart subtotal is updated accordingly.

### STEP_003

**Action**

Verify the cart subtotal reflects 2 units of the Sony Bravia TV.

**Expected Result**

The subtotal is approximately double the single-unit price.

### STEP_004

**Action**

Decrease the quantity back to "${initial_quantity}" using the quantity control.

**Expected Result**

The quantity updates to "${initial_quantity}" and the cart subtotal reverts to the single-unit price.
