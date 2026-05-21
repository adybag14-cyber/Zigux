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

EXACT_MARKERS = {
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
        "\"run: python3 scripts/zigux/check-phase1-bench.py --self-test\",",
        "\"run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\",",
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

WORKFLOW_ORDER = (
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

FORBIDDEN_EXACT_MARKERS = {
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


def collect_missing_files(root: Path) -> list[str]:
    return [relative_path for relative_path in REQUIRED_FILES if not (root / relative_path).is_file()]


def collect_exact_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    for marker in markers:
        count = sum(1 for line in lines if line.strip() == marker.strip())
        if count != 1:
            issues.append(f"{label}:expected_once:actual={count}:{marker}")
    return issues


def collect_forbidden_markers(text: str, label: str, markers: tuple[str, ...]) -> list[str]:
    issues: list[str] = []
    lines = text.splitlines()
    for marker in markers:
        count = sum(1 for line in lines if line.strip() == marker.strip())
        if count != 0:
            issues.append(f"{label}:forbidden:actual={count}:{marker}")
    return issues


def collect_workflow_order(text: str) -> list[str]:
    issues: list[str] = []
    positions: list[int] = []
    for marker in WORKFLOW_ORDER:
        position = text.find(marker)
        if position == -1:
            return []
        positions.append(position)
    if positions != sorted(positions):
        issues.append(".github/workflows/zigux-bootstrap.yml:workflow_order:out_of_order")
    return issues


def collect_missing_markers(root: Path) -> list[str]:
    issues = [f"missing_file:{relative_path}" for relative_path in collect_missing_files(root)]
    if issues:
        return issues

    for relative_path, markers in EXACT_MARKERS.items():
        text = read_text(root, relative_path)
        issues.extend(collect_exact_markers(text, relative_path, markers))
        issues.extend(
            collect_forbidden_markers(
                text,
                relative_path,
                FORBIDDEN_EXACT_MARKERS.get(relative_path, ()),
            )
        )

    workflow_text = read_text(root, ".github/workflows/zigux-bootstrap.yml")
    issues.extend(collect_workflow_order(workflow_text))
    return issues


def write_text(root: Path, relative_path: str, content: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        markers = EXACT_MARKERS.get(relative_path, ())
        write_text(root, relative_path, "\n".join(markers) + ("\n" if markers else ""))


def mutate_remove_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")


def mutate_duplicate_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text.replace(marker, marker + "\n" + marker, 1), encoding="utf-8")


def mutate_append_marker(root: Path, relative_path: str, marker: str) -> None:
    target = root / relative_path
    text = target.read_text(encoding="utf-8")
    target.write_text(text + marker + "\n", encoding="utf-8")


def mutate_reverse_workflow_pair(root: Path) -> None:
    target = root / ".github/workflows/zigux-bootstrap.yml"
    text = target.read_text(encoding="utf-8")
    first = WORKFLOW_ORDER[0]
    second = WORKFLOW_ORDER[1]
    swapped = text.replace(first + "\n" + second, second + "\n" + first, 1)
    target.write_text(swapped, encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, object]] = [("success", None)]
    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path}", ("missing_file", relative_path)))
    for relative_path, markers in EXACT_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path}", ("remove", relative_path, marker)))
            cases.append((f"duplicate_marker:{relative_path}", ("duplicate", relative_path, marker)))
    cases.append(("workflow_out_of_order", ("workflow_swap",)))
    cases.append(
        (
            "forbidden_live_bench_run",
            ("forbidden", ".github/workflows/zigux-bootstrap.yml", FORBIDDEN_EXACT_MARKERS[".github/workflows/zigux-bootstrap.yml"][0]),
        )
    )

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-workflow-gate-cluster-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation is not None:
                kind = mutation[0]
                if kind == "missing_file":
                    (root / mutation[1]).unlink()
                elif kind == "remove":
                    mutate_remove_marker(root, mutation[1], mutation[2])
                elif kind == "duplicate":
                    mutate_duplicate_marker(root, mutation[1], mutation[2])
                elif kind == "forbidden":
                    mutate_append_marker(root, mutation[1], mutation[2])
                elif kind == "workflow_swap":
                    mutate_reverse_workflow_pair(root)
            issues = collect_missing_markers(root)
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

    issues = collect_missing_markers(repo_root(args.root))
    if issues:
        print("PHASE1_WORKFLOW_GATE_CLUSTER=fail")
        for item in issues:
            print(item)
        return 1

    print("PHASE1_WORKFLOW_GATE_CLUSTER=pass")
    print(f"PHASE1_WORKFLOW_GATE_CLUSTER_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_WORKFLOW_GATE_CLUSTER_REQUIRED_MARKER_COUNT="
        f"{sum(len(markers) for markers in EXACT_MARKERS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
