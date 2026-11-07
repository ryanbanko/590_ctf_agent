"""Trusted namespace firewall and NFLOG collector; no network listening socket."""

import ipaddress
import json
import os
import subprocess
import sys


def emit(event, **fields):
    print(json.dumps({"event": event, **fields}), flush=True)


def main():
    policy = json.loads(os.environ["GUARD_POLICY"])
    allowed = []
    for endpoint in policy["endpoints"]:
        address = str(ipaddress.IPv4Address(endpoint["address"]))
        port = endpoint["port"]
        protocol = endpoint["protocol"]
        if type(port) is not int or not 1 <= port <= 65535 or protocol not in {"tcp", "udp"}:
            raise ValueError("Invalid trusted endpoint policy")
        allowed.append(f"ip daddr {address} {protocol} dport {port} accept")
    rules = """
table inet ctf {
  counter denied { }
  chain deny {
    counter name denied log group 10 snaplen 96 queue-threshold 1 drop
  }
  chain output {
    type filter hook output priority -300; policy drop;
    ip daddr 127.0.0.11 udp dport 53 accept
    ip daddr 127.0.0.11 tcp dport 53 accept
    udp dport 53 jump deny
    tcp dport 53 jump deny
    oifname "lo" accept
    ct state established,related accept
    ALLOWED
    ip daddr { 0.0.0.0/8, 10.0.0.0/8, 100.64.0.0/10, 127.0.0.0/8,
               169.254.0.0/16, 172.16.0.0/12, 192.0.0.0/24, 192.0.2.0/24,
               192.168.0.0/16, 198.18.0.0/15, 198.51.100.0/24,
               203.0.113.0/24, 224.0.0.0/4, 240.0.0.0/4 } jump deny
    meta nfproto ipv4 tcp dport 443 accept
    jump deny
  }
  chain input {
    type filter hook input priority -300; policy drop;
    iifname "lo" accept
    ct state established,related accept
  }
  chain forward {
    type filter hook forward priority -300; policy drop;
  }
}
""".replace("ALLOWED", "\n    ".join(allowed))
    subprocess.run(["nft", "-f", "-"], input=rules, text=True, check=True)
    collector = subprocess.Popen(
        ["tcpdump", "-Z", "tcpdump", "--immediate-mode", "-l", "-nn", "-tt", "-i", "nflog:10"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
    )
    ready = False
    try:
        for line in collector.stdout:
            line = line.strip()
            if "listening on nflog:10" in line:
                ready = True
                emit("guard_ready")
            elif ready:
                emit("network_denied", packet=line[:2000])
            else:
                emit("guard_diagnostic", message=line[:2000])
        raise RuntimeError(f"NFLOG collector stopped: {collector.wait()}")
    finally:
        collector.terminate()
        collector.wait(timeout=2)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        emit("guard_failed", message=str(error))
        sys.exit(1)
