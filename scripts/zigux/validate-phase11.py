#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[2]


required_files = [
    ROOT / "scripts" / "zigux" / "validate-phase11.py",
    ROOT / "scripts" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "review-checklist.md",
    ROOT / ".github" / "workflows" / "zigux-bootstrap.yml",
    ROOT / "zigux" / "Makefile",
    ROOT / "drivers" / "watchdog" / "gpio_wdt.zig",
    ROOT / "drivers" / "watchdog" / "bcm2835_wdt.zig",
    ROOT / "drivers" / "watchdog" / "dw_wdt.zig",
    ROOT / "drivers" / "tty" / "hvc" / "hvc_console.zig",
    ROOT / "zigux" / "tests" / "phase11_build.zig",
    ROOT / "zigux" / "tests" / "phase11_gpio_wdt_manifest.json",
    ROOT / "zigux" / "tests" / "phase11_bcm2835_wdt_manifest.json",
    ROOT / "zigux" / "tests" / "phase11_dw_wdt_manifest.json",
    ROOT / "zigux" / "tests" / "phase11_hvc_console_manifest.json",
    ROOT / "zigux" / "tests" / "phase11_uapi_header_parity_manifest.json",
    ROOT / "zigux" / "tests" / "phase11_gpio_wdt_survey.zig",
    ROOT / "zigux" / "tests" / "phase11_bcm2835_wdt_survey.zig",
    ROOT / "zigux" / "tests" / "phase11_dw_wdt_survey.zig",
    ROOT / "zigux" / "tests" / "phase11_hvc_console_survey.zig",
    ROOT / "zigux" / "tests" / "phase11_uapi_header_parity_survey.zig",
]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def has_hex_commit(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def find_gap(manifest: dict[str, object], gap_id: str) -> dict[str, object] | None:
    for gap in manifest.get("gaps", []):
        if gap.get("id") == gap_id:
            return gap
    return None


missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print("PHASE11_VALIDATION=fail")
    print("MISSING_PHASE11_FILES_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE11_FILES_END")
    sys.exit(1)

script_readme = (ROOT / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
review_checklist = (ROOT / "Documentation" / "zigux" / "review-checklist.md").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
makefile = (ROOT / "zigux" / "Makefile").read_text(encoding="utf-8")
phase11_build = (ROOT / "zigux" / "tests" / "phase11_build.zig").read_text(encoding="utf-8")

required_make_markers = [
    "PHONY += phase11-validate phase11-test phase11",
    "phase11-validate:",
    "scripts/zigux/validate-phase11.py",
    "phase11-test:",
    "$(ZIG) build test --build-file zigux/tests/phase11_build.zig --summary all",
    "phase11: phase11-validate phase11-test",
]

required_workflow_markers = [
    "Validate Phase 11 simple-driver bundle",
    "make -C zigux phase11-validate",
    "Run Phase 11 watchdog and console tests",
    "zig build test --build-file zigux/tests/phase11_build.zig --summary all",
]

required_script_readme_markers = [
    "validate-phase11.py",
    "Phase 11 flow",
    "make -C zigux phase11-validate",
    "phase11_build.zig",
    "phase11_gpio_wdt_manifest.json",
    "phase11_bcm2835_wdt_manifest.json",
    "phase11_dw_wdt_manifest.json",
    "phase11_hvc_console_manifest.json",
    "phase11_uapi_header_parity_manifest.json",
]

required_review_checklist_markers = [
    "if the change is a Phase 11 simple-driver slice, do `scripts/zigux/validate-phase11.py`, `zigux/tests/phase11_build.zig`, the four driver-local Phase 11 manifests, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still agree on the same bounded simple-driver scope, shared replay contract, and explicit ready-next versus blocked follow-up posture?",
    "if the change touches the shared Phase 11 tooling path, does the bundle still keep `zigux/tests/phase11_hvc_console_survey.zig` as a dedicated replay instead of silently implying that every Phase 11 survey gate already runs in the shared `phase11_build.zig` path?",
]

required_build_markers = [
    "phase11-gpio-wdt-tests",
    "phase11-gpio-wdt-survey-tests",
    "phase11-bcm2835-wdt-tests",
    "phase11-bcm2835-wdt-survey-tests",
    "phase11-dw-wdt-tests",
    "phase11-dw-wdt-survey-tests",
    "phase11-uapi-header-parity-survey-tests",
    "phase11-hvc-console-tests",
    "test_step.dependOn(&run_phase11_gpio_wdt_tests.step);",
    "test_step.dependOn(&run_phase11_gpio_wdt_survey_tests.step);",
    "test_step.dependOn(&run_phase11_bcm2835_wdt_tests.step);",
    "test_step.dependOn(&run_phase11_bcm2835_wdt_survey_tests.step);",
    "test_step.dependOn(&run_phase11_dw_wdt_tests.step);",
    "test_step.dependOn(&run_phase11_dw_wdt_survey_tests.step);",
    "test_step.dependOn(&run_phase11_uapi_header_parity_survey_tests.step);",
    "test_step.dependOn(&run_phase11_hvc_console_tests.step);",
]

forbidden_build_markers = [
    "phase11_hvc_console_survey_tests",
    "run_phase11_hvc_console_survey_tests.step",
]

missing_markers: list[str] = []

for marker in required_make_markers:
    if marker not in makefile:
        missing_markers.append(f"make:{marker}")
for marker in required_workflow_markers:
    if marker not in workflow:
        missing_markers.append(f"workflow:{marker}")
for marker in required_script_readme_markers:
    if marker not in script_readme:
        missing_markers.append(f"script_readme:{marker}")
for marker in required_review_checklist_markers:
    if marker not in review_checklist:
        missing_markers.append(f"review_checklist:{marker}")
for marker in required_build_markers:
    if marker not in phase11_build:
        missing_markers.append(f"phase11_build:{marker}")
for marker in forbidden_build_markers:
    if marker in phase11_build:
        missing_markers.append(f"phase11_build:forbidden:{marker}")

manifest_specs = {
    "phase11_gpio_wdt_manifest.json": {
        "lane_key": "P11-L04",
        "anchor": "drivers/watchdog/gpio_wdt.c",
        "gap_count": 10,
        "ready_next": [],
        "blocked": ["phase11-gpio-wdt-platform-registration"],
        "summary_expectations": {
            "preexisting_phase11_build_present": True,
            "preexisting_gpio_wdt_zig_present": True,
            "preexisting_gpio_wdt_test_present": True,
        },
    },
    "phase11_bcm2835_wdt_manifest.json": {
        "lane_key": "P11-L06",
        "anchor": "drivers/watchdog/bcm2835_wdt.c",
        "gap_count": 12,
        "ready_next": [],
        "blocked": ["phase11-bcm2835-wdt-live-platform-registration"],
        "summary_expectations": {
            "preexisting_phase11_build_present": True,
            "bcm2835_wdt_zig_present": True,
            "bcm2835_wdt_survey_gate_present": True,
            "bcm2835_wdt_validation_matrix_present": True,
        },
    },
    "phase11_dw_wdt_manifest.json": {
        "lane_key": "P11-L10",
        "anchor": "drivers/watchdog/dw_wdt.c",
        "gap_count": 10,
        "ready_next": ["phase11-dw-wdt-registration-handoff"],
        "blocked": ["phase11-dw-wdt-platform-and-pm"],
        "summary_expectations": {
            "preexisting_phase11_build_present": True,
            "dw_wdt_zig_present": True,
            "watchdog_uapi_header_present": True,
            "watchdog_core_header_present": True,
        },
    },
    "phase11_hvc_console_manifest.json": {
        "lane_key": "P11-L13",
        "anchor": "drivers/tty/hvc/hvc_console.c",
        "gap_count": 8,
        "ready_next": ["phase11-hvc-console-tty-and-teardown-parity"],
        "blocked": [],
        "summary_expectations": {
            "preexisting_phase11_build_present": True,
            "hvc_console_zig_present": True,
            "hvc_console_test_present": True,
            "hvc_console_survey_gate_present": True,
        },
    },
    "phase11_uapi_header_parity_manifest.json": {
        "lane_key": "P11-L11",
        "anchor": "include/uapi/linux/watchdog.h",
        "gap_count": 6,
        "ready_next": ["phase11-phase3-interop-followup"],
        "blocked": [],
        "summary_expectations": {
            "preexisting_phase11_build_present": True,
            "watchdog_uapi_header_present": True,
            "watchdog_core_header_present": True,
            "hvc_console_header_present": True,
        },
    },
}

allowed_statuses = {
    "starter_landed",
    "ready_next",
    "blocked_on_driver_scaffold",
    "blocked_on_kernel_integration",
    "future_phase_boundary",
}

ready_next_total = 0
blocked_total = 0
starter_total = 0

for name, spec in manifest_specs.items():
    manifest = load_json(ROOT / "zigux" / "tests" / name)
    if manifest.get("phase") != "Phase 11":
        missing_markers.append(f"{name}:phase={manifest.get('phase')}")
    if manifest.get("lane_key") != spec["lane_key"]:
        missing_markers.append(f"{name}:lane_key={manifest.get('lane_key')}")
    if manifest.get("anchor") != spec["anchor"]:
        missing_markers.append(f"{name}:anchor={manifest.get('anchor')}")
    if not has_hex_commit(manifest.get("surveyed_commit")):
        missing_markers.append(f"{name}:surveyed_commit")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        missing_markers.append(f"{name}:gaps_type")
        continue
    if len(gaps) != spec["gap_count"]:
        missing_markers.append(f"{name}:gap_count={len(gaps)}")

    seen_ids: set[str] = set()
    summary = manifest.get("survey_summary", {})
    if not isinstance(summary, dict):
        missing_markers.append(f"{name}:survey_summary_type")
        summary = {}
    for key, expected in spec["summary_expectations"].items():
        if summary.get(key) != expected:
            missing_markers.append(f"{name}:survey_summary:{key}={summary.get(key)}")

    for gap in gaps:
        if not isinstance(gap, dict):
            missing_markers.append(f"{name}:gap_type")
            continue
        gap_id = gap.get("id")
        status = gap.get("status")
        destination = gap.get("zigux_destination")
        why_now = gap.get("why_now")
        if not isinstance(gap_id, str) or not gap_id:
            missing_markers.append(f"{name}:gap_id")
            continue
        if gap_id in seen_ids:
            missing_markers.append(f"{name}:duplicate_gap:{gap_id}")
        seen_ids.add(gap_id)
        if status not in allowed_statuses:
            missing_markers.append(f"{name}:status:{gap_id}={status}")
        if not isinstance(destination, str) or not destination:
            missing_markers.append(f"{name}:destination:{gap_id}")
        if not isinstance(why_now, str) or not why_now:
            missing_markers.append(f"{name}:why_now:{gap_id}")
        if status == "starter_landed":
            starter_total += 1
        elif status == "ready_next":
            ready_next_total += 1
        elif isinstance(status, str) and status.startswith("blocked_on_"):
            blocked_total += 1

    for gap_id in spec["ready_next"]:
        gap = find_gap(manifest, gap_id)
        if gap is None:
            missing_markers.append(f"{name}:missing_ready_next:{gap_id}")
        elif gap.get("status") != "ready_next":
            missing_markers.append(f"{name}:ready_next_status:{gap_id}={gap.get('status')}")

    for gap_id in spec["blocked"]:
        gap = find_gap(manifest, gap_id)
        if gap is None:
            missing_markers.append(f"{name}:missing_blocked:{gap_id}")
        elif not isinstance(gap.get("status"), str) or not gap["status"].startswith("blocked_on_"):
            missing_markers.append(f"{name}:blocked_status:{gap_id}={gap.get('status')}")

if ready_next_total != 3:
    missing_markers.append(f"phase11_bundle:ready_next_total={ready_next_total}")
if blocked_total != 3:
    missing_markers.append(f"phase11_bundle:blocked_total={blocked_total}")
if starter_total != 40:
    missing_markers.append(f"phase11_bundle:starter_total={starter_total}")

if missing_markers:
    print("PHASE11_VALIDATION=fail")
    print("MISSING_PHASE11_MARKERS_START")
    for marker in missing_markers:
        print(marker)
    print("MISSING_PHASE11_MARKERS_END")
    sys.exit(1)

print("PHASE11_VALIDATION=pass")
print(f"PHASE11_REQUIRED_FILE_COUNT={len(required_files)}")
print(
    "PHASE11_REQUIRED_MARKER_COUNT="
    f"{len(required_make_markers) + len(required_workflow_markers) + len(required_script_readme_markers) + len(required_review_checklist_markers) + len(required_build_markers)}"
)
print(f"PHASE11_MANIFEST_COUNT={len(manifest_specs)}")
print(f"PHASE11_STARTER_STATUS_COUNT={starter_total}")
print(f"PHASE11_READY_NEXT_STATUS_COUNT={ready_next_total}")
print(f"PHASE11_BLOCKED_STATUS_COUNT={blocked_total}")
