# Zero-model web target diagnostic

November 7, 2026. Fresh supplied target startup plus fixed HTTP status-only probes
from the isolated solver on the assigned port **80**. No model calls, solving,
flag submissions, scope expansion, target-image change or agent change.

[Samples and results](check.json) show MongoDB repeatedly restarting with exit
**132**, no OOM kill, and the explicit warning that MongoDB 5.0+ requires AVX
support unavailable here. Restart counts grew from 3 to 9. The Node app initially
responded through nginx, then exited with code 1 and database hostname/connection
errors (`getaddrinfo ENOTFOUND mongo`). The final approved HTTP probes timed out.
The source nginx config proxies frontend port 80 to `nodeserver:4999` on the
private backend network. Port 4999 on the nginx container is not an additional
assigned endpoint, and adding it would not repair the database.

This independently demonstrates a target CPU/emulation compatibility failure.
It supports an explanation for the pilot's 502 responses; it does not prove the
exact timing of every pilot process because pilot backend logs were not retained.
The agent subsequently probing unapproved ports remains a distinct scope violation.

Cleanup passed. The existing TCP-only preparation/isolation check can pass while
a dependency is restarting: Docker reports `Running=true` during this restart
loop. That result is not full application health. A narrowly scoped readiness
improvement and a compatible Mongo/host choice need separate review. No image,
scope or application code changes were made during this diagnostic.

Generated Compose snapshots remain local/private and Git-ignored because they
can contain target answer/environment data. Sanitized service diagnostics above
exclude those values. Detailed conversational trace review remains with the user.
