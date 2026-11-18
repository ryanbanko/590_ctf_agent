"""Build a public task from HTB MCP data and relay flag verdicts; host-only.

The MCP token and all HTB calls stay on the host. The solver receives only the
public task text and network access to the started container's endpoint; the
submit_flag verdict is relayed through verify_candidate, exactly like the manual
path, so no answer key or token ever enters the solver.

Two response shapes are not yet observed on a live container and are isolated
here for confirmation when the event opens: `download_url` (get_download_link)
and `connection_endpoints` (start/status container). Both are defensive and
unit-tested against the shapes HTB is expected to return.
"""

from contextlib import contextmanager
import ipaddress
import json
import socket
import time
import urllib.request

from . import htb_mcp
from .htb_mcp import HtbMcpError
from .manual import import_handouts, MAX_BYTES
from .sandbox import validate_endpoints

# Best-effort HTB category labels; the description is the primary signal, so an
# unknown id falls back to a neutral label rather than a possibly-wrong name.
CATEGORY_NAMES = {
    1: "Fullpwn", 2: "Web", 3: "Pwn", 4: "Crypto", 5: "Reversing",
    6: "Stego", 7: "Forensics", 8: "Misc", 9: "OSINT", 10: "Hardware",
    11: "Mobile", 12: "Blockchain", 13: "Coding", 14: "Cloud", 15: "ICS", 16: "AI",
}


def category_label(challenge: dict) -> str:
    name = challenge.get("category")
    if isinstance(name, str) and name.strip():
        return name.strip()[:64]
    category_id = challenge.get("challenge_category_id")
    if isinstance(category_id, int) and category_id in CATEGORY_NAMES:
        return CATEGORY_NAMES[category_id]
    return f"category {category_id}"


def find_challenge(event: dict, challenge_id: int) -> dict:
    for challenge in event.get("challenges", []):
        if challenge.get("id") == challenge_id:
            return challenge
    available = ", ".join(str(c.get("id")) for c in event.get("challenges", []))
    raise ValueError(f"Challenge {challenge_id} not in event; available: {available or 'none'}")


def download_url(link) -> str:
    """Extract the signed download URL from a get_download_link result.

    CONFIRM AT NOON: handles a bare URL string or a dict carrying it under a
    common key. Raises if no http(s) URL is present.
    """
    if isinstance(link, str) and link.startswith("http"):
        return link
    if isinstance(link, dict):
        for key in ("url", "download_url", "link", "signed_url", "downloadUrl"):
            value = link.get(key)
            if isinstance(value, str) and value.startswith("http"):
                return value
    raise ValueError(f"No download URL in get_download_link result: {json.dumps(link)[:300]}")


def download_files(call, challenge_id: int, work_dir, *, timeout: float = 60.0) -> dict:
    """Download the challenge archive to the host and import bounded handouts."""
    url = download_url(htb_mcp.get_download_link(call, challenge_id))
    archive = work_dir / "download" / "challenge.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": htb_mcp.USER_AGENT})
    total = 0
    with urllib.request.urlopen(request, timeout=timeout) as response, archive.open("xb") as handle:
        while chunk := response.read(1024 * 1024):
            total += len(chunk)
            if total > MAX_BYTES:
                raise ValueError("Challenge download exceeds 512 MiB")
            handle.write(chunk)
    destination = work_dir / "files"
    destination.mkdir(parents=True, exist_ok=True)
    names, _ = import_handouts(archive, destination)
    return {name: destination / name for name in names}


def connection_endpoints(data, *, resolve=socket.gethostbyname) -> list[dict]:
    """Return [{address, protocol, port}] from a container start/status payload.

    CONFIRM AT NOON: the exact fields HTB returns for a running container are not
    yet observed. This scans the known candidate shapes — ip/host/hostname +
    port(s), a 'host:port' connection string, or a docker_ports list — and
    resolves a hostname to IPv4 (the solver has no outbound DNS). Returns [] when
    no connection info is present yet, so the caller can poll.
    """
    endpoints: list[dict] = []
    if not isinstance(data, dict):
        return endpoints
    host = None
    for key in ("ip", "host", "hostname", "server", "address"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            host = value.strip()
            break
    ports: list[int] = []
    for key in ("port", "ports", "docker_ports"):
        value = data.get(key)
        if isinstance(value, int):
            ports.append(value)
        elif isinstance(value, list):
            ports.extend(item for item in value if isinstance(item, int))
        elif isinstance(value, str) and value.isdigit():
            ports.append(int(value))
    # A single 'host:port' connection string.
    for key in ("connection", "connection_string", "ip_port", "entrypoint"):
        value = data.get(key)
        if isinstance(value, str) and ":" in value:
            maybe_host, _, maybe_port = value.rpartition(":")
            if maybe_port.isdigit():
                host = host or maybe_host.strip()
                ports.append(int(maybe_port))
    if host is None or not ports:
        return endpoints
    address = resolve_ipv4(host, resolve)
    for port in dict.fromkeys(ports):  # de-duplicate, preserve order
        if 1 <= port <= 65535:
            endpoints.append({"address": address, "protocol": "tcp", "port": port})
    validate_endpoints(endpoints)
    return endpoints


def resolve_ipv4(host: str, resolve=socket.gethostbyname) -> str:
    """Return host if it is already IPv4, else resolve the hostname on the host."""
    try:
        return str(ipaddress.IPv4Address(host))
    except ipaddress.AddressValueError:
        return str(ipaddress.IPv4Address(resolve(host)))


def flag_verdict(result) -> dict:
    """Map an HTB submit_flag payload to the verify_candidate contract {'correct': bool}.

    HTB reports a WRONG flag as an error with status 400 ("Wrong flag, sorry!"),
    and a correct flag as an accepted result with no error field. A wrong flag is
    a normal rejection; a genuine failure (auth, server, rate limit) is re-raised
    so the attempt stops for review rather than being misread as a wrong flag.

    CONFIRM AT NOON: the exact shape of a CORRECT submission is not yet observed;
    an accepted result (no error) is treated as a solve, with an explicit boolean
    field honoured if present.
    """
    if not isinstance(result, dict):
        raise HtbMcpError("submit_flag", f"unexpected verdict: {result!r}"[:200])
    error = result.get("error")
    if error:
        status = result.get("status_code")
        lowered = str(error).lower()
        if status in (400, 422) or any(word in lowered for word in ("wrong flag", "incorrect", "invalid flag")):
            return {"correct": False}
        raise HtbMcpError("submit_flag", str(error), status)
    for key in ("isCorrect", "correct", "is_correct", "solved", "success"):
        value = result.get(key)
        if isinstance(value, bool):
            return {"correct": value}
    return {"correct": True}


def verify_with_mcp(call, challenge_id: int):
    """Return a verify_candidate(candidate, remaining) that submits via HTB MCP."""
    def verify(candidate: str, remaining):
        remaining()
        verdict = flag_verdict(htb_mcp.submit_flag(call, challenge_id, candidate))
        remaining()
        return verdict

    return verify


def build_task(call, ctf_id: int, challenge_id: int, work_dir, endpoints: list[dict]) -> tuple[dict, dict, dict]:
    """Fetch the challenge, download any files, and assemble the public task dict."""
    event = htb_mcp.retrieve_ctf(call, ctf_id)
    challenge = find_challenge(event, challenge_id)
    files = download_files(call, challenge_id, work_dir) if challenge.get("filename") else {}
    task = {
        "name": str(challenge.get("name") or f"challenge-{challenge_id}"),
        "category": category_label(challenge),
        "description": str(challenge.get("description") or "").strip() or "No description provided.",
        "files": sorted(files),
        "endpoints": endpoints,
    }
    return task, files, challenge


def start_target(call, challenge_id: int, *, budget: float = 120.0, interval: float = 5.0,
                 sleep=time.sleep) -> list[dict]:
    """Start the challenge container and poll until it reports a reachable endpoint.

    Reads connection info from both the start response and container_status, since
    which one carries host:port is not yet observed. Raises if nothing reachable
    appears within `budget` seconds.
    """
    start = htb_mcp.start_container(call, challenge_id)
    endpoints = connection_endpoints(start)
    if endpoints:
        return endpoints
    deadline = time.monotonic() + budget
    while True:
        try:
            status = htb_mcp.container_status(call, challenge_id)
            endpoints = connection_endpoints(status)
        except HtbMcpError:
            endpoints = []
        if endpoints:
            return endpoints
        if time.monotonic() >= deadline:
            raise RuntimeError(f"Container for challenge {challenge_id} reported no reachable endpoint "
                               f"within {budget:.0f}s")
        sleep(min(interval, max(0.0, deadline - time.monotonic())))


def stop_target(call, challenge_id: int):
    """Best-effort stop of the challenge container; errors are returned, not raised."""
    try:
        htb_mcp.stop_container(call, challenge_id)
        return None
    except HtbMcpError as error:
        return str(error)


@contextmanager
def htb_network(endpoints: list[dict], directory):
    """Own a local bridge for the solver; HTB owns the remote container.

    Mirrors manual_network: the solver reaches the HTB endpoint through the guard
    allowlist, and only the local bridge is this process's to clean up.
    """
    from .manual import manual_network

    with manual_network(endpoints, directory) as target:
        yield target
