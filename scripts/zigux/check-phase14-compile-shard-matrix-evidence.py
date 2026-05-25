#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

EVIDENCE_PATH = Path("Documentation/zigux/phase14-compile-shard-matrix-evidence.md")
SURVEY_PATH = Path("Documentation/zigux/phase14-compile-shard-matrix-survey.md")
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

EVIDENCE_MARKERS = [
    "lane: `P14-L09`",
    "manifest `surveyed_commit`: `aba08e207f1742838c4b96b151b0a12d340b3676`",
    "shared gate: `make -C zigux phase14-validate`",
    "focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`",
    "PHASE14_COMPILE_SHARD_TOTAL=6",
    "PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1",
    "PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5",
    "PHASE14_SHARED_SMOKE_GATE_COUNT=1",
    "PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0",
]

SURVEY_MARKERS = [
    "- `PHASE14_COMPILE_SHARD_TOTAL=6`",
    "- shared gate: `make -C zigux phase14-validate`",
    "- focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`",
]

BUILD_MARKERS = [
    'const phase14_workqueue_bridge_tests = b.addTest(.{ .name = "phase14-workqueue-bridge-tests", .root_module = phase14_workqueue_bridge_module, });',
    'const phase14_workqueue_reviewability_tests = b.addTest(.{ .name = "phase14-workqueue-reviewability-tests", .root_module = phase14_workqueue_reviewability_module, });',
    'const phase14_skbuff_bridge_tests = b.addTest(.{ .name = "phase14-skbuff-bridge-tests", .root_module = phase14_skbuff_bridge_module, });',
    'const phase14_ring_buffer_survey_tests = b.addTest(.{ .name = "phase14-ring-buffer-survey-tests", .root_module = phase14_ring_buffer_survey_module, });',
    'const phase14_rcu_tree_survey_tests = b.addTest(.{ .name = "phase14-rcu-tree-survey-tests", .root_module = phase14_rcu_tree_survey_module, });',
    'const phase14_end_to_end_smoke_tests = b.addTest(.{ .name = "phase14-end-to-end-smoke-tests", .root_module = phase14_end_to_end_smoke_module, });',
    'const smoke_step = b.step("phase14-smoke", "Run the focused Phase 14 smoke shard");',
    'const test_step = b.step("test", "Run the full Phase 14 bounded bridge and survey bundle");',
]

MAKEFILE_MARKERS = [
    "phase14-validate:",
    "scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "scripts/zigux/validate-phase14.py --self-test",
    "scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 14 compile-shard matrix evidence note matches current bounded repo reality."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    return parser.parse_args()


def require_file(root: Path, rel: Path, failures: list[str]) -> Path | None:
    path = root / rel
    if not path.exists():
        failures.append(f"missing_file:{rel.as_posix()}")
        return None
    return path


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    evidence_path = require_file(root, EVIDENCE_PATH, failures)
    survey_path = require_file(root, SURVEY_PATH, failures)
    manifest_path = require_file(root, MANIFEST_PATH, failures)
    build_path = require_file(root, BUILD_PATH, failures)
    makefile_path = require_file(root, MAKEFILE_PATH, failures)
    if failures:
        return failures

    evidence = evidence_path.read_text(encoding="utf-8")
    survey = survey_path.read_text(encoding="utf-8")
    build = build_path.read_text(encoding="utf-8")
    makefile = makefile_path.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for marker in EVIDENCE_MARKERS:
        if marker not in evidence:
            failures.append(f"missing_marker:{EVIDENCE_PATH.as_posix()}:{marker}")
    for label, root_source, coverage in EXPECTED_ROWS:
        row = f"`{label}` -> `{root_source}` -> `{coverage}`"
        if row not in evidence:
            failures.append(f"missing_row:{EVIDENCE_PATH.as_posix()}:{label}")
    for marker in SURVEY_MARKERS:
        if marker not in survey:
            failures.append(f"missing_marker:{SURVEY_PATH.as_posix()}:{marker}")
    for marker in BUILD_MARKERS:
        if marker not in build:
            failures.append(f"missing_marker:{BUILD_PATH.as_posix()}:{marker}")
    for marker in MAKEFILE_MARKERS:
        if marker not in makefile:
            failures.append(f"missing_marker:{MAKEFILE_PATH.as_posix()}:{marker}")
    for forbidden in ("phase14-smoke:", "phase14-test:", "phase14:"):
        if forbidden in makefile:
            failures.append(f"unexpected_wrapper:{MAKEFILE_PATH.as_posix()}:{forbidden}")

    compile_shards = manifest.get("compile_shards", [])
    if len(compile_shards) != len(EXPECTED_ROWS):
        failures.append(f"unexpected_compile_shard_count:{len(compile_shards)}")
    actual_rows = [
        (row.get("label"), row.get("root_source"), row.get("coverage")) for row in compile_shards
    ]
    if actual_rows != EXPECTED_ROWS:
        failures.append("unexpected_compile_shard_rows")
    if manifest.get("smoke_commands") != ["make -C zigux phase14-validate"]:
        failures.append("unexpected_smoke_commands")
    if manifest.get("smoke_shard_commands") != ["zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"]:
        failures.append("unexpected_smoke_shard_commands")
    summary = manifest.get("survey_summary", {})
    expected_summary = {
        "phase14_make_target_present": True,
        "phase14_make_smoke_target_present": False,
        "phase14_build_has_shared_smoke_step": True,
        "phase14_build_has_smoke_shard_step": True,
        "phase14_validate_runs_skbuff_compile_route_checker": True,
        "shared_manifest_records_skbuff_compile_route_checker": True,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            failures.append(f"unexpected_summary:{key}:{summary.get(key)!r}")

    return failures


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    (root / EVIDENCE_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / SURVEY_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / MANIFEST_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / BUILD_PATH.parent).mkdir(parents=True, exist_ok=True)
    (root / MAKEFILE_PATH.parent).mkdir(parents=True, exist_ok=True)

    evidence_lines = [
        "# Phase 14 Compile Shard Matrix Evidence",
        "",
        "This note records the exact current `master` compile-shard evidence for the bounded Phase 14 shared smoke packet.",
        "",
        "## Current readback",
        "",
        "- lane: `P14-L09`",
        "- phase: `Phase 14`",
        "- manifest path: `zigux/tests/phase14_end_to_end_smoke_manifest.json`",
        "- manifest `surveyed_commit`: `aba08e207f1742838c4b96b151b0a12d340b3676`",
        "- shared gate: `make -C zigux phase14-validate`",
        "- focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`",
        "- readable current `zigux/Makefile` body still has `phase14-validate` and still omits `phase14-smoke`, `phase14-test`, and `phase14`",
        "- exact current matrix counts:",
        "- `PHASE14_COMPILE_SHARD_TOTAL=6`",
        "- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`",
        "- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`",
        "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
        "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
        "",
        "## Exact shard rows",
        "",
    ]
    evidence_lines.extend(f"- `{label}` -> `{root_source}` -> `{coverage}`" for label, root_source, coverage in EXPECTED_ROWS)
    (root / EVIDENCE_PATH).write_text("\n".join(evidence_lines) + "\n", encoding="utf-8")

    survey_lines = [
        "# Phase 14 Compile Shard Matrix Survey",
        "",
        "- `PHASE14_COMPILE_SHARD_TOTAL=6`",
        "- shared gate: `make -C zigux phase14-validate`",
        "- focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`",
    ]
    (root / SURVEY_PATH).write_text("\n".join(survey_lines) + "\n", encoding="utf-8")

    manifest = {
        "smoke_commands": ["make -C zigux phase14-validate"],
        "smoke_shard_commands": ["zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"],
        "compile_shards": [
            {"label": label, "root_source": root_source, "coverage": coverage}
            for label, root_source, coverage in EXPECTED_ROWS
        ],
        "survey_summary": {
            "phase14_make_target_present": True,
            "phase14_make_smoke_target_present": False,
            "phase14_build_has_shared_smoke_step": True,
            "phase14_build_has_smoke_shard_step": True,
            "phase14_validate_runs_skbuff_compile_route_checker": True,
            "shared_manifest_records_skbuff_compile_route_checker": True,
        },
    }
    (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    build_text = "\n".join(BUILD_MARKERS) + "\n"
    (root / BUILD_PATH).write_text(build_text, encoding="utf-8")

    makefile_text = "\n".join(
        [
            "phase14-validate:",
            "\tpython3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
            "\tpython3 scripts/zigux/validate-phase14.py --self-test",
            "\tpython3 scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
        ]
    ) + "\n"
    (root / MAKEFILE_PATH).write_text(makefile_text, encoding="utf-8")


def run_self_test() -> int:
    temp_root = Path(tempfile.mkdtemp(prefix="p14-l09-"))
    try:
        write_sample_root(temp_root)
        failures = validate(temp_root)
        if failures:
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            for failure in failures:
                print(failure)
            return 1

        build_path = temp_root / BUILD_PATH
        build_path.write_text(
            build_path.read_text(encoding="utf-8").replace(BUILD_MARKERS[2] + "\n", ""),
            encoding="utf-8",
        )
        negative = validate(temp_root)
        if not any(item == f"missing_marker:{BUILD_PATH.as_posix()}:{BUILD_MARKERS[2]}" for item in negative):
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            print("negative_case_missing")
            return 1

        write_sample_root(temp_root)
        manifest = json.loads((temp_root / MANIFEST_PATH).read_text(encoding="utf-8"))
        manifest["compile_shards"][5]["coverage"] = "full_bundle_only"
        (temp_root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        negative = validate(temp_root)
        if "unexpected_compile_shard_rows" not in negative:
            print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=fail")
            print("negative_manifest_case_missing")
            return 1

        write_sample_root(temp_root)
        print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST=pass")
        print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE_SELF_TEST_CASE_COUNT=6")
        return 0
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def main() -> int:
    args = parse_args()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        return 0
    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE14_COMPILE_SHARD_MATRIX_EVIDENCE=fail")
        for failure in failures:
            print(failure)
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
