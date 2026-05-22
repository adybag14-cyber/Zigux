#!/usr/bin/env python3
"""Guard the current Phase 1 bootstrap packet across reminder surfaces and workflow order."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

DOCS_ROOT_REL = Path("Documentation/zigux/README.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
LANE_SEQUENCING_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_README_REL = Path("zigux/tests/README.md")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

DIRECT_OWNER_CHECKER_REL = Path("scripts/zigux/check-phase1-direct-owner-markers.py")
STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
ROUTE_SUMMARY_CHECKER_REL = Path("scripts/zigux/check-phase1-route-summary-counts.py")
BOOTSTRAP_PACKET_CHECKER_REL = Path("scripts/zigux/check-phase1-bootstrap-packet-alignment.py")
BENCH_CHECKER_REL = Path("scripts/zigux/check-phase1-bench.py")
SHARED_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase1-shared-reminder-packet.py")
CLOSURE_VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")

REQUIRED_FILES = (
    DOCS_ROOT_REL,
    PHASE1_CLOSURE_REL,
    LANE_SEQUENCING_REL,
    REVIEW_CHECKLIST_REL,
    SCRIPTS_README_REL,
    TESTS_README_REL,
    WORKFLOW_REL,
    DIRECT_OWNER_CHECKER_REL,
    STRING_REVIEW_CHECKER_REL,
    ROUTE_SUMMARY_CHECKER_REL,
    BOOTSTRAP_PACKET_CHECKER_REL,
    BENCH_CHECKER_REL,
    SHARED_REMINDER_CHECKER_REL,
    CLOSURE_VALIDATOR_REL,
)

WORKFLOW_PACKET_LINES = (
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "run: python3 scripts/zigux/validate-phase1-closure.py",
    "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
)

OPTIONAL_WORKFLOW_PACKET_LINES = (
    "run: python3 scripts/zigux/check-phase1-bootstrap-packet-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase1-bootstrap-packet-alignment.py",
)

FORBIDDEN_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase1-bench.py",
)

REQUIRED_MARKERS = {
    DOCS_ROOT_REL: (
        "* `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the bounded current reminder checks, while the live checker routes guard the shipped Phase 1 packet without widening it back into the older closure-side or installer-companion stack.",
    ),
    PHASE1_CLOSURE_REL: (
        "The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet: `.github/workflows/zigux-bootstrap.yml` self-tests the directly readable Phase 1 direct-owner, string-review, route-summary, bench, shared-reminder, and closure-validator checks, replays the route-summary, direct-owner, string-review, shared-reminder, closure-validator, and shared tests-root smoke steps on current `master`, and currently keeps the bench checker at self-test coverage only.",
        "- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`",
    ),
    LANE_SEQUENCING_REL: (
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ACTIVE_PACKET=Documentation/zigux/README.md,Documentation/zigux/phase1-closure.md,Documentation/zigux/review-checklist.md,zigux/tests/README.md,scripts/zigux/README.md,scripts/zigux/validate-phase1-closure.py,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py`",
    ),
    REVIEW_CHECKLIST_REL: (
        "* if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, keep `zigux/Makefile` explicit as current repo evidence for the returned non-Phase-1 route families, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?",
    ),
    SCRIPTS_README_REL: (
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `scripts/zigux/check-phase1-shared-reminder-packet.py`, and `scripts/zigux/validate-phase1-closure.py` keep the shipped string-review, direct-owner, bench, shared-reminder, and closure-validator packet explicit from the scripts root",
    ),
    TESTS_README_REL: (
        "- `.github/workflows/zigux-bootstrap.yml`",
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    ),
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = sum(1 for current in text.splitlines() if current.strip() == needle)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def collect_workflow_order_failures(text: str) -> list[str]:
    failures: list[str] = []
    position_map: dict[str, int] = {}
    for line in WORKFLOW_PACKET_LINES:
        count = sum(1 for current in text.splitlines() if current.strip() == line)
        if count != 1:
            failures.append(f"workflow:{line}:expected=1:actual={count}")
            continue
        position_map[line] = text.index(line)
    if failures:
        return failures
    positions = [position_map[line] for line in WORKFLOW_PACKET_LINES]
    if positions != sorted(positions):
        return ["workflow:phase1_packet_order:expected=strictly_increasing:actual=out_of_order"]

    optional_counts = {
        line: sum(1 for current in text.splitlines() if current.strip() == line)
        for line in OPTIONAL_WORKFLOW_PACKET_LINES
    }
    present_optional = [line for line, count in optional_counts.items() if count]
    if not present_optional:
        return failures
    if len(present_optional) != len(OPTIONAL_WORKFLOW_PACKET_LINES):
        for line in OPTIONAL_WORKFLOW_PACKET_LINES:
            count = optional_counts[line]
            if count != 1:
                failures.append(f"workflow:{line}:expected_optional_pair_member=1:actual={count}")
        return failures

    optional_positions = [text.index(line) for line in OPTIONAL_WORKFLOW_PACKET_LINES]
    if optional_positions != sorted(optional_positions):
        failures.append("workflow:phase1_bootstrap_optional_pair:expected=strictly_increasing:actual=out_of_order")
        return failures

    route_summary_check_pos = position_map["run: python3 scripts/zigux/check-phase1-route-summary-counts.py"]
    bench_self_test_pos = position_map["run: python3 scripts/zigux/check-phase1-bench.py --self-test"]
    if not all(route_summary_check_pos < pos < bench_self_test_pos for pos in optional_positions):
        failures.append(
            "workflow:phase1_bootstrap_optional_pair:expected=between_route_summary_check_and_bench_self_test:actual=outside_slot"
        )
    return failures


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).is_file():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    for relative_path, markers in REQUIRED_MARKERS.items():
        text = load_text(root, relative_path)
        for marker in markers:
            failures.extend(
                require_exact_occurrence(
                    text,
                    f"{relative_path.as_posix()}:{marker}",
                    marker,
                )
            )

    workflow_text = load_text(root, WORKFLOW_REL)
    failures.extend(collect_workflow_order_failures(workflow_text))
    for line in FORBIDDEN_WORKFLOW_LINES:
        failures.extend(
            require_absent_occurrence(
                workflow_text,
                f"{WORKFLOW_REL.as_posix()}:{line}",
                line,
            )
        )

    return failures


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    for relative_path in REQUIRED_FILES:
        write_text(root, relative_path, "sample\n")

    for relative_path, markers in REQUIRED_MARKERS.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")

    write_text(root, WORKFLOW_REL, "\n".join(WORKFLOW_PACKET_LINES) + "\n")


def write_sample_root(destination: Path) -> None:
    if destination.exists() and any(destination.iterdir()):
        raise SystemExit(f"sample root destination must be empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    build_sample_repo(destination)


def remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    text = load_text(root, relative_path)
    write_text(root, relative_path, text.replace(marker + "\n", "", 1))


def duplicate_marker(root: Path, relative_path: Path, marker: str) -> None:
    text = load_text(root, relative_path)
    write_text(root, relative_path, text.replace(marker, marker + "\n" + marker, 1))


def reorder_workflow(root: Path) -> None:
    lines = list(WORKFLOW_PACKET_LINES)
    lines[0], lines[1] = lines[1], lines[0]
    write_text(root, WORKFLOW_REL, "\n".join(lines) + "\n")


def add_forbidden_workflow_line(root: Path) -> None:
    text = load_text(root, WORKFLOW_REL)
    write_text(root, WORKFLOW_REL, text + FORBIDDEN_WORKFLOW_LINES[0] + "\n")


def add_optional_workflow_pair(root: Path, mode: str) -> None:
    lines = load_text(root, WORKFLOW_REL).splitlines()
    bench_index = lines.index("run: python3 scripts/zigux/check-phase1-bench.py --self-test")
    pair = list(OPTIONAL_WORKFLOW_PACKET_LINES)
    if mode == "reversed":
        pair = list(reversed(pair))
    elif mode == "self_only":
        pair = [OPTIONAL_WORKFLOW_PACKET_LINES[0]]
    elif mode == "check_only":
        pair = [OPTIONAL_WORKFLOW_PACKET_LINES[1]]
    if mode == "after_bench":
        insert_index = bench_index + 1
    else:
        insert_index = bench_index
    lines[insert_index:insert_index] = pair
    write_text(root, WORKFLOW_REL, "\n".join(lines) + "\n")


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", ("missing_file", relative_path)))

    for relative_path, markers in REQUIRED_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path.as_posix()}", ("remove", relative_path, marker)))
            cases.append((f"duplicate_marker:{relative_path.as_posix()}", ("duplicate", relative_path, marker)))

    for line in WORKFLOW_PACKET_LINES:
        cases.append((f"missing_workflow:{line}", ("remove", WORKFLOW_REL, line)))
        cases.append((f"duplicate_workflow:{line}", ("duplicate", WORKFLOW_REL, line)))

    cases.append(("workflow_reordered", ("reorder_workflow",)))
    cases.append(("workflow_forbidden_line", ("forbidden_workflow",)))
    cases.append(("workflow_optional_pair_present", ("optional_workflow", "normal"),))
    cases.append(("workflow_optional_pair_reversed", ("optional_workflow", "reversed"),))
    cases.append(("workflow_optional_pair_after_bench", ("optional_workflow", "after_bench"),))
    cases.append(("workflow_optional_pair_self_only", ("optional_workflow", "self_only"),))
    cases.append(("workflow_optional_pair_check_only", ("optional_workflow", "check_only"),))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-bootstrap-packet-") as tmpdir:
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
                elif kind == "reorder_workflow":
                    reorder_workflow(root)
                elif kind == "forbidden_workflow":
                    add_forbidden_workflow_line(root)
                elif kind == "optional_workflow":
                    add_optional_workflow_pair(root, mutation[1])
            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("self-test:success:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif name == "workflow_optional_pair_present":
                if failures:
                    print("self-test:workflow_optional_pair_present:unexpected_failures")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument(
        "--write-sample-root",
        help="write a current-like sample repo tree to this empty directory and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        destination = Path(args.write_sample_root).resolve()
        write_sample_root(destination)
        print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SAMPLE_ROOT={destination}")
        print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_SAMPLE_FILE_COUNT={len(REQUIRED_FILES)}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_BOOTSTRAP_PACKET_ALIGNMENT=pass")
    print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_REQUIRED_WORKFLOW_STEP_COUNT={len(WORKFLOW_PACKET_LINES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
