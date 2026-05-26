#!/usr/bin/env python3
"""Fail closed when the exact Phase 14 compile-shard matrix evidence drifts."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


NOTE_PATH = Path("Documentation/zigux/phase14-compile-shard-matrix-evidence.md")
SURVEY_PATH = Path("Documentation/zigux/phase14-compile-shard-matrix-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")
BUILD_PATH = Path("zigux/tests/phase14_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")

EXPECTED_HEAD_SHA = "9c4f5255d15055642bb440d32b408ffcc1d20f5e"
EXPECTED_HEAD_SUBJECT = "test(scripts/zigux): add Phase 10 review-guide packet guard"

EXPECTED_NOTE_MARKERS = [
    f"- current `master` head observed during this lane: `{EXPECTED_HEAD_SHA}`",
    f"- current `master` head subject: `{EXPECTED_HEAD_SUBJECT}`",
    "- `PHASE14_COMPILE_SHARD_TOTAL=6`",
    "- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`",
    "- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`",
    "- shared gate: `make -C zigux phase14-validate`",
    "- focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`",
    "- current workflow route: `run: make -C zigux phase14-validate`",
]

EXPECTED_SURVEY_MARKERS = [
    "- `PHASE14_COMPILE_SHARD_TOTAL=6`",
    "- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`",
    "- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`",
    "- shared gate: `make -C zigux phase14-validate`",
    "- focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`",
]

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

EXPECTED_BUILD_MARKERS = [
    '.root_source_file = b.path("phase14_end_to_end_smoke_survey.zig")',
    '.root_source_file = b.path("phase14_ring_buffer_survey.zig")',
    '.root_source_file = b.path("phase14_rcu_tree_survey.zig")',
    '.root_source_file = b.path("../../kernel/workqueue_bridge.zig")',
    '.root_source_file = b.path("../../net/core/skbuff_bridge.zig")',
    '.root_source_file = b.path("phase14_workqueue_bridge.zig")',
    '.root_source_file = b.path("phase14_workqueue_reviewability.zig")',
    '.root_source_file = b.path("phase14_skbuff_bridge.zig")',
    '.name = "phase14-workqueue-bridge-tests"',
    '.name = "phase14-workqueue-reviewability-tests"',
    '.name = "phase14-skbuff-bridge-tests"',
    '.name = "phase14-ring-buffer-survey-tests"',
    '.name = "phase14-rcu-tree-survey-tests"',
    '.name = "phase14-end-to-end-smoke-tests"',
    'const smoke_step = b.step("phase14-smoke", "Run the focused Phase 14 smoke shard")',
    'const test_step = b.step("test", "Run the full Phase 14 bounded bridge and survey bundle")',
]

EXPECTED_WORKFLOW_MARKERS = [
    "- name: Self-test current Phase 14 shared smoke route checker",
    "run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "- name: Run current Phase 14 validate route",
    "run: make -C zigux phase14-validate",
]

FORBIDDEN_WORKFLOW_MARKERS = [
    "run: make -C zigux phase14-smoke",
    "run: make -C zigux phase14-test",
]


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    return path.read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_markers(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def require_absent(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"forbidden_marker:{rel.as_posix()}:{marker}")


def require_makefile_split(errors: list[str], text: str) -> None:
    required = ["phase14-validate:", "phase14-validate"]
    forbidden = ["phase14-smoke:", "phase14-test:", "\nphase14:"]
    for marker in required:
        if marker not in text:
            errors.append(f"missing_marker:{MAKEFILE_PATH.as_posix()}:{marker}")
    for marker in forbidden:
        if marker in text:
            errors.append(f"forbidden_marker:{MAKEFILE_PATH.as_posix()}:{marker}")


def require_manifest(errors: list[str], text: str) -> None:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{MANIFEST_PATH.as_posix()}:{exc.msg}")
        return

    compile_shards = payload.get("compile_shards")
    if compile_shards != EXPECTED_COMPILE_SHARDS:
        errors.append(
            "manifest_value_mismatch:compile_shards:"
            f"expected={EXPECTED_COMPILE_SHARDS!r}:actual={compile_shards!r}"
        )

    smoke_commands = payload.get("smoke_commands")
    if smoke_commands != ["make -C zigux phase14-validate"]:
        errors.append(
            "manifest_value_mismatch:smoke_commands:"
            f"expected={['make -C zigux phase14-validate']!r}:actual={smoke_commands!r}"
        )

    smoke_shard_commands = payload.get("smoke_shard_commands")
    if smoke_shard_commands != [
        "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"
    ]:
        errors.append(
            "manifest_value_mismatch:smoke_shard_commands:"
            "expected=['zig build phase14-smoke --build-file zigux/tests/phase14_build.zig']:"
            f"actual={smoke_shard_commands!r}"
        )


def check(root: Path) -> list[str]:
    errors: list[str] = []
    required_files = [
        NOTE_PATH,
        SURVEY_PATH,
        MANIFEST_PATH,
        BUILD_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
    ]
    for rel in required_files:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    require_markers(errors, NOTE_PATH, read_text(root, NOTE_PATH), EXPECTED_NOTE_MARKERS)
    require_markers(errors, SURVEY_PATH, read_text(root, SURVEY_PATH), EXPECTED_SURVEY_MARKERS)
    require_manifest(errors, read_text(root, MANIFEST_PATH))
    require_markers(errors, BUILD_PATH, read_text(root, BUILD_PATH), EXPECTED_BUILD_MARKERS)
    require_makefile_split(errors, read_text(root, MAKEFILE_PATH))
    workflow = read_text(root, WORKFLOW_PATH)
    require_markers(errors, WORKFLOW_PATH, workflow, EXPECTED_WORKFLOW_MARKERS)
    require_absent(errors, WORKFLOW_PATH, workflow, FORBIDDEN_WORKFLOW_MARKERS)
    return errors


def fixture_note() -> str:
    return """# Phase 14 Compile Shard Matrix Evidence

This note records the exact current-master Phase 14 compile-shard coverage verified for lane `P14-L09`.

## Current head

- verified on `2026-05-26`
- current `master` head observed during this lane: `9c4f5255d15055642bb440d32b408ffcc1d20f5e`
- current `master` head subject: `test(scripts/zigux): add Phase 10 review-guide packet guard`

## Exact current coverage

- `PHASE14_COMPILE_SHARD_TOTAL=6`
- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`
- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`
- shared gate: `make -C zigux phase14-validate`
- focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`
- current workflow route: `run: make -C zigux phase14-validate`
- current broader wrapper gap: `phase14-smoke`, `phase14-test`, and `phase14` remain absent from the readable `zigux/Makefile` route layer
"""


def fixture_survey() -> str:
    return """# Phase 14 Compile Shard Matrix Survey

- `PHASE14_COMPILE_SHARD_TOTAL=6`
- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`
- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`
- shared gate: `make -C zigux phase14-validate`
- focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`
"""


def fixture_manifest() -> str:
    return json.dumps(
        {
            "smoke_commands": ["make -C zigux phase14-validate"],
            "smoke_shard_commands": [
                "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"
            ],
            "compile_shards": EXPECTED_COMPILE_SHARDS,
        },
        indent=2,
    ) + "\n"


def fixture_build() -> str:
    return (
        'const std = @import("std"); '
        'pub fn build(b: *std.Build) void { '
        'const target = b.standardTargetOptions(.{}); '
        'const optimize = b.standardOptimizeOption(.{}); '
        'const phase14_end_to_end_smoke_module = b.createModule(.{ .root_source_file = b.path("phase14_end_to_end_smoke_survey.zig"), .target = target, .optimize = optimize, }); '
        'const phase14_ring_buffer_survey_module = b.createModule(.{ .root_source_file = b.path("phase14_ring_buffer_survey.zig"), .target = target, .optimize = optimize, }); '
        'const phase14_rcu_tree_survey_module = b.createModule(.{ .root_source_file = b.path("phase14_rcu_tree_survey.zig"), .target = target, .optimize = optimize, }); '
        'const workqueue_bridge_module = b.createModule(.{ .root_source_file = b.path("../../kernel/workqueue_bridge.zig"), .target = target, .optimize = optimize, }); '
        'const skbuff_bridge_module = b.createModule(.{ .root_source_file = b.path("../../net/core/skbuff_bridge.zig"), .target = target, .optimize = optimize, }); '
        'const phase14_workqueue_bridge_module = b.createModule(.{ .root_source_file = b.path("phase14_workqueue_bridge.zig"), .target = target, .optimize = optimize, }); '
        'const phase14_workqueue_reviewability_module = b.createModule(.{ .root_source_file = b.path("phase14_workqueue_reviewability.zig"), .target = target, .optimize = optimize, }); '
        'const phase14_skbuff_bridge_module = b.createModule(.{ .root_source_file = b.path("phase14_skbuff_bridge.zig"), .target = target, .optimize = optimize, }); '
        'const phase14_workqueue_bridge_tests = b.addTest(.{ .name = "phase14-workqueue-bridge-tests", .root_module = phase14_workqueue_bridge_module, }); '
        'const phase14_workqueue_reviewability_tests = b.addTest(.{ .name = "phase14-workqueue-reviewability-tests", .root_module = phase14_workqueue_reviewability_module, }); '
        'const phase14_skbuff_bridge_tests = b.addTest(.{ .name = "phase14-skbuff-bridge-tests", .root_module = phase14_skbuff_bridge_module, }); '
        'const phase14_ring_buffer_survey_tests = b.addTest(.{ .name = "phase14-ring-buffer-survey-tests", .root_module = phase14_ring_buffer_survey_module, }); '
        'const phase14_rcu_tree_survey_tests = b.addTest(.{ .name = "phase14-rcu-tree-survey-tests", .root_module = phase14_rcu_tree_survey_module, }); '
        'const phase14_end_to_end_smoke_tests = b.addTest(.{ .name = "phase14-end-to-end-smoke-tests", .root_module = phase14_end_to_end_smoke_module, }); '
        'const smoke_step = b.step("phase14-smoke", "Run the focused Phase 14 smoke shard"); '
        'const test_step = b.step("test", "Run the full Phase 14 bounded bridge and survey bundle"); }'
    )


def fixture_makefile() -> str:
    return """PHONY += phase14-validate

.PHONY: phase14-validate

phase14-validate:
\tcd .. && python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
\tcd .. && python3 scripts/zigux/check-phase14-shared-smoke-route.py
"""


def fixture_workflow() -> str:
    return """- name: Self-test current Phase 14 shared smoke route checker
  run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
- name: Run current Phase 14 validate route
  run: make -C zigux phase14-validate
"""


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, NOTE_PATH, fixture_note())
    write_text(root, SURVEY_PATH, fixture_survey())
    write_text(root, MANIFEST_PATH, fixture_manifest())
    write_text(root, BUILD_PATH, fixture_build())
    write_text(root, MAKEFILE_PATH, fixture_makefile())
    write_text(root, WORKFLOW_PATH, fixture_workflow())


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-compile-shard-matrix-evidence-"))
    try:
        write_fixture_tree(base)
        if errors := check(base):
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        (base / NOTE_PATH).write_text(fixture_note().replace(EXPECTED_HEAD_SHA, "deadbeef", 1), encoding="utf-8")
        if not any(EXPECTED_HEAD_SHA in error for error in check(base)):
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            print("expected head-sha drift to fail")
            return 1

        write_fixture_tree(base)
        (base / MANIFEST_PATH).write_text(fixture_manifest().replace("focused_and_full_bundle", "full_bundle_only", 1), encoding="utf-8")
        if not any("manifest_value_mismatch:compile_shards" in error for error in check(base)):
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            print("expected compile-shard drift to fail")
            return 1

        write_fixture_tree(base)
        (base / BUILD_PATH).write_text(fixture_build().replace('phase14-smoke', 'phase14-smoke-missing', 1), encoding="utf-8")
        if not any("phase14-smoke" in error for error in check(base)):
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            print("expected build-shard drift to fail")
            return 1

        write_fixture_tree(base)
        (base / MAKEFILE_PATH).write_text(fixture_makefile() + "\nphase14-smoke:\n\ttrue\n", encoding="utf-8")
        if not any("forbidden_marker:zigux/Makefile:phase14-smoke:" in error for error in check(base)):
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            print("expected makefile wrapper drift to fail")
            return 1

        write_fixture_tree(base)
        (base / WORKFLOW_PATH).write_text(fixture_workflow() + "\n- name: Wrong route\n  run: make -C zigux phase14-smoke\n", encoding="utf-8")
        if not any("forbidden_marker:.github/workflows/zigux-bootstrap.yml:run: make -C zigux phase14-smoke" in error for error in check(base)):
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            print("expected workflow drift to fail")
            return 1

        print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=pass")
        print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST_CASE_COUNT=5")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if errors := check(args.root):
        print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE=fail")
        print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_ISSUES_END")
        return 1

    print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE=pass")
    print("PHASE14_COMPILE_SHARD_TOTAL=6")
    print("PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1")
    print("PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5")
    print("PHASE14_SHARED_SMOKE_GATE_COUNT=1")
    print("PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
