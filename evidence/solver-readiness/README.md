# Solver environment and timeout contract — November 4, 2026

Approved scope: correct baseline solver execution/tooling and expose the active
command timeout to the model. Recovery behavior is deferred. No model requests,
challenge-solving attempts, hosted uploads or API spending were made.

The three reviewed development attempts (`challenge-ab3134582f2c`,
`challenge-c6f12d005a7b`, `challenge-3dd76ec6c9cb`) all ended without success or
submissions, before exhausting their limits. They exposed missing utilities,
oversized timeout requests and a permission failure executing a handout binary.
Other model/script recovery problems remain outside this change.

Hypothesis stated before the checks: standard utilities, executable workspace
mounts and an x86-compatible solver remove incidental environment failures;
including the real timeout maximum/default in the tool schema removes the need
to discover that limit by rejection. These checks establish environment behavior,
not improved solve rate or fewer invalid model calls.

| Evidence | Result |
| --- | --- |
| [Before probe](before.json), [SDK spans](before-spans.json) | ARM64 solver; `/workspace` mounted `noexec`; copied `/bin/true` fails with errno 13. Common utilities absent. |
| [Contestant formats](file-formats.json) | Listed filenames and first 20 bytes only: 20 ELF64 x86-64 and two ELF32 x86 files. No solution analysis. |
| [Final build](build-final.log), [installed OS packages](os-packages.txt) | AMD64 solver; standard inspection, connection, archive, C compiler/debugger utilities and 32-bit runtime libraries. Python dependencies unchanged. Earlier build log preserves the intermediate build. |
| [Fast tests](fast-tests.xml) | 64 passed. Effective 10/30-second schema maximum/default reach response callbacks and SDK traces without mutating static definitions. |
| [Controls suite](self-check-c5bb4fa7337a/suite.json), [test output](controls.log) | 21 passed; cleanup verified. Benign copied/compiled executable, utility workflows, permitted curl/nc access, blocked curl, other network/isolation/deadline/evaluator checks. Full per-attempt SDK spans retained beside summaries. |
| [Capability probe](after.json), [SDK spans](after-spans.json) | Benign AMD64 and dynamically linked i386 executables exit 0. Workspace retains `nosuid,nodev` and permits execution; root remains read-only. GDB child execution fails with register/ptrace errors on this Apple Silicon Docker setup; static GDB inspection passed in the suite. |
| [Challenge preparation](ctftiny-readiness-aaaa6d25a582/check.json) | `cry-ecxor` passes two fresh staging/isolation/cleanup cycles; no solving. |

Solver image ID: `sha256:f129145d36f35fa2e94c7bcdf228ffc34247407d2f27fd3e8516b5bdcec0f2ca`.
Full image/source/configuration provenance is in the controls suite and after probe.

Reproduce from the repository root, with Docker running:

```sh
uv run --frozen python -m ctf_agent build-images
uv run --frozen python -m pytest tests -q --disable-plugin-autoload
uv run --frozen python -m ctf_agent self-check
uv run --frozen python -m ctf_agent prepare-challenge --challenge cry-ecxor
```

Use native AMD64 Linux when live debugging is needed. Arbitrary binaries and
specialized requirements such as Sage, Android tooling or ML packages are not
established by these baseline checks. Numeric limits and recovery/stopping policy
were not changed. Installing curl did not widen network permissions.
