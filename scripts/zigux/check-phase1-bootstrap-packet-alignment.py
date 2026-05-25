#!/usr/bin/env python3
"""Guard the live Phase 1 bootstrap packet order and checker surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
DIRECT_OWNER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
DIRECT_ANCHOR_REL = Path("scripts/zigux/check-phase1-direct-anchor-manifest-gate.py")
STRING_REVIEW_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
FIND_BIT_REVIEW_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")
ROUTE_SUMMARY_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
BENCH_REL = Path("scripts/zigux/check-phase1-bench.py")
FIND_BIT_BENCH_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")
SHARED_REMINDER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")

REQUIRED_FILES = (
    WORKFLOW_REL,
    DIRECT_OWNER_REL,
    DIRECT_ANCHOR_REL,
    STRING_REVIEW_REL,
    FIND_BIT_REVIEW_REL,
    ROUTE_SUMMARY_REL,
    BENCH_REL,
    FIND_BIT_BENCH_REL,
    SHARED_REMINDER_REL,
    CLOSURE_VALIDATOR_REL,
)

SCRIPT_MARKERS = {
    DIRECT_OWNER_REL: ('print("PHASE1_DIRECT_OWNER_MARKERS=pass")', 'print("PHASE1_DIRECT_OWNER_MARKERS_SELF_TEST=pass")'),
    DIRECT_ANCHOR_REL: ('print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=pass")', 'print("PHASE1_DIRECT_ANCHOR_MANIFEST_GATE_SELF_TEST=pass")'),
    STRING_REVIEW_REL: ('print("phase1-string-review-packet:ok")', 'print("PHASE1_STRING_REVIEW_PACKET_SELF_TEST=pass")'),
    FIND_BIT_REVIEW_REL: ('print("phase1-find-bit-review-packet:ok")', 'print("PHASE1_FIND_BIT_REVIEW_PACKET_SELF_TEST=pass")'),
    ROUTE_SUMMARY_REL: ('print("PHASE1_ROUTE_SUMMARY_COUNTS=pass")', 'print("PHASE1_ROUTE_SUMMARY_COUNTS_SELF_TEST=pass")'),
    BENCH_REL: ('print("PHASE1_BENCH_CHECK_SELF_TEST=pass")', 'PHASE1_BENCH_CHECK_SELF_TEST_CASE_COUNT='),
    FIND_BIT_BENCH_REL: ('print("PHASE1_FIND_BIT_BENCH_ANCHORS=pass")', 'print("PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass")'),
    SHARED_REMINDER_REL: ('print("PHASE1_SHARED_REMINDER_PACKET=pass")', 'print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")'),
    CLOSURE_VALIDATOR_REL: ('print("PHASE1_CLOSURE_VALIDATION=pass")', 'print("PHASE1_CLOSURE_SELF_TEST=pass")'),
}

PACKET_STEPS = (
    ("Self-test current Phase 1 direct-owner checker", "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test"),
    ("Check current Phase 1 direct-owner markers", "python3 scripts/zigux/check-phase1-direct-owner-markers.py"),
    ("Self-test current Phase 1 direct-anchor manifest gate", "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test"),
    ("Check current Phase 1 direct-anchor manifest gate", "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py"),
    ("Self-test current Phase 1 string review checker", "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test"),
    ("Check current Phase 1 string review packet", "python3 scripts/zigux/check-phase1-string-review-packet.py"),
    ("Self-test current Phase 1 find-bit review checker", "python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test"),
    ("Check current Phase 1 find-bit review packet", "python3 scripts/zigux/check-phase1-find-bit-review-packet.py"),
    ("Self-test current Phase 1 route summary checker", "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test"),
    ("Check current Phase 1 route summary packet", "python3 scripts/zigux/check-phase1-route-summary-counts.py"),
    ("Self-test current Phase 1 bench checker", "python3 scripts/zigux/check-phase1-bench.py --self-test"),
    ("Self-test current Phase 1 find-bit bench anchor checker", "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test"),
    ("Check current Phase 1 find-bit bench anchor packet", "python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py"),
    ("Self-test current Phase 1 shared reminder checker", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test"),
    ("Check current Phase 1 shared reminder packet", "python3 scripts/zigux/check-phase1-shared-reminder-packet.py"),
    ("Self-test current Phase 1 closure validator", "python3 scripts/zigux/validate-phase1-closure.py --self-test"),
    ("Check current Phase 1 closure packet", "python3 scripts/zigux/validate-phase1-closure.py"),
    ("Self-test current Phase 3 interop packet", "python3 scripts/zigux/validate_phase3_selftest.py"),
    ("Check current Phase 3 interop packet", "python3 scripts/zigux/run-phase3-checks.py"),
    ("Run current Phase 3 export/UAPI layout replay", "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig"),
    ("Run current Phase 3 export shim replay", "zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig"),
    ("Run current Phase 3 policy starter-packet replay", "make -C zigux phase3-policy-starter-packet-test"),
    ("Run current Phase 3 policy dump replay", "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig"),
    ("Run current Phase 3 policy dump make wrapper", "make -C zigux phase3-policy-dump"),
    ("Self-test current Phase 3 low-level wrapper survey validator", "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"),
    ("Check current Phase 3 low-level wrapper survey packet", "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py"),
    ("Run current Phase 3 low-level wrapper replay", "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig"),
    ("Run current Phase 3 shared tests-root packet", "zig build phase3-test --build-file zigux/tests/build.zig"),
    ("Run current Phase 3 ABI dump replay", "zig build phase3-dump --build-file zigux/tests/build.zig"),
    ("Run current Phase 1 shared tests-root smoke", "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig"),
)

PREDECESSOR = ("Validate current Phase 2 tool packet", "python3 scripts/zigux/validate-phase2.py")
SUCCESSOR = ("Self-test current Phase 4 repo-reality warning checker", "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test")
FORBIDDEN_LINES = (
    "run: python3 scripts/zigux/check-phase1-bootstrap-packet-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase1-bootstrap-packet-alignment.py",
)


def root_path(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def exact_count(text: str, needle: str) -> int:
    return text.count(needle)


def stripped_count(text: str, needle: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == needle)


def step_block(name: str, run: str) -> str:
    return f"      - name: {name}\n        run: {run}"


def step_names(text: str) -> list[str]:
    prefix = "      - name: "
    return [line[len(prefix):] for line in text.splitlines() if line.startswith(prefix)]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            failures.append(f"missing_file:{rel.as_posix()}")
    if failures:
        return failures

    for rel, markers in SCRIPT_MARKERS.items():
        text = read_text(root, rel)
        for marker in markers:
            if exact_count(text, marker) != 1:
                failures.append(f"{rel.as_posix()}:{marker}:expected=1:actual={exact_count(text, marker)}")

    workflow = read_text(root, WORKFLOW_REL)
    for name, run in (PREDECESSOR, SUCCESSOR):
        if stripped_count(workflow, f"- name: {name}") != 1:
            failures.append(f"workflow_name:{name}:expected=1")
        if stripped_count(workflow, f"run: {run}") != 1:
            failures.append(f"workflow_run:{run}:expected=1")
        if exact_count(workflow, step_block(name, run)) != 1:
            failures.append(f"workflow_pair:{name}:expected=1")

    positions: list[int] = []
    names: list[str] = []
    for name, run in PACKET_STEPS:
        names.append(name)
        if stripped_count(workflow, f"- name: {name}") != 1:
            failures.append(f"workflow_name:{name}:expected=1")
        if stripped_count(workflow, f"run: {run}") != 1:
            failures.append(f"workflow_run:{run}:expected=1")
        block = step_block(name, run)
        if exact_count(workflow, block) != 1:
            failures.append(f"workflow_pair:{name}:expected=1")
        else:
            positions.append(workflow.index(block))
    if failures:
        return failures

    if positions != sorted(positions):
        failures.append("workflow_order:expected=strictly_increasing:actual=out_of_order")

    chain = tuple(names)
    workflow_names = step_names(workflow)
    if not any(tuple(workflow_names[i:i + len(chain)]) == chain for i in range(len(workflow_names) - len(chain) + 1)):
        failures.append("workflow_phase1_packet:expected=adjacent:actual=split_or_interleaved")

    boundary = (PREDECESSOR[0],) + chain + (SUCCESSOR[0],)
    if not any(tuple(workflow_names[i:i + len(boundary)]) == boundary for i in range(len(workflow_names) - len(boundary) + 1)):
        failures.append("workflow_phase1_packet_slot:expected=between_phase2_tail_and_phase4_head:actual=split_or_shifted")

    for line in FORBIDDEN_LINES:
        if stripped_count(workflow, line) != 0:
            failures.append(f"workflow_forbidden:{line}:expected=0")
    return failures


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_root(root: Path) -> None:
    for rel, markers in SCRIPT_MARKERS.items():
        write_text(root, rel, "\n".join(markers) + "\n")
    blocks = [step_block(*PREDECESSOR)]
    blocks.extend(step_block(name, run) for name, run in PACKET_STEPS)
    blocks.append(step_block(*SUCCESSOR))
    write_text(root, WORKFLOW_REL, "\n".join(blocks) + "\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-bootstrap-packet-") as tmp:
        root = Path(tmp)
        build_sample_root(root)
        if collect_failures(root):
            print("self-test:baseline:unexpected_failure")
            return 1

        (root / DIRECT_ANCHOR_REL).unlink()
        if not collect_failures(root):
            print("self-test:missing_file:expected_failure")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bootstrap-packet-") as tmp:
        root = Path(tmp)
        build_sample_root(root)
        bad = read_text(root, SHARED_REMINDER_REL).replace('print("PHASE1_SHARED_REMINDER_PACKET=pass")\n', "", 1)
        write_text(root, SHARED_REMINDER_REL, bad)
        if not collect_failures(root):
            print("self-test:missing_marker:expected_failure")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bootstrap-packet-") as tmp:
        root = Path(tmp)
        build_sample_root(root)
        bad = read_text(root, WORKFLOW_REL).replace(
            "      - name: Check current Phase 1 route summary packet\n",
            "      - name: Check current Phase 1 route summary packet\n      - name: Drifted current Phase 1 spacer\n        run: true\n",
            1,
        )
        write_text(root, WORKFLOW_REL, bad)
        if not collect_failures(root):
            print("self-test:workflow_spacer:expected_failure")
            return 1

    with tempfile.TemporaryDirectory(prefix="phase1-bootstrap-packet-") as tmp:
        root = Path(tmp)
        build_sample_root(root)
        bad = read_text(root, WORKFLOW_REL) + "        run: python3 scripts/zigux/check-phase1-bootstrap-packet-alignment.py --self-test\n"
        write_text(root, WORKFLOW_REL, bad)
        if not collect_failures(root):
            print("self-test:forbidden_line:expected_failure")
            return 1

    print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SELF_TEST=pass")
    print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(root_path(args.root))
    if failures:
        print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT=pass")
    print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_REQUIRED_WORKFLOW_STEP_COUNT={len(PACKET_STEPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
