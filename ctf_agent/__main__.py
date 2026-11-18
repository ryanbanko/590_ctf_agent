"""One challenge launcher and explicit setup/verification commands."""

import argparse
from pathlib import Path
import subprocess

from .config import CONFIG_PATH, load_settings


def main():
    parser = argparse.ArgumentParser(description="Isolated CTFTiny agent and verification commands")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    commands = parser.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("setup-manual", help="Save a public HTB task from prompts; no model calls or Docker")
    setup.add_argument("--output", type=Path, default=Path("runs/htb/tasks"))
    manual = commands.add_parser("run-manual",
        help="Enter a challenge (unless --task) and run it with human-relayed flag verdicts (LIVE)")
    manual.add_argument("--task", type=Path,
        help="A saved task.json; omit to enter the challenge interactively and run it in one step")
    manual.add_argument("--experiment", type=Path, default=Path("configs/htb-manual.toml"))
    manual.add_argument("--output", type=Path, default=Path("runs/htb/attempts"))
    manual.add_argument("--task-output", type=Path, default=Path("runs/htb/tasks"),
        help="Where an interactively entered task is saved before running")
    listing = commands.add_parser("htb-challenges", help="List an HTB event's challenges over MCP (read-only)")
    listing.add_argument("--ctf-id", type=int, default=3755)
    htb = commands.add_parser("run-htb", help="Run one HTB challenge over MCP end to end (LIVE)")
    htb.add_argument("--ctf-id", type=int, default=3755)
    htb.add_argument("--challenge", type=int, required=True, help="HTB challenge id (integer)")
    htb.add_argument("--experiment", type=Path, default=Path("configs/htb-manual.toml"))
    htb.add_argument("--output", type=Path, default=Path("runs/htb/attempts"))
    event = commands.add_parser("run-htb-event", help="Attempt an HTB event's challenges, budget-paced (LIVE)")
    event.add_argument("--ctf-id", type=int, default=3755)
    event.add_argument("--experiment", type=Path, default=Path("configs/htb-manual.toml"))
    event.add_argument("--output", type=Path, default=Path("runs/htb/events"))
    event.add_argument("--budget", type=float, help="Global cost budget in USD; stops the event when reached")
    event.add_argument("--limit", type=int, help="Attempt at most this many challenges (for testing)")
    event.add_argument("--workers", type=int, default=1,
        help="Concurrent challenges (default 1 = sequential; capped). Higher finishes faster for placement.")
    event.add_argument("--manual-verify", action="store_true",
        help="MCP fetches/spawns challenges, but YOU relay each flag (hedge if MCP submit misbehaves)")
    commands.add_parser("build-images", help="Build the solver, guard, and synthetic target")
    check = commands.add_parser("self-check", help="Run fixed synthetic controls checks; no model calls")
    check.add_argument("--output", type=Path, default=Path("runs"))
    hosted = commands.add_parser("langfuse-check", help="Send/retrieve one synthetic Langfuse trace; no model calls")
    hosted.add_argument("--output", type=Path, default=Path("runs"))
    model = commands.add_parser("model-check", help="One LIVE synthetic model attempt; requires spending approval")
    model.add_argument("--output", type=Path, default=Path("runs"))
    prepare = commands.add_parser("prepare-challenge", help="Check one challenge's files/services; no model calls or solving")
    prepare.add_argument("--experiment", type=Path, default=CONFIG_PATH)
    prepare.add_argument("--challenge", default="pwn-baby-boi")
    prepare.add_argument("--dataset", type=Path, default=Path("datasets/CTFTiny/ctftiny.json"))
    prepare.add_argument("--manifest", type=Path, default=Path("configs/ctftiny.json"))
    prepare.add_argument("--output", type=Path, default=Path("runs"))
    run = commands.add_parser("run-challenge", help="Run one LIVE challenge attempt with bounded model/tool calls")
    run.add_argument("--experiment", type=Path, default=CONFIG_PATH)
    run.add_argument("--dataset", type=Path, default=Path("datasets/CTFTiny/ctftiny.json"))
    run.add_argument("--manifest", type=Path, default=Path("configs/ctftiny.json"))
    run.add_argument("--challenge", required=True)
    run.add_argument("--output", type=Path, default=Path("runs/challenges"))
    batch = commands.add_parser("run-batch", help="Run sequential LIVE attempts using the single-challenge launcher")
    batch.add_argument("--experiment", type=Path, default=CONFIG_PATH)
    batch.add_argument("--dataset", type=Path, default=Path("datasets/CTFTiny/ctftiny.json"))
    batch.add_argument("--manifest", type=Path, default=Path("configs/ctftiny.json"))
    batch.add_argument("--challenges", nargs="+", required=True)
    batch.add_argument("--trials", type=int, default=1)
    batch.add_argument("--output", type=Path, default=Path("runs/batches"))
    args = parser.parse_args()
    if args.command in {"setup-manual", "run-manual"}:
        try:
            if args.command == "setup-manual":
                from .manual import setup_manual_task

                setup_manual_task(args.output)
            else:
                from .launch import launch_manual

                task = args.task
                if task is None:
                    from .manual import setup_manual_task

                    task = setup_manual_task(args.task_output)
                    print("\nStarting the agent on this task now (Ctrl-C to abort)...\n")
                launch_manual(args.experiment, task, args.output)
        except (ValueError, OSError) as error:
            parser.error(str(error))
        except (KeyboardInterrupt, EOFError):
            raise SystemExit("Manual setup/run cancelled") from None
    elif args.command == "htb-challenges":
        from .launch import list_htb_challenges

        try:
            list_htb_challenges(args.ctf_id)
        except (ValueError, RuntimeError) as error:
            parser.error(str(error))
    elif args.command == "run-htb":
        from .launch import launch_htb

        try:
            launch_htb(args.experiment, args.ctf_id, args.challenge, args.output)
        except (ValueError, OSError) as error:
            parser.error(str(error))
        except KeyboardInterrupt:
            raise SystemExit("HTB run cancelled") from None
    elif args.command == "run-htb-event":
        from .compete import run_event, DEFAULT_POLICY

        policy = dict(DEFAULT_POLICY, global_budget_usd=args.budget) if args.budget is not None else None
        try:
            run_event(args.experiment, args.ctf_id, args.output, policy=policy, limit=args.limit,
                      workers=args.workers, manual_verify=args.manual_verify)
        except (ValueError, OSError) as error:
            parser.error(str(error))
        except KeyboardInterrupt:
            raise SystemExit("Event run cancelled") from None
    elif args.command == "build-images":
        settings = load_settings(args.config)
        for role, key in [("solver", "solver_image"), ("guard", "guard_image"), ("fixture", "target_image")]:
            platform = ["--platform", "linux/amd64"] if role == "solver" else []
            subprocess.run(["docker", "build", *platform, "-f", f"docker/{role}.Dockerfile", "-t", settings[key], "."], check=True)
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

        check_readiness(args.experiment, args.dataset, args.manifest, args.output, args.challenge)
    elif args.command == "run-batch":
        from .launch import launch_batch

        launch_batch(args.experiment, args.dataset, args.manifest, args.challenges, args.trials, args.output)
    else:
        from .launch import launch_challenge

        launch_challenge(args.experiment, args.dataset, args.manifest, args.challenge, args.output)


if __name__ == "__main__":
    main()
