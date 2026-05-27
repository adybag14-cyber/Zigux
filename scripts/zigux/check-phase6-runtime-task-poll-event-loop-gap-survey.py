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
    'ACP `eventDelivery.mode = "poll"`',
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

SELF_TEST_MUTATIONS = [
    EXPECTED_SNIPPETS[0],
    EXPECTED_SNIPPETS[1],
    EXPECTED_SNIPPETS[6],
    EXPECTED_SNIPPETS[10],
    EXPECTED_SNIPPETS[11],
    EXPECTED_SNIPPETS[14],
    EXPECTED_SNIPPETS[15],
    EXPECTED_SNIPPETS[16],
    EXPECTED_SNIPPETS[17],
    EXPECTED_SNIPPETS[18],
    EXPECTED_SNIPPETS[22],
    EXPECTED_SNIPPETS[24],
]
SELF_TEST_CASE_COUNT = len(SELF_TEST_MUTATIONS) + 1


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


def survey_template() -> str:
    return """# Phase 6 Runtime Task, Poll, And Event-Loop Gap Survey

This note records the bounded gap between the current Phase 6 Zigux helper packet and the broader runtime task, polling, and event-loop substrate visible in the attached ZAR runtime references.

## Why this survey exists

Phase 6 remains intentionally narrow in the product roadmap. Its approved helper anchors are still:

- `lib/base64.c`
- `lib/bsearch.c`
- `lib/checksum.c`
- `lib/hexdump.c`

The attached runtime archive already shows richer task, polling, and scheduler-oriented control surfaces. Writing that down keeps the current Phase 6 packet truthful: it makes those runtime substrates reviewable as comparison material without implying that Zigux Phase 6 has already widened into runtime pilot or event-loop delivery work.

## Runtime task and polling surfaces visible in the attached archive

The attached `docs/operations.md`, `src/runtime/tool_runtime.zig`, and `src/runtime/task_receipts.zig` show four relevant runtime-substrate families:

### 1. Polling-based session and task update delivery

The runtime contract describes polling-based update delivery for both session events and task receipts, including:

- ACP `eventDelivery.mode = "poll"`
- `acp.sessions.events`
- `tasks.events`
- `tasks.get`

That is a live runtime update-delivery substrate, not a Phase 6 leaf-helper replay.

### 2. Process polling and long-running runtime work

The runtime service also exposes a dedicated process-poll surface, including:

- `process.poll`
- process state readback
- running and finished timestamps
- stdout and stderr byte counts
- timeout and signal status

That is runtime task orchestration pressure, not helper-only Phase 6 evidence.

### 3. Persisted task receipts and task-event recording

The task-receipt layer records durable task metadata and task-event trails, including:

- `recordTaskReceipt(...)`
- `recordTaskEvent(...)`
- `recordSessionEvent(...)`
- persisted task summaries, step counts, and status updates

That is runtime task-state bookkeeping, not a bounded helper portability slice.

### 4. Scheduler and wake/timer probe pressure

The runtime operations snapshot also documents a broad scheduler and timer validation surface, including:

- scheduler baseline, disable/enable, reset, policy-switch, saturation, and priority-budget probes
- timer wake, timer quantum, timer cancel, and periodic timer probes
- wake-queue, task-resume, and scheduler-wake timer-clear probes

That is event-loop and dispatch substrate pressure, not truthful evidence that Zigux Phase 6 already owns a scheduler or polling runtime.

## What this means for Zigux Phase 6

The roadmap-backed Phase 6 packet should stay bounded to the four helper anchors and their direct helper, parity, fixture, checker, and perf evidence.

This survey therefore treats the runtime task, polling, and event-loop families as:

- relevant future pressure from the attached runtime archive
- useful comparison material for later runtime-facing phases
- out of scope for current Phase 6 progress claims

A fresh attached-reference reread on 2026-05-27 did not change that boundary. The truthful Phase 6 product scope is still the four helper anchors above, while the runtime task, polling, and event-loop substrate remains comparison material rather than shipped helper evidence.

## Honest next-step boundary

Use this note only as a boundary reminder.

Do not use it to claim that Zigux Phase 6 has already landed:

- task receipt orchestration
- polling-based runtime update delivery
- process lifecycle polling
- scheduler dispatch, wake, or timer-loop ownership

Those surfaces belong to later product phases if and when the roadmap deliberately widens into tooling, runtime pilots, or deeper runtime substrate work.

## Source grounding

This survey is grounded in:

- `agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md`
- `agent_files/ZAR-Zig-Agent-Runtime-main (11).zip`
  - `docs/operations.md`
  - `src/runtime/tool_runtime.zig`
  - `src/runtime/task_receipts.zig`

Reopen this note only when the shared Phase 6 packet needs to restate the boundary between helper-only progress and broader runtime task, polling, or event-loop substrate work.
"""


def scaffold(root: Path) -> None:
    write(root / SURVEY_PATH, survey_template())


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


def drop_first(path: Path, snippet: str) -> None:
    original = read_text(path)
    if snippet + "\n" in original:
        write(path, original.replace(snippet + "\n", "", 1))
    else:
        write(path, original.replace(snippet, "", 1))


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_p6_l20_gap_survey_") as tmpdir:
        root = Path(tmpdir)
        scaffold(root)
        validate(root)

        cases_run = 0
        expect_failure(root, lambda path: path.unlink())
        cases_run += 1

        for snippet in SELF_TEST_MUTATIONS:
            expect_failure(root, lambda path, snippet=snippet: drop_first(path, snippet))
            cases_run += 1

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} self-test cases, ran {cases_run}")

    print("PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_GAP_SURVEY_SELF_TEST=pass")
    print(f"PHASE6_RUNTIME_TASK_POLL_EVENT_LOOP_GAP_SURVEY_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-sample-root", type=Path)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.write_sample_root is not None:
        scaffold(args.write_sample_root)
        print(f"Wrote sample root to {args.write_sample_root}")
        return 0
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
