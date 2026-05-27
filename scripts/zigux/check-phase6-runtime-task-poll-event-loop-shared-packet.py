#!/usr/bin/env python3
"""Guard the shared Phase 6 packet for the runtime-task, poll, and event-loop boundary survey."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SURVEY_PATH = Path("Documentation/zigux/phase6-runtime-task-poll-event-loop-gap-survey.md")
SURVEY_CHECKER_PATH = Path("scripts/zigux/check-phase6-runtime-task-poll-event-loop-gap-survey.py")
SHARED_PACKET_CHECKER_PATH = Path(
    "scripts/zigux/check-phase6-runtime-task-poll-event-loop-shared-packet.py"
)
EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
EXPECTED_REPLAY_ROUTE = (
    "python3 scripts/zigux/check-phase6-runtime-task-poll-event-loop-shared-packet.py"
)
SELF_TEST_CASE_COUNT = 8


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid json: {path.as_posix()}") from exc


def require_list_entry(name: str, value: object, expected: str) -> None:
    if not isinstance(value, list):
        raise ValidationError(f"{name} missing")
    if expected not in value:
        raise ValidationError(f"{name} missing {expected}")


def validate(root: Path) -> None:
    survey = root / SURVEY_PATH
    survey_checker = root / SURVEY_CHECKER_PATH
    shared_packet_checker = root / SHARED_PACKET_CHECKER_PATH
    if not survey.exists():
        raise ValidationError(f"missing required file: {SURVEY_PATH.as_posix()}")
    if not survey_checker.exists():
        raise ValidationError(f"missing required file: {SURVEY_CHECKER_PATH.as_posix()}")
    if not shared_packet_checker.exists():
        raise ValidationError(f"missing required file: {SHARED_PACKET_CHECKER_PATH.as_posix()}")

    evidence_manifest = read_json(root / EVIDENCE_MANIFEST_PATH)
    parity_manifest = read_json(root / PARITY_MANIFEST_PATH)

    require_list_entry(
        "phase6 helper evidence current_direct_readback_companions",
        evidence_manifest.get("current_direct_readback_companions"),
        SURVEY_PATH.as_posix(),
    )
    require_list_entry(
        "phase6 helper evidence current_direct_readback_companions",
        evidence_manifest.get("current_direct_readback_companions"),
        SURVEY_CHECKER_PATH.as_posix(),
    )
    require_list_entry(
        "phase6 helper evidence current_direct_readback_companions",
        evidence_manifest.get("current_direct_readback_companions"),
        SHARED_PACKET_CHECKER_PATH.as_posix(),
    )
    require_list_entry(
        "phase6 helper evidence current_shared_replay_inventory",
        evidence_manifest.get("current_shared_replay_inventory"),
        EXPECTED_REPLAY_ROUTE,
    )
    require_list_entry(
        "phase6 helper parity shared_direct_evidence",
        parity_manifest.get("shared_direct_evidence"),
        SURVEY_PATH.as_posix(),
    )
    require_list_entry(
        "phase6 helper parity shared_direct_evidence",
        parity_manifest.get("shared_direct_evidence"),
        SURVEY_CHECKER_PATH.as_posix(),
    )
    require_list_entry(
        "phase6 helper parity shared_direct_evidence",
        parity_manifest.get("shared_direct_evidence"),
        SHARED_PACKET_CHECKER_PATH.as_posix(),
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / SURVEY_PATH, "# Phase 6 Runtime Task, Poll, And Event-Loop Gap Survey\n")
    write(root / SURVEY_CHECKER_PATH, "#!/usr/bin/env python3\n")
    write(root / SHARED_PACKET_CHECKER_PATH, "#!/usr/bin/env python3\n")
    write(
        root / EVIDENCE_MANIFEST_PATH,
        json.dumps(
            {
                "current_direct_readback_companions": [
                    SURVEY_PATH.as_posix(),
                    SURVEY_CHECKER_PATH.as_posix(),
                    SHARED_PACKET_CHECKER_PATH.as_posix(),
                ],
                "current_shared_replay_inventory": [EXPECTED_REPLAY_ROUTE],
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / PARITY_MANIFEST_PATH,
        json.dumps(
            {
                "shared_direct_evidence": [
                    SURVEY_PATH.as_posix(),
                    SURVEY_CHECKER_PATH.as_posix(),
                    SHARED_PACKET_CHECKER_PATH.as_posix(),
                ]
            },
            indent=2,
        )
        + "\n",
    )


def expect_failure(root: Path, mutate) -> None:
    scaffold_repo(root)
    mutate()
    try:
        validate(root)
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_runtime_task_poll_packet_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0
        expect_failure(root, lambda: (root / SURVEY_PATH).unlink())
        cases_run += 1
        expect_failure(root, lambda: (root / SURVEY_CHECKER_PATH).unlink())
        cases_run += 1
        expect_failure(root, lambda: (root / SHARED_PACKET_CHECKER_PATH).unlink())
        cases_run += 1
        expect_failure(
            root,
            lambda: write(
                root / EVIDENCE_MANIFEST_PATH,
                json.dumps(
                    {
                        "current_direct_readback_companions": [
                            SURVEY_PATH.as_posix(),
                            SHARED_PACKET_CHECKER_PATH.as_posix(),
                        ],
                        "current_shared_replay_inventory": [EXPECTED_REPLAY_ROUTE],
                    },
                    indent=2,
                )
                + "\n",
            ),
        )
        cases_run += 1
        expect_failure(
            root,
            lambda: write(
                root / EVIDENCE_MANIFEST_PATH,
                json.dumps(
                    {
                        "current_direct_readback_companions": [
                            SURVEY_PATH.as_posix(),
                            SURVEY_CHECKER_PATH.as_posix(),
                            SHARED_PACKET_CHECKER_PATH.as_posix(),
                        ],
                        "current_shared_replay_inventory": [],
                    },
                    indent=2,
                )
                + "\n",
            ),
        )
        cases_run += 1
        expect_failure(
            root,
            lambda: write(
                root / PARITY_MANIFEST_PATH,
                json.dumps(
                    {
                        "shared_direct_evidence": [
                            SURVEY_PATH.as_posix(),
                            SURVEY_CHECKER_PATH.as_posix(),
                        ]
                    },
                    indent=2,
                )
                + "\n",
            ),
        )
        cases_run += 1
        expect_failure(root, lambda: write(root / EVIDENCE_MANIFEST_PATH, "{not json}\n"))
        cases_run += 1
        expect_failure(root, lambda: write(root / PARITY_MANIFEST_PATH, "{not json}\n"))
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} self-test cases, ran {cases_run}")

    print("PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET_SELF_TEST=pass")
    print(
        f"PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET_SELF_TEST_CASE_COUNT={cases_run}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        validate(args.root)
    except ValidationError as exc:
        print(f"PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET=fail: {exc}")
        return 1

    print("PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
