#!/usr/bin/env python3
"""Guard the Phase 6 runtime task, polling, and event-loop gap survey."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SURVEY_PATH = Path("Documentation/zigux/phase6-runtime-task-poll-event-loop-gap-survey.md")

REQUIRED_SNIPPETS = [
    "# Phase 6 Runtime Task, Polling, and Event-Loop Gap Survey",
    "- roadmap anchors: `lib/base64.c`, `lib/bsearch.c`, `lib/checksum.c`, and `lib/hexdump.c`",
    "- scheduler substrate markers: `scheduler round-robin`, `scheduler priority budget`, `scheduler timeslice`, `scheduler disable-enable`, `scheduler reset`, `scheduler saturation`, and `scheduler wake-timer-clear`",
    "- task lifecycle markers: `task lifecycle`, `active-task terminate`, `task resume interrupt-timeout`, `task resume timer-clear`, and `timer cancel task`",
    "- polling and loop markers: `command-loop`, `telegram reply loop`, `pollDnsPacket`, `pollDnsPacketStrictInto`, `pollTcpPacketStrictInto`, and bounded receive timeouts",
    "- tty event markers: `/runtime/tty/<name>/`, `events.log`, `transcript.log`, and `event_count`",
    "- review posture: keep this survey out of the bounded Phase 6 leaf-helper tranche and defer scheduler, task, polling, and event-loop substrate adoption to later roadmap-backed tooling or runtime lanes",
    "- evidence sources: `agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md`, `agent_files/ZAR-Zig-Agent-Runtime-main (11).zip`, `docs/operations.md`, and `src/baremetal/tty_runtime.zig`",
]

SELF_TEST_CASE_COUNT = len(REQUIRED_SNIPPETS)


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(
                f"missing expected Phase 6 runtime-gap marker in {path.as_posix()}: {snippet}"
            )


def validate(root: Path) -> None:
    require_snippets(root / SURVEY_PATH, REQUIRED_SNIPPETS)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def survey_template() -> str:
    return """# Phase 6 Runtime Task, Polling, and Event-Loop Gap Survey

This note records the current scheduler, task, polling, and event-loop substrate gap between the attached ZAR runtime archive and the bounded Phase 6 Zigux helper tranche.

## Why this note exists

Phase 6 is intentionally narrow in the roadmap: it allows new helper delivery under `lib/` without widening into runtime-core ownership. The attached ZAR runtime archive already exposes broader scheduler, task, polling, and event-loop surfaces, so this survey keeps that contrast explicit and reviewable.

## Roadmap-backed Phase 6 scope

- roadmap anchors: `lib/base64.c`, `lib/bsearch.c`, `lib/checksum.c`, and `lib/hexdump.c`
- required Phase 6 posture: leaf helper portability, clear API parity, and perf gates for math-sensitive helpers without runtime-core expansion

## Attached runtime surfaces already beyond the Phase 6 helper tranche

- scheduler substrate markers: `scheduler round-robin`, `scheduler priority budget`, `scheduler timeslice`, `scheduler disable-enable`, `scheduler reset`, `scheduler saturation`, and `scheduler wake-timer-clear`
- task lifecycle markers: `task lifecycle`, `active-task terminate`, `task resume interrupt-timeout`, `task resume timer-clear`, and `timer cancel task`
- polling and loop markers: `command-loop`, `telegram reply loop`, `pollDnsPacket`, `pollDnsPacketStrictInto`, `pollTcpPacketStrictInto`, and bounded receive timeouts
- tty event markers: `/runtime/tty/<name>/`, `events.log`, `transcript.log`, and `event_count`

## Current Phase 6 review posture

- review posture: keep this survey out of the bounded Phase 6 leaf-helper tranche and defer scheduler, task, polling, and event-loop substrate adoption to later roadmap-backed tooling or runtime lanes
- this note is a truthfulness survey only; it does not authorize Phase 6 to absorb scheduler policy, task state machines, timer queues, receive loops, or session event plumbing

## Evidence used

- evidence sources: `agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md`, `agent_files/ZAR-Zig-Agent-Runtime-main (11).zip`, `docs/operations.md`, and `src/baremetal/tty_runtime.zig`
"""


def scaffold(root: Path) -> None:
    write(root / SURVEY_PATH, survey_template())


def expect_failure(root: Path, expected: str) -> None:
    try:
        validate(root)
    except ValidationError as exc:
        if expected not in str(exc):
            raise AssertionError(f"expected {expected!r} in {str(exc)!r}") from exc
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_runtime_gap_") as tmpdir:
        root = Path(tmpdir)
        scaffold(root)
        validate(root)
        cases_run = 0

        path = root / SURVEY_PATH
        original = read_text(path)
        for snippet in REQUIRED_SNIPPETS:
            if snippet + "\n" in original:
                mutated = original.replace(snippet + "\n", "", 1)
            else:
                mutated = original.replace(snippet, "", 1)
            write(path, mutated)
            expect_failure(root, snippet)
            cases_run += 1
            write(path, original)

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
