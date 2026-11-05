# Approved solver libraries and command guidance — November 4, 2026

Scope: six approved libraries, live command output increased to 32 KiB, and clearer
network-deadline/session guidance. Reedsolo was excluded. The live command limit
stays at 30 seconds, with a 300-second attempt wall limit and terminal command
timeout. The system prompt, model settings and endpoint-only network policy are
unchanged by this milestone. No model requests or challenge-solving attempts ran;
model API spending was **$0**.

| Direct library | Verified installed version |
| --- | --- |
| pwntools | 4.15.0 |
| SymPy | 1.14.0 |
| NumPy | 2.5.4 |
| PyCryptodome (`Crypto`) | 4.3.0 |
| requests | 2.34.2 |
| Pillow | 13.0.0 |

The [input](../../docker/solver-requirements.in) and
[resolved requirements](../../docker/solver-requirements.txt) pin 40 packages
including dependencies for Python 3.13.2 on AMD64 Linux. Docker runs `pip check`;
[installed versions](python-packages.txt) include base-image packaging tools too.
The host's `pyproject.toml`/`uv.lock` were not changed.

| Evidence | Actual verification |
| --- | --- |
| [Initial build](build.log), [final build](build-final.log) | Dependencies downloaded during image build; no runtime registry access enabled. Final image sets `PWNLIB_NOTERM=1` for the noninteractive worker. |
| [Fast tests](fast-tests.xml) | 64 passed. |
| [Full controls suite](self-check-0b93b7381e00/suite.json), [output](controls.log) | 23 passed on the library image before the final non-terminal setting; cleanup verified. |
| [Final-image checks](final-checks.xml), [output](final-checks.log) | Four passed after that setting: library/network workflows, output bounds, filesystem/credential boundaries and blocked curl. Full per-attempt SDK spans and summaries are in `final-checks/`. |
| [Final library probe](final-checks/7d10a7e2c404/otel-spans.json) | Benign ELF/packing, symbolic/numeric math, AES round-trip, PNG round-trip, requests and pwntools HTTP access to the permitted fixture all passed. A deliberately stalled read returned after approximately 0.22 seconds without stopping the attempt. Whole worker command took approximately 1.35 seconds, with empty stderr. |
| [Final provenance](provenance.json) | Actual image IDs, source hashes including both requirements files, and live/model settings. |

Final solver image:
`sha256:c0b3c2a21c74b38b59ff56d97f9d54bc41b9cd0d6454164dea291cb07c1549ef`.

The output check retained 17,001 stdout bytes plus a diagnostic on stderr. A
40,001-byte output was correctly truncated within the 32,768-byte combined bound.
The initial synthetic configuration still uses 16 KiB and a 10-second command
limit; the live configuration explicitly overrides output to 32 KiB and retains
30 seconds. Checks that exercise those values use explicit overrides.

The terminal setting uses pwntools' supported
[non-terminal branch](https://github.com/Gallopsled/pwntools/blob/4.15.0/pwnlib/term/unix_termcap.py).
It removes the otherwise harmless missing-terminfo warning. It does not repair
the previously observed live GDB limitation on Apple Silicon.

Reproduce using the normal commands from the repository root:

```sh
uv run --frozen python -m ctf_agent build-images
uv run --frozen python -m pytest tests -q --disable-plugin-autoload
uv run --frozen python -m ctf_agent self-check
```

To update solver dependencies, edit the input file, regenerate the resolved file,
then rebuild and check the image:

```sh
uv pip compile docker/solver-requirements.in --python-version 3.13.2 --python-platform x86_64-manylinux_2_36 --no-header --no-annotate --index-url https://pypi.org/simple --output-file docker/solver-requirements.txt
```

Network deadlines remain guidance, not automatic enforcement of socket options.
Outputs larger than the cap can still lose a late error; scripts must preserve
their own terminal buffers. Library availability and these benign checks do not
establish improved solve rate. [Experiment 2](../../docs/EXPERIMENTS.md#experiment-2--solver-libraries-output-visibility-and-network-guidance)
records the rationale and the pending live comparison.
