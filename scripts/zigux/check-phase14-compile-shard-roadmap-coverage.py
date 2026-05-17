#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=compile_shard_roadmap_coverage

Fail-closed checker for the shared Phase 14 compile-shard matrix.
It keeps the manifest, shared smoke survey, and build wiring aligned with
the roadmap-backed workqueue and skbuff bridge destinations.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


EXPECTED_COMPILE_SHARDS = [
    {
        "label": "phase14-workqueue-bridge-tests",
        "root_source": "phase14_workqueue_bridge.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-workqueue-reviewability-tests",
        "root_source": "phase14_workqueue_reviewability.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-skbuff-bridge-tests",
        "root_source": "phase14_skbuff_bridge.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-ring-buffer-survey-tests",
        "root_source": "phase14_ring_buffer_survey.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-rcu-tree-survey-tests",
        "root_source": "phase14_rcu_tree_survey.zig",
        "coverage": "full_bundle_only",
    },
    {
        "label": "phase14-end-to-end-smoke-tests",
        "root_source": "phase14_end_to_end_smoke_survey.zig",
        "coverage": "focused_and_full_bundle",
    },
]

EXPECTED_COMPILE_SHARD_COUNTS = {
    "total": 6,
    "focused_and_full_bundle": 1,
    "full_bundle_only": 5,
}

EXPECTED_MATRIX_ROWS = [
    "    * `phase14-workqueue-bridge-tests` -> `phase14_workqueue_bridge.zig` -> `full_bundle_only`",
    "    * `phase14-workqueue-reviewability-tests` -> `phase14_workqueue_reviewability.zig` -> `full_bundle_only`",
    "    * `phase14-skbuff-bridge-tests` -> `phase14_skbuff_bridge.zig` -> `full_bundle_only`",
    "    * `phase14-ring-buffer-survey-tests` -> `phase14_ring_buffer_survey.zig` -> `full_bundle_only`",
    "    * `phase14-rcu-tree-survey-tests` -> `phase14_rcu_tree_survey.zig` -> `full_bundle_only`",
    "    * `phase14-end-to-end-smoke-tests` -> `phase14_end_to_end_smoke_survey.zig` -> `focused_and_full_bundle`",
]

EXPECTED_ROADMAP_DESTINATION_LINE = (
    "  * the same packet also keeps the two landed bridge-backed roadmap destinations "
    "explicit by tying `phase14-workqueue-bridge-tests` to "
    "`../../kernel/workqueue_bridge.zig` and `phase14-skbuff-bridge-tests` to "
    "`../../net/core/skbuff_bridge.zig`, instead of letting the matrix collapse "
    "to test-root names alone."
)

EXPECTED_BUILD_MARKERS = [
    'const workqueue_bridge_module = b.createModule(.{ .root_source_file = b.path("../../kernel/workqueue_bridge.zig")',
    'const skbuff_bridge_module = b.createModule(.{ .root_source_file = b.path("../../net/core/skbuff_bridge.zig")',
    'const phase14_workqueue_bridge_module = b.createModule(.{ .root_source_file = b.path("phase14_workqueue_bridge.zig")',
    'const phase14_skbuff_bridge_module = b.createModule(.{ .root_source_file = b.path("phase14_skbuff_bridge.zig")',
    'phase14_workqueue_bridge_module.addImport("workqueue_bridge", workqueue_bridge_module);',
    'phase14_skbuff_bridge_module.addImport("skbuff_bridge", skbuff_bridge_module);',
    '.name = "phase14-workqueue-bridge-tests"',
    '.name = "phase14-skbuff-bridge-tests"',
]


def read_text(root: Path, relative: str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def require_markers(missing: list[str], prefix: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{prefix}:{marker}")


def check_root(root: Path) -> list[str]:
    missing: list[str] = []

    manifest_text = read_text(root, "zigux/tests/phase14_end_to_end_smoke_manifest.json")
    manifest = json.loads(manifest_text)

    if manifest.get("compile_shards") != EXPECTED_COMPILE_SHARDS:
        missing.append("manifest:compile_shards")

    if manifest.get("compile_shard_counts") != EXPECTED_COMPILE_SHARD_COUNTS:
        missing.append("manifest:compile_shard_counts")

    survey_text = read_text(root, "Documentation/zigux/phase14-end-to-end-smoke-survey.md")
    require_markers(missing, "survey", survey_text, EXPECTED_MATRIX_ROWS)
    require_markers(missing, "survey", survey_text, [EXPECTED_ROADMAP_DESTINATION_LINE])

    row_count = sum(
        1
        for line in survey_text.splitlines()
        if line.startswith("    * `phase14-") and "->" in line
    )
    if row_count != EXPECTED_COMPILE_SHARD_COUNTS["total"]:
        missing.append(f"survey:compile_shard_row_count={row_count}")

    build_text = read_text(root, "zigux/tests/phase14_build.zig")
    require_markers(missing, "build", build_text, EXPECTED_BUILD_MARKERS)

    return missing


def write_fixture(root: Path) -> None:
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)

    survey_lines = [
        "# Phase 14 End-to-End Smoke Survey",
        "",
        "## Exact evidence captured",
        "  * compile shard matrix captured in the current shared packet:",
        *EXPECTED_MATRIX_ROWS,
        EXPECTED_ROADMAP_DESTINATION_LINE,
    ]
    (root / "Documentation/zigux/phase14-end-to-end-smoke-survey.md").write_text(
        "\n".join(survey_lines) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "compile_shards": EXPECTED_COMPILE_SHARDS,
        "compile_shard_counts": EXPECTED_COMPILE_SHARD_COUNTS,
    }
    (root / "zigux/tests/phase14_end_to_end_smoke_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    build_lines = [
        "pub fn build() void {",
        'const workqueue_bridge_module = b.createModule(.{ .root_source_file = b.path("../../kernel/workqueue_bridge.zig"), .target = target, .optimize = optimize, });',
        'const skbuff_bridge_module = b.createModule(.{ .root_source_file = b.path("../../net/core/skbuff_bridge.zig"), .target = target, .optimize = optimize, });',
        'const phase14_workqueue_bridge_module = b.createModule(.{ .root_source_file = b.path("phase14_workqueue_bridge.zig"), .target = target, .optimize = optimize, });',
        'phase14_workqueue_bridge_module.addImport("workqueue_bridge", workqueue_bridge_module);',
        'const phase14_skbuff_bridge_module = b.createModule(.{ .root_source_file = b.path("phase14_skbuff_bridge.zig"), .target = target, .optimize = optimize, });',
        'phase14_skbuff_bridge_module.addImport("skbuff_bridge", skbuff_bridge_module);',
        'const phase14_workqueue_bridge_tests = b.addTest(.{ .name = "phase14-workqueue-bridge-tests", .root_module = phase14_workqueue_bridge_module, });',
        'const phase14_skbuff_bridge_tests = b.addTest(.{ .name = "phase14-skbuff-bridge-tests", .root_module = phase14_skbuff_bridge_module, });',
        "}",
    ]
    (root / "zigux/tests/phase14_build.zig").write_text(
        "\n".join(build_lines) + "\n",
        encoding="utf-8",
    )


def run_self_test() -> int:
    temp_dir = Path(tempfile.mkdtemp(prefix="phase14-compile-shard-roadmap-"))
    try:
        write_fixture(temp_dir)
        missing = check_root(temp_dir)
        if missing:
            print("PHASE14_COMPILE_SHARD_ROADMAP_COVERAGE_SELF_TEST=fail")
            print("SELF_TEST_REASON=unexpected_missing_markers")
            for item in missing:
                print(item)
            return 1

        build_path = temp_dir / "zigux/tests/phase14_build.zig"
        build_text = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            build_text.replace("../../net/core/skbuff_bridge.zig", "../../net/core/skbuff_missing.zig"),
            encoding="utf-8",
        )
        missing = check_root(temp_dir)
        expected = "build:const skbuff_bridge_module = b.createModule(.{ .root_source_file = b.path(\"../../net/core/skbuff_bridge.zig\")"
        if expected not in missing:
            print("PHASE14_COMPILE_SHARD_ROADMAP_COVERAGE_SELF_TEST=fail")
            print("SELF_TEST_REASON=missing_expected_build_failure")
            for item in missing:
                print(item)
            return 1

        print("PHASE14_COMPILE_SHARD_ROADMAP_COVERAGE_SELF_TEST=pass")
        print("PHASE14_COMPILE_SHARD_ROADMAP_COVERAGE_SELF_TEST_CASES=2")
        return 0
    finally:
        shutil.rmtree(temp_dir)


def main() -> int:
    parser = argparse.ArgumentParser()
    script_path = Path(__file__).resolve()
    default_root = script_path.parents[2] if len(script_path.parents) > 2 else Path.cwd()
    parser.add_argument("--root", type=Path, default=default_root)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = check_root(args.root)
    if missing:
        print("PHASE14_COMPILE_SHARD_ROADMAP_COVERAGE=fail")
        print("PHASE14_COMPILE_SHARD_ROADMAP_COVERAGE_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE14_COMPILE_SHARD_ROADMAP_COVERAGE_MISSING_END")
        return 1

    print("PHASE14_COMPILE_SHARD_ROADMAP_COVERAGE=pass")
    print(f"PHASE14_COMPILE_SHARD_TOTAL={EXPECTED_COMPILE_SHARD_COUNTS['total']}")
    print(
        "PHASE14_COMPILE_SHARD_ROADMAP_DESTINATIONS="
        "../../kernel/workqueue_bridge.zig,../../net/core/skbuff_bridge.zig"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
