# Bounded NYU solver-image evaluation

November 6, 2026 (America/New_York), with November 7 follow-up.
**The [8 GiB retry](retry-8g/README.md) subsequently built and passed 34 candidate
checks. Recommend the tested NYU base plus small adapter, pending default integration.**
The remainder of this file preserves the initial canceled build and storage review.
The supplied build was canceled at its host-storage bound, before a candidate
image was exported. NYU runtime compatibility is **untested**, not failed.
No live model calls, hosted uploads, CTFTiny attempts or held-out answer review.

## November 7 storage review

The terminal condition was our selected **10 GiB physical host-space reserve**,
not a Docker/host filesystem-full error. A read-only probe measured about **931
GiB available inside Docker's Linux filesystem**. `Docker.raw` has a **1 TiB
virtual ceiling**, occupying about **40.4 GiB physically**; the Mac had about
**24.4 GiB available** before authorized cleanup. These current measurements are
not historical peak samples. Raising the virtual ceiling cannot add physical
Mac storage. Logical image/cache totals and raw-file allocation are different
accounting measures; do not add them or assume their gap is removable waste.

The build setup was appropriate: standard integrated Docker builder, AMD64,
UID 1000, and only **2,704 bytes** of Dockerfile/entrypoint context. The bulk was
installed software: 5.131 GB initial package layer, 790 MB pip layer, 397 MB
Rust/Cargo layer, other layers and the incomplete external installer. Completed
cache totals exclude the canceled step's temporary peak. No build-time memory,
swap or precise minimum-free-space samples were retained.

Docker is configured for **16 GiB RAM on a 16 GiB Mac**. Current host swap is
about **6.6 GiB**. Swap may have contributed to pressure; its historical share is
unknown. Recommend about **8 GiB** Docker VM memory (Docker's documented default
is 50% of host RAM), without changing solver limits. No allocation change applied.

The largest unrelated image, `nipreps/fmriprep:latest`, had **10.94 GB unique
Docker-reported size** and no dependent containers. The user explicitly approved
its removal; only that image was removed and the working solver identity was
reverified. Follow-up measurement showed host free space increasing from **24.29
to 34.46 GiB**; raw-file allocation fell from about 40.4 to **30.25 GiB**.
Host-space reclamation can lag logical deletion. No other pruning,
allocation change or build retry was performed. [Measurements](storage-review.json),
[removal and recovery measurements](fmriprep-removal.json).

Recommendation revised: give the unchanged candidate a fair monitored retry after
checking recovered host headroom and the RAM setting. Do not use the reserve-
triggered cancellation to settle image suitability. Candidate compatibility still
needs the original checks. [Docker disk accounting](https://docs.docker.com/desktop/troubleshoot-and-support/faqs/macfaqs/),
[resource settings](https://docs.docker.com/desktop/settings-and-maintenance/settings/).

## Inputs and build result

- NYU release `20250206`, commit `112cfa33f5c0a06a20e49af525ac8eb07ec98457`.
  [Exact recipe](https://github.com/NYU-LLM-CTF/nyuctf_agents/blob/112cfa33f5c0a06a20e49af525ac8eb07ec98457/Dockerfile).
  Unchanged build inputs are in [upstream/](upstream/); their URLs and hashes
  are in [source.json](source.json). The current baseline recipe reviewed at
  `612190f298ae9e604f00370019beed4ba1f372f6` had the same Dockerfile hash.
- Source runtime: `00e6a411811b9d076907f6e512fac5b97f20fc96`. Existing uncommitted
  smoke/status documentation was preserved. Docker Desktop 4.44.3 / Engine 28.3.2
  on Apple Silicon; candidate build explicitly `linux/amd64`, `HOST_UID=1000`.
- Separate candidate tag: `ctf590-solver:nyu-20250206-evaluation`. No host NYU
  setup script/framework installation was run. Build context contained only the
  supplied Dockerfile and entrypoint, not project secrets or challenge data.
- Initial build/direct pull failed with Docker Hub EOF errors. The official ECR
  mirror also failed downloading a layer. Host registry/auth requests responded.
  After the user disconnected the VPN, the unchanged build proceeded. This
  establishes the observed sequence, not a general claim about VPN compatibility.
  [Initial failure](build-initial-network.log), [registry diagnostics](registry-diagnostics.json),
  [mirror result](mirror-pull-result.json). Temporary download URL queries are redacted.
- Evaluation bounds: 1,200 seconds or host free space below 10 GiB. These are
  temporary build safeguards, not assignment requirements or agent settings.
  The second bound canceled the build after **567.92 seconds**; time did not expire.
  [Build result](build-result.json), [complete build log](build.log).

The Ubuntu package, radare2/JADX, Python venv and pip-install steps completed.
The external installer then added Kali/Metasploit/Docker repositories and was
installing additional tools when canceled. No source/package failure was the
terminal reason. Successful intermediate installation steps do not prove imports,
executables or controls work in the final runtime.

The first apt step selected **1,068 new packages**, estimating **5,097 MB** added
filesystem data. The completed cache chain occupied **6.742 GB** before cleanup.
Neither is a final image size; final size and full build duration remain unknown.
The installer review snapshot ([source](installer-reviewed.sh), hash in source.json)
is evidence only: the unmodified recipe fetched mutable `master` independently.

## Compatibility, preservation and cleanup

**Eleven existing synthetic Docker cases passed on the current image**, with no
model calls: all three tools and private verification; filesystem/credentials/
privilege boundaries; detached-child timeout/restart recovery; tool and wall
limits; six network-denial cases with incident evidence. These are a subset of
the existing 29-case coverage, not eleven newly added cases.
[Pytest results](current-controls.xml), [console](current-controls.log),
[local summaries and SDK spans](current-controls/).

The current image ID and RootFS match before/after inspection. It retains the
normal tag and gains `ctf590-solver:before-nyu-evaluation-00e6a41`.
[Preservation check](preservation.json). Its local Git-ignored archive is recorded
in [frozen-current-image.json](frozen-current-image.json), including checksum,
size (266,362,880 bytes) and manifest/blob validation. It is not uploaded or
available automatically to teammates; normal setup instructions are unchanged.

No managed containers/networks remain. Only the canceled build's **19** cache
records were pruned by exact IDs after tracing their parent chain and confirming
they were new, private and reclaimable. Docker reported **6.742 GB reclaimed**;
build cache returned from 8.261 GB to 1.52 GB (three tiny source records remain).
The initial cleanup with boolean filters matched nothing; exact-ID cleanup
succeeded. No global prune or image removal was used. Working image identity/
RootFS were reverified after cleanup. [Owned chain](evaluation-cache-chain.json),
[cleanup log](cache-cleanup.log), [disk/cache totals](disk-after-cleanup.txt).

**Not run in the initial canceled attempt** (superseded by the passing retry above):
candidate imports/utilities, standard copying/writing, sudo/effective
permissions, scope/limits, pip installation, restart persistence, fresh-state
checks, or candidate tracing. No workspace overlay was built. Source review
indicates a writable `/workspace` adaptation and environment/path checks would
still be necessary. Missing-library fixes would depend on actual import tests;
no new Python environment or dependency overlay is presumed necessary.

## November 6 initial recommendation (reopened November 7)

Retain our small working image and existing toolkit. This bounded attempt did not
establish a lower-maintenance supplied replacement. We do not declare NYU broken
or incompatible because of a local disk safeguard. A future retry needs adequate
storage and the original compatibility checks; the larger toolkit should address
a concrete need before we adopt its build/distribution burden. No installer fork,
image backend layer or additional runtime subsystem was added.

The professor accepts repository Compose/private controller verification,
Langfuse JSON exports and our CTFTiny development/held-out split. The guide does
not require this image; its sudo/network defaults still require our controls.
Pip permission remains in effect. Existing agent/tools/model, SDK export, TOML,
guard/evaluator and batch wrapper are unchanged.

[Machine-readable result](evaluation.json), [unchanged runtime/test hashes](unchanged-source-sha256.json).
Documentation verification passed: 152 local links, 23 heading links and
`git diff --check`; no application/configuration/test files differ from HEAD.
Stop for review before refreshing the ten environments or starting a separately
authorized live pilot. No solve-rate or agent-behavior improvement is claimed.
