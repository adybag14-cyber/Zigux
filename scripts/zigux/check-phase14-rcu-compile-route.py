#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=rcu_compile_route

Fail-closed checker for the Phase 14 RCU compile-route packet.

This guard keeps the compile-shard story honest across the dedicated
RCU survey note, the shared Phase 14 smoke manifest, and the focused
Phase 14 build shard without promoting the anchor beyond its current
freeze-in-C posture.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=rcu_compile_route"
CHECKER_PATH = "scripts/zigux/check-phase14-rcu-compile-route.py"
EXPECTED_SURVEYED_COMMIT = "4c889233d157960514b241bcd5aff7cac5fda312"
NOTE_PATH = Path("Documentation/zigux/phase14-rcu-tree-survey.md")
BUILD_PATH = Path("zigux/tests/phase14_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")

NOTE_MARKERS = [
    "- dedicated compile-route guard surface:",
    "  - `scripts/zigux/check-phase14-rcu-compile-route.py`",
    "- packet-local rerun vocabulary that public fallback now corroborates, even though this lane still lacks a local exact-replay environment on current `master`:",
    "  - `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all`",
    "  - `zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
]

BUILD_MARKERS = [
    'const phase14_rcu_tree_survey_module = b.createModule(.{ .root_source_file = b.path("phase14_rcu_tree_survey.zig"), .target = target, .optimize = optimize, });',
    'const phase14_rcu_tree_survey_tests = b.addTest(.{ .name = "phase14-rcu-tree-survey-tests", .root_module = phase14_rcu_tree_survey_module, });',
    'const run_phase14_rcu_tree_survey_tests = b.addRunArtifact(phase14_rcu_tree_survey_tests);',
    'test_step.dependOn(&run_phase14_rcu_tree_survey_tests.step);',
]

REQUIRED_MANIFEST_VALUES = {
    ("smoke_shard_commands",): [
        "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"
    ],
}

REQUIRED_COMPILE_SHARD = {
    "label": "phase14-rcu-tree-survey-tests",
    "root_source": "phase14_rcu_tree_survey.zig",
    "coverage": "full_bundle_only",
}

REQUIRED_ANCHOR_FIELDS = {
    "lane_key": "P14-L16",
    "anchor": "kernel/rcu/tree.c",
    "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
    "manifest_path": "zigux/tests/phase14_rcu_tree_manifest.json",
    "survey_note_path": "Documentation/zigux/phase14-rcu-tree-survey.md",
    "blocked_gap": "phase14-rcu-tree-bridge-blocker",
}


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    if not path.exists():
        raise FileNotFoundError(rel.as_posix())
    return path.read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], rel: Path, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def lookup_path(payload: object, path: tuple[str, ...]) -> object:
    current = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise KeyError(".".join(path))
        current = current[key]
    return current


def require_manifest_values(errors: list[str], manifest: object) -> None:
    for path, expected in REQUIRED_MANIFEST_VALUES.items():
        try:
            actual = lookup_path(manifest, path)
        except KeyError:
            errors.append(f"missing_manifest_key:{'.'.join(path)}")
            continue
        if actual != expected:
            errors.append(
                "manifest_value_mismatch:"
                f"{'.'.join(path)}:expected={expected!r}:actual={actual!r}"
            )


def require_compile_shard(errors: list[str], manifest: object) -> None:
    if not isinstance(manifest, dict):
        errors.append("manifest_not_object")
        return

    compile_shards = manifest.get("compile_shards")
    if not isinstance(compile_shards, list):
        errors.append("missing_manifest_key:compile_shards")
        return

    rcu_row = None
    for row in compile_shards:
        if isinstance(row, dict) and row.get("label") == REQUIRED_COMPILE_SHARD["label"]:
            rcu_row = row
            break

    if rcu_row is None:
        errors.append(f"missing_compile_shard_label:{REQUIRED_COMPILE_SHARD['label']}")
        return

    for key, expected in REQUIRED_COMPILE_SHARD.items():
        actual = rcu_row.get(key)
        if actual != expected:
            errors.append(
                f"compile_shard_{key}_mismatch:{REQUIRED_COMPILE_SHARD['label']}:"
                f"expected={expected!r}:actual={actual!r}"
            )


def require_anchor_packet(errors: list[str], manifest: object) -> None:
    if not isinstance(manifest, dict):
        errors.append("manifest_not_object")
        return

    anchor_packets = manifest.get("anchor_packets")
    if not isinstance(anchor_packets, list):
        errors.append("missing_manifest_key:anchor_packets")
        return

    rcu_anchor = None
    for row in anchor_packets:
        if isinstance(row, dict) and row.get("anchor") == REQUIRED_ANCHOR_FIELDS["anchor"]:
            rcu_anchor = row
            break

    if rcu_anchor is None:
        errors.append(f"missing_anchor_packet:{REQUIRED_ANCHOR_FIELDS['anchor']}")
        return

    for key, expected in REQUIRED_ANCHOR_FIELDS.items():
        actual = rcu_anchor.get(key)
        if actual != expected:
            errors.append(
                f"anchor_packet_mismatch:{key}:expected={expected!r}:actual={actual!r}"
            )


def check(root: Path) -> list[str]:
    errors: list[str] = []

    if MARKER not in Path(__file__).read_text(encoding="utf-8"):
        errors.append("missing_checker_marker:self")

    required_paths = [NOTE_PATH, BUILD_PATH, MANIFEST_PATH]
    for rel in required_paths:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    note = read_text(root, NOTE_PATH)
    require_markers(errors, NOTE_PATH, note, NOTE_MARKERS)

    build = read_text(root, BUILD_PATH)
    require_markers(errors, BUILD_PATH, build, BUILD_MARKERS)

    manifest_text = read_text(root, MANIFEST_PATH)
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{MANIFEST_PATH.as_posix()}:{exc.msg}")
        return errors

    require_manifest_values(errors, manifest)
    require_compile_shard(errors, manifest)
    require_anchor_packet(errors, manifest)
    return errors


def fixture_note() -> str:
    return "\n".join([
        "# Phase 14 RCU Tree Survey",
        *NOTE_MARKERS,
        "",
    ])


def fixture_build() -> str:
    return " ".join(BUILD_MARKERS) + "\n"


def fixture_manifest() -> str:
    payload = {
        "smoke_shard_commands": [
            "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"
        ],
        "compile_shards": [REQUIRED_COMPILE_SHARD],
        "anchor_packets": [REQUIRED_ANCHOR_FIELDS],
    }
    return json.dumps(payload, indent=2) + "\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, NOTE_PATH, fixture_note())
    write_text(root, BUILD_PATH, fixture_build())
    write_text(root, MANIFEST_PATH, fixture_manifest())


def remove_line(root: Path, rel: Path, marker: str) -> None:
    text = read_text(root, rel)
    updated = text.replace(marker + "\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    write_text(root, rel, updated)


def write_manifest_payload(root: Path, payload: object) -> None:
    write_text(root, MANIFEST_PATH, json.dumps(payload, indent=2) + "\n")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-rcu-compile-route-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_RCU_COMPILE_ROUTE_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        remove_line(base, NOTE_PATH, NOTE_MARKERS[1])
        if not any(NOTE_MARKERS[1] in error for error in check(base)):
            print("PHASE14_RCU_COMPILE_ROUTE_SELF_TEST=fail")
            print("expected note checker marker drift to fail")
            return 1

        write_fixture_tree(base)
        remove_line(base, BUILD_PATH, BUILD_MARKERS[2])
        if not any(BUILD_MARKERS[2] in error for error in check(base)):
            print("PHASE14_RCU_COMPILE_ROUTE_SELF_TEST=fail")
            print("expected build route drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["compile_shards"][0]["coverage"] = "focused_and_full_bundle"
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith("compile_shard_coverage_mismatch:phase14-rcu-tree-survey-tests")
            for error in check(base)
        ):
            print("PHASE14_RCU_COMPILE_ROUTE_SELF_TEST=fail")
            print("expected compile-shard coverage drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["anchor_packets"][0]["lane_key"] = "P14-L12"
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith("anchor_packet_mismatch:lane_key:") for error in check(base)
        ):
            print("PHASE14_RCU_COMPILE_ROUTE_SELF_TEST=fail")
            print("expected anchor lane drift to fail")
            return 1

        print("PHASE14_RCU_COMPILE_ROUTE_SELF_TEST=pass")
        print("PHASE14_RCU_COMPILE_ROUTE_SELF_TEST_CASE_COUNT=4")
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

    errors = check(args.root)
    if errors:
        print("PHASE14_RCU_COMPILE_ROUTE=fail")
        print("PHASE14_RCU_COMPILE_ROUTE_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_RCU_COMPILE_ROUTE_ISSUES_END")
        return 1

    print("PHASE14_RCU_COMPILE_ROUTE=pass")
    print(f"PHASE14_RCU_COMPILE_ROUTE_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    print(f"PHASE14_RCU_COMPILE_ROUTE_BUILD_MARKER_COUNT={len(BUILD_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
