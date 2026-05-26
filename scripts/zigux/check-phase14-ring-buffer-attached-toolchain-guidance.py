#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=ring_buffer_attached_toolchain_guidance

Fail-closed checker for the Phase 14 ring-buffer attached-toolchain and
environment-guidance packet.

This guard keeps the ring-buffer lane's study-only operational guidance
explicit without widening into shared-smoke or anchor-ownership claims.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=ring_buffer_attached_toolchain_guidance"
NOTE_PATH = Path("Documentation/zigux/phase14-ring-buffer-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase14_ring_buffer_manifest.json")

NOTE_MARKERS = [
    "## Attached Toolchain and Environment Guidance",
    "current guidance status: `packet_local_only`",
    "keep the attached Zig toolchain as ring-buffer-local replay support only when a checkout-capable Zigux tree is present beside it",
    "if a run only has GitHub readback plus the attached toolchain, record the toolchain as environment context and do not claim a fresh local replay for this packet",
    "checkout-capable attached-toolchain command examples, kept as packet-local vocabulary rather than shared-smoke proof:",
    "`/absolute/path/to/attached-zig/zig test zigux/tests/phase14_ring_buffer_survey.zig`",
    "`/absolute/path/to/attached-zig/zig build test --build-file zigux/tests/phase14_build.zig --summary all`",
    "these examples stay subordinate to the same study-only, no-parity, no-wrapper-restoration posture recorded above",
]

REQUIRED_MANIFEST_FIELDS = {
    "lane_key": "P14-L08",
    "phase": "Phase 14",
    "anchor": "kernel/trace/ring_buffer.c",
}

REQUIRED_GAP = {
    "id": "phase14-ring-buffer-maintenance-handoff",
    "status": "starter_landed",
    "kind": "maintenance_handoff",
    "zigux_destination": "Documentation/zigux/phase14-ring-buffer-survey.md",
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


def require_manifest(errors: list[str], manifest: object) -> None:
    if not isinstance(manifest, dict):
        errors.append("manifest_not_object")
        return

    for key, expected in REQUIRED_MANIFEST_FIELDS.items():
        actual = manifest.get(key)
        if actual != expected:
            errors.append(
                f"manifest_field_mismatch:{key}:expected={expected!r}:actual={actual!r}"
            )

    maintenance = manifest.get("maintenance_handoff")
    if not isinstance(maintenance, dict):
        errors.append("missing_manifest_key:maintenance_handoff")
    else:
        current_lane_posture = maintenance.get("current_lane_posture")
        if current_lane_posture != "maintenance_mode":
            errors.append(
                "maintenance_handoff_mismatch:current_lane_posture:"
                f"expected='maintenance_mode':actual={current_lane_posture!r}"
            )
        replay_before_trusting = maintenance.get("replay_before_trusting")
        expected_replay = [
            "zig test zigux/tests/phase14_ring_buffer_survey.zig",
            "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
        ]
        if replay_before_trusting != expected_replay:
            errors.append(
                "maintenance_handoff_mismatch:replay_before_trusting:"
                f"expected={expected_replay!r}:actual={replay_before_trusting!r}"
            )

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        errors.append("missing_manifest_key:gaps")
        return

    for gap in gaps:
        if not isinstance(gap, dict):
            continue
        if all(gap.get(key) == value for key, value in REQUIRED_GAP.items()):
            why_now = gap.get("why_now", "")
            if "explicit reopen conditions" not in why_now:
                errors.append(
                    "maintenance_gap_why_now_missing:'explicit reopen conditions'"
                )
            return
    errors.append(f"missing_gap:{REQUIRED_GAP['id']}")


def check(root: Path) -> list[str]:
    errors: list[str] = []

    if MARKER not in Path(__file__).read_text(encoding="utf-8"):
        errors.append("missing_checker_marker:self")

    for rel in [NOTE_PATH, MANIFEST_PATH]:
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

    require_manifest(errors, manifest)
    return errors


def fixture_note() -> str:
    return "# Phase 14 Ring Buffer Survey\n\n" + "\n".join(NOTE_MARKERS) + "\n"


def fixture_manifest() -> str:
    payload = {
        "lane_key": "P14-L08",
        "phase": "Phase 14",
        "anchor": "kernel/trace/ring_buffer.c",
        "maintenance_handoff": {
            "current_lane_posture": "maintenance_mode",
            "replay_before_trusting": [
                "zig test zigux/tests/phase14_ring_buffer_survey.zig",
                "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
            ],
        },
        "gaps": [
            {
                "id": "phase14-ring-buffer-maintenance-handoff",
                "status": "starter_landed",
                "kind": "maintenance_handoff",
                "zigux_destination": "Documentation/zigux/phase14-ring-buffer-survey.md",
                "why_now": "The parked packet now carries explicit reopen conditions, returned-public-readback truthfulness, and a future truthfulness-only target so later runs can keep the study-only posture disciplined without inventing a new bridge or audit seam.",
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
    base = Path(tempfile.mkdtemp(prefix="phase14-ring-buffer-attached-toolchain-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_RING_BUFFER_ATTACHED_TOOLCHAIN_GUIDANCE_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        remove_line(base, NOTE_PATH, NOTE_MARKERS[0])
        if not any(
            error.startswith(f"missing_marker:{NOTE_PATH.as_posix()}:## Attached Toolchain")
            for error in check(base)
        ):
            print("PHASE14_RING_BUFFER_ATTACHED_TOOLCHAIN_GUIDANCE_SELF_TEST=fail")
            print("expected note section header drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["maintenance_handoff"]["current_lane_posture"] = "blocked"
        write_manifest_payload(base, manifest)
        if not any(
            error.startswith(
                "maintenance_handoff_mismatch:current_lane_posture:expected='maintenance_mode'"
            )
            for error in check(base)
        ):
            print("PHASE14_RING_BUFFER_ATTACHED_TOOLCHAIN_GUIDANCE_SELF_TEST=fail")
            print("expected maintenance posture drift to fail")
            return 1

        write_fixture_tree(base)
        manifest = json.loads(fixture_manifest())
        manifest["gaps"][0]["why_now"] = "missing the intended reminder"
        write_manifest_payload(base, manifest)
        if "maintenance_gap_why_now_missing:'explicit reopen conditions'" not in check(base):
            print("PHASE14_RING_BUFFER_ATTACHED_TOOLCHAIN_GUIDANCE_SELF_TEST=fail")
            print("expected maintenance gap wording drift to fail")
            return 1

        print("PHASE14_RING_BUFFER_ATTACHED_TOOLCHAIN_GUIDANCE_SELF_TEST=pass")
        print("PHASE14_RING_BUFFER_ATTACHED_TOOLCHAIN_GUIDANCE_SELF_TEST_CASE_COUNT=4")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.write_sample_root is not None:
        write_fixture_tree(args.write_sample_root)
        return 0

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        print("PHASE14_RING_BUFFER_ATTACHED_TOOLCHAIN_GUIDANCE=fail")
        print("PHASE14_RING_BUFFER_ATTACHED_TOOLCHAIN_GUIDANCE_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_RING_BUFFER_ATTACHED_TOOLCHAIN_GUIDANCE_ISSUES_END")
        return 1

    print("PHASE14_RING_BUFFER_ATTACHED_TOOLCHAIN_GUIDANCE=pass")
    print(f"PHASE14_RING_BUFFER_ATTACHED_TOOLCHAIN_GUIDANCE_NOTE_MARKER_COUNT={len(NOTE_MARKERS)}")
    print("PHASE14_RING_BUFFER_ATTACHED_TOOLCHAIN_GUIDANCE_REQUIRED_PATH_COUNT=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
