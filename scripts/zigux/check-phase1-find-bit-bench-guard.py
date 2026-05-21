#!/usr/bin/env python3
"""Guard the current Phase 1 find_bit bench contract across closure and helper surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "scripts/zigux/check-phase1-bench.py",
)

EXACT_LINE_MARKERS = {
    "Documentation/zigux/phase1-closure.md": (
        "- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
    ),
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md": (
        "- `PHASE1_FIND_BIT_DIRECT_OWNER=find_bit helper-local same-word start-mask, head-word and tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), and findLastBit() byte-clump and backward-scan coverage, underscore-alias and Linux-style alias coverage including the shipped find_first_andnot_bit(), find_next_andnot_bit(), _find_first_andnot_bit(), and _find_next_andnot_bit() entry points, and tail-word skip anchors plus the committed tail-clamped and tail-inclusive-boundary find_bit replay fields already preserved in zigux/tests/fixtures/phase1_helpers.json`",
        "- `PHASE1_FIND_BIT_NEXT_SAFE_STEP=find_bit reopens only for direct-anchor drift inside same-word start-mask, inclusive-boundary, zero-window, zero-sized short-circuit, past-nbits, clump8, getValue8(), findLastBit(), underscore-alias or Linux-style alias coverage including the shipped andnot scan entry points, or tail-word skip anchors, or for committed tail-clamped or tail-inclusive-boundary replay drift; do not reopen older saved validator cues or neighboring helper families`",
    ),
    "zigux/tests/fixtures/phase1_helper_manifest.json": (
        "\"andnot_scan_entrypoint_contract\": \"The shipped public, Linux-style, and underscore andnot scan entry points stay owned by the direct find_bit packet instead of being left implicit under generic alias wording.\",",
        "\"tail_inclusive_boundary_fixture_keys\": [",
        "\"tail_inclusive_boundary_next\",",
        "\"tail_inclusive_boundary_zero\",",
        "\"tail_inclusive_boundary_and\"",
    ),
    "scripts/zigux/check-phase1-bench.py": (
        "\"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS\": 20000,",
        "\"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS\": 20000,",
        "FIND_BIT_REQUIRED_EXACT_CHECKSUMS = {",
        "\"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\",",
        "\"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM\",",
        "\"boundary_next_and_bit\": \"checksum +%= @intCast(find_bit.findNextAndBit(&boundary_set, &boundary_set, head_nbits, boundary));\",",
        "\"tail_last_bit\": \"checksum +%= @intCast(find_bit.findLastBit(&tail_set, tail_nbits));\",",
        "print(\"PHASE1_BENCH_CHECK_SELF_TEST=pass\")",
    ),
}

FORBIDDEN_LINE_MARKERS = {
    "Documentation/zigux/phase1-closure.md": (
        "- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=10000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=10000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path}")
    if failures:
        return failures

    for relative_path, markers in EXACT_LINE_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_exact_line(text, f"{relative_path}:{marker}", marker))

    for relative_path, markers in FORBIDDEN_LINE_MARKERS.items():
        text = read_text(root, relative_path)
        for marker in markers:
            failures.extend(require_absent_line(text, f"{relative_path}:{marker}", marker))

    return failures


def write_text(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        lines = list(EXACT_LINE_MARKERS.get(relative_path, ()))
        write_text(root, relative_path, "\n".join(lines) + ("\n" if lines else ""))


def remove_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            del lines[idx]
            path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
            return
    raise ValueError(f"missing marker: {relative_path}: {marker}")


def duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == marker.strip():
            lines.insert(idx + 1, line)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(f"missing marker: {relative_path}: {marker}")


def add_forbidden(root: Path, relative_path: str, marker: str) -> None:
    path = root / relative_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text + marker + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = [("success", None)]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", ("missing_file", relative_path)))
    for relative_path, markers in EXACT_LINE_MARKERS.items():
        for marker in markers:
            cases.append((f"remove:{relative_path}", ("remove", relative_path, marker)))
            cases.append((f"duplicate:{relative_path}", ("duplicate", relative_path, marker)))
    for relative_path, markers in FORBIDDEN_LINE_MARKERS.items():
        for marker in markers:
            cases.append((f"forbidden:{relative_path}", ("forbidden", relative_path, marker)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-find-bit-bench-guard-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove":
                    remove_marker(root, mutation[1], mutation[2])
                elif kind == "duplicate":
                    duplicate_marker(root, mutation[1], mutation[2])
                elif kind == "forbidden":
                    add_forbidden(root, mutation[1], mutation[2])
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_FIND_BIT_BENCH_GUARD_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_BENCH_GUARD_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_FIND_BIT_BENCH_GUARD=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_FIND_BIT_BENCH_GUARD=pass")
    print(f"PHASE1_FIND_BIT_BENCH_GUARD_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_FIND_BIT_BENCH_GUARD_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_LINE_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
