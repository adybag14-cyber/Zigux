#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")
BUILD_PATH = Path("zigux/tests/phase14_build.zig")

EXPECTED_COVERAGE = {
    "phase14-workqueue-bridge-tests": "full_bundle_only",
    "phase14-workqueue-reviewability-tests": "full_bundle_only",
    "phase14-skbuff-bridge-tests": "full_bundle_only",
    "phase14-ring-buffer-survey-tests": "full_bundle_only",
    "phase14-rcu-tree-survey-tests": "full_bundle_only",
    "phase14-end-to-end-smoke-tests": "focused_and_full_bundle",
}


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    manifest_path = root / MANIFEST_PATH
    build_path = root / BUILD_PATH

    if not manifest_path.exists():
        return [f"repo:missing_manifest:{MANIFEST_PATH.as_posix()}"]
    if not build_path.exists():
        return [f"repo:missing_build:{BUILD_PATH.as_posix()}"]

    manifest = _read_json(manifest_path)
    if not isinstance(manifest, dict):
        return ["manifest:not_object"]

    compile_shards = manifest.get("compile_shards")
    if not isinstance(compile_shards, list):
        failures.append("manifest:missing_compile_shards")
        return failures

    compile_shard_counts = manifest.get("compile_shard_counts")
    if not isinstance(compile_shard_counts, dict):
        failures.append("manifest:missing_compile_shard_counts")
        return failures

    build_text = _read_text(build_path)
    seen_labels: set[str] = set()
    coverage_counts: dict[str, int] = {}

    for index, shard in enumerate(compile_shards):
        if not isinstance(shard, dict):
            failures.append(f"manifest:compile_shard_not_object:{index}")
            continue

        label = shard.get("label")
        root_source = shard.get("root_source")
        coverage = shard.get("coverage")

        if not isinstance(label, str) or not label:
            failures.append(f"manifest:compile_shard_missing_label:{index}")
            continue
        if not isinstance(root_source, str) or not root_source:
            failures.append(f"manifest:compile_shard_missing_root_source:{label}")
            continue
        if not isinstance(coverage, str) or not coverage:
            failures.append(f"manifest:compile_shard_missing_coverage:{label}")
            continue

        if label in seen_labels:
            failures.append(f"manifest:compile_shard_duplicate_label:{label}")
            continue
        seen_labels.add(label)

        expected_coverage = EXPECTED_COVERAGE.get(label)
        if expected_coverage is None:
            failures.append(f"manifest:compile_shard_unexpected_label:{label}")
        elif coverage != expected_coverage:
            failures.append(
                f"manifest:compile_shard_wrong_coverage:{label}:expected={expected_coverage}:actual={coverage}"
            )

        coverage_counts[coverage] = coverage_counts.get(coverage, 0) + 1

        if label not in build_text:
            failures.append(f"build:missing_label:{label}")
        if root_source not in build_text:
            failures.append(f"build:missing_root_source:{root_source}")

    missing_labels = sorted(set(EXPECTED_COVERAGE) - seen_labels)
    for label in missing_labels:
        failures.append(f"manifest:compile_shard_missing_expected_label:{label}")

    total = compile_shard_counts.get("total")
    if total != len(compile_shards):
        failures.append(
            f"manifest:compile_shard_counts_total_mismatch:expected={len(compile_shards)}:actual={total}"
        )

    for coverage, expected_count in {
        "focused_and_full_bundle": 1,
        "full_bundle_only": 5,
    }.items():
        actual_count = coverage_counts.get(coverage, 0)
        manifest_count = compile_shard_counts.get(coverage)
        if actual_count != expected_count:
            failures.append(
                f"manifest:compile_shard_expected_distribution:{coverage}:expected={expected_count}:actual={actual_count}"
            )
        if manifest_count != actual_count:
            failures.append(
                f"manifest:compile_shard_counts_distribution_mismatch:{coverage}:expected={actual_count}:actual={manifest_count}"
            )

    smoke_shard_present = 'b.step("phase14-smoke"' in build_text or 'b.step("phase14-smoke", "Run the focused Phase 14 smoke shard")' in build_text
    if not smoke_shard_present:
        failures.append("build:missing_phase14_smoke_step")

    return failures


def _sample_manifest() -> str:
    return json.dumps(
        {
            "lane_key": "P14-L03",
            "phase": "Phase 14",
            "surveyed_commit": "sample-current-master",
            "compile_shards": [
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
            ],
            "compile_shard_counts": {
                "total": 6,
                "focused_and_full_bundle": 1,
                "full_bundle_only": 5,
            },
        },
        indent=2,
    )


def _sample_build() -> str:
    return """const std = @import(\"std\");

pub fn build(b: *std.Build) void {
    const phase14_workqueue_bridge_tests = b.addTest(.{ .name = \"phase14-workqueue-bridge-tests\", .root_source_file = b.path(\"phase14_workqueue_bridge.zig\") });
    _ = phase14_workqueue_bridge_tests;
    const phase14_workqueue_reviewability_tests = b.addTest(.{ .name = \"phase14-workqueue-reviewability-tests\", .root_source_file = b.path(\"phase14_workqueue_reviewability.zig\") });
    _ = phase14_workqueue_reviewability_tests;
    const phase14_skbuff_bridge_tests = b.addTest(.{ .name = \"phase14-skbuff-bridge-tests\", .root_source_file = b.path(\"phase14_skbuff_bridge.zig\") });
    _ = phase14_skbuff_bridge_tests;
    const phase14_ring_buffer_survey_tests = b.addTest(.{ .name = \"phase14-ring-buffer-survey-tests\", .root_source_file = b.path(\"phase14_ring_buffer_survey.zig\") });
    _ = phase14_ring_buffer_survey_tests;
    const phase14_rcu_tree_survey_tests = b.addTest(.{ .name = \"phase14-rcu-tree-survey-tests\", .root_source_file = b.path(\"phase14_rcu_tree_survey.zig\") });
    _ = phase14_rcu_tree_survey_tests;
    const phase14_end_to_end_smoke_tests = b.addTest(.{ .name = \"phase14-end-to-end-smoke-tests\", .root_source_file = b.path(\"phase14_end_to_end_smoke_survey.zig\") });
    _ = phase14_end_to_end_smoke_tests;
    const smoke_step = b.step(\"phase14-smoke\", \"Run the focused Phase 14 smoke shard\");
    _ = smoke_step;
}
"""


def _seed(root: Path) -> None:
    _write_text(root / MANIFEST_PATH, _sample_manifest())
    _write_text(root / BUILD_PATH, _sample_build())


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase14_compile_shard_matrix_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")

        missing_counts_root = root / "missing_counts"
        _seed(missing_counts_root)
        manifest = json.loads(_read_text(missing_counts_root / MANIFEST_PATH))
        manifest.pop("compile_shard_counts", None)
        _write_text(missing_counts_root / MANIFEST_PATH, json.dumps(manifest, indent=2))
        failures = collect_failures(missing_counts_root)
        if failures != ["manifest:missing_compile_shard_counts"]:
            raise AssertionError(f"unexpected missing-counts failure: {failures}")

        bad_coverage_root = root / "bad_coverage"
        _seed(bad_coverage_root)
        manifest = json.loads(_read_text(bad_coverage_root / MANIFEST_PATH))
        manifest["compile_shards"][0]["coverage"] = "focused_and_full_bundle"
        _write_text(bad_coverage_root / MANIFEST_PATH, json.dumps(manifest, indent=2))
        failures = collect_failures(bad_coverage_root)
        expected = [
            "manifest:compile_shard_wrong_coverage:phase14-workqueue-bridge-tests:expected=full_bundle_only:actual=focused_and_full_bundle",
            "manifest:compile_shard_expected_distribution:focused_and_full_bundle:expected=1:actual=2",
            "manifest:compile_shard_counts_distribution_mismatch:focused_and_full_bundle:expected=2:actual=1",
            "manifest:compile_shard_expected_distribution:full_bundle_only:expected=5:actual=4",
            "manifest:compile_shard_counts_distribution_mismatch:full_bundle_only:expected=4:actual=5",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected bad-coverage failure: {failures}")

        missing_build_root = root / "missing_build_label"
        _seed(missing_build_root)
        _write_text(
            missing_build_root / BUILD_PATH,
            _sample_build().replace('\"phase14-ring-buffer-survey-tests\"', '\"phase14-ring-buffer-other-tests\"', 1),
        )
        failures = collect_failures(missing_build_root)
        if failures != ["build:missing_label:phase14-ring-buffer-survey-tests"]:
            raise AssertionError(f"unexpected missing-build failure: {failures}")

    print("PHASE14_COMPILE_SHARD_MATRIX_SELF_TEST=pass")
    print("PHASE14_COMPILE_SHARD_MATRIX_SELF_TEST_CASE_COUNT=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 14 shared smoke manifest keeps its compile-shard matrix aligned with the live build file."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE14_COMPILE_SHARD_MATRIX=pass")
    print("PHASE14_COMPILE_SHARD_LABEL_COUNT=6")
    print("PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1")
    print("PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
