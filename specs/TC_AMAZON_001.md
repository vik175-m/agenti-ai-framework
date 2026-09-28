# TC_AMAZON_001

## Metadata

- ID: TC_AMAZON_001
- Title: Guest User Verifies Amazon Homepage Loads Successfully
- Module: AmazonShopping
- Priority: High
- Type: UI
- Tags: smoke, guest, homepage, navigation

## Preconditions

- Amazon website (https://www.amazon.com) is accessible.
- User is browsing as a guest (not logged in, no existing session).

## Test Data

- (none)

## Steps

### STEP_001

**Action**

Navigate to the Amazon homepage (https://www.amazon.com).

**Expected Result**

The Amazon homepage loads successfully with no errors.

### STEP_002

**Action**

Verify primary navigation is visible.

**Expected Result**

The top navigation bar, logo, and main menu links are displayed.

### STEP_003

**Action**

Verify the search bar is visible and accessible.

**Expected Result**

The search input field and search submit button are visible on the page.

### STEP_004

**Action**

Verify product/content sections are visible.

**Expected Result**

At least one product or content section is visible on the homepage.

### STEP_005

**Action**

Verify guest shopping controls are available.

**Expected Result**

Sign-in prompt or guest user controls are visible; no authenticated user state is shown.
