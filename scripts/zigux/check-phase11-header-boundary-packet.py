#!/usr/bin/env python3
"""Check the bounded Phase 11 shared header-boundary packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


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
    "phase11-dw-wdt-watchdog-header-boundary",
    "phase11-dw-wdt-watchdog-info-layout-assert",
    "phase11-hvc-console-winsize-layout-assert",
    "phase11-hvc-console-export-signature-assert",
    "phase11-uapi-header-parity-surface",
]

REQUIRED_SURVEY_MARKERS = [
    "phase11-dw-wdt-watchdog-info-layout-assert",
    "phase11-hvc-console-winsize-layout-assert",
    "phase11-hvc-console-export-signature-assert",
    "phase11-uapi-header-parity-survey-tests",
    "phase11-dw-wdt-suspend-resume-tests",
    "phase11-hvc-console-poll-retry-split-tests",
    "pub fn hvc_instantiate",
    "pub fn notifier_del_irq",
]

REQUIRED_BUILD_MARKERS = [
    "phase11_uapi_header_parity_survey.zig",
    "phase11-uapi-header-parity-survey-tests",
    "test_step.dependOn(&run_phase11_uapi_header_parity_survey_tests.step);",
]


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def require_markers(text: str, markers: list[str], label: str) -> None:
    missing = [marker for marker in markers if marker not in text]
    if missing:
        raise SystemExit(f"{label} missing markers: {', '.join(missing)}")


def check_repo(root: Path) -> None:
    manifest = json.loads(read_text(root, "zigux/tests/phase11_uapi_header_parity_manifest.json"))
    if manifest.get("lane_key") != "P11-L08":
        raise SystemExit("manifest lane_key mismatch")
    if manifest.get("phase") != "Phase 11":
        raise SystemExit("manifest phase mismatch")

    gap_ids = {gap["id"] for gap in manifest.get("gaps", [])}
    if gap_ids != REQUIRED_GAP_IDS:
        raise SystemExit(f"manifest gap ids mismatch: {sorted(gap_ids)}")

    note = read_text(root, "Documentation/zigux/phase11-uapi-header-parity-survey.md")
    survey = read_text(root, "zigux/tests/phase11_uapi_header_parity_survey.zig")
    build = read_text(root, "zigux/tests/phase11_build.zig")
    inventory = read_text(root, "zigux/tests/fixtures/phase11_build_inventory.json")
    hvc_console = read_text(root, "drivers/tty/hvc/hvc_console.zig")

    require_markers(note, REQUIRED_NOTE_MARKERS + [manifest["surveyed_commit"]], "note")
    require_markers(build, REQUIRED_BUILD_MARKERS, "build")
    require_markers(
        inventory,
        [
            "phase11-uapi-header-parity-survey-tests",
            "phase11-dw-wdt-suspend-resume-tests",
            "phase11-dw-wdt-remove-idle-split-tests",
            "phase11-hvc-console-modem-control-split-tests",
            "phase11-hvc-console-poll-retry-split-tests",
        ],
        "inventory",
    )
    require_markers(
        survey + "\n" + hvc_console,
        REQUIRED_SURVEY_MARKERS,
        "survey",
    )


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
