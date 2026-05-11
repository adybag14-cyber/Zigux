#!/usr/bin/env python3
"""PHASE9_CHECK_PACKET=runtime_loader_prepared_state_explicitness

Fail-closed checker for the live Phase 9 runtime-loader prepared-state proof.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE9_CHECK_PACKET=runtime_loader_prepared_state_explicitness"
CHECKER_PATH = "scripts/zigux/check-phase9-runtime-loader-prepared-state-explicitness.py"
TARGET_PATH = Path("zigux/tests/runtime_loader_allocator_init_flow.zig")
PHASE9_BUILD_PATH = Path("zigux/tests/phase9_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
TARGET_ASSERTION = (
    "try std.testing.expect("
    "runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan)"
    ");"
)
REQUIRED_BUILD_MARKERS = (
    '.root_source_file = b.path("runtime_loader_allocator_init_flow.zig")',
    '"phase9-runtime-loader-shared-tests"',
    "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);",
    "test_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);",
)
REQUIRED_MAKEFILE_MARKERS = (
    "PHONY += phase9-runtime-atomic64-test phase9-runtime-bitmap-top-bit-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-runtime-loader-shared-tests phase9-test phase9",
    "phase9-runtime-loader-shared-tests",
)
REQUIRED_BLOCKS = (
    """    request.plan.requires_runtime_substrate = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));
""",
    """    request.plan.module_name = \"runtime_trace_events_drift\";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));
    try std.testing.expectEqualStrings(stable_plan.module_name, request.prepared_plan.module_name);
""",
    """    request.plan.anchor = \"samples/trace_events/trace-events-sample-drift.c\";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));
""",
    """    request.plan.entry_symbol = \"zigux_runtime_trace_events_init_drift\";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));
""",
    """    request.plan.exit_symbol = \"zigux_runtime_trace_events_exit_drift\";
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));
    request.plan = stable_plan;
""",
    """    request.plan.provides_selftest_hook = false;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));
""",
    """    request.plan.init_flow.selftest_runs = 2;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, request.plan));
""",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    target = root / TARGET_PATH
    build_path = root / PHASE9_BUILD_PATH
    makefile_path = root / MAKEFILE_PATH

    for path in (target, build_path, makefile_path):
        if not path.exists():
            issues.append(f"missing file: {path.relative_to(root).as_posix()}")
    if issues:
        return issues

    if MARKER not in read_text(Path(__file__)):
        issues.append("checker marker missing from checker source")

    target_text = read_text(target)
    build_text = read_text(build_path)
    makefile_text = read_text(makefile_path)

    assertion_count = target_text.count(TARGET_ASSERTION)
    if assertion_count != 7:
        issues.append(
            "prepared-state explicitness assertion count drifted "
            f"(expected 7, found {assertion_count})"
        )

    for index, block in enumerate(REQUIRED_BLOCKS, start=1):
        if block not in target_text:
            issues.append(f"missing prepared-state proof block {index}")

    for marker in REQUIRED_BUILD_MARKERS:
        if marker not in build_text:
            issues.append(f"missing phase9 build marker: {marker}")

    for marker in REQUIRED_MAKEFILE_MARKERS:
        if marker not in makefile_text:
            issues.append(f"missing phase9 makefile marker: {marker}")

    return issues


def build_good_target_text() -> str:
    allocator_block = """    request.plan = stable_plan;
    request.plan.allocator_handoff = .arena;
    try std.testing.expectError(error.PreparedPlanDrift, request.requestRuntimeLoad());
    try expectPreparedPlanDriftKeepsPreparedState(request, stable_plan);
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.caller_provided, request.prepared_plan.allocator_handoff);
    try std.testing.expectEqual(runtime_loader.AllocatorHandoff.arena, request.plan.allocator_handoff);

"""
    return (
        "test \"phase 9 runtime loader allocator/init-flow replay keeps prepared snapshots pinned when requestRuntimeLoad sees prepared-plan drift\" {\n"
        "    const stable_plan = makePlan(\n"
        "        \"runtime_trace_events\",\n"
        "        \"samples/trace_events/trace-events-sample.c\",\n"
        "        \"zigux_runtime_trace_events_init\",\n"
        "        \"zigux_runtime_trace_events_exit\",\n"
        "        .caller_provided,\n"
        "        .{\n"
        "            .handoff_stage = .selftest_complete,\n"
        "            .init_runs = 1,\n"
        "            .selftest_runs = 1,\n"
        "            .exit_runs = 0,\n"
        "        },\n"
        "    );\n\n"
        "    var request = try runtime_loader.prepareRequest(stable_plan);\n"
        "    try std.testing.expectEqual(runtime_loader.RequestState.prepared, request.state);\n"
        "    try std.testing.expect(runtime_loader.keepsRequestStateAndPlanExplicit(request, .prepared, stable_plan));\n\n"
        + REQUIRED_BLOCKS[0]
        + "\n    request.plan = stable_plan;\n"
        + REQUIRED_BLOCKS[1]
        + "\n    request.plan = stable_plan;\n"
        + REQUIRED_BLOCKS[2]
        + "\n    request.plan = stable_plan;\n"
        + REQUIRED_BLOCKS[3]
        + "\n    request.plan = stable_plan;\n"
        + REQUIRED_BLOCKS[4]
        + "\n"
        + allocator_block
        + "    request.plan = stable_plan;\n"
        + REQUIRED_BLOCKS[5]
        + "\n    request.plan = stable_plan;\n"
        + REQUIRED_BLOCKS[6]
        + "}\n"
    )


def build_good_phase9_build_text() -> str:
    return "\n".join(REQUIRED_BUILD_MARKERS) + "\n"


def build_good_makefile_text() -> str:
    return "\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n"


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase9_prepared_state_checker_") as tmpdir:
        root = Path(tmpdir)
        current_checker_path = Path(__file__)
        original_source = read_text(current_checker_path)

        write_text(root / TARGET_PATH, build_good_target_text())
        write_text(root / PHASE9_BUILD_PATH, build_good_phase9_build_text())
        write_text(root / MAKEFILE_PATH, build_good_makefile_text())

        issues = collect_issues(root)
        if issues:
            print("PHASE9_PREPARED_STATE_EXPLICITNESS_SELF_TEST=fail", file=sys.stderr)
            for issue in issues:
                print(issue, file=sys.stderr)
            return 1
        case_count += 1

        write_text(
            root / TARGET_PATH,
            build_good_target_text().replace(TARGET_ASSERTION + "\n", "", 1),
        )
        issues = collect_issues(root)
        if not any("assertion count drifted" in issue for issue in issues):
            print("expected missing assertion count failure", file=sys.stderr)
            return 1
        case_count += 1

        write_text(root / TARGET_PATH, build_good_target_text())
        write_text(
            root / TARGET_PATH,
            build_good_target_text().replace(
                REQUIRED_BLOCKS[2], REQUIRED_BLOCKS[2].replace(TARGET_ASSERTION + "\n", ""), 1
            ),
        )
        issues = collect_issues(root)
        if "missing prepared-state proof block 3" not in issues:
            print("expected missing block 3 failure", file=sys.stderr)
            return 1
        case_count += 1

        write_text(
            root / TARGET_PATH,
            build_good_target_text() + "    " + TARGET_ASSERTION + "\n",
        )
        issues = collect_issues(root)
        if not any("assertion count drifted" in issue for issue in issues):
            print("expected duplicate assertion count failure", file=sys.stderr)
            return 1
        case_count += 1

        write_text(root / TARGET_PATH, build_good_target_text())
        write_text(root / PHASE9_BUILD_PATH, "")
        issues = collect_issues(root)
        if not any("missing phase9 build marker" in issue for issue in issues):
            print("expected missing phase9 build marker failure", file=sys.stderr)
            return 1
        case_count += 1

        write_text(root / PHASE9_BUILD_PATH, build_good_phase9_build_text())
        write_text(root / MAKEFILE_PATH, "")
        issues = collect_issues(root)
        if not any("missing phase9 makefile marker" in issue for issue in issues):
            print("expected missing phase9 makefile marker failure", file=sys.stderr)
            return 1
        case_count += 1

        write_text(root / MAKEFILE_PATH, build_good_makefile_text())
        write_text(current_checker_path, original_source.replace(MARKER, "PHASE9_CHECK_PACKET=broken"))
        issues = collect_issues(root)
        if "checker marker missing from checker source" not in issues:
            print("expected checker-source marker failure", file=sys.stderr)
            write_text(current_checker_path, original_source)
            return 1
        write_text(current_checker_path, original_source)
        case_count += 1

    print("PHASE9_PREPARED_STATE_EXPLICITNESS_SELF_TEST=pass")
    print(f"PHASE9_PREPARED_STATE_EXPLICITNESS_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    parser.add_argument("--repo-root", type=Path, default=repo_root())
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.repo_root)
    if issues:
        print("PHASE9_PREPARED_STATE_EXPLICITNESS=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE9_PREPARED_STATE_EXPLICITNESS=pass")
    print("PHASE9_PREPARED_STATE_ASSERTION_COUNT=7")
    print(f"PHASE9_PREPARED_STATE_CHECKER={CHECKER_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
