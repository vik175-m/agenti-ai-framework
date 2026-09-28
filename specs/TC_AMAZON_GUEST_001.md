# TC_AMAZON_GUEST_001

## Metadata

- ID: TC_AMAZON_GUEST_001
- Title: Guest User Searches and Views iPhone 18 Pro Max Product Details
- Module: AmazonShopping
- Priority: High
- Type: UI
- Tags: smoke, guest, search, amazon

## Preconditions

- Amazon website (https://www.amazon.com) is available.
- User is browsing as a guest (not logged in, no existing session).

## Test Data

- search_term: iPhone 18 Pro Max

## Steps

### STEP_001

**Action**

Navigate to the Amazon homepage.

**Expected Result**

Amazon homepage should be displayed with the search bar visible.

### STEP_002

**Action**

Enter "${search_term}" into the search bar.

**Expected Result**

The search term should be accepted and visible in the search bar.

### STEP_003

**Action**

Submit the search.

**Expected Result**

Search results page should be displayed with listings related to "${search_term}".

### STEP_004

**Action**

Open the first matching product from the search results.

**Expected Result**

The product detail page should be displayed.

### STEP_005

**Action**

Verify the product title on the product detail page.

**Expected Result**

The product title should be relevant to "${search_term}".
