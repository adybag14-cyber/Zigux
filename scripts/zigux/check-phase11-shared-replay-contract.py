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
BCM2835_WDT_MATRIX_PATH = "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md"
GPIO_WDT_MATRIX_PATH = "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md"
DW_WDT_MATRIX_PATH = "Documentation/zigux/phase11-dw-wdt-validation-matrix.md"
HVC_CONSOLE_MATRIX_PATH = "Documentation/zigux/phase11-hvc-console-validation-matrix.md"
DOCS_README_PATH = "Documentation/zigux/README.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
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
    "`zigux/tests/phase11_hvc_console_survey.zig`",
    "`zigux/tests/phase11_uapi_header_parity_manifest.json`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`drivers/watchdog/dw_wdt_verify.zig`",
    "The shipped DesignWare watchdog sub-packet inside that shared route stays explicit as `phase11-dw-wdt-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`.",
    "`drivers/tty/hvc/hvc_console_verify.zig`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "there is no dedicated shared `validate-phase11.py` on `master`",
    "there is no shipped `zigux/tests/fixtures/phase11_build_inventory.json` on `master`",
    "there is no broader multi-checker Phase 11 validator stack on `master`",
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
    "keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from the shipped shared Phase 11 replay route or the focused shared header-boundary packet",
]

REQUIRED_DW_WDT_MATRIX_MARKERS = [
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`zigux/tests/README.md`",
    "`zigux/Makefile`",
    "`drivers/watchdog/dw_wdt_verify.zig`",
    "`phase11-dw-wdt-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests` remain the shared Phase 11 artifacts that cover this DesignWare packet",
    "keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from the shipped shared Phase 11 replay route or the focused shared header-boundary packet",
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
    "`scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` now keep the shared-versus-dedicated Phase 11 packet honest: the shipped contract checker plus the focused header-boundary checker, the shared build-and-make packet, the dedicated `hvc_console` survey note and replay, the bounded `hvc_cleanup()` handoff, the focused shared header-boundary note and manifest-backed survey replay, and the four driver-local validation matrices all remain reviewable without implying a removed `validate-phase11.py`, a missing build inventory, or a broader validator stack than the shipped `check-phase11-shared-replay-contract.py` plus `check-phase11-header-boundary-packet.py` routes on `master`.",
]

REQUIRED_SCRIPT_README_MARKERS = [
    "Phase 11 flow",
    "- the current shared Phase 11 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
    "`scripts/zigux/check-phase11-shared-replay-contract.py`",
    "`python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test` and `check-phase11-shared-replay-contract.py` keep the docs-root summary, scripts-root, replay-contract note, Makefile, and workflow contract fail-closed while preserving the dedicated archival survey split.",
    "there is no dedicated shared `validate-phase11.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, or `phase11-validate` target on `master`",
]

REQUIRED_TESTS_README_MARKERS = [
    "keep the shared-versus-dedicated Phase 11 simple-driver packet explicit in the tests root too:",
    "`Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `zig build test --build-file zigux/tests/phase11_build.zig`, and `make -C zigux phase11` should continue to keep the shipped shared replay route, the focused shared header-boundary packet, the dedicated `hvc_console` archival survey note and replay, the bounded `hvc_cleanup()` teardown handoff, and the four driver-local validation matrices reviewable from the tests root without implying a removed `validate-phase11.py`, a shipped `zigux/tests/fixtures/phase11_build_inventory.json`, or a broader checker-script packet that does not exist on `master`",
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "* if the change touches the shared Phase 11 simple-driver packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `zig build test --build-file zigux/tests/phase11_build.zig`, and `make -C zigux phase11` still agree on the same shared-versus-dedicated replay split, the focused header-boundary note plus manifest-backed survey packet, the four driver-local validation matrices, the bounded `hvc_cleanup()` teardown handoff, and the dedicated archival `hvc_console` survey without implying a removed `validate-phase11.py`, missing build-inventory fixture, or a broader validator stack than the shipped `check-phase11-shared-replay-contract.py` plus `check-phase11-header-boundary-packet.py` routes on `master`?",
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

FORBIDDEN_CONTRACT_MARKERS = [
    "there is no dedicated shared `validate-phase11.py` or `phase11-validate` packet on current `master`",
    "the shipped checker only keeps the shared-versus-dedicated replay contract fail-closed",
]

PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT = 19


def read_text(root: Path) -> str:
    return (root / rel_path).read_text(encoding="utf-8")
