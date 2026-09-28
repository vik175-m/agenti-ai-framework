# TC_AMAZON_004

## Metadata

- ID: TC_AMAZON_004
- Title: Sony Bravia TV PLP Filters and Sorting Options Work Correctly
- Module: AmazonShopping
- Priority: Medium
- Type: UI
- Tags: regression, guest, plp, filters, sorting, sony-bravia

## Preconditions

- Amazon website (https://www.amazon.com) is accessible.
- User is on the Sony Bravia TV product listing page.
- User is browsing as a guest.

## Test Data

- search_term: Sony Bravia TV
- sort_option: Price: Low to High

## Steps

### STEP_001

**Action**

Navigate to the Sony Bravia TV product listing page by searching for "${search_term}".

**Expected Result**

The PLP is displayed with multiple product results.

### STEP_002

**Action**

Apply the "${sort_option}" sorting option from the sort dropdown.

**Expected Result**

The sort option is selected and the page updates.

### STEP_003

**Action**

Verify the product listing is reordered after applying the sort.

**Expected Result**

Products are displayed in ascending price order.

### STEP_004

**Action**

Apply a filter from the left-hand filter panel (e.g. brand or screen size).

**Expected Result**

The filter is applied and the product count or list is updated to reflect the selection.

### STEP_005

**Action**

Verify only filtered results are shown.

**Expected Result**

Displayed products are consistent with the applied filter criteria.
