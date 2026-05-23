#!/usr/bin/env python3
"""Guard the current Phase 1 shared tests-root smoke packet on current master."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
TESTS_README_REL = Path("zigux/tests/README.md")
SCRIPTS_README_REL = Path("scripts/zigux/README.md")
TESTS_BUILD_REL = Path("zigux/tests/build.zig")
PHASE1_SMOKE_REL = Path("zigux/tests/phase1_host_tools_smoke.zig")
WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")

REQUIRED_FILES = (
    PHASE1_CLOSURE_REL,
    TESTS_README_REL,
    SCRIPTS_README_REL,
    TESTS_BUILD_REL,
    PHASE1_SMOKE_REL,
    WORKFLOW_REL,
)

REQUIRED_MARKERS = {
    PHASE1_CLOSURE_REL: (
        "The current shared tests-root closure route is narrow on purpose:",
        "- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet: `.github/workflows/zigux-bootstrap.yml` self-tests the directly readable Phase 1 direct-owner, string-review, route-summary, bench, shared-reminder, and closure-validator checks, replays the route-summary, direct-owner, string-review, shared-reminder, closure-validator, and shared tests-root smoke steps on current `master`, and currently keeps the bench checker at self-test coverage only.",
    ),
    TESTS_README_REL: (
        "  * current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "  * keep the Phase 1 tests-root reminder truthful: the thirteen helper ports remain closed through the committed manifest, the nine shared-replay parked helpers reopen only for packet or fixture drift, and only `tools/lib/bitmap.zig`, `tools/lib/find_bit.zig`, `tools/lib/rbtree.zig`, and `tools/lib/string.zig` still keep bounded direct-anchor follow-up markers on current `master`",
        "- Does the bounded Phase 1 reminder keep the restored closure note, the workflow-backed closure-validator and shipped checker packet, the shared tests-root smoke route, the manifest-backed owner map, the broader-companion wording for the validator-first, parity, bench-replay, and helper-replay family, and the historical-gap wording for the missing Phase 1 Makefile routes aligned without widening back into the older full closure stack?",
    ),
    SCRIPTS_README_REL: (
        "- `python3 scripts/zigux/validate-phase1-closure.py`, `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, `python3 scripts/zigux/check-phase1-bench.py --self-test`, and `python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test` replay the shipped bounded Phase 1 reminder checks, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` replays the shipped shared tests-root smoke route",
        "- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `zigux/tests/build.zig`, `zigux/tests/phase1_host_tools_smoke.zig`, and `scripts/zigux/README.md` remain the current reminder-surface companions for that packet",
        "- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts",
    ),
}

REQUIRED_BUILD_LINES = (
    '    const phase1_step = b.step(',
    '        "phase1-host-tools-smoke",',
    '        "Run the shared Phase 1 host-tools smoke anchor from zigux/tests",',
    '    phase1_step.dependOn(&phase1_host_tools_smoke.step);',
    '    smoke_step.dependOn(&phase1_host_tools_smoke.step);',
    '    test_step.dependOn(&phase1_host_tools_smoke.step);',
)

REQUIRED_SMOKE_LINES = (
    'test "phase1 host-tools smoke imports the live helper modules" {',
    'test "phase1 host-tools smoke exercises live helper behavior" {',
    'test "phase1 host-tools smoke keeps find_bit andnot and clump anchors aligned" {',
    'test "phase1 host-tools smoke keeps bitmap alias zero-size and empty-format edges aligned" {',
    '    try std.testing.expectEqualSlices(i32, &.{ 0, 2, 4 }, duplicate_serials[0..duplicate_count]);',
    '    try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);',
)

WORKFLOW_PACKET_STEPS = (
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
        "Check current Phase 1 closure packet",
        "python3 scripts/zigux/validate-phase1-closure.py",
    ),
    (
        "Self-test current Phase 3 interop packet",
        "python3 scripts/zigux/validate_phase3_selftest.py",
    ),
    (
        "Check current Phase 3 interop packet",
        "python3 scripts/zigux/run-phase3-checks.py",
    ),
    (
        "Run current Phase 3 export/UAPI layout replay",
        "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    ),
    (
        "Run current Phase 3 policy starter-packet replay",
        "make -C zigux phase3-policy-starter-packet-test",
    ),
    (
        "Run current Phase 3 policy dump replay",
        "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    ),
    (
        "Self-test current Phase 3 low-level wrapper survey validator",
        "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    ),
    (
        "Check current Phase 3 low-level wrapper survey packet",
        "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    ),
    (
        "Run current Phase 3 low-level wrapper replay",
        "zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    ),
    (
        "Run current Phase 3 shared tests-root packet",
        "zig build phase3-test --build-file zigux/tests/build.zig",
    ),
    (
        "Run current Phase 3 ABI dump replay",
        "zig build phase3-dump --build-file zigux/tests/build.zig",
    ),
    (
        "Run current Phase 1 shared tests-root smoke",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    ),
)

PREDECESSOR_STEP = (
    "Self-test current Phase 1 string review checker",
    "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
)
SUCCESSOR_STEP = (
    "Self-test current Phase 4 repo-reality warning checker",
    "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
)

FORBIDDEN_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-phase1-bench.py",
    "run: zig build test --build-file zigux/tests/build.zig",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def write_text(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_line_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line == needle)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_absent_line_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == needle)
    return [] if count == 0 else [f"{label}:expected=0:actual={count}"]


def workflow_step_block(step_name: str, run_command: str) -> str:
    return f"      - name: {step_name}\n        run: {run_command}"


def workflow_step_names(text: str) -> list[str]:
    prefix = "      - name: "
    return [line[len(prefix) :] for line in text.splitlines() if line.startswith(prefix)]


def contains_adjacent_chain(names: list[str], expected_chain: tuple[str, ...]) -> bool:
    width = len(expected_chain)
    for start in range(len(names) - width + 1):
        if tuple(names[start : start + width]) == expected_chain:
            return True
    return False


def collect_workflow_failures(text: str) -> list[str]:
    failures: list[str] = []

    for label, step in (("predecessor", PREDECESSOR_STEP), ("successor", SUCCESSOR_STEP)):
        block = workflow_step_block(*step)
        count = text.count(block)
        if count != 1:
            failures.append(f"workflow_boundary_{label}:{step[0]}:expected=1:actual={count}")

    positions: list[int] = []
    for step_name, run_command in WORKFLOW_PACKET_STEPS:
        block = workflow_step_block(step_name, run_command)
        count = text.count(block)
        if count != 1:
            failures.append(f"workflow_pair:{step_name}:expected=1:actual={count}")
            continue
        positions.append(text.index(block))

    if failures:
        return failures
    if positions != sorted(positions):
        failures.append("workflow:phase1_shared_smoke_packet:expected=strictly_increasing:actual=out_of_order")
        return failures

    workflow_names = workflow_step_names(text)
    core_chain = tuple(step_name for step_name, _ in WORKFLOW_PACKET_STEPS)
    if not contains_adjacent_chain(workflow_names, core_chain):
        failures.append("workflow:phase1_shared_smoke_packet:expected=adjacent_without_insertions:actual=split_or_interleaved")

    boundary_chain = (PREDECESSOR_STEP[0],) + core_chain + (SUCCESSOR_STEP[0],)
    if not contains_adjacent_chain(workflow_names, boundary_chain):
        failures.append("workflow:phase1_shared_smoke_packet:expected=between_phase1_string_selftest_and_phase4_head:actual=split_or_shifted")

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
                require_exact_occurrence(text, f"{relative_path.as_posix()}:{marker}", marker)
            )

    tests_build_text = load_text(root, TESTS_BUILD_REL)
    for marker in REQUIRED_BUILD_LINES:
        failures.extend(
            require_exact_line_occurrence(
                tests_build_text, f"{TESTS_BUILD_REL.as_posix()}:{marker}", marker
            )
        )

    smoke_text = load_text(root, PHASE1_SMOKE_REL)
    for marker in REQUIRED_SMOKE_LINES:
        failures.extend(
            require_exact_line_occurrence(
                smoke_text, f"{PHASE1_SMOKE_REL.as_posix()}:{marker}", marker
            )
        )

    workflow_text = load_text(root, WORKFLOW_REL)
    failures.extend(collect_workflow_failures(workflow_text))
    for marker in FORBIDDEN_WORKFLOW_LINES:
        failures.extend(
            require_absent_line_occurrence(
                workflow_text, f"{WORKFLOW_REL.as_posix()}:{marker}", marker
            )
        )

    return failures


def build_sample_repo(root: Path) -> None:
    for relative_path, markers in REQUIRED_MARKERS.items():
        write_text(root, relative_path, "\n".join(markers) + "\n")

    write_text(root, TESTS_BUILD_REL, "\n".join(REQUIRED_BUILD_LINES) + "\n")
    write_text(root, PHASE1_SMOKE_REL, "\n".join(REQUIRED_SMOKE_LINES) + "\n")

    blocks = [workflow_step_block(*PREDECESSOR_STEP)]
    blocks.extend(workflow_step_block(step_name, run_command) for step_name, run_command in WORKFLOW_PACKET_STEPS)
    blocks.append(workflow_step_block(*SUCCESSOR_STEP))
    write_text(root, WORKFLOW_REL, "\n".join(blocks) + "\n")


def remove_marker(root: Path, relative_path: Path, marker: str) -> None:
    text = load_text(root, relative_path)
    write_text(root, relative_path, text.replace(marker + "\n", "", 1))


def duplicate_marker(root: Path, relative_path: Path, marker: str) -> None:
    text = load_text(root, relative_path)
    write_text(root, relative_path, text.replace(marker, marker + "\n" + marker, 1))


def reorder_workflow(root: Path) -> None:
    steps = list(WORKFLOW_PACKET_STEPS)
    steps[-1], steps[-2] = steps[-2], steps[-1]
    blocks = [workflow_step_block(*PREDECESSOR_STEP)]
    blocks.extend(workflow_step_block(step_name, run_command) for step_name, run_command in steps)
    blocks.append(workflow_step_block(*SUCCESSOR_STEP))
    write_text(root, WORKFLOW_REL, "\n".join(blocks) + "\n")


def add_forbidden_workflow_line(root: Path, line: str) -> None:
    text = load_text(root, WORKFLOW_REL)
    write_text(root, WORKFLOW_REL, text + "        " + line + "\n")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[str, object] | None]] = [("success", None)]

    for relative_path in REQUIRED_FILES:
        cases.append((f"missing_file:{relative_path.as_posix()}", ("missing_file", relative_path)))

    for relative_path, markers in REQUIRED_MARKERS.items():
        for marker in markers:
            cases.append((f"missing_marker:{relative_path.as_posix()}", ("remove", relative_path, marker)))
            cases.append((f"duplicate_marker:{relative_path.as_posix()}", ("duplicate", relative_path, marker)))

    for marker in REQUIRED_BUILD_LINES:
        cases.append((f"missing_build_line:{marker}", ("remove", TESTS_BUILD_REL, marker)))

    for marker in REQUIRED_SMOKE_LINES:
        cases.append((f"missing_smoke_line:{marker}", ("remove", PHASE1_SMOKE_REL, marker)))

    cases.extend(
        [
            ("workflow_reordered", ("reorder_workflow",)),
            ("workflow_forbidden_bench_run", ("forbidden_workflow", FORBIDDEN_WORKFLOW_LINES[0])),
            ("workflow_forbidden_generic_test_run", ("forbidden_workflow", FORBIDDEN_WORKFLOW_LINES[1])),
        ]
    )

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-shared-smoke-packet-") as tmpdir:
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

    print("PHASE1_SHARED_SMOKE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_SHARED_SMOKE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_SHARED_SMOKE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_SHARED_SMOKE_PACKET=pass")
    print(f"PHASE1_SHARED_SMOKE_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_SHARED_SMOKE_PACKET_REQUIRED_WORKFLOW_STEP_COUNT={len(WORKFLOW_PACKET_STEPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
