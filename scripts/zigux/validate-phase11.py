#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")
BUILD_TEST_NAME_RE = re.compile(r'\.name = "(phase11-[^"]+)"')
BUILD_DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
BUILD_MODULE_RE = re.compile(
    r'const ([A-Za-z0-9_]+) = b\.createModule\(\.\{\s*'
    r'\.root_source_file = b\.path\("([^"]+)"\),',
    re.S,
)
BUILD_IMPORT_RE = re.compile(r'([A-Za-z0-9_]+)\.addImport\("([^"]+)", ([A-Za-z0-9_]+)\);')
BUILD_TEST_ROOT_MODULE_RE = re.compile(
    r'\.name = "(phase11-[^"]+)",\s*'
    r'\.root_module = ([A-Za-z0-9_]+),',
    re.S,
)

FILES = [
    "scripts/zigux/check-phase11-build-inventory.py",
    "scripts/zigux/validate-phase11.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase11-dw-wdt-survey.md",
    "Documentation/zigux/phase11-dw-wdt-slice.md",
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
    "Documentation/zigux/phase11-bcm2835-wdt-slice.md",
    "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-gpio-wdt-survey.md",
    "Documentation/zigux/phase11-gpio-wdt-slice.md",
    "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-console-slice.md",
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
    "zigux/tests/phase11_gpio_wdt.zig",
    "zigux/tests/phase11_bcm2835_wdt.zig",
    "zigux/tests/phase11_dw_wdt.zig",
    "zigux/tests/phase11_hvc_console.zig",
    "zigux/tests/fixtures/phase11_build_inventory.json",
]

MAKE_MARKERS = [
    "PHONY += phase11-validate phase11-test phase11",
    "phase11-validate:",
    "scripts/zigux/check-phase11-build-inventory.py",
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
    "check-phase11-build-inventory.py",
    "validate-phase11.py",
    "Phase 11 flow",
    "make -C zigux phase11-validate",
    "phase11_build_inventory.json",
    "phase11_gpio_wdt_manifest.json",
    "phase11_uapi_header_parity_manifest.json",
    "dedicated hvc_console survey note and validation matrix",
    "exact shared-versus-dedicated replay commands and observed outcome lines",
]
CHECKLIST_MARKERS = [
    "if the change is a Phase 11 simple-driver slice, do `scripts/zigux/validate-phase11.py`, `zigux/tests/phase11_build.zig`, the four driver-local Phase 11 manifests, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still agree on the same bounded simple-driver scope, shared replay contract, and explicit ready-next versus blocked follow-up posture?",
    "if the change touches the shared Phase 11 tooling path, do `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, and `zigux/tests/phase11_hvc_console_survey.zig` still agree on the exact shared build inventory and the dedicated-survey boundary instead of silently implying that every Phase 11 survey gate already runs in the shared path?",
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
BUILD_INVENTORY_FIXTURE = "zigux/tests/fixtures/phase11_build_inventory.json"

MANIFEST_SPECS = {
    "phase11_gpio_wdt_manifest.json": ("P11-L04", "drivers/watchdog/gpio_wdt.c", 13, [], ["phase11-gpio-wdt-platform-registration"]),
    "phase11_bcm2835_wdt_manifest.json": ("P11-L05", "drivers/watchdog/bcm2835_wdt.c", 13, [], ["phase11-bcm2835-wdt-live-platform-registration"]),
    "phase11_dw_wdt_manifest.json": ("P11-L11", "drivers/watchdog/dw_wdt.c", 12, [], ["phase11-dw-wdt-platform-and-pm"]),
    "phase11_hvc_console_manifest.json": ("P11-L18", "drivers/tty/hvc/hvc_console.c", 12, [], []),
    "phase11_uapi_header_parity_manifest.json": ("P11-L17", "include/uapi/linux/watchdog.h and include/uapi/asm-generic/termios.h", 8, ["phase11-phase3-interop-followup"], []),
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
    "slice": "Documentation/zigux/phase11-hvc-console-slice.md",
    "matrix": "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
}
GPIO_WDT_DOC_PATHS = {
    "survey": "Documentation/zigux/phase11-gpio-wdt-survey.md",
    "slice": "Documentation/zigux/phase11-gpio-wdt-slice.md",
    "matrix": "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
}
DW_WDT_DOC_PATHS = {
    "survey": "Documentation/zigux/phase11-dw-wdt-survey.md",
    "slice": "Documentation/zigux/phase11-dw-wdt-slice.md",
    "matrix": "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
}
BCM2835_WDT_DOC_PATHS = {
    "survey": "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
    "slice": "Documentation/zigux/phase11-bcm2835-wdt-slice.md",
    "matrix": "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
}


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_manifest(name: str) -> dict[str, object]:
    return json.loads(text(f"zigux/tests/{name}"))


def load_json(path: str) -> object:
    return json.loads(text(path))


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

build_inventory = load_json(BUILD_INVENTORY_FIXTURE)
expected_build_test_names = build_inventory.get("build_test_names")
if not isinstance(expected_build_test_names, list) or not all(isinstance(item, str) for item in expected_build_test_names):
    missing.append("phase11_build_fixture:build_test_names")
else:
    actual_build_test_names = BUILD_TEST_NAME_RE.findall(build_text)
    if actual_build_test_names != expected_build_test_names:
        missing.append("phase11_build_fixture:build_test_names_mismatch")

expected_depend_steps = build_inventory.get("shared_test_depend_steps")
if not isinstance(expected_depend_steps, list) or not all(isinstance(item, str) for item in expected_depend_steps):
    missing.append("phase11_build_fixture:shared_test_depend_steps")
else:
    actual_depend_steps = BUILD_DEPEND_STEP_RE.findall(build_text)
    if actual_depend_steps != expected_depend_steps:
        missing.append("phase11_build_fixture:shared_test_depend_steps_mismatch")

expected_module_roots = build_inventory.get("module_root_source_files")
if not isinstance(expected_module_roots, list) or not all(
    isinstance(item, dict)
    and isinstance(item.get("module"), str)
    and isinstance(item.get("path"), str)
    for item in expected_module_roots
):
    missing.append("phase11_build_fixture:module_root_source_files")
else:
    actual_module_roots = [
        {"module": module_name, "path": root_path}
        for module_name, root_path in BUILD_MODULE_RE.findall(build_text)
    ]
    if actual_module_roots != expected_module_roots:
        missing.append("phase11_build_fixture:module_root_source_files_mismatch")

expected_module_imports = build_inventory.get("module_imports")
if not isinstance(expected_module_imports, list) or not all(
    isinstance(item, dict)
    and isinstance(item.get("module"), str)
    and isinstance(item.get("import_name"), str)
    and isinstance(item.get("imported_module"), str)
    for item in expected_module_imports
):
    missing.append("phase11_build_fixture:module_imports")
else:
    actual_module_imports = [
        {
            "module": module_name,
            "import_name": import_name,
            "imported_module": imported_module,
        }
        for module_name, import_name, imported_module in BUILD_IMPORT_RE.findall(build_text)
    ]
    if actual_module_imports != expected_module_imports:
        missing.append("phase11_build_fixture:module_imports_mismatch")

expected_test_root_modules = build_inventory.get("test_root_modules")
if not isinstance(expected_test_root_modules, list) or not all(
    isinstance(item, dict)
    and isinstance(item.get("test"), str)
    and isinstance(item.get("root_module"), str)
    for item in expected_test_root_modules
):
    missing.append("phase11_build_fixture:test_root_modules")
else:
    actual_test_root_modules = [
        {"test": test_name, "root_module": root_module}
        for test_name, root_module in BUILD_TEST_ROOT_MODULE_RE.findall(build_text)
    ]
    if actual_test_root_modules != expected_test_root_modules:
        missing.append("phase11_build_fixture:test_root_modules_mismatch")

expected_forbidden_markers = build_inventory.get("forbidden_markers")
if expected_forbidden_markers != FORBIDDEN_BUILD_MARKERS:
    missing.append("phase11_build_fixture:forbidden_markers")

dedicated_survey_replays = build_inventory.get("dedicated_survey_replays")
if dedicated_survey_replays != ["zigux/tests/phase11_hvc_console_survey.zig"]:
    missing.append("phase11_build_fixture:dedicated_survey_replays")

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
hvc_slice_doc = text(HVC_DOC_PATHS["slice"])
hvc_matrix_doc = text(HVC_DOC_PATHS["matrix"])
for marker in [
    f"reviewed against live `master` `{hvc_commit}`",
    "dedicated hvc survey replay is still separate from `zigux/tests/phase11_build.zig`",
    "The next honest bounded step inside the same Phase 11 lane is to leave the starter parked unless fresh repo inspection finds another comparably small host-free notifier or sysrq handoff; otherwise avoid widening straight into live khvcd worker behavior or host-backed teardown.",
]:
    if marker not in hvc_survey_doc:
        missing.append(f"phase11_hvc_console_docs:survey:{marker}")
for marker in [
    "adds a tiny tty-registration handoff summary that keeps `setup_hvc_console()`-adjacent close-wait ownership, notifier boundaries, and khvcd wakeup intent reviewable without claiming worker execution",
    "adds a tiny khvcd polling-contract summary that keeps notifier-driven versus polling-driven wakeups, bounded reschedule intent, and teardown-facing host-I/O boundaries reviewable without claiming worker execution",
    "adds a tiny khvcd sleep-and-reschedule handoff summary that keeps the pre-sleep kick check, the interruptible-state recheck, untimed schedule versus timed backoff selection, and running-state restore reviewable without claiming live worker execution",
    "adds a tiny `hvc_hangup()` disconnect summary that keeps resize-cancel ordering, the stale-count guard, tty detach, outbuf clearing, and notifier-hangup boundaries reviewable without claiming notifier callback execution",
    "adds a tiny `hvc_remove()` handoff summary that keeps console-lock slot clearing, the paired `vtermnos[]` and `cons_ops[]` release, `tty_port_put()` ordering, `tty_vhangup()` follow-through, and the keep-IRQ-until-hangup teardown boundary reviewable without claiming live console locking or IRQ teardown",
    "This slice does not claim tty-driver registration, khvcd polling or execution, sysrq handling, notifier callback execution, hotplug discovery, or live hypervisor-backed reads and writes yet.",
    "The next honest bounded step inside the same Phase 11 lane is to leave this starter parked unless another comparably small host-free notifier or sysrq handoff becomes obvious; otherwise avoid widening straight into live khvcd worker behavior or host-backed teardown.",
]:
    if marker not in hvc_slice_doc:
        missing.append(f"phase11_hvc_console_docs:slice:{marker}")
for marker in [
    "PHASE11_HVC_CONSOLE_STATUS=remove_handoff_landed",
    "`zigux/tests/phase11_build.zig` continues to run `zigux/tests/phase11_hvc_console.zig` inside the shared Phase 11 starter replay",
    "`zigux/tests/phase11_hvc_console.zig` now keeps the timed-sleep, untimed-sleep, pre-state kick, and post-state kick assertions inside the shared Phase 11 replay",
    "`zigux/tests/phase11_hvc_console.zig` now keeps the tty-attached and tty-detached remove-handoff assertions inside the shared Phase 11 replay",
    "leave this helper parked unless another comparably small host-free notifier or sysrq split becomes obvious",
    "the shared Phase 11 gate for this lane remains `zigux/tests/phase11_build.zig`",
    "the dedicated archival survey gate remains `zigux/tests/phase11_hvc_console_survey.zig`",
]:
    if marker not in hvc_matrix_doc:
        missing.append(f"phase11_hvc_console_docs:matrix:{marker}")
