#!/usr/bin/env python3
"""Check the bounded Phase 11 shared header-boundary packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


EXPECTED_LANE_KEY = "P11-L18"

REQUIRED_GAP_IDS = {
    "phase11-build-gate",
    "phase11-uapi-header-parity-survey-gate",
    "phase11-uapi-header-parity-note",
    "phase11-dw-wdt-watchdog-info-layout-assert",
    "phase11-hvc-console-winsize-layout-assert",
    "phase11-hvc-console-export-signature-assert",
}

REQUIRED_NOTE_MARKERS = [
    "PHASE11_HEADER_BOUNDARY_STATUS=shared_header_packet_restored",
    f"lane: `{EXPECTED_LANE_KEY}`",
    "phase11-dw-wdt-watchdog-header-boundary",
    "phase11-dw-wdt-watchdog-info-layout-assert",
    "phase11-hvc-console-winsize-layout-assert",
    "phase11-hvc-console-export-signature-assert",
    "phase11-uapi-header-parity-surface",
    "notifier_hangup_irq",
]

REQUIRED_SURVEY_MARKERS = [
    "phase11 shared header parity survey manifest records the maintained packet cleanly",
    "phase11 shared header parity survey keeps a bounded watchdog_info layout proof",
    "phase11 shared header parity survey keeps a bounded winsize layout proof",
    "phase11 shared header parity survey keeps the note pinned to the manifest provenance",
    "phase11 shared header parity survey keeps shared replay markers explicit without a missing inventory fixture",
    "phase11 shared header parity survey keeps the exported hvc surface explicit",
    "phase11 shared header parity survey keeps the shared build hook explicit",
    "layout_assert.assertSize(WatchdogInfo, 40);",
    "layout_assert.assertSize(WinSize, 8);",
]

REQUIRED_BUILD_MARKERS = [
    "phase11_uapi_header_parity_survey.zig",
    "phase11-uapi-header-parity-survey-tests",
    "phase11-hvc-console-survey-tests",
    "test_step.dependOn(&run_phase11_uapi_header_parity_survey_tests.step);",
    "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
    'phase11_uapi_header_parity_survey_module.addImport("layout_assert", layout_assert_module);',
]

REQUIRED_CONTRACT_MARKERS = [
    "PHASE11_SHARED_REPLAY_STATUS=starter_packet_reviewable",
    "zigux/tests/phase11_build.zig",
    "zigux/tests/phase11_uapi_header_parity_survey.zig",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "there is no shipped `zigux/tests/fixtures/phase11_build_inventory.json` on `master`",
    "there is no broader multi-checker Phase 11 validator stack on `master`",
]

REQUIRED_HVC_CONSOLE_MARKERS = [
    "pub fn hvc_instantiate",
    "pub fn hvc_alloc",
    "pub fn hvc_remove",
    "pub fn hvc_poll",
    "pub fn hvc_kick",
    "pub fn __hvc_resize",
    "pub fn notifier_add_irq",
    "pub fn notifier_del_irq",
]

REQUIRED_HVC_HEADER_MARKERS = [
    "extern void notifier_hangup_irq",
]


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def require_markers(text: str, markers: list[str], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"{label} missing markers: {', '.join(missing)}")


def check_repo(root: Path) -> None:
    manifest = json.loads(read_text(root, "zigux/tests/phase11_uapi_header_parity_manifest.json"))
    if manifest.get("lane_key") != EXPECTED_LANE_KEY:
        raise SystemExit("manifest lane_key mismatch")
    if manifest.get("phase") != "Phase 11":
        raise SystemExit("manifest phase mismatch")

    gap_ids = {gap["id"] for gap in manifest.get("gaps", [])}
    if gap_ids != REQUIRED_GAP_IDS:
        raise SystemExit(f"manifest gap ids mismatch: {sorted(gap_ids)}")

    note = read_text(root, "Documentation/zigux/phase11-uapi-header-parity-survey.md")
    survey = read_text(root, "zigux/tests/phase11_uapi_header_parity_survey.zig")
    build = read_text(root, "zigux/tests/phase11_build.zig")
    contract = read_text(root, "Documentation/zigux/phase11-shared-replay-contract.md")
    hvc_console = read_text(root, "drivers/tty/hvc/hvc_console.zig")
    hvc_header = read_text(root, "drivers/tty/hvc/hvc_console.h")

    require_markers(note, REQUIRED_NOTE_MARKERS + [manifest["surveyed_commit"]], "note")
    require_markers(survey, REQUIRED_SURVEY_MARKERS, "survey")
    require_markers(build, REQUIRED_BUILD_MARKERS, "build")
    require_markers(contract, REQUIRED_CONTRACT_MARKERS, "contract")
    require_markers(hvc_console, REQUIRED_HVC_CONSOLE_MARKERS, "hvc_console")
    require_markers(hvc_header, REQUIRED_HVC_HEADER_MARKERS, "hvc_header")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    check_repo(root)
    if args.self_test:
        print("phase11-header-boundary-packet: self-test passed")
    else:
        print("phase11-header-boundary-packet: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
