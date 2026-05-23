#!/usr/bin/env python3
"""Fail-close guard for the current shared Phase 11 direct-read packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent

CONTRACT_PATH = Path("Documentation/zigux/phase11-shared-replay-contract.md")
SEQUENCING_PATH = Path("Documentation/zigux/phase11-driver-lane-sequencing.md")
MATRIX_GAP_PATH = Path("Documentation/zigux/phase11-validation-matrix-gap-survey.md")
TESTS_COMPANION_PATH = Path("Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md")
CONTRIBUTOR_SYNC_PATH = Path("Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
MAKEFILE_PATH = Path("zigux/Makefile")

CONTRACT_MARKERS = (
    "`PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful`",
    "`scripts/zigux/validate-phase11.py`",
    "`zigux/Makefile` now materializes `make -C zigux phase11-validate`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "`zigux/tests/phase11_build.zig` is not part of the current shared packet on",
    "no `make -C zigux phase11-contract`, `make -C zigux phase11`, or",
)

SEQUENCING_MARKERS = (
    "contributor-note lane `P11-L18` owns broad cross-phase reminder wording",
    "`scripts/zigux/validate-phase11.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase11-validate` route",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`Documentation/zigux/phase11-shared-replay-contract.md` directly readable",
    "`make -C zigux phase11` and",
    "`make -C zigux phase11-contract` still remain missing on current `master`",
)

MATRIX_GAP_MARKERS = (
    "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`scripts/zigux/validate-phase11.py`",
    "`zigux/Makefile`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "`make -C zigux phase11-validate`",
    "The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared",
    "That inventory does not stand in for a whole-Phase-11 replay roster",
)

TESTS_COMPANION_MARKERS = (
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`scripts/zigux/validate-phase11.py`",
    "`make -C zigux phase11-validate`",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
    "still does not rematerialize `zigux/tests/phase11_build.zig`",
)

CONTRIBUTOR_SYNC_MARKERS = (
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "`scripts/zigux/validate-phase11.py`",
    "`zigux/Makefile`",
    "`make -C zigux phase11-validate`",
    "`make -C zigux phase11` and `make -C zigux phase11-contract`",
)

MAKEFILE_MARKERS = (
    "phase11-validate:",
    "$(PYTHON) scripts/zigux/validate-phase11.py",
    "$(ZIG) build test --build-file zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
    "$(ZIG) build test --build-file zigux/tests/phase11_dw_wdt_build.zig",
    "$(ZIG) build test --build-file zigux/tests/phase11_dw_wdt_pm_build.zig",
    "$(ZIG) build test --build-file zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
    "$(ZIG) build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "$(ZIG) build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "$(ZIG) build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "$(ZIG) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
)

EXPECTED_INVENTORY = {
    "build_test_names": [
        "phase11-hvc-hv-ops-layout-proof-tests",
        "phase11-hvc-export-surface-layout-proof-tests",
        "phase11-hvc-cleanup-packet-proof",
    ],
    "shared_test_depend_steps": [],
    "dedicated_survey_replays": [],
    "shared_split_replays": [],
    "shared_adjunct_replays": [
        "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
        "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
        "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
    ],
    "shared_adjunct_build_replays": [
        "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
        "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
        "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    ],
    "workflow_phase11_steps": [
        {
            "name": "Validate current Phase 11 support bundle",
            "run": "make -C zigux phase11-validate",
        }
    ],
}

EXPECTED_EXACT_CURRENT_CHECKS = [
    "python3 scripts/zigux/check-phase11-build-inventory.py --self-test",
    "python3 scripts/zigux/check-phase11-build-inventory.py",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
    "python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test",
    "python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py",
    "zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
]


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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


def expect_equal(payload: dict[str, object], key: str, expected: object) -> None:
    if payload.get(key) != expected:
        raise CheckError(f"{key} does not match the current shared Phase 11 packet")


def run_check(root: Path) -> None:
    require_markers(root, CONTRACT_PATH, "shared-contract", CONTRACT_MARKERS)
    require_markers(root, SEQUENCING_PATH, "lane-sequencing", SEQUENCING_MARKERS)
    require_markers(root, MATRIX_GAP_PATH, "matrix-gap", MATRIX_GAP_MARKERS)
    require_markers(root, TESTS_COMPANION_PATH, "tests-companion", TESTS_COMPANION_MARKERS)
    require_markers(root, CONTRIBUTOR_SYNC_PATH, "contributor-sync", CONTRIBUTOR_SYNC_MARKERS)
    require_markers(root, MAKEFILE_PATH, "makefile", MAKEFILE_MARKERS)

    payload = read_inventory(root)
    for key, expected in EXPECTED_INVENTORY.items():
        expect_equal(payload, key, expected)
    expect_equal(payload, "exact_current_checks", EXPECTED_EXACT_CURRENT_CHECKS)


def build_fixture(root: Path) -> None:
    write(
        root / CONTRACT_PATH,
        "\n".join(
            [
                "# Phase 11 Shared Replay Contract",
                "",
                "- `PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful`",
                "- `scripts/zigux/validate-phase11.py`",
                "- `zigux/Makefile` now materializes `make -C zigux phase11-validate`",
                "- `zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`",
                "- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
                "- `zigux/tests/phase11_build.zig` is not part of the current shared packet on `master`",
                "- no `make -C zigux phase11-contract`, `make -C zigux phase11`, or `make -C zigux phase11-hvc-survey` route on current `master`",
                "",
            ]
        ),
    )
    write(
        root / SEQUENCING_PATH,
        "\n".join(
            [
                "# Phase 11 Driver Lane Sequencing",
                "",
                "- contributor-note lane `P11-L18` owns broad cross-phase reminder wording in `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase11.py`, and `zigux/Makefile` plus the returned `make -C zigux phase11-validate` route",
                "- keep `Documentation/zigux/phase11-shared-replay-contract.md` directly readable",
                "- keep `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` explicit in the narrower HVC packet",
                "- `make -C zigux phase11` and `make -C zigux phase11-contract` still remain missing on current `master`",
                "",
            ]
        ),
    )
    write(
        root / MATRIX_GAP_PATH,
        "\n".join(
            [
                "# Phase 11 Validation Matrix Gap Survey",
                "",
                "- `PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
                "- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
                "- `scripts/zigux/validate-phase11.py`",
                "- `zigux/Makefile`",
                "- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
                "- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
                "- `make -C zigux phase11-validate`",
                "- The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared",
                "  depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.",
                "- That inventory does not stand in for a whole-Phase-11 replay roster",
                "",
            ]
        ),
    )
    write(
        root / TESTS_COMPANION_PATH,
        "\n".join(
            [
                "# Phase 10, 11, and 13 Tests-Root Review Companion",
                "",
                "- `Documentation/zigux/phase11-shared-replay-contract.md`",
                "- `scripts/zigux/validate-phase11.py`",
                "- `make -C zigux phase11-validate`",
                "- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
                "- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
                "- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
                "- `PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
                "- Current direct readback still does not rematerialize `zigux/tests/phase11_build.zig`",
                "",
            ]
        ),
    )
    write(
        root / CONTRIBUTOR_SYNC_PATH,
        "\n".join(
            [
                "# Phase 10, 11, and 13 Contributor Surface Sync",
                "",
                "- `Documentation/zigux/phase11-shared-replay-contract.md`",
                "- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
                "- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
                "- `scripts/zigux/validate-phase11.py`",
                "- `zigux/Makefile`",
                "- `make -C zigux phase11-validate`",
                "- `make -C zigux phase11` and `make -C zigux phase11-contract` still remain missing",
                "",
            ]
        ),
    )
    write(
        root / MAKEFILE_PATH,
        "\n".join(
            [
                ".PHONY: phase11-validate",
                "",
                "phase11-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_dw_wdt_build.zig",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_dw_wdt_pm_build.zig",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
                "",
            ]
        ),
    )
    write(
        root / INVENTORY_PATH,
        json.dumps(
            {
                "build_test_names": EXPECTED_INVENTORY["build_test_names"],
                "shared_test_depend_steps": EXPECTED_INVENTORY["shared_test_depend_steps"],
                "exact_current_checks": EXPECTED_EXACT_CURRENT_CHECKS,
                "workflow_phase11_steps": EXPECTED_INVENTORY["workflow_phase11_steps"],
                "dedicated_survey_replays": EXPECTED_INVENTORY["dedicated_survey_replays"],
                "shared_split_replays": EXPECTED_INVENTORY["shared_split_replays"],
                "shared_adjunct_replays": EXPECTED_INVENTORY["shared_adjunct_replays"],
                "shared_adjunct_build_replays": EXPECTED_INVENTORY["shared_adjunct_build_replays"],
            },
            indent=2,
        )
        + "\n",
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

        missing_contract = tmpdir / "missing_contract"
        shutil.copytree(fixture, missing_contract, dirs_exist_ok=True)
        write(
            missing_contract / CONTRACT_PATH,
            read_text(missing_contract / CONTRACT_PATH).replace(
                "`zigux/Makefile` now materializes `make -C zigux phase11-validate`",
                "",
            ),
        )
        expect_failure(missing_contract, "`zigux/Makefile` now materializes `make -C zigux phase11-validate`")

        missing_sequencing = tmpdir / "missing_sequencing"
        shutil.copytree(fixture, missing_sequencing, dirs_exist_ok=True)
        write(
            missing_sequencing / SEQUENCING_PATH,
            read_text(missing_sequencing / SEQUENCING_PATH).replace(
                "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
                "",
            ),
        )
        expect_failure(missing_sequencing, "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`")

        wrong_status = tmpdir / "wrong_status"
        shutil.copytree(fixture, wrong_status, dirs_exist_ok=True)
        write(
            wrong_status / MATRIX_GAP_PATH,
            read_text(wrong_status / MATRIX_GAP_PATH).replace(
                "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
                "`PHASE11_MATRIX_GAP_STATUS=stale_partial_matrix_story`",
            ),
        )
        expect_failure(wrong_status, "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`")

        missing_tests_marker = tmpdir / "missing_tests_marker"
        shutil.copytree(fixture, missing_tests_marker, dirs_exist_ok=True)
        write(
            missing_tests_marker / TESTS_COMPANION_PATH,
            read_text(missing_tests_marker / TESTS_COMPANION_PATH).replace(
                "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
                "",
            ),
        )
        expect_failure(missing_tests_marker, "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`")

        missing_contributor_sync = tmpdir / "missing_contributor_sync"
        shutil.copytree(fixture, missing_contributor_sync, dirs_exist_ok=True)
        write(
            missing_contributor_sync / CONTRIBUTOR_SYNC_PATH,
            read_text(missing_contributor_sync / CONTRIBUTOR_SYNC_PATH).replace(
                "`make -C zigux phase11-validate`",
                "",
            ),
        )
        expect_failure(missing_contributor_sync, "`make -C zigux phase11-validate`")

        missing_makefile_route = tmpdir / "missing_makefile_route"
        shutil.copytree(fixture, missing_makefile_route, dirs_exist_ok=True)
        write(
            missing_makefile_route / MAKEFILE_PATH,
            read_text(missing_makefile_route / MAKEFILE_PATH).replace(
                "phase11-validate:",
                "phase11-review:",
            ),
        )
        expect_failure(missing_makefile_route, "phase11-validate:")

        wrong_inventory = tmpdir / "wrong_inventory"
        shutil.copytree(fixture, wrong_inventory, dirs_exist_ok=True)
        payload = read_inventory(wrong_inventory)
        payload["build_test_names"] = payload["build_test_names"][:-1]
        write(wrong_inventory / INVENTORY_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(wrong_inventory, "build_test_names does not match the current shared Phase 11 packet")

        wrong_checks = tmpdir / "wrong_checks"
        shutil.copytree(fixture, wrong_checks, dirs_exist_ok=True)
        payload = read_inventory(wrong_checks)
        payload["exact_current_checks"] = payload["exact_current_checks"][:-1]
        write(wrong_checks / INVENTORY_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(wrong_checks, "exact_current_checks does not match the current shared Phase 11 packet")

        print("PHASE11_SHARED_DIRECT_READ_ALIGNMENT_SELF_TEST=pass")
        print("PHASE11_SHARED_DIRECT_READ_ALIGNMENT_SELF_TEST_CASE_COUNT=8")
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
        print(f"PHASE11_SHARED_DIRECT_READ_ALIGNMENT_SAMPLE_ROOT={args.write_sample_root}")
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
