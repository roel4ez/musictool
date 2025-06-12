---
title: Tracklist Database for Vinyl and Digital Collections
status: Proposed
---

## Context

We aim to identify songs that are available on vinyl (from the `gazmazk4ez` collection) but not in digital form (from the `collection.nml` file). However, the `gazmazk4ez` collection contains release-level information, while the `collection.nml` file contains song-level information. This mismatch complicates direct comparisons.

Additionally, the collections are dynamic: new records may be added to the vinyl collection, and new songs may appear in the digital library. Therefore, the solution must handle updates efficiently.

## Decision

We propose creating a local tracklist database to store detailed information about releases and their associated songs. This database will:

1. **Fetch Tracklists**: Use the Discogs API to retrieve tracklists for all releases in the `gazmazk4ez` collection.
2. **Store Locally**: Save the tracklist data in a structured format (e.g., SQLite database or JSON/CSV file).
3. **Handle Updates**: Provide mechanisms to update the database when new records are added to the vinyl collection or new songs are added to the digital library.

## Options Considered

### Option 1: Fetch Tracklists on Demand
- **Pros**:
  - No need to maintain a local database.
  - Always retrieves the latest data from Discogs.
- **Cons**:
  - Requires frequent API calls, which may hit rate limits.
  - Slower performance due to network latency.

### Option 2: Create a Local Database
- **Pros**:
  - Faster performance by avoiding repeated API calls.
  - Can handle updates incrementally.
  - Provides a single source of truth for tracklist data.
- **Cons**:
  - Requires initial setup and maintenance.
  - May become outdated if not updated regularly.

### Option 3: Hybrid Approach
- **Description**: Use a local database but fetch data from Discogs on demand for missing or outdated entries.
- **Pros**:
  - Combines the benefits of both approaches.
  - Ensures data is up-to-date while minimizing API calls.
- **Cons**:
  - More complex implementation.

## Decision

We choose **Option 3: Hybrid Approach** as it balances performance and data freshness. The local database will store tracklist data, and the system will fetch updates from Discogs as needed.

## Implementation Plan

1. **Database Setup**:
   - Use SQLite for the local database.
   - Define tables for `Releases` and `Tracks`.

2. **Initial Data Population**:
   - Iterate over the `gazmazk4ez` collection.
   - Fetch tracklists for each release using the Discogs API.
   - Store the data in the database.

3. **Update Mechanism**:
   - Provide a function to add new releases to the database.
   - Check for updates to existing releases (e.g., modified tracklists).

4. **Comparison Logic**:
   - Load tracklist data from the database.
   - Compare with the `collection.nml` data to identify missing songs.

## Database Structure

To efficiently manage tracklist data and limit API calls, we propose the following database structure:

### 1. Releases Table
- **Purpose**: Store metadata about each release in the `gazmazk4ez` collection.
- **Columns**:
  - `release_id` (Primary Key): Unique identifier for the release (from Discogs).
  - `catalog_number`: Catalog number of the release.
  - `title`: Title of the release.
  - `artist`: Artist(s) associated with the release.
  - `label`: Label of the release.
  - `format`: Format of the release (e.g., vinyl).
  - `year`: Year of the release.
  - `last_processed`: Timestamp of the last time the release was processed.
  - `tracklist_fetched` (Boolean): Indicates whether the tracklist has been fetched.

### 2. Tracks Table
- **Purpose**: Store detailed track information for each release.
- **Columns**:
  - `track_id` (Primary Key): Unique identifier for the track (auto-generated).
  - `release_id` (Foreign Key): Links to the `Releases` table.
  - `track_title`: Title of the track.
  - `track_artist`: Artist(s) associated with the track.
  - `position`: Position of the track on the release (e.g., A1, B2).

### 3. Change Log Table (Optional)
- **Purpose**: Track changes or updates to the database (e.g., new releases added, tracklists updated).
- **Columns**:
  - `log_id` (Primary Key): Unique identifier for the log entry.
  - `timestamp`: Timestamp of the change.
  - `action`: Description of the action (e.g., "Added release", "Updated tracklist").
  - `details`: Additional details about the change.

## Workflow for Identifying Releases to Process

1. **Check the `Releases` Table**:
   - Query for releases where `tracklist_fetched = FALSE` or `last_processed` is older than a certain threshold.

2. **Fetch Tracklists**:
   - For each unprocessed release, fetch the tracklist using the Discogs API.
   - Update the `Releases` table to set `tracklist_fetched = TRUE` and update the `last_processed` timestamp.

3. **Store Tracklists**:
   - Insert the tracklist data into the `Tracks` table, linked to the corresponding `release_id`.

4. **Handle Updates**:
   - If a release is reprocessed (e.g., due to changes in the `gazmazk4ez` collection), update the `Tracks` table with the new tracklist.

## Status

This ADR is currently in the **Proposed** state. Feedback and suggestions are welcome before implementation begins.
