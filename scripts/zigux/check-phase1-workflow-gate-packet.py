#!/usr/bin/env python3
"""Guard the current Phase 1 workflow gate packet inside zigux-bootstrap."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_SEQUENCE = (
    "      - name: Self-test current Phase 1 route summary checker",
    "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "      - name: Check current Phase 1 route summary packet",
    "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "      - name: Self-test current Phase 1 bench checker",
    "        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "      - name: Self-test current Phase 1 shared reminder checker",
    "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "      - name: Check current Phase 1 shared reminder packet",
    "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "      - name: Self-test current Phase 1 closure validator",
    "        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "      - name: Check current Phase 1 closure packet",
    "        run: python3 scripts/zigux/validate-phase1-closure.py",
    "      - name: Run current Phase 1 shared tests-root smoke",
    "        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

FORBIDDEN_LINES = (
    "        run: python3 scripts/zigux/check-phase1-bench.py",
    "        run: python3 scripts/zigux/check-phase1-parity.py --self-test",
    "        run: python3 scripts/zigux/check-phase1-parity.py",
    "        run: python3 scripts/zigux/validate-phase1.py --self-test",
    "        run: python3 scripts/zigux/validate-phase1.py",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_workflow(root: Path) -> str:
    return (root / WORKFLOW_REL).read_text(encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    workflow_path = root / WORKFLOW_REL
    if not workflow_path.exists():
        return [f"missing_file:{WORKFLOW_REL.as_posix()}"]

    text = read_workflow(root)
    lines = text.splitlines()
    failures: list[str] = []

    last_index = -1
    for marker in REQUIRED_SEQUENCE:
        matches = [idx for idx, line in enumerate(lines) if line == marker]
        if len(matches) != 1:
            failures.append(
                f"workflow_marker:{marker}:expected=1:actual={len(matches)}"
            )
            continue
        index = matches[0]
        if index <= last_index:
            failures.append(
                f"workflow_order:{marker}:expected_after={last_index + 1}:actual={index + 1}"
            )
        last_index = index

    for marker in FORBIDDEN_LINES:
        count = sum(1 for line in lines if line == marker)
        if count != 0:
            failures.append(f"workflow_forbidden:{marker}:actual={count}")

    return failures


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_text(root, WORKFLOW_REL, "\n".join(REQUIRED_SEQUENCE) + "\n")


def remove_marker(root: Path, marker: str) -> None:
    path = root / WORKFLOW_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def duplicate_marker(root: Path, marker: str) -> None:
    path = root / WORKFLOW_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def insert_forbidden(root: Path, marker: str) -> None:
    path = root / WORKFLOW_REL
    text = path.read_text(encoding="utf-8")
    path.write_text(text + marker + "\n", encoding="utf-8")


def swap_adjacent(root: Path, first: str, second: str) -> None:
    path = root / WORKFLOW_REL
    lines = path.read_text(encoding="utf-8").splitlines()
    first_index = lines.index(first)
    second_index = lines.index(second)
    lines[first_index], lines[second_index] = lines[second_index], lines[first_index]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-workflow-gates-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1

    cases: list[tuple[str, object]] = [("success", None)]
    cases.append(("missing_file", ("missing_file",)))
    for marker in REQUIRED_SEQUENCE:
        cases.append((f"remove:{marker}", ("remove", marker)))
        cases.append((f"duplicate:{marker}", ("duplicate", marker)))
    cases.append(
        (
            "reorder:shared-reminder-before-bench",
            (
                "swap",
                "      - name: Self-test current Phase 1 bench checker",
                "      - name: Self-test current Phase 1 shared reminder checker",
            ),
        )
    )
    for marker in FORBIDDEN_LINES:
        cases.append((f"forbidden:{marker}", ("forbidden", marker)))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-workflow-gates-case-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / WORKFLOW_REL).unlink()
                elif kind == "remove":
                    remove_marker(root, mutation[1])
                elif kind == "duplicate":
                    duplicate_marker(root, mutation[1])
                elif kind == "forbidden":
                    insert_forbidden(root, mutation[1])
                elif kind == "swap":
                    swap_adjacent(root, mutation[1], mutation[2])
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

    print("PHASE1_WORKFLOW_GATE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_GATE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
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
        print("PHASE1_WORKFLOW_GATE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_WORKFLOW_GATE_PACKET=pass")
    print(f"PHASE1_WORKFLOW_GATE_PACKET_REQUIRED_MARKER_COUNT={len(REQUIRED_SEQUENCE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
