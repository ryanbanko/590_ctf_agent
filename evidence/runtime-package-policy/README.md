# Temporary runtime pip default — November 4, 2026

The user approved a reversible change so ordinary missing-package installation
can fail as a tool observation rather than trigger a scope stop. Package repository
access is awaiting course clarification. The firewall, scope incident handling,
batch stop policy, installed libraries and model settings are unchanged.

The solver Dockerfile sets these **after** its normal build-time installs:

```dockerfile
# Temporary runtime default while package-repository access is being clarified.
ENV PIP_NO_INDEX=1 PIP_DISABLE_PIP_VERSION_CHECK=1
```

The command description tells the agent runtime package downloads are unavailable.
This uses [pip's existing no-index setting](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-no-index),
not a custom package manager or download filter. It is a default, not an enforced
boundary: overrides, direct URLs and other download commands remain subject to
the existing network guard and scope stopping policy. No QR decoder was added.

| Evidence | Result |
| --- | --- |
| [Recorded incident](incident.json) | Prior batch completed two attempts, including one verified success, then stopped on a pip-triggered DNS lookup for `pypi.org`; records and cleanup were complete. |
| [Build log](build.log) | Solver rebuilt with only the runtime defaults added; build-time dependency installation remains available. |
| [Fast tests](fast-tests.xml) | 81 passed. |
| [Controls suite](self-check-5a62edf95e5f/suite.json), [output](controls.log) | 24 passed; cleanup verified. Includes the existing real network-denial checks. Source/configuration/image provenance is retained in the suite. |
| [Pip probe SDK spans](self-check-5a62edf95e5f/0cfd436ae391/otel-spans.json) | Missing package returns exit 1 with “No matching distribution found” in about 0.42 seconds, without timing out or triggering a scope stop. A second command prints `still-running` successfully in the same attempt. |

Solver image:
`sha256:577ecb2fa53b1105df78c401f03f7d171ac46a3ee1a885658d6a3e5301ebfaa0`.

**Reverse:** remove the marked ENV line and its comment from
`docker/solver.Dockerfile`, adjust the corresponding download guidance in
`ctf_agent/tools.py`, and rebuild the solver. This reverses the pip default; it
does not enable network access. Course clarification and a separate reviewed
network-policy change would still be needed for online package downloads.

Reproduce the checks:

```sh
uv run --frozen python -m ctf_agent build-images
uv run --frozen python -m pytest tests -q --disable-plugin-autoload
uv run --frozen python -m ctf_agent self-check
```

No real challenge or model API calls ran during this fix. The model's future
behavior is untested: it may use available tools, end unsuccessfully, or attempt
another blocked request. A missing dependency remains a possible solve blocker.
