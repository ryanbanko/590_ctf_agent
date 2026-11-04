"""Launch pytest's Docker checks and preserve their reports and run provenance."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET

from ctf_agent.config import load_settings
from ctf_agent.docker import docker


def collect_provenance(settings: dict) -> dict:
    images = {}
    for role in ("solver", "guard", "target"):
        images[role] = json.loads(docker("image", "inspect", "--format",
            '{"id":{{json .Id}},"architecture":{{json .Architecture}}}', settings[f"{role}_image"]))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    hashes = {}
    for pattern in ["ctf_agent/*.py", "docker/*.py", "docker/*.Dockerfile", "tests/**/*.py",
                    "configs/*.toml", "pyproject.toml", "uv.lock"]:
        for path in sorted(Path(".").glob(pattern)):
            hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"images": images, "commit": commit.stdout.strip() if commit.returncode == 0 else None,
            "source_sha256": hashes, "docker": docker("version", "--format", "{{.Server.Version}}"),
            "config": settings}


def self_check(config_path: Path, output_root: Path) -> Path:
    suite_dir = output_root / ("self-check-" + uuid.uuid4().hex[:12])
    suite_dir.mkdir(parents=True, mode=0o700)
    suite = {"mode": "synthetic-controls", "time_utc": datetime.now(timezone.utc).isoformat(),
             "checks": [], "passed": False, "model_calls": 0, "cost_usd": 0.0}
    started = time.monotonic()
    try:
        suite["provenance"] = collect_provenance(load_settings(config_path))
        report_path = suite_dir / "pytest.xml"
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests", "-m", "docker", "-q", "-x",
            "--disable-plugin-autoload", "--ctf-config", str(config_path.resolve()),
            "--ctf-output", str(suite_dir.resolve()), "--junitxml", str(report_path.resolve()),
        ], check=False)
        if report_path.exists():
            for case in ET.parse(report_path).iter("testcase"):
                properties = {p.attrib["name"]: p.attrib["value"] for p in case.findall("properties/property")}
                suite["checks"].append({
                    "name": properties.get("check_name", case.attrib["name"]),
                    "run_id": properties.get("run_id"),
                    "passed": not any(case.find(tag) is not None for tag in ("error", "failure", "skipped")),
                })
        containers = docker("ps", "--all", "--filter", "label=ctf590.managed=true", "--format", "{{.Names}}")
        networks = docker("network", "ls", "--filter", "label=ctf590.managed=true", "--format", "{{.Name}}")
        suite["cleanup_verified"] = not containers and not networks
        suite["pytest_exit_code"] = result.returncode
        suite["passed"] = (result.returncode == 0 and bool(suite["checks"])
                           and all(check["passed"] for check in suite["checks"]) and suite["cleanup_verified"])
    except BaseException as error:
        suite["error"] = {"type": type(error).__name__, "message": str(error)[:2000]}
        raise
    finally:
        suite["total_seconds"] = round(time.monotonic() - started, 6)
        (suite_dir / "suite.json").write_text(json.dumps(suite, indent=2) + "\n")
        print(f"Evidence: {suite_dir}", flush=True)
    if not suite["passed"]:
        raise RuntimeError(f"Controls checks failed; see {suite_dir}")
    return suite_dir
