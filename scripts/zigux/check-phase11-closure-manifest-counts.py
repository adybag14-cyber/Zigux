#!/usr/bin/env python3
"""Fail closed when the Phase 11 closure manifest drifts from the current packet."""

from __future__ import annotations

import argparse
import copy
import json
import sys
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) > 2 else SELF_PATH.parent
MANIFEST_PATH = 'zigux/tests/phase11_closure_manifest.json'

COUNT_FIELDS = {
    'doc_count': 'docs',
    'manifest_count': 'manifests',
    'driver_count': 'drivers',
    'test_count': 'tests',
}

REQUIRED_DRIVER_LOCAL_MATRICES = [
    'Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md',
    'Documentation/zigux/phase11-gpio-wdt-validation-matrix.md',
    'Documentation/zigux/phase11-hvc-console-validation-matrix.md',
    'Documentation/zigux/phase11-dw-wdt-validation-matrix.md',
]

REQUIRED_DETERMINISTIC_FIXTURE_SURFACES = [
    'zigux/tests/fixtures/phase11_build_inventory.json',
    'zigux/tests/fixtures/phase11_validate_checks.json',
    'zigux/tests/fixtures/phase11_shared_tooling_manifest.json',
    'zigux/tests/phase11_dw_wdt_manifest.json',
]

REQUIRED_FOCUSED_FAILURE_MODE_BUILDS = [
    'zigux/tests/phase11_hvc_modem_control_proof_build.zig',
    'zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig',
    'zigux/tests/phase11_dw_wdt_restart_build.zig',
    'zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig',
]

REQUIRED_PROOF_BUILD_ROUTES = [
    'zig build test --build-file zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig',
    'zig build test --build-file zigux/tests/phase11_dw_wdt_build.zig',
    'zig build test --build-file zigux/tests/phase11_dw_wdt_restart_build.zig',
    'zig build test --build-file zigux/tests/phase11_dw_wdt_pm_build.zig',
    'zig build test --build-file zigux/tests/phase11_gpio_wdt_verify_helper_build.zig',
    'zig build test --build-file zigux/tests/phase11_gpio_wdt_preflight_review_build.zig',
    'zig build test --build-file zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig',
    'zig build test --build-file zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig',
    'zig build test --build-file zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig',
    'zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig',
    'zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig',
    'zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig',
    'zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig',
    'zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig',
]

REQUIRED_EXACT_CHECKS = [
    'python3 scripts/zigux/check-phase11-build-inventory.py',
    'python3 scripts/zigux/check-phase11-validate-manifest-roster.py',
    'python3 scripts/zigux/check-phase11-validate-check-roster.py',
    'python3 scripts/zigux/check-phase11-validate-route-alignment.py',
    'python3 scripts/zigux/check-phase11-shared-tooling-manifest.py',
    'python3 scripts/zigux/check-phase11-closure-manifest-counts.py',
    'python3 scripts/zigux/check-phase11-focused-direct-build-replays.py',
    'python3 scripts/zigux/check-phase11-shared-replay-contract-counts.py',
    'python3 scripts/zigux/check-phase11-matrix-gap-survey.py',
    'python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py',
    'python3 scripts/zigux/check-phase11-watchdog-lifecycle-parity-gap.py',
    'python3 scripts/zigux/check-phase11-header-boundary-packet.py',
    'python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py',
    'python3 scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py',
    'python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py',
    'python3 scripts/zigux/check-phase11-hvc-current-head-manifest.py',
    'python3 scripts/zigux/check-phase11-dw-wdt-teardown-packet.py',
    'python3 scripts/zigux/check-phase11-dw-wdt-verify-alignment.py',
    'python3 scripts/zigux/validate-phase11.py',
    'make -C zigux phase11-validate',
]


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding='utf-8'))


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def require_list_members(
    drift: list[str], prefix: str, actual_list: object, required_items: list[str]
) -> None:
    if not isinstance(actual_list, list) or not actual_list:
        drift.append(f'{prefix}:missing')
        return
    for item in required_items:
        if item not in actual_list:
            drift.append(f"{prefix}:{item!r}:missing")


def collect_drift(manifest: dict[str, object]) -> list[str]:
    drift: list[str] = []
    for count_field, list_field in COUNT_FIELDS.items():
        listed = manifest.get(list_field)
        if not isinstance(listed, list) or not listed:
            drift.append(f'{list_field}:missing')
            continue
        count = manifest.get(count_field)
        if not isinstance(count, int):
            drift.append(f'{count_field}:missing')
            continue
        if count != len(listed):
            drift.append(f'{count_field}:{count}!=len({list_field}):{len(listed)}')

    if manifest.get('phase') != 'Phase 11':
        drift.append(f"phase:{manifest.get('phase')!r}!='Phase 11'")
    if manifest.get('lane_key') != 'P11-L17':
        drift.append(f"lane_key:{manifest.get('lane_key')!r}!='P11-L17'")
    if manifest.get('status') != 'closure_packet_materialized':
        drift.append(
            f"status:{manifest.get('status')!r}!='closure_packet_materialized'"
        )
    if manifest.get('shared_validate_route') != 'make -C zigux phase11-validate':
        drift.append('shared_validate_route:missing_or_changed')

    require_list_members(
        drift,
        'driver_local_matrices',
        manifest.get('driver_local_matrices'),
        REQUIRED_DRIVER_LOCAL_MATRICES,
    )
    require_list_members(
        drift,
        'deterministic_fixture_surfaces',
        manifest.get('deterministic_fixture_surfaces'),
        REQUIRED_DETERMINISTIC_FIXTURE_SURFACES,
    )
    require_list_members(
        drift,
        'focused_failure_mode_builds',
        manifest.get('focused_failure_mode_builds'),
        REQUIRED_FOCUSED_FAILURE_MODE_BUILDS,
    )
    require_list_members(
        drift,
        'proof_build_routes',
        manifest.get('proof_build_routes'),
        REQUIRED_PROOF_BUILD_ROUTES,
    )

    exact_checks = manifest.get('exact_checks')
    if not isinstance(exact_checks, list) or not exact_checks:
        drift.append('exact_checks:missing')
        return drift
    indexes: list[int] = []
    for item in REQUIRED_EXACT_CHECKS:
        if item not in exact_checks:
            drift.append(f"exact_checks:{item!r}:missing")
            continue
        indexes.append(exact_checks.index(item))
    if len(indexes) == len(REQUIRED_EXACT_CHECKS) and indexes != sorted(indexes):
        drift.append('exact_checks:required_routes:out_of_order')

    return drift


def validate(root: Path) -> tuple[list[str], list[str]]:
    manifest_path = root / MANIFEST_PATH
    if not manifest_path.exists():
        return ([MANIFEST_PATH], [])
    manifest = read_json(manifest_path)
    return ([], collect_drift(manifest))


def fixture_manifest() -> dict[str, object]:
    docs = [
        'Documentation/zigux/phase11-closure-evidence.md',
        'Documentation/zigux/phase11-driver-lane-sequencing.md',
        'Documentation/zigux/phase11-validation-matrix-gap-survey.md',
        'Documentation/zigux/phase11-codegen-manifest-tooling-gap-survey.md',
        'Documentation/zigux/phase11-watchdog-lifecycle-parity-gap.md',
        'Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md',
        'Documentation/zigux/phase11-gpio-wdt-validation-matrix.md',
        'Documentation/zigux/phase11-hvc-console-validation-matrix.md',
        'Documentation/zigux/phase11-dw-wdt-validation-matrix.md',
    ]
    manifests = [
        'zigux/tests/phase11_closure_manifest.json',
        'zigux/tests/fixtures/phase11_build_inventory.json',
        'zigux/tests/fixtures/phase11_validate_checks.json',
        'zigux/tests/fixtures/phase11_shared_tooling_manifest.json',
        'zigux/tests/phase11_bcm2835_wdt_manifest.json',
        'zigux/tests/phase11_dw_wdt_manifest.json',
    ]
    drivers = [
        'drivers/tty/hvc/hvc_console.zig',
        'drivers/tty/hvc/hvc_console_verify.zig',
        'drivers/watchdog/bcm2835_wdt.zig',
        'drivers/watchdog/bcm2835_wdt_verify.zig',
        'drivers/watchdog/gpio_wdt.zig',
        'drivers/watchdog/gpio_wdt_verify.zig',
        'drivers/watchdog/dw_wdt_restart.zig',
        'drivers/watchdog/dw_wdt_pm.zig',
        'drivers/watchdog/dw_wdt_pm_scaffold.zig',
        'drivers/watchdog/dw_wdt_verify.zig',
    ]
    tests = [
        'zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey.zig',
        'zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig',
        'zigux/tests/phase11_bcm2835_wdt.zig',
        'zigux/tests/phase11_dw_wdt_survey.zig',
        'zigux/tests/phase11_dw_wdt_registration_scaffold.zig',
        'zigux/tests/phase11_dw_wdt_build.zig',
        'zigux/tests/phase11_dw_wdt_restart_build.zig',
        'zigux/tests/phase11_dw_wdt_pm_build.zig',
        'zigux/tests/phase11_gpio_wdt_verify_helper_build.zig',
        'zigux/tests/phase11_gpio_wdt_preflight_review.zig',
        'zigux/tests/phase11_gpio_wdt_preflight_review_build.zig',
        'zigux/tests/phase11_gpio_wdt_register_device_glue_review.zig',
        'zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig',
        'zigux/tests/phase11_gpio_wdt_nowayout_policy_review.zig',
        'zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig',
        'zigux/tests/phase11_gpio_wdt_remove_handoff_review.zig',
        'zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig',
        'zigux/tests/phase11_hvc_hv_ops_layout_proof.zig',
        'zigux/tests/phase11_hvc_hv_ops_layout_build.zig',
        'zigux/tests/phase11_hvc_export_surface_layout_proof.zig',
        'zigux/tests/phase11_hvc_export_surface_layout_build.zig',
        'zigux/tests/phase11_hvc_cleanup_packet_proof.zig',
        'zigux/tests/phase11_hvc_cleanup_packet_build.zig',
        'zigux/tests/phase11_hvc_modem_control_proof.zig',
        'zigux/tests/phase11_hvc_modem_control_proof_build.zig',
        'zigux/tests/phase11_hvc_targetless_unregister_gap.zig',
        'zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig',
    ]
    return {
        'phase': 'Phase 11',
        'lane_key': 'P11-L17',
        'status': 'closure_packet_materialized',
        'tranche': 'simple-driver-delivery-gate-evidence',
        'shared_validate_route': 'make -C zigux phase11-validate',
        'doc_count': len(docs),
        'manifest_count': len(manifests),
        'driver_count': len(drivers),
        'test_count': len(tests),
        'driver_local_matrices': REQUIRED_DRIVER_LOCAL_MATRICES,
        'deterministic_fixture_surfaces': REQUIRED_DETERMINISTIC_FIXTURE_SURFACES,
        'focused_failure_mode_builds': REQUIRED_FOCUSED_FAILURE_MODE_BUILDS,
        'proof_build_routes': REQUIRED_PROOF_BUILD_ROUTES,
        'docs': docs,
        'manifests': manifests,
        'drivers': drivers,
        'tests': tests,
        'exact_checks': REQUIRED_EXACT_CHECKS,
    }


def write_fixture(root: Path) -> None:
    manifest = fixture_manifest()
    write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + '\n')


def expect_contains(items: list[str], expected: str, label: str) -> None:
    if expected not in items:
        actual = ','.join(items) if items else 'none'
        raise SystemExit(f'{label}:expected={expected}:actual={actual}')


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix='zigux_phase11_closure_manifest_') as tmp_dir:
        root = Path(tmp_dir)
        write_fixture(root)
        missing_files, drift = validate(root)
        if missing_files or drift:
            raise SystemExit(
                'phase11-closure-manifest-self-test:baseline_failed:'
                f"files={','.join(missing_files) or 'none'}:"
                f"drift={','.join(drift) or 'none'}"
            )

        manifest_path = root / MANIFEST_PATH
        original = read_json(manifest_path)

        def write_manifest(data: dict[str, object]) -> None:
            write_text(manifest_path, json.dumps(data, indent=2) + '\n')

        cases = 0

        broken = copy.deepcopy(original)
        broken['doc_count'] = broken['doc_count'] - 1
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            f"doc_count:{broken['doc_count']}!=len(docs):{original['doc_count']}",
            'phase11-closure-manifest-self-test',
        )
        cases += 1
        write_fixture(root)

        broken = copy.deepcopy(original)
        broken['proof_build_routes'] = broken['proof_build_routes'][:-1]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "proof_build_routes:'zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig':missing",
            'phase11-closure-manifest-self-test',
        )
        cases += 1
        write_fixture(root)

        broken = copy.deepcopy(original)
        broken['exact_checks'] = [
            item for item in broken['exact_checks'] if item != 'python3 scripts/zigux/check-phase11-closure-manifest-counts.py'
        ]
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "exact_checks:'python3 scripts/zigux/check-phase11-closure-manifest-counts.py':missing",
            'phase11-closure-manifest-self-test',
        )
        cases += 1
        write_fixture(root)

        broken = copy.deepcopy(original)
        reordered = list(REQUIRED_EXACT_CHECKS)
        reordered[4], reordered[5] = reordered[5], reordered[4]
        broken['exact_checks'] = reordered
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            'exact_checks:required_routes:out_of_order',
            'phase11-closure-manifest-self-test',
        )
        cases += 1
        write_fixture(root)

        broken = copy.deepcopy(original)
        broken['status'] = 'stale'
        write_manifest(broken)
        expect_contains(
            validate(root)[1],
            "status:'stale'!='closure_packet_materialized'",
            'phase11-closure-manifest-self-test',
        )
        cases += 1

    print('PHASE11_CLOSURE_MANIFEST_COUNTS_SELF_TEST=pass')
    print(f'PHASE11_CLOSURE_MANIFEST_COUNTS_SELF_TEST_CASE_COUNT={cases}')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Validate the Phase 11 closure manifest summary-count packet.'
    )
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--repo-root', type=Path, default=ROOT)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, drift = validate(args.repo_root)
    if missing_files:
        print('PHASE11_CLOSURE_MANIFEST_COUNTS=fail')
        print('MISSING_PHASE11_CLOSURE_MANIFEST_COUNTS_FILES_START')
        for item in missing_files:
            print(item)
        print('MISSING_PHASE11_CLOSURE_MANIFEST_COUNTS_FILES_END')
        return 1

    if drift:
        print('PHASE11_CLOSURE_MANIFEST_COUNTS=fail')
        print('PHASE11_CLOSURE_MANIFEST_COUNTS_DRIFT_START')
        for item in drift:
            print(item)
        print('PHASE11_CLOSURE_MANIFEST_COUNTS_DRIFT_END')
        return 1

    print('PHASE11_CLOSURE_MANIFEST_COUNTS=pass')
    print(f'PHASE11_CLOSURE_MANIFEST_COUNTS_FIELD_COUNT={len(COUNT_FIELDS)}')
    print(
        'PHASE11_CLOSURE_MANIFEST_COUNTS_REQUIRED_DRIVER_MATRIX_COUNT='
        f'{len(REQUIRED_DRIVER_LOCAL_MATRICES)}'
    )
    print(
        'PHASE11_CLOSURE_MANIFEST_COUNTS_REQUIRED_DETERMINISTIC_FIXTURE_COUNT='
        f'{len(REQUIRED_DETERMINISTIC_FIXTURE_SURFACES)}'
    )
    print(
        'PHASE11_CLOSURE_MANIFEST_COUNTS_REQUIRED_FAILURE_MODE_BUILD_COUNT='
        f'{len(REQUIRED_FOCUSED_FAILURE_MODE_BUILDS)}'
    )
    print(
        'PHASE11_CLOSURE_MANIFEST_COUNTS_REQUIRED_PROOF_BUILD_ROUTE_COUNT='
        f'{len(REQUIRED_PROOF_BUILD_ROUTES)}'
    )
    print(
        'PHASE11_CLOSURE_MANIFEST_COUNTS_REQUIRED_EXACT_CHECK_COUNT='
        f'{len(REQUIRED_EXACT_CHECKS)}'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
