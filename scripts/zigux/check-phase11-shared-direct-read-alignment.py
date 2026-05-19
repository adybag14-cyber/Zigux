#!/usr/bin/env python3
"""Fail-close guard for the shared Phase 11 direct-read reminder packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

DOCS_ROOT_PATH = Path("Documentation/zigux/README.md")
SEQUENCING_PATH = Path("Documentation/zigux/phase11-driver-lane-sequencing.md")
MATRIX_GAP_PATH = Path("Documentation/zigux/phase11-validation-matrix-gap-survey.md")
HVC_SURVEY_PATH = Path("Documentation/zigux/phase11-hvc-console-survey.md")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")

DOCS_ROOT_MARKERS = (
    "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
    "`Documentation/zigux/phase11-hvc-console-survey.md`",
    "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`scripts/zigux/check-phase11-matrix-gap-survey.py`",
    "`scripts/zigux/check-phase11-validation-matrix-gap-survey.py`",
    "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "`drivers/watchdog/dw_wdt.zig`",
    "`drivers/watchdog/dw_wdt_verify.zig`",
    "`drivers/tty/hvc/hvc_console.zig`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`zigux/tests/phase11_dw_wdt_manifest.json`",
    "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`Documentation/zigux/phase11-closure-note.md`",
    "`scripts/zigux/check-phase11-shared-replay-contract.py`",
    "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
    "`zigux/tests/phase11_build.zig`",
    "still exposes no dedicated `make -C zigux phase11`, `make -C zigux phase11-validate`, or `make -C zigux phase11-contract` routes",
)

SEQUENCING_MARKERS = (
    "shared sequencing lane `P11-Y06`",
    "DesignWare lane `P11-L10` currently owns the returned watchdog-local packet",
    "`drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`,",
    "`scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and",
    "`scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`",
    "HVC archival lane `P11-L16` currently keeps the directly readable",
    "`Documentation/zigux/phase11-hvc-console-survey.md`,",
    "`drivers/tty/hvc/hvc_console.zig`,",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md` authoritative",
    "current `master` still does not rematerialize the shared-validator surfaces `scripts/zigux/validate-phase11.py`",
)

MATRIX_GAP_MARKERS = (
    "`PHASE11_MATRIX_GAP_STATUS=gpio_hvc_and_dw_matrices_direct_readback_only`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`",
    "`scripts/zigux/check-phase11-matrix-gap-survey.py`",
    "`scripts/zigux/check-phase11-validation-matrix-gap-survey.py`",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "Current direct contents reads in this run do not rematerialize",
    "The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared",
    "depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.",
)

HVC_SURVEY_MARKERS = (
    "`PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`",
    "current authenticated contents readback keeps the bounded HVC current-head",
    "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "Current-Head Packet",
    "keep the deeper verify helper, sysrq helper, focused survey replay, manifest,",
    "`zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey`",
)

EXPECTED_INVENTORY = {
    "build_test_names": [
        "phase11-hvc-hv-ops-layout-proof-tests",
        "phase11-hvc-export-surface-layout-proof-tests",
        "phase11-hvc-cleanup-packet-proof",
    ],
    "shared_test_depend_steps": [],
    "dedicated_survey_replays": [],
    "shared_adjunct_replays": [
        "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
        "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
        "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
    ],
}


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def require_markers(root: Path, rel: Path, label: str, markers: tuple[str, ...]) -> None:
    text = read_text(root / rel)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing {label} marker: {marker}")


def read_inventory(root: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(root / INVENTORY_PATH))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {INVENTORY_PATH}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckError(f"expected object in {INVENTORY_PATH}")
    return payload


def expect_list(payload: dict[str, object], key: str, expected: list[object]) -> None:
    value = payload.get(key)
    if value != expected:
        raise CheckError(f"{key} does not match the shared Phase 11 direct-read packet")


def run_check(root: Path) -> None:
    require_markers(root, DOCS_ROOT_PATH, "docs-root", DOCS_ROOT_MARKERS)
    require_markers(root, SEQUENCING_PATH, "lane-sequencing", SEQUENCING_MARKERS)
    require_markers(root, MATRIX_GAP_PATH, "matrix-gap", MATRIX_GAP_MARKERS)
    require_markers(root, HVC_SURVEY_PATH, "hvc-survey", HVC_SURVEY_MARKERS)

    payload = read_inventory(root)
    for key, expected in EXPECTED_INVENTORY.items():
        expect_list(payload, key, expected)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(
        root / DOCS_ROOT_PATH,
        "\n".join(
            [
                "# Zigux Documentation",
                "Phase 11 notes",
                "- `Documentation/zigux/phase11-driver-lane-sequencing.md`",
                "- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
                "- `Documentation/zigux/phase11-hvc-console-survey.md`",
                "- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
                "- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
                "- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
                "- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
                "- `scripts/zigux/check-phase11-build-inventory.py`",
                "- `scripts/zigux/check-phase11-matrix-gap-survey.py`",
                "- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`",
                "- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
                "- `drivers/watchdog/dw_wdt.zig`",
                "- `drivers/watchdog/dw_wdt_verify.zig`",
                "- `drivers/tty/hvc/hvc_console.zig`",
                "- `zigux/tests/fixtures/phase11_build_inventory.json`",
                "- `zigux/tests/phase11_dw_wdt_manifest.json`",
                "- `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
                "- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
                "- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
                "- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
                "- `Documentation/zigux/phase11-shared-replay-contract.md`",
                "- `Documentation/zigux/phase11-closure-note.md`",
                "- `scripts/zigux/check-phase11-shared-replay-contract.py`",
                "- `scripts/zigux/check-phase11-shared-summary-surfaces.py`",
                "- `zigux/tests/phase11_build.zig`",
                "- current `master` still exposes no dedicated `make -C zigux phase11`, `make -C zigux phase11-validate`, or `make -C zigux phase11-contract` routes",
                "",
            ]
        ),
    )
    write(
        root / SEQUENCING_PATH,
        "\n".join(
            [
                "# Phase 11 Driver Lane Sequencing",
                "shared sequencing lane `P11-Y06`",
                "DesignWare lane `P11-L10` currently owns the returned watchdog-local packet",
                "`drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`,",
                "`scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`, and",
                "`scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`",
                "HVC archival lane `P11-L16` currently keeps the directly readable",
                "`Documentation/zigux/phase11-hvc-console-survey.md`,",
                "`drivers/tty/hvc/hvc_console.zig`,",
                "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and",
                "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md` authoritative",
                "current `master` still does not rematerialize the shared-validator surfaces `scripts/zigux/validate-phase11.py`",
                "",
            ]
        ),
    )
    write(
        root / MATRIX_GAP_PATH,
        "\n".join(
            [
                "# Phase 11 Validation Matrix Gap Survey",
                "`PHASE11_MATRIX_GAP_STATUS=gpio_hvc_and_dw_matrices_direct_readback_only`",
                "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
                "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
                "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
                "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
                "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`",
                "`scripts/zigux/check-phase11-matrix-gap-survey.py`",
                "`scripts/zigux/check-phase11-validation-matrix-gap-survey.py`",
                "`scripts/zigux/check-phase11-build-inventory.py`",
                "Current direct contents reads in this run do not rematerialize",
                "The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared",
                "depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.",
                "",
            ]
        ),
    )
    write(
        root / HVC_SURVEY_PATH,
        "\n".join(
            [
                "# Phase 11 HVC Console Survey",
                "`PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`",
                "current authenticated contents readback keeps the bounded HVC current-head packet reviewable through:",
                "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
                "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
                "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
                "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
                "`zigux/tests/fixtures/phase11_build_inventory.json`",
                "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
                "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
                "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
                "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
                "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
                "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
                "## Current-Head Packet",
                "keep the deeper verify helper, sysrq helper, focused survey replay, manifest, teardown note, slice, and dedicated survey checker framed as archival or repo-reality-gap vocabulary until a future reread proves they returned beside the smaller companion packet.",
                "`zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey` route",
                "",
            ]
        ),
    )
    write(
        root / INVENTORY_PATH,
        json.dumps(EXPECTED_INVENTORY, indent=2) + "\n",
    )


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_shared_direct_read_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        missing_docs_gap = tmpdir / "missing_docs_gap"
        shutil.copytree(fixture, missing_docs_gap, dirs_exist_ok=True)
        write(
            missing_docs_gap / DOCS_ROOT_PATH,
            read_text(missing_docs_gap / DOCS_ROOT_PATH).replace(
                "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
                "",
            ),
        )
        expect_failure(missing_docs_gap, "`scripts/zigux/check-phase11-shared-summary-surfaces.py`")

        missing_validate_gap = tmpdir / "missing_validate_gap"
        shutil.copytree(fixture, missing_validate_gap, dirs_exist_ok=True)
        write(
            missing_validate_gap / SEQUENCING_PATH,
            read_text(missing_validate_gap / SEQUENCING_PATH).replace(
                "`scripts/zigux/validate-phase11.py`",
                "`scripts/zigux/validate-phase11-missing.py`",
            ),
        )
        expect_failure(missing_validate_gap, "`scripts/zigux/validate-phase11.py`")

        missing_matrix_inventory = tmpdir / "missing_matrix_inventory"
        shutil.copytree(fixture, missing_matrix_inventory, dirs_exist_ok=True)
        write(
            missing_matrix_inventory / MATRIX_GAP_PATH,
            read_text(missing_matrix_inventory / MATRIX_GAP_PATH).replace(
                "The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared",
                "The shared build inventory now carries 2 HVC proof-backed build tests, 0 shared",
            ),
        )
        expect_failure(missing_matrix_inventory, "The shared build inventory now carries 3 HVC proof-backed build tests")

        missing_hvc_route = tmpdir / "missing_hvc_route"
        shutil.copytree(fixture, missing_hvc_route, dirs_exist_ok=True)
        write(
            missing_hvc_route / HVC_SURVEY_PATH,
            read_text(missing_hvc_route / HVC_SURVEY_PATH).replace(
                "`zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey` route",
                "",
            ),
        )
        expect_failure(missing_hvc_route, "`zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey`")

        wrong_inventory = tmpdir / "wrong_inventory"
        shutil.copytree(fixture, wrong_inventory, dirs_exist_ok=True)
        payload = read_inventory(wrong_inventory)
        payload["build_test_names"] = payload["build_test_names"][:-1]
        write(wrong_inventory / INVENTORY_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(wrong_inventory, "build_test_names does not match the shared Phase 11 direct-read packet")

        missing_file = tmpdir / "missing_file"
        shutil.copytree(fixture, missing_file, dirs_exist_ok=True)
        (missing_file / DOCS_ROOT_PATH).unlink()
        expect_failure(missing_file, str(DOCS_ROOT_PATH))

        print("PHASE11_SHARED_DIRECT_READ_ALIGNMENT_SELF_TEST=pass")
        print("PHASE11_SHARED_DIRECT_READ_ALIGNMENT_SELF_TEST_CASE_COUNT=6")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        run_check(args.root)
    except CheckError as exc:
        print(f"PHASE11_SHARED_DIRECT_READ_ALIGNMENT=fail: {exc}")
        return 1

    print("PHASE11_SHARED_DIRECT_READ_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())