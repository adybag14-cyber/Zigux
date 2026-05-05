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
    "scripts/zigux/check-phase11-header-boundary-packet.py",
    "scripts/zigux/validate-phase11.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md",
    "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
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
    "scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
    "scripts/zigux/check-phase11-header-boundary-packet.py",
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
    "Self-test Phase 11 header boundary packet checker",
    "Validate Phase 11 shared replay contract",
    "Validate Phase 11 header boundary packet",
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
    "check-phase11-header-boundary-packet.py",
    "check-phase11-header-boundary-packet.py --self-test",
    "validate-phase11.py",
    "validate-phase11.py --self-test",
    "Phase 11 flow",
    "make -C zigux phase11-validate",
    "make -C zigux phase11-hvc-survey",
    "phase11-shared-replay-contract.md",
    "phase11_build_inventory.json",
    "phase11_gpio_wdt_manifest.json",
    "phase11_uapi_header_parity_manifest.json",
    "paired UAPI header parity packet",
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
    "zigux/tests/phase11_gpio_wdt_manifest.json",
    "zigux/tests/phase11_bcm2835_wdt_manifest.json",
    "zigux/tests/phase11_dw_wdt_manifest.json",
    "zigux/tests/phase11_hvc_console_manifest.json",
    "python3 scripts/zigux/check-phase11-build-inventory.py",
    "python3 scripts/zigux/check-phase11-shared-replay-contract.py",
    "python3 scripts/zigux/check-phase11-header-boundary-packet.py",
    "python3 scripts/zigux/validate-phase11.py",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "make -C zigux phase11-validate",
    "make -C zigux phase11",
]
CHECKLIST_MARKERS = [
    "if the change is a Phase 11 simple-driver slice, do `scripts/zigux/validate-phase11.py`, `zigux/tests/phase11_build.zig`, the four driver-local Phase 11 manifests, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still agree on the same bounded simple-driver scope, shared replay contract, and explicit ready-next versus blocked follow-up posture?",
    "if the change touches the shared Phase 11 tooling path, do `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, and `zigux/tests/phase11_hvc_console_survey.zig` still agree on the exact shared build inventory and the dedicated-survey boundary instead of silently implying that every Phase 11 survey gate already runs in the shared path?",
    "if the change touches the shared Phase 11 replay contract packet, do `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/validate-phase11.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, and `zigux/tests/phase11_hvc_console_survey.zig` still agree on the same shared-versus-dedicated replay boundary instead of leaving that packet split implicit?",
    "if the change touches the active Phase 11 contributor packet, do `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still keep the pre-replay stack, the shared-versus-dedicated `hvc_console` split, and the shared header-boundary packet aligned?",
]
REVIEW_GUIDE_MARKERS = [
    "## Phase 11: Simple-driver packet",
    "python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
    "python3 scripts/zigux/check-phase11-header-boundary-packet.py",
    "zigux/tests/phase11_uapi_header_parity_manifest.json",
    "Do the pre-replay checkers still describe the same delivery contract that the shared build inventory, the shared header-boundary packet, the active review checklist prompt, the four roadmap-backed driver matrices, and the Phase 11 manifests claim?",
]
TESTS_COMPANION_MARKERS = [
    "## Phase 11 tests-root packet",
    "scripts/zigux/check-phase11-header-boundary-packet.py",
    "zigux/tests/phase11_uapi_header_parity_manifest.json",
    "keeps the shared header-boundary packet explicit through `scripts/zigux/check-phase11-header-boundary-packet.py`",
]
TESTS_README_MARKERS = [
    "Phase 11 guidance",
    "keep the current Phase 11 simple-driver packet reviewable through `zigux/tests/phase11_build.zig`, `scripts/zigux/validate-phase11.py`, `make -C zigux phase11-validate`, and `zigux/tests/fixtures/phase11_build_inventory.json` instead of widening into ad hoc driver-local bootstrap claims.",
    "four shared split and adjunct replays",
    "shared-versus-dedicated replay boundary",
    "shared header packet as the docs-root and validator-first packet.",
    "`scripts/zigux/check-phase11-header-boundary-packet.py` keeps the shared header-boundary packet explicit beside that split.",
    "Phase 11: do `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_dw_wdt_suspend_resume.zig`, `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still keep the pre-replay stack, the shared-versus-dedicated `hvc_console` split, and the shared header-boundary packet aligned?",
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

        scripts_readme_path = tmp_root / "scripts/zigux/README.md"
        original_scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            original_scripts_readme.replace(
                "check-phase11-header-boundary-packet.py --self-test",
                "check-phase11-shared-replay-contract.py --self-test",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "scripts_readme_header_boundary_self_test_marker",
            tmp_root,
            "scripts_readme:check-phase11-header-boundary-packet.py --self-test",
        )
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        docs_readme_path = tmp_root / "Documentation/zigux/README.md"
        original_docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            original_docs_readme.replace(
                "zigux/tests/phase11_dw_wdt_manifest.json",
                "zigux/tests/phase11_uapi_header_parity_manifest.json",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "docs_readme_manifest_inventory_marker",
            tmp_root,
            "docs_readme:zigux/tests/phase11_dw_wdt_manifest.json",
        )
        docs_readme_path.write_text(original_docs_readme, encoding="utf-8")

        review_checklist_path = tmp_root / "Documentation/zigux/review-checklist.md"
        original_review_checklist = review_checklist_path.read_text(encoding="utf-8")
        review_checklist_path.write_text(
            original_review_checklist.replace(
                "scripts/zigux/check-phase11-header-boundary-packet.py",
                "scripts/zigux/check-phase11-shared-replay-contract.py",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "review_checklist_header_boundary_marker",
            tmp_root,
            "review_checklist:if the change touches the active Phase 11 contributor packet, do `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still keep the pre-replay stack, the shared-versus-dedicated `hvc_console` split, and the shared header-boundary packet aligned?",
        )
        review_checklist_path.write_text(original_review_checklist, encoding="utf-8")

        review_guide_path = tmp_root / "Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md"
        original_review_guide = review_guide_path.read_text(encoding="utf-8")
        review_guide_path.write_text(
            original_review_guide.replace(
                "python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
                "python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "review_guide_header_boundary_marker",
            tmp_root,
            "review_guide:python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
        )
        review_guide_path.write_text(original_review_guide, encoding="utf-8")

        tests_companion_path = tmp_root / "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md"
        original_tests_companion = tests_companion_path.read_text(encoding="utf-8")
        tests_companion_path.write_text(
            original_tests_companion.replace(
                "keeps the shared header-boundary packet explicit through `scripts/zigux/check-phase11-header-boundary-packet.py`",
                "keeps the shared packet explicit through `scripts/zigux/check-phase11-shared-replay-contract.py`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_companion_header_boundary_marker",
            tmp_root,
            "tests_companion:keeps the shared header-boundary packet explicit through `scripts/zigux/check-phase11-header-boundary-packet.py`",
        )
        tests_companion_path.write_text(original_tests_companion, encoding="utf-8")

        tests_readme_path = tmp_root / "zigux/tests/README.md"
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "four shared split and adjunct replays",
                "shared split replays",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_phase11_guidance_marker",
            tmp_root,
            "tests_readme:four shared split and adjunct replays",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        tests_readme_path.write_text(
            original_tests_readme.replace(
                "zigux/tests/phase11_dw_wdt_suspend_resume.zig",
                "zigux/tests/phase11_hvc_console_survey.zig",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_phase11_contributor_prompt",
            tmp_root,
            "tests_readme:Phase 11: do `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-layout-assert-surface.py`, `scripts/zigux/check-phase11-hvc-validation-flow.py`, `scripts/zigux/check-phase11-hvc-cleanup-alignment.py`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_dw_wdt_suspend_resume.zig`, `zigux/tests/phase11_dw_wdt_remove_idle_split.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, and `zigux/tests/phase11_uapi_header_parity_manifest.json` still keep the pre-replay stack, the shared-versus-dedicated `hvc_console` split, and the shared header-boundary packet aligned?",
        )
        tests_readme_path.write_text(original_tests_readme, encoding="utf-8")

        makefile_path = tmp_root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
                "scripts/zigux/check-phase11-build-inventory.py --self-test",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_header_boundary_self_test_hook",
            tmp_root,
            "make:scripts/zigux/check-phase11-header-boundary-packet.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        workflow_path = tmp_root / ".github/workflows/zigux-bootstrap.yml"
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "Validate Phase 11 header boundary packet",
                "Validate Phase 11 replay packet",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_header_boundary_validate_step",
            tmp_root,
            "workflow:Validate Phase 11 header boundary packet",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        header_checker_path = tmp_root / "scripts/zigux/check-phase11-header-boundary-packet.py"
        header_checker_path.unlink()
        expect_missing_marker(
            "header_boundary_checker_file_presence",
            tmp_root,
            "missing_file:scripts/zigux/check-phase11-header-boundary-packet.py",
        )
        clone_fixture_root(tmp_root)

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

    review_guide = text("Documentation/zigux/phase10-phase11-phase13-validator-first-review-guide.md")
    for marker in REVIEW_GUIDE_MARKERS:
        if marker not in review_guide:
            missing.append(f"review_guide:{marker}")

    tests_companion = text("Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md")
    for marker in TESTS_COMPANION_MARKERS:
        if marker not in tests_companion:
            missing.append(f"tests_companion:{marker}")

    tests_readme = text("zigux/tests/README.md")
    for marker in TESTS_README_MARKERS:
        if marker not in tests_readme:
            missing.append(f"tests_readme:{marker}")

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
        "`python3 scripts/zigux/check-phase11-header-boundary-packet.py`",
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
