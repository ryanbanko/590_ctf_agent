"""Inspect/export the real SDK's native spans; used only for local verification."""

import json
from pathlib import Path


def read_spans(telemetry: dict, trace_id: str):
    telemetry["client"].flush()
    return [span for span in telemetry["exporter"].get_finished_spans()
            if format(span.context.trace_id, "032x") == trace_id]


def save_spans(telemetry: dict, directory: Path, trace_id: str):
    spans = read_spans(telemetry, trace_id)
    (directory / "otel-spans.json").write_text(
        "[\n" + ",\n".join(span.to_json() for span in spans) + "\n]\n", encoding="utf-8")
    return spans


def attribute(span, name: str):
    value = span.attributes.get("langfuse.observation." + name)
    return json.loads(value) if value is not None else None
