# TC_AMAZON_003

## Metadata

- ID: TC_AMAZON_003
- Title: Sony Bravia TV Product Listing Page Displays Relevant Products
- Module: AmazonShopping
- Priority: High
- Type: UI
- Tags: regression, guest, plp, sony-bravia, search-results

## Preconditions

- Amazon website (https://www.amazon.com) is accessible.
- User is on the Sony Bravia TV search results / product listing page.
- User is browsing as a guest.

## Test Data

- search_term: Sony Bravia TV

## Steps

### STEP_001

**Action**

Navigate to the Amazon homepage and search for "${search_term}".

**Expected Result**

The product listing page for Sony Bravia TV is displayed.

### STEP_002

**Action**

Verify product names are visible in the listing.

**Expected Result**

At least one product title containing "Sony" or "Bravia" is displayed.

### STEP_003

**Action**

Verify product images are displayed.

**Expected Result**

Each listed product has a corresponding product image.

### STEP_004

**Action**

Verify product prices are displayed.

**Expected Result**

Price information is visible for the listed products.

### STEP_005

**Action**

Verify ratings are displayed where available.

**Expected Result**

Star ratings or review counts are visible for products that have them.

### STEP_006

**Action**

Verify shopping actions are available.

**Expected Result**

Each product card displays a link or button to view or purchase the product.
