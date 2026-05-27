#!/usr/bin/env python3
"""Guard the Phase 6 runtime task, poll, and event-loop gap survey."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SURVEY_PATH = Path("Documentation/zigux/phase6-runtime-task-poll-event-loop-gap-survey.md")

EXPECTED_SNIPPETS = [
    "# Phase 6 Runtime Task, Poll, And Event-Loop Gap Survey",
    "Its approved helper anchors are still:",
    "- `lib/base64.c`",
    "- `lib/bsearch.c`",
    "- `lib/checksum.c`",
    "- `lib/hexdump.c`",
    "ACP `eventDelivery.mode = \"poll\"`",
    "- `acp.sessions.events`",
    "- `tasks.events`",
    "- `tasks.get`",
    "- `process.poll`",
    "- `recordTaskReceipt(...)`",
    "- `recordTaskEvent(...)`",
    "- `recordSessionEvent(...)`",
    "- scheduler baseline, disable/enable, reset, policy-switch, saturation, and priority-budget probes",
    "- timer wake, timer quantum, timer cancel, and periodic timer probes",
    "- wake-queue, task-resume, and scheduler-wake timer-clear probes",
    "Do not use it to claim that Zigux Phase 6 has already landed:",
    "- task receipt orchestration",
    "- polling-based runtime update delivery",
    "- process lifecycle polling",
    "- scheduler dispatch, wake, or timer-loop ownership",
    "- `docs/operations.md`",
    "- `src/runtime/tool_runtime.zig`",
    "- `src/runtime/task_receipts.zig`",
]

SELF_TEST_CASE_COUNT = 8


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing survey: {path.as_posix()}") from exc


def validate(root: Path) -> None:
    content = read_text(root / SURVEY_PATH)
    for snippet in EXPECTED_SNIPPETS:
        if snippet not in content:
            raise ValidationError(f"missing expected marker: {snippet}")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold(root: Path) -> None:
    write(root / SURVEY_PATH, "\n".join(EXPECTED_SNIPPETS) + "\n")


def expect_failure(root: Path, mutate) -> None:
    path = root / SURVEY_PATH
    original = read_text(path)
    mutate(path)
    try:
        validate(root)
    except ValidationError:
        return
    finally:
        write(path, original)
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_p6_l24_gap_survey_") as tmpdir:
        root = Path(tmpdir)
        scaffold(root)
        validate(root)

        cases_run = 0
        expect_failure(root, lambda path: path.unlink())
        cases_run += 1
        expect_failure(root, lambda path: write(path, read_text(path).replace(EXPECTED_SNIPPETS[0] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, lambda path: write(path, read_text(path).replace(EXPECTED_SNIPPETS[6] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, lambda path: write(path, read_text(path).replace(EXPECTED_SNIPPETS[10] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, lambda path: write(path, read_text(path).replace(EXPECTED_SNIPPETS[14] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, lambda path: write(path, read_text(path).replace(EXPECTED_SNIPPETS[18] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, lambda path: write(path, read_text(path).replace(EXPECTED_SNIPPETS[22] + "\n", "", 1)))
        cases_run += 1
        expect_failure(root, lambda path: write(path, read_text(path).replace(EXPECTED_SNIPPETS[24] + "\n", "", 1)))
        cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} self-test cases, ran {cases_run}")

    print("PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_GAP_SURVEY_SELF_TEST=pass")
    print(f"PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_GAP_SURVEY_SELF_TEST_CASE_COUNT={cases_run}")


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
        print(f"PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_GAP_SURVEY=fail: {exc}")
        return 1
    print("PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_GAP_SURVEY=pass")
    print(f"PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_GAP_SURVEY_MARKER_COUNT={len(EXPECTED_SNIPPETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
