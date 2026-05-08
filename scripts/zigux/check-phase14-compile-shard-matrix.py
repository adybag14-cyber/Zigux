#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=compile_shard_matrix

Fail-closed checker for the shared Phase 14 compile shard matrix.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

MARKER = "PHASE14_CHECK_PACKET=compile_shard_matrix"
MANIFEST_PATH = "zigux/tests/phase14_end_to_end_smoke_manifest.json"
BUILD_PATH = "zigux/tests/phase14_build.zig"
NOTE_PATH = "Documentation/zigux/phase14-end-to-end-smoke-survey.md"
EXPECTED_SHARDS = [
    ("phase14-workqueue-bridge-tests", "phase14_workqueue_bridge.zig", "full_bundle_only"),
    ("phase14-skbuff-bridge-tests", "phase14_skbuff_bridge.zig", "full_bundle_only"),
    ("phase14-ring-buffer-survey-tests", "phase14_ring_buffer_survey.zig", "full_bundle_only"),
    ("phase14-rcu-tree-survey-tests", "phase14_rcu_tree_survey.zig", "full_bundle_only"),
    ("phase14-end-to-end-smoke-tests", "phase14_end_to_end_smoke_survey.zig", "focused_and_full_bundle"),
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def compile_note_row(label: str, root_source: str, coverage: str) -> str:
    return f"- `{label}`: root `{root_source}`, coverage `{coverage}`"


def collect_compile_shards(manifest: dict) -> tuple[list[tuple[str, str, str]], list[str]]:
    raw = manifest.get("compile_shards")
    if not isinstance(raw, list):
        return [], ["phase14 manifest compile_shards payload is not a list"]
    rows: list[tuple[str, str, str]] = []
    errors: list[str] = []
    for index, shard in enumerate(raw):
        if not isinstance(shard, dict):
            errors.append(f"phase14 manifest compile_shard entry {index} is not an object")
            continue
        label = shard.get("label")
        root_source = shard.get("root_source")
        coverage = shard.get("coverage")
        if not isinstance(label, str) or not isinstance(root_source, str) or not isinstance(coverage, str):
            errors.append(f"phase14 manifest compile_shard entry {index} is missing a string label, root_source, or coverage")
            continue
        rows.append((label, root_source, coverage))
    return rows, errors


def check_dir(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / MANIFEST_PATH
    build_path = root / BUILD_PATH
    note_path = root / NOTE_PATH
    if not manifest_path.exists():
        return [f"missing file: {MANIFEST_PATH}"]
    if not build_path.exists():
        return [f"missing file: {BUILD_PATH}"]
    if not note_path.exists():
        return [f"missing file: {NOTE_PATH}"]

    manifest = json.loads(read_text(manifest_path))
    rows, row_errors = collect_compile_shards(manifest)
    errors.extend(row_errors)
    if rows != EXPECTED_SHARDS:
        errors.append("phase14 compile_shards matrix drifted from the current five-row compile packet")

    note_text = read_text(note_path)
    build_text = read_text(build_path)

    if note_text.count("coverage `focused_and_full_bundle`") != 1:
        errors.append("phase14 smoke note focused compile-shard count drifted from the current one-shard packet")
    if note_text.count("coverage `full_bundle_only`") != 4:
        errors.append("phase14 smoke note full-bundle-only compile count drifted from the current four-artifact packet")
    if build_text.count("b.addTest(.") != 5:
        errors.append("phase14 build bundle no longer declares the current five compile artifacts")
    if build_text.count("b.addRunArtifact(") != 5:
        errors.append("phase14 build bundle no longer wires the current five compile-artifact runs")

    forbidden_smoke_dependencies = [
        "smoke_step.dependOn(&run_phase14_workqueue_bridge_tests.step);",
        "smoke_step.dependOn(&run_phase14_skbuff_bridge_tests.step);",
        "smoke_step.dependOn(&run_phase14_ring_buffer_survey_tests.step);",
        "smoke_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);",
    ]
    for marker in forbidden_smoke_dependencies:
        if marker in build_text:
            errors.append("phase14 smoke shard stopped being dedicated to the shared end-to-end smoke survey")
            break

    for label, root_source, coverage in EXPECTED_SHARDS:
        row = compile_note_row(label, root_source, coverage)
        if row not in note_text:
            errors.append(f"missing compile-matrix row in {NOTE_PATH}: {row}")
        if label not in build_text:
            errors.append(f"missing compile-artifact label in {BUILD_PATH}: {label}")
        if root_source not in build_text:
            errors.append(f"missing compile-artifact root in {BUILD_PATH}: {root_source}")
    return errors


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        manifest = {
            "compile_shards": [
                {"label": label, "root_source": root_source, "coverage": coverage}
                for label, root_source, coverage in EXPECTED_SHARDS
            ]
        }
        write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        note_lines = [
            "# Phase 14 End-to-End Smoke Survey",
            "PHASE14_COMPILE_ARTIFACT_COUNT=5",
            "PHASE14_FOCUSED_SHARD_COUNT=1",
            "PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=4",
        ]
        note_lines.extend(compile_note_row(*row) for row in EXPECTED_SHARDS)
        write_text(root / NOTE_PATH, "\n".join(note_lines) + "\n")
        build_lines = [
            'const smoke_step = b.step("phase14-smoke", "Run the focused Phase 14 end-to-end smoke survey")',
            "smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);",
        ]
        for label, root_source, _coverage in EXPECTED_SHARDS:
            build_lines.append("b.addTest(.")
            build_lines.append("b.addRunArtifact(")
            build_lines.append(label)
            build_lines.append(root_source)
        write_text(root / BUILD_PATH, "\n".join(build_lines) + "\n")

        errors = check_dir(root)
        if errors:
            print("self-test expected success but failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1

        broken = json.loads(read_text(root / MANIFEST_PATH))
        broken["compile_shards"] = "not-a-list"
        write_text(root / MANIFEST_PATH, json.dumps(broken, indent=2) + "\n")
        errors = check_dir(root)
        if "phase14 manifest compile_shards payload is not a list" not in errors:
            print("self-test expected non-list compile_shards failure", file=sys.stderr)
            return 1

        manifest["compile_shards"] = [
            {"label": "phase14-workqueue-bridge-tests", "root_source": "phase14_workqueue_bridge.zig", "coverage": "focused_and_full_bundle"}
        ] + manifest["compile_shards"][1:]
        write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        errors = check_dir(root)
        if "phase14 compile_shards matrix drifted from the current five-row compile packet" not in errors:
            print("self-test expected compile-matrix drift failure", file=sys.stderr)
            return 1

        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    errors = check_dir(repo_root())
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("phase14 compile shard matrix validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
