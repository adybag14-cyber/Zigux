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
    "`zigux/tests/phase11_hvc_console_survey.zig`",
    "`make -C zigux phase11-hvc-survey`",
    "`zigux/tests/phase11_uapi_header_parity_manifest.json`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`drivers/watchdog/dw_wdt_verify.zig`",
    "The shipped DesignWare watchdog sub-packet inside that shared route stays explicit as `phase11-dw-wdt-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests`.",
    "`drivers/tty/hvc/hvc_console_verify.zig`",
    "the dedicated `scripts/zigux/check-phase11-hvc-survey-packet.py` route",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`zig build test --build-file zigux/tests/phase11_build.zig --summary all`",
    "`make -C zigux phase11`",
    "there is no dedicated shared `validate-phase11.py` on `master`",
    "there is no shipped `zigux/tests/fixtures/phase11_build_inventory.json` on `master`",
    "there is no broader multi-checker Phase 11 validator stack on `master`",
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
    "`phase11-dw-wdt-tests`, `phase11-dw-wdt-verify-tests`, and `phase11-dw-wdt-survey-tests` remain the shared Phase 11 artifacts that cover this DesignWare packet",
    "keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_survey.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_build.zig`, and `zigux/Makefile` aligned so this matrix does not drift away from the shipped shared Phase 11 replay route or the focused shared header-boundary packet",
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
    "`scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` now keep the shared-versus-dedicated Phase 11 packet honest: the shipped contract checker plus the focused header-boundary checker, the shared build-and-make packet, the dedicated `hvc_console` survey note and replay, the bounded `hvc_cleanup()` handoff, the focused shared header-boundary note and manifest-backed survey replay, and the four driver-local validation matrices all remain reviewable without implying a removed `validate-phase11.py`, a missing build inventory, or a broader checker-script packet than the dedicated `scripts/zigux/check-phase11-hvc-survey-packet.py` archival route plus the shipped `check-phase11-shared-replay-contract.py` and `check-phase11-header-boundary-packet.py` routes on `master`.",
]
REQUIRED_SCRIPT_README_MARKERS = [
    "Phase 11 flow",
    "- the current shared Phase 11 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
    "`scripts/zigux/check-phase11-shared-replay-contract.py`",
    "`python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test` and `check-phase11-shared-replay-contract.py` keep the docs-root summary, scripts-root, replay-contract note, Makefile, and workflow contract fail-closed while preserving the dedicated archival survey split.",
    "there is no dedicated shared `validate-phase11.py`, `zigux/tests/fixtures/phase11_build_inventory.json`, or `phase11-validate` target on `master`",
]
REQUIRED_TESTS_README_MARKERS = [
    "keep the shared-versus-dedicated Phase 11 simple-driver packet explicit in the tests root too:",
    "`Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `zig build test --build-file zigux/tests/phase11_build.zig`, and `make -C zigux phase11` should continue to keep the shipped shared replay route, the focused shared header-boundary packet, the dedicated `hvc_console` archival survey note and replay, the bounded `hvc_cleanup()` teardown handoff, and the four driver-local validation matrices reviewable from the tests root without implying a removed `validate-phase11.py`, a shipped `zigux/tests/fixtures/phase11_build_inventory.json`, or a broader checker-script packet than the dedicated `scripts/zigux/check-phase11-hvc-survey-packet.py` archival route plus the shipped `check-phase11-shared-replay-contract.py` and `check-phase11-header-boundary-packet.py` routes on `master`",
]
REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "* if the change touches the shared Phase 11 simple-driver packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, `zigux/tests/README.md`, `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-uapi-header-parity-survey.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_uapi_header_parity_manifest.json`, `zigux/tests/phase11_uapi_header_parity_survey.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `zig build test --build-file zigux/tests/phase11_build.zig`, `make -C zigux phase11`, and `make -C zigux phase11-hvc-survey` still agree on the same shared-versus-dedicated replay split, the focused header-boundary note plus manifest-backed survey packet, the four driver-local validation matrices, the bounded `hvc_cleanup()` teardown handoff, and the dedicated archival `hvc_console` survey plus checker-backed replay route without implying a removed `validate-phase11.py`, missing build-inventory fixture, or a broader validator stack than the dedicated `scripts/zigux/check-phase11-hvc-survey-packet.py` archival route plus the shipped `check-phase11-shared-replay-contract.py` and `check-phase11-header-boundary-packet.py` routes on `master`?",
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
]
FORBIDDEN_CONTRACT_MARKERS = [
    "there is no dedicated shared `validate-phase11.py` or `phase11-validate` packet on current `master`",
    "the shipped checker only keeps the shared-versus-dedicated replay contract fail-closed",
]

PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT = 36

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
    (MAKEFILE_PATH, REQUIRED_MAKEFILE_MARKERS, "makefile"),
    (WORKFLOW_PATH, REQUIRED_WORKFLOW_MARKERS, "workflow"),
]

SELF_TEST_CASES = [
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[10], REQUIRED_CONTRACT_MARKERS[10]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[7], REQUIRED_CONTRACT_MARKERS[7]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[11], REQUIRED_CONTRACT_MARKERS[11]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[12], REQUIRED_CONTRACT_MARKERS[12]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[14], REQUIRED_CONTRACT_MARKERS[14]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[15], REQUIRED_CONTRACT_MARKERS[15]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[20], REQUIRED_CONTRACT_MARKERS[20]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[22], REQUIRED_CONTRACT_MARKERS[22]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", REQUIRED_CONTRACT_MARKERS[23], REQUIRED_CONTRACT_MARKERS[23]),
    (DRIVER_LANE_SEQUENCING_PATH, "driver_lane_sequencing", REQUIRED_DRIVER_LANE_SEQUENCING_MARKERS[0], REQUIRED_DRIVER_LANE_SEQUENCING_MARKERS[0]),
    (DRIVER_LANE_SEQUENCING_PATH, "driver_lane_sequencing", REQUIRED_DRIVER_LANE_SEQUENCING_MARKERS[2], REQUIRED_DRIVER_LANE_SEQUENCING_MARKERS[2]),
    (DOCS_README_PATH, "docs_readme", "`scripts/zigux/check-phase11-header-boundary-packet.py`, ", REQUIRED_DOCS_README_MARKERS[2]),
    (SCRIPTS_README_PATH, "scripts_readme", "`scripts/zigux/check-phase11-header-boundary-packet.py`, ", REQUIRED_SCRIPT_README_MARKERS[1]),
    (TESTS_README_PATH, "tests_readme", "`scripts/zigux/check-phase11-header-boundary-packet.py`, ", REQUIRED_TESTS_README_MARKERS[1]),
    (TESTS_README_PATH, "tests_readme", "`Documentation/zigux/phase11-driver-lane-sequencing.md`, ", REQUIRED_TESTS_README_MARKERS[1]),
    (REVIEW_CHECKLIST_PATH, "review_checklist", "`Documentation/zigux/phase11-driver-lane-sequencing.md`, ", REQUIRED_REVIEW_CHECKLIST_MARKERS[0]),
    (REVIEW_CHECKLIST_PATH, "review_checklist", "`scripts/zigux/check-phase11-header-boundary-packet.py`, ", REQUIRED_REVIEW_CHECKLIST_MARKERS[0]),
    (REVIEW_CHECKLIST_PATH, "review_checklist", "`zigux/tests/phase11_hvc_console_manifest.json`, ", REQUIRED_REVIEW_CHECKLIST_MARKERS[0]),
    (REVIEW_CHECKLIST_PATH, "review_checklist", "`make -C zigux phase11-hvc-survey`", REQUIRED_REVIEW_CHECKLIST_MARKERS[0]),
    (REVIEW_CHECKLIST_PATH, "review_checklist", "the dedicated archival `hvc_console` survey plus checker-backed replay route", REQUIRED_REVIEW_CHECKLIST_MARKERS[0]),
    (MAKEFILE_PATH, "makefile", REQUIRED_MAKEFILE_MARKERS[2], REQUIRED_MAKEFILE_MARKERS[2]),
    (WORKFLOW_PATH, "workflow", REQUIRED_WORKFLOW_MARKERS[1], REQUIRED_WORKFLOW_MARKERS[1]),
    (GPIO_WDT_MATRIX_PATH, "gpio_wdt_matrix", REQUIRED_GPIO_WDT_MATRIX_MARKERS[3], REQUIRED_GPIO_WDT_MATRIX_MARKERS[3]),
    (GPIO_WDT_MATRIX_PATH, "gpio_wdt_matrix", "`zigux/tests/phase11_gpio_wdt_manifest.json`", REQUIRED_GPIO_WDT_MATRIX_MARKERS[4]),
    (BCM2835_WDT_MATRIX_PATH, "bcm2835_wdt_matrix", REQUIRED_BCM2835_WDT_MATRIX_MARKERS[4], REQUIRED_BCM2835_WDT_MATRIX_MARKERS[4]),
    (DW_WDT_MATRIX_PATH, "dw_wdt_matrix", REQUIRED_DW_WDT_MATRIX_MARKERS[4], REQUIRED_DW_WDT_MATRIX_MARKERS[4]),
    (DW_WDT_MATRIX_PATH, "dw_wdt_matrix", "`zigux/tests/phase11_dw_wdt_manifest.json`", REQUIRED_DW_WDT_MATRIX_MARKERS[5]),
    (HVC_CONSOLE_MATRIX_PATH, "hvc_console_matrix", REQUIRED_HVC_CONSOLE_MATRIX_MARKERS[3], REQUIRED_HVC_CONSOLE_MATRIX_MARKERS[3]),
    (HVC_CONSOLE_MATRIX_PATH, "hvc_console_matrix", REQUIRED_HVC_CONSOLE_MATRIX_MARKERS[4], REQUIRED_HVC_CONSOLE_MATRIX_MARKERS[4]),
    (HVC_CONSOLE_MATRIX_PATH, "hvc_console_matrix", REQUIRED_HVC_CONSOLE_MATRIX_MARKERS[5], REQUIRED_HVC_CONSOLE_MATRIX_MARKERS[5]),
    (HVC_CONSOLE_MATRIX_PATH, "hvc_console_matrix", "compile-local `hvc_console_verify` replay stay explicit inside the wider Phase 11 packet", REQUIRED_HVC_CONSOLE_MATRIX_MARKERS[6]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", "`scripts/zigux/check-phase11-hvc-survey-packet.py`", REQUIRED_CONTRACT_MARKERS[10]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", "`zigux/tests/phase11_hvc_console_manifest.json`", REQUIRED_CONTRACT_MARKERS[12]),
    (PHASE11_CONTRACT_PATH, "phase11_contract", "`make -C zigux phase11-hvc-survey`", REQUIRED_CONTRACT_MARKERS[14]),
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
    path.write_text(original.replace(marker, "", 1), encoding="utf-8")
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
