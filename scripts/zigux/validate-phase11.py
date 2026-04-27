#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")

FILES = [
    "scripts/zigux/validate-phase11.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "drivers/watchdog/gpio_wdt.zig",
    "drivers/watchdog/bcm2835_wdt.zig",
    "drivers/watchdog/dw_wdt.zig",
    "drivers/tty/hvc/hvc_console.zig",
    "zigux/tests/phase11_build.zig",
    "zigux/tests/phase11_gpio_wdt_manifest.json",
    "zigux/tests/phase11_bcm2835_wdt_manifest.json",
    "zigux/tests/phase11_dw_wdt_manifest.json",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "zigux/tests/phase11_uapi_header_parity_manifest.json",
    "zigux/tests/phase11_gpio_wdt_survey.zig",
    "zigux/tests/phase11_bcm2835_wdt_survey.zig",
    "zigux/tests/phase11_dw_wdt_survey.zig",
    "zigux/tests/phase11_hvc_console_survey.zig",
    "zigux/tests/phase11_uapi_header_parity_survey.zig",
]

MAKE_MARKERS = [
    "PHONY += phase11-validate phase11-test phase11",
    "phase11-validate:",
    "scripts/zigux/validate-phase11.py",
    "$(ZIG) build test --build-file zigux/tests/phase11_build.zig --summary all",
    "phase11: phase11-validate phase11-test",
]
WORKFLOW_MARKERS = [
    "Validate Phase 11 simple-driver bundle",
    "make -C zigux phase11-validate",
    "Run Phase 11 watchdog and console tests",
    "zig build test --build-file zigux/tests/phase11_build.zig --summary all",
]
README_MARKERS = [
    "validate-phase11.py",
    "Phase 11 flow",
    "make -C zigux phase11-validate",
    "phase11_gpio_wdt_manifest.json",
    "phase11_uapi_header_parity_manifest.json",
    "dedicated hvc_console survey note and validation matrix",
    "exact shared-versus-dedicated replay commands and observed outcome lines",
]
CHECKLIST_MARKERS = [
    "if the change is a Phase 11 simple-driver slice, do `scripts/zigux/validate-phase11.py`, `zigux/tests/phase11_build.zig`, the four driver-local Phase 11 manifests, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still agree on the same bounded simple-driver scope, shared replay contract, and explicit ready-next versus blocked follow-up posture?",
    "if the change touches the shared Phase 11 tooling path, does the bundle still keep `zigux/tests/phase11_hvc_console_survey.zig` as a dedicated survey replay instead of silently implying that every Phase 11 survey gate already runs in the shared `phase11_build.zig` path?",
]
BUILD_MARKERS = [
    "phase11-gpio-wdt-tests",
    "phase11-bcm2835-wdt-tests",
    "phase11-dw-wdt-tests",
    "phase11-uapi-header-parity-survey-tests",
    "phase11-hvc-console-tests",
    "test_step.dependOn(&run_phase11_gpio_wdt_survey_tests.step);",
    "test_step.dependOn(&run_phase11_bcm2835_wdt_survey_tests.step);",
    "test_step.dependOn(&run_phase11_dw_wdt_survey_tests.step);",
    "test_step.dependOn(&run_phase11_uapi_header_parity_survey_tests.step);",
    "test_step.dependOn(&run_phase11_hvc_console_tests.step);",
]
FORBIDDEN_BUILD_MARKERS = [
    "phase11_hvc_console_survey_tests",
    "run_phase11_hvc_console_survey_tests.step",
]

MANIFEST_SPECS = {
    "phase11_gpio_wdt_manifest.json": ("P11-L04", "drivers/watchdog/gpio_wdt.c", 10, [], ["phase11-gpio-wdt-platform-registration"]),
    "phase11_bcm2835_wdt_manifest.json": ("P11-L06", "drivers/watchdog/bcm2835_wdt.c", 12, [], ["phase11-bcm2835-wdt-live-platform-registration"]),
    "phase11_dw_wdt_manifest.json": ("P11-L10", "drivers/watchdog/dw_wdt.c", 11, ["phase11-dw-wdt-platform-resource-preflight"], ["phase11-dw-wdt-platform-and-pm"]),
    "phase11_hvc_console_manifest.json": ("P11-L14", "drivers/tty/hvc/hvc_console.c", 8, [], []),
    "phase11_uapi_header_parity_manifest.json": ("P11-L17", "include/uapi/linux/watchdog.h and include/uapi/asm-generic/termios.h", 7, ["phase11-phase3-interop-followup"], []),
}
ALLOWED_STATUSES = {
    "starter_landed",
    "ready_next",
    "blocked_on_driver_scaffold",
    "blocked_on_kernel_integration",
    "future_phase_boundary",
}
SURVEY_SPECS = {
    "phase11_gpio_wdt_manifest.json": {
        "path": "zigux/tests/phase11_gpio_wdt_survey.zig",
        "count_markers": [("starter_landed_count", "starter_landed"), ("blocked_count", "blocked_on_")],
    },
    "phase11_bcm2835_wdt_manifest.json": {
        "path": "zigux/tests/phase11_bcm2835_wdt_survey.zig",
        "count_markers": [("starter_landed_count", "starter_landed"), ("ready_next_count", "ready_next"), ("blocked_count", "blocked_on_")],
    },
    "phase11_dw_wdt_manifest.json": {
        "path": "zigux/tests/phase11_dw_wdt_survey.zig",
        "count_markers": [("starter_landed_count", "starter_landed"), ("ready_next_count", "ready_next"), ("blocked_count", "blocked_on_")],
    },
    "phase11_hvc_console_manifest.json": {
        "path": "zigux/tests/phase11_hvc_console_survey.zig",
        "count_markers": [("starter_landed_count", "starter_landed"), ("ready_next_count", "ready_next"), ("blocked_count", "blocked_on_")],
    },
    "phase11_uapi_header_parity_manifest.json": {
        "path": "zigux/tests/phase11_uapi_header_parity_survey.zig",
        "count_markers": [("starter_landed_count", "starter_landed"), ("ready_next_count", "ready_next")],
    },
}
HVC_DOC_PATHS = {
    "survey": "Documentation/zigux/phase11-hvc-console-survey.md",
    "matrix": "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
}


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_manifest(name: str) -> dict[str, object]:
    return json.loads(text(f"zigux/tests/{name}"))


def find_gap(manifest: dict[str, object], gap_id: str) -> dict[str, object] | None:
    for gap in manifest.get("gaps", []):
        if gap.get("id") == gap_id:
            return gap
    return None


def count_statuses(manifest: dict[str, object], match: str) -> int:
    total = 0
    for gap in manifest.get("gaps", []):
        status = gap.get("status")
        if not isinstance(status, str):
            continue
        if match.endswith("_") and status.startswith(match):
            total += 1
        elif status == match:
            total += 1
    return total


missing_files = [path for path in FILES if not (ROOT / path).exists()]
if missing_files:
    print("PHASE11_VALIDATION=fail")
    print("MISSING_PHASE11_FILES_START")
    for path in missing_files:
        print(path)
    print("MISSING_PHASE11_FILES_END")
    sys.exit(1)

missing: list[str] = []
for name, source, markers in [
    ("make", text("zigux/Makefile"), MAKE_MARKERS),
    ("workflow", text(".github/workflows/zigux-bootstrap.yml"), WORKFLOW_MARKERS),
    ("script_readme", text("scripts/zigux/README.md"), README_MARKERS),
    ("review_checklist", text("Documentation/zigux/review-checklist.md"), CHECKLIST_MARKERS),
    ("phase11_build", text("zigux/tests/phase11_build.zig"), BUILD_MARKERS),
]:
    for marker in markers:
        if marker not in source:
            missing.append(f"{name}:{marker}")

build_text = text("zigux/tests/phase11_build.zig")
for marker in FORBIDDEN_BUILD_MARKERS:
    if marker in build_text:
        missing.append(f"phase11_build:forbidden:{marker}")

starter_total = 0
ready_total = 0
blocked_total = 0
for name, (lane_key, anchor, gap_count, ready_ids, blocked_ids) in MANIFEST_SPECS.items():
    manifest = load_manifest(name)
    if manifest.get("phase") != "Phase 11":
        missing.append(f"{name}:phase")
    if manifest.get("lane_key") != lane_key:
        missing.append(f"{name}:lane_key")
    if manifest.get("anchor") != anchor:
        missing.append(f"{name}:anchor")
    if not HEX40.fullmatch(str(manifest.get("surveyed_commit", ""))):
        missing.append(f"{name}:surveyed_commit")
    gaps = manifest.get("gaps")
    if not isinstance(gaps, list) or len(gaps) != gap_count:
        missing.append(f"{name}:gap_count")
        continue
    seen: set[str] = set()
    for gap in gaps:
        gap_id = gap.get("id")
        status = gap.get("status")
        if not isinstance(gap_id, str) or gap_id in seen:
            missing.append(f"{name}:gap_id")
            continue
        seen.add(gap_id)
        if status not in ALLOWED_STATUSES:
            missing.append(f"{name}:status:{gap_id}")
        if status == "starter_landed":
            starter_total += 1
        elif status == "ready_next":
            ready_total += 1
        elif isinstance(status, str) and status.startswith("blocked_on_"):
            blocked_total += 1
    for gap_id in ready_ids:
        if (find_gap(manifest, gap_id) or {}).get("status") != "ready_next":
            missing.append(f"{name}:ready_next:{gap_id}")
    for gap_id in blocked_ids:
        status = (find_gap(manifest, gap_id) or {}).get("status")
        if not isinstance(status, str) or not status.startswith("blocked_on_"):
            missing.append(f"{name}:blocked:{gap_id}")
    survey_spec = SURVEY_SPECS[name]
    survey_text = text(survey_spec["path"])
    commit = str(manifest.get("surveyed_commit", ""))
    if commit not in survey_text:
        missing.append(f"{name}:survey_commit_pin")
    for variable_name, status_match in survey_spec["count_markers"]:
        expected_count = count_statuses(manifest, status_match)
        count_marker = f'expectEqual(@as(usize, {expected_count}), {variable_name});'
        if count_marker not in survey_text:
            missing.append(f"{name}:survey_count:{variable_name}={expected_count}")

hvc_manifest = load_manifest("phase11_hvc_console_manifest.json")
hvc_commit = str(hvc_manifest.get("surveyed_commit", ""))
hvc_survey_doc = text(HVC_DOC_PATHS["survey"])
hvc_matrix_doc = text(HVC_DOC_PATHS["matrix"])
for marker in [
    f"reviewed against live `master` `{hvc_commit}`",
    "dedicated hvc survey replay is still separate from `zigux/tests/phase11_build.zig`",
    "The next honest bounded step inside the same Phase 11 lane is a tiny khvcd polling-contract summary",
]:
    if marker not in hvc_survey_doc:
        missing.append(f"phase11_hvc_console_docs:survey:{marker}")
for marker in [
    "PHASE11_HVC_CONSOLE_STATUS=tty_registration_handoff_landed",
    "shared replay observed on `master` currently runs `phase11-hvc-console-tests` but not `phase11-hvc-console-survey-tests`",
    "`zig build test --build-file zigux/tests/phase11_build.zig --summary all`",
    "`Build Summary: 17/17 steps succeeded; 37/37 tests passed`",
    "`run test phase11-hvc-console-tests 6 pass (6 total)`",
    "`zig test zigux/tests/phase11_hvc_console_survey.zig`",
    "`2/2 ... OK`",
    "deepen the next bounded khvcd polling-contract summary",
]:
    if marker not in hvc_matrix_doc:
        missing.append(f"phase11_hvc_console_docs:matrix:{marker}")

if starter_total != 43:
    missing.append(f"phase11_bundle:starter_total={starter_total}")
if ready_total != 2:
    missing.append(f"phase11_bundle:ready_total={ready_total}")
if blocked_total != 3:
    missing.append(f"phase11_bundle:blocked_total={blocked_total}")

if missing:
    print("PHASE11_VALIDATION=fail")
    print("MISSING_PHASE11_MARKERS_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE11_MARKERS_END")
    sys.exit(1)

print("PHASE11_VALIDATION=pass")
print(f"PHASE11_REQUIRED_FILE_COUNT={len(FILES)}")
print(f"PHASE11_REQUIRED_MARKER_COUNT={len(MAKE_MARKERS) + len(WORKFLOW_MARKERS) + len(README_MARKERS) + len(CHECKLIST_MARKERS) + len(BUILD_MARKERS)}")
print(f"PHASE11_MANIFEST_COUNT={len(MANIFEST_SPECS)}")
print(f"PHASE11_STARTER_STATUS_COUNT={starter_total}")
print(f"PHASE11_READY_NEXT_STATUS_COUNT={ready_total}")
print(f"PHASE11_BLOCKED_STATUS_COUNT={blocked_total}")
