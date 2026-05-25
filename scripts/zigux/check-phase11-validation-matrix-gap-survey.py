#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

FILES = {
    "matrix_gap_note": "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
    "inventory": "zigux/tests/fixtures/phase11_build_inventory.json",
    "validate_checks": "zigux/tests/fixtures/phase11_validate_checks.json",
    "validate_phase11": "scripts/zigux/validate-phase11.py",
    "makefile": "zigux/Makefile",
}

EXPECTED_INVENTORY_LISTS = {
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
    "shared_adjunct_build_replays": [
        "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
        "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
        "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    ],
    "focused_direct_build_replays": [
        "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
        "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
    ],
    "deterministic_fixture_surfaces": [
        "zigux/tests/fixtures/phase11_build_inventory.json",
        "zigux/tests/fixtures/phase11_validate_checks.json",
        "zigux/tests/phase11_dw_wdt_manifest.json",
    ],
    "focused_teardown_failure_mode_builds": [
        "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
        "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
        "zigux/tests/phase11_dw_wdt_restart_build.zig",
        "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    ],
}

EXPECTED_INVENTORY_SCALARS = {
    "deterministic_tooling_lane": "P11-L07",
    "deterministic_golden_output_gap": "phase11-validate now carries the dedicated golden-output fixture roster `zigux/tests/fixtures/phase11_validate_checks.json` plus fail-closed `scripts/zigux/check-phase11-validate-check-roster.py` and `scripts/zigux/check-phase11-validate-route-alignment.py` guards; keep future deterministic output drift inside that validator packet",
}

SURVEY_MARKERS = (
    "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
    "shared packet lane: `P11-Y06`",
    "deterministic tooling survey lane: `P11-L07`",
    "Phase 11 still names `drivers/watchdog/gpio_wdt.c`, `drivers/watchdog/bcm2835_wdt.c`, `drivers/watchdog/dw_wdt.c`, and `drivers/tty/hvc/hvc_console.c` as the simple-production-driver anchors.",
    "Phase 11 still requires a hardware validation matrix together with teardown or failure-mode parity.",
    "Authenticated GitHub contents rereads in this run rematerialize the bcm2835, gpio watchdog, HVC console, and DesignWare driver-local Phase 11 matrix notes named by the roadmap on current `master`.",
    "The currently reread driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`.",
    "`zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/fixtures/phase11_validate_checks.json`, and `zigux/tests/phase11_dw_wdt_manifest.json` are the current machine-readable deterministic fixture surfaces inside the shared Phase 11 packet.",
    "The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`, `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`, `zigux/tests/phase11_dw_wdt_restart_build.zig`, and `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig` are the current focused teardown-or-failure-mode proof builds directly named by the shared packet.",
    "`make -C zigux phase11-validate` remains the returned shared validation route, and `scripts/zigux/validate-phase11.py` keeps the current shared packet build-proof-first.",
    "The shared Phase 11 packet now rematerializes a dedicated golden-output fixture roster through `zigux/tests/fixtures/phase11_validate_checks.json` plus fail-closed `scripts/zigux/check-phase11-validate-check-roster.py` and `scripts/zigux/check-phase11-validate-route-alignment.py` guards.",
    "It still does not rematerialize a refresh helper route or an artifact-diff-style deterministic output guard for the driver-local proof builds.",
    "`scripts/zigux/validate-phase11.py` and `make -C zigux phase11-validate` therefore stay build-proof-first rather than expected-output-refresh-first.",
    "That leaves a narrower roadmap-facing deterministic tooling gap: the repo can prove that the focused builds still compile and run, and it can exact-check the shared validate roster, but it still cannot refresh and diff shared golden outputs for the same bounded packet.",
)

REQUIRED_VALIDATE_PHASE11_MARKERS = (
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_dw_wdt_restart_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_modem_control_proof_build.zig")',
    '("zig", "build", "test", "--build-file", "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig")',
)

REQUIRED_MAKEFILE_MARKERS = (
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_dw_wdt_restart_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
)

REQUIRED_VALIDATE_CHECK_NAMES = (
    "phase11-validation-matrix-gap-survey-self-test",
    "phase11-validation-matrix-gap-survey",
)

REQUIRED_VALIDATE_CHECK_COMMANDS = (
    ["python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py", "--self-test"],
    ["python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py"],
)


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def read_json(root: Path, relative_path: str) -> dict[str, object]:
    try:
        value = json.loads(read_text(root, relative_path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {relative_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckError(f"expected object in {relative_path}")
    return value


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def require_text_markers(label: str, text: str, markers: tuple[str, ...]) -> None:
    normalized = normalize_whitespace(text)
    for marker in markers:
        if normalize_whitespace(marker) not in normalized:
            raise CheckError(f"missing marker in {label}: {marker}")


def expect_string_list(label: str, value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CheckError(f"expected string list for {label}")
    return list(value)


def run_check(root: Path) -> None:
    survey_text = read_text(root, FILES["matrix_gap_note"])
    require_text_markers("matrix_gap_note", survey_text, SURVEY_MARKERS)

    inventory = read_json(root, FILES["inventory"])
    for key, expected in EXPECTED_INVENTORY_LISTS.items():
        if expect_string_list(key, inventory.get(key)) != expected:
            raise CheckError(f"{key} does not match the current-head Phase 11 packet")
    for key, expected in EXPECTED_INVENTORY_SCALARS.items():
        if inventory.get(key) != expected:
            raise CheckError(f"{key} does not match the current-head Phase 11 packet")

    validate_phase11_text = read_text(root, FILES["validate_phase11"])
    require_text_markers("validate_phase11", validate_phase11_text, REQUIRED_VALIDATE_PHASE11_MARKERS)

    makefile_text = read_text(root, FILES["makefile"])
    require_text_markers("makefile", makefile_text, REQUIRED_MAKEFILE_MARKERS)

    validate_checks = read_json(root, FILES["validate_checks"])
    names = []
    commands = []
    exact_checks = validate_checks.get("exact_checks")
    if not isinstance(exact_checks, list) or any(not isinstance(item, dict) for item in exact_checks):
        raise CheckError("expected object list for exact_checks")
    for item in exact_checks:
        names.append(item.get("name"))
        commands.append(item.get("command"))
    for expected_name in REQUIRED_VALIDATE_CHECK_NAMES:
        if expected_name not in names:
            raise CheckError(f"missing exact_checks name in {FILES['validate_checks']}: {expected_name}")
    for expected_command in REQUIRED_VALIDATE_CHECK_COMMANDS:
        if expected_command not in commands:
            raise CheckError(
                f"missing exact_checks command in {FILES['validate_checks']}: {' '.join(expected_command)}"
            )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_inventory() -> dict[str, object]:
    return {
        "build_test_names": EXPECTED_INVENTORY_LISTS["build_test_names"],
        "shared_test_depend_steps": EXPECTED_INVENTORY_LISTS["shared_test_depend_steps"],
        "dedicated_survey_replays": EXPECTED_INVENTORY_LISTS["dedicated_survey_replays"],
        "shared_adjunct_replays": EXPECTED_INVENTORY_LISTS["shared_adjunct_replays"],
        "shared_adjunct_build_replays": EXPECTED_INVENTORY_LISTS["shared_adjunct_build_replays"],
        "focused_direct_build_replays": EXPECTED_INVENTORY_LISTS["focused_direct_build_replays"],
        "deterministic_fixture_surfaces": EXPECTED_INVENTORY_LISTS["deterministic_fixture_surfaces"],
        "focused_teardown_failure_mode_builds": EXPECTED_INVENTORY_LISTS["focused_teardown_failure_mode_builds"],
        "deterministic_tooling_lane": EXPECTED_INVENTORY_SCALARS["deterministic_tooling_lane"],
        "deterministic_golden_output_gap": EXPECTED_INVENTORY_SCALARS["deterministic_golden_output_gap"],
    }


def fixture_validate_checks() -> dict[str, object]:
    return {
        "exact_checks": [
            {
                "name": "phase11-validation-matrix-gap-survey-self-test",
                "command": ["python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py", "--self-test"],
            },
            {
                "name": "phase11-validation-matrix-gap-survey",
                "command": ["python", "scripts/zigux/check-phase11-validation-matrix-gap-survey.py"],
            },
        ]
    }


def remove_marker(text: str, marker: str) -> str:
    normalized = normalize_whitespace(marker)
    if normalized not in normalize_whitespace(text):
        raise AssertionError(marker)
    return text.replace(marker, "", 1)


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def build_fixture(root: Path, survey_text: str) -> None:
    write(root / FILES["matrix_gap_note"], survey_text)
    write(root / FILES["inventory"], json.dumps(fixture_inventory(), indent=2) + "\n")
    write(root / FILES["validate_checks"], json.dumps(fixture_validate_checks(), indent=2) + "\n")
    write(root / FILES["validate_phase11"], "\n".join(REQUIRED_VALIDATE_PHASE11_MARKERS) + "\n")
    write(root / FILES["makefile"], "\n".join(REQUIRED_MAKEFILE_MARKERS) + "\n")


def run_self_test() -> None:
    survey_text = read_text(ROOT, FILES["matrix_gap_note"])
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_matrix_gap_validation_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_fixture(fixture_root, survey_text)
        run_check(fixture_root)
        case_count = 1

        for marker in SURVEY_MARKERS[:7]:
            case_root = tmpdir / f"survey_{case_count}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES["matrix_gap_note"]
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            expect_failure(case_root, marker)
            case_count += 1

        inventory_root = tmpdir / "inventory"
        shutil.copytree(fixture_root, inventory_root, dirs_exist_ok=True)
        inventory = read_json(inventory_root, FILES["inventory"])
        inventory["deterministic_tooling_lane"] = "P11-L99"
        write(inventory_root / FILES["inventory"], json.dumps(inventory, indent=2) + "\n")
        expect_failure(inventory_root, "deterministic_tooling_lane does not match")
        case_count += 1

        inventory_list_root = tmpdir / "inventory_list"
        shutil.copytree(fixture_root, inventory_list_root, dirs_exist_ok=True)
        inventory = read_json(inventory_list_root, FILES["inventory"])
        inventory["deterministic_fixture_surfaces"] = inventory["deterministic_fixture_surfaces"][:-1]
        write(inventory_list_root / FILES["inventory"], json.dumps(inventory, indent=2) + "\n")
        expect_failure(inventory_list_root, "deterministic_fixture_surfaces does not match")
        case_count += 1

        validate_root = tmpdir / "validate"
        shutil.copytree(fixture_root, validate_root, dirs_exist_ok=True)
        path = validate_root / FILES["validate_phase11"]
        marker = REQUIRED_VALIDATE_PHASE11_MARKERS[0]
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
        expect_failure(validate_root, marker)
        case_count += 1

        makefile_root = tmpdir / "makefile"
        shutil.copytree(fixture_root, makefile_root, dirs_exist_ok=True)
        path = makefile_root / FILES["makefile"]
        marker = REQUIRED_MAKEFILE_MARKERS[0]
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
        expect_failure(makefile_root, marker)
        case_count += 1

        checks_root = tmpdir / "checks"
        shutil.copytree(fixture_root, checks_root, dirs_exist_ok=True)
        payload = read_json(checks_root, FILES["validate_checks"])
        payload["exact_checks"] = payload["exact_checks"][1:]
        write(checks_root / FILES["validate_checks"], json.dumps(payload, indent=2) + "\n")
        expect_failure(checks_root, "phase11-validation-matrix-gap-survey-self-test")
        case_count += 1

        print("PHASE11_MATRIX_GAP_SURVEY_CHECK=pass")
        print(f"PHASE11_MATRIX_GAP_SURVEY_SELF_TEST_CASE_COUNT={case_count}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE11_MATRIX_GAP_SURVEY_CHECK=fail: {exc}")
        return 1

    print("PHASE11_MATRIX_GAP_SURVEY_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
