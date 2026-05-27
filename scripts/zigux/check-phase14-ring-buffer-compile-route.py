#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=ring_buffer_compile_route

Fail-closed checker for the Phase 14 ring-buffer compile-route packet.

This guard keeps the compile-shard story honest across the dedicated
ring-buffer survey note and the shared Phase 14 smoke manifest without
promoting the lane beyond its study-only maintenance posture.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=ring_buffer_compile_route"
NOTE_PATH = Path("Documentation/zigux/phase14-ring-buffer-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase14_end_to_end_smoke_manifest.json")

NOTE_MARKERS = [
    "current public raw-file readback now recovers `zigux/tests/phase14_ring_buffer_survey.zig`, while `zigux/tests/phase14_build.zig` still does not return through this lane's exact contents path",
    "`zig test zigux/tests/phase14_ring_buffer_survey.zig`",
    "`zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`",
    "shared smoke manifest still records that focused build-shard command as historical vocabulary only",
]

REQUIRED_MANIFEST_VALUES = {
    ("smoke_shard_commands",): [
        "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"
    ],
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

    ring_row = None
    for row in compile_shards:
        if isinstance(row, dict) and row.get("label") == "phase14-ring-buffer-survey-tests":
            ring_row = row
            break
    if ring_row is None:
        errors.append("missing_compile_shard_label:phase14-ring-buffer-survey-tests")
    else:
        if ring_row.get("coverage") != "full_bundle_only":
            errors.append(
                "compile_shard_coverage_mismatch:phase14-ring-buffer-survey-tests:"
                f"expected=full_bundle_only:actual={ring_row.get('coverage')!r}"
            )
        if ring_row.get("root_source") != "phase14_ring_buffer_survey.zig":
            errors.append(
                "compile_shard_root_source_mismatch:phase14-ring-buffer-survey-tests:"
                f"expected='phase14_ring_buffer_survey.zig':actual={ring_row.get('root_source')!r}"
            )

    anchor_packets = manifest.get("anchor_packets")
    if not isinstance(anchor_packets, list):
        errors.append("missing_manifest_key:anchor_packets")
        return

    ring_anchor = None
    for row in anchor_packets:
        if isinstance(row, dict) and row.get("anchor") == "kernel/trace/ring_buffer.c":
            ring_anchor = row
            break
    if ring_anchor is None:
        errors.append("missing_anchor_packet:kernel/trace/ring_buffer.c")
        return

    expected_anchor_fields = {
        "lane_key": "P14-L08",
        "manifest_path": "zigux/tests/phase14_ring_buffer_manifest.json",
        "survey_note_path": "Documentation/zigux/phase14-ring-buffer-survey.md",
        "blocked_gap": "phase14-ring-buffer-zig-port-blocker",
    }
    for key, expected in expected_anchor_fields.items():
        actual = ring_anchor.get(key)
        if actual != expected:
            errors.append(
                f"anchor_packet_mismatch:{key}:expected={expected!r}:actual={actual!r}"
            )


def check(root: Path) -> list[str]:
    errors: list[str] = []

    if MARKER not in Path(__file__).read_text(encoding="utf-8"):
        errors.append("missing_checker_marker:self")

    required_paths = [NOTE_PATH, MANIFEST_PATH]
    for rel in required_paths:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    note = read_text(root, NOTE_PATH)
    require_markers(errors, NOTE_PATH, note, NOTE_MARKERS)

    manifest_text = read_text(root, MANIFEST_PATH)
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{MANIFEST_PATH.as_posix()}:{exc.msg}")
        return errors

    require_manifest_values(errors, manifest)
    require_compile_shard(errors, manifest)
    return errors


def fixture_note() -> str:
    return "\n".join(
        [
            "# Phase 14 Ring Buffer Survey",
            *NOTE_MARKERS,
            "",
        ]
    )


def fixture_manifest() -> str:
    payload = {
        "smoke_shard_commands": [
            "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig"
        ],
        "compile_shards": [
            {
                "label": "phase14-ring-buffer-survey-tests",
                "coverage": "full_bundle_only",
                "root_source": "phase14_ring_buffer_survey.zig",
            }
        ],
        "anchor_packets": [
            {
                "lane_key": "P14-L08",
                "anchor": "kernel/trace/ring_buffer.c",
                "manifest_path": "zigux/tests/phase14_ring_buffer_manifest.json",
                "survey_note_path": "Documentation/zigux/phase14-ring-buffer-survey.md",
                "blocked_gap": "phase14-ring-buffer-zig-port-blocker",
            }
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, NOTE_PATH, fixture_note())
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
    base = Path(tempfile.mkdtemp(prefix="phase14-ring-buffer-compile-route-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_RING_BUFFER_COMPILE_ROUTE_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        remove_line(base, NOTE_PATH, NOTE_MARKERS[0])
        if not any(NOTE_MARKERS[0] in error for error in check(base)):
            print("PHASE14_RING_BUFFER_COMPILE_ROUTE_SELF_TEST=fail")
            print("expected note raw-readback marker drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["compile_shards"][0]["coverage"] = "focused_and_full_bundle"
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith(
                "compile_shard_coverage_mismatch:phase14-ring-buffer-survey-tests"
            )
            for error in check(base)
        ):
            print("PHASE14_RING_BUFFER_COMPILE_ROUTE_SELF_TEST=fail")
            print("expected compile-shard coverage drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["anchor_packets"][0]["lane_key"] = "P14-L09"
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith("anchor_packet_mismatch:lane_key:") for error in check(base)
        ):
            print("PHASE14_RING_BUFFER_COMPILE_ROUTE_SELF_TEST=fail")
            print("expected anchor lane drift to fail")
            return 1

        print("PHASE14_RING_BUFFER_COMPILE_ROUTE_SELF_TEST=pass")
        print("PHASE14_RING_BUFFER_COMPILE_ROUTE_SELF_TEST_CASE_COUNT=3")
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
        print("PHASE14_RING_BUFFER_COMPILE_ROUTE=fail")
        print("PHASE14_RING_BUFFER_COMPILE_ROUTE_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_RING_BUFFER_COMPILE_ROUTE_ISSUES_END")
        return 1

    print("PHASE14_RING_BUFFER_COMPILE_ROUTE=pass")
    print(f"PHASE14_RING_BUFFER_COMPILE_ROUTE_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())