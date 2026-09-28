# TC_AMAZON_016

## Metadata

- ID: TC_AMAZON_016
- Title: Guest User Completes iPhone 18 Pro Checkout Journey to Payment Handoff
- Module: AmazonShopping
- Priority: Critical
- Type: E2E
- Tags: smoke, guest, e2e, checkout, iphone, order-summary, payment

## Preconditions

- Amazon website (https://www.amazon.com) is accessible.
- User is browsing as a guest (no Amazon account required).
- Test stops before submitting real payment or placing a real order.

## Test Data

- product: iPhone 18 Pro
- guest_email: <guest_email>
- delivery_address: <delivery_address>

## Steps

### STEP_001

**Action**

Navigate to the Amazon homepage and search for "${product}".

**Expected Result**

Search results for iPhone 18 Pro are displayed.

### STEP_002

**Action**

Open the iPhone 18 Pro product detail page and add it to the cart.

**Expected Result**

iPhone 18 Pro is added to the cart.

### STEP_003

**Action**

Proceed to checkout from the cart.

**Expected Result**

The checkout journey begins; guest checkout path is available.

### STEP_004

**Action**

Complete the delivery information step with "${guest_email}" and "${delivery_address}".

**Expected Result**

Delivery information is accepted and the next checkout step is displayed.

### STEP_005

**Action**

Verify the order summary is displayed with the correct product and total.

**Expected Result**

Order summary shows iPhone 18 Pro with correct quantity and price.

### STEP_006

**Action**

Verify the payment step is reached (do not submit payment).

**Expected Result**

Payment options or payment form is displayed confirming end of the pre-payment checkout journey.
