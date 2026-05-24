#!/usr/bin/env python3
"""Guard the live Phase 1 find_bit bench-adjacent packet on current master."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
FIND_BIT_BENCH_ANCHORS_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")
FIND_BIT_HELPER_REL = Path("tools/lib/find_bit.zig")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    CLOSURE_VALIDATOR_REL,
    FIND_BIT_BENCH_ANCHORS_REL,
    FIND_BIT_HELPER_REL,
    WORKFLOW_REL,
)

REQUIRED_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "Current `master` also ships `scripts/zigux/check-phase1-find-bit-bench-anchors.py` as a helper-local current-head guard: it exact-checks the inclusive-boundary, past-`nbits` no-read, `clump8` past-end no-read, and tail-clamped `findLastBit()` anchors directly in `tools/lib/find_bit.zig` while the broader expectations packet remains absent.",
        "- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
        "- `PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",
        "Current `master` also now spells the lead direct anchor as `find first and next set bits across words, with andnot gaps explicit`, names the underscore and Linux-style alias anchors `including andnot`, and keeps the dedicated `single-word tail windows keep the last in-range next matches reachable from an inclusive start` proof alongside the head-word and tail-word boundary packet, so leave `find_bit` parked unless one of those direct anchors or committed replay fields drifts.",
    ),
    CLOSURE_VALIDATOR_REL: (
        'FIND_BIT_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-review-packet.py")',
        'FIND_BIT_BENCH_ANCHOR_CHECKER_REL = Path("scripts/zigux/check-phase1-find-bit-bench-anchors.py")',
        '    "find_bit_bench_anchor_guard": "`PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`",',
        '    (FIND_BIT_REVIEW_CHECKER_REL, "phase1-find-bit-review-packet"),',
        '    (FIND_BIT_BENCH_ANCHOR_CHECKER_REL, "phase1-find-bit-bench-anchors"),',
    ),
    FIND_BIT_BENCH_ANCHORS_REL: (
        '"boundary_head_test": \'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start" {\'',
        '"single_word_tail_test": \'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start" {\'',
        '"find_next_andnot_boundary": "findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary)"',
        '"find_clump8_low_level_alias_past_end": "_find_next_clump8(&clump, &empty, 8, 20)"',
        'print("PHASE1_FIND_BIT_BENCH_ANCHORS_SELF_TEST=pass")',
    ),
    FIND_BIT_HELPER_REL: (
        'test "head-word boundary scans keep the last in-range bit reachable from an inclusive start" {',
        'test "single-word tail windows keep the last in-range next matches reachable from an inclusive start" {',
        'test "clump8 past-end scans return without reading bitmap words" {',
        "findNextAndNotBit(&andnot_lhs, &andnot_rhs, nbits, boundary)",
        "_find_next_clump8(&clump, &empty, 8, 20)",
    ),
    WORKFLOW_REL: (
        "      - name: Self-test current Phase 1 bench checker",
        "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "      - name: Self-test current Phase 1 shared reminder checker",
        "      - name: Check current Phase 1 shared reminder packet",
        "      - name: Self-test current Phase 1 closure validator",
    ),
}

FORBIDDEN_WORKFLOW_LINES = (
    "        run: python3 scripts/zigux/check-phase1-bench.py",
    "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    "        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            count = text.count(marker)
            if count != 1:
                failures.append(
                    f"{relative_path.as_posix()}:expected_once:actual_count={count}:{marker}"
                )

    workflow_text = read_text(root, WORKFLOW_REL)
    for line in FORBIDDEN_WORKFLOW_LINES:
        count = sum(1 for current in workflow_text.splitlines() if current == line)
        if count != 0:
            failures.append(f"{WORKFLOW_REL.as_posix()}:forbidden_line:actual_count={count}:{line}")

    return failures


def build_sample_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")


def remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    text = read_text(root, relative_path)
    write_text(root, relative_path, text.replace(marker + "\n", "", 1))


def add_forbidden_workflow_line(root: Path, line: str) -> None:
    text = read_text(root, WORKFLOW_REL)
    write_text(root, WORKFLOW_REL, text + line + "\n")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, object] | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", ("missing_file", relative_path)))

    for relative_path, markers in REQUIRED_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path.as_posix()}", ("remove", relative_path, marker)))

    for line in FORBIDDEN_WORKFLOW_LINES:
        cases.append((f"forbidden_workflow:{line}", ("forbidden", line)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-find-bit-bench-packet-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if mutation is not None:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove":
                    remove_marker(root, mutation[1], mutation[2])
                elif kind == "forbidden":
                    add_forbidden_workflow_line(root, mutation[1])

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print(f"self-test:{name}:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_FIND_BIT_BENCH_PACKET_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_BENCH_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test only")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_FIND_BIT_BENCH_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_FIND_BIT_BENCH_PACKET=pass")
    print(f"PHASE1_FIND_BIT_BENCH_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
