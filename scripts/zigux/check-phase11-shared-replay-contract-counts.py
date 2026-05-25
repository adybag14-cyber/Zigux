#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 shared replay contract count summary."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

DEFAULT_ROOT = (
    Path(__file__).resolve().parents[3]
    if len(Path(__file__).resolve().parents) > 3
    else Path.cwd()
)
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
CONTRACT_PATH = Path("Documentation/zigux/phase11-shared-replay-contract.md")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
MAKEFILE_PATH = Path("zigux/Makefile")

EXPECTED_COUNTS = {
    "build_test_names": 3,
    "shared_test_depend_steps": 0,
    "dedicated_survey_replays": 0,
    "shared_adjunct_replays": 3,
    "shared_adjunct_build_replays": 3,
    "focused_direct_build_checks": 2,
    "focused_direct_build_replays": 2,
    "exact_current_checks": 11,
}

EXPECTED_EXACT_CURRENT_CHECKS = (
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
    "zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
)

EXPECTED_FOCUSED_DIRECT_BUILD_CHECKS = (
    "python3 scripts/zigux/check-phase11-focused-direct-build-replays.py --self-test",
    "python3 scripts/zigux/check-phase11-focused-direct-build-replays.py",
)

EXPECTED_FOCUSED_DIRECT_BUILD_REPLAYS = (
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
)

EXPECTED_PROOF_FANOUT_MARKERS = (
    "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
    "zigux/tests/phase11_dw_wdt_build.zig",
    "zigux/tests/phase11_dw_wdt_restart_build.zig",
    "zigux/tests/phase11_dw_wdt_pm_build.zig",
    "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
)

REQUIRED_CONTRACT_MARKERS = (
    "3 build test names",
    "0 shared `test_step.dependOn(...)` edges",
    "0 dedicated survey replays",
    "3 shared adjunct proof replays",
    "3 adjunct build replays",
    "2 focused direct build checker routes",
    "2 focused direct build replays",
    "11 HVC current-head exact command markers",
    "`make -C zigux phase11-validate` wrapper now cover thirteen focused proof builds through",
)

REQUIRED_DESIGNWARE_CURRENT_HEAD_MARKERS = (
    "`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`,",
    "`Documentation/zigux/phase11-dw-wdt-provenance-readback.md`,",
    "`Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`,",
    "`Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`,",
    "`Documentation/zigux/phase11-dw-wdt-survey.md`,",
    "`scripts/zigux/check-phase11-dw-wdt-teardown-packet.py`,",
    "`scripts/zigux/check-phase11-dw-wdt-verify-alignment.py`,",
    "`zigux/tests/phase11_dw_wdt_manifest.json`,",
    "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`,",
    "`zigux/tests/phase11_dw_wdt_survey.zig`,",
    "`drivers/watchdog/dw_wdt_restart.zig`,",
    "`drivers/watchdog/dw_wdt_pm.zig`, and",
    "`drivers/watchdog/dw_wdt_pm_scaffold.zig`; keep that returned smaller",
    "broader direct driver, verify-helper, replay-backed stack, platform-backed registration, PM",
    "execution, IRQ execution, and MMIO follow-through remain parked as the next",
)

REQUIRED_VALIDATE_SUPPORT_MARKERS = (
    "`scripts/zigux/check-phase11-validate-manifest-roster.py`",
    "`scripts/zigux/check-phase11-validate-check-roster.py`",
    "`scripts/zigux/check-phase11-validate-route-alignment.py`",
    "`zigux/tests/fixtures/phase11_validate_checks.json`",
)

REQUIRED_WORKFLOW_MARKERS = (
    "run: make -C zigux phase11-validate",
)

REQUIRED_MAKEFILE_MARKERS = (
    "phase11-validate:",
    "scripts/zigux/validate-phase11.py",
    *EXPECTED_PROOF_FANOUT_MARKERS,
)


class CheckError(RuntimeError):
    pass


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckError(f"expected object in {path}")
    return value


def expect_string_list(label: str, value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CheckError(f"expected string list for {label}")
    return list(value)


def require_markers(label: str, text: str, markers: tuple[str, ...]) -> None:
    normalized = normalize_whitespace(text)
    for marker in markers:
        if normalize_whitespace(marker) not in normalized:
            raise CheckError(f"missing marker in {label}: {marker}")


def run_check(root: Path) -> None:
    inventory = read_json(root / INVENTORY_PATH)
    contract = read_text(root / CONTRACT_PATH)
    workflow = read_text(root / WORKFLOW_PATH)
    makefile = read_text(root / MAKEFILE_PATH)

    for label, expected in EXPECTED_COUNTS.items():
        actual = len(expect_string_list(label, inventory.get(label)))
        if actual != expected:
            raise CheckError(f"{label} count mismatch: expected {expected}, found {actual}")

    exact_current_checks = expect_string_list(
        "exact_current_checks",
        inventory.get("exact_current_checks"),
    )
    if exact_current_checks != list(EXPECTED_EXACT_CURRENT_CHECKS):
        raise CheckError("exact_current_checks does not match the current-head HVC packet")

    focused_direct_build_checks = expect_string_list(
        "focused_direct_build_checks",
        inventory.get("focused_direct_build_checks"),
    )
    if focused_direct_build_checks != list(EXPECTED_FOCUSED_DIRECT_BUILD_CHECKS):
        raise CheckError("focused_direct_build_checks does not match the current-head Phase 11 packet")

    focused_direct_build_replays = expect_string_list(
        "focused_direct_build_replays",
        inventory.get("focused_direct_build_replays"),
    )
    if focused_direct_build_replays != list(EXPECTED_FOCUSED_DIRECT_BUILD_REPLAYS):
        raise CheckError("focused_direct_build_replays does not match the current-head Phase 11 packet")

    require_markers(str(CONTRACT_PATH), contract, REQUIRED_CONTRACT_MARKERS)
    require_markers(str(CONTRACT_PATH), contract, REQUIRED_DESIGNWARE_CURRENT_HEAD_MARKERS)
    require_markers(str(CONTRACT_PATH), contract, REQUIRED_VALIDATE_SUPPORT_MARKERS)
    require_markers(str(CONTRACT_PATH), contract, EXPECTED_EXACT_CURRENT_CHECKS)
    require_markers(str(CONTRACT_PATH), contract, EXPECTED_FOCUSED_DIRECT_BUILD_CHECKS)
    require_markers(str(CONTRACT_PATH), contract, EXPECTED_FOCUSED_DIRECT_BUILD_REPLAYS)
    require_markers(str(CONTRACT_PATH), contract, EXPECTED_PROOF_FANOUT_MARKERS)
    require_markers(str(WORKFLOW_PATH), workflow, REQUIRED_WORKFLOW_MARKERS)
    require_markers(str(MAKEFILE_PATH), makefile, REQUIRED_MAKEFILE_MARKERS)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(
        root / INVENTORY_PATH,
        json.dumps(
            {
                "build_test_names": ["a", "b", "c"],
                "shared_test_depend_steps": [],
                "dedicated_survey_replays": [],
                "shared_adjunct_replays": ["a", "b", "c"],
                "shared_adjunct_build_replays": ["a", "b", "c"],
                "focused_direct_build_checks": list(EXPECTED_FOCUSED_DIRECT_BUILD_CHECKS),
                "focused_direct_build_replays": list(EXPECTED_FOCUSED_DIRECT_BUILD_REPLAYS),
                "exact_current_checks": list(EXPECTED_EXACT_CURRENT_CHECKS),
            },
            indent=2,
        )
        + "\n",
    )
    write(
        root / CONTRACT_PATH,
        "\n".join(
            [
                "3 build test names",
                "0 shared `test_step.dependOn(...)` edges",
                "0 dedicated survey replays",
                "3 shared adjunct proof replays",
                "3 adjunct build replays",
                "2 focused direct build checker routes",
                "2 focused direct build replays",
                "11 HVC current-head exact command markers",
                "`make -C zigux phase11-validate` wrapper now cover thirteen focused proof builds through",
                *REQUIRED_DESIGNWARE_CURRENT_HEAD_MARKERS,
                *REQUIRED_VALIDATE_SUPPORT_MARKERS,
                *EXPECTED_EXACT_CURRENT_CHECKS,
                *EXPECTED_FOCUSED_DIRECT_BUILD_CHECKS,
                *EXPECTED_FOCUSED_DIRECT_BUILD_REPLAYS,
                *EXPECTED_PROOF_FANOUT_MARKERS,
            ]
        )
        + "\n",
    )
    write(
        root / WORKFLOW_PATH,
        "\n".join(
            [
                "name: zigux-bootstrap",
                "- name: Validate current Phase 11 support bundle",
                "  run: make -C zigux phase11-validate",
            ]
        )
        + "\n",
    )
    write(
        root / MAKEFILE_PATH,
        "\n".join(
            [
                "phase11-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase11.py",
                *(
                    f"\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file {marker}"
                    for marker in EXPECTED_PROOF_FANOUT_MARKERS
                ),
            ]
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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_shared_replay_counts_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        wrong_contract = tmpdir / "wrong_contract"
        shutil.copytree(fixture, wrong_contract, dirs_exist_ok=True)
        write(
            wrong_contract / CONTRACT_PATH,
            read_text(wrong_contract / CONTRACT_PATH).replace(
                "11 HVC current-head exact command markers",
                "9 HVC current-head exact command markers",
                1,
            ),
        )
        expect_failure(wrong_contract, "11 HVC current-head exact command markers")
        case_count += 1

        missing_designware_current_head_marker = tmpdir / "missing_designware_current_head_marker"
        shutil.copytree(fixture, missing_designware_current_head_marker, dirs_exist_ok=True)
        write(
            missing_designware_current_head_marker / CONTRACT_PATH,
            read_text(missing_designware_current_head_marker / CONTRACT_PATH).replace(
                "`Documentation/zigux/phase11-dw-wdt-survey.md`,",
                "",
                1,
            ),
        )
        expect_failure(
            missing_designware_current_head_marker,
            "`Documentation/zigux/phase11-dw-wdt-survey.md`,",
        )
        case_count += 1

        missing_validate_support_marker = tmpdir / "missing_validate_support_marker"
        shutil.copytree(fixture, missing_validate_support_marker, dirs_exist_ok=True)
        write(
            missing_validate_support_marker / CONTRACT_PATH,
            read_text(missing_validate_support_marker / CONTRACT_PATH).replace(
                "`scripts/zigux/check-phase11-validate-route-alignment.py`",
                "",
                1,
            ),
        )
        expect_failure(
            missing_validate_support_marker,
            "`scripts/zigux/check-phase11-validate-route-alignment.py`",
        )
        case_count += 1

        missing_contract_check = tmpdir / "missing_contract_check"
        shutil.copytree(fixture, missing_contract_check, dirs_exist_ok=True)
        write(
            missing_contract_check / CONTRACT_PATH,
            read_text(missing_contract_check / CONTRACT_PATH).replace(
                "python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py",
                "",
                1,
            ),
        )
        expect_failure(
            missing_contract_check,
            "python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py",
        )
        case_count += 1

        missing_focused_check = tmpdir / "missing_focused_check"
        shutil.copytree(fixture, missing_focused_check, dirs_exist_ok=True)
        write(
            missing_focused_check / CONTRACT_PATH,
            read_text(missing_focused_check / CONTRACT_PATH).replace(
                "python3 scripts/zigux/check-phase11-focused-direct-build-replays.py --self-test",
                "",
                1,
            ),
        )
        expect_failure(
            missing_focused_check,
            "python3 scripts/zigux/check-phase11-focused-direct-build-replays.py --self-test",
        )
        case_count += 1

        missing_focused_replay = tmpdir / "missing_focused_replay"
        shutil.copytree(fixture, missing_focused_replay, dirs_exist_ok=True)
        write(
            missing_focused_replay / CONTRACT_PATH,
            read_text(missing_focused_replay / CONTRACT_PATH).replace(
                "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
                "",
                1,
            ),
        )
        expect_failure(
            missing_focused_replay,
            "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
        )
        case_count += 1

        missing_proof_fanout_marker = tmpdir / "missing_proof_fanout_marker"
        shutil.copytree(fixture, missing_proof_fanout_marker, dirs_exist_ok=True)
        write(
            missing_proof_fanout_marker / CONTRACT_PATH,
            read_text(missing_proof_fanout_marker / CONTRACT_PATH).replace(
                "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
                "",
                1,
            ),
        )
        expect_failure(
            missing_proof_fanout_marker,
            "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
        )
        case_count += 1

        missing_remove_handoff_proof = tmpdir / "missing_remove_handoff_proof"
        shutil.copytree(fixture, missing_remove_handoff_proof, dirs_exist_ok=True)
        write(
            missing_remove_handoff_proof / CONTRACT_PATH,
            read_text(missing_remove_handoff_proof / CONTRACT_PATH).replace(
                "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
                "",
                1,
            ),
        )
        expect_failure(
            missing_remove_handoff_proof,
            "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
        )
        case_count += 1

        missing_workflow_route = tmpdir / "missing_workflow_route"
        shutil.copytree(fixture, missing_workflow_route, dirs_exist_ok=True)
        write(
            missing_workflow_route / WORKFLOW_PATH,
            read_text(missing_workflow_route / WORKFLOW_PATH).replace(
                "run: make -C zigux phase11-validate",
                "run: make -C zigux phase10-validate",
                1,
            ),
        )
        expect_failure(missing_workflow_route, "run: make -C zigux phase11-validate")
        case_count += 1

        missing_makefile_route = tmpdir / "missing_makefile_route"
        shutil.copytree(fixture, missing_makefile_route, dirs_exist_ok=True)
        write(
            missing_makefile_route / MAKEFILE_PATH,
            read_text(missing_makefile_route / MAKEFILE_PATH).replace(
                "phase11-validate:",
                "phase11-check:",
                1,
            ),
        )
        expect_failure(missing_makefile_route, "phase11-validate:")
        case_count += 1

        missing_makefile_proof = tmpdir / "missing_makefile_proof"
        shutil.copytree(fixture, missing_makefile_proof, dirs_exist_ok=True)
        write(
            missing_makefile_proof / MAKEFILE_PATH,
            read_text(missing_makefile_proof / MAKEFILE_PATH).replace(
                "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
                "",
                1,
            ),
        )
        expect_failure(
            missing_makefile_proof,
            "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
        )
        case_count += 1

        for label, replacement in (
            ("build_test_names", ["a", "b"]),
            ("shared_test_depend_steps", ["unexpected-step"]),
            ("dedicated_survey_replays", ["unexpected-survey"]),
            ("shared_adjunct_replays", ["a", "b"]),
            ("shared_adjunct_build_replays", ["a", "b"]),
            ("focused_direct_build_checks", ["python3 scripts/zigux/check-phase11-focused-direct-build-replays.py"]),
            ("focused_direct_build_replays", ["zigux/tests/phase11_hvc_modem_control_proof_build.zig"]),
        ):
            wrong_count = tmpdir / f"wrong_{label}"
            shutil.copytree(fixture, wrong_count, dirs_exist_ok=True)
            inventory = read_json(wrong_count / INVENTORY_PATH)
            inventory[label] = replacement
            write(wrong_count / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
            expect_failure(wrong_count, f"{label} count mismatch")
            case_count += 1

        wrong_inventory = tmpdir / "wrong_inventory"
        shutil.copytree(fixture, wrong_inventory, dirs_exist_ok=True)
        inventory = read_json(wrong_inventory / INVENTORY_PATH)
        inventory["exact_current_checks"] = inventory["exact_current_checks"][:-1]
        write(wrong_inventory / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_inventory, "exact_current_checks count mismatch")
        case_count += 1

        wrong_inventory_order = tmpdir / "wrong_inventory_order"
        shutil.copytree(fixture, wrong_inventory_order, dirs_exist_ok=True)
        inventory = read_json(wrong_inventory_order / INVENTORY_PATH)
        inventory["exact_current_checks"] = list(reversed(inventory["exact_current_checks"]))
        write(wrong_inventory_order / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_inventory_order, "exact_current_checks does not match")
        case_count += 1

        wrong_focused_checks = tmpdir / "wrong_focused_checks"
        shutil.copytree(fixture, wrong_focused_checks, dirs_exist_ok=True)
        inventory = read_json(wrong_focused_checks / INVENTORY_PATH)
        inventory["focused_direct_build_checks"] = list(reversed(inventory["focused_direct_build_checks"]))
        write(wrong_focused_checks / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_focused_checks, "focused_direct_build_checks does not match")
        case_count += 1

        print("PHASE11_SHARED_REPLAY_CONTRACT_COUNTS_SELF_TEST=pass")
        print(f"PHASE11_SHARED_REPLAY_CONTRACT_COUNTS_SELF_TEST_CASE_COUNT={case_count}")
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
        print(f"PHASE11_SHARED_REPLAY_CONTRACT_COUNTS=fail: {exc}")
        return 1

    print("PHASE11_SHARED_REPLAY_CONTRACT_COUNTS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
