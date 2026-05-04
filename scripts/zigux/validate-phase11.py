#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import shutil
import subprocess
import sys
import tempfile


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
    "scripts/zigux/check-phase11-layout-assert-surface.py",
    "scripts/zigux/check-phase11-hvc-validation-flow.py",
    "scripts/zigux/check-phase11-hvc-cleanup-alignment.py",
    "scripts/zigux/check-phase11-shared-replay-contract.py",
    "scripts/zigux/validate-phase11.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase11-shared-replay-contract.md",
    "Documentation/zigux/phase11-dw-wdt-survey.md",
    "Documentation/zigux/phase11-dw-wdt-slice.md",
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
    "Documentation/zigux/phase11-bcm2835-wdt-slice.md",
    "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-gpio-wdt-survey.md",
    "Documentation/zigux/phase11-gpio-wdt-slice.md",
    "Documentation/zigux/phase11-gpio-wdt-module-slice.md",
    "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-console-slice.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-uapi-header-parity-survey.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "drivers/watchdog/gpio_wdt.zig",
    "drivers/watchdog/bcm2835_wdt.zig",
    "drivers/watchdog/dw_wdt.zig",
    "drivers/tty/hvc/hvc_console.zig",
    "drivers/tty/hvc/hvc_console_sysrq.zig",
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
    "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    "zigux/tests/fixtures/phase11_build_inventory.json",
]

MAKE_MARKERS = [
    "PHONY += phase11-validate phase11-test phase11-hvc-survey phase11",
    "phase11-validate:",
    "scripts/zigux/check-phase11-build-inventory.py --self-test",
    "scripts/zigux/check-phase11-build-inventory.py",
    "scripts/zigux/check-phase11-layout-assert-surface.py --self-test",
    "scripts/zigux/check-phase11-layout-assert-surface.py",
    "scripts/zigux/check-phase11-hvc-validation-flow.py --self-test",
    "scripts/zigux/check-phase11-hvc-validation-flow.py",
    "scripts/zigux/check-phase11-hvc-cleanup-alignment.py --self-test",
    "scripts/zigux/check-phase11-hvc-cleanup-alignment.py",
    "scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
    "scripts/zigux/check-phase11-shared-replay-contract.py",
    "scripts/zigux/validate-phase11.py --self-test",
    "scripts/zigux/validate-phase11.py",
    "$(ZIG) build test --build-file zigux/tests/phase11_build.zig --summary all",
    "phase11-hvc-survey:",
    "$(ZIG) build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all",
    "phase11: phase11-validate phase11-test phase11-hvc-survey",
]
WORKFLOW_MARKERS = [
    "Self-test Phase 11 simple-driver validator",
    "python3 scripts/zigux/validate-phase11.py --self-test",
    "Self-test Phase 11 build inventory checker",
    "Self-test Phase 11 hvc validation flow checker",
    "Self-test Phase 11 hvc cleanup alignment checker",
    "Self-test Phase 11 layout assert surface checker",
    "Self-test Phase 11 shared replay contract checker",
    "Validate Phase 11 shared replay contract",
    "Validate Phase 11 simple-driver bundle",
    "make -C zigux phase11-validate",
    "Run Phase 11 watchdog and console tests",
    "zig build test --build-file zigux/tests/phase11_build.zig --summary all",
    "Run dedicated Phase 11 hvc survey replay",
    "make -C zigux phase11-hvc-survey",
]
README_MARKERS = [
    "check-phase11-build-inventory.py",
    "check-phase11-layout-assert-surface.py",
    "check-phase11-hvc-validation-flow.py",
    "check-phase11-hvc-cleanup-alignment.py",
    "check-phase11-shared-replay-contract.py",
    "validate-phase11.py",
    "validate-phase11.py --self-test",
    "Phase 11 flow",
    "make -C zigux phase11-validate",
    "make -C zigux phase11-hvc-survey",
    "phase11-shared-replay-contract.md",
    "phase11_build_inventory.json",
    "phase11_gpio_wdt_manifest.json",
    "phase11_uapi_header_parity_manifest.json",
    "dedicated hvc_console survey note and validation matrix",
    "exact shared-versus-dedicated replay commands and observed outcome lines",
]
DOCS_README_MARKERS = [
    "Phase 11 notes",
    "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-uapi-header-parity-survey.md",
    "Documentation/zigux/phase11-shared-replay-contract.md",
    "the active Phase 11 simple-driver packet now keeps the four roadmap-backed driver lanes visible from the top-level docs index",
    "python3 scripts/zigux/check-phase11-build-inventory.py",
    "python3 scripts/zigux/check-phase11-shared-replay-contract.py",
    "python3 scripts/zigux/validate-phase11.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, `make -C zigux phase11-validate`, and `make -C zigux phase11` now define the shared Phase 11 reviewability path",
]
CHECKLIST_MARKERS = [
    "if the change is a Phase 11 simple-driver slice, do `scripts/zigux/validate-phase11.py`, `zigux/tests/phase11_build.zig`, the four driver-local Phase 11 manifests, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still agree on the same bounded simple-driver scope, shared replay contract, and explicit ready-next versus blocked follow-up posture?",
    "if the change touches the shared Phase 11 tooling path, do `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, and `zigux/tests/phase11_hvc_console_survey.zig` still agree on the exact shared build inventory and the dedicated-survey boundary instead of silently implying that every Phase 11 survey gate already runs in the shared path?",
    "if the change touches the shared Phase 11 replay contract packet, do `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/validate-phase11.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, and `zigux/tests/phase11_hvc_console_survey.zig` still agree on the same shared-versus-dedicated replay boundary instead of leaving that packet split implicit?",
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
    "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
]
BUILD_INVENTORY_FIXTURE = "zigux/tests/fixtures/phase11_build_inventory.json"
PHASE11_BUILD_FIXTURE_TEST_NAMES = [
    "phase11-gpio-wdt-tests",
    "phase11-gpio-wdt-survey-tests",
    "phase11-bcm2835-wdt-tests",
    "phase11-bcm2835-wdt-survey-tests",
    "phase11-dw-wdt-tests",
    "phase11-dw-wdt-suspend-resume-tests",
    "phase11-dw-wdt-remove-idle-split-tests",
    "phase11-dw-wdt-survey-tests",
    "phase11-uapi-header-parity-survey-tests",
    "phase11-hvc-console-tests",
    "phase11-hvc-console-modem-control-split-tests",
    "phase11-hvc-console-poll-retry-split-tests",
    "phase11-hvc-console-survey-tests",
]
PHASE11_BUILD_FIXTURE_DEPEND_STEPS = [
    "run_phase11_gpio_wdt_tests",
    "run_phase11_gpio_wdt_survey_tests",
    "run_phase11_bcm2835_wdt_tests",
    "run_phase11_bcm2835_wdt_survey_tests",
    "run_phase11_dw_wdt_tests",
    "run_phase11_dw_wdt_suspend_resume_tests",
    "run_phase11_dw_wdt_remove_idle_split_tests",
    "run_phase11_dw_wdt_survey_tests",
    "run_phase11_uapi_header_parity_survey_tests",
    "run_phase11_hvc_console_tests",
    "run_phase11_hvc_console_modem_control_split_tests",
    "run_phase11_hvc_console_poll_retry_split_tests",
]
PHASE11_BUILD_FIXTURE_DEDICATED_SURVEY_REPLAYS = [
    {
        "test": "phase11-hvc-console-survey-tests",
        "path": "zigux/tests/phase11_hvc_console_survey.zig",
    },
]
PHASE11_BUILD_FIXTURE_SHARED_SPLIT_REPLAYS = [
    {
        "test": "phase11-dw-wdt-remove-idle-split-tests",
        "path": "zigux/tests/phase11_dw_wdt_remove_idle_split.zig",
    },
    {
        "test": "phase11-hvc-console-modem-control-split-tests",
        "path": "zigux/tests/phase11_hvc_console_modem_control_split.zig",
    },
    {
        "test": "phase11-hvc-console-poll-retry-split-tests",
        "path": "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
    },
]
PHASE11_BUILD_FIXTURE_SHARED_ADJUNCT_REPLAYS = [
    {
        "test": "phase11-dw-wdt-suspend-resume-tests",
        "path": "zigux/tests/phase11_dw_wdt_suspend_resume.zig",
    },
]
PHASE11_BUILD_FIXTURE_SHARED_REPLAY_MARKERS = [
    {
        "path": "zigux/tests/phase11_dw_wdt_suspend_resume.zig",
        "marker": "    try std.testing.expect(summary.resume_preserves_timeout_programming);",
    },
    {
        "path": "zigux/tests/phase11_dw_wdt_remove_idle_split.zig",
        "marker": "    try std.testing.expect(reset_available_summary.remove_clears_interrupt_status);",
    },
    {
        "path": "zigux/tests/phase11_hvc_console_modem_control_split.zig",
        "marker": "    try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",
    },
    {
        "path": "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
        "marker": "    try std.testing.expect(dispatch.invokes_sysrq_handler);",
    },
]

MANIFEST_SPECS = {
    "phase11_gpio_wdt_manifest.json": ("P11-L04", "drivers/watchdog/gpio_wdt.c", 15, [], ["phase11-gpio-wdt-platform-registration"]),
    "phase11_bcm2835_wdt_manifest.json": ("P11-L08", "drivers/watchdog/bcm2835_wdt.c", 13, [], ["phase11-bcm2835-wdt-live-platform-registration"]),
    "phase11_dw_wdt_manifest.json": ("P11-L10", "drivers/watchdog/dw_wdt.c", 12, [], ["phase11-dw-wdt-platform-and-pm"]),
    "phase11_hvc_console_manifest.json": ("P11-L18", "drivers/tty/hvc/hvc_console.c", 17, [], []),
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

def clone_fixture_root(destination_root: Path) -> None:
    for rel_path in FILES:
        source = ROOT / rel_path
        target = destination_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)

def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/zigux/validate-phase11.py")],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )

def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    result = run_validator(root)
    if result.returncode == 0:
        raise SystemExit(f"phase11-self-test:{label}:unexpected_pass")
    if expected_marker not in result.stdout:
        actual = result.stdout.strip() or "none"
        raise SystemExit(
            f"phase11-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )

def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase11_validator_selftest_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        baseline = run_validator(tmp_root)
        if baseline.returncode != 0:
            raise SystemExit(
                "phase11-self-test:baseline_failed:"
                f"{baseline.stdout.strip() or baseline.stderr.strip() or 'no_output'}"
            )

        makefile_path = tmp_root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_self_test_hook",
            tmp_root,
            "make:scripts/zigux/validate-phase11.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Self-test Phase 11 simple-driver validator\n"
                "        run: python3 scripts/zigux/validate-phase11.py --self-test\n\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_self_test_step",
            tmp_root,
            "workflow:Self-test Phase 11 simple-driver validator",
        )
        workflow_path.writeText if False else None
        workflow_path.write_text(original_workflow, encoding="utf-8")

        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Run dedicated Phase 11 hvc survey replay\n"
                "        run: make -C zigux phase11-hvc-survey\n\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_hvc_survey_step",
            tmp_root,
            "workflow:Run dedicated Phase 11 hvc survey replay",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        docs_readme_path = tmp_root / "Documentation/zigux/README.md"
        original_docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            original_docs_readme.replace(
                "Phase 11 notes\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "docs_readme_phase11_section",
            tmp_root,
            "docs_readme:Phase 11 notes",
        )
        docs_readme_path.write_text(original_docs_readme, encoding="utf-8")

        gpio_test_path = tmp_root / "zigux/tests/phase11_gpio_wdt.zig"
        original_gpio_test = gpio_test_path.read_text(encoding="utf-8")
        gpio_test_path.write_text(
            original_gpio_test.replace(
                "    const toggle_teardown = try toggle_watchdog.summarizeTeardown(false);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "gpio_teardown_summary_surface",
            tmp_root,
            "phase11_gpio_wdt_tests:    const toggle_teardown = try toggle_watchdog.summarizeTeardown(false);",
        )
        gpio_test_path.write_text(original_gpio_test, encoding="utf-8")

        hvc_test_path = tmp_root / "zigux/tests/phase11_hvc_console.zig"
        original_hvc_test = hvc_test_path.read_text(encoding="utf-8")
        hvc_test_path.write_text(
            original_hvc_test.replace(
                "    try std.testing.expectEqual(@as(u32, 11), clamped_worker.sleep_timeout_ms);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "hvc_worker_timeout_clamp_surface",
            tmp_root,
            "phase11_hvc_console_tests:    try std.testing.expectEqual(@as(u32, 11), clamped_worker.sleep_timeout_ms);",
        )
        hvc_test_path.write_text(original_hvc_test, encoding="utf-8")

        hvc_test_path.write_text(
            original_hvc_test.replace(
                "    try std.testing.expect(active_teardown.notifier_del_pending);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "hvc_close_teardown_surface",
            tmp_root,
            "phase11_hvc_console_tests:    try std.testing.expect(active_teardown.notifier_del_pending);",
        )
        hvc_test_path.write_text(original_hvc_test, encoding="utf-8")

        dw_test_path = tmp_root / "zigux/tests/phase11_dw_wdt.zig"
        original_dw_test = dw_test_path.read_text(encoding="utf-8")
        dw_test_path.write_text(
            original_dw_test.replace(
                "    try std.testing.expect(stoppable_summary.stop_uses_reset_pulse);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "dw_teardown_failure_mode_surface",
            tmp_root,
            "phase11_dw_wdt_tests:    try std.testing.expect(stoppable_summary.stop_uses_reset_pulse);",
        )
        dw_test_path.write_text(original_dw_test, encoding="utf-8")

        bcm2835_test_path = tmp_root / "zigux/tests/phase11_bcm2835_wdt.zig"
        original_bcm2835_test = bcm2835_test_path.read_text(encoding="utf-8")
        bcm2835_test_path.write_text(
            original_bcm2835_test.replace(
                "    try std.testing.expect(conflict.poweroff_handler_left_in_place);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "bcm2835_remove_failure_mode_surface",
            tmp_root,
            "phase11_bcm2835_wdt_tests:    try std.testing.expect(conflict.poweroff_handler_left_in_place);",
        )
        bcm2835_test_path.write_text(original_bcm2835_test, encoding="utf-8")

        bcm2835_test_path.write_text(
            original_bcm2835_test.replace(
                "    try std.testing.expect(blocked.poweroff_handler_conflict);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "bcm2835_blocked_platform_conflict_surface",
            tmp_root,
            "phase11_bcm2835_wdt_tests:    try std.testing.expect(blocked.poweroff_handler_conflict);",
        )
        bcm2835_test_path.write_text(original_bcm2835_test, encoding="utf-8")

        hvc_test_path.write_text(
            original_hvc_test.replace(
                "    try std.testing.expect(!stale_hangup.notifier_hangup_pending);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "hvc_stale_hangup_failure_mode_surface",
            tmp_root,
            "phase11_hvc_console_tests:    try std.testing.expect(!stale_hangup.notifier_hangup_pending);",
        )
        hvc_test_path.write_text(original_hvc_test, encoding="utf-8")

        hvc_test_path.write_text(
            original_hvc_test.replace(
                "    try std.testing.expect(attached_remove.tty_port_put_precedes_tty_vhangup);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "hvc_attached_remove_order_surface",
            tmp_root,
            "phase11_hvc_console_tests:    try std.testing.expect(attached_remove.tty_port_put_precedes_tty_vhangup);",
        )
        hvc_test_path.write_text(original_hvc_test, encoding="utf-8")

        hvc_test_path.write_text(
            original_hvc_test.replace(
                "    try std.testing.expect(!detached_remove.tty_vhangup_requested);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "hvc_detached_remove_teardown_surface",
            tmp_root,
            "phase11_hvc_console_tests:    try std.testing.expect(!detached_remove.tty_vhangup_requested);",
        )
        hvc_test_path.write_text(original_hvc_test, encoding="utf-8")

        hvc_test_path.write_text(
            original_hvc_test.replace(
                "    try std.testing.expect(!detached_remove.tty_kref_put_after_vhangup);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "hvc_detached_remove_release_surface",
            tmp_root,
            "phase11_hvc_console_tests:    try std.testing.expect(!detached_remove.tty_kref_put_after_vhangup);",
        )
        hvc_test_path.write_text(original_hvc_test, encoding="utf-8")

        hvc_test_path.write_text(
            original_hvc_test.replace(
                "    try std.testing.expect(hangup_drain.read_hangup_pending);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "hvc_poll_hangup_failure_mode_surface",
            tmp_root,
            "phase11_hvc_console_tests:    try std.testing.expect(hangup_drain.read_hangup_pending);",
        )
        hvc_test_path.write_text(original_hvc_test, encoding="utf-8")

        hvc_sysrq_path = tmp_root / "drivers/tty/hvc/hvc_console_sysrq.zig"
        hvc_sysrq_path.unlink()
        expect_missing_marker(
            "hvc_sysrq_helper_file_presence",
            tmp_root,
            "missing_file:drivers/tty/hvc/hvc_console_sysrq.zig",
        )
        clone_fixture_root(tmp_root)

        hvc_modem_control_split_path = tmp_root / "zigux/tests/phase11_hvc_console_modem_control_split.zig"
        hvc_modem_control_split_path.unlink()
        expect_missing_marker(
            "hvc_modem_control_split_file_presence",
            tmp_root,
            "missing_file:zigux/tests/phase11_hvc_console_modem_control_split.zig",
        )
        clone_fixture_root(tmp_root)

        hvc_poll_retry_split_path = tmp_root / "zigux/tests/phase11_hvc_console_poll_retry_split.zig"
        hvc_poll_retry_split_path.unlink()
        expect_missing_marker(
            "hvc_poll_retry_split_file_presence",
            tmp_root,
            "missing_file:zigux/tests/phase11_hvc_console_poll_retry_split.zig",
        )
        clone_fixture_root(tmp_root)

        matrix_path = tmp_root / "Documentation/zigux/phase11-hvc-console-validation-matrix.md"
        original_matrix = matrix_path.read_text(encoding="utf-8")
        matrix_path.write_text(
            original_matrix.replace(
                "| `hvc_cleanup()` tty-port release handoff | `summarizeCleanupHandoff()` keeps `tty_port_put()` ownership, tty-port reference drop timing, and the deferred final release boundary reviewable without claiming live tty destruction or host-backed teardown |\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "hvc_cleanup_alignment_matrix_marker",
            tmp_root,
            "phase11_hvc_console_docs:matrix:`hvc_cleanup()` tty-port release handoff",
        )
        matrix_path.write_text(original_matrix, encoding="utf-8")

        build_inventory_path = tmp_root / BUILD_INVENTORY_FIXTURE
        original_build_inventory = build_inventory_path.read_text(encoding="utf-8")

        build_inventory = json.loads(original_build_inventory)
        build_inventory["build_test_names"] = build_inventory["build_test_names"][:-1]
        build_inventory_path.write_text(json.dumps(build_inventory, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "build_inventory_test_names",
            tmp_root,
            "phase11_build_fixture:build_test_names",
        )
        build_inventory_path.write_text(original_build_inventory, encoding="utf-8")

        build_inventory = json.loads(original_build_inventory)
        build_inventory["shared_test_depend_steps"] = build_inventory["shared_test_depend_steps"][:-1]
        build_inventory_path.write_text(json.dumps(build_inventory, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "build_inventory_depend_steps",
            tmp_root,
            "phase11_build_fixture:shared_test_depend_steps",
        )
        build_inventory_path.write_text(original_build_inventory, encoding="utf-8")

        build_inventory = json.loads(original_build_inventory)
        build_inventory["dedicated_survey_replays"] = []
        build_inventory_path.write_text(json.dumps(build_inventory, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "build_inventory_dedicated_replays",
            tmp_root,
            "phase11_build_fixture:dedicated_survey_replays",
        )
        build_inventory_path.write_text(original_build_inventory, encoding="utf-8")

        build_inventory = json.loads(original_build_inventory)
        build_inventory["shared_split_replays"] = build_inventory["shared_split_replays"][:-1]
        build_inventory_path.write_text(json.dumps(build_inventory, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "build_inventory_shared_split_replays",
            tmp_root,
            "phase11_build_fixture:shared_split_replays",
        )
        build_inventory_path.write_text(original_build_inventory, encoding="utf-8")

        build_inventory = json.loads(original_build_inventory)
        build_inventory["shared_adjunct_replays"] = []
        build_inventory_path.write_text(json.dumps(build_inventory, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "build_inventory_shared_adjunct_replays",
            tmp_root,
            "phase11_build_fixture:shared_adjunct_replays",
        )
        build_inventory_path.write_text(original_build_inventory, encoding="utf-8")

        build_inventory = json.loads(original_build_inventory)
        build_inventory["shared_replay_markers"] = build_inventory["shared_replay_markers"][:-1]
        build_inventory_path.write_text(json.dumps(build_inventory, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "build_inventory_shared_replay_markers",
            tmp_root,
            "phase11_build_fixture:shared_replay_markers",
        )
        build_inventory_path.write_text(original_build_inventory, encoding="utf-8")

        print("PHASE11_SELF_TEST=pass")
        return 0

def load_manifest(name: str) -> dict[str, object]:
    manifest_path = ROOT / "zigux/tests" / name
    return json.loads(manifest_path.read_text(encoding="utf-8"))

def find_gap(manifest: dict[str, object], gap_id: str) -> dict[str, object] | None:
    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        return None
    for gap in gaps:
        if isinstance(gap, dict) and gap.get("id") == gap_id:
            return gap
    return None

def count_statuses(manifest: dict[str, object], status_match: str) -> int:
    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        return 0
    total = 0
    for gap in gaps:
        if not isinstance(gap, dict):
            continue
        status = gap.get("status")
        if not isinstance(status, str):
            continue
        if status_match.endswith("_"):
            if status.startswith(status_match):
                total += 1
        elif status == status_match:
            total += 1
    return total

def parse_build_inventory() -> dict[str, object]:
    fixture_path = ROOT / BUILD_INVENTORY_FIXTURE
    return json.loads(fixture_path.read_text(encoding="utf-8"))

def validate_build_inventory_fixture(build_inventory: dict[str, object], missing: list[str]) -> None:
    build_test_names = build_inventory.get("build_test_names")
    if build_test_names != PHASE11_BUILD_FIXTURE_TEST_NAMES:
        missing.append("phase11_build_fixture:build_test_names")

    shared_test_depend_steps = build_inventory.get("shared_test_depend_steps")
    if shared_test_depend_steps != PHASE11_BUILD_FIXTURE_DEPEND_STEPS:
        missing.append("phase11_build_fixture:shared_test_depend_steps")

    dedicated_survey_replays = build_inventory.get("dedicated_survey_replays")
    if dedicated_survey_replays != PHASE11_BUILD_FIXTURE_DEDICATED_SURVEY_REPLAYS:
        missing.append("phase11_build_fixture:dedicated_survey_replays")

    shared_split_replays = build_inventory.get("shared_split_replays")
    if shared_split_replays != PHASE11_BUILD_FIXTURE_SHARED_SPLIT_REPLAYS:
        missing.append("phase11_build_fixture:shared_split_replays")

    shared_adjunct_replays = build_inventory.get("shared_adjunct_replays")
    if shared_adjunct_replays != PHASE11_BUILD_FIXTURE_SHARED_ADJUNCT_REPLAYS:
        missing.append("phase11_build_fixture:shared_adjunct_replays")

    forbidden_build_markers = build_inventory.get("forbidden_markers")
    if forbidden_build_markers != FORBIDDEN_BUILD_MARKERS:
        missing.append("phase11_build_fixture:forbidden_markers")

    shared_replay_markers = build_inventory.get("shared_replay_markers")
    if shared_replay_markers != PHASE11_BUILD_FIXTURE_SHARED_REPLAY_MARKERS:
        missing.append("phase11_build_fixture:shared_replay_markers")

def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        return run_self_test()
    if len(sys.argv) > 1:
        print("usage: validate-phase11.py [--self-test]", file=sys.stderr)
        return 2

    missing: list[str] = []

    for rel_path in FILES:
        if not (ROOT / rel_path).exists():
            missing.append(f"missing_file:{rel_path}")

    if missing:
        print("PHASE11_VALIDATION=fail")
        print("PHASE11_VALIDATION_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE11_VALIDATION_MISSING_END")
        sys.exit(1)

    makefile = text("zigux/Makefile")
    for marker in MAKE_MARKERS:
        if marker not in makefile:
            missing.append(f"make:{marker}")

    workflow = text(".github/workflows/zigux-bootstrap.yml")
    for marker in WORKFLOW_MARKERS:
        if marker not in workflow:
            missing.append(f"workflow:{marker}")

    scripts_readme = text("scripts/zigux/README.md")
    for marker in README_MARKERS:
        if marker not in scripts_readme:
            missing.append(f"scripts_readme:{marker}")

    docs_readme = text("Documentation/zigux/README.md")
    for marker in DOCS_README_MARKERS:
        if marker not in docs_readme:
            missing.append(f"docs_readme:{marker}")

    review_checklist = text("Documentation/zigux/review-checklist.md")
    for marker in CHECKLIST_MARKERS:
        if marker not in review_checklist:
            missing.append(f"review_checklist:{marker}")

    phase11_build = text("zigux/tests/phase11_build.zig")
    for marker in BUILD_MARKERS:
        if marker not in phase11_build:
            missing.append(f"phase11_build:{marker}")
    for marker in FORBIDDEN_BUILD_MARKERS:
        if marker in phase11_build:
            missing.append(f"phase11_build:forbidden:{marker}")

    build_inventory = parse_build_inventory()
    validate_build_inventory_fixture(build_inventory, missing)

    required_shared_replay_note = text("Documentation/zigux/phase11-shared-replay-contract.md")
    for marker in [
        "Phase 11 shared replay contract",
        "zigux/tests/phase11_build.zig",
        "zigux/tests/fixtures/phase11_build_inventory.json",
        "zigux/tests/phase11_hvc_console_survey.zig",
        "shared-versus-dedicated replay boundary",
        "hvc_console survey remains dedicated because it still reads the broader documentation packet rather than only the shared driver-owned replay surfaces",
        "phase11-hvc-survey",
        "phase11-uapi-header-parity-surface",
        "phase11-dw-wdt-watchdog-header-boundary",
    ]:
        if marker not in required_shared_replay_note:
            missing.append(f"shared_replay_contract:{marker}")

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
        if name == "phase11_hvc_console_manifest.json":
            if "expectSurveyedCommitProvenance(survey_note, manifest.surveyed_commit);" not in survey_text:
                missing.append(f"{name}:survey_commit_pin")
        elif commit not in survey_text:
            missing.append(f"{name}:survey_commit_pin")
        for variable_name, status_match in survey_spec["count_markers"]:
            expected_count = count_statuses(manifest, status_match)
            count_marker = f'expectEqual(@as(usize, {expected_count}), {variable_name});'
            if count_marker not in survey_text:
                missing.append(f"{name}:survey_count:{variable_name}={expected_count}")

    if missing:
        print("PHASE11_VALIDATION=fail")
        print("PHASE11_VALIDATION_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE11_VALIDATION_MISSING_END")
        return 1

    print("PHASE11_VALIDATION=pass")
    print(f"PHASE11_REQUIRED_FILE_COUNT={len(FILES)}")
    print(f"PHASE11_STARTER_STATUS_COUNT={starter_total}")
    print(f"PHASE11_READY_NEXT_STATUS_COUNT={ready_total}")
    print(f"PHASE11_BLOCKED_STATUS_COUNT={blocked_total}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
