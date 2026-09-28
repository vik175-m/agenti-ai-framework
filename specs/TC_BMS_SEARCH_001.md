# TC_BMS_SEARCH_001

## Metadata

- ID: TC_BMS_SEARCH_001
- Title: Guest User Searches and Views Movie Details on BookMyShow
- Module: BookMyShow
- Priority: High
- Type: UI
- Tags: smoke, guest, search, bookmyshow

## Preconditions

- BookMyShow website (https://in.bookmyshow.com) is available.
- User is browsing as a guest (not logged in, no existing session).
- A city context is available (either a default city or one selected during navigation).

## Test Data

- movie_name: ${MOVIE_NAME}

## Steps

### STEP_001

**Action**

Navigate to the BookMyShow homepage.

**Expected Result**

BookMyShow homepage should be displayed with the search bar visible.

### STEP_002

**Action**

Enter "${movie_name}" into the search bar.

**Expected Result**

The search term should be accepted and visible in the search bar.

### STEP_003

**Action**

Submit the search.

**Expected Result**

Search results should be displayed with listings related to "${movie_name}".

### STEP_004

**Action**

Open the first matching movie from the search results.

**Expected Result**

The movie details page should be displayed.

### STEP_005

**Action**

Verify the movie title on the movie details page.

**Expected Result**

The movie title should be relevant to "${movie_name}".
