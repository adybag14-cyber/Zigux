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
    "`scripts/zigux/check-phase11-shared-replay-contract.py`",
    "`scripts/zigux/check-phase11-header-boundary-packet.py`",
    "- `scripts/zigux/check-phase11-hvc-survey-packet.py`\n- `zigux/tests/phase11_build.zig`",
    "`zigux/tests/phase11_hvc_cleanup.zig`",
    "`zigux/tests/phase11_hvc_console_survey.zig`",
    "`zigux/tests/phase11_uapi_header_parity_manifest.json`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`drivers/watchdog/dw_wdt_verify.zig`",
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

PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT = 13


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in [
        PHASE11_CONTRACT_PATH,
        BCM2835_WDT_MATRIX_PATH,
        GPIO_WDT_MATRIX_PATH,
        DW_WDT_MATRIX_PATH,
        HVC_CONSOLE_MATRIX_PATH,
        DOCS_README_PATH,
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
        REVIEW_CHECKLIST_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
    ]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    if failures:
        return failures

    phase11_contract = read_text(root, PHASE11_CONTRACT_PATH)
    bcm2835_wdt_matrix = read_text(root, BCM2835_WDT_MATRIX_PATH)
    gpio_wdt_matrix = read_text(root, GPIO_WDT_MATRIX_PATH)
    dw_wdt_matrix = read_text(root, DW_WDT_MATRIX_PATH)
    hvc_console_matrix = read_text(root, HVC_CONSOLE_MATRIX_PATH)
    docs_readme = read_text(root, DOCS_README_PATH)
    scripts_readme = read_text(root, SCRIPTS_README_PATH)
    tests_readme = read_text(root, TESTS_README_PATH)
    review_checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)
    for marker in REQUIRED_CONTRACT_MARKERS:
        if marker not in phase11_contract:
            failures.append(f"phase11_contract:{marker}")
    for marker in REQUIRED_BCM2835_WDT_MATRIX_MARKERS:
        if marker not in bcm2835_wdt_matrix:
            failures.append(f"bcm2835_wdt_matrix:{marker}")
    for marker in REQUIRED_GPIO_WDT_MATRIX_MARKERS:
        if marker not in gpio_wdt_matrix:
            failures.append(f"gpio_wdt_matrix:{marker}")
    for marker in REQUIRED_DW_WDT_MATRIX_MARKERS:
        if marker not in dw_wdt_matrix:
            failures.append(f"dw_wdt_matrix:{marker}")
    for marker in REQUIRED_HVC_CONSOLE_MATRIX_MARKERS:
        if marker not in hvc_console_matrix:
            failures.append(f"hvc_console_matrix:{marker}")
    for marker in REQUIRED_DOCS_README_MARKERS:
        if marker not in docs_readme:
            failures.append(f"docs_readme:{marker}")
    for marker in REQUIRED_SCRIPT_README_MARKERS:
        if marker not in scripts_readme:
            failures.append(f"scripts_readme:{marker}")
    for marker in REQUIRED_TESTS_README_MARKERS:
        if marker not in tests_readme:
            failures.append(f"tests_readme:{marker}")
    for marker in REQUIRED_REVIEW_CHECKLIST_MARKERS:
        if marker not in review_checklist:
            failures.append(f"review_checklist:{marker}")
    for marker in REQUIRED_MAKEFILE_MARKERS:
        if marker not in makefile:
            failures.append(f"makefile:{marker}")
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if marker not in workflow:
            failures.append(f"workflow:{marker}")
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

    write(
        root / PHASE11_CONTRACT_PATH,
        """# Phase 11 Shared Replay Contract

## Current Shared Review Surface On `master`
- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`
- `Documentation/zigux/phase11-uapi-header-parity-survey.md`
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `scripts/zigux/check-phase11-header-boundary-packet.py`
- `scripts/zigux/check-phase11-hvc-survey-packet.py`
- `zigux/tests/phase11_build.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`
- `zigux/tests/phase11_hvc_console_survey.zig`
- `zigux/tests/phase11_uapi_header_parity_manifest.json`
- `drivers/watchdog/bcm2835_wdt_verify.zig`
- `drivers/watchdog/dw_wdt_verify.zig`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/Makefile`

## Shared Replay Commands
- `zig build test --build-file zigux/tests/phase11_build.zig --summary all`
- `make -C zigux phase11`

## What This Contract Does Not Claim
- there is no shared `make -C zigux phase11-validate` target on `master`
- there is no dedicated shared `validate-phase11.py` on `master`
- there is no shipped `zigux/tests/fixtures/phase11_build_inventory.json` on `master`
- beyond the focused `scripts/zigux/check-phase11-header-boundary-packet.py` route and its coupled manifest, survey note, and survey replay, there is no broader multi-checker Phase 11 validator stack on `master`
""",
    )
    write(
        root / DOCS_README_PATH,
        """# Documentation/zigux

Phase 11 notes
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-survey.md`
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` now keep the shared-versus-dedicated Phase 11 packet honest: the shipped contract checker plus the focused header-boundary checker, the shared build-and-make packet, the dedicated `hvc_console` survey note and replay, the bounded `hvc_cleanup()` handoff, the focused shared header-boundary note and manifest-backed survey replay, and the four driver-local validation matrices all remain reviewable without implying a removed `validate-phase11.py`, a missing build inventory, or a broader validator stack than the shipped `check-phase11-shared-replay-contract.py` plus `check-phase11-header-boundary-packet.py` routes on `master`.
""",
    )
    write(
        root / BCM2835_WDT_MATRIX_PATH,
        """# Phase 11 BCM2835 Watchdog Validation Matrix

## Status
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `drivers/watchdog/bcm2835_wdt_verify.zig`

## Shared Replay Surface
- `phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests` remain the shared Phase 11 artifacts that cover this bcm2835 packet

## Review Rules
- keep `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from either the shipped shared replay route or the dedicated bcm2835 archival packet
""",
    )
    write(
        root / GPIO_WDT_MATRIX_PATH,
        """# Phase 11 GPIO Watchdog Validation Matrix

## Status
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `drivers/watchdog/gpio_wdt.zig`

## Review Rules
- keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from the shipped shared Phase 11 replay route or the focused shared header-boundary packet
""",
    )
    write(
        root / DW_WDT_MATRIX_PATH,
        """# Phase 11 DesignWare Watchdog Validation Matrix

## Status
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `drivers/watchdog/dw_wdt_verify.zig`

## Shared Replay Surface
- `phase11-dw-wdt-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests` remain the shared Phase 11 artifacts that cover this DesignWare packet

## Review Rules
- keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from the shipped shared Phase 11 replay route or the focused shared header-boundary packet
""",
    )
    write(
        root / HVC_CONSOLE_MATRIX_PATH,
        """# Phase 11 HVC Console Validation Matrix

## Status
- `Documentation/zigux/phase11-shared-replay-contract.md`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `drivers/tty/hvc/hvc_console_verify.zig`
- `zigux/tests/phase11_hvc_cleanup.zig`
- `Documentation/zigux/phase11-hvc-console-teardown-note.md`

## Review Rules
- keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned with this matrix whenever the shared-versus-dedicated HVC replay split changes so the dedicated `hvc_cleanup()` teardown replay and the compile-local `hvc_console_verify` replay stay explicit inside the wider Phase 11 packet, the focused shared header-boundary packet stays visible beside them, and the dedicated archival `phase11-hvc-survey` route keeps failing closed
""",
    )
    write(
        root / SCRIPTS_README_PATH,
        """# scripts/zigux

Phase 11 flow
- the current shared Phase 11 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.
- `python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test` and `check-phase11-shared-replay-contract.py` keep the docs-root summary, scripts-root, replay-contract note, Makefile, and workflow contract fail-closed while preserving the dedicated archival survey split.
- `zig build test --build-file zigux/tests/phase11_build.zig --summary all` and `make -C zigux phase11` rerun that same simple-driver starter packet, while `zigux/tests/phase11_hvc_cleanup.zig` keeps the bounded `hvc_cleanup()` tty-port release handoff and teardown-gating replay explicit and the dedicated `zigux/tests/phase11_hvc_console_survey.zig` archival replay stays separate.
- there is no dedicated shared `validate-phase11.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, or `phase11-validate` target on `master`; the shipped Phase 11 checker is intentionally narrower than a broader validator packet.
""",
    )
    write(
        root / TESTS_README_PATH,
        """# zigux/tests

- keep the shared-versus-dedicated Phase 11 simple-driver packet explicit in the tests root too: `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `zig build test --build-file zigux/tests/phase11_build.zig`, and `make -C zigux phase11` should continue to keep the shipped shared replay route, the focused shared header-boundary packet, the dedicated `hvc_console` archival survey note and replay, the bounded `hvc_cleanup()` teardown handoff, and the four driver-local validation matrices reviewable from the tests root without implying a removed `validate-phase11.py`, a shipped `zigux/tests/fixtures/phase11_build_inventory.json`, or a broader checker-script packet that does not exist on `master`
""",
    )
    write(
        root / REVIEW_CHECKLIST_PATH,
        """# Zigux Review Checklist

* if the change touches the shared Phase 11 simple-driver packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `zig build test --build-file zigux/tests/phase11_build.zig`, and `make -C zigux phase11` still agree on the same shared-versus-dedicated replay split, the focused header-boundary note plus manifest-backed survey packet, the four driver-local validation matrices, the bounded `hvc_cleanup()` teardown handoff, and the dedicated archival `hvc_console` survey without implying a removed `validate-phase11.py`, missing build-inventory fixture, or a broader validator stack than the shipped `check-phase11-shared-replay-contract.py` plus `check-phase11-header-boundary-packet.py` routes on `master`?",
""",
    )
    write(
        root / MAKEFILE_PATH,
        """PHONY += phase11-contract phase11-test phase11-hvc-survey phase11

PYTHON ?= python3
ZIG ?= zig
ZIGUX_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

phase11-contract:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-shared-replay-contract.py

phase11-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_build.zig --summary all

phase11-hvc-survey:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase11-hvc-survey-packet.py
	cd $(ZIGUX_ROOT) && $(ZIG) build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all

phase11: phase11-contract phase11-test phase11-hvc-survey
""",
    )
    write(
        root / WORKFLOW_PATH,
        """name: zigux-bootstrap

jobs:
  bootstrap:
    runs-on: ubuntu-latest
    steps:
      - name: Self-test Phase 11 shared replay contract checker
        run: python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test

      - name: Run Phase 11 shared replay contract checker
        run: make -C zigux phase11-contract
""",
    )


def expect_failure(root: Path, rel_path: str, marker: str, expected_failure: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(marker, "", 1), encoding="utf-8")
    failures = validate(root)
    if expected_failure not in failures:
        raise AssertionError(f"missing expected failure {expected_failure!r}; got {failures!r}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase11_contract_", dir=None) as tmpdir:
        root = Path(tmpdir)

        write_fixture_tree(root)
        failures = validate(root)
        if failures:
            for failure in failures:
                print(failure, file=sys.stderr)
            return 1

        cases = [
            (
                PHASE11_CONTRACT_PATH,
                "- `scripts/zigux/check-phase11-hvc-survey-packet.py`\n",
                "phase11_contract:- `scripts/zigux/check-phase11-hvc-survey-packet.py`\n- `zigux/tests/phase11_build.zig`",
            ),
            (
                PHASE11_CONTRACT_PATH,
                "- `zigux/tests/phase11_hvc_cleanup.zig`\n",
                "phase11_contract:`zigux/tests/phase11_hvc_cleanup.zig`",
            ),
            (
                PHASE11_CONTRACT_PATH,
                "- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`\n",
                "phase11_contract:`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
            ),
            (
                PHASE11_CONTRACT_PATH,
                "- `Documentation/zigux/phase11-hvc-console-teardown-note.md`\n",
                "phase11_contract:`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
            ),
            (
                PHASE11_CONTRACT_PATH,
                "- `drivers/watchdog/dw_wdt_verify.zig`\n",
                "phase11_contract:`drivers/watchdog/dw_wdt_verify.zig`",
            ),
            (
                SCRIPTS_README_PATH,
                "`scripts/zigux/check-phase11-header-boundary-packet.py`, ",
                "scripts_readme:- the current shared Phase 11 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
            ),
            (
                REVIEW_CHECKLIST_PATH,
                "`scripts/zigux/check-phase11-header-boundary-packet.py`, ",
                "review_checklist:* if the change touches the shared Phase 11 simple-driver packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `zig build test --build-file zigux/tests/phase11_build.zig`, and `make -C zigux phase11` still agree on the same shared-versus-dedicated replay split, the focused header-boundary note plus manifest-backed survey packet, the four driver-local validation matrices, the bounded `hvc_cleanup()` teardown handoff, and the dedicated archival `hvc_console` survey without implying a removed `validate-phase11.py`, missing build-inventory fixture, or a broader validator stack than the shipped `check-phase11-shared-replay-contract.py` plus `check-phase11-header-boundary-packet.py` routes on `master`?",
            ),
            (
                GPIO_WDT_MATRIX_PATH,
                "`drivers/watchdog/gpio_wdt.zig`\n",
                "gpio_wdt_matrix:`drivers/watchdog/gpio_wdt.zig`",
            ),
            (
                BCM2835_WDT_MATRIX_PATH,
                "`phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests` remain the shared Phase 11 artifacts that cover this bcm2835 packet\n",
                "bcm2835_wdt_matrix:`phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests` remain the shared Phase 11 artifacts that cover this bcm2835 packet",
            ),
            (
                DW_WDT_MATRIX_PATH,
                "`phase11-dw-wdt-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests` remain the shared Phase 11 artifacts that cover this DesignWare packet\n",
                "dw_wdt_matrix:`phase11-dw-wdt-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests` remain the shared Phase 11 artifacts that cover this DesignWare packet",
            ),
            (
                HVC_CONSOLE_MATRIX_PATH,
                "`drivers/tty/hvc/hvc_console_verify.zig`\n",
                "hvc_console_matrix:`drivers/tty/hvc/hvc_console_verify.zig`",
            ),
            (
                HVC_CONSOLE_MATRIX_PATH,
                "`zigux/tests/phase11_hvc_cleanup.zig`\n",
                "hvc_console_matrix:`zigux/tests/phase11_hvc_cleanup.zig`",
            ),
            (
                HVC_CONSOLE_MATRIX_PATH,
                "`Documentation/zigux/phase11-hvc-console-teardown-note.md`\n",
                "hvc_console_matrix:`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
            ),
            (
                HVC_CONSOLE_MATRIX_PATH,
                "compile-local `hvc_console_verify` replay stay explicit inside the wider Phase 11 packet",
                "hvc_console_matrix:keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `scripts/zigux/check-phase11-hvc-survey-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` aligned with this matrix whenever the shared-versus-dedicated HVC replay split changes so the dedicated `hvc_cleanup()` teardown replay and the compile-local `hvc_console_verify` replay stay explicit inside the wider Phase 11 packet, the focused shared header-boundary packet stays visible beside them, and the dedicated archival `phase11-hvc-survey` route keeps failing closed",
            ),
        ]

        for rel_path, marker, expected_failure in cases:
            write_fixture_tree(root)
            try:
                expect_failure(root, rel_path, marker, expected_failure)
            except AssertionError as exc:
                print(str(exc), file=sys.stderr)
                return 1

    print("PHASE11_SHARED_REPLAY_CONTRACT_SELFTEST=pass")
    print(
        "PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT="
        f"{PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT}"
    )
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
