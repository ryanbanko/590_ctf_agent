# CTFTiny readiness — work in progress

November 3, 2026 (America/New_York). This approved milestone prepares one development
challenge without model calls or solving. It is **not complete**.

The public [CTFTiny index](https://raw.githubusercontent.com/NYU-LLM-CTF/CTFTiny/main/ctftiny.json)
was read through the available web tool. Only index metadata was saved in
[index-metadata.json](index-metadata.json). A dataset checkout and immutable revision
have not yet been obtained. The canonical JSON hash is recorded in
`configs/ctftiny.json`; revision remains null so loading cannot proceed accidentally.

The ten scored IDs are the first ten when all IDs are ordered by SHA-256 of the
UTF-8 string `ctf590-v1:<id>`. The remainder are development. This fixed method used
no challenge answers, solutions, performance, or target compatibility. The readiness
candidate is `pwn-baby-boi`, the first development pwn ID in lexical order. No scored
challenge contents or individual development answers/solutions have been read.

`ctf_agent/challenge.py` adds only trusted loading/public-field construction and
listed-file validation/staging. Standard Docker tar input carries file bytes into
the solver with UID/GID 1000 and no host mounts. Archive contents, hashes, ownership,
path restrictions, and the public/private boundary were checked offline. No actual
Docker copy, benchmark load, target start, connectivity, or reset has been verified.

Actual verification:

```sh
.venv/bin/python -m pytest -q --disable-plugin-autoload --junitxml=evidence/ctftiny-readiness/pytest-fast.xml
```

[JUnit](pytest-fast.xml): **53 passed**, 19 Docker cases deselected, zero failures,
errors, or skips. No live model requests or paid gateway usage occurred.

The local baseline commit was authorized, and candidate baseline files were checked
for the configured gateway token and Langfuse secret key; neither was found. The
commit command was not executed because automatic approval review reported its own
usage limit. It classified this as a review failure rather than a safety rejection.
No bypass was attempted. Protected Git/package/network/Docker work remains pending.

Remaining approved work: create the local baseline, obtain/pin the dataset and loader,
inspect only the selected development Compose setup, implement its minimal lifecycle/
connection mapping, verify real staging/connectivity/reset/cleanup, and document the
preparation command. Do not infer benchmark readiness from the offline cases.
