#!/usr/bin/env python3
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

MANIFEST_PATH = Path("zigux/tests/fixtures/phase11_shared_tooling_manifest.json")
SURVEY_PATH = Path("Documentation/zigux/phase11-codegen-manifest-tooling-gap-survey.md")
VALIDATOR_PATH = Path("scripts/zigux/validate-phase11.py")
VALIDATE_FIXTURE_PATH = Path("zigux/tests/fixtures/phase11_validate_checks.json")

EXPECTED_MANIFEST = {
    "lane_key": "P11-L04",
    "phase": "Phase 11",
    "status": "shared_packet_aggregate_surface_materialized",
    "scope": "shared Phase 11 codegen and manifest tooling stale aggregate-manifest cleanup",
    "shared_docs": [
        "Documentation/zigux/phase11-shared-replay-contract.md",
        "Documentation/zigux/phase11-driver-lane-sequencing.md",
        "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
        "Documentation/zigux/phase11-watchdog-lifecycle-parity-gap.md",
        "Documentation/zigux/phase11-codegen-manifest-tooling-gap-survey.md",
    ],
    "shared_checkers": [
        "scripts/zigux/check-phase11-build-inventory.py",
        "scripts/zigux/check-phase11-validate-manifest-roster.py",
        "scripts/zigux/check-phase11-validate-check-roster.py",
        "scripts/zigux/check-phase11-validate-route-alignment.py",
        "scripts/zigux/check-phase11-focused-direct-build-replays.py",
        "scripts/zigux/check-phase11-shared-replay-contract-counts.py",
        "scripts/zigux/check-phase11-matrix-gap-survey.py",
        "scripts/zigux/check-phase11-validation-matrix-gap-survey.py",
        "scripts/zigux/check-phase11-watchdog-lifecycle-parity-gap.py",
        "scripts/zigux/check-phase11-header-boundary-packet.py",
        "scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
        "scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py",
        "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py",
        "scripts/zigux/check-phase11-hvc-current-head-manifest.py",
        "scripts/zigux/check-phase11-dw-wdt-teardown-packet.py",
        "scripts/zigux/check-phase11-dw-wdt-verify-alignment.py",
        "scripts/zigux/check-phase11-shared-tooling-manifest.py",
    ],
    "shared_routes": [
        "python3 scripts/zigux/validate-phase11.py",
        "make -C zigux phase11-validate",
    ],
    "proof_builds": [
        "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
        "zigux/tests/phase11_dw_wdt_build.zig",
        "zigux/tests/phase11_dw_wdt_restart_build.zig",
        "zigux/tests/phase11_dw_wdt_pm_build.zig",
        "zigux/tests/phase11_gpio_wdt_verify_helper_build.zig",
        "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
        "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
        "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
        "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
        "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
        "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
        "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
        "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
        "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
    ],
    "driver_local_matrices": [
        "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
        "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    ],
    "narrow_inventory_boundary": {
        "inventory_path": "zigux/tests/fixtures/phase11_build_inventory.json",
        "inventory_scope": "HVC current-head continuity packet",
        "aggregate_scope": "shared phase11-validate checker stack and proof fan-out",
    },
    "retired_shared_routes": [
        "make -C zigux phase11",
        "make -C zigux phase11-contract",
        "zigux/tests/phase11_build.zig",
    ],
}

REQUIRED_SURVEY_MARKERS = (
    "`PHASE11_TOOLING_GAP_STATUS=shared_packet_aggregate_surface_materialized`",
    "`scripts/zigux/check-phase11-shared-tooling-manifest.py`",
    "`zigux/tests/fixtures/phase11_shared_tooling_manifest.json`",
    "`scripts/zigux/check-phase11-watchdog-lifecycle-parity-gap.py`",
    "`scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py`",
    "`scripts/zigux/check-phase11-hvc-current-head-manifest.py`",
    "distinguishes the narrower `zigux/tests/fixtures/phase11_build_inventory.json` HVC continuity packet from the broader shared `phase11-validate` checker stack and proof fan-out",
    "`scripts/zigux/check-phase11-shared-tooling-manifest.py` is already wired into `scripts/zigux/validate-phase11.py`",
    "`zigux/tests/fixtures/phase11_validate_checks.json` records both the shared tooling-manifest self-test and live validator entries",
    "aggregate surface now also carries the shared watchdog lifecycle note plus the cleanup-prerequisite and current-head manifest guards that the validator route already ships",
)

FORBIDDEN_SURVEY_MARKERS = (
    "`PHASE11_TOOLING_GAP_STATUS=shared_packet_manifest_gap_open`",
    "there is no current aggregate manifest or generated summary surface",
    "wire `scripts/zigux/check-phase11-shared-tooling-manifest.py` into the shared `phase11-validate` route only after current-head rereads confirm the surrounding Phase 11 packet did not drift again",
)

REQUIRED_VALIDATOR_MARKERS = (
    'CheckSpec("phase11-shared-tooling-manifest-self-test", ("python", "scripts/zigux/check-phase11-shared-tooling-manifest.py", "--self-test"))',
    'CheckSpec("phase11-shared-tooling-manifest", ("python", "scripts/zigux/check-phase11-shared-tooling-manifest.py"))',
)

REQUIRED_VALIDATE_FIXTURE_MARKERS = (
    '"name": "phase11-shared-tooling-manifest-self-test"',
    '"command": ["python", "scripts/zigux/check-phase11-shared-tooling-manifest.py", "--self-test"]',
    '"name": "phase11-shared-tooling-manifest"',
    '"command": ["python", "scripts/zigux/check-phase11-shared-tooling-manifest.py"]',
)

EXPECTED_VALIDATE_FIXTURE_ENTRIES = (
    (
        "phase11-shared-tooling-manifest-self-test",
        ["python", "scripts/zigux/check-phase11-shared-tooling-manifest.py", "--self-test"],
    ),
    (
        "phase11-shared-tooling-manifest",
        ["python", "scripts/zigux/check-phase11-shared-tooling-manifest.py"],
    ),
)


class CheckError(RuntimeError):
    pass


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def read_json(root: Path, relative_path: Path) -> dict[str, object]:
    try:
        value = json.loads(read_text(root, relative_path))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {relative_path}: {exc}") from exc
    if not isinstance(value, dict):
        raise CheckError(f"expected object in {relative_path}")
    return value


def require_exact_list(label: str, actual: object, expected: list[str]) -> None:
    if not isinstance(actual, list) or any(not isinstance(item, str) for item in actual):
        raise CheckError(f"expected string list for {label}")
    if actual != expected:
        raise CheckError(f"{label} does not match the current Phase 11 shared tooling packet")
    if len(actual) != len(set(actual)):
        raise CheckError(f"duplicate entry in {label}")


def require_text_markers(label: str, text: str, markers: tuple[str, ...]) -> None:
    normalized = normalize_whitespace(text)
    for marker in markers:
        if normalize_whitespace(marker) not in normalized:
            raise CheckError(f"missing marker in {label}: {marker}")


def forbid_text_markers(label: str, text: str, markers: tuple[str, ...]) -> None:
    normalized = normalize_whitespace(text)
    for marker in markers:
        if normalize_whitespace(marker) in normalized:
            raise CheckError(f"forbidden marker in {label}: {marker}")


def require_existing_paths(root: Path, paths: list[str], label: str) -> None:
    for path in paths:
        if not (root / path).exists():
            raise CheckError(f"missing path from {label}: {path}")


def require_validate_fixture_entries(fixture: dict[str, object]) -> None:
    exact_checks = fixture.get("exact_checks")
    if not isinstance(exact_checks, list):
        raise CheckError("expected list for exact_checks")

    positions: list[int] = []
    for expected_name, expected_command in EXPECTED_VALIDATE_FIXTURE_ENTRIES:
        matching_positions = []
        same_name_count = 0
        for index, entry in enumerate(exact_checks):
            if not isinstance(entry, dict):
                raise CheckError("expected object entries in exact_checks")
            name = entry.get("name")
            command = entry.get("command")
            if name == expected_name:
                same_name_count += 1
                if command == expected_command:
                    matching_positions.append(index)
        if same_name_count != 1 or len(matching_positions) != 1:
            raise CheckError(f"validate fixture entry mismatch for {expected_name}")
        positions.append(matching_positions[0])

    if positions != sorted(positions):
        raise CheckError("validate fixture tooling-manifest entries are out of order")


def run_check(root: Path) -> None:
    manifest = read_json(root, MANIFEST_PATH)
    survey_text = read_text(root, SURVEY_PATH)
    validator_text = read_text(root, VALIDATOR_PATH)
    validate_fixture = read_json(root, VALIDATE_FIXTURE_PATH)
    validate_fixture_text = read_text(root, VALIDATE_FIXTURE_PATH)

    for key in ("lane_key", "phase", "status", "scope"):
        if manifest.get(key) != EXPECTED_MANIFEST[key]:
            raise CheckError(f"{key} does not match the current Phase 11 shared tooling packet")

    require_exact_list("shared_docs", manifest.get("shared_docs"), EXPECTED_MANIFEST["shared_docs"])
    require_exact_list("shared_checkers", manifest.get("shared_checkers"), EXPECTED_MANIFEST["shared_checkers"])
    require_exact_list("shared_routes", manifest.get("shared_routes"), EXPECTED_MANIFEST["shared_routes"])
    require_exact_list("proof_builds", manifest.get("proof_builds"), EXPECTED_MANIFEST["proof_builds"])
    require_exact_list(
        "driver_local_matrices",
        manifest.get("driver_local_matrices"),
        EXPECTED_MANIFEST["driver_local_matrices"],
    )
    require_exact_list(
        "retired_shared_routes",
        manifest.get("retired_shared_routes"),
        EXPECTED_MANIFEST["retired_shared_routes"],
    )

    if manifest.get("narrow_inventory_boundary") != EXPECTED_MANIFEST["narrow_inventory_boundary"]:
        raise CheckError("narrow_inventory_boundary does not match the current Phase 11 shared tooling packet")

    require_existing_paths(root, EXPECTED_MANIFEST["shared_docs"], "shared_docs")
    require_existing_paths(root, EXPECTED_MANIFEST["shared_checkers"], "shared_checkers")
    require_existing_paths(root, EXPECTED_MANIFEST["proof_builds"], "proof_builds")
    require_existing_paths(root, EXPECTED_MANIFEST["driver_local_matrices"], "driver_local_matrices")
    if not (root / EXPECTED_MANIFEST["narrow_inventory_boundary"]["inventory_path"]).exists():
        raise CheckError("missing narrow inventory path")

    require_text_markers("phase11-codegen-manifest-tooling-gap-survey.md", survey_text, REQUIRED_SURVEY_MARKERS)
    forbid_text_markers("phase11-codegen-manifest-tooling-gap-survey.md", survey_text, FORBIDDEN_SURVEY_MARKERS)
    require_text_markers("validate-phase11.py", validator_text, REQUIRED_VALIDATOR_MARKERS)
    require_text_markers("phase11_validate_checks.json", validate_fixture_text, REQUIRED_VALIDATE_FIXTURE_MARKERS)
    require_validate_fixture_entries(validate_fixture)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_validate_fixture(path: Path, exact_checks: list[dict[str, object]]) -> None:
    lines = ["{", '  "exact_checks": [']
    for index, entry in enumerate(exact_checks):
        suffix = "," if index + 1 < len(exact_checks) else ""
        lines.append(
            f'    {{"name": {json.dumps(entry["name"])}, "command": {json.dumps(entry["command"])}}}{suffix}'
        )
    lines.extend(["  ]", "}"])
    write(path, "\n".join(lines) + "\n")


def build_fixture(root: Path) -> None:
    write(root / MANIFEST_PATH, json.dumps(EXPECTED_MANIFEST, indent=2) + "\n")
    write(
        root / SURVEY_PATH,
        "\n".join(
            (
                "# Phase 11 Codegen and Manifest Tooling Gap Survey",
                "",
                "- `PHASE11_TOOLING_GAP_STATUS=shared_packet_aggregate_surface_materialized`",
                "- `scripts/zigux/check-phase11-shared-tooling-manifest.py`",
                "- `zigux/tests/fixtures/phase11_shared_tooling_manifest.json`",
                "- `scripts/zigux/check-phase11-watchdog-lifecycle-parity-gap.py`",
                "- `scripts/zigux/check-phase11-hvc-cleanup-prerequisite-packet.py`",
                "- `scripts/zigux/check-phase11-hvc-current-head-manifest.py`",
                "- distinguishes the narrower `zigux/tests/fixtures/phase11_build_inventory.json` HVC continuity packet from the broader shared `phase11-validate` checker stack and proof fan-out",
                "- `scripts/zigux/check-phase11-shared-tooling-manifest.py` is already wired into `scripts/zigux/validate-phase11.py`",
                "- `zigux/tests/fixtures/phase11_validate_checks.json` records both the shared tooling-manifest self-test and live validator entries`",
                "- aggregate surface now also carries the shared watchdog lifecycle note plus the cleanup-prerequisite and current-head manifest guards that the validator route already ships",
            )
        )
        + "\n",
    )
    write(
        root / VALIDATOR_PATH,
        "\n".join(
            (
                "CHECKS = (",
                '    CheckSpec("phase11-shared-tooling-manifest-self-test", ("python", "scripts/zigux/check-phase11-shared-tooling-manifest.py", "--self-test")),',
                '    CheckSpec("phase11-shared-tooling-manifest", ("python", "scripts/zigux/check-phase11-shared-tooling-manifest.py")),',
                ")",
            )
        )
        + "\n",
    )
    write_validate_fixture(
        root / VALIDATE_FIXTURE_PATH,
        [
            {
                "name": "phase11-shared-tooling-manifest-self-test",
                "command": ["python", "scripts/zigux/check-phase11-shared-tooling-manifest.py", "--self-test"],
            },
            {
                "name": "phase11-shared-tooling-manifest",
                "command": ["python", "scripts/zigux/check-phase11-shared-tooling-manifest.py"],
            },
        ],
    )
    for path in (
        *EXPECTED_MANIFEST["shared_docs"],
        *EXPECTED_MANIFEST["shared_checkers"],
        *EXPECTED_MANIFEST["proof_builds"],
        *EXPECTED_MANIFEST["driver_local_matrices"],
        EXPECTED_MANIFEST["narrow_inventory_boundary"]["inventory_path"],
    ):
        if Path(path) in (MANIFEST_PATH, SURVEY_PATH, VALIDATOR_PATH, VALIDATE_FIXTURE_PATH):
            continue
        write(root / path, f"fixture:{path}\n")


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_shared_tooling_manifest_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        stale_future_note = tmpdir / "stale_future_note"
        shutil.copytree(fixture, stale_future_note, dirs_exist_ok=True)
        path = stale_future_note / SURVEY_PATH
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\nwire `scripts/zigux/check-phase11-shared-tooling-manifest.py` into the shared `phase11-validate` route only after current-head rereads confirm the surrounding Phase 11 packet did not drift again\n",
            encoding="utf-8",
        )
        expect_failure(stale_future_note, "forbidden marker")
        case_count += 1

        missing_validator_entry = tmpdir / "missing_validator_entry"
        shutil.copytree(fixture, missing_validator_entry, dirs_exist_ok=True)
        path = missing_validator_entry / VALIDATOR_PATH
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                '    CheckSpec("phase11-shared-tooling-manifest", ("python", "scripts/zigux/check-phase11-shared-tooling-manifest.py")),\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(missing_validator_entry, 'missing marker in validate-phase11.py: CheckSpec("phase11-shared-tooling-manifest"')
        case_count += 1

        missing_fixture_entry = tmpdir / "missing_fixture_entry"
        shutil.copytree(fixture, missing_fixture_entry, dirs_exist_ok=True)
        path = missing_fixture_entry / VALIDATE_FIXTURE_PATH
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                '"name": "phase11-shared-tooling-manifest-self-test"',
                '"name": "phase11-other-check"',
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(missing_fixture_entry, 'missing marker in phase11_validate_checks.json: "name": "phase11-shared-tooling-manifest-self-test"')
        case_count += 1

        wrong_fixture_command = tmpdir / "wrong_fixture_command"
        shutil.copytree(fixture, wrong_fixture_command, dirs_exist_ok=True)
        payload = read_json(wrong_fixture_command, VALIDATE_FIXTURE_PATH)
        payload["exact_checks"][0]["command"] = ["python", "scripts/zigux/check-phase11-shared-tooling-manifest.py"]
        write_validate_fixture(wrong_fixture_command / VALIDATE_FIXTURE_PATH, payload["exact_checks"])
        expect_failure(wrong_fixture_command, 'missing marker in phase11_validate_checks.json: "command": ["python", "scripts/zigux/check-phase11-shared-tooling-manifest.py", "--self-test"]')
        case_count += 1

        duplicate_fixture_entry = tmpdir / "duplicate_fixture_entry"
        shutil.copytree(fixture, duplicate_fixture_entry, dirs_exist_ok=True)
        payload = read_json(duplicate_fixture_entry, VALIDATE_FIXTURE_PATH)
        payload["exact_checks"].append(
            {
                "name": "phase11-shared-tooling-manifest",
                "command": ["python", "scripts/zigux/check-phase11-shared-tooling-manifest.py"],
            }
        )
        write_validate_fixture(duplicate_fixture_entry / VALIDATE_FIXTURE_PATH, payload["exact_checks"])
        expect_failure(duplicate_fixture_entry, "validate fixture entry mismatch for phase11-shared-tooling-manifest")
        case_count += 1

        out_of_order_fixture_entries = tmpdir / "out_of_order_fixture_entries"
        shutil.copytree(fixture, out_of_order_fixture_entries, dirs_exist_ok=True)
        payload = read_json(out_of_order_fixture_entries, VALIDATE_FIXTURE_PATH)
        payload["exact_checks"] = list(reversed(payload["exact_checks"]))
        write_validate_fixture(out_of_order_fixture_entries / VALIDATE_FIXTURE_PATH, payload["exact_checks"])
        expect_failure(out_of_order_fixture_entries, "validate fixture tooling-manifest entries are out of order")
        case_count += 1

        missing_shared_packet_marker = tmpdir / "missing_shared_packet_marker"
        shutil.copytree(fixture, missing_shared_packet_marker, dirs_exist_ok=True)
        path = missing_shared_packet_marker / SURVEY_PATH
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "- `scripts/zigux/check-phase11-hvc-current-head-manifest.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(missing_shared_packet_marker, "`scripts/zigux/check-phase11-hvc-current-head-manifest.py`")
        case_count += 1

        stale_gap_claim = tmpdir / "stale_gap_claim"
        shutil.copytree(fixture, stale_gap_claim, dirs_exist_ok=True)
        path = stale_gap_claim / SURVEY_PATH
        path.write_text(
            path.read_text(encoding="utf-8") + "\nthere is no current aggregate manifest or generated summary surface\n",
            encoding="utf-8",
        )
        expect_failure(stale_gap_claim, "forbidden marker")
        case_count += 1

        print("PHASE11_SHARED_TOOLING_MANIFEST_SELF_TEST=pass")
        print(f"PHASE11_SHARED_TOOLING_MANIFEST_SELF_TEST_CASE_COUNT={case_count}")
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
        print(f"PHASE11_SHARED_TOOLING_MANIFEST=fail: {exc}")
        return 1

    print("PHASE11_SHARED_TOOLING_MANIFEST=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
