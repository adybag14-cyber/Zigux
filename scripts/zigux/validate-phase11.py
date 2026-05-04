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

MANIFEST_SPECS = {
    "phase11_gpio_wdt_manifest.json": ("P11-L04", "drivers/watchdog/gpio_wdt.c", 15, [], ["phase11-gpio-wdt-platform-registration"]),
    "phase11_bcm2835_wdt_manifest.json": ("P11-L08", "drivers/watchdog/bcm2835_wdt.c", 13, [], ["phase11-bcm2835-wdt-live-platform-registration"]),
    "phase11_dw_wdt_manifest.json": ("P11-L11", "drivers/watchdog/dw_wdt.c", 12, [], ["phase11-dw-wdt-platform-and-pm"]),
    "phase11_hvc_console_manifest.json": ("P11-L18", "drivers/tty/hvc/hvc_console.c", 16, [], []),
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
        makefile_path.writeText(original_makefile, encoding="utf-8")

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
            "hvc_cleanup_matrix_row",
            tmp_root,
            "phase11_hvc_console_docs:matrix:`hvc_cleanup()` tty-port release handoff",
        )
        matrix_path.write_text(original_matrix, encoding="utf-8")

        inventory_path = tmp_root / BUILD_INVENTORY_FIXTURE
        original_inventory = inventory_path.read_text(encoding="utf-8")
        inventory_path.write_text(
            original_inventory.replace(
                '    "zigux/tests/phase11_hvc_console_survey.zig"\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "build_inventory_dedicated_replay",
            tmp_root,
            "phase11_build_fixture:dedicated_survey_replays",
        )
        inventory_path.write_text(original_inventory, encoding="utf-8")

        return 0


def load_manifest(path: str) -> dict[str, object]:
    return json.loads(text(f"zigux/tests/{path}"))


def find_gap(manifest: dict[str, object], gap_id: str) -> dict[str, object] | None:
    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        return None
    for gap in gaps:
        if isinstance(gap, dict) and gap.get("id") == gap_id:
            return gap
    return None


def count_statuses(manifest: dict[str, object], prefix_or_exact: str) -> int:
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
        if prefix_or_exact.endswith("_"):
            if status.startswith(prefix_or_exact):
                total += 1
        elif status == prefix_or_exact:
            total += 1
    return total


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        return run_self_test()

    missing: list[str] = []
    for rel_path in FILES:
        if not (ROOT / rel_path).is_file():
            missing.append(rel_path)

    makefile_text = text("zigux/Makefile")
    for marker in MAKE_MARKERS:
        if marker not in makefile_text:
            missing.append(f"make:{marker}")

    workflow_text = text(".github/workflows/zigux-bootstrap.yml")
    for marker in WORKFLOW_MARKERS:
        if marker not in workflow_text:
            missing.append(f"workflow:{marker}")

    readme_text = text("scripts/zigux/README.md")
    for marker in README_MARKERS:
        if marker not in readme_text:
            missing.append(f"scripts_readme:{marker}")

    docs_readme_text = text("Documentation/zigux/README.md")
    for marker in DOCS_README_MARKERS:
        if marker not in docs_readme_text:
            missing.append(f"docs_readme:{marker}")

    checklist_text = text("Documentation/zigux/review-checklist.md")
    for marker in CHECKLIST_MARKERS:
        if marker not in checklist_text:
            missing.append(f"review_checklist:{marker}")

    build_text = text("zigux/tests/phase11_build.zig")
    for marker in BUILD_MARKERS:
        if marker not in build_text:
            missing.append(f"phase11_build:{marker}")
    for marker in FORBIDDEN_BUILD_MARKERS:
        if marker in build_text:
            missing.append(f"phase11_build:forbidden:{marker}")

    build_inventory = load_manifest("fixtures/phase11_build_inventory.json")
    if build_inventory.get("build_file") != "zigux/tests/phase11_build.zig":
        missing.append("phase11_build_fixture:build_file")
    if build_inventory.get("module_root") != "zigux/tests":
        missing.append("phase11_build_fixture:module_root")
    if build_inventory.get("make_target") != "make -C zigux phase11-test":
        missing.append("phase11_build_fixture:make_target")
    if build_inventory.get("validation_target") != "make -C zigux phase11-validate":
        missing.append("phase11_build_fixture:validation_target")
    if build_inventory.get("dedicated_hvc_survey_target") != "make -C zigux phase11-hvc-survey":
        missing.append("phase11_build_fixture:dedicated_hvc_survey_target")
    if build_inventory.get("shared_replay_command") != "zig build test --build-file zigux/tests/phase11_build.zig --summary all":
        missing.append("phase11_build_fixture:shared_replay_command")
    if build_inventory.get("dedicated_hvc_survey_command") != "zig test zigux/tests/phase11_hvc_console_survey.zig":
        missing.append("phase11_build_fixture:dedicated_hvc_survey_command")
    if build_inventory.get("phase11_build_target") != "phase11":
        missing.append("phase11_build_fixture:phase11_build_target")
    if build_inventory.get("phase11_build_targets") != ["phase11-validate", "phase11-test", "phase11-hvc-survey"]:
        missing.append("phase11_build_fixture:phase11_build_targets")

    expected_build_tests = build_inventory.get("build_tests")
    if not isinstance(expected_build_tests, list) or not all(isinstance(item, str) for item in expected_build_tests):
        missing.append("phase11_build_fixture:build_tests")
    else:
        actual_build_tests = BUILD_TEST_NAME_RE.findall(build_text)
        if actual_build_tests != expected_build_tests:
            missing.append("phase11_build_fixture:build_tests_mismatch")

    expected_test_step_dependencies = build_inventory.get("test_step_dependencies")
    if not isinstance(expected_test_step_dependencies, list) or not all(
        isinstance(item, str) for item in expected_test_step_dependencies
    ):
        missing.append("phase11_build_fixture:test_step_dependencies")
    else:
        actual_test_step_dependencies = BUILD_DEPEND_STEP_RE.findall(build_text)
        if actual_test_step_dependencies != expected_test_step_dependencies:
            missing.append("phase11_build_fixture:test_step_dependencies_mismatch")

    expected_module_roots = build_inventory.get("module_roots")
    if not isinstance(expected_module_roots, list) or not all(
        isinstance(item, dict)
        and isinstance(item.get("module"), str)
        and isinstance(item.get("root_source_file"), str)
        for item in expected_module_roots
    ):
        missing.append("phase11_build_fixture:module_roots")
    else:
        actual_module_roots = [
            {"module": module_name, "root_source_file": root_source_file}
            for module_name, root_source_file in BUILD_MODULE_RE.findall(build_text)
        ]
        if actual_module_roots != expected_module_roots:
            missing.append("phase11_build_fixture:module_roots_mismatch")

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

    hvc_manifest = load_manifest("phase11_hvc_console_manifest.json")
    hvc_commit = str(hvc_manifest.get("surveyed_commit", ""))
    hvc_survey_doc = text(HVC_DOC_PATHS["survey"])
    hvc_slice_doc = text(HVC_DOC_PATHS["slice"])
    hvc_matrix_doc = text(HVC_DOC_PATHS["matrix"])
    hvc_test_text = text("zigux/tests/phase11_hvc_console.zig")
    for marker in [
        f"reviewed against live `master` `{hvc_commit}`",
        "dedicated hvc survey replay is still separate from `zigux/tests/phase11_build.zig`",
        "a tiny final-close teardown summary",
        "a tiny notifier-add open handoff summary",
        "a khvcd worker-entry summary",
        "The next honest bounded step inside the same Phase 11 lane is to leave the starter parked unless fresh repo inspection finds another comparably small host-free sysrq or khvcd handoff that is not already covered by the notifier-add open handoff, the bounded sysrq helper, the `struct winsize` layout proof, the `struct hv_ops` layout proof, and the `hv_ops` callback-signature proof; otherwise avoid widening straight into live tty teardown, notifier execution, sysrq handling, live khvcd worker behavior, `struct hvc_struct`, or host-backed teardown.",
    ]:
        if marker not in hvc_survey_doc:
            missing.append(f"phase11_hvc_console_docs:survey:{marker}")
    for marker in [
        "adds a tiny final-close teardown summary that keeps tty detachment, `HUPCL`-gated `dtr_rts` shutdown, `notifier_del` ownership, resize-work cancellation, and `tty_wait_until_sent()` intent reviewable without claiming notifier execution or tty-core teardown timing",
        "adds a tiny tty-registration handoff summary that keeps `setup_hvc_console()`-adjacent close-wait ownership, notifier boundaries, and khvcd wakeup intent reviewable without claiming worker execution",
        "adds a tiny notifier-add open handoff summary that keeps notifier-add success, polling fallback, failed-open close cleanup, open-time IRQ request boundaries, and khvcd kick follow-through reviewable without claiming live notifier callback execution",
        "adds a tiny khvcd polling-contract summary that keeps notifier-driven versus polling-driven wakeups, bounded reschedule intent, and teardown-facing host-I/O boundaries reviewable without claiming worker execution",
        "adds a tiny khvcd worker-entry summary that keeps wake-before-sleep decisions, xmon-forced read polling, mutex-backed list walks, and timeout-backoff choices reviewable without claiming live worker execution",
        "adds a tiny khvcd sleep-and-reschedule handoff summary that keeps the pre-sleep kick check, the interruptible-state recheck, untimed schedule versus timed backoff selection, and running-state restore reviewable without claiming live worker execution",
        "adds a tiny `hvc_hangup()` disconnect summary that keeps resize-cancel ordering, the stale-count guard, tty detach, outbuf clearing, and notifier-hangup boundaries reviewable without claiming notifier callback execution",
        "adds a tiny `hvc_remove()` handoff summary that keeps console-lock slot clearing, the paired `vtermnos[]` and `cons_ops[]` release, `tty_port_put()` ordering, `tty_vhangup()` follow-through, and the keep-IRQ-until-hangup teardown boundary reviewable without claiming live console locking or IRQ teardown",
        "This slice does not claim tty-driver registration, khvcd polling or execution, live sysrq execution, notifier callback execution, hotplug discovery, or live hypervisor-backed reads and writes yet.",
        "The next honest bounded step inside the same Phase 11 lane is to leave this starter parked unless another comparably small host-free notifier callback or khvcd handoff becomes obvious; otherwise avoid widening straight into live tty teardown, live khvcd worker behavior, or host-backed teardown.",
    ]:
        if marker not in hvc_slice_doc:
            missing.append(f"phase11_hvc_console_docs:slice:{marker}")
    for marker in [
        "PHASE11_HVC_CONSOLE_STATUS=cleanup_handoff_landed",
        f"reviewed against live `master` `{hvc_commit}`",
        "| final-close teardown handoff | `summarizeCloseTeardown()` keeps tty detachment, `HUPCL`-gated `dtr_rts` shutdown, `notifier_del` ownership, resize-work cancellation, `tty_wait_until_sent()` intent, and final `port_initialized` clearing reviewable without claiming notifier callbacks or tty-core teardown timing |",
        "`zigux/tests/phase11_build.zig` continues to run `zigux/tests/phase11_hvc_console.zig` inside the shared Phase 11 starter replay",
        "`zigux/tests/phase11_hvc_console.zig` now keeps the initialized, uninitialized, and hung-up final-close teardown assertions inside the shared Phase 11 replay",
        "`zigux/tests/phase11_hvc_console.zig` now keeps the worker-entry sleep and backoff assertions inside the shared Phase 11 replay",
        "`zigux/tests/phase11_hvc_console.zig` now keeps the timed-sleep, untimed-sleep, pre-state kick, and post-state kick assertions inside the shared Phase 11 replay",
        "`zigux/tests/phase11_hvc_console.zig` now keeps the active-hangup and stale-hangup assertions inside the shared Phase 11 replay",
        "`zigux/tests/phase11_hvc_console.zig` now keeps the tty-attached and tty-detached remove-handoff assertions inside the shared Phase 11 replay",
        "`hvc_cleanup()` tty-port release handoff",
        "`zigux/tests/phase11_hvc_console.zig` now keeps the final-close and hangup-driven cleanup handoff assertions inside the shared Phase 11 replay",
        "leave this helper parked unless another comparably small host-free tty-port teardown split becomes obvious",
        "the shared Phase 11 gate for this lane remains `zigux/tests/phase11_build.zig`",
        "the dedicated archival survey gate remains `zigux/tests/phase11_hvc_console_survey.zig`",
    ]:
        if marker not in hvc_matrix_doc:
            missing.append(f"phase11_hvc_console_docs:matrix:{marker}")
    for marker in [
        "khvcd timeout underflow is now pinned in the focused hvc replay",
        "timeout_ms = 0",
        "final-close teardown sequencing is now pinned separately from the broader close-wait gate",
        "active_teardown.notifier_del_pending",
        "`__hvc_poll()` hangup pressure is now pinned separately from the throttled and detached cases",
        "read_hangup_pending",
        "remove-time detached teardown is now pinned separately from the attached path",
        "tty_attached = false",
        "final-close and hangup-driven cleanup handoff boundaries are now pinned separately from the broader remove packet",
        "close-skipped requests",
        "deferred final release explicit",
    ]:
        if marker not in hvc_matrix_doc:
            missing.append(f"phase11_hvc_console_docs:failure_modes:{marker}")
    for marker in [
        'test "phase11 hvc console keeps final-close teardown sequencing reviewable" {',
        "    try std.testing.expect(active_teardown.notifier_del_pending);",
        "    try std.testing.expect(!uninitialized_teardown.notifier_del_pending);",
        'test "phase11 hvc console keeps hvc_hangup disconnect boundaries reviewable" {',
        "    try std.testing.expect(active_hangup.notifier_hangup_pending);",
        "    try std.testing.expect(!stale_hangup.notifier_hangup_pending);",
        'test "phase11 hvc console keeps khvcd worker-entry sleep and backoff boundaries reviewable" {',
        "        .timeout_ms = 0,",
        "    try std.testing.expectEqual(@as(u32, 11), clamped_worker.sleep_timeout_ms);",
        'test "phase11 hvc console keeps __hvc_poll drain ordering and wakeup boundaries reviewable" {',
        "    try std.testing.expect(hangup_drain.read_hangup_pending);",
        "    try std.testing.expect(hangup_drain.read_poll_armed_without_irq);",
        'test "phase11 hvc console keeps hvc_remove handoff boundaries reviewable" {',
        "    try std.testing.expect(attached_remove.tty_port_put_precedes_tty_vhangup);",
        "        .tty_attached = false,",
        "    try std.testing.expect(!detached_remove.tty_vhangup_requested);",
        "    try std.testing.expect(!detached_remove.tty_kref_put_after_vhangup);",
        'test "phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable" {',
        "    try std.testing.expect(final_cleanup.tty_port_put_requested);",
        "    try std.testing.expect(hangup_cleanup.close_skipped);",
        "    try std.testing.expect(hangup_cleanup.drops_tty_port_reference);",
    ]:
        if marker not in hvc_test_text:
            missing.append(f"phase11_hvc_console_tests:{marker}")

    gpio_manifest = load_manifest("phase11_gpio_wdt_manifest.json")
    gpio_survey_doc = text(GPIO_WDT_DOC_PATHS["survey"])
    gpio_slice_doc = text(GPIO_WDT_DOC_PATHS["slice"])
    gpio_matrix_doc = text(GPIO_WDT_DOC_PATHS["matrix"])
    gpio_test_text = text("zigux/tests/phase11_gpio_wdt.zig")
    for marker in [
        "This survey note now tracks the landed Phase 11 `gpio_wdt` starter anchored to `drivers/watchdog/gpio_wdt.c`.",
        "a tiny nowayout-aware teardown-facing stop helper that separates watchdog-core policy blocking from hardware `always-running` behavior",
        "an explicit `summarizeTeardown()` helper for eternal-ping disable ordering plus toggle-versus-level teardown fallout",
        "a tiny `registerDeviceCallSummary()` helper, so the lane now exposes the exact watchdog metadata, timeout, parent, `nowayout`, and stop-on-reboot state that would reach the first bounded `devm_watchdog_register_device()` request without claiming a live call",
        "The next honest bounded step inside the same lane is to leave this starter parked unless fresh repo inspection finds another comparably small teardown or failure-mode drift inside `gpio_wdt`.",
    ]:
        if marker not in gpio_survey_doc:
            missing.append(f"phase11_gpio_wdt_docs:survey:{marker}")
    for marker in [
        "adds an explicit `summarizeTeardown()` helper so eternal-ping disable ordering, toggle-versus-level disable fallout, and `always-running` versus `nowayout` stop failure modes stay reviewable before any unregister path exists",
        "distinguishes watchdog-core `nowayout` stop blocking from the driver's own `always-running` hardware behavior so teardown-facing stop review does not blur policy gating with hardware gating",
        "adds one tiny `registerDeviceCallSummary()` helper so the starter records the exact watchdog metadata, timeout bounds, driver-data ownership, parent linkage, `nowayout`, stop-on-reboot, startup state, and explicit `register_device_requested` marker that would reach the first bounded `devm_watchdog_register_device()` request without claiming the live call itself",
        "The next honest bounded step inside the same Phase 11 lane is to leave the starter parked unless fresh repo inspection finds another comparably small teardown or failure-mode drift inside `gpio_wdt`.",
    ]:
        if marker not in gpio_slice_doc:
            missing.append(f"phase11_gpio_wdt_docs:slice:{marker}")
    for marker in [
        "PHASE11_GPIO_WDT_STATUS=metadata_teardown_and_register_device_surface_landed",
        "| teardown-facing stop and failure-mode evidence | `requestStop()` keeps nowayout blocking, non-`always_running` disable, and `always_running` keepalive outcomes reviewable as teardown-facing metadata immediately adjacent to the current register-device planning boundary |",
        "| explicit disable-order teardown summary | `summarizeTeardown()` now keeps `gpio_wdt_disable()`-style eternal-ping ordering, toggle-mode return-to-input behavior, level-mode asserted-output behavior, and `always-running` versus `nowayout` stop fallout reviewable without claiming a live unregister path |",
        "| register-device call surface | `registerDeviceCallSummary()` now records the exact watchdog metadata, timeout bounds, driver-data ownership, parent linkage, `nowayout`, stop-on-reboot, startup state, and explicit `register_device_requested` marker that would reach the first bounded `devm_watchdog_register_device()` request without claiming the live call or descriptor path |",
        "current shared replay wiring on `master` includes both `phase11-gpio-wdt-tests` and `phase11-gpio-wdt-survey-tests`",
    ]:
        if marker not in gpio_matrix_doc:
            missing.append(f"phase11_gpio_wdt_docs:matrix:{marker}")
    for marker in [
        'test "phase11 gpio_wdt stop requests distinguish nowayout gating from always-running hardware" {',
        "    try std.testing.expectEqual(gpio_wdt.StopDisposition.blocked_by_nowayout, blocked.disposition);",
        "    const toggle_teardown = try toggle_watchdog.summarizeTeardown(false);",
        "    try std.testing.expect(toggle_teardown.disable_returns_toggle_line_to_input);",
        "    try std.testing.expect(level_teardown.disable_keeps_level_line_output);",
        "    try std.testing.expect(prestarted_call.register_device_requested);",
    ]:
        if marker not in gpio_test_text:
            missing.append(f"phase11_gpio_wdt_tests:{marker}")

    bcm2835_manifest = load_manifest("phase11_bcm2835_wdt_manifest.json")
    bcm2835_commit = str(bcm2835_manifest.get("surveyed_commit", ""))
    bcm2835_survey_doc = text(BCM2835_WDT_DOC_PATHS["survey"])
    bcm2835_slice_doc = text(BCM2835_WDT_DOC_PATHS["slice"])
    bcm2835_matrix_doc = text(BCM2835_WDT_DOC_PATHS["matrix"])
    bcm2835_test_text = text("zigux/tests/phase11_bcm2835_wdt.zig")
    for marker in [
        f"reviewed against live `master` `{bcm2835_commit}`",
        "a tiny platform-registration or PM-base handoff summary",
        "a tiny remove-time ownership summary",
        "The next honest bounded step inside the same Phase 11 family is not another review-only handoff.",
    ]:
        if marker not in bcm2835_survey_doc:
            missing.append(f"phase11_bcm2835_wdt_docs:survey:{marker}")
    for marker in [
        "adds a tiny platform-registration and PM-base handoff summary for parent attachment, PM base availability, drvdata handoff readiness, register-device intent, and poweroff claim-vs-conflict reviewability",
        "adds a tiny remove-time teardown summary for devm-managed watchdog cleanup while clearing the shared poweroff handler only when the bcm2835 lane currently owns it",
        "This slice does not claim platform-driver registration, watchdog-core registration, MMIO access, delayed restart behavior, module parameter wiring beyond bookkeeping, live remove-time poweroff-handler release logic, or live poweroff integration yet.",
    ]:
        if marker not in bcm2835_slice_doc:
            missing.append(f"phase11_bcm2835_wdt_docs:slice:{marker}")
    for marker in [
        "| platform registration and PM-base handoff | `platformHandoffSummary()` now records parent attachment, PM-base availability, drvdata handoff readiness, register-device intent, and poweroff claim-vs-conflict reviewability without claiming platform-driver execution or live MMIO |",
        "| remove-time teardown boundary | `removeSummary()` records that watchdog teardown stays devm-managed while the explicit remove callback only clears the shared poweroff handler if the bcm2835 lane owns it, leaving conflicting ownership in place |",
        "current shared replay wiring on `master` includes both `phase11-bcm2835-wdt-tests` and `phase11-bcm2835-wdt-survey-tests`",
    ]:
        if marker not in bcm2835_matrix_doc:
            missing.append(f"phase11_bcm2835_wdt_docs:matrix:{marker}")
    for marker in [
        'test "phase11 bcm2835_wdt platform handoff summary keeps parent and PM-base prerequisites reviewable" {',
        "    try std.testing.expect(ready.pm_base_handoff_ready);",
        "    try std.testing.expect(!blocked.pm_base_handoff_ready);",
        "    try std.testing.expect(blocked.poweroff_handler_conflict);",
        'test "phase11 bcm2835_wdt remove summary only clears the shared poweroff handler when bcm2835 owns it" {',
        "    try std.testing.expect(conflict.poweroff_handler_left_in_place);",
        "    try std.testing.expect(!absent.poweroff_handler_left_in_place);",
    ]:
        if marker not in bcm2835_test_text:
            missing.append(f"phase11_bcm2835_wdt_tests:{marker}")

    dw_manifest = load_manifest("phase11_dw_wdt_manifest.json")
    dw_commit = str(dw_manifest.get("surveyed_commit", ""))
    dw_survey_doc = text(DW_WDT_DOC_PATHS["survey"])
    dw_slice_doc = text(DW_WDT_DOC_PATHS["slice"])
    dw_matrix_doc = text(DW_WDT_DOC_PATHS["matrix"])
    dw_test_text = text("zigux/tests/phase11_dw_wdt.zig")
    for marker in [
        f"`master` `{dw_commit}`",
        "an explicit `summarizeTeardownLifecycle()` stop-and-restart helper",
        "the focused `dw_wdt` driver and survey replays for this landed starter packet remain green",
    ]:
        if marker not in dw_survey_doc:
            missing.append(f"phase11_dw_wdt_docs:survey:{marker}")
    for marker in [
        "keeps the DesignWare non-stoppable stop semantics explicit when reset control is unavailable",
        "adds a tiny platform-resource preflight plus live resource-order summary that keeps the timer-clock choice, optional APB clock presence, reset-control availability, and optional pretimeout-IRQ wiring, plus the bounded tclk, optional pclk, reset, irq, and registration sequencing reviewable before any live devm calls",
        "adds an explicit `summarizeTeardownLifecycle()` helper so reset-control-backed stop pulses, non-stoppable stop fallout, reset-mode restart forcing, and restart-from-stopped enablement stay reviewable before any live platform remove or PM teardown work",
    ]:
        if marker not in dw_slice_doc:
            missing.append(f"phase11_dw_wdt_docs:slice:{marker}")
    for marker in [
        "| platform-resource ordering surface | `platformResourcePreflightSummary()` plus `liveResourceOrderSummary()` keep timer-clock choice, optional APB clock presence, reset-control availability, optional pretimeout-IRQ wiring, and the bounded tclk, optional pclk, reset, irq, and registration sequencing reviewable before any live devm calls |",
        "| stop and restart failure-mode boundary | `stop()`, `armRestart()`, and `summarizeTeardownLifecycle()` keep the non-stoppable stop failure-mode boundary explicit when reset control is unavailable while still recording the stoppable path, interrupt-status clearing, restart arming, reset-mode restart forcing, and restart-from-stopped enablement without claiming reboot-side effects |",
        "current shared replay wiring on `master` includes both `phase11-dw-wdt-tests` and `phase11-dw-wdt-survey-tests`",
    ]:
        if marker not in dw_matrix_doc:
            missing.append(f"phase11_dw_wdt_docs:matrix:{marker}")
    for marker in [
        'test "phase11 dw_wdt platform resource preflight keeps clock choice and optional resources reviewable" {',
        'test "phase11 dw_wdt live resource order keeps tclk, optional pclk, reset, irq, and registration sequencing explicit" {',
        'test "phase11 dw_wdt stop and restart stay bounded to reset-control and non-stoppable semantics" {',
        "    try std.testing.expect(!unstoppable_summary.stop_uses_reset_pulse);",
        "    try std.testing.expect(stoppable_summary.stop_uses_reset_pulse);",
    ]:
        if marker not in dw_test_text:
            missing.append(f"phase11_dw_wdt_tests:{marker}")

    if missing:
        print("PHASE11_VALIDATION=fail")
        print("PHASE11_VALIDATION_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE11_VALIDATION_MISSING_END")
        sys.exit(1)

    print("PHASE11_VALIDATION=pass")
    print(f"PHASE11_REQUIRED_FILE_COUNT={len(FILES)}")
    print(f"PHASE11_STARTER_STATUS_COUNT={starter_total}")
    print(f"PHASE11_READY_NEXT_STATUS_COUNT={ready_total}")
    print(f"PHASE11_BLOCKED_STATUS_COUNT={blocked_total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
