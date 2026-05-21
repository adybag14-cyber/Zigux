#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
PHASE1_BENCH_REL = Path("scripts/zigux/check-phase1-bench.py")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

BENCH_GUARD_MARKER = (
    "`PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes "
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 "
    "and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM "
    "when the broader expectations packet returns`"
)
WORKFLOW_POSTURE_MARKER = "and currently keeps the bench checker at self-test coverage only."
BENCH_REQUIRED_MARKERS = (
    '"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,',
    '"PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,',
    'try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}\\n", .{find_bit_result.checksum});',
    'try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\\n", .{find_bit_edge_result.checksum});',
    "FIND_BIT_REQUIRED_EXACT_CHECKSUMS = {",
)
WORKFLOW_REQUIRED_MARKERS = (
    "- name: Self-test current Phase 1 bench checker",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "- name: Check current Phase 1 shared reminder packet",
    "- name: Check current Phase 1 closure packet",
)
WORKFLOW_FORBIDDEN_MARKERS = (
    "      - name: Check current Phase 1 bench checker\n        run: python3 scripts/zigux/check-phase1-bench.py\n",
)


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def require_exact_once(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected_once:actual_count={count}:{marker}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in (PHASE1_CLOSURE_REL, PHASE1_BENCH_REL, WORKFLOW_REL):
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    closure_text = read_text(root, PHASE1_CLOSURE_REL)
    failures.extend(
        require_exact_once(
            closure_text,
            f"{PHASE1_CLOSURE_REL.as_posix()}:find_bit_bench_guard",
            BENCH_GUARD_MARKER,
        )
    )
    failures.extend(
        require_exact_once(
            closure_text,
            f"{PHASE1_CLOSURE_REL.as_posix()}:workflow_posture",
            WORKFLOW_POSTURE_MARKER,
        )
    )

    bench_text = read_text(root, PHASE1_BENCH_REL)
    for marker in BENCH_REQUIRED_MARKERS:
        failures.extend(
            require_exact_once(
                bench_text,
                f"{PHASE1_BENCH_REL.as_posix()}:required_marker",
                marker,
            )
        )

    workflow_text = read_text(root, WORKFLOW_REL)
    for marker in WORKFLOW_REQUIRED_MARKERS:
        failures.extend(
            require_exact_once(
                workflow_text,
                f"{WORKFLOW_REL.as_posix()}:required_marker",
                marker,
            )
        )
    for marker in WORKFLOW_FORBIDDEN_MARKERS:
        count = workflow_text.count(marker)
        if count:
            failures.append(
                f"{WORKFLOW_REL.as_posix()}:forbidden_marker:actual_count={count}:{marker}"
            )

    return failures


def build_closure_note() -> str:
    return f"""# Phase 1 Closure

This note keeps the shared Phase 1 closure packet explicit.

The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet and currently keeps the bench checker at self-test coverage only.

- {BENCH_GUARD_MARKER}
"""


def build_bench_checker() -> str:
    return """#!/usr/bin/env python3
EXPECTED_ITERATIONS = {
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS": 20000,
}
EXPECTED_CHECKSUMS = [
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
]
FIND_BIT_REQUIRED_EXACT_CHECKSUMS = {
    "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
}
try stdout_writer.interface.print("PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM={d}\\n", .{find_bit_result.checksum});
try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\\n", .{find_bit_edge_result.checksum});
"""


def build_workflow() -> str:
    return """name: zigux-bootstrap
jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Self-test current Phase 1 bench checker
        run: python3 scripts/zigux/check-phase1-bench.py --self-test
      - name: Check current Phase 1 shared reminder packet
        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py
      - name: Check current Phase 1 closure packet
        run: python3 scripts/zigux/validate-phase1-closure.py
"""


def write_sample_root(root: Path) -> None:
    write_text(root / PHASE1_CLOSURE_REL, build_closure_note())
    write_text(root / PHASE1_BENCH_REL, build_bench_checker())
    write_text(root / WORKFLOW_REL, build_workflow())


def replace_once(text: str, old: str, new: str = "") -> str:
    if old not in text:
        raise AssertionError(f"marker not found for self-test mutation: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1_find_bit_bench_guard_") as tmpdir:
        root = Path(tmpdir)
        write_sample_root(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        case_count += 1

        write_text(
            root / PHASE1_CLOSURE_REL,
            replace_once(read_text(root, PHASE1_CLOSURE_REL), BENCH_GUARD_MARKER + "\n"),
        )
        failures = collect_failures(root)
        expected = [
            f"{PHASE1_CLOSURE_REL.as_posix()}:find_bit_bench_guard:expected_once:actual_count=0:{BENCH_GUARD_MARKER}"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected missing guard failure: {failures}")
        case_count += 1
        write_sample_root(root)

        write_text(
            root / PHASE1_CLOSURE_REL,
            replace_once(read_text(root, PHASE1_CLOSURE_REL), WORKFLOW_POSTURE_MARKER, "drifted workflow wording"),
        )
        failures = collect_failures(root)
        expected = [
            f"{PHASE1_CLOSURE_REL.as_posix()}:workflow_posture:expected_once:actual_count=0:{WORKFLOW_POSTURE_MARKER}"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected workflow posture failure: {failures}")
        case_count += 1
        write_sample_root(root)

        write_text(
            root / PHASE1_BENCH_REL,
            replace_once(
                read_text(root, PHASE1_BENCH_REL),
                '"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,',
                '"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 10000,',
            ),
        )
        failures = collect_failures(root)
        expected = [
            f'{PHASE1_BENCH_REL.as_posix()}:required_marker:expected_once:actual_count=0:"PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS": 20000,'
        ]
        if failures != expected:
            raise AssertionError(f"unexpected bench-iteration failure: {failures}")
        case_count += 1
        write_sample_root(root)

        write_text(
            root / PHASE1_BENCH_REL,
            replace_once(
                read_text(root, PHASE1_BENCH_REL),
                'try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={d}\\n", .{find_bit_edge_result.checksum});\n',
            ),
        )
        failures = collect_failures(root)
        expected = [
            f'{PHASE1_BENCH_REL.as_posix()}:required_marker:expected_once:actual_count=0:try stdout_writer.interface.print("PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM={{d}}\\n", .{{find_bit_edge_result.checksum}});'
        ]
        if failures != expected:
            raise AssertionError(f"unexpected bench-checksum failure: {failures}")
        case_count += 1
        write_sample_root(root)

        write_text(
            root / WORKFLOW_REL,
            replace_once(read_text(root, WORKFLOW_REL), "- name: Self-test current Phase 1 bench checker\n"),
        )
        failures = collect_failures(root)
        expected = [
            f"{WORKFLOW_REL.as_posix()}:required_marker:expected_once:actual_count=0:- name: Self-test current Phase 1 bench checker"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected workflow self-test failure: {failures}")
        case_count += 1
        write_sample_root(root)

        write_text(
            root / WORKFLOW_REL,
            read_text(root, WORKFLOW_REL)
            + "      - name: Check current Phase 1 bench checker\n"
            + "        run: python3 scripts/zigux/check-phase1-bench.py\n",
        )
        failures = collect_failures(root)
        expected = [
            f"{WORKFLOW_REL.as_posix()}:forbidden_marker:actual_count=1:      - name: Check current Phase 1 bench checker\n        run: python3 scripts/zigux/check-phase1-bench.py\n",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected forbidden workflow failure: {failures}")
        case_count += 1

    print("PHASE1_FIND_BIT_BENCH_GUARD_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_FIND_BIT_BENCH_GUARD_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 1 closure note's find_bit bench guard stays aligned with the shipped bench checker and workflow posture."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE1_FIND_BIT_BENCH_GUARD_ALIGNMENT_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_FIND_BIT_BENCH_GUARD_ALIGNMENT=pass")
    print("PHASE1_FIND_BIT_BENCH_GUARD_ALIGNMENT_REQUIRED_FILE_COUNT=3")
    print("PHASE1_FIND_BIT_BENCH_GUARD_ALIGNMENT_REQUIRED_BENCH_MARKER_COUNT=5")
    print("PHASE1_FIND_BIT_BENCH_GUARD_ALIGNMENT_REQUIRED_WORKFLOW_MARKER_COUNT=4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
