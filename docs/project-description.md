# Ideas for features of musictool

Looking to create a music management tool, based on my local collection. My
collection consists of physical vinyl records, described in a discogs csv file,
and my digital collection of mp3, flac, and aiff files.


Multiple datasources:

- NML file from Traktor Pro
    - this file should only be written to with explicit approval from user
    - we should keep a local copy, and think of a way to sync changes to our
      local copy
    - the source of truth
- CSV export file from discogs. Contains a record collection, listing _releases_
    - this collecting is not very consistent:
        - catalog number complexity
        - artist relation complexity
        - label duplication
        - format inconsistencies
- Discogs API, especially /search endpoint
    - API key available in /.env

1. the export file can be extended to include all song information. The relation
   is that 1 release can have multiple songs. However, the discogs API could
   return multiple matches for 1 release - how do we solve this?

1. I want to identify which songs there are on vinyl, but not in the digital
   collection. Can we create "ghost" entries in the local collection?

1. I want to be able to edit metadata
    - manually
    - by looking up info from discogs
    - in batch (multiple songs together)

1. ideally, we work on local copies of the files, and provide a mechanism to
   import new or updated collections, and export any changes back to the nml collection.

## Open questions:

- if we update the NML file, do we still need to update the actual file tags as
  well? I assume we do. 

