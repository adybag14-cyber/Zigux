#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

PHASE11_CONTRACT_PATH = "Documentation/zigux/phase11-shared-replay-contract.md"
DRIVER_LANE_SEQUENCING_PATH = "Documentation/zigux/phase11-driver-lane-sequencing.md"
BCM2835_WDT_MATRIX_PATH = "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md"
GPIO_WDT_MATRIX_PATH = "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md"
DW_WDT_MATRIX_PATH = "Documentation/zigux/phase11-dw-wdt-validation-matrix.md"
HVC_CONSOLE_MATRIX_PATH = "Documentation/zigux/phase11-hvc-console-validation-matrix.md"
DOCS_README_PATH = "Documentation/zigux/README.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
BUILD_PATH = "zigux/tests/phase11_build.zig"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"

REQUIRED_CONTRACT_MARKERS = [
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-console-survey.md`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`Documentation/zigux/phase11-uapi-header-parity-survey.md`",
    "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
    "`scripts/zigux/check-phase11-shared-replay-contract.py`",
    "`scripts/zigux/check-phase11-header-boundary-packet.py`",
    "- `scripts/zigux/check-phase11-hvc-survey-packet.py`\n- `zigux/tests/phase11_build.zig`",
    "`zigux/tests/phase11_hvc_cleanup.zig`",
    "`zigux/tests/phase11_hvc_console_manifest.json`",
    "`make -C zigux phase11-hvc-survey`",
    "`zigux/tests/phase11_uapi_header_parity_manifest.json`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`drivers/watchdog/dw_wdt_verify.zig`",
    "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
    "The shipped DesignWare watchdog sub-packet inside that shared route stays explicit as `phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`.",
    "`drivers/tty/hvc/hvc_console_verify.zig`",
    "the dedicated `scripts/zigux/check-phase11-hvc-survey-packet.py` route",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`zig build test --build-file zigux/tests/phase11_build.zig --summary all`",
    "`make -C zigux phase11`",
    "`Documentation/zigux/phase11-closure-note.md`",
    "The shared closure checkpoint now also stays explicit beside that replay route:",
    "there is no dedicated shared `validate-phase11.py` on `master`",
    "there is no shipped `zigux/tests/fixtures/phase11_build_inventory.json` on `master`",
    "there is no broader multi-checker Phase 11 validator stack on `master`",
    "The dedicated archival bcm2835 evidence also stays explicit beside that shared route:",
    "`Documentation/zigux/phase11-bcm2835-wdt-survey.md`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest.json`",
    "`zigux/tests/phase11_bcm2835_wdt_survey.zig`",
    "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
    "`python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
    "`Documentation/zigux/phase11-dw-wdt-teardown-note.md`",
    "`Documentation/zigux/phase11-dw-wdt-teardown-note.md` keeps the bounded DesignWare stop, teardown, and remove ownership split explicit for the watchdog packet",
    "- `Documentation/zigux/phase11-gpio-wdt-survey.md`\n- `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`\n- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "- gpio watchdog: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-gpio-wdt-teardown-note.md`, `zigux/tests/phase11_gpio_wdt_manifest.json`, and `zigux/tests/phase11_gpio_wdt_survey.zig`",
    "`Documentation/zigux/phase11-gpio-wdt-teardown-note.md` keeps the bounded GPIO stop-policy, stop-transition, and teardown-handoff split explicit for the starter packet",
    "khvcd worker-entry sleep, kick, poll-mask, minimum-timeout flooring, maximum-timeout clamping, timeout-backoff, and invalid-open-count replays beside the shared packet",
]
REQUIRED_DRIVER_LANE_SEQUENCING_MARKERS = [
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`make -C zigux phase11-hvc-survey`",
    "the dedicated HVC survey checker or its `make -C zigux phase11-hvc-survey` replay path",
]
REQUIRED_BCM2835_WDT_MATRIX_MARKERS = [
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`zigux/tests/README.md`",
    "`zigux/Makefile`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests` remain the shared Phase 11 artifacts that cover this bcm2835 packet",
    "keep `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from either the shipped shared replay route or the dedicated bcm2835 archival packet",
]
REQUIRED_GPIO_WDT_MATRIX_MARKERS = [
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`zigux/tests/README.md`",
    "`zigux/Makefile`",
    "`drivers/watchdog/gpio_wdt.zig`",
    "keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-gpio-wdt-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/tests/phase11_gpio_wdt_manifest.json`, `zigux/tests/phase11_gpio_wdt_survey.zig`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from the shipped shared Phase 11 replay route or the focused shared header-boundary packet",
]
REQUIRED_DW_WDT_MATRIX_MARKERS = [
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`zigux/tests/README.md`",
    "`zigux/Makefile`",
    "`drivers/watchdog/dw_wdt_verify.zig`",
    "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
    "`phase11-dw-wdt-tests`, `phase11-dw-wdt-registration-scaffold-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests` remain the shared Phase 11 artifacts that cover this DesignWare packet",
    "keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from the shipped shared Phase 11 replay route or the focused shared header-boundary packet",
]
REQUIRED_HVC_CONSOLE_MATRIX_MARKERS = [
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`zigux/tests/README.md`",
    "`zigux/Makefile`",
    "`drivers/tty/hvc/hvc_console_verify.zig`",
    "`zigux/tests/phase11_hvc_cleanup.zig`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned with this matrix whenever the shared-versus-dedicated HVC replay split changes so the dedicated `hvc_cleanup()` teardown replay and the compile-local `hvc_console_verify` replay stay explicit inside the wider Phase 11 packet, the focused shared header-boundary packet stays visible beside them, and the dedicated archival `phase11-hvc-survey` route keeps failing closed",
]
REQUIRED_DOCS_README_MARKERS = [
    "Phase 11 notes",
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-gpio-wdt-survey.md`",
    "`Documentation/zigux/phase11-gpio-wdt-teardown-note.md`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-teardown-note.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-console-survey.md`",
    "`Documentation/zigux/phase11-bcm2835-wdt-survey.md`",
    "`Documentation/zigux/phase11-closure-note.md`",
    "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
    "`scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` now keep the shared-versus-dedicated Phase 11 packet honest: the shipped contract checker plus the focused header-boundary checker, the shared build-and-make packet, the dedicated `hvc_console` survey note and replay, the bounded `hvc_cleanup()` handoff, the focused shared header-boundary note and manifest-backed survey replay, and the four driver-local validation matrices all remain reviewable without implying a removed `validate-phase11.py`, a missing build inventory, or a broader checker-script packet than the dedicated `scripts/zigux/check-phase11-hvc-survey-packet.py` archival route plus the shipped `check-phase11-shared-replay-contract.py` and `check-phase11-header-boundary-packet.py` routes on `master`.",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
]
REQUIRED_SCRIPT_README_MARKERS = [
    "Phase 11 notes",
    "- `check-phase11-dw-wdt-packet.py`",
    "- `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` now keep the shared-versus-dedicated Phase 11 packet honest: the shipped contract checker plus the dedicated bcm2835 archival checker route, the focused header-boundary checker, the dedicated bcm2835 manifest-backed survey checkpoint, the dedicated HVC survey checker route and manifest-backed archival checkpoint, the shared build-and-make packet, the parked shared closure checkpoint, the parked driver-lane owner map, the dedicated gpio teardown companion, the dedicated DesignWare teardown companion, the dedicated `hvc_console` survey note, teardown note, and checker-backed `make -C zigux phase11-hvc-survey` replay, the bounded `hvc_cleanup()` handoff, the focused shared header-boundary note and manifest-backed survey replay, and the four driver-local validation matrices all remain reviewable without implying a removed `validate-phase11.py`, a missing build inventory, or a broader checker-script packet that does not exist on `master`.",
    "the dedicated DesignWare teardown companion",
    "`Documentation/zigux/phase11-closure-note.md`",
    "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`scripts/zigux/check-phase11-shared-replay-contract.py`",
]
REQUIRED_TESTS_README_MARKERS = [
    "keep the shared-versus-dedicated Phase 11 simple-driver packet explicit in the tests root too:",
    "`Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `zig build test --build-file zigux/tests/phase11_build.zig --summary all`, and `make -C zigux phase11` should continue to keep the shipped shared replay route, the focused shared header-boundary packet, the dedicated `hvc_console` archival survey note and replay, the bounded `hvc_cleanup()` teardown handoff, and the four driver-local validation matrices reviewable from the tests root without implying a removed `validate-phase11.py`, a shipped `zigux/tests/fixtures/phase11_build_inventory.json`, or a broader checker-script packet than the dedicated `scripts/zigux/check-phase11-hvc-survey-packet.py` archival route plus the shipped `check-phase11-shared-replay-contract.py` and `check-phase11-header-boundary-packet.py` routes on `master`",
    "`Documentation/zigux/phase11-closure-note.md`",
    "`Documentation/zigux/phase11-dw-wdt-teardown-note.md`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "`scripts/zigux/check-phase11-hvc-survey-packet.py`",
    "`zigux/tests/phase11_hvc_console_manifest.json`",
    "`make -C zigux phase11-hvc-survey`",
]
REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "* if the change touches the shared Phase 11 simple-driver packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/tests/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `zig build test --build-file zigux/tests/phase11_build.zig --summary all`, `make -C zigux phase11`, and `make -C zigux phase11-hvc-survey` still agree on the same shared-versus-dedicated replay split, the focused header-boundary note plus manifest-backed survey packet, the four driver-local validation matrices, the bounded `hvc_cleanup()` teardown handoff, and the dedicated archival `hvc_console` survey plus checker-backed replay route without implying a removed `validate-phase11.py`, missing build-inventory fixture, or a broader validator stack than the dedicated `scripts/zigux/check-phase11-hvc-survey-packet.py` archival route plus the shipped `check-phase11-shared-replay-contract.py` and `check-phase11-header-boundary-packet.py` routes on `master`?",
]
REQUIRED_BUILD_MARKERS = [
    '.name = "phase11-gpio-wdt-tests"',
    '.name = "phase11-bcm2835-wdt-tests"',
    '.name = "phase11-dw-wdt-tests"',
    '.name = "phase11-hvc-console-tests"',
    '.name = "phase11-hvc-cleanup-tests"',
    '.name = "phase11-uapi-header-parity-survey-tests"',
    'const test_step = b.step("test", "Run the shared Phase 11 starter packet");',
    "test_step.dependOn(&run_phase11_gpio_wdt_tests.step);",
    'const hvc_console_survey_step = b.step("hvc-console-survey", "Run the dedicated Phase 11 hvc_console archival survey");',
    "hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
]
REQUIRED_MAKEFILE_MARKERS = [
    "PHONY += phase11-contract phase11-test phase11-hvc-survey phase11",
    "phase11-contract:",
    "$(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py",
    "phase11: phase11-contract phase11-test phase11-hvc-survey",
]
REQUIRED_WORKFLOW_MARKERS = [
    "Self-test Phase 11 shared replay contract checker",
    "python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test",
    "Run Phase 11 shared replay contract checker",
    "make -C zigux phase11-contract",
]
EXACT_COUNT_MARKERS = [
    (
        DOCS_README_PATH,
        "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
        1,
        "docs_readme_lane_owner_map",
    ),
    (
        TESTS_README_PATH,
        "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
        1,
        "tests_readme_lane_owner_map",
    ),
    (
        REVIEW_CHECKLIST_PATH,
        "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
        1,
        "review_checklist_lane_owner_map",
    ),
    (
        BUILD_PATH,
        "test_step.dependOn(",
        13,
        "phase11_build_shared_depend_count",
    ),
    (
        BUILD_PATH,
        "hvc_console_survey_step.dependOn(",
        1,
        "phase11_build_dedicated_depend_count",
    ),
]
FORBIDDEN_CONTRACT_MARKERS = [
    "there is no dedicated shared `validate-phase11.py` or `phase11-validate` packet on current `master`",
    "the shipped checker only keeps the shared-versus-dedicated replay contract fail-closed",
]

PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT = 85

TARGETS = [
    (PHASE11_CONTRACT_PATH, REQUIRED_CONTRACT_MARKERS, "phase11_contract"),
    (DRIVER_LANE_SEQUENCING_PATH, REQUIRED_DRIVER_LANE_SEQUENCING_MARKERS, "driver_lane_sequencing"),
    (BCM2835_WDT_MATRIX_PATH, REQUIRED_BCM2835_WDT_MATRIX_MARKERS, "bcm2835_wdt_matrix"),
    (GPIO_WDT_MATRIX_PATH, REQUIRED_GPIO_WDT_MATRIX_MARKERS, "gpio_wdt_matrix"),
    (DW_WDT_MATRIX_PATH, REQUIRED_DW_WDT_MATRIX_MARKERS, "dw_wdt_matrix"),
    (HVC_CONSOLE_MATRIX_PATH, REQUIRED_HVC_CONSOLE_MATRIX_MARKERS, "hvc_console_matrix"),
    (DOCS_README_PATH, REQUIRED_DOCS_README_MARKERS, "docs_readme"),
    (SCRIPTS_README_PATH, REQUIRED_SCRIPT_README_MARKERS, "scripts_readme"),
    (TESTS_README_PATH, REQUIRED_TESTS_README_MARKERS, "tests_readme"),
    (REVIEW_CHECKLIST_PATH, REQUIRED_REVIEW_CHECKLIST_MARKERS, "review_checklist"),
    (BUILD_PATH, REQUIRED_BUILD_MARKERS, "phase11_build"),
    (MAKEFILE_PATH, REQUIRED_MAKEFILE_MARKERS, "makefile"),
    (WORKFLOW_PATH, REQUIRED_WORKFLOW_MARKERS, "workflow"),
]

SELF_TEST_CASES = [
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[10], REQUIRED_CONTRACT_MARKERS[10]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[7], REQUIRED_CONTRACT_MARKERS[7]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[11], REQUIRED_CONTRACT_MARKERS[11]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[12], REQUIRED_CONTRACT_MARKERS[12]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[13], REQUIRED_CONTRACT_MARKERS[13]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[14], REQUIRED_CONTRACT_MARKERS[14]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[20], REQUIRED_CONTRACT_MARKERS[20]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[22], REQUIRED_CONTRACT_MARKERS[22]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[23], REQUIRED_CONTRACT_MARKERS[23]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[24], REQUIRED_CONTRACT_MARKERS[24]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[25], REQUIRED_CONTRACT_MARKERS[25]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[-1], REQUIRED_CONTRACT_MARKERS[-1]),
    (DRIVER_LANE_SEQUENCING_PATH, "driver_lane_sequencing", REQUIRED_DRIVER_LANE_SEQUENCING_MARKERS[0], REQUIRED_DRIVER_LANE_SEQUENCING_MARKERS[0]),
    (DRIVER_LANE_SEQUENCING_PATH, "driver_lane_sequencing", REQUIRED_DRIVER_LANE_SEQUENCING_MARKERS[2], REQUIRED_DRIVER_LANE_SEQUENCING_MARKERS[2]),
    (DOCS_README_PATH, "docs_readme", "`scripts/zigux/check-phase11-header-boundary-packet.py`, ", REQUIRED_DOCS_README_MARKERS[13]),
    (DOCS_README_PATH, "docs_readme", REQUIRED_DOCS_README_MARKERS[2], REQUIRED_DOCS_README_MARKERS[2]),
    (DOCS_README_PATH, "docs_readme", REQUIRED_DOCS_README_MARKERS[3], REQUIRED_DOCS_README_MARKERS[3]),
    (DOCS_README_PATH, "docs_readme", REQUIRED_DOCS_README_MARKERS[4], REQUIRED_DOCS_README_MARKERS[4]),
    (DOCS_README_PATH, "docs_readme", REQUIRED_DOCS_README_MARKERS[5], REQUIRED_DOCS_README_MARKERS[5]),
    (DOCS_README_PATH, "docs_readme", REQUIRED_DOCS_README_MARKERS[6], REQUIRED_DOCS_README_MARKERS[6]),
    (DOCS_README_PATH, "docs_readme", REQUIRED_DOCS_README_MARKERS[7], REQUIRED_DOCS_README_MARKERS[7]),
    (DOCS_README_PATH, "docs_readme", REQUIRED_DOCS_README_MARKERS[8], REQUIRED_DOCS_README_MARKERS[8]),
    (DOCS_README_PATH, "docs_readme", REQUIRED_DOCS_README_MARKERS[9], REQUIRED_DOCS_README_MARKERS[9]),
    (DOCS_README_PATH, "docs_readme", REQUIRED_DOCS_README_MARKERS[10], REQUIRED_DOCS_README_MARKERS[10]),
    (DOCS_README_PATH, "docs_readme", REQUIRED_DOCS_README_MARKERS[11], REQUIRED_DOCS_README_MARKERS[11]),
    (DOCS_README_PATH, "docs_readme", REQUIRED_DOCS_README_MARKERS[12], REQUIRED_DOCS_README_MARKERS[12]),
    (DOCS_README_PATH, "docs_readme", REQUIRED_DOCS_README_MARKERS[13], REQUIRED_DOCS_README_MARKERS[13]),
    (DOCS_README_PATH, "docs_readme", REQUIRED_DOCS_README_MARKERS[14], REQUIRED_DOCS_README_MARKERS[14]),
    (SCRIPTS_README_PATH, "scripts_readme", REQUIRED_SCRIPT_README_MARKERS[1], REQUIRED_SCRIPT_README_MARKERS[1]),
]

FORBIDDEN_SELF_TEST_CASES = [
    (PHASE11_CONTRACT_PATH, FORBIDDEN_CONTRACT_MARKERS[0]),
    (PHASE11_CONTRACT_PATH, FORBIDDEN_CONTRACT_MARKERS[1]),
    (SCRIPTS_README_PATH, FORBIDDEN_CONTRACT_MARKERS[0]),
    (SCRIPTS_README_PATH, FORBIDDEN_CONTRACT_MARKERS[1]),
]

BUILD_FIXTURE_LINES = [
    '.name = "phase11-gpio-wdt-tests"',
    '.name = "phase11-bcm2835-wdt-tests"',
    '.name = "phase11-dw-wdt-tests"',
    '.name = "phase11-hvc-console-tests"',
    '.name = "phase11-hvc-cleanup-tests"',
    '.name = "phase11-uapi-header-parity-survey-tests"',
    'const test_step = b.step("test", "Run the shared Phase 11 starter packet");',
    "test_step.dependOn(&run_phase11_gpio_wdt_tests.step);",
    "test_step.dependOn(&run_shared_02.step);",
    "test_step.dependOn(&run_shared_03.step);",
    "test_step.dependOn(&run_shared_04.step);",
    "test_step.dependOn(&run_shared_05.step);",
    "test_step.dependOn(&run_shared_06.step);",
    "test_step.dependOn(&run_shared_07.step);",
    "test_step.dependOn(&run_shared_08.step);",
    "test_step.dependOn(&run_shared_09.step);",
    "test_step.dependOn(&run_shared_10.step);",
    "test_step.dependOn(&run_shared_11.step);",
    "test_step.dependOn(&run_shared_12.step);",
    "test_step.dependOn(&run_shared_13.step);",
    'const hvc_console_survey_step = b.step("hvc-console-survey", "Run the dedicated Phase 11 hvc_console archival survey");',
    "hvc_console_survey_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
]

FIXTURE_CONTENT = {
    PHASE11_CONTRACT_PATH: "\n".join(REQUIRED_CONTRACT_MARKERS) + "\n",
    DRIVER_LANE_SEQUENCING_PATH: "\n".join(REQUIRED_DRIVER_LANE_SEQUENCING_MARKERS) + "\n",
    BCM2835_WDT_MATRIX_PATH: "\n".join(REQUIRED_BCM2835_WDT_MATRIX_MARKERS) + "\n",
    GPIO_WDT_MATRIX_PATH: "\n".join(REQUIRED_GPIO_WDT_MATRIX_MARKERS) + "\n",
    DW_WDT_MATRIX_PATH: "\n".join(REQUIRED_DW_WDT_MATRIX_MARKERS) + "\n",
    HVC_CONSOLE_MATRIX_PATH: "\n".join(REQUIRED_HVC_CONSOLE_MATRIX_MARKERS) + "\n",
    DOCS_README_PATH: "\n".join(REQUIRED_DOCS_README_MARKERS) + "\n",
    SCRIPTS_README_PATH: "\n".join(REQUIRED_SCRIPT_README_MARKERS) + "\n",
    TESTS_README_PATH: "\n".join(REQUIRED_TESTS_README_MARKERS) + "\n",
    REVIEW_CHECKLIST_PATH: "\n".join(REQUIRED_REVIEW_CHECKLIST_MARKERS) + "\n",
    BUILD_PATH: "\n".join(BUILD_FIXTURE_LINES) + "\n",
    MAKEFILE_PATH: "\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n",
    WORKFLOW_PATH: "\n".join(REQUIRED_WORKFLOW_MARKERS) + "\n",
}

def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")

def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path, markers, label in TARGETS:
        path = root / rel_path
        if not path.exists():
            failures.append(f"missing_file:{rel_path}")
            continue
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"{label}:{marker}")
    if failures:
        return failures
    for rel_path, marker, expected_count, label in EXACT_COUNT_MARKERS:
        count = read_text(root, rel_path).count(marker)
        if count != expected_count:
            failures.append(f"exact_count:{label}:{expected_count}:{count}:{marker}")
    if failures:
        return failures
    phase11_contract = read_text(root, PHASE11_CONTRACT_PATH)
    scripts_readme = read_text(root, SCRIPTS_README_PATH)
    for marker in FORBIDDEN_CONTRACT_MARKERS:
        if marker in phase11_contract or marker in scripts_readme:
            failures.append(f"forbidden_marker:{marker}")
    return failures

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel_path, content in FIXTURE_CONTENT.items():
        write(root / rel_path, content)

def expect_failure(root: Path, rel_path: str, label: str, marker: str, expected_marker: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    if marker not in original:
        raise AssertionError(f"self-test marker {marker!r} not found in {rel_path}")
    mutated = original.replace(marker, "", 1)
    path.write_text(mutated, encoding="utf-8")
    failures = validate(root)
    expected_failure = f"{label}:{expected_marker}"
    if expected_failure not in failures:
        raise AssertionError(f"missing expected failure {expected_failure!r}; got {failures!r}")

def expect_exact_count_failure(root: Path, rel_path: str, marker: str, label: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original + marker + "\n", encoding="utf-8")
    failures = validate(root)
    expected_prefix = f"exact_count:{label}:"
    if not any(failure.startswith(expected_prefix) for failure in failures):
        raise AssertionError(f"missing expected exact-count failure {expected_prefix!r}; got {failures!r}")

def expect_forbidden_failure(root: Path, rel_path: str, marker: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original + marker + "\n", encoding="utf-8")
    failures = validate(root)
    expected_failure = f"forbidden_marker:{marker}"
    if expected_failure not in failures:
        raise AssertionError(f"missing expected forbidden-marker failure {expected_failure!r}; got {failures!r}")

def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase11_contract_") as tmpdir:
        root = Path(tmpdir)
        write_fixture_tree(root)
        failures = validate(root)
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            return 1
        for rel_path, label, marker, expected_marker in SELF_TEST_CASES:
            write_fixture_tree(root)
            try:
                expect_failure(root, rel_path, label, marker, expected_marker)
            except AssertionError as exc:
                print(exc, file=sys.stderr)
                return 1
        for rel_path, marker, _expected_count, label in EXACT_COUNT_MARKERS:
            write_fixture_tree(root)
            try:
                expect_exact_count_failure(root, rel_path, marker, label)
            except AssertionError as exc:
                print(exc, file=sys.stderr)
                return 1
        for rel_path, marker in FORBIDDEN_SELF_TEST_CASES:
            write_fixture_tree(root)
            try:
                expect_forbidden_failure(root, rel_path, marker)
            except AssertionError as exc:
                print(exc, file=sys.stderr)
                return 1
    print("PHASE11_SHARED_REPLAY_CONTRACT_SELFTEST=pass")
    print(f"PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT={PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT}")
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description="Check the shipped Phase 11 shared replay contract.")
    parser.add_argument("--self-test", action="store_true", help="exercise the checker against a synthetic fixture tree")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to validate")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print("PHASE11_SHARED_REPLAY_CONTRACT=pass")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
