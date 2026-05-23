#!/usr/bin/env python3
"""Guard the current Phase 1 workflow-gate cluster across reminder surfaces."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

REQUIRED_FILES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase1-route-summary-counts.py",
    "scripts/zigux/check-phase1-bench.py",
    "scripts/zigux/check-phase1-shared-reminder-packet.py",
    "scripts/zigux/validate-phase1-closure.py",
    "zigux/tests/README.md",
    "zigux/tests/build.zig",
    "zigux/tests/phase1_host_tools_smoke.zig",
    ".github/workflows/zigux-bootstrap.yml",
)

MARKERS = {
    "Documentation/zigux/README.md": (
        "`python3 scripts/zigux/check-phase1-bench.py --self-test`",
        "`python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test`",
    ),
    "Documentation/zigux/phase1-closure.md": (
        "`PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`",
        "`PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
        "`PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    ),
    "Documentation/zigux/review-checklist.md": (
        "`scripts/zigux/check-phase1-bench.py`",
        "`scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet",
    ),
    "scripts/zigux/README.md": (
        "`python3 scripts/zigux/check-phase1-bench.py --self-test`",
        "`python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test`",
        "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "`scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py`",
    ),
    "scripts/zigux/check-phase1-route-summary-counts.py": (
        '"run: python3 scripts/zigux/check-phase1-bench.py --self-test",',
        '"run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",',
    ),
    "scripts/zigux/check-phase1-bench.py": (
        'print("PHASE1_BENCH_CHECK_SELF_TEST=pass")',
        'print("PHASE1_BENCH_CHECK=pass")',
    ),
    "scripts/zigux/check-phase1-shared-reminder-packet.py": (
        'print("PHASE1_SHARED_REMINDER_PACKET_SELF_TEST=pass")',
        'print("PHASE1_SHARED_REMINDER_PACKET=pass")',
    ),
    "scripts/zigux/validate-phase1-closure.py": (
        'print("PHASE1_CLOSURE_SELF_TEST=pass")',
        'print("PHASE1_CLOSURE_VALIDATION=pass")',
    ),
    "zigux/tests/README.md": (
        "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "`scripts/zigux/check-phase1-bench.py`",
        "`scripts/zigux/check-phase1-shared-reminder-packet.py`",
        "`scripts/zigux/validate-phase1-closure.py`",
    ),
    "zigux/tests/build.zig": (
        '.name = "phase1-host-tools-smoke",',
        '.root_source_file = b.path("phase1_host_tools_smoke.zig"),',
    ),
    "zigux/tests/phase1_host_tools_smoke.zig": (
        'test "phase1 host-tools smoke exercises live helper behavior"',
    ),
    ".github/workflows/zigux-bootstrap.yml": (
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
        "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
        "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
        "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "run: python3 scripts/zigux/validate-phase1-closure.py",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
}

WORKFLOW_ORDER = MARKERS[".github/workflows/zigux-bootstrap.yml"]

FORBIDDEN = {
    ".github/workflows/zigux-bootstrap.yml": (
        "run: python3 scripts/zigux/check-phase1-bench.py",
    ),
    "scripts/zigux/README.md": (
        "`python3 scripts/zigux/check-phase1-bench.py`",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            issues.append(f"missing_file:{relative_path}")
    if issues:
        return issues

    for relative_path, markers in MARKERS.items():
        text = read_text(root, relative_path)
        lines = text.splitlines()
        for marker in markers:
            count = sum(1 for line in lines if line.strip() == marker.strip())
            if count != 1:
                issues.append(f"{relative_path}:expected_once:actual={count}:{marker}")
        for marker in FORBIDDEN.get(relative_path, ()):
            count = sum(1 for line in lines if line.strip() == marker.strip())
            if count != 0:
                issues.append(f"{relative_path}:forbidden:actual={count}:{marker}")

    workflow = read_text(root, ".github/workflows/zigux-bootstrap.yml")
    positions = [workflow.find(marker) for marker in WORKFLOW_ORDER]
    if all(position != -1 for position in positions) and positions != sorted(positions):
        issues.append(".github/workflows/zigux-bootstrap.yml:workflow_order:out_of_order")
    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, "\n".join(MARKERS.get(relative_path, ())) + "\n")


def mutate_remove(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def mutate_append(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text + marker + "\n", encoding="utf-8")


def mutate_swap(root: Path) -> None:
    target = root / ".github/workflows/zigux-bootstrap.yml"
    first, second = WORKFLOW_ORDER[:2]
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(first + "\n" + second, second + "\n" + first, 1), encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, ...] | None]] = [("success", None)]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", ("missing_file", relative_path)))
    for relative_path, markers in MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path}", ("remove", relative_path, marker)))
            cases.append((f"duplicate_marker:{relative_path}", ("duplicate", relative_path, marker)))
    cases.append(("workflow_out_of_order", ("swap",)))
    cases.append(("forbidden_live_bench_run", ("append", ".github/workflows/zigux-bootstrap.yml", FORBIDDEN[".github/workflows/zigux-bootstrap.yml"][0])))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-workflow-gate-cluster-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation is not None:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove":
                    mutate_remove(root, mutation[1], mutation[2])
                elif kind == "duplicate":
                    mutate_duplicate(root, mutation[1], mutation[2])
                elif kind == "append":
                    mutate_append(root, mutation[1], mutation[2])
                elif kind == "swap":
                    mutate_swap(root)
            issues = collect_issues(root)
            if name == "success":
                if issues:
                    print("self-test:success:unexpected_failures")
                    for item in issues:
                        print(item)
                    return 1
            elif not issues:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_WORKFLOW_GATE_CLUSTER_SELF_TEST=pass")
    print(f"PHASE1_WORKFLOW_GATE_CLUSTER_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_WORKFLOW_GATE_CLUSTER=fail")
        for item in issues:
            print(item)
        return 1

    print("PHASE1_WORKFLOW_GATE_CLUSTER=pass")
    print(f"PHASE1_WORKFLOW_GATE_CLUSTER_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_WORKFLOW_GATE_CLUSTER_REQUIRED_MARKER_COUNT={sum(len(markers) for markers in MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
