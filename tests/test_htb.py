"""HTB task-building helpers: category, lookup, download URL, endpoints, verdicts.

All offline. The live-unknown shapes (download_url, connection_endpoints,
flag_verdict) are exercised against the shapes HTB is expected to return; these
are the functions to re-check against a real container when the event opens.
"""

import pytest

from ctf_agent import htb
from ctf_agent.htb_mcp import HtbMcpError


# --- challenge selection and labelling -------------------------------------

def test_category_label_prefers_explicit_name_then_map_then_id():
    assert htb.category_label({"category": "Web"}) == "Web"
    assert htb.category_label({"challenge_category_id": 4}) == "Crypto"
    assert htb.category_label({"challenge_category_id": 999}) == "category 999"
    assert htb.category_label({}) == "category None"


def test_find_challenge():
    event = {"challenges": [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]}
    assert htb.find_challenge(event, 2)["name"] == "b"
    with pytest.raises(ValueError, match="available: 1, 2"):
        htb.find_challenge(event, 9)


# --- download link ----------------------------------------------------------

def test_download_url_from_string_and_dict():
    assert htb.download_url("https://s3/x.zip") == "https://s3/x.zip"
    assert htb.download_url({"url": "https://s3/y.zip"}) == "https://s3/y.zip"
    assert htb.download_url({"download_url": "http://s3/z.zip"}) == "http://s3/z.zip"


def test_download_url_missing_raises():
    with pytest.raises(ValueError, match="No download URL"):
        htb.download_url({"status": "ok"})


# --- connection endpoints (CONFIRM AT NOON) ---------------------------------

def no_resolve(host):
    raise AssertionError("should not resolve an IPv4 literal")


def test_connection_endpoints_ip_and_port():
    data = {"ip": "83.136.254.1", "port": 31234}
    assert htb.connection_endpoints(data, resolve=no_resolve) == [
        {"address": "83.136.254.1", "protocol": "tcp", "port": 31234}]


def test_connection_endpoints_hostname_resolved():
    data = {"hostname": "docker.hackthebox.eu", "port": 40000}
    endpoints = htb.connection_endpoints(data, resolve=lambda host: "94.237.0.9")
    assert endpoints == [{"address": "94.237.0.9", "protocol": "tcp", "port": 40000}]


def test_connection_endpoints_host_port_string():
    data = {"connection": "94.237.1.2:55555"}
    assert htb.connection_endpoints(data, resolve=no_resolve) == [
        {"address": "94.237.1.2", "protocol": "tcp", "port": 55555}]


def test_connection_endpoints_docker_ports_list():
    data = {"ip": "10.10.10.10", "docker_ports": [1337, 1338]}
    ports = [e["port"] for e in htb.connection_endpoints(data, resolve=no_resolve)]
    assert ports == [1337, 1338]


def test_connection_endpoints_empty_until_ready():
    assert htb.connection_endpoints({}, resolve=no_resolve) == []
    assert htb.connection_endpoints({"ip": "1.2.3.4"}, resolve=no_resolve) == []  # no port yet
    assert htb.connection_endpoints(None, resolve=no_resolve) == []


def test_resolve_ipv4_passthrough_and_lookup():
    assert htb.resolve_ipv4("1.2.3.4", resolve=no_resolve) == "1.2.3.4"
    assert htb.resolve_ipv4("host.example", resolve=lambda h: "5.6.7.8") == "5.6.7.8"


# --- flag verdict mapping (CONFIRM AT NOON) ---------------------------------

def test_flag_verdict_wrong_flag_is_rejection_not_error():
    # The observed HTB shape: a wrong flag is reported as an error 400.
    assert htb.flag_verdict({"error": "Wrong flag, sorry!", "status_code": 400}) == {"correct": False}
    assert htb.flag_verdict({"error": "Incorrect flag", "status_code": 400}) == {"correct": False}


def test_flag_verdict_accepted_is_solve():
    # A correct flag comes back without an error field.
    assert htb.flag_verdict({"message": "Correct! You solved it", "status_code": 200}) == {"correct": True}
    assert htb.flag_verdict({"isCorrect": True}) == {"correct": True}
    assert htb.flag_verdict({"correct": False}) == {"correct": False}  # explicit boolean honoured


def test_flag_verdict_genuine_error_is_raised():
    # Auth / server / rate-limit failures must stop the attempt, not read as wrong.
    with pytest.raises(HtbMcpError):
        htb.flag_verdict({"error": "CTF is not running", "status_code": 403})
    with pytest.raises(HtbMcpError):
        htb.flag_verdict({"error": "Server Error", "status_code": 500})
    with pytest.raises(HtbMcpError):
        htb.flag_verdict("not a dict")


# --- verify callback relays through MCP submit_flag -------------------------

def test_verify_with_mcp_submits_and_maps():
    calls = []

    def fake_call(name, arguments=None, *, raise_on_error=True):
        calls.append((name, arguments, raise_on_error))
        assert name == "submit_flag"
        return {"message": "Correct!", "status_code": 200}

    verify = htb.verify_with_mcp(fake_call, 79390)
    assert verify("HTB{z}", lambda: 100.0) == {"correct": True}
    # submit_flag must ask the client NOT to raise, so a wrong flag is interpretable.
    assert calls == [("submit_flag", {"challenge_id": 79390, "flag": "HTB{z}"}, False)]


def test_verify_with_mcp_wrong_flag_returns_rejection():
    def fake_call(name, arguments=None, *, raise_on_error=True):
        return {"error": "Wrong flag, sorry!", "status_code": 400}

    verify = htb.verify_with_mcp(fake_call, 79390)
    assert verify("HTB{nope}", lambda: 100.0) == {"correct": False}


def test_verify_with_mcp_propagates_genuine_error():
    def fake_call(name, arguments=None, *, raise_on_error=True):
        return {"error": "CTF is not running", "status_code": 403}

    verify = htb.verify_with_mcp(fake_call, 1)
    with pytest.raises(HtbMcpError):
        verify("HTB{z}", lambda: 100.0)


# --- start_target polling ---------------------------------------------------

def test_start_target_polls_until_endpoint():
    responses = iter([
        {},                                    # start_container: no endpoint yet
        {"message": "starting"},               # status: not ready
        {"ip": "83.136.9.9", "port": 32100},   # status: ready
    ])
    waits = []

    def fake_call(name, arguments=None):
        return next(responses)

    endpoints = htb.start_target(fake_call, 79390, interval=1.0, sleep=waits.append)
    assert endpoints == [{"address": "83.136.9.9", "protocol": "tcp", "port": 32100}]
    assert waits  # it slept at least once while waiting


def test_start_target_times_out():
    def fake_call(name, arguments=None):
        return {}  # never reports an endpoint

    with pytest.raises(RuntimeError, match="no reachable endpoint"):
        htb.start_target(fake_call, 1, budget=0.0, sleep=lambda s: None)


def test_build_task_without_files():
    def fake_call(name, arguments=None):
        assert name == "retrieve_ctf"
        return {"challenges": [{"id": 79390, "name": "DNS Dossier",
                                "challenge_category_id": 2, "difficulty": "easy",
                                "description": "A tool.", "filename": ""}]}

    endpoints = [{"address": "1.2.3.4", "protocol": "tcp", "port": 80}]
    task, files, challenge = htb.build_task(fake_call, 3755, 79390, None, endpoints)
    assert files == {}
    assert task == {"name": "DNS Dossier", "category": "Web", "description": "A tool.",
                    "files": [], "endpoints": endpoints}
