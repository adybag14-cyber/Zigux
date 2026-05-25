#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=skbuff_compile_route

Fail-closed checker for the validator-side Phase 14 skbuff compile-route packet.

This guard keeps the compile-route story honest across the dedicated skbuff survey
note, the shared Phase 14 smoke manifest, and the Phase 14 build shard without
reopening skbuff ownership or parity claims.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=skbuff_compile_route"
CHECKER_PATH = "scripts/zigux/check-phase14-skbuff-compile-route.py"
EXPECTED_SURVEYED_COMMIT = "f05e02445443e7743c3675a6f8ca4f70f6e736fb"
NOTE_PATH = Path("Documentation/zigux/phase14-skbuff-bridge-survey.md")
BUILD_PATH = Path("zigux/tests/phase14_build.zig")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")

NOTE_MARKERS = [
    "- current `master` exposes `zigux/tests/phase14_skbuff_bridge.zig`",
    "- current `master` exposes `zigux/tests/phase14_build.zig`",
    "- current `master` exposes `net/core/skbuff_bridge.zig`",
    "- current `master` exposes `zigux/tests/phase14_skbuff_bridge_manifest.json`",
    "- `zigux/tests/phase14_build.zig` wires `../../net/core/skbuff_bridge.zig` and `phase14_skbuff_bridge.zig` into the dedicated Phase 14 build shard, so there is now a live skbuff-local review route on current `master`",
    "- that route is still evidence for a bounded boundary packet only; it must not be restated as a parity claim while `phase14-skbuff-live-ownership-blocker` stays open",
]

BUILD_MARKERS = [
    'const skbuff_bridge_module = b.createModule(.{ .root_source_file = b.path("../../net/core/skbuff_bridge.zig"), .target = target, .optimize = optimize, });',
    'const phase14_skbuff_bridge_module = b.createModule(.{ .root_source_file = b.path("phase14_skbuff_bridge.zig"), .target = target, .optimize = optimize, });',
    'phase14_skbuff_bridge_module.addImport("skbuff_bridge", skbuff_bridge_module);',
    'const phase14_skbuff_bridge_tests = b.addTest(.{ .name = "phase14-skbuff-bridge-tests", .root_module = phase14_skbuff_bridge_module, });',
    'const run_phase14_skbuff_bridge_tests = b.addRunArtifact(phase14_skbuff_bridge_tests);',
    'test_step.dependOn(&run_phase14_skbuff_bridge_tests.step);',
]

REQUIRED_MANIFEST_VALUES = {
    ("smoke_shard_commands",): [
        "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"
    ],
}

REQUIRED_SHARED_SMOKE_SURFACES = [
    CHECKER_PATH,
    "Documentation/zigux/phase14-skbuff-bridge-survey.md",
    "zigux/tests/phase14_build.zig",
]

REQUIRED_SURVEY_SUMMARY_FLAGS = {
    "shared_manifest_records_skbuff_compile_route_checker": True,
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


def require_shared_smoke_surfaces(errors: list[str], manifest: object) -> None:
    if not isinstance(manifest, dict):
        errors.append("manifest_not_object")
        return

    shared_smoke_surfaces = manifest.get("shared_smoke_surfaces")
    if not isinstance(shared_smoke_surfaces, list):
        errors.append("missing_manifest_key:shared_smoke_surfaces")
        return

    for surface in REQUIRED_SHARED_SMOKE_SURFACES:
        if surface not in shared_smoke_surfaces:
            errors.append(f"missing_shared_smoke_surface:{surface}")


def require_survey_summary_flags(errors: list[str], manifest: object) -> None:
    if not isinstance(manifest, dict):
        errors.append("manifest_not_object")
        return

    survey_summary = manifest.get("survey_summary")
    if not isinstance(survey_summary, dict):
        errors.append("missing_manifest_key:survey_summary")
        return

    for key, expected in REQUIRED_SURVEY_SUMMARY_FLAGS.items():
        actual = survey_summary.get(key)
        if actual != expected:
            errors.append(
                "survey_summary_mismatch:"
                f"{key}:expected={expected!r}:actual={actual!r}"
            )


def require_compile_shard(errors: list[str], manifest: object) -> None:
    if not isinstance(manifest, dict):
        errors.append("manifest_not_object")
        return

    compile_shards = manifest.get("compile_shards")
    if not isinstance(compile_shards, list):
        errors.append("missing_manifest_key:compile_shards")
        return

    skbuff_row = None
    for row in compile_shards:
        if isinstance(row, dict) and row.get("label") == "phase14-skbuff-bridge-tests":
            skbuff_row = row
            break
    if skbuff_row is None:
        errors.append("missing_compile_shard_label:phase14-skbuff-bridge-tests")
    else:
        if skbuff_row.get("coverage") != "full_bundle_only":
            errors.append(
                "compile_shard_coverage_mismatch:phase14-skbuff-bridge-tests:"
                f"expected=full_bundle_only:actual={skbuff_row.get('coverage')!r}"
            )
        if skbuff_row.get("root_source") != "phase14_skbuff_bridge.zig":
            errors.append(
                "compile_shard_root_source_mismatch:phase14-skbuff-bridge-tests:"
                f"expected='phase14_skbuff_bridge.zig':actual={skbuff_row.get('root_source')!r}"
            )

    anchor_packets = manifest.get("anchor_packets")
    if not isinstance(anchor_packets, list):
        errors.append("missing_manifest_key:anchor_packets")
        return

    skbuff_anchor = None
    for row in anchor_packets:
        if isinstance(row, dict) and row.get("anchor") == "net/core/skbuff.c":
            skbuff_anchor = row
            break
    if skbuff_anchor is None:
        errors.append("missing_anchor_packet:net/core/skbuff.c")
        return

    expected_anchor_fields = {
        "lane_key": "P14-L11",
        "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
        "manifest_path": "zigux/tests/phase14_skbuff_bridge_manifest.json",
        "survey_note_path": "Documentation/zigux/phase14-skbuff-bridge-survey.md",
        "blocked_gap": "phase14-skbuff-live-ownership-blocker",
    }
    for key, expected in expected_anchor_fields.items():
        actual = skbuff_anchor.get(key)
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
    if "full_bundle_only" in note:
        errors.append("forbidden_note_text:full_bundle_only")

    build = read_text(root, BUILD_PATH)
    require_markers(errors, BUILD_PATH, build, BUILD_MARKERS)

    manifest_text = read_text(root, MANIFEST_PATH)
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{MANIFEST_PATH.as_posix()}:{exc.msg}")
        return errors

    require_manifest_values(errors, manifest)
    require_shared_smoke_surfaces(errors, manifest)
    require_survey_summary_flags(errors, manifest)
    require_compile_shard(errors, manifest)
    return errors


def fixture_note() -> str:
    return "\n".join([
        "# Phase 14 Skbuff Bridge Survey",
        *NOTE_MARKERS,
        "",
    ])


def fixture_build() -> str:
    return " ".join(BUILD_MARKERS) + "\n"


def fixture_manifest() -> str:
    payload = {
        "shared_smoke_surfaces": REQUIRED_SHARED_SMOKE_SURFACES,
        "smoke_shard_commands": [
            "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"
        ],
        "compile_shards": [
            {
                "label": "phase14-skbuff-bridge-tests",
                "coverage": "full_bundle_only",
                "root_source": "phase14_skbuff_bridge.zig",
            }
        ],
        "anchor_packets": [
            {
                "lane_key": "P14-L11",
                "anchor": "net/core/skbuff.c",
                "surveyed_commit": EXPECTED_SURVEYED_COMMIT,
                "manifest_path": "zigux/tests/phase14_skbuff_bridge_manifest.json",
                "survey_note_path": "Documentation/zigux/phase14-skbuff-bridge-survey.md",
                "blocked_gap": "phase14-skbuff-live-ownership-blocker",
            }
        ],
        "survey_summary": {
            "shared_manifest_records_skbuff_compile_route_checker": True,
        },
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
    base = Path(tempfile.mkdtemp(prefix="phase14-skbuff-compile-route-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_SKBUFF_COMPILE_ROUTE_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        remove_line(base, NOTE_PATH, NOTE_MARKERS[4])
        if not any(NOTE_MARKERS[4] in error for error in check(base)):
            print("PHASE14_SKBUFF_COMPILE_ROUTE_SELF_TEST=fail")
            print("expected note compile-route marker drift to fail")
            return 1

        write_fixture_tree(base)
        remove_line(base, BUILD_PATH, BUILD_MARKERS[2])
        if not any(BUILD_MARKERS[2] in error for error in check(base)):
            print("PHASE14_SKBUFF_COMPILE_ROUTE_SELF_TEST=fail")
            print("expected build import marker drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["compile_shards"][0]["coverage"] = "focused_and_full_bundle"
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith("compile_shard_coverage_mismatch:phase14-skbuff-bridge-tests")
            for error in check(base)
        ):
            print("PHASE14_SKBUFF_COMPILE_ROUTE_SELF_TEST=fail")
            print("expected compile-shard coverage drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["anchor_packets"][0]["lane_key"] = "P14-L12"
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith("anchor_packet_mismatch:lane_key:") for error in check(base)
        ):
            print("PHASE14_SKBUFF_COMPILE_ROUTE_SELF_TEST=fail")
            print("expected anchor lane drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["shared_smoke_surfaces"].remove(CHECKER_PATH)
        write_manifest_payload(base, manifest)
        if not any(
            error == f"missing_shared_smoke_surface:{CHECKER_PATH}" for error in check(base)
        ):
            print("PHASE14_SKBUFF_COMPILE_ROUTE_SELF_TEST=fail")
            print("expected shared smoke surface drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["survey_summary"]["shared_manifest_records_skbuff_compile_route_checker"] = False
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith("survey_summary_mismatch:shared_manifest_records_skbuff_compile_route_checker:")
            for error in check(base)
        ):
            print("PHASE14_SKBUFF_COMPILE_ROUTE_SELF_TEST=fail")
            print("expected survey summary drift to fail")
            return 1

        print("PHASE14_SKBUFF_COMPILE_ROUTE_SELF_TEST=pass")
        print("PHASE14_SKBUFF_COMPILE_ROUTE_SELF_TEST_CASE_COUNT=6")
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
        print("PHASE14_SKBUFF_COMPILE_ROUTE=fail")
        print("PHASE14_SKBUFF_COMPILE_ROUTE_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_SKBUFF_COMPILE_ROUTE_ISSUES_END")
        return 1

    print("PHASE14_SKBUFF_COMPILE_ROUTE=pass")
    print(f"PHASE14_SKBUFF_COMPILE_ROUTE_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    print(f"PHASE14_SKBUFF_COMPILE_ROUTE_BUILD_MARKER_COUNT={len(BUILD_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
