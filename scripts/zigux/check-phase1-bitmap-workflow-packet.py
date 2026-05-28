#!/usr/bin/env python3
"""Guard the current Phase 1 bitmap workflow packet against workflow and reminder drift."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
BITMAP_CHECKER_REL = Path("scripts/zigux/check-phase1-bitmap-direct-anchors.py")
BITMAP_HELPER_REL = Path("tools/lib/bitmap.zig")

REQUIRED_FILES = (
    WORKFLOW_REL,
    CLOSURE_REL,
    SCRIPTS_README_REL,
    BITMAP_CHECKER_REL,
    BITMAP_HELPER_REL,
)

REQUIRED_WORKFLOW_LINES = (
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
)

REQUIRED_CLOSURE_MARKERS = (
    "`PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet because the shared Phase 1 replay now already owns allocator sizing, zero-filled allocation words, copy/copy-clear-tail/copy-and-extend replay, logical operator outputs, range set/clear/fill/zero outcomes, scnprintf output, truncation, tiny-buffer handling, and partial-window xor replay, so current master keeps whole-word range edges, raw copy alias behavior, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, out-of-range tail-bit full or empty or weight masking, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage review-visible at the helper surface`",
    "`PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`",
)

REQUIRED_SCRIPTS_README_MARKERS = (
    "`scripts/zigux/check-phase1-bitmap-direct-anchors.py` is directly readable on current `master`, so bitmap-side follow-through should keep that helper-local guard wired into the scripts-root reminder packet and bootstrap workflow instead of leaving the bitmap direct-anchor route as lane-note-only context",
)

REQUIRED_BITMAP_CHECKER_MARKERS = (
    '"""Guard the Phase 1 bitmap direct-anchor packet against helper-local drift."""',
    'print("PHASE1_BITMAP_DIRECT_ANCHORS=pass")',
    'print("PHASE1_BITMAP_DIRECT_ANCHORS_SELF_TEST=pass")',
)

REQUIRED_BITMAP_HELPER_MARKERS = (
    'test "bitmap or keeps caller-selected bit window" {',
    'test "bitmap weighted and andnot clamp counts to the declared tail window" {',
    'test "bitmap Linux-style aliases mirror copy logical range and format helpers" {',
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_count(text: str, label: str, needle: str, expected: int = 1) -> list[str]:
    actual = text.count(needle)
    return [] if actual == expected else [f"{label}:expected={expected}:actual={actual}"]


def require_exact_line(text: str, label: str, needle: str, expected: int = 1) -> list[str]:
    actual = sum(1 for line in text.splitlines() if line == needle)
    return [] if actual == expected else [f"{label}:expected={expected}:actual={actual}"]


def collect_workflow_failures(text: str) -> list[str]:
    failures: list[str] = []
    lines = text.splitlines()
    positions: list[int] = []
    for idx, line in enumerate(REQUIRED_WORKFLOW_LINES):
        failures.extend(require_exact_line(text, f"workflow_line_{idx}", line))
        positions.append(next((line_idx for line_idx, current in enumerate(lines) if current == line), -1))
    if failures:
        return failures
    if positions != sorted(positions):
        failures.append("workflow_order:expected=ascending:actual=drifted")
    return failures


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    workflow_text = load_text(root, WORKFLOW_REL)
    failures.extend(collect_workflow_failures(workflow_text))

    closure_text = load_text(root, CLOSURE_REL)
    for idx, marker in enumerate(REQUIRED_CLOSURE_MARKERS):
        failures.extend(require_exact_count(closure_text, f"closure_marker_{idx}", marker))

    scripts_readme_text = load_text(root, SCRIPTS_README_REL)
    for idx, marker in enumerate(REQUIRED_SCRIPTS_README_MARKERS):
        failures.extend(require_exact_count(scripts_readme_text, f"scripts_readme_marker_{idx}", marker))

    bitmap_checker_text = load_text(root, BITMAP_CHECKER_REL)
    for idx, marker in enumerate(REQUIRED_BITMAP_CHECKER_MARKERS):
        failures.extend(require_exact_count(bitmap_checker_text, f"bitmap_checker_marker_{idx}", marker))

    bitmap_helper_text = load_text(root, BITMAP_HELPER_REL)
    for idx, marker in enumerate(REQUIRED_BITMAP_HELPER_MARKERS):
        failures.extend(require_exact_count(bitmap_helper_text, f"bitmap_helper_marker_{idx}", marker))

    return failures


def write_text(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(root, WORKFLOW_REL, "\n".join(REQUIRED_WORKFLOW_LINES) + "\n")
    write_text(root, CLOSURE_REL, "\n".join(REQUIRED_CLOSURE_MARKERS) + "\n")
    write_text(root, SCRIPTS_README_REL, "\n".join(REQUIRED_SCRIPTS_README_MARKERS) + "\n")
    write_text(root, BITMAP_CHECKER_REL, "\n".join(REQUIRED_BITMAP_CHECKER_MARKERS) + "\n")
    write_text(root, BITMAP_HELPER_REL, "\n".join(REQUIRED_BITMAP_HELPER_MARKERS) + "\n")


def write_sample_root(root: Path) -> None:
    build_sample_repo(root)


def remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def duplicate_marker(root: Path, relative_path: Path, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("baseline", None)]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", lambda root, relative_path=relative_path: (root / relative_path).unlink()))
    for marker in REQUIRED_WORKFLOW_LINES:
        cases.append((f"missing_workflow:{marker}", lambda root, marker=marker: remove_marker(root, WORKFLOW_REL, marker)))
        cases.append((f"duplicate_workflow:{marker}", lambda root, marker=marker: duplicate_marker(root, WORKFLOW_REL, marker)))
    for marker in REQUIRED_CLOSURE_MARKERS:
        cases.append((f"missing_closure:{marker}", lambda root, marker=marker: remove_marker(root, CLOSURE_REL, marker)))
    for marker in REQUIRED_SCRIPTS_README_MARKERS:
        cases.append((f"missing_scripts_readme:{marker}", lambda root, marker=marker: remove_marker(root, SCRIPTS_README_REL, marker)))
    for marker in REQUIRED_BITMAP_CHECKER_MARKERS:
        cases.append((f"missing_bitmap_checker:{marker}", lambda root, marker=marker: remove_marker(root, BITMAP_CHECKER_REL, marker)))
    for marker in REQUIRED_BITMAP_HELPER_MARKERS:
        cases.append((f"missing_bitmap_helper:{marker}", lambda root, marker=marker: remove_marker(root, BITMAP_HELPER_REL, marker)))

    for name, mutate in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bitmap-workflow-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutate is not None:
                mutate(root)
            failures = collect_failures(root)
            if name == "baseline":
                if failures:
                    print(f"self-test:{name}:unexpected={failures}")
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_BITMAP_WORKFLOW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_BITMAP_WORKFLOW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run synthetic self-tests")
    parser.add_argument("--write-sample-root", help="materialize a passing sample root and exit")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_BITMAP_WORKFLOW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BITMAP_WORKFLOW_PACKET=pass")
    print(f"PHASE1_BITMAP_WORKFLOW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BITMAP_WORKFLOW_PACKET_REQUIRED_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
