# TC_AMAZON_002

## Metadata

- ID: TC_AMAZON_002
- Title: Guest User Searches for Sony Bravia TV from Homepage
- Module: AmazonShopping
- Priority: High
- Type: UI
- Tags: smoke, guest, homepage, search, sony-bravia

## Preconditions

- Amazon website (https://www.amazon.com) is accessible.
- User is browsing as a guest (not logged in).

## Test Data

- search_term: Sony Bravia TV

## Steps

### STEP_001

**Action**

Navigate to the Amazon homepage (https://www.amazon.com).

**Expected Result**

Amazon homepage loads with the search bar visible.

### STEP_002

**Action**

Enter "${search_term}" into the search bar.

**Expected Result**

The search term is accepted and visible in the search input.

### STEP_003

**Action**

Submit the search.

**Expected Result**

The browser navigates to a search results or product listing page.

### STEP_004

**Action**

Verify the page displays results relevant to "${search_term}".

**Expected Result**

Product listings related to Sony Bravia TV are displayed.
