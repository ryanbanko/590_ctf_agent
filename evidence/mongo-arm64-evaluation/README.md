# Same-release ARM64 MongoDB evaluation

November 7, 2026. **Passed: two fresh zero-model functional cycles.** Matching
ARM64 MongoDB fixes the reproduced target startup/database failure on this machine.
The normal project configuration and dataset remain unchanged pending review.
No model calls, solving, flag submissions, agent change or scope expansion.

Subsequently adopted through the reviewed
[normal launcher integration](../mongo-arm64-integration/README.md). The evaluation
statements below describe the prior temporary-substitution checkpoint.

## Artifact and reuse

The supplied database is **AMD64 MongoDB 7.0.9**. The official `mongo:7.0.9`
release index contains both that exact original AMD64 manifest and an ARM64
sibling. The tested pinned candidate is:

`mongo@sha256:8ff69162926750978451697274dc3c93eac609894b9cff7ed977e76e6bcabcbe`

It is **MongoDB 7.0.9, Ubuntu Jammy, ARM64/v8**, from the same official release
build. No database downgrade, custom Mongo build, replacement application or
new runtime subsystem. [Original image](original-image.json), [candidate image](candidate-image.json),
[official manifest](manifest-vpn-off.json), [version probe](candidate-version.txt).
MongoDB's [platform requirements](https://www.mongodb.com/docs/manual/administration/production-notes/)
explain the differing x86 AVX and ARM CPU requirements; local tests establish
whether this particular artifact works on this Docker host.

Initial manifest/pull attempts failed while VPN-connected, with IPv6 socket/EOF
errors. After the user disconnected VPN, ordinary Docker pull succeeded in
**9.617s**. No alternate registry/version or download subsystem was introduced.
[Initial pull](pull-result.json), [successful pull](pull-vpn-off-result.json).

## Functional and boundary checks

[Complete checks](checks.json) and per-cycle local SDK observations record:

- Authenticated database ping succeeds.
- Assigned frontend port **80** returns HTTP 200.
- Benign fresh-user registration returns 201 with success confirmation, login
  returns 200, and that user's own profile returns 200. No protected flag route
  or evaluator submission is used.
- MongoDB, Node and nginx remain running after 35 seconds in each cycle, with
  **zero restarts**, zero exit errors and no OOM kills. The prior AMD64 diagnostic
  instead showed Mongo restart loops/exit 132 and eventual Node exit.
- The same normal test username registers successfully in both new deployments;
  distinct containers/volumes and verified volume removal establish fresh state.
- Requests execute in the existing isolated UID-1000 solver, without host keys or
  Docker socket. The normal guard/evaluator boundary remains. In cycle two, an
  intentional port-4999 probe is still denied and stops the solver as designed.
  That deliberate diagnostic incident is not a model attempt or a missing port.
- Expected answer is absent from local spans; zero model calls; solver/target
  cleanup and final absence of managed containers/networks pass.

The existing project Compose integration and runner were reused. An evaluation-only
in-memory substitution replaced **only Mongo's image and platform**, recording the
adjustment; no dataset or application source was edited. Supplied Node/nginx,
commands, environment, networks and endpoint scope were preserved. Original Mongo
RootFS remains intact. [Input hashes/preservation](evaluation-inputs.json).
Generated runtime Compose files stay local/Git-ignored because they contain private
deployment data. No default image tag, permanent override, new configuration field,
readiness implementation, commit or push was added.

## Recommendation

Adopt this exact same-release ARM64 Mongo manifest on ARM64 Docker hosts for the
specific supplied AMD64 digest; retain the supplied digest on native AMD64 hosts.
Keep it an explicit, recorded compatibility adjustment in the existing target
integration. Do not add a general registry resolver, broad image replacement
policy, new container backend, port allowance or dependency downgrade.

Also make the existing preparation checks reject restarting/exited/unhealthy
services and report restart counts, using supplied health status where available.
This is a narrow response to the observed false readiness pass; it does not make
TCP checks a universal application-health guarantee. Add focused checks for that
behavior and rerun this environment's normal preparation after integration.
A live web retry remains a separately reviewed stage; the original failed pilot
must remain recorded. No solve-rate improvement is claimed from these checks.

Architecture differs even with matching Mongo/server release, so this result is
local compatibility evidence, not proof of identical CPU performance or every
possible application operation. Other challenges were not rerun here.
