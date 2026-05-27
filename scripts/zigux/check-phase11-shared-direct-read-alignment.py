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
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`scripts/zigux/validate-phase11.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase11-validate`",
)

SEQUENCING_MARKERS = (
    "shared sequencing lane `P11-Y06` owns the shared reminder wording",
    "DesignWare lane `P11-L10` stays separate from the shared sequencing lane",
    "HVC continuity lane `P11-L16` currently keeps the directly readable",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`scripts/zigux/validate-phase11.py`,",
    "`zigux/Makefile`, and the returned `make -C zigux phase11-validate` route",
    "`make -C zigux phase11` and",
    "`make -C zigux phase11-contract` still remain missing on current `master`",
)

MATRIX_GAP_MARKERS = (
    "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
    "deterministic tooling survey lane: `P11-L07`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/fixtures/phase11_validate_checks.json`, and `zigux/tests/phase11_dw_wdt_manifest.json`",
    "The shared Phase 11 packet now rematerializes a dedicated golden-output fixture roster through `zigux/tests/fixtures/phase11_validate_checks.json` plus fail-closed `scripts/zigux/check-phase11-validate-check-roster.py` and `scripts/zigux/check-phase11-validate-route-alignment.py` guards.",
    "It still does not rematerialize a refresh helper route or an artifact-diff-style deterministic output guard for the driver-local proof builds.",
    "`scripts/zigux/validate-phase11.py` and `make -C zigux phase11-validate` therefore stay build-proof-first rather than expected-output-refresh-first.",
    "they still do not refresh or compare stable expected-output artifacts for the shared Phase 11 proof fan-out.",
)

HVC_SURVEY_MARKERS = (
    "`PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`",
    "current authenticated contents readback keeps the bounded HVC current-head",
    "`scripts/zigux/check-phase11-validate-manifest-roster.py`",
    "`scripts/zigux/check-phase11-validate-check-roster.py`",
    "`scripts/zigux/check-phase11-validate-route-alignment.py`",
    "the dedicated validate-check fixture roster",
    "focused-direct-build replay checker",
    "cleanup-current-head checker",
    "targetless-unregister witness checker",
    "the dedicated modem-control proof pair",
    "the standalone targetless-unregister witness pair",
    "`zigux/tests/phase11_hvc_current_head_manifest.json`",
    "`scripts/zigux/check-phase11-hvc-current-head-manifest.py`",
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
                "- `Documentation/zigux/phase11-driver-lane-sequencing.md`",
                "- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
                "- `Documentation/zigux/phase11-hvc-console-survey.md`",
                "- `Documentation/zigux/phase11-shared-replay-contract.md`",
                "- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
                "- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
                "- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
                "- `scripts/zigux/validate-phase11.py`",
                "- `zigux/Makefile`",
                "- `make -C zigux phase11-validate`",
                "",
            ]
        ),
    )
    write(
        root / SEQUENCING_PATH,
        "\n".join(
            [
                "# Phase 11 Driver Lane Sequencing",
                "shared sequencing lane `P11-Y06` owns the shared reminder wording",
                "DesignWare lane `P11-L10` stays separate from the shared sequencing lane",
                "HVC continuity lane `P11-L16` currently keeps the directly readable",
                "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
                "`scripts/zigux/validate-phase11.py`,",
                "`zigux/Makefile`, and the returned `make -C zigux phase11-validate` route",
                "`make -C zigux phase11` and",
                "`make -C zigux phase11-contract` still remain missing on current `master`",
                "",
            ]
        ),
    )
    write(
        root / MATRIX_GAP_PATH,
        "\n".join(
            [
                "# Phase 11 Validation Matrix Gap Survey",
                "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
                "deterministic tooling survey lane: `P11-L07`",
                "`zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/fixtures/phase11_validate_checks.json`, and `zigux/tests/phase11_dw_wdt_manifest.json`",
                "The shared Phase 11 packet now rematerializes a dedicated golden-output fixture roster through `zigux/tests/fixtures/phase11_validate_checks.json` plus fail-closed `scripts/zigux/check-phase11-validate-check-roster.py` and `scripts/zigux/check-phase11-validate-route-alignment.py` guards.",
                "It still does not rematerialize a refresh helper route or an artifact-diff-style deterministic output guard for the driver-local proof builds.",
                "`scripts/zigux/validate-phase11.py` and `make -C zigux phase11-validate` therefore stay build-proof-first rather than expected-output-refresh-first.",
                "they still do not refresh or compare stable expected-output artifacts for the shared Phase 11 proof fan-out.",
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
                "current authenticated contents readback keeps the bounded HVC current-head",
                "`scripts/zigux/check-phase11-validate-manifest-roster.py`",
                "`scripts/zigux/check-phase11-validate-check-roster.py`",
                "`scripts/zigux/check-phase11-validate-route-alignment.py`",
                "the dedicated validate-check fixture roster",
                "focused-direct-build replay checker",
                "cleanup-current-head checker",
                "targetless-unregister witness checker",
                "the dedicated modem-control proof pair",
                "the standalone targetless-unregister witness pair",
                "`zigux/tests/phase11_hvc_current_head_manifest.json`",
                "`scripts/zigux/check-phase11-hvc-current-head-manifest.py`",
                "`zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey`",
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

        missing_docs_route = tmpdir / "missing_docs_route"
        shutil.copytree(fixture, missing_docs_route, dirs_exist_ok=True)
        write(
            missing_docs_route / DOCS_ROOT_PATH,
            read_text(missing_docs_route / DOCS_ROOT_PATH).replace(
                "- `make -C zigux phase11-validate`\n",
                "",
            ),
        )
        expect_failure(missing_docs_route, "`make -C zigux phase11-validate`")

        missing_validate_route = tmpdir / "missing_validate_route"
        shutil.copytree(fixture, missing_validate_route, dirs_exist_ok=True)
        write(
            missing_validate_route / SEQUENCING_PATH,
            read_text(missing_validate_route / SEQUENCING_PATH).replace(
                "`zigux/Makefile`, and the returned `make -C zigux phase11-validate` route",
                "`zigux/Makefile`, but no shared route returned",
            ),
        )
        expect_failure(missing_validate_route, "`zigux/Makefile`, and the returned `make -C zigux phase11-validate` route")

        missing_matrix_status = tmpdir / "missing_matrix_status"
        shutil.copytree(fixture, missing_matrix_status, dirs_exist_ok=True)
        write(
            missing_matrix_status / MATRIX_GAP_PATH,
            read_text(missing_matrix_status / MATRIX_GAP_PATH).replace(
                "all_simple_driver_matrices_present",
                "gpio_hvc_and_dw_matrices_direct_readback_only",
            ),
        )
        expect_failure(missing_matrix_status, "all_simple_driver_matrices_present")

        missing_validate_roster = tmpdir / "missing_validate_roster"
        shutil.copytree(fixture, missing_validate_roster, dirs_exist_ok=True)
        write(
            missing_validate_roster / MATRIX_GAP_PATH,
            read_text(missing_validate_roster / MATRIX_GAP_PATH).replace(
                "`scripts/zigux/check-phase11-validate-check-roster.py` and ",
                "",
            ),
        )
        expect_failure(missing_validate_roster, "`scripts/zigux/check-phase11-validate-check-roster.py`")

        missing_targetless_marker = tmpdir / "missing_targetless_marker"
        shutil.copytree(fixture, missing_targetless_marker, dirs_exist_ok=True)
        write(
            missing_targetless_marker / HVC_SURVEY_PATH,
            read_text(missing_targetless_marker / HVC_SURVEY_PATH).replace(
                "targetless-unregister witness checker\n",
                "",
            ),
        )
        expect_failure(missing_targetless_marker, "targetless-unregister witness checker")

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
        print("PHASE11_SHARED_DIRECT_READ_ALIGNMENT_SELF_TEST_CASE_COUNT=7")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        build_fixture(args.write_sample_root)
        return 0

    try:
        run_check(args.root)
    except CheckError as exc:
        print(f"PHASE11_SHARED_DIRECT_READ_ALIGNMENT=fail: {exc}")
        return 1

    print("PHASE11_SHARED_DIRECT_READ_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
