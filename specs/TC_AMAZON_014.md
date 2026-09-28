# TC_AMAZON_014

## Metadata

- ID: TC_AMAZON_014
- Title: Guest User Proceeds from iPhone 18 Pro Cart to Checkout
- Module: AmazonShopping
- Priority: High
- Type: UI
- Tags: smoke, guest, cart, checkout, iphone, guest-checkout

## Preconditions

- Amazon website (https://www.amazon.com) is accessible.
- User is browsing as a guest.
- Cart contains one iPhone 18 Pro.

## Test Data

- product: iPhone 18 Pro

## Steps

### STEP_001

**Action**

Navigate to the cart containing the "${product}".

**Expected Result**

Cart page is displayed with the iPhone 18 Pro as a line item.

### STEP_002

**Action**

Click the "Proceed to Checkout" button.

**Expected Result**

The checkout journey is initiated and the first checkout step is displayed.

### STEP_003

**Action**

Verify the guest checkout option is available or the checkout proceeds without requiring a logged-in account.

**Expected Result**

A guest checkout option, sign-in prompt with guest path, or direct checkout form is displayed.
