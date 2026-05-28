#!/usr/bin/env python3
"""Guard the current Phase 1 closure workflow packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")

WORKFLOW_ORDERED_STEPS = (
    "      - name: Run current Phase 2 validate make route",
    "      - name: Validate current Phase 2 tool packet",
    "      - name: Self-test current Phase 1 direct-owner checker",
    "      - name: Check current Phase 1 direct-owner markers",
    "      - name: Self-test current Phase 1 direct-anchor manifest gate",
    "      - name: Check current Phase 1 direct-anchor manifest gate",
    "      - name: Self-test current Phase 1 string review checker",
    "      - name: Check current Phase 1 string review packet",
    "      - name: Self-test current Phase 1 find-bit review checker",
    "      - name: Check current Phase 1 find-bit review packet",
    "      - name: Self-test current Phase 1 bitmap direct-anchor checker",
    "      - name: Check current Phase 1 bitmap direct-anchor packet",
    "      - name: Self-test current Phase 1 rbtree review checker",
    "      - name: Check current Phase 1 rbtree review packet",
    "      - name: Self-test current Phase 1 route summary checker",
    "      - name: Check current Phase 1 route summary packet",
    "      - name: Self-test current Phase 1 bench checker",
    "      - name: Self-test current Phase 1 find-bit bench anchor checker",
    "      - name: Check current Phase 1 find-bit bench anchor packet",
    "      - name: Self-test current Phase 1 shared reminder checker",
    "      - name: Check current Phase 1 shared reminder packet",
    "      - name: Self-test current Phase 1 closure validator",
    "      - name: Check current Phase 1 closure packet",
    "      - name: Self-test current Phase 3 interop packet",
    "      - name: Check current Phase 3 interop packet",
    "      - name: Run current Phase 3 shared tests-root packet",
    "      - name: Run current Phase 1 shared tests-root smoke",
    "      - name: Self-test current Phase 4 repo-reality warning checker",
    "      - name: Check current Phase 4 repo-reality warning packet",
)

OPTIONAL_SLOT_STEPS = (
    "      - name: Self-test current Phase 1 workflow slot checker",
    "      - name: Check current Phase 1 workflow slot packet",
)

EXACT_RUN_LINES = (
    "        run: python3 scripts/zigux/validate-phase2.py",
    "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    "        run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "        run: python3 scripts/zigux/validate-phase1-closure.py",
    "        run: python3 scripts/zigux/run-phase3-checks.py",
    "        run: zig build phase3-test --build-file zigux/tests/build.zig",
    "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py",
)

FORBIDDEN_WORKFLOW_LINES = (
    "      - name: Self-test current Phase 1 workflow viability checker",
    "      - name: Check current Phase 1 workflow viability packet",
    "      - name: Self-test current Phase 1 workflow preflight checker",
    "      - name: Check current Phase 1 workflow preflight packet",
    "        run: python3 scripts/zigux/check-phase1-bench.py",
)

CLOSURE_NOTE_MARKERS = (
    "- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
    "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "- `PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet because the shared Phase 1 replay now already owns allocator sizing, zero-filled allocation words, copy/copy-clear-tail/copy-and-extend replay, logical operator outputs, range set/clear/fill/zero outcomes, scnprintf output, truncation, tiny-buffer handling, and partial-window xor replay, so current master keeps whole-word range edges, raw copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage review-visible at the helper surface`",
    "- `PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`",
    "- `PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py exact-checks helper-local rbtree anchors plus the committed duplicate-search and cached-leftmost replay packet across the helper, closure note, lane note, manifest, fixture, and shared smoke route`",
    "- `PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",
    "- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`",
)

FORBIDDEN_CLOSURE_MARKERS = (
    "- `PHASE1_CLOSURE_VALIDATOR_STATE=missing_current_master`",
    "- `PHASE1_NEXT_SAFE_STEP=restore the missing phase1 closure note first`",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative: Path) -> str:
    return (root / relative).read_text(encoding="utf-8")


def require_line_counts(lines: list[str], failures: list[str], expected_lines: tuple[str, ...]) -> None:
    for line in expected_lines:
        count = sum(1 for current in lines if current == line)
        if count != 1:
            failures.append(f"line_count:{line}:expected=1:actual={count}")


def find_index(lines: list[str], target: str) -> int:
    for index, line in enumerate(lines):
        if line == target:
            return index
    return -1


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    workflow_path = root / WORKFLOW_REL
    closure_note_path = root / CLOSURE_NOTE_REL
    if not workflow_path.exists():
        failures.append(f"missing_file:{WORKFLOW_REL.as_posix()}")
    if not closure_note_path.exists():
        failures.append(f"missing_file:{CLOSURE_NOTE_REL.as_posix()}")
    if failures:
        return failures

    workflow_lines = read_text(root, WORKFLOW_REL).splitlines()
    closure_text = read_text(root, CLOSURE_NOTE_REL)

    require_line_counts(workflow_lines, failures, WORKFLOW_ORDERED_STEPS)
    require_line_counts(workflow_lines, failures, EXACT_RUN_LINES)

    last_index = -1
    for step in WORKFLOW_ORDERED_STEPS:
        current_index = find_index(workflow_lines, step)
        if current_index == -1:
            continue
        if current_index <= last_index:
            failures.append(f"step_order:{step}:index={current_index}:previous={last_index}")
        last_index = current_index

    slot_self_index = find_index(workflow_lines, OPTIONAL_SLOT_STEPS[0])
    slot_packet_index = find_index(workflow_lines, OPTIONAL_SLOT_STEPS[1])
    if slot_self_index != -1 or slot_packet_index != -1:
        if slot_self_index == -1 or slot_packet_index == -1:
            failures.append("slot_pair:expected_both_optional_steps")
        elif slot_self_index > slot_packet_index:
            failures.append(
                f"slot_order:self_test_index={slot_self_index}:packet_index={slot_packet_index}"
            )
        else:
            route_summary_index = find_index(workflow_lines, WORKFLOW_ORDERED_STEPS[15])
            bench_index = find_index(workflow_lines, WORKFLOW_ORDERED_STEPS[16])
            if route_summary_index != -1 and slot_self_index <= route_summary_index:
                failures.append(
                    f"slot_position:self_test_index={slot_self_index}:route_summary_index={route_summary_index}"
                )
            if bench_index != -1 and slot_packet_index >= bench_index:
                failures.append(
                    f"slot_position:packet_index={slot_packet_index}:bench_index={bench_index}"
                )

    for line in FORBIDDEN_WORKFLOW_LINES:
        count = sum(1 for current in workflow_lines if current == line)
        if count != 0:
            failures.append(f"forbidden_workflow:{line}:actual={count}")

    for marker in CLOSURE_NOTE_MARKERS:
        if marker not in closure_text:
            failures.append(f"missing_closure_marker:{marker}")

    for marker in FORBIDDEN_CLOSURE_MARKERS:
        if marker in closure_text:
            failures.append(f"forbidden_closure_marker:{marker}")

    return failures


def write_text(root: Path, relative: Path, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_workflow(include_slot_steps: bool = False) -> str:
    lines = [
        "name: zigux-bootstrap",
        "jobs:",
        "  bootstrap:",
        "    steps:",
        "      - name: Run current Phase 2 validate make route",
        "        run: make -C zigux phase2-validate",
        "      - name: Run current Phase 2 aggregate make route",
        "        run: make -C zigux phase2",
        "      - name: Validate current Phase 2 tool packet",
        "        run: python3 scripts/zigux/validate-phase2.py",
        "      - name: Self-test current Phase 1 direct-owner checker",
        "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "      - name: Check current Phase 1 direct-owner markers",
        "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
        "      - name: Self-test current Phase 1 direct-anchor manifest gate",
        "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
        "      - name: Check current Phase 1 direct-anchor manifest gate",
        "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "      - name: Self-test current Phase 1 string review checker",
        "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
        "      - name: Check current Phase 1 string review packet",
        "        run: python3 scripts/zigux/check-phase1-string-review-packet.py",
        "      - name: Self-test current Phase 1 find-bit review checker",
        "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
        "      - name: Check current Phase 1 find-bit review packet",
        "        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
        "      - name: Self-test current Phase 1 bitmap direct-anchor checker",
        "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
        "      - name: Check current Phase 1 bitmap direct-anchor packet",
        "        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
        "      - name: Self-test current Phase 1 rbtree review checker",
        "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
        "      - name: Check current Phase 1 rbtree review packet",
        "        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
        "      - name: Self-test current Phase 1 route summary checker",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "      - name: Check current Phase 1 route summary packet",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    ]
    if include_slot_steps:
        lines.extend(
            [
                "      - name: Self-test current Phase 1 workflow slot checker",
                "        run: python3 scripts/zigux/check-phase1-workflow-slot.py --self-test",
                "      - name: Check current Phase 1 workflow slot packet",
                "        run: python3 scripts/zigux/check-phase1-workflow-slot.py",
            ]
        )
    lines.extend(
        [
            "      - name: Self-test current Phase 1 bench checker",
            "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
            "      - name: Self-test current Phase 1 find-bit bench anchor checker",
            "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
            "      - name: Check current Phase 1 find-bit bench anchor packet",
            "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
            "      - name: Self-test current Phase 1 shared reminder checker",
            "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
            "      - name: Check current Phase 1 shared reminder packet",
            "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
            "      - name: Self-test current Phase 1 closure validator",
            "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
            "      - name: Check current Phase 1 closure packet",
            "        run: python3 scripts/zigux/validate-phase1-closure.py",
            "      - name: Self-test current Phase 3 interop packet",
            "        run: python3 scripts/zigux/validate_phase3_selftest.py",
            "      - name: Check current Phase 3 interop packet",
            "        run: python3 scripts/zigux/run-phase3-checks.py",
            "      - name: Run current Phase 3 shared tests-root packet",
            "        run: zig build phase3-test --build-file zigux/tests/build.zig",
            "      - name: Run current Phase 1 shared tests-root smoke",
            "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
            "      - name: Self-test current Phase 4 repo-reality warning checker",
            "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
            "      - name: Check current Phase 4 repo-reality warning packet",
            "        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py",
        ]
    )
    return "\n".join(lines) + "\n"


def build_sample_closure_note() -> str:
    return "\n".join(
        [
            "# Phase 1 Closure",
            "",
            "## Closure Validation",
            "",
            *CLOSURE_NOTE_MARKERS,
            "",
        ]
    )


def build_sample_root(root: Path, include_slot_steps: bool = False) -> None:
    write_text(root, WORKFLOW_REL, build_sample_workflow(include_slot_steps=include_slot_steps))
    write_text(root, CLOSURE_NOTE_REL, build_sample_closure_note())


def remove_line(root: Path, relative: Path, target: str) -> None:
    path = root / relative
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line == target:
            del lines[index]
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(f"missing target line: {target}")


def add_line(root: Path, relative: Path, target: str) -> None:
    path = root / relative
    lines = path.read_text(encoding="utf-8").splitlines()
    lines.append(target)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def duplicate_line(root: Path, relative: Path, target: str) -> None:
    path = root / relative
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line == target:
            lines.insert(index + 1, target)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(f"missing target line: {target}")


def swap_lines(root: Path, first: str, second: str) -> None:
    path = root / WORKFLOW_REL
    lines = path.read_text(encoding="utf-8").splitlines()
    first_index = lines.index(first)
    second_index = lines.index(second)
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def remove_marker(root: Path, marker: str) -> None:
    path = root / CLOSURE_NOTE_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", ""), encoding="utf-8")


def add_marker(root: Path, marker: str) -> None:
    path = root / CLOSURE_NOTE_REL
    path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = (
        ("success_delegated", None, False),
        ("success_slot_wired", None, True),
        ("missing_workflow", ("remove_file", WORKFLOW_REL), False),
        ("missing_closure_note", ("remove_file", CLOSURE_NOTE_REL), False),
        ("missing_bitmap_packet", ("remove_line", WORKFLOW_REL, WORKFLOW_ORDERED_STEPS[10]), False),
        ("missing_rbtree_packet", ("remove_line", WORKFLOW_REL, WORKFLOW_ORDERED_STEPS[13]), False),
        ("missing_route_summary_packet", ("remove_line", WORKFLOW_REL, WORKFLOW_ORDERED_STEPS[15]), False),
        ("duplicate_smoke_step", ("duplicate_line", WORKFLOW_REL, WORKFLOW_ORDERED_STEPS[26]), False),
        ("phase3_phase1_smoke_swap", ("swap_lines", WORKFLOW_ORDERED_STEPS[25], WORKFLOW_ORDERED_STEPS[26]), False),
        ("forbidden_viability_step", ("add_line", WORKFLOW_REL, FORBIDDEN_WORKFLOW_LINES[0]), False),
        ("missing_bitmap_marker", ("remove_marker", CLOSURE_NOTE_MARKERS[3]), False),
        ("missing_closure_validator_marker", ("remove_marker", CLOSURE_NOTE_MARKERS[0]), False),
        ("forbidden_old_closure_marker", ("add_marker", FORBIDDEN_CLOSURE_MARKERS[0]), False),
        ("slot_pair_incomplete", ("add_line", WORKFLOW_REL, OPTIONAL_SLOT_STEPS[0]), False),
        ("slot_packet_after_bench", ("late_slot_packet",), False),
    )

    for name, mutation, include_slot_steps in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-closure-workflow-") as tmpdir:
            root = Path(tmpdir)
            build_sample_root(root, include_slot_steps=include_slot_steps)
            if mutation is not None:
                kind = mutation[0]
                if kind == "remove_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove_line":
                    remove_line(root, mutation[1], mutation[2])
                elif kind == "duplicate_line":
                    duplicate_line(root, mutation[1], mutation[2])
                elif kind == "swap_lines":
                    swap_lines(root, mutation[1], mutation[2])
                elif kind == "add_line":
                    add_line(root, mutation[1], mutation[2])
                elif kind == "remove_marker":
                    remove_marker(root, mutation[1])
                elif kind == "add_marker":
                    add_marker(root, mutation[1])
                elif kind == "late_slot_packet":
                    add_line(root, WORKFLOW_REL, OPTIONAL_SLOT_STEPS[0])
                    add_line(root, WORKFLOW_REL, OPTIONAL_SLOT_STEPS[1])
                else:
                    raise ValueError(f"unknown mutation: {kind}")

            failures = collect_failures(root)
            if name.startswith("success_"):
                if failures:
                    print("PHASE1_CLOSURE_WORKFLOW_PACKET_SELF_TEST=fail")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"PHASE1_CLOSURE_WORKFLOW_PACKET_SELF_TEST_CASE_FAILED={name}")
                return 1

    print("PHASE1_CLOSURE_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_CLOSURE_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample root for replay validation",
    )
    parser.add_argument(
        "--sample-mode",
        choices=("delegated", "slot-wired"),
        default="delegated",
        help="sample-root flavor to write",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        root = Path(args.write_sample_root).resolve()
        build_sample_root(root, include_slot_steps=args.sample_mode == "slot-wired")
        print(f"phase1-closure-workflow-packet:sample-root-written:{root}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_CLOSURE_WORKFLOW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    mode = "slot-wired" if OPTIONAL_SLOT_STEPS[0] in read_text(repo_root(args.root), WORKFLOW_REL) else "delegated-current-master"
    print("PHASE1_CLOSURE_WORKFLOW_PACKET=pass")
    print(f"PHASE1_CLOSURE_WORKFLOW_PACKET_MODE={mode}")
    print(f"PHASE1_CLOSURE_WORKFLOW_PACKET_REQUIRED_STEP_COUNT={len(WORKFLOW_ORDERED_STEPS)}")
    print(f"PHASE1_CLOSURE_WORKFLOW_PACKET_REQUIRED_MARKER_COUNT={len(CLOSURE_NOTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
