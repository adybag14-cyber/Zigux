#!/usr/bin/env python3
"""Check that the bounded Phase 14 compile-shard matrix evidence stays aligned."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

NOTE_PATH = Path("Documentation/zigux/phase14-compile-shard-matrix-evidence.md")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")
BUILD_PATH = Path("zigux/tests/phase14_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")

EXPECTED_ROWS = [
    ("phase14-workqueue-bridge-tests", "phase14_workqueue_bridge.zig", "full_bundle_only"),
    ("phase14-workqueue-reviewability-tests", "phase14_workqueue_reviewability.zig", "full_bundle_only"),
    ("phase14-skbuff-bridge-tests", "phase14_skbuff_bridge.zig", "full_bundle_only"),
    ("phase14-ring-buffer-survey-tests", "phase14_ring_buffer_survey.zig", "full_bundle_only"),
    ("phase14-rcu-tree-survey-tests", "phase14_rcu_tree_survey.zig", "full_bundle_only"),
    ("phase14-end-to-end-smoke-tests", "phase14_end_to_end_smoke_survey.zig", "focused_and_full_bundle"),
]

REQUIRED_NOTE_MARKERS = (
    "`PHASE14_LANE_KEY=P14-L09`",
    "`PHASE14_COMPILE_SHARD_COUNT=6`",
    "`PHASE14_FULL_BUNDLE_ONLY_COUNT=5`",
    "`PHASE14_FOCUSED_AND_FULL_BUNDLE_COUNT=1`",
    "`PHASE14_SHARED_SMOKE_COMMAND_COUNT=1`",
    "`PHASE14_SMOKE_SHARD_COMMAND_COUNT=0`",
    "public raw readback on `2026-05-22` recovered `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, and `zigux/tests/phase14_rcu_tree_survey.zig` even though the same files still returned contents-path `404` in this lane's exact read mode.",
    "`zigux/tests/phase14_build.zig` carries six `b.addTest` shard entries, wires `phase14-smoke` to the focused `phase14-end-to-end-smoke-tests` shard only, and wires the build-file `test` step to all six shards.",
    "`zigux/Makefile` still narrows the shared rerun route to `phase14-validate`; it does not materialize `phase14-smoke`, `phase14-test`, or `phase14`, so the focused smoke shard remains build-file-local evidence rather than a returned Makefile wrapper.",
)

REQUIRED_BUILD_MARKERS = (
    'b.step("phase14-smoke", "Run the focused Phase 14 smoke shard")',
    'b.step("test", "Run the full Phase 14 bounded bridge and survey bundle")',
)

FORBIDDEN_MAKEFILE_MARKERS = (
    "phase14-smoke:",
    "phase14-test:",
    "phase14: phase14-validate phase14-smoke phase14-test",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def check(root: Path) -> None:
    note_path = root / NOTE_PATH
    manifest_path = root / MANIFEST_PATH
    build_path = root / BUILD_PATH
    makefile_path = root / MAKEFILE_PATH

    for path in (note_path, manifest_path, build_path, makefile_path):
        require(path.exists(), f"missing required file: {path.relative_to(root)}")

    note_text = note_path.read_text(encoding="utf-8")
    for marker in REQUIRED_NOTE_MARKERS:
        require(marker in note_text, f"note missing marker: {marker}")
    for label, root_source, coverage in EXPECTED_ROWS:
        row_marker = f"`{label}` -> `{root_source}` -> `{coverage}`"
        require(row_marker in note_text, f"note missing row marker: {row_marker}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    compile_shards = manifest.get("compile_shards")
    require(isinstance(compile_shards, list), "manifest compile_shards must be a list")
    actual_rows = [
        (row.get("label"), row.get("root_source"), row.get("coverage"))
        for row in compile_shards
    ]
    require(actual_rows == EXPECTED_ROWS, f"compile_shards mismatch: {actual_rows!r}")
    require(manifest.get("smoke_commands") == ["make -C zigux phase14-validate"], "manifest smoke_commands drifted")
    require(manifest.get("smoke_shard_commands") == [], "manifest smoke_shard_commands must stay empty")

    survey_summary = manifest.get("survey_summary", {})
    require(survey_summary.get("phase14_build_has_shared_smoke_step") is True, "manifest lost shared smoke step evidence")
    require(survey_summary.get("phase14_build_has_smoke_shard_step") is True, "manifest lost smoke shard step evidence")
    require(survey_summary.get("phase14_make_target_present") is True, "manifest lost phase14-validate Makefile evidence")
    require(survey_summary.get("phase14_make_smoke_target_present") is False, "manifest unexpectedly claims a Makefile smoke target")
    require(survey_summary.get("workflow_runs_phase14_build") is False, "manifest unexpectedly claims workflow build coverage")
    require(survey_summary.get("workflow_runs_phase14_smoke_shard") is False, "manifest unexpectedly claims workflow smoke-shard coverage")

    build_text = build_path.read_text(encoding="utf-8")
    for marker in REQUIRED_BUILD_MARKERS:
        require(marker in build_text, f"build file missing marker: {marker}")
    for label, root_source, _coverage in EXPECTED_ROWS:
        require(f'.name = "{label}"' in build_text, f"build file missing test label: {label}")
        require(f'b.path("{root_source}")' in build_text, f"build file missing root source: {root_source}")
    require("smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);" in build_text, "build file smoke step drifted")
    depend_count = build_text.count("test_step.dependOn(")
    require(depend_count == 6, f"expected 6 full-bundle test dependencies, saw {depend_count}")

    makefile_text = makefile_path.read_text(encoding="utf-8")
    require("phase14-validate:" in makefile_text, "Makefile lost phase14-validate target")
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        require(marker not in makefile_text, f"Makefile unexpectedly gained marker: {marker}")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    note_lines = [
        "# Phase 14 Compile Shard Matrix Evidence",
        "",
        "This note records exact bounded evidence for the current Phase 14 compile-shard matrix on `master`.",
        "",
        "## Status",
        "",
        "- `PHASE14_LANE_KEY=P14-L09`",
        "- `PHASE14_EVIDENCE_DATE=2026-05-22`",
        "- `PHASE14_EVIDENCE_KIND=compile_shard_matrix`",
        "- `PHASE14_MANIFEST_PATH=zigux/tests/phase14_end_to_end_smoke_manifest.json`",
        "- `PHASE14_BUILD_PATH=zigux/tests/phase14_build.zig`",
        "- `PHASE14_MAKEFILE_PATH=zigux/Makefile`",
        "- `PHASE14_COMPILE_SHARD_COUNT=6`",
        "- `PHASE14_FULL_BUNDLE_ONLY_COUNT=5`",
        "- `PHASE14_FOCUSED_AND_FULL_BUNDLE_COUNT=1`",
        "- `PHASE14_SHARED_SMOKE_COMMAND_COUNT=1`",
        "- `PHASE14_SMOKE_SHARD_COMMAND_COUNT=0`",
        "",
        "## Exact matrix",
        "",
    ]
    note_lines.extend([f"- `{label}` -> `{root_source}` -> `{coverage}`" for label, root_source, coverage in EXPECTED_ROWS])
    note_lines.extend(
        [
            "",
            "## Current evidence",
            "",
            "- `zigux/tests/phase14_end_to_end_smoke_manifest.json` is directly readable through the contents path and keeps `make -C zigux phase14-validate` as the only shared smoke command while `smoke_shard_commands` stays empty.",
            "- public raw readback on `2026-05-22` recovered `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, and `zigux/tests/phase14_rcu_tree_survey.zig` even though the same files still returned contents-path `404` in this lane's exact read mode.",
            "- `zigux/tests/phase14_build.zig` carries six `b.addTest` shard entries, wires `phase14-smoke` to the focused `phase14-end-to-end-smoke-tests` shard only, and wires the build-file `test` step to all six shards.",
            "- `zigux/Makefile` still narrows the shared rerun route to `phase14-validate`; it does not materialize `phase14-smoke`, `phase14-test`, or `phase14`, so the focused smoke shard remains build-file-local evidence rather than a returned Makefile wrapper.",
            "- the current manifest and build file therefore agree on shard count and labels, but they also preserve the narrower route split: one focused smoke shard exists in `phase14_build.zig` while the shared route surface still exposes only `make -C zigux phase14-validate`.",
        ]
    )
    write_text(root / NOTE_PATH, "\n".join(note_lines) + "\n")

    manifest = {
        "smoke_commands": ["make -C zigux phase14-validate"],
        "smoke_shard_commands": [],
        "compile_shards": [
            {"label": label, "root_source": root_source, "coverage": coverage}
            for label, root_source, coverage in EXPECTED_ROWS
        ],
        "survey_summary": {
            "phase14_build_has_shared_smoke_step": True,
            "phase14_build_has_smoke_shard_step": True,
            "phase14_make_target_present": True,
            "phase14_make_smoke_target_present": False,
            "workflow_runs_phase14_build": False,
            "workflow_runs_phase14_smoke_shard": False,
        },
    }
    write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")

    build_text = '''const std = @import("std");
pub fn build(b: *std.Build) void {
    const phase14_end_to_end_smoke_module = b.createModule(.{ .root_source_file = b.path("phase14_end_to_end_smoke_survey.zig"), });
    const phase14_ring_buffer_survey_module = b.createModule(.{ .root_source_file = b.path("phase14_ring_buffer_survey.zig"), });
    const phase14_rcu_tree_survey_module = b.createModule(.{ .root_source_file = b.path("phase14_rcu_tree_survey.zig"), });
    const phase14_workqueue_bridge_module = b.createModule(.{ .root_source_file = b.path("phase14_workqueue_bridge.zig"), });
    const phase14_workqueue_reviewability_module = b.createModule(.{ .root_source_file = b.path("phase14_workqueue_reviewability.zig"), });
    const phase14_skbuff_bridge_module = b.createModule(.{ .root_source_file = b.path("phase14_skbuff_bridge.zig"), });
    const phase14_workqueue_bridge_tests = b.addTest(.{ .name = "phase14-workqueue-bridge-tests", .root_module = phase14_workqueue_bridge_module, });
    const run_phase14_workqueue_bridge_tests = b.addRunArtifact(phase14_workqueue_bridge_tests);
    const phase14_workqueue_reviewability_tests = b.addTest(.{ .name = "phase14-workqueue-reviewability-tests", .root_module = phase14_workqueue_reviewability_module, });
    const run_phase14_workqueue_reviewability_tests = b.addRunArtifact(phase14_workqueue_reviewability_tests);
    const phase14_skbuff_bridge_tests = b.addTest(.{ .name = "phase14-skbuff-bridge-tests", .root_module = phase14_skbuff_bridge_module, });
    const run_phase14_skbuff_bridge_tests = b.addRunArtifact(phase14_skbuff_bridge_tests);
    const phase14_ring_buffer_survey_tests = b.addTest(.{ .name = "phase14-ring-buffer-survey-tests", .root_module = phase14_ring_buffer_survey_module, });
    const run_phase14_ring_buffer_survey_tests = b.addRunArtifact(phase14_ring_buffer_survey_tests);
    const phase14_rcu_tree_survey_tests = b.addTest(.{ .name = "phase14-rcu-tree-survey-tests", .root_module = phase14_rcu_tree_survey_module, });
    const run_phase14_rcu_tree_survey_tests = b.addRunArtifact(phase14_rcu_tree_survey_tests);
    const phase14_end_to_end_smoke_tests = b.addTest(.{ .name = "phase14-end-to-end-smoke-tests", .root_module = phase14_end_to_end_smoke_module, });
    const run_phase14_end_to_end_smoke_tests = b.addRunArtifact(phase14_end_to_end_smoke_tests);
    const smoke_step = b.step("phase14-smoke", "Run the focused Phase 14 smoke shard");
    smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);
    const test_step = b.step("test", "Run the full Phase 14 bounded bridge and survey bundle");
    test_step.dependOn(&run_phase14_workqueue_bridge_tests.step);
    test_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);
    test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);
    test_step.dependOn(&run_phase14_ring_buffer_survey_tests.step);
    test_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);
    test_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);
}
'''
    write_text(root / BUILD_PATH, build_text)

    makefile_text = '''phase12:
\t@true

phase14-validate:
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-shared-smoke-route.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-shared-smoke-route.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase14-tests-readme-smoke-summary.py
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py --self-test
\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase14.py
'''
    write_text(root / MAKEFILE_PATH, makefile_text)


def run_self_test() -> int:
    root = Path(tempfile.mkdtemp(prefix="phase14-compile-shard-matrix-"))
    try:
        write_fixture_tree(root)
        check(root)
        case_count = 1

        broken_manifest = root / MANIFEST_PATH
        manifest = json.loads(broken_manifest.read_text(encoding="utf-8"))
        manifest["compile_shards"][5]["coverage"] = "full_bundle_only"
        write_text(broken_manifest, json.dumps(manifest, indent=2) + "\n")
        try:
            check(root)
        except SystemExit as exc:
            require("compile_shards mismatch" in str(exc), f"unexpected self-test failure: {exc}")
        else:
            raise SystemExit("expected compile_shards mismatch failure")
        case_count += 1

        write_fixture_tree(root)
        broken_build = root / BUILD_PATH
        broken_build.write_text(
            broken_build.read_text(encoding="utf-8").replace(
                'smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);',
                "",
                1,
            ),
            encoding="utf-8",
        )
        try:
            check(root)
        except SystemExit as exc:
            require("build file smoke step drifted" in str(exc), f"unexpected self-test failure: {exc}")
        else:
            raise SystemExit("expected build smoke-step failure")
        case_count += 1

        write_fixture_tree(root)
        broken_makefile = root / MAKEFILE_PATH
        broken_makefile.write_text(
            broken_makefile.read_text(encoding="utf-8") + "phase14-smoke:\n\t@true\n",
            encoding="utf-8",
        )
        try:
            check(root)
        except SystemExit as exc:
            require("Makefile unexpectedly gained marker" in str(exc), f"unexpected self-test failure: {exc}")
        else:
            raise SystemExit("expected Makefile marker failure")
        case_count += 1

        write_fixture_tree(root)
        broken_note = root / NOTE_PATH
        broken_note.write_text(
            broken_note.read_text(encoding="utf-8").replace("`PHASE14_COMPILE_SHARD_COUNT=6`", "", 1),
            encoding="utf-8",
        )
        try:
            check(root)
        except SystemExit as exc:
            require("note missing marker" in str(exc), f"unexpected self-test failure: {exc}")
        else:
            raise SystemExit("expected note marker failure")
        case_count += 1

        print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=pass")
        print(f"PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    check(args.root.resolve())
    print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
