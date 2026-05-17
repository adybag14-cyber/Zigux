#!/usr/bin/env python3
"""Fail-closed checker for the current-head Phase 11 build-inventory packet."""

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

LANE_NOTE_PATH = Path("Documentation/zigux/phase11-driver-lane-sequencing.md")
MATRIX_SURVEY_PATH = Path("Documentation/zigux/phase11-validation-matrix-gap-survey.md")
HVC_SURVEY_PATH = Path("Documentation/zigux/phase11-hvc-console-survey.md")
HVC_COMPANION_PATH = Path(
    "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md"
)
BUILD_FILE_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_build.zig")
PROOF_PATHS = (
    Path("zigux/tests/phase11_hvc_export_surface_layout_proof.zig"),
    Path("zigux/tests/phase11_hvc_cleanup_packet_proof.zig"),
)
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")

LANE_NOTE_MARKERS = (
    "`Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
    "`Documentation/zigux/phase11-hvc-console-survey.md`",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "did not rematerialize `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-shared-summary-surfaces.py`, `zigux/tests/phase11_build.zig`, or `zigux/Makefile`",
)

MATRIX_SURVEY_MARKERS = (
    "`scripts/zigux/check-phase11-matrix-gap-survey.py`",
    "`Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`",
    "`Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`",
    "shared matrix packet is no longer an honest four-matrix direct-readback claim",
)

HVC_SURVEY_MARKERS = (
    "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
)

HVC_COMPANION_MARKERS = (
    "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
)

BUILD_FILE_MARKERS = (
    'phase11_hvc_cleanup_packet_proof.zig',
    'phase11-hvc-cleanup-packet-proof',
    'Run the focused Phase 11 HVC cleanup packet proof',
)

REQUIRED_BUILD_TEST_NAMES = (
    "phase11-gpio-wdt-tests",
    "phase11-gpio-wdt-survey-tests",
    "phase11-bcm2835-wdt-tests",
    "phase11-bcm2835-wdt-verify-tests",
    "phase11-bcm2835-wdt-survey-tests",
    "phase11-dw-wdt-tests",
    "phase11-dw-wdt-registration-scaffold-tests",
    "phase11-dw-wdt-verify-tests",
    "phase11-dw-wdt-survey-tests",
    "phase11-hvc-console-tests",
    "phase11-hvc-console-verify-tests",
    "phase11-hvc-cleanup-tests",
    "phase11-hvc-console-survey-tests",
    "phase11-uapi-header-parity-survey-tests",
)

REQUIRED_SHARED_DEPEND_STEPS = (
    "run_phase11_gpio_wdt_tests",
    "run_phase11_gpio_wdt_survey_tests",
    "run_phase11_bcm2835_wdt_tests",
    "run_bcm2835_wdt_verify_tests",
    "run_phase11_bcm2835_wdt_survey_tests",
    "run_phase11_dw_wdt_tests",
    "run_phase11_dw_wdt_registration_scaffold_tests",
    "run_dw_wdt_verify_tests",
    "run_phase11_dw_wdt_survey_tests",
    "run_phase11_uapi_header_parity_survey_tests",
    "run_phase11_hvc_console_tests",
    "run_hvc_console_verify_tests",
    "run_phase11_hvc_cleanup_tests",
)

REQUIRED_MODULE_PATHS = {
    "abi_bindings_module": "../bindings/abi.zig",
    "layout_assert_module": "../helpers/layout_assert.zig",
    "gpio_wdt_module": "../../drivers/watchdog/gpio_wdt.zig",
    "phase11_gpio_wdt_module": "phase11_gpio_wdt.zig",
    "phase11_gpio_wdt_survey_module": "phase11_gpio_wdt_survey.zig",
    "bcm2835_wdt_module": "../../drivers/watchdog/bcm2835_wdt.zig",
    "bcm2835_wdt_verify_module": "../../drivers/watchdog/bcm2835_wdt_verify.zig",
    "phase11_bcm2835_wdt_module": "phase11_bcm2835_wdt.zig",
    "phase11_bcm2835_wdt_survey_module": "phase11_bcm2835_wdt_survey.zig",
    "dw_wdt_module": "../../drivers/watchdog/dw_wdt.zig",
    "dw_wdt_verify_module": "../../drivers/watchdog/dw_wdt_verify.zig",
    "phase11_dw_wdt_module": "phase11_dw_wdt.zig",
    "phase11_dw_wdt_registration_scaffold_module": "phase11_dw_wdt_registration_scaffold.zig",
    "phase11_dw_wdt_survey_module": "phase11_dw_wdt_survey.zig",
    "hvc_console_module": "../../drivers/tty/hvc/hvc_console.zig",
    "hvc_console_verify_module": "../../drivers/tty/hvc/hvc_console_verify.zig",
    "phase11_hvc_console_module": "phase11_hvc_console.zig",
    "phase11_hvc_cleanup_module": "phase11_hvc_cleanup.zig",
    "phase11_hvc_console_survey_module": "phase11_hvc_console_survey.zig",
    "phase11_uapi_header_parity_survey_module": "phase11_uapi_header_parity_survey.zig",
}

REQUIRED_IMPORT_TRIPLES = {
    ("layout_assert_module", "abi_bindings", "abi_bindings_module"),
    ("phase11_gpio_wdt_module", "gpio_wdt", "gpio_wdt_module"),
    ("phase11_bcm2835_wdt_module", "bcm2835_wdt", "bcm2835_wdt_module"),
    ("phase11_dw_wdt_module", "dw_wdt", "dw_wdt_module"),
    ("phase11_dw_wdt_registration_scaffold_module", "dw_wdt", "dw_wdt_module"),
    ("phase11_hvc_console_module", "hvc_console", "hvc_console_module"),
    ("phase11_hvc_cleanup_module", "hvc_console", "hvc_console_module"),
    ("phase11_hvc_console_survey_module", "layout_assert", "layout_assert_module"),
    (
        "phase11_uapi_header_parity_survey_module",
        "layout_assert",
        "layout_assert_module",
    ),
}

REQUIRED_TEST_ROOT_MODULES = {
    "phase11-gpio-wdt-tests": "phase11_gpio_wdt_module",
    "phase11-gpio-wdt-survey-tests": "phase11_gpio_wdt_survey_module",
    "phase11-bcm2835-wdt-tests": "phase11_bcm2835_wdt_module",
    "phase11-bcm2835-wdt-verify-tests": "bcm2835_wdt_verify_module",
    "phase11-bcm2835-wdt-survey-tests": "phase11_bcm2835_wdt_survey_module",
    "phase11-dw-wdt-tests": "phase11_dw_wdt_module",
    "phase11-dw-wdt-registration-scaffold-tests": "phase11_dw_wdt_registration_scaffold_module",
    "phase11-dw-wdt-verify-tests": "dw_wdt_verify_module",
    "phase11-dw-wdt-survey-tests": "phase11_dw_wdt_survey_module",
    "phase11-hvc-console-tests": "phase11_hvc_console_module",
    "phase11-hvc-console-verify-tests": "hvc_console_verify_module",
    "phase11-hvc-cleanup-tests": "phase11_hvc_cleanup_module",
    "phase11-hvc-console-survey-tests": "phase11_hvc_console_survey_module",
    "phase11-uapi-header-parity-survey-tests": "phase11_uapi_header_parity_survey_module",
}

REQUIRED_REPLAY_MARKERS = {
    (
        "zigux/tests/phase11_dw_wdt_suspend_resume.zig",
        " try std.testing.expect(summary.resume_preserves_timeout_programming);",
    ),
    (
        "zigux/tests/phase11_dw_wdt_remove_idle_split.zig",
        " try std.testing.expect(reset_available_summary.remove_clears_interrupt_status);",
    ),
    (
        "zigux/tests/phase11_hvc_console_modem_control_split.zig",
        " try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",
    ),
    (
        "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
        " try std.testing.expect(dispatch.invokes_sysrq_handler);",
    ),
}


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


def expect_markers(path: Path, markers: tuple[str, ...]) -> None:
    normalized_text = normalize_whitespace(read_text(path))
    for marker in markers:
        if normalize_whitespace(marker) not in normalized_text:
            raise CheckError(f"missing marker in {path}: {marker}")


def expect_string_list(label: str, value: object) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise CheckError(f"expected string list for {label}")
    if len(value) != len(set(value)):
        raise CheckError(f"duplicate entry in {label}")
    return list(value)


def expect_object_list(label: str, value: object) -> list[dict[str, object]]:
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise CheckError(f"expected object list for {label}")
    return list(value)


def mapping_from_entries(
    entries: object,
    key_field: str,
    value_field: str,
    label: str,
) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for entry in expect_object_list(label, entries):
        key = entry.get(key_field)
        value = entry.get(value_field)
        if not isinstance(key, str) or not isinstance(value, str):
            raise CheckError(f"invalid entry in {label}")
        mapping[key] = value
    return mapping


def run_check(root: Path) -> None:
    expect_markers(root / LANE_NOTE_PATH, LANE_NOTE_MARKERS)
    expect_markers(root / MATRIX_SURVEY_PATH, MATRIX_SURVEY_MARKERS)
    expect_markers(root / HVC_SURVEY_PATH, HVC_SURVEY_MARKERS)
    expect_markers(root / HVC_COMPANION_PATH, HVC_COMPANION_MARKERS)
    expect_markers(root / BUILD_FILE_PATH, BUILD_FILE_MARKERS)

    for proof_path in PROOF_PATHS:
        read_text(root / proof_path)

    inventory = read_json(root / INVENTORY_PATH)

    build_test_names = expect_string_list("build_test_names", inventory.get("build_test_names"))
    for name in REQUIRED_BUILD_TEST_NAMES:
        if name not in build_test_names:
            raise CheckError(f"missing build_test_names entry: {name}")

    shared_steps = expect_string_list(
        "shared_test_depend_steps",
        inventory.get("shared_test_depend_steps"),
    )
    for step in REQUIRED_SHARED_DEPEND_STEPS:
        if step not in shared_steps:
            raise CheckError(f"missing shared_test_depend_steps entry: {step}")

    module_paths = mapping_from_entries(
        inventory.get("module_root_source_files"),
        "module",
        "path",
        "module_root_source_files",
    )
    for module, path in REQUIRED_MODULE_PATHS.items():
        if module_paths.get(module) != path:
            raise CheckError(f"module_root_source_files mismatch for {module}")

    imports = {
        (
            entry.get("module"),
            entry.get("import_name"),
            entry.get("imported_module"),
        )
        for entry in expect_object_list("module_imports", inventory.get("module_imports"))
    }
    for triple in REQUIRED_IMPORT_TRIPLES:
        if triple not in imports:
            raise CheckError(f"missing module import triple: {triple!r}")

    test_root_modules = mapping_from_entries(
        inventory.get("test_root_modules"),
        "test",
        "root_module",
        "test_root_modules",
    )
    for test_name, module in REQUIRED_TEST_ROOT_MODULES.items():
        if test_root_modules.get(test_name) != module:
            raise CheckError(f"test_root_modules mismatch for {test_name}")

    dedicated_survey_replays = expect_string_list(
        "dedicated_survey_replays",
        inventory.get("dedicated_survey_replays"),
    )
    if "zigux/tests/phase11_hvc_console_survey.zig" not in dedicated_survey_replays:
        raise CheckError(
            "missing dedicated_survey_replays entry: zigux/tests/phase11_hvc_console_survey.zig"
        )

    if expect_string_list("shared_split_replays", inventory.get("shared_split_replays")):
        raise CheckError("expected shared_split_replays to stay empty")
    if expect_string_list("shared_adjunct_replays", inventory.get("shared_adjunct_replays")):
        raise CheckError("expected shared_adjunct_replays to stay empty")

    replay_pairs = {
        (entry.get("path"), entry.get("marker"))
        for entry in expect_object_list("shared_replay_markers", inventory.get("shared_replay_markers"))
    }
    for pair in REQUIRED_REPLAY_MARKERS:
        if pair not in replay_pairs:
            raise CheckError(f"missing shared replay marker pair: {pair!r}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def fixture_inventory() -> dict[str, object]:
    return {
        "build_test_names": list(REQUIRED_BUILD_TEST_NAMES),
        "shared_test_depend_steps": list(REQUIRED_SHARED_DEPEND_STEPS),
        "module_root_source_files": [
            {"module": module, "path": path}
            for module, path in REQUIRED_MODULE_PATHS.items()
        ],
        "module_imports": [
            {
                "module": module,
                "import_name": import_name,
                "imported_module": imported_module,
            }
            for module, import_name, imported_module in sorted(REQUIRED_IMPORT_TRIPLES)
        ],
        "test_root_modules": [
            {"test": test_name, "root_module": module}
            for test_name, module in REQUIRED_TEST_ROOT_MODULES.items()
        ],
        "dedicated_survey_replays": ["zigux/tests/phase11_hvc_console_survey.zig"],
        "shared_split_replays": [],
        "shared_adjunct_replays": [],
        "shared_replay_markers": [
            {"path": path, "marker": marker}
            for path, marker in sorted(REQUIRED_REPLAY_MARKERS)
        ],
    }


FIXTURE_LANE_NOTE = """# Phase 11 Driver Lane Sequencing

- shared sequencing lane keeps `Documentation/zigux/phase11-validation-matrix-gap-survey.md` and `Documentation/zigux/phase11-hvc-console-survey.md` explicit beside `scripts/zigux/check-phase11-build-inventory.py` and `zigux/tests/fixtures/phase11_build_inventory.json`
- current direct rereads did not rematerialize `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `scripts/zigux/check-phase11-shared-replay-contract.py`, `scripts/zigux/check-phase11-shared-summary-surfaces.py`, `zigux/tests/phase11_build.zig`, or `zigux/Makefile`
"""

FIXTURE_MATRIX_SURVEY = """# Phase 11 Validation Matrix Gap Survey

- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`
- `Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`
- shared matrix packet is no longer an honest four-matrix direct-readback claim
"""

FIXTURE_HVC_SURVEY = """# Phase 11 HVC Console Survey

- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
"""

FIXTURE_HVC_COMPANION = """# Phase 11 HVC Cleanup Alignment Current-Head Companion

- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
- `zigux/tests/fixtures/phase11_build_inventory.json`
- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
"""

FIXTURE_BUILD_FILE = """const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const proof_module = b.createModule(.{
        .root_source_file = b.path("phase11_hvc_cleanup_packet_proof.zig"),
        .target = target,
        .optimize = optimize,
    });

    const proof_tests = b.addTest(.{
        .name = "phase11-hvc-cleanup-packet-proof",
        .root_module = proof_module,
    });
    const run_proof_tests = b.addRunArtifact(proof_tests);

    const test_step = b.step("test", "Run the focused Phase 11 HVC cleanup packet proof");
    test_step.dependOn(&run_proof_tests.step);
}
"""


def build_fixture(root: Path) -> None:
    write(root / LANE_NOTE_PATH, FIXTURE_LANE_NOTE)
    write(root / MATRIX_SURVEY_PATH, FIXTURE_MATRIX_SURVEY)
    write(root / HVC_SURVEY_PATH, FIXTURE_HVC_SURVEY)
    write(root / HVC_COMPANION_PATH, FIXTURE_HVC_COMPANION)
    write(root / BUILD_FILE_PATH, FIXTURE_BUILD_FILE)
    for proof_path in PROOF_PATHS:
        write(root / proof_path, "test {}\n")
    write(root / INVENTORY_PATH, json.dumps(fixture_inventory(), indent=2) + "\n")


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_build_inventory_current_head_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        missing_lane_marker = tmpdir / "missing_lane_marker"
        shutil.copytree(fixture, missing_lane_marker, dirs_exist_ok=True)
        write(
            missing_lane_marker / LANE_NOTE_PATH,
            read_text(missing_lane_marker / LANE_NOTE_PATH).replace(
                "`scripts/zigux/check-phase11-build-inventory.py`",
                "",
                1,
            ),
        )
        expect_failure(missing_lane_marker, "`scripts/zigux/check-phase11-build-inventory.py`")
        case_count += 1

        missing_build_marker = tmpdir / "missing_build_marker"
        shutil.copytree(fixture, missing_build_marker, dirs_exist_ok=True)
        write(
            missing_build_marker / BUILD_FILE_PATH,
            read_text(missing_build_marker / BUILD_FILE_PATH).replace(
                "phase11-hvc-cleanup-packet-proof",
                "",
                1,
            ),
        )
        expect_failure(missing_build_marker, "phase11-hvc-cleanup-packet-proof")
        case_count += 1

        missing_build_name = tmpdir / "missing_build_name"
        shutil.copytree(fixture, missing_build_name, dirs_exist_ok=True)
        inventory = read_json(missing_build_name / INVENTORY_PATH)
        inventory["build_test_names"].remove("phase11-hvc-cleanup-tests")
        write(missing_build_name / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(missing_build_name, "phase11-hvc-cleanup-tests")
        case_count += 1

        missing_shared_step = tmpdir / "missing_shared_step"
        shutil.copytree(fixture, missing_shared_step, dirs_exist_ok=True)
        inventory = read_json(missing_shared_step / INVENTORY_PATH)
        inventory["shared_test_depend_steps"].remove("run_hvc_console_verify_tests")
        write(missing_shared_step / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(missing_shared_step, "run_hvc_console_verify_tests")
        case_count += 1

        wrong_module_path = tmpdir / "wrong_module_path"
        shutil.copytree(fixture, wrong_module_path, dirs_exist_ok=True)
        inventory = read_json(wrong_module_path / INVENTORY_PATH)
        for entry in inventory["module_root_source_files"]:
            if entry["module"] == "hvc_console_verify_module":
                entry["path"] = "../../drivers/tty/hvc/hvc_console.zig"
                break
        write(wrong_module_path / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_module_path, "module_root_source_files mismatch for hvc_console_verify_module")
        case_count += 1

        missing_import = tmpdir / "missing_import"
        shutil.copytree(fixture, missing_import, dirs_exist_ok=True)
        inventory = read_json(missing_import / INVENTORY_PATH)
        inventory["module_imports"] = [
            entry
            for entry in inventory["module_imports"]
            if not (
                entry["module"] == "phase11_hvc_cleanup_module"
                and entry["import_name"] == "hvc_console"
                and entry["imported_module"] == "hvc_console_module"
            )
        ]
        write(missing_import / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(missing_import, "('phase11_hvc_cleanup_module', 'hvc_console', 'hvc_console_module')")
        case_count += 1

        wrong_root_module = tmpdir / "wrong_root_module"
        shutil.copytree(fixture, wrong_root_module, dirs_exist_ok=True)
        inventory = read_json(wrong_root_module / INVENTORY_PATH)
        for entry in inventory["test_root_modules"]:
            if entry["test"] == "phase11-hvc-cleanup-tests":
                entry["root_module"] = "phase11_hvc_console_module"
                break
        write(wrong_root_module / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(wrong_root_module, "test_root_modules mismatch for phase11-hvc-cleanup-tests")
        case_count += 1

        missing_replay_pair = tmpdir / "missing_replay_pair"
        shutil.copytree(fixture, missing_replay_pair, dirs_exist_ok=True)
        inventory = read_json(missing_replay_pair / INVENTORY_PATH)
        inventory["shared_replay_markers"] = inventory["shared_replay_markers"][:-1]
        write(missing_replay_pair / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(missing_replay_pair, "missing shared replay marker pair")
        case_count += 1

        missing_proof = tmpdir / "missing_proof"
        shutil.copytree(fixture, missing_proof, dirs_exist_ok=True)
        (missing_proof / PROOF_PATHS[1]).unlink()
        expect_failure(missing_proof, str(PROOF_PATHS[1]))
        case_count += 1

        print("PHASE11_BUILD_INVENTORY_SELF_TEST=pass")
        print(f"PHASE11_BUILD_INVENTORY_SELF_TEST_CASE_COUNT={case_count}")
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
        print(f"PHASE11_BUILD_INVENTORY=fail: {exc}")
        return 1

    print("PHASE11_BUILD_INVENTORY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
