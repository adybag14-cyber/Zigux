#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


SURVEYED_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

REQUIRED_FILES = [
    "include/zigux/notifier_abi.h",
    "zigux/bindings/notifier_abi.zig",
    "zigux/helpers/notifier_chain_view.zig",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/tests/phase13_notifier_list_reviewability.zig",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/build.zig",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    "zigux/Makefile",
]

ABI_MARKERS = [
    "pub const NotifierBlockRef = extern struct",
    "pub const RawNotifierHeadRef = extern struct",
    "pub const NotifierChainView = extern struct",
    "pub const NotifierChainSummary = extern struct",
    "pub const NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING: u32 = 16;",
]

C_HEADER_MARKERS = [
    "struct zigux_notifier_block_ref",
    "struct zigux_raw_notifier_head_ref",
    "struct zigux_notifier_chain_view",
    "struct zigux_notifier_chain_summary",
    "zigux_notifier_chain_view_from_head",
    "zigux_notifier_chain_view_valid",
    "zigux_notifier_chain_empty",
    "zigux_notifier_chain_length_bounded",
    "zigux_notifier_chain_summarize",
    "zigux_notifier_chain_has_nonincreasing_priority_order",
    "ZIGUX_NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING",
]

HELPER_MARKERS = [
    "pub fn viewFromHead",
    "pub fn isEmpty",
    "pub fn length",
    "pub fn summarize",
    "pub fn hasNonincreasingPriorityOrder",
    "NOTIFIER_CHAIN_FLAG_PRIORITY_NONINCREASING",
    "clears the priority-order flag when priorities rise",
]

REVIEWABILITY_MARKERS = [
    'test "phase13 notifier/list survey records the landed read-only generic notifier foothold"',
    'try std.testing.expectEqualStrings("P13-L19", manifest.lane_key);',
    'try std.testing.expect(std.mem.indexOf(u8, notifier_c_header_text, "zigux_notifier_chain_view_valid") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, notifier_c_header_text, "zigux_notifier_chain_summarize") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, notifier_c_header_text, "zigux_notifier_chain_has_nonincreasing_priority_order") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, notifier_helper_text, "pub fn hasNonincreasingPriorityOrder") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "`zigux_notifier_chain_has_nonincreasing_priority_order()`") != null);',
    'try std.testing.expect(std.mem.indexOf(u8, survey_note, "`hasNonincreasingPriorityOrder`") != null);',
    'try std.testing.expect(found_c_header_gap);',
]

BUILD_MARKERS = [
    "phase13-notifier-list-reviewability-tests",
    "phase13-notifier-chain-view-tests",
    "../bindings/notifier_abi.zig",
    "../helpers/notifier_chain_view.zig",
]

PHASE3_BUILD_MARKERS = [
    "../helpers/list_view.zig",
    "../helpers/hlist_view.zig",
    "../helpers/chrdev_notify_plan.zig",
]

SURVEY_MARKERS = [
    "lane key: `P13-L19`",
    "zigux/bindings/notifier_abi.zig",
    "include/zigux/notifier_abi.h",
    "`zigux_notifier_chain_view_valid()`",
    "reserved or zero-bounded views",
    "zigux/helpers/notifier_chain_view.zig",
    "`hasNonincreasingPriorityOrder`",
    "`zigux_notifier_chain_has_nonincreasing_priority_order()`",
    "keeps the direct priority-order convenience reviewable",
    "keeps the dedicated exported C header small",
    "registration, callback execution, SRCU, and blocking notifier semantics remain out of scope",
]

MAKE_MARKERS = [
    "phase13-validate:",
    "scripts/zigux/check-phase13-notifier-packet.py --self-test",
    "scripts/zigux/check-phase13-notifier-packet.py",
]

EXPECTED_STARTER_LANDED = {
    "phase13-build-gate",
    "phase13-notifier-list-reviewability-gate",
    "phase13-notifier-list-survey-note",
    "phase13-generic-notifier-abi-foothold",
    "phase13-generic-notifier-helper-foothold",
    "phase13-generic-notifier-c-header-foothold",
}

EXPECTED_PREEXISTING_PHASE3 = {
    "phase3-list-abi-and-view-surface",
    "phase3-list-view-helper-surface",
    "phase13-list-helper-api-companion-surface",
    "phase3-list-hlist-replay-surface",
}

EXPECTED_ANCHORS = [
    "include/linux/list.h",
    "include/linux/notifier.h",
    "include/linux/acpi_amd_wbrf.h",
    "include/net/dsa.h",
    "include/linux/watchdog.h",
]

REQUIRED_SURVEY_SUMMARY_FLAGS = [
    "landed_generic_notifier_abi_present",
    "landed_generic_notifier_build_surface_present",
    "landed_generic_notifier_helper_present",
    "landed_generic_notifier_c_header_surface_present",
    "preexisting_list_helper_api_companion_present",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _require_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def _check_repo(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(f"missing_file:{rel}")
    if missing:
        return missing

    abi_text = _read(root / "zigux/bindings/notifier_abi.zig")
    c_header_text = _read(root / "include/zigux/notifier_abi.h")
    helper_text = _read(root / "zigux/helpers/notifier_chain_view.zig")
    reviewability_text = _read(root / "zigux/tests/phase13_notifier_list_reviewability.zig")
    build_text = _read(root / "zigux/tests/phase13_build.zig")
    phase3_build_text = _read(root / "zigux/tests/build.zig")
    survey_text = _read(root / "Documentation/zigux/phase13-notifier-list-survey.md")
    make_text = _read(root / "zigux/Makefile")

    _require_markers(missing, "abi", abi_text, ABI_MARKERS)
    _require_markers(missing, "c_header", c_header_text, C_HEADER_MARKERS)
    _require_markers(missing, "helper", helper_text, HELPER_MARKERS)
    _require_markers(missing, "reviewability", reviewability_text, REVIEWABILITY_MARKERS)
    _require_markers(missing, "build", build_text, BUILD_MARKERS)
    _require_markers(missing, "phase3_build", phase3_build_text, PHASE3_BUILD_MARKERS)
    _require_markers(missing, "survey", survey_text, SURVEY_MARKERS)
    _require_markers(missing, "make", make_text, MAKE_MARKERS)

    manifest = json.loads(_read(root / "zigux/tests/phase13_notifier_list_manifest.json"))
    if manifest.get("lane_key") != "P13-L19":
        missing.append("manifest:lane_key")
    if manifest.get("phase") != "Phase 13":
        missing.append("manifest:phase")
    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not SURVEYED_COMMIT_RE.fullmatch(surveyed_commit):
        missing.append("manifest:surveyed_commit")
    elif f"last inspected current-master commit: `{surveyed_commit}`" not in survey_text:
        missing.append("survey:surveyed_commit")

    anchors = manifest.get("anchors")
    if anchors != EXPECTED_ANCHORS:
        missing.append("manifest:anchors")

    survey_summary = manifest.get("survey_summary")
    if not isinstance(survey_summary, dict):
        missing.append("manifest:survey_summary")
    else:
        for flag in REQUIRED_SURVEY_SUMMARY_FLAGS:
            if survey_summary.get(flag) is not True:
                missing.append(f"manifest:survey_summary:{flag}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        missing.append("manifest:gaps")
        return missing

    starter_landed = {
        gap.get("id")
        for gap in gaps
        if isinstance(gap, dict) and gap.get("status") == "starter_landed"
    }
    if starter_landed != EXPECTED_STARTER_LANDED:
        missing.append("manifest:starter_landed_set")

    preexisting_phase3 = {
        gap.get("id")
        for gap in gaps
        if isinstance(gap, dict) and gap.get("status") == "preexisting_phase3_surface"
    }
    if preexisting_phase3 != EXPECTED_PREEXISTING_PHASE3:
        missing.append("manifest:preexisting_phase3_set")

    c_header_gap = False
    helper_gap = False
    for gap in gaps:
        if not isinstance(gap, dict):
            continue
        if gap.get("id") == "phase13-generic-notifier-c-header-foothold":
            c_header_gap = gap.get("zigux_destination") == "include/zigux/notifier_abi.h"
        if gap.get("id") == "phase13-generic-notifier-helper-foothold":
            helper_gap = gap.get("zigux_destination") == "zigux/helpers/notifier_chain_view.zig"
    if not c_header_gap:
        missing.append("manifest:c_header_gap_destination")
    if not helper_gap:
        missing.append("manifest:helper_gap_destination")

    return missing


def _run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for rel in (
            "include/zigux",
            "zigux/bindings",
            "zigux/helpers",
            "zigux/tests",
            "Documentation/zigux",
            "zigux",
        ):
            (root / rel).mkdir(parents=True, exist_ok=True)

        surveyed_commit = "66b55d8a9a800345097f3c04b9f95130b1f8d0b8"
        (root / "zigux/bindings/notifier_abi.zig").write_text("\n".join(ABI_MARKERS) + "\n", encoding="utf-8")
        (root / "include/zigux/notifier_abi.h").write_text("\n".join(C_HEADER_MARKERS) + "\n", encoding="utf-8")
        (root / "zigux/helpers/notifier_chain_view.zig").write_text("\n".join(HELPER_MARKERS) + "\n", encoding="utf-8")
        (root / "zigux/tests/phase13_notifier_list_reviewability.zig").write_text("\n".join(REVIEWABILITY_MARKERS) + "\n", encoding="utf-8")
        (root / "zigux/tests/phase13_build.zig").write_text("\n".join(BUILD_MARKERS) + "\n", encoding="utf-8")
        (root / "zigux/tests/build.zig").write_text("\n".join(PHASE3_BUILD_MARKERS) + "\n", encoding="utf-8")
        (root / "Documentation/zigux/phase13-notifier-list-survey.md").write_text(
            f"last inspected current-master commit: `{surveyed_commit}`\n" + "\n".join(SURVEY_MARKERS) + "\n",
            encoding="utf-8",
        )
        (root / "zigux/Makefile").write_text("\n".join(MAKE_MARKERS) + "\n", encoding="utf-8")
        manifest = {
            "lane_key": "P13-L19",
            "phase": "Phase 13",
            "surveyed_commit": surveyed_commit,
            "anchors": EXPECTED_ANCHORS,
            "survey_summary": {flag: True for flag in REQUIRED_SURVEY_SUMMARY_FLAGS},
            "gaps": [
                {"id": "phase13-build-gate", "status": "starter_landed", "zigux_destination": "zigux/tests/phase13_build.zig"},
                {"id": "phase13-notifier-list-reviewability-gate", "status": "starter_landed", "zigux_destination": "zigux/tests/phase13_notifier_list_reviewability.zig"},
                {"id": "phase13-notifier-list-survey-note", "status": "starter_landed", "zigux_destination": "Documentation/zigux/phase13-notifier-list-survey.md"},
                {"id": "phase3-list-abi-and-view-surface", "status": "preexisting_phase3_surface", "zigux_destination": "zigux/bindings/abi.zig"},
                {"id": "phase3-list-view-helper-surface", "status": "preexisting_phase3_surface", "zigux_destination": "zigux/helpers/list_view.zig"},
                {"id": "phase13-list-helper-api-companion-surface", "status": "preexisting_phase3_surface", "zigux_destination": "zigux/helpers/list_view.zig"},
                {"id": "phase3-list-hlist-replay-surface", "status": "preexisting_phase3_surface", "zigux_destination": "zigux/tests/build.zig"},
                {"id": "phase13-generic-notifier-abi-foothold", "status": "starter_landed", "zigux_destination": "zigux/bindings/notifier_abi.zig"},
                {"id": "phase13-generic-notifier-helper-foothold", "status": "starter_landed", "zigux_destination": "zigux/helpers/notifier_chain_view.zig"},
                {"id": "phase13-generic-notifier-c-header-foothold", "status": "starter_landed", "zigux_destination": "include/zigux/notifier_abi.h"},
            ],
        }
        (root / "zigux/tests/phase13_notifier_list_manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )

        missing = _check_repo(root)
        if missing:
            print("PHASE13_NOTIFIER_PACKET_SELF_TEST=fail")
            for item in missing:
                print(item)
            return 1

    print("PHASE13_NOTIFIER_PACKET_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    if args.self_test:
        return _run_self_test()

    missing = _check_repo(Path(args.root).resolve())
    if missing:
        print("PHASE13_NOTIFIER_PACKET=fail")
        print("PHASE13_NOTIFIER_PACKET_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE13_NOTIFIER_PACKET_MISSING_END")
        return 1

    print("PHASE13_NOTIFIER_PACKET=pass")
    print(f"PHASE13_NOTIFIER_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE13_NOTIFIER_MARKER_COUNT="
        f"{len(ABI_MARKERS) + len(C_HEADER_MARKERS) + len(HELPER_MARKERS) + len(REVIEWABILITY_MARKERS) + len(BUILD_MARKERS) + len(PHASE3_BUILD_MARKERS) + len(SURVEY_MARKERS) + len(MAKE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
