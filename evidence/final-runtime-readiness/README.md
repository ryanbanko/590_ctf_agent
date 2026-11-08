# Final-runtime reserved-environment readiness

November 7, 2026. **All ten reserved environments passed two fresh cycles each
(20 cycles), with zero model calls and no challenge solving.** This is environment
readiness, not scored evaluation or evidence of solving compatibility.

Used the normal `prepare-challenge` command sequentially with the unchanged
[development configuration snapshot](experiment.toml) and the newly integrated
NYU default solver. Total elapsed time: **63.506 seconds**. The check program
loads private answers only for trusted privacy audits; they were not inspected
or separately exposed. No target response contents or write-ups were read.

| Challenge | Result | Evidence |
| --- | --- | --- |
| `cry-babycrypto` | Passed | [Two-cycle record](checks/ctftiny-readiness-70ee8637bc5f/check.json) |
| `cry-collision-course` | Passed | [Two-cycle record](checks/ctftiny-readiness-3fc78739af8e/check.json) |
| `for-whyos` | Passed | [Two-cycle record](checks/ctftiny-readiness-e26393eda8b7/check.json) |
| `msc-quantum-leap` | Passed | [Two-cycle record](checks/ctftiny-readiness-88bcaf4b6929/check.json) |
| `msc-weak-password` | Passed | [Two-cycle record](checks/ctftiny-readiness-b008728086e0/check.json) |
| `pwn-puffin` | Passed | [Two-cycle record](checks/ctftiny-readiness-efb59435230e/check.json) |
| `pwn-slithery` | Passed | [Two-cycle record](checks/ctftiny-readiness-efd366818989/check.json) |
| `pwn-unlimited-subway` | Passed | [Two-cycle record](checks/ctftiny-readiness-c3ae8ca2df39/check.json) |
| `rev-rebug-2` | Passed | [Two-cycle record](checks/ctftiny-readiness-eb1ee18c2829/check.json) |
| `web-smug-dino` | Passed | [Two-cycle record](checks/ctftiny-readiness-b939dd34fbd1/check.json) |

Each cycle checks exact contestant-file hashes/ownership, non-root execution with
no effective capabilities, no host/evaluator/credential/socket exposure, bounded
solver setup, supplied target networks and allowed endpoint connect-and-close.
The second cycle deliberately tries a reserved test address to confirm a blocked
request, terminal solver stopping and independent incident evidence. Those
readiness-only `scope_violation` records are intentional control probes, not model
behavior. All cycles check answer absence from traces and cleanup. Distinct run/
network/container identities and equal contestant files establish fresh reset.

[Summary](summary.json), [incremental index](index.json), per-challenge console
logs and local SDK observations are retained. No hosted/model call, source/settings
change, commit or push. This refreshes the older held-out environment checks under
the final runtime while preserving all previous evidence.

The separately approved three-category development pilot still requires its own
readiness and VPN connectivity. No performance or final evaluation claim follows
from these checks alone.
