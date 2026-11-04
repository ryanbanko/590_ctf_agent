"""Shared fixtures: real SDK spans locally, Docker only when explicitly requested."""

from contextlib import contextmanager
from pathlib import Path
from unittest.mock import Mock

from langfuse import Langfuse
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
import pytest

from ctf_agent.attempt import run_attempt
from ctf_agent.config import DEFAULTS, load_settings
from .fixtures.target import synthetic_target
from .fixtures.tracing import save_spans


def pytest_addoption(parser):
    parser.addoption("--ctf-config", default="configs/initial.toml")
    parser.addoption("--ctf-output", default="runs/pytest-controls")


@pytest.fixture(scope="session")
def telemetry():
    # Native SDK exporter substitution, not a second application tracing backend.
    exporter = InMemorySpanExporter()
    client = Langfuse(public_key="pk-lf-ctf590-local", secret_key="sk-lf-ctf590-local",
                      tracer_provider=TracerProvider(), span_exporter=exporter)
    yield {"client": client, "exporter": exporter}
    client.shutdown()


@pytest.fixture(scope="session")
def settings(pytestconfig):
    return load_settings(Path(pytestconfig.getoption("--ctf-config")))


@pytest.fixture(scope="session")
def output_root(pytestconfig):
    return Path(pytestconfig.getoption("--ctf-output"))


@pytest.fixture
def local_attempt(request, tmp_path, monkeypatch, telemetry):
    # Substitute only Docker operations; keep the real controller, tools, and SDK.
    monkeypatch.setattr("ctf_agent.attempt.docker", lambda *args, **kwargs: "test-image")
    monkeypatch.setattr("ctf_agent.attempt.start_sandbox", lambda *args: None)
    monkeypatch.setattr("ctf_agent.attempt.close_sandbox", lambda sandbox: [])
    monkeypatch.setattr("ctf_agent.attempt.stop_solver", lambda sandbox: True)
    monkeypatch.setattr("ctf_agent.attempt.audit_network", lambda *args: None)
    monkeypatch.setattr("ctf_agent.tools.invoke_worker", Mock(side_effect=AssertionError("Unexpected worker call")))

    @contextmanager
    def open_attempt(respond=None, public_task="public", expected_flag="private-expected-answer", model_usage=None):
        with run_attempt(DEFAULTS | getattr(request, "param", {}), "private-network", "private-gateway", [],
                         expected_flag, tmp_path, langfuse=telemetry["client"],
                         public_task=public_task, respond=respond, model_usage=model_usage) as run:
            yield run

    return open_attempt


@pytest.fixture
def target(settings):
    with synthetic_target(settings) as target:
        yield target


@pytest.fixture
def attempt(request, settings, target, output_root, record_property, telemetry):
    parameters = getattr(getattr(request.node, "callspec", None), "params", {})
    label = parameters.get("destination", request.node.name.split("[")[0].removeprefix("test_"))
    record_property("check_name", label)
    run = None
    try:
        with run_attempt(settings | getattr(request, "param", {}), target["network"], target["gateway"],
                         target["endpoints"], target["expected_flag"], output_root,
                         langfuse=telemetry["client"], label=label) as run:
            record_property("run_id", run["run_id"])
            yield run
    finally:
        if run is not None:
            save_spans(telemetry, run["directory"], run["result"]["trace_id"])
