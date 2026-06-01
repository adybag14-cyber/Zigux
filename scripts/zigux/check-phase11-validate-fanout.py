#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 shared validate-route fan-out."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

CONTRACT_PATH = Path("Documentation/zigux/phase11-shared-replay-contract.md")
VALIDATE_PATH = Path("scripts/zigux/validate-phase11.py")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")

REQUIRED_SHARED_BUILD_FILES = (
    "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
    "zigux/tests/phase11_dw_wdt_build.zig",
    "zigux/tests/phase11_dw_wdt_pm_build.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
)

FORBIDDEN_VALIDATE_ONLY_BUILD_FILES = (
    "zigux/tests/phase11_dw_wdt_restart_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
)

REQUIRED_VALIDATE_MARKERS = (
    '("python", "scripts/zigux/check-phase11-build-inventory.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-build-inventory.py")',
    '("python", "scripts/zigux/check-phase11-shared-replay-contract-counts.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-shared-replay-contract-counts.py")',
    '("python", "scripts/zigux/check-phase11-matrix-gap-survey.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-matrix-gap-survey.py")',
    '("python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py")',
    '("python", "scripts/zigux/check-phase11-hvc-cleanup-current-head.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-hvc-cleanup-current-head.py")',
    '("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py")',
    '("python", "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py")',
    '("python", "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py", "--self-test")',
    '("python", "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py")',
)

REQUIRED_CONTRACT_MARKERS = (
    "The same shared validator and Makefile route now fan out through",
    "`zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig`,",
    "`zigux/tests/phase11_dw_wdt_build.zig`,",
    "`zigux/tests/phase11_dw_wdt_pm_build.zig`,",
    "`zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig`,",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`,",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`,",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`,",
    "eight-route proof fan-out explicit",
)

REQUIRED_WORKFLOW_MARKERS = (
    "- name: Validate current Phase 11 support bundle",
    "run: make -C zigux phase11-validate",
)

REQUIRED_INVENTORY_BUILD_TEST_NAMES = (
    "phase11-hvc-hv-ops-layout-proof-tests",
    "phase11-hvc-export-surface-layout-proof-tests",
    "phase11-hvc-cleanup-packet-proof",
)

REQUIRED_INVENTORY_ADJUNCT_BUILDS = (
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
)


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative: Path) -> str:
    path = root / relative
    if not path.is_file():
        raise CheckError(f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def read_json(root: Path, relative: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(root, relative))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {relative}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckError(f"expected object in {relative}")
    return payload


def expect_string_list(label: str, value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CheckError(f"expected string list for {label}")
    if len(value) != len(set(value)):
        raise CheckError(f"duplicate entry in {label}")
    return list(value)


def require_markers(label: str, text: str, markers: tuple[str, ...]) -> None:
    normalized = " ".join(text.split())
    for marker in markers:
        if " ".join(marker.split()) not in normalized:
            raise CheckError(f"missing marker in {label}: {marker}")


def extract_build_files(text: str) -> list[str]:
    return re.findall(r"zigux/tests/phase11_[A-Za-z0-9_]+_build\.zig", text)


def run_check(root: Path) -> None:
    contract_text = read_text(root, CONTRACT_PATH)
    validate_text = read_text(root, VALIDATE_PATH)
    makefile_text = read_text(root, MAKEFILE_PATH)
    workflow_text = read_text(root, WORKFLOW_PATH)
    inventory = read_json(root, INVENTORY_PATH)

    require_markers(str(CONTRACT_PATH), contract_text, REQUIRED_CONTRACT_MARKERS)
    require_markers(str(VALIDATE_PATH), validate_text, REQUIRED_VALIDATE_MARKERS)
    require_markers(str(WORKFLOW_PATH), workflow_text, REQUIRED_WORKFLOW_MARKERS)

    validate_build_files = extract_build_files(validate_text)
    makefile_build_files = extract_build_files(makefile_text)

    if makefile_build_files != list(REQUIRED_SHARED_BUILD_FILES):
        raise CheckError("phase11-validate Makefile fan-out does not match the current shared contract")
    if validate_build_files != list(REQUIRED_SHARED_BUILD_FILES):
        raise CheckError("phase11-validate validator fan-out does not match the current shared contract")

    for forbidden in FORBIDDEN_VALIDATE_ONLY_BUILD_FILES:
        if forbidden in validate_build_files:
            raise CheckError(f"validator still widens Phase 11 fan-out beyond the shared contract: {forbidden}")
        if forbidden in contract_text or forbidden in makefile_text:
            raise CheckError(f"unexpected widened Phase 11 shared-route marker: {forbidden}")

    if expect_string_list("build_test_names", inventory.get("build_test_names")) != list(REQUIRED_INVENTORY_BUILD_TEST_NAMES):
        raise CheckError("build inventory no longer matches the narrower HVC continuity packet")
    if expect_string_list("shared_adjunct_build_replays", inventory.get("shared_adjunct_build_replays")) != list(REQUIRED_INVENTORY_ADJUNCT_BUILDS):
        raise CheckError("shared_adjunct_build_replays no longer matches the narrower HVC continuity packet")
    if expect_string_list("shared_test_depend_steps", inventory.get("shared_test_depend_steps")) != []:
        raise CheckError("shared_test_depend_steps should stay empty for the narrower HVC continuity packet")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path, *, include_validator_drift: bool = False) -> None:
    validate_build_lines = "\n".join(
        f'    CheckSpec("build-{index}", ("zig", "build", "test", "--build-file", "{path}")),'
        for index, path in enumerate(
            REQUIRED_SHARED_BUILD_FILES + FORBIDDEN_VALIDATE_ONLY_BUILD_FILES if include_validator_drift else REQUIRED_SHARED_BUILD_FILES,
            start=1,
        )
    )
    write(
        root / VALIDATE_PATH,
        "\n".join(
            [
                "CHECKS = (",
                *[f"    {marker}," for marker in REQUIRED_VALIDATE_MARKERS],
                validate_build_lines,
                ")",
            ]
        )
        + "\n",
    )
    write(
        root / MAKEFILE_PATH,
        "phase11-validate:\n"
        + "".join(
            f"\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file {path}\n"
            for path in REQUIRED_SHARED_BUILD_FILES
        ),
    )
    write(
        root / CONTRACT_PATH,
        "\n".join(
            [
                "# Phase 11 Shared Replay Contract",
                "The same shared validator and Makefile route now fan out through",
                *[f"- `{path}`," for path in REQUIRED_SHARED_BUILD_FILES[:-1]],
                f"- `{REQUIRED_SHARED_BUILD_FILES[-1]}`,",
                "so keep that eight-route proof fan-out explicit instead of reducing the current shared gate to the narrower HVC inventory alone.",
            ]
        )
        + "\n",
    )
    write(
        root / WORKFLOW_PATH,
        "jobs:\n  bootstrap:\n    steps:\n      - name: Validate current Phase 11 support bundle\n        run: make -C zigux phase11-validate\n",
    )
    write(
        root / INVENTORY_PATH,
        json.dumps(
            {
                "build_test_names": list(REQUIRED_INVENTORY_BUILD_TEST_NAMES),
                "shared_adjunct_build_replays": list(REQUIRED_INVENTORY_ADJUNCT_BUILDS),
                "shared_test_depend_steps": [],
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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_validate_fanout_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        validator_drift = tmpdir / "validator_drift"
        build_fixture(validator_drift, include_validator_drift=True)
        expect_failure(validator_drift, "phase11-validate validator fan-out does not match the current shared contract")
        case_count += 1

        missing_contract_marker = tmpdir / "missing_contract_marker"
        build_fixture(missing_contract_marker)
        write(
            missing_contract_marker / CONTRACT_PATH,
            read_text(missing_contract_marker, CONTRACT_PATH).replace("eight-route proof fan-out explicit", "", 1),
        )
        expect_failure(missing_contract_marker, "eight-route proof fan-out explicit")
        case_count += 1

        widened_makefile = tmpdir / "widened_makefile"
        build_fixture(widened_makefile)
        write(
            widened_makefile / MAKEFILE_PATH,
            read_text(widened_makefile, MAKEFILE_PATH)
            + "\tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_dw_wdt_restart_build.zig\n",
        )
        expect_failure(widened_makefile, "phase11-validate Makefile fan-out does not match the current shared contract")
        case_count += 1

        wrong_inventory = tmpdir / "wrong_inventory"
        build_fixture(wrong_inventory)
        write(
            wrong_inventory / INVENTORY_PATH,
            json.dumps(
                {
                    "build_test_names": list(REQUIRED_INVENTORY_BUILD_TEST_NAMES[:-1]),
                    "shared_adjunct_build_replays": list(REQUIRED_INVENTORY_ADJUNCT_BUILDS),
                    "shared_test_depend_steps": [],
                },
                indent=2,
            )
            + "\n",
        )
        expect_failure(wrong_inventory, "build inventory no longer matches the narrower HVC continuity packet")
        case_count += 1

        print("PHASE11_VALIDATE_FANOUT_SELF_TEST=pass")
        print(f"PHASE11_VALIDATE_FANOUT_SELF_TEST_CASE_COUNT={case_count}")
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
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_VALIDATE_FANOUT=fail: {exc}")
        return 1

    print("PHASE11_VALIDATE_FANOUT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
