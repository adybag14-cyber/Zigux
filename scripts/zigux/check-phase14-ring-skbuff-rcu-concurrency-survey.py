#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

NOTE_PATH = "Documentation/zigux/phase14-ring-skbuff-rcu-concurrency-survey.md"

REQUIRED_MARKERS = [
    "`PHASE14_LANE_KEY=P14-L12`",
    "`PHASE14_STATUS_BUCKET=study_only_cross_anchor`",
    "`PHASE14_SCOPE=ring-buffer-skbuff-rcu-concurrency`",
    "`PHASE14_BLOCKED_GAP=phase14-cross-anchor-concurrency-bridge-blocker`",
    "`Documentation/zigux/phase14-ring-buffer-survey.md`",
    "`Documentation/zigux/phase14-skbuff-bridge-survey.md`",
    "`Documentation/zigux/phase14-rcu-tree-survey.md`",
    "`Documentation/zigux/phase14-core-boundary-traceability.md`",
    "`Documentation/zigux/freeze-map.md`",
    "Publication and ordering ownership still stays in C.",
    "Consumer lifetime and teardown ownership still stays in C.",
    "Asynchronous wake, offload, and escalation ownership still stays in C.",
    "`ring_buffer_lock_reserve()`",
    "`validate_xmit_skb_list()`",
    "`rcu_start_this_gp`",
    "`ring_buffer_read_page()`",
    "`sock_wfree`",
    "`rcu_barrier`",
    "`ring_buffer_wait()`",
    "`wake_nocb_gp_defer`",
    "do not treat `kernel/trace/ring_buffer.zig` as an active bridge target",
    "do not treat the returned skbuff bridge packet as a parity or runtime-ownership signal",
    "do not treat `kernel/rcu/tree_bridge.zig` as a live bridge claim",
    "`Architecture Council` reopen record linked from the active packet that proposes the wider review",
    "any wording that upgrades this packet into parity, bridge ownership, or a freeze-map status change",
]

FORBIDDEN_MARKERS = [
    "ownership transfer claim",
]


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    note = root / NOTE_PATH
    if not note.exists():
        return [f"missing_file:{NOTE_PATH}"]

    text = note.read_text(encoding="utf-8")
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            failures.append(f"missing_marker:{marker}")

    required_phrases = [
        "It does not claim parity.",
        "It does not claim ownership transfer.",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            failures.append(f"missing_phrase:{phrase}")

    for marker in FORBIDDEN_MARKERS:
        if marker in text:
            failures.append(f"forbidden_marker:{marker}")
    return failures


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


FIXTURE_NOTE = """# Phase 14 Ring Buffer, Skbuff, and RCU Concurrency Survey

This note records the bounded `P14-L12` cross-anchor study packet for the three Phase 14 concurrency-heavy anchors that still stay outside active Zig ownership: `kernel/trace/ring_buffer.c`, `net/core/skbuff.c`, and `kernel/rcu/tree.c`.

## Status
- `PHASE14_LANE_KEY=P14-L12`
- `PHASE14_STATUS_BUCKET=study_only_cross_anchor`
- `PHASE14_SCOPE=ring-buffer-skbuff-rcu-concurrency`
- `PHASE14_BLOCKED_GAP=phase14-cross-anchor-concurrency-bridge-blocker`
- roadmap-aligned owner surfaces for this packet:
  - `Documentation/zigux/phase14-ring-buffer-survey.md`
  - `Documentation/zigux/phase14-skbuff-bridge-survey.md`
  - `Documentation/zigux/phase14-rcu-tree-survey.md`
  - `Documentation/zigux/phase14-core-boundary-traceability.md`
  - `Documentation/zigux/freeze-map.md`

## Why this packet exists
It does not claim parity.
It does not claim ownership transfer.

## Cross-anchor finding
1. Publication and ordering ownership still stays in C.
- ring buffer: `ring_buffer_lock_reserve()`
- skbuff: `validate_xmit_skb_list()`
- RCU tree: `rcu_start_this_gp`

2. Consumer lifetime and teardown ownership still stays in C.
- ring buffer: `ring_buffer_read_page()`
- skbuff: `sock_wfree`
- RCU tree: `rcu_barrier`

3. Asynchronous wake, offload, and escalation ownership still stays in C.
- ring buffer: `ring_buffer_wait()`
- RCU tree: `wake_nocb_gp_defer`

## Explicit stay-in-C decision
- do not treat `kernel/trace/ring_buffer.zig` as an active bridge target
- do not treat the returned skbuff bridge packet as a parity or runtime-ownership signal
- do not treat `kernel/rcu/tree_bridge.zig` as a live bridge claim

## Reopen threshold
- `Architecture Council` reopen record linked from the active packet that proposes the wider review
- any wording that upgrades this packet into parity, bridge ownership, or a freeze-map status change
"""


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-ring-skbuff-rcu-"))
    try:
        write_text(base / NOTE_PATH, FIXTURE_NOTE)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture should pass but failed: {failures!r}")

        cases = [
            ("remove-lane-key", "`PHASE14_LANE_KEY=P14-L12`", "missing_marker:`PHASE14_LANE_KEY=P14-L12`"),
            ("remove-ring-buffer-survey", "`Documentation/zigux/phase14-ring-buffer-survey.md`", "missing_marker:`Documentation/zigux/phase14-ring-buffer-survey.md`"),
            ("remove-publication-heading", "Publication and ordering ownership still stays in C.", "missing_marker:Publication and ordering ownership still stays in C."),
            ("remove-skbuff-marker", "`validate_xmit_skb_list()`", "missing_marker:`validate_xmit_skb_list()`"),
            ("remove-rcu-marker", "`rcu_barrier`", "missing_marker:`rcu_barrier`"),
            ("remove-stay-in-c-decision", "do not treat `kernel/rcu/tree_bridge.zig` as a live bridge claim", "missing_marker:do not treat `kernel/rcu/tree_bridge.zig` as a live bridge claim"),
            ("remove-reopen-threshold", "`Architecture Council` reopen record linked from the active packet that proposes the wider review", "missing_marker:`Architecture Council` reopen record linked from the active packet that proposes the wider review"),
        ]
        for _, marker, expected in cases:
            write_text(base / NOTE_PATH, FIXTURE_NOTE.replace(marker, "", 1))
            failures = validate(base)
            if expected not in failures:
                raise SystemExit(f"expected {expected!r}, got {failures!r}")

        write_text(base / NOTE_PATH, FIXTURE_NOTE.replace("It does not claim ownership transfer.", "", 1))
        failures = validate(base)
        if "missing_phrase:It does not claim ownership transfer." not in failures:
            raise SystemExit(f"expected ownership-transfer phrase failure, got {failures!r}")

        print("PHASE14_RING_SKBUFF_RCU_CONCURRENCY_SURVEY_SELF_TEST=pass")
        print("PHASE14_RING_SKBUFF_RCU_CONCURRENCY_SURVEY_SELF_TEST_CASE_COUNT=8")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the dedicated Phase 14 cross-anchor concurrency survey stays aligned with its stay-in-C contract."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run the fixture-backed self-test.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE14_RING_SKBUFF_RCU_CONCURRENCY_SURVEY=fail")
        print("PHASE14_RING_SKBUFF_RCU_CONCURRENCY_SURVEY_DRIFT_START")
        for failure in failures:
            print(failure)
        print("PHASE14_RING_SKBUFF_RCU_CONCURRENCY_SURVEY_DRIFT_END")
        return 1

    print("PHASE14_RING_SKBUFF_RCU_CONCURRENCY_SURVEY=pass")
    print(f"PHASE14_RING_SKBUFF_RCU_CONCURRENCY_SURVEY_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
