# CTFTiny index metadata

`index-metadata.json` is kept because `tests/test_challenge.py`
(`test_recorded_split_matches_metadata_only_selection`) reads it. The test checks that
the held-out IDs in `configs/ctftiny.json` are the first ten IDs ranked by SHA-256 of
`ctf590-v1:<id>`.
