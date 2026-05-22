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

WORKFLOW_PACKET_STEPS = (
    (
        "Self-test current Phase 1 direct-owner checker",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    ),
    (
        "Check current Phase 1 direct-owner markers",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    ),
    (
        "Self-test current Phase 1 string review checker",
        "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    ),
    (
        "Check current Phase 1 string review packet",
        "python3 scripts/zigux/check-phase1-string-review-packet.py",
    ),
    (
        "Self-test current Phase 1 route summary checker",
        "python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    ),
    (
        "Check current Phase 1 route summary packet",
        "python3 scripts/zigux/check-phase1-route-summary-counts.py",
    ),
    (
        "Self-test current Phase 1 bench checker",
        "python3 scripts/zigux/check-phase1-bench.py --self-test",
    ),
    (
        "Self-test current Phase 1 shared reminder checker",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    ),
    (
        "Check current Phase 1 shared reminder packet",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    ),
    (
        "Self-test current Phase 1 closure validator",
        "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    ),
    (
        "Validate current Phase 1 closure packet",
        "python3 scripts/zigux/validate-phase1-closure.py",
    ),
    (
        "Run current Phase 1 shared tests-root smoke",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
)

OPTIONAL_WORKFLOW_PACKET_STEPS = (
    (
        "Self-test current Phase 1 bootstrap packet alignment checker",
        "python3 scripts/zigux/check-phase1-bootstrap-packet-alignment.py --self-test",
    ),
    (
        "Check current Phase 1 bootstrap packet alignment",
        "python3 scripts/zigux/check-phase1-bootstrap-packet-alignment.py",
    ),
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
        "- `PHASE1_DIRECT_OWNER_SHARED_REMINDER_ROUTE_SPLIT=Documentation/zigux/README.md, Documentation/zigux/review-checklist.md, zigux/tests/README.md, and scripts/zigux/README.md now all carry the shipped bench-checker wording, while Documentation/zigux/phase1-closure.md plus scripts/zigux/validate-phase1-closure.py keep the restored closure-side packet explicit and the broader installer-backed, validator-first, bench-route, and replay names remain historical packet members until direct current-master rereads restore them`",
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


def workflow_name_line(step_name: str) -> str:
    return f"- name: {step_name}"


def workflow_run_line(run_command: str) -> str:
    return f"run: {run_command}"


def workflow_step_block(step_name: str, run_command: str) -> str:
    return f"      - name: {step_name}\n        run: {run_command}"


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing text to replace: {old}")
    return text.replace(old, new, 1)


def collect_workflow_order_failures(text: str) -> list[str]:
    failures: list[str] = []
    position_map: dict[str, int] = {}
    for step_name, run_command in WORKFLOW_PACKET_STEPS:
        name_line = workflow_name_line(step_name)
        run_line = workflow_run_line(run_command)
        block = workflow_step_block(step_name, run_command)
        name_count = sum(1 for current in text.splitlines() if current.strip() == name_line)
        if name_count != 1:
            failures.append(f"workflow_step:{step_name}:expected=1:actual={name_count}")
        run_count = sum(1 for current in text.splitlines() if current.strip() == run_line)
        if run_count != 1:
            failures.append(f"workflow_run:{run_command}:expected=1:actual={run_count}")
        block_count = text.count(block)
        if block_count != 1:
            failures.append(f"workflow_pair:{step_name}:expected=1:actual={block_count}")
            continue
        block_position = text.index(block)
        position_map[step_name] = block_position
    if failures:
        return failures

    positions = [position_map[step_name] for step_name, _ in WORKFLOW_PACKET_STEPS]
    if positions != sorted(positions):
        return ["workflow:phase1_packet_order:expected=strictly_increasing:actual=out_of_order"]

    optional_counts = {}
    optional_pair_counts = {}
    optional_positions: list[int] = []
    for step_name, run_command in OPTIONAL_WORKFLOW_PACKET_STEPS:
        name_line = workflow_name_line(step_name)
        run_line = workflow_run_line(run_command)
        optional_counts[step_name] = (
            sum(1 for current in text.splitlines() if current.strip() == name_line),
            sum(1 for current in text.splitlines() if current.strip() == run_line),
        )
        pair_count = text.count(workflow_step_block(step_name, run_command))
        optional_pair_counts[step_name] = pair_count
        if pair_count == 1:
            optional_positions.append(text.index(workflow_step_block(step_name, run_command)))
    present_optional = [
        step_name
        for step_name, counts in optional_counts.items()
        if counts != (0, 0) or optional_pair_counts[step_name] != 0
    ]
    if not present_optional:
        return failures
    if len(present_optional) != len(OPTIONAL_WORKFLOW_PACKET_STEPS):
        for step_name, run_command in OPTIONAL_WORKFLOW_PACKET_STEPS:
            name_count, run_count = optional_counts[step_name]
            pair_count = optional_pair_counts[step_name]
            if name_count != 1:
                failures.append(f"workflow_optional_step:{step_name}:expected=1:actual={name_count}")
            if run_count != 1:
                failures.append(f"workflow_optional_run:{run_command}:expected=1:actual={run_count}")
            if pair_count != 1:
                failures.append(f"workflow_optional_pair:{step_name}:expected=1:actual={pair_count}")
        return failures

    optional_pair_failures = []
    for step_name, run_command in OPTIONAL_WORKFLOW_PACKET_STEPS:
        name_count, run_count = optional_counts[step_name]
        pair_count = optional_pair_counts[step_name]
        if name_count != 1:
            optional_pair_failures.append(f"workflow_optional_step:{step_name}:expected=1:actual={name_count}")
        if run_count != 1:
            optional_pair_failures.append(f"workflow_optional_run:{run_command}:expected=1:actual={run_count}")
        if pair_count != 1:
            optional_pair_failures.append(f"workflow_optional_pair:{step_name}:expected=1:actual={pair_count}")
    if optional_pair_failures:
        failures.extend(optional_pair_failures)
        return failures

    if optional_positions != sorted(optional_positions):
        failures.append("workflow:phase1_bootstrap_optional_pair:expected=strictly_increasing:actual=out_of_order")
        return failures

    route_summary_check_pos = position_map["Check current Phase 1 route summary packet"]
    bench_self_test_pos = position_map["Self-test current Phase 1 bench checker"]
    if not all(route_summary_check_pos < pos < bench_self_test_pos for pos in optional_positions):
        failures.append(
            "workflow:phase1_bootstrap_optional_pair:expected=between_route_summary_check_and_bench_self_test:actual=outside_slot"
        )
        return failures

    optional_pair_block = "\n".join(
        workflow_step_block(step_name, run_command)
        for step_name, run_command in OPTIONAL_WORKFLOW_PACKET_STEPS
    )
    if text.count(optional_pair_block) != 1:
        failures.append(
            "workflow:phase1_bootstrap_optional_pair:expected=adjacent_self_test_then_check:actual=split_or_misordered"
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

    write_text(
        root,
        WORKFLOW_REL,
        "\n".join(workflow_step_block(step_name, run_command) for step_name, run_command in WORKFLOW_PACKET_STEPS) + "\n",
    )


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
    steps = list(WORKFLOW_PACKET_STEPS)
    steps[0], steps[1] = steps[1], steps[0]
    write_text(
        root,
        WORKFLOW_REL,
        "\n".join(workflow_step_block(step_name, run_command) for step_name, run_command in steps) + "\n",
    )


def add_forbidden_workflow_line(root: Path) -> None:
    text = load_text(root, WORKFLOW_REL)
    write_text(root, WORKFLOW_REL, text + "        " + FORBIDDEN_WORKFLOW_LINES[0] + "\n")


def add_optional_workflow_pair(root: Path, mode: str) -> None:
    blocks = [workflow_step_block(step_name, run_command) for step_name, run_command in WORKFLOW_PACKET_STEPS]
    bench_block = workflow_step_block(*WORKFLOW_PACKET_STEPS[6])
    bench_index = blocks.index(bench_block)
    pair_blocks = [workflow_step_block(step_name, run_command) for step_name, run_command in OPTIONAL_WORKFLOW_PACKET_STEPS]
    if mode == "reversed":
        pair_blocks = list(reversed(pair_blocks))
    elif mode == "self_only":
        pair_blocks = [pair_blocks[0]]
    elif mode == "check_only":
        pair_blocks = [pair_blocks[1]]
    elif mode == "split":
        pair_blocks = [
            pair_blocks[0],
            "      - name: Split current Phase 1 bootstrap packet spacer\n        run: true",
            pair_blocks[1],
        ]
    insert_index = bench_index + 1 if mode == "after_bench" else bench_index
    blocks[insert_index:insert_index] = pair_blocks
    write_text(root, WORKFLOW_REL, "\n".join(blocks) + "\n")


def rename_workflow_step(root: Path, original_name: str, replacement_name: str) -> None:
    text = load_text(root, WORKFLOW_REL)
    write_text(root, WORKFLOW_REL, replace_once(text, f"- name: {original_name}", f"- name: {replacement_name}"))


def rewrite_workflow_command(root: Path, original_command: str, replacement_command: str) -> None:
    text = load_text(root, WORKFLOW_REL)
    write_text(root, WORKFLOW_REL, replace_once(text, f"run: {original_command}", f"run: {replacement_command}"))


def run_self_test() -> int:
    cases: list[tuple[str, object | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", ("missing_file", relative_path)))

    for relative_path, markers in REQUIRED_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path.as_posix()}", ("remove", relative_path, marker)))
            cases.append((f"duplicate_marker:{relative_path.as_posix()}", ("duplicate", relative_path, marker)))

    for step_name, run_command in WORKFLOW_PACKET_STEPS:
        cases.append((f"missing_workflow_step:{step_name}", ("remove", WORKFLOW_REL, workflow_name_line(step_name))))
        cases.append((f"duplicate_workflow_step:{step_name}", ("duplicate", WORKFLOW_REL, workflow_name_line(step_name))))
        cases.append((f"missing_workflow_run:{run_command}", ("remove", WORKFLOW_REL, workflow_run_line(run_command))))
        cases.append((f"duplicate_workflow_run:{run_command}", ("duplicate", WORKFLOW_REL, workflow_run_line(run_command))))

    cases.append(("workflow_reordered", ("reorder_workflow",)))
    cases.append(("workflow_forbidden_line", ("forbidden_workflow",)))
    cases.append(("workflow_optional_pair_present", ("optional_workflow", "normal")))
    cases.append(("workflow_optional_pair_reversed", ("optional_workflow", "reversed")))
    cases.append(("workflow_optional_pair_after_bench", ("optional_workflow", "after_bench")))
    cases.append(("workflow_optional_pair_split", ("optional_workflow", "split")))
    cases.append(("workflow_optional_pair_self_only", ("optional_workflow", "self_only")))
    cases.append(("workflow_optional_pair_check_only", ("optional_workflow", "check_only")))
    cases.append(
        (
            "workflow_required_step_name_drift",
            ("rename_workflow_step", "Self-test current Phase 1 direct-owner checker", "Self-test current Phase 1 direct-owner proof"),
        )
    )
    cases.append(
        (
            "workflow_required_command_drift",
            (
                "rewrite_workflow_command",
                "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
                "python3 scripts/zigux/check-phase1-direct-owner-markers.py --dry-run",
            ),
        )
    )
    cases.append(
        (
            "workflow_optional_step_name_drift",
            (
                "optional_step_name_drift",
                "Self-test current Phase 1 bootstrap packet alignment checker",
                "Self-test current Phase 1 bootstrap packet proof",
            ),
        )
    )
    cases.append(
        (
            "workflow_optional_command_drift",
            (
                "optional_command_drift",
                "python3 scripts/zigux/check-phase1-bootstrap-packet-alignment.py --self-test",
                "python3 scripts/zigux/check-phase1-bootstrap-packet-alignment.py --dry-run",
            ),
        )
    )

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
                elif kind == "rename_workflow_step":
                    rename_workflow_step(root, mutation[1], mutation[2])
                elif kind == "rewrite_workflow_command":
                    rewrite_workflow_command(root, mutation[1], mutation[2])
                elif kind == "optional_step_name_drift":
                    add_optional_workflow_pair(root, "normal")
                    rename_workflow_step(root, mutation[1], mutation[2])
                elif kind == "optional_command_drift":
                    add_optional_workflow_pair(root, "normal")
                    rewrite_workflow_command(root, mutation[1], mutation[2])
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
    print(f"PHASE1_BOOTSTRAP_PACKET_ALIGNMENT_REQUIRED_WORKFLOW_STEP_COUNT={len(WORKFLOW_PACKET_STEPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
