#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile


WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

RETAINED_STEPS = (
    ("- name: Run Phase 4 artifact-diff contract make route", "run: make -C zigux phase4-artifact-diff-contract"),
    ("- name: Run focused Phase 8 libbpf segment tests", "run: make -C zigux phase8-libbpf-segments-test"),
    ("- name: Self-test current Phase 9 trace-events direct-summary checker", "run: python3 scripts/zigux/check-phase9-trace-events-direct-summary.py --self-test"),
    ("- name: Check current Phase 9 trace-events direct-summary packet", "run: python3 scripts/zigux/check-phase9-trace-events-direct-summary.py"),
    ("- name: Self-test current Phase 12 complex-driver lane packet checker", "run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test"),
    ("- name: Check current Phase 12 complex-driver lane packet", "run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py"),
    ("- name: Self-test current Phase 12 libbpf snapshot checker", "run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test"),
    ("- name: Check current Phase 12 libbpf snapshot packet", "run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py"),
    ("- name: Self-test current Phase 12 libbpf heavy-consumer packet checker", "run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test"),
    ("- name: Check current Phase 12 libbpf heavy-consumer packet", "run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py"),
)

ORDERED_STEP_PAIRS = (
    (
        "- name: Run Phase 4 rollback tests",
        "- name: Run Phase 4 artifact-diff contract make route",
    ),
    (
        "- name: Run focused Phase 8 exec-cmd tests",
        "- name: Run focused Phase 8 libbpf segment tests",
    ),
    (
        "- name: Check current Phase 9 trace-events runtime packet",
        "- name: Self-test current Phase 9 trace-events direct-summary checker",
    ),
    (
        "- name: Check current Phase 9 trace-events direct-summary packet",
        "- name: Self-test current Phase 9 trace-events summary-preservation checker",
    ),
    (
        "- name: Check current Phase 12 build-only surface",
        "- name: Self-test current Phase 12 complex-driver lane packet checker",
    ),
    (
        "- name: Check current Phase 12 complex-driver lane packet",
        "- name: Self-test current Phase 12 release-readiness packet checker",
    ),
    (
        "- name: Check current Phase 12 release-readiness packet",
        "- name: Self-test current Phase 12 libbpf snapshot checker",
    ),
    (
        "- name: Check current Phase 12 libbpf snapshot packet",
        "- name: Self-test current Phase 12 libbpf heavy-consumer packet checker",
    ),
    (
        "- name: Check current Phase 12 libbpf heavy-consumer packet",
        "- name: Validate current Phase 12 support bundle",
    ),
)


def require_marker(text: str, marker: str, label: str) -> None:
    if marker not in text:
        raise SystemExit(f"lane05 retained bootstrap step guard missing {label}: {marker}")


def require_exact_line_count(text: str, marker: str, expected: int, label: str) -> None:
    actual = sum(1 for line in text.splitlines() if line.strip() == marker)
    if actual != expected:
        raise SystemExit(
            "lane05 retained bootstrap step guard expected exactly "
            f"{expected} occurrences of {label} {marker}, found {actual}"
        )


def require_order(text: str, earlier: str, later: str, label: str) -> None:
    earlier_index = text.find(earlier)
    later_index = text.find(later)
    if earlier_index == -1 or later_index == -1:
        raise SystemExit(
            f"lane05 retained bootstrap step guard missing ordered markers for {label}"
        )
    if earlier_index >= later_index:
        raise SystemExit(
            "lane05 retained bootstrap step guard expected "
            f"{label} `{earlier}` before `{later}`"
        )


def check_workflow(text: str) -> None:
    for step_name, command in RETAINED_STEPS:
        require_marker(text, step_name, "step name")
        require_exact_line_count(text, step_name, 1, "step name")
        require_marker(text, command, "step command")
        require_exact_line_count(text, command, 1, "step command")

    for earlier, later in ORDERED_STEP_PAIRS:
        require_order(text, earlier, later, "workflow step order")


def sample_workflow() -> str:
    return """name: zigux-bootstrap
jobs:
  bootstrap:
    steps:
      - name: Run Phase 4 rollback tests
        run: make -C zigux phase4-test
      - name: Run Phase 4 artifact-diff contract make route
        run: make -C zigux phase4-artifact-diff-contract
      - name: Run focused Phase 8 exec-cmd tests
        run: make -C zigux phase8-exec-cmd-test
      - name: Run focused Phase 8 libbpf segment tests
        run: make -C zigux phase8-libbpf-segments-test
      - name: Check current Phase 9 trace-events runtime packet
        run: python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py
      - name: Self-test current Phase 9 trace-events direct-summary checker
        run: python3 scripts/zigux/check-phase9-trace-events-direct-summary.py --self-test
      - name: Check current Phase 9 trace-events direct-summary packet
        run: python3 scripts/zigux/check-phase9-trace-events-direct-summary.py
      - name: Self-test current Phase 9 trace-events summary-preservation checker
        run: python3 scripts/zigux/check-phase9-trace-events-summary-preservation.py --self-test
      - name: Check current Phase 12 build-only surface
        run: python3 scripts/zigux/check-build-only-phase12-surface.py
      - name: Self-test current Phase 12 complex-driver lane packet checker
        run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test
      - name: Check current Phase 12 complex-driver lane packet
        run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py
      - name: Self-test current Phase 12 release-readiness packet checker
        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test
      - name: Check current Phase 12 release-readiness packet
        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py
      - name: Self-test current Phase 12 libbpf snapshot checker
        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test
      - name: Check current Phase 12 libbpf snapshot packet
        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py
      - name: Self-test current Phase 12 libbpf heavy-consumer packet checker
        run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test
      - name: Check current Phase 12 libbpf heavy-consumer packet
        run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py
      - name: Validate current Phase 12 support bundle
        run: python3 scripts/zigux/validate-phase12.py
"""


def run_self_test() -> int:
    workflow = sample_workflow()
    check_workflow(workflow)
    case_count = 1

    missing_phase4 = workflow.replace(
        "      - name: Run Phase 4 artifact-diff contract make route\n        run: make -C zigux phase4-artifact-diff-contract\n",
        "",
        1,
    )
    try:
        check_workflow(missing_phase4)
    except SystemExit as exc:
        assert "artifact-diff contract" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing Phase 4 artifact-diff contract step failure")

    duplicate_phase8 = workflow.replace(
        "      - name: Run focused Phase 8 libbpf segment tests\n        run: make -C zigux phase8-libbpf-segments-test\n",
        "      - name: Run focused Phase 8 libbpf segment tests\n        run: make -C zigux phase8-libbpf-segments-test\n"
        "      - name: Run focused Phase 8 libbpf segment tests\n        run: make -C zigux phase8-libbpf-segments-test\n",
        1,
    )
    try:
        check_workflow(duplicate_phase8)
    except SystemExit as exc:
        assert "expected exactly 1 occurrences" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected duplicate Phase 8 libbpf step failure")

    reordered_phase9 = workflow.replace(
        "      - name: Check current Phase 9 trace-events runtime packet\n        run: python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py\n"
        "      - name: Self-test current Phase 9 trace-events direct-summary checker\n        run: python3 scripts/zigux/check-phase9-trace-events-direct-summary.py --self-test\n",
        "      - name: Self-test current Phase 9 trace-events direct-summary checker\n        run: python3 scripts/zigux/check-phase9-trace-events-direct-summary.py --self-test\n"
        "      - name: Check current Phase 9 trace-events runtime packet\n        run: python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py\n",
        1,
    )
    try:
        check_workflow(reordered_phase9)
    except SystemExit as exc:
        assert "workflow step order" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected reordered Phase 9 step failure")

    missing_phase12 = workflow.replace(
        "      - name: Self-test current Phase 12 libbpf snapshot checker\n        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test\n"
        "      - name: Check current Phase 12 libbpf snapshot packet\n        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py\n",
        "",
        1,
    )
    try:
        check_workflow(missing_phase12)
    except SystemExit as exc:
        assert "libbpf snapshot" in str(exc)
        case_count += 1
    else:
        raise AssertionError("expected missing Phase 12 libbpf snapshot step failure")

    print("LANE05_RETAINED_BOOTSTRAP_STEPS_SELF_TEST=pass")
    print(f"LANE05_RETAINED_BOOTSTRAP_STEPS_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Lane 05 workflow restack preserves unrelated retained bootstrap steps."
    )
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--workflow",
        type=Path,
        default=WORKFLOW_PATH,
        help="Path to .github/workflows/zigux-bootstrap.yml",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    check_workflow(args.workflow.read_text(encoding="utf-8"))
    print("LANE05_RETAINED_BOOTSTRAP_STEPS=pass")
    print(f"LANE05_RETAINED_BOOTSTRAP_STEP_COUNT={len(RETAINED_STEPS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
