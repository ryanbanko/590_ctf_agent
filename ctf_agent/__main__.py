"""One challenge launcher and explicit setup/verification commands."""

import argparse
from pathlib import Path
import subprocess

from .config import load_settings


def main():
    parser = argparse.ArgumentParser(description="Isolated CTFTiny agent and verification commands")
    parser.add_argument("--config", type=Path, default=Path("configs/initial.toml"))
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("build-images", help="Build the solver, guard, and synthetic target")
    check = commands.add_parser("self-check", help="Run fixed synthetic controls checks; no model calls")
    check.add_argument("--output", type=Path, default=Path("runs"))
    hosted = commands.add_parser("langfuse-check", help="Send/retrieve one synthetic Langfuse trace; no model calls")
    hosted.add_argument("--output", type=Path, default=Path("runs"))
    model = commands.add_parser("model-check", help="One LIVE synthetic model attempt; requires spending approval")
    model.add_argument("--output", type=Path, default=Path("runs"))
    prepare = commands.add_parser("prepare-challenge", help="Check one challenge's files/services; no model calls or solving")
    prepare.add_argument("--challenge", default="pwn-baby-boi")
    prepare.add_argument("--dataset", type=Path, default=Path("datasets/CTFTiny/ctftiny.json"))
    prepare.add_argument("--manifest", type=Path, default=Path("configs/ctftiny.json"))
    prepare.add_argument("--output", type=Path, default=Path("runs"))
    run = commands.add_parser("run-challenge", help="Run one LIVE challenge attempt with bounded model/tool calls")
    run.add_argument("--experiment", type=Path, default=Path("configs/development.toml"))
    run.add_argument("--dataset", type=Path, default=Path("datasets/CTFTiny/ctftiny.json"))
    run.add_argument("--manifest", type=Path, default=Path("configs/ctftiny.json"))
    run.add_argument("--challenge", required=True)
    run.add_argument("--output", type=Path, default=Path("runs/challenges"))
    args = parser.parse_args()
    if args.command == "build-images":
        settings = load_settings(args.config)
        for role, key in [("solver", "solver_image"), ("guard", "guard_image"), ("fixture", "target_image")]:
            subprocess.run(["docker", "build", "-f", f"docker/{role}.Dockerfile", "-t", settings[key], "."], check=True)
    elif args.command == "self-check":
        # Keep the convenience command; test implementation lives under tests/.
        from tests.test_controls import self_check

        self_check(args.config, args.output)
    elif args.command == "langfuse-check":
        from tests.check_langfuse import check_langfuse

        check_langfuse(args.config, args.output)
    elif args.command == "model-check":
        from tests.check_model import check_model

        check_model(args.config, args.output)
    elif args.command == "prepare-challenge":
        from tests.check_readiness import check_readiness

        check_readiness(args.config, args.dataset, args.manifest, args.output, args.challenge)
    else:
        from .launch import launch_challenge

        launch_challenge(args.experiment, args.dataset, args.manifest, args.challenge, args.output)


if __name__ == "__main__":
    main()
