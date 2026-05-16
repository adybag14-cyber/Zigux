#!/usr/bin/env python3
"""Fail-closed checker for the shared Phase 11 build-inventory packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

FILES = {
    "inventory": "zigux/tests/fixtures/phase11_build_inventory.json",
    "build_file": "zigux/tests/phase11_build.zig",
    "contract_note": "Documentation/zigux/phase11-shared-replay-contract.md",
    "closure_note": "Documentation/zigux/phase11-closure-note.md",
    "lane_note": "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "scripts_root": "scripts/zigux/README.md",
    "shared_contract_checker": "scripts/zigux/check-phase11-shared-replay-contract.py",
    "shared_summary_checker": "scripts/zigux/check-phase11-shared-summary-surfaces.py",
    "makefile": "zigux/Makefile",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
}

REQUIRED_BUILD_TEST_NAMES = [
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
]

REQUIRED_SHARED_DEPEND_STEPS = [
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
]

FORBIDDEN_SHARED_DEPEND_STEP = "run_phase11_hvc_console_survey_tests"
FORBIDDEN_BUILD_FILE_MARKER = (
    "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);"
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

TEXT_MARKERS = {
    "contract_note": [
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
        "`zigux/tests/phase11_build.zig`",
    ],
    "closure_note": [
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
        "`make -C zigux phase11-contract`",
    ],
    "lane_note": [
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json` anchor",
        "`make -C zigux phase11-contract`",
    ],
    "scripts_root": [
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
        "`zig build test --build-file zigux/tests/phase11_build.zig --summary all`",
    ],
    "shared_contract_checker": [
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
    ],
    "shared_summary_checker": [
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
    ],
    "makefile": [
        "PHONY += phase11-contract phase11-test phase11-hvc-survey phase11",
        "phase11-contract:",
        "phase11: phase11-contract phase11-test phase11-hvc-survey",
    ],
    "workflow": [
        "- name: Self-test Phase 11 shared replay contract checker",
        "- name: Self-test Phase 11 shared summary-surfaces checker",
        "- name: Run Phase 11 shared replay contract checker",
        "- name: Check Phase 11 shared summary surfaces",
        "- name: Run Phase 11 watchdog and console tests",
        "run: zig build test --build-file zigux/tests/phase11_build.zig --summary all",
        "- name: Run dedicated Phase 11 hvc survey replay",
    ],
}


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


def expect_markers(label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {label}: {marker}")


def expect_unique_strings(label: str, values: object) -> list[str]:
    if not isinstance(values, list) or any(not isinstance(v, str) for v in values):
        raise CheckError(f"expected string list for {label}")
    if len(values) != len(set(values)):
        raise CheckError(f"duplicate entry in {label}")
    return values


def expect_objects(label: str, values: object) -> list[dict[str, object]]:
    if not isinstance(values, list) or any(not isinstance(v, dict) for v in values):
        raise CheckError(f"expected object list for {label}")
    return values


def mapping_from_entries(values: object, key_field: str, value_field: str, label: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for entry in expect_objects(label, values):
        key = entry.get(key_field)
        value = entry.get(value_field)
        if not isinstance(key, str) or not isinstance(value, str):
            raise CheckError(f"invalid entry in {label}")
        mapping[key] = value
    return mapping


def expect_build_file_marker(build_text: str, marker: str, label: str) -> None:
    if marker not in build_text:
        raise CheckError(f"missing {label} in build_file: {marker}")


def build_file_fixture_text() -> str:
    lines = ['const std = @import("std");']
    for path in REQUIRED_MODULE_PATHS.values():
        lines.append(f'// "{path}"')
    for name in REQUIRED_BUILD_TEST_NAMES:
        lines.append(f'// "{name}"')
    for module in REQUIRED_TEST_ROOT_MODULES.values():
        lines.append(f"// .root_module = {module}")
    for step in REQUIRED_SHARED_DEPEND_STEPS:
        lines.append(f"const {step} = b.addRunArtifact(undefined);")
    lines.append(FORBIDDEN_BUILD_FILE_MARKER)
    return "\n".join(lines) + "\n"


def run_check(root: Path) -> None:
    inventory = read_json(root, FILES["inventory"])
    build_text = read_text(root, FILES["build_file"])

    build_test_names = expect_unique_strings("build_test_names", inventory.get("build_test_names"))
    for name in REQUIRED_BUILD_TEST_NAMES:
        if name not in build_test_names:
            raise CheckError(f"missing {name!r} in build_test_names")
        expect_build_file_marker(build_text, f'"{name}"', "build test name")

    shared_steps = expect_unique_strings(
        "shared_test_depend_steps", inventory.get("shared_test_depend_steps")
    )
    for step in REQUIRED_SHARED_DEPEND_STEPS:
        if step not in shared_steps:
            raise CheckError(f"missing {step!r} in shared_test_depend_steps")
        expect_build_file_marker(
            build_text, f"const {step} = b.addRunArtifact(", "shared depend step"
        )
    if FORBIDDEN_SHARED_DEPEND_STEP in shared_steps:
        raise CheckError(
            f"forbidden dedicated survey step present in shared_test_depend_steps: {FORBIDDEN_SHARED_DEPEND_STEP}"
        )
    expect_build_file_marker(build_text, FORBIDDEN_BUILD_FILE_MARKER, "forbidden marker")

    module_paths = mapping_from_entries(
        inventory.get("module_root_source_files"),
        "module",
        "path",
        "module_root_source_files",
    )
    for module, path in REQUIRED_MODULE_PATHS.items():
        if module_paths.get(module) != path:
            raise CheckError(f"module_root_source_files mismatch for {module}")
        expect_build_file_marker(build_text, f'"{path}"', "module path")

    imports = {
        (
            entry.get("module"),
            entry.get("import_name"),
            entry.get("imported_module"),
        )
        for entry in expect_objects("module_imports", inventory.get("module_imports"))
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
        expect_build_file_marker(build_text, f".root_module = {module}", "root module")

    forbidden_markers = expect_unique_strings(
        "forbidden_markers", inventory.get("forbidden_markers")
    )
    if FORBIDDEN_BUILD_FILE_MARKER not in forbidden_markers:
        raise CheckError(f"missing {FORBIDDEN_BUILD_FILE_MARKER!r} in forbidden_markers")

    dedicated_survey_replays = expect_unique_strings(
        "dedicated_survey_replays", inventory.get("dedicated_survey_replays")
    )
    required_dedicated = "zigux/tests/phase11_hvc_console_survey.zig"
    if required_dedicated not in dedicated_survey_replays:
        raise CheckError(f"missing {required_dedicated!r} in dedicated_survey_replays")

    if expect_unique_strings("shared_split_replays", inventory.get("shared_split_replays")):
        raise CheckError("expected shared_split_replays to stay empty")
    if expect_unique_strings("shared_adjunct_replays", inventory.get("shared_adjunct_replays")):
        raise CheckError("expected shared_adjunct_replays to stay empty")

    replay_pairs = {
        (entry.get("path"), entry.get("marker"))
        for entry in expect_objects("shared_replay_markers", inventory.get("shared_replay_markers"))
    }
    for pair in REQUIRED_REPLAY_MARKERS:
        if pair not in replay_pairs:
            raise CheckError(f"missing shared replay marker pair: {pair!r}")

    for label, markers in TEXT_MARKERS.items():
        expect_markers(label, read_text(root, FILES[label]), markers)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_inventory_fixture() -> dict[str, object]:
    return {
        "build_test_names": REQUIRED_BUILD_TEST_NAMES,
        "shared_test_depend_steps": REQUIRED_SHARED_DEPEND_STEPS,
        "module_root_source_files": [
            {"module": "abi_bindings_module", "path": "../bindings/abi.zig"},
            {"module": "layout_assert_module", "path": "../helpers/layout_assert.zig"},
            {"module": "gpio_wdt_module", "path": "../../drivers/watchdog/gpio_wdt.zig"},
            {"module": "phase11_gpio_wdt_module", "path": "phase11_gpio_wdt.zig"},
            {"module": "phase11_gpio_wdt_survey_module", "path": "phase11_gpio_wdt_survey.zig"},
            {"module": "bcm2835_wdt_module", "path": "../../drivers/watchdog/bcm2835_wdt.zig"},
            {
                "module": "bcm2835_wdt_verify_module",
                "path": "../../drivers/watchdog/bcm2835_wdt_verify.zig",
            },
            {"module": "phase11_bcm2835_wdt_module", "path": "phase11_bcm2835_wdt.zig"},
            {
                "module": "phase11_bcm2835_wdt_survey_module",
                "path": "phase11_bcm2835_wdt_survey.zig",
            },
            {"module": "dw_wdt_module", "path": "../../drivers/watchdog/dw_wdt.zig"},
            {
                "module": "dw_wdt_verify_module",
                "path": "../../drivers/watchdog/dw_wdt_verify.zig",
            },
            {"module": "phase11_dw_wdt_module", "path": "phase11_dw_wdt.zig"},
            {
                "module": "phase11_dw_wdt_registration_scaffold_module",
                "path": "phase11_dw_wdt_registration_scaffold.zig",
            },
            {
                "module": "phase11_dw_wdt_survey_module",
                "path": "phase11_dw_wdt_survey.zig",
            },
            {
                "module": "hvc_console_module",
                "path": "../../drivers/tty/hvc/hvc_console.zig",
            },
            {
                "module": "hvc_console_verify_module",
                "path": "../../drivers/tty/hvc/hvc_console_verify.zig",
            },
            {"module": "phase11_hvc_console_module", "path": "phase11_hvc_console.zig"},
            {"module": "phase11_hvc_cleanup_module", "path": "phase11_hvc_cleanup.zig"},
            {
                "module": "phase11_hvc_console_survey_module",
                "path": "phase11_hvc_console_survey.zig",
            },
            {
                "module": "phase11_uapi_header_parity_survey_module",
                "path": "phase11_uapi_header_parity_survey.zig",
            },
        ],
        "module_imports": [
            {
                "module": "layout_assert_module",
                "import_name": "abi_bindings",
                "imported_module": "abi_bindings_module",
            },
            {
                "module": "phase11_gpio_wdt_module",
                "import_name": "gpio_wdt",
                "imported_module": "gpio_wdt_module",
            },
            {
                "module": "phase11_bcm2835_wdt_module",
                "import_name": "bcm2835_wdt",
                "imported_module": "bcm2835_wdt_module",
            },
            {
                "module": "phase11_dw_wdt_module",
                "import_name": "dw_wdt",
                "imported_module": "dw_wdt_module",
            },
            {
                "module": "phase11_dw_wdt_registration_scaffold_module",
                "import_name": "dw_wdt",
                "imported_module": "dw_wdt_module",
            },
            {
                "module": "phase11_hvc_console_module",
                "import_name": "hvc_console",
                "imported_module": "hvc_console_module",
            },
            {
                "module": "phase11_hvc_cleanup_module",
                "import_name": "hvc_console",
                "imported_module": "hvc_console_module",
            },
            {
                "module": "phase11_hvc_console_survey_module",
                "import_name": "layout_assert",
                "imported_module": "layout_assert_module",
            },
            {
                "module": "phase11_uapi_header_parity_survey_module",
                "import_name": "layout_assert",
                "imported_module": "layout_assert_module",
            },
        ],
        "test_root_modules": [
            {"test": "phase11-gpio-wdt-tests", "root_module": "phase11_gpio_wdt_module"},
            {
                "test": "phase11-gpio-wdt-survey-tests",
                "root_module": "phase11_gpio_wdt_survey_module",
            },
            {
                "test": "phase11-bcm2835-wdt-tests",
                "root_module": "phase11_bcm2835_wdt_module",
            },
            {
                "test": "phase11-bcm2835-wdt-verify-tests",
                "root_module": "bcm2835_wdt_verify_module",
            },
            {
                "test": "phase11-bcm2835-wdt-survey-tests",
                "root_module": "phase11_bcm2835_wdt_survey_module",
            },
            {"test": "phase11-dw-wdt-tests", "root_module": "phase11_dw_wdt_module"},
            {
                "test": "phase11-dw-wdt-registration-scaffold-tests",
                "root_module": "phase11_dw_wdt_registration_scaffold_module",
            },
            {
                "test": "phase11-dw-wdt-verify-tests",
                "root_module": "dw_wdt_verify_module",
            },
            {
                "test": "phase11-dw-wdt-survey-tests",
                "root_module": "phase11_dw_wdt_survey_module",
            },
            {
                "test": "phase11-hvc-console-tests",
                "root_module": "phase11_hvc_console_module",
            },
            {
                "test": "phase11-hvc-console-verify-tests",
                "root_module": "hvc_console_verify_module",
            },
            {
                "test": "phase11-hvc-cleanup-tests",
                "root_module": "phase11_hvc_cleanup_module",
            },
            {
                "test": "phase11-hvc-console-survey-tests",
                "root_module": "phase11_hvc_console_survey_module",
            },
            {
                "test": "phase11-uapi-header-parity-survey-tests",
                "root_module": "phase11_uapi_header_parity_survey_module",
            },
        ],
        "forbidden_markers": [FORBIDDEN_BUILD_FILE_MARKER],
        "dedicated_survey_replays": ["zigux/tests/phase11_hvc_console_survey.zig"],
        "shared_split_replays": [],
        "shared_adjunct_replays": [],
        "shared_replay_markers": [
            {
                "path": "zigux/tests/phase11_dw_wdt_suspend_resume.zig",
                "marker": " try std.testing.expect(summary.resume_preserves_timeout_programming);",
            },
            {
                "path": "zigux/tests/phase11_dw_wdt_remove_idle_split.zig",
                "marker": " try std.testing.expect(reset_available_summary.remove_clears_interrupt_status);",
            },
            {
                "path": "zigux/tests/phase11_hvc_console_modem_control_split.zig",
                "marker": " try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);",
            },
            {
                "path": "zigux/tests/phase11_hvc_console_poll_retry_split.zig",
                "marker": " try std.testing.expect(dispatch.invokes_sysrq_handler);",
            },
        ],
    }


def build_fixture(root: Path) -> None:
    write(root / FILES["inventory"], json.dumps(build_inventory_fixture(), indent=2) + "\n")
    write(root / FILES["build_file"], build_file_fixture_text())
    for label, markers in TEXT_MARKERS.items():
        write(root / FILES[label], "\n".join(markers) + "\n")


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_build_inventory_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        def rewrite_json(case: str, mutate) -> Path:
            root = tmpdir / case
            shutil.copytree(fixture, root, dirs_exist_ok=True)
            data = json.loads((root / FILES["inventory"]).read_text(encoding="utf-8"))
            mutate(data)
            write(root / FILES["inventory"], json.dumps(data, indent=2) + "\n")
            return root

        def rewrite_text_case(case: str, label: str, marker: str) -> Path:
            root = tmpdir / case
            shutil.copytree(fixture, root, dirs_exist_ok=True)
            relative_path = FILES[label]
            write(
                root / relative_path,
                read_text(root, relative_path).replace(marker, "", 1),
            )
            return root

        base_json_cases = [
            (
                "missing_build_name",
                lambda data: data["build_test_names"].remove("phase11-hvc-cleanup-tests"),
                "phase11-hvc-cleanup-tests",
            ),
            (
                "wrong_module_path",
                lambda data: next(
                    entry.update({"path": "drivers/tty/hvc/hvc_console_verify.zig"})
                    for entry in data["module_root_source_files"]
                    if entry["module"] == "hvc_console_verify_module"
                ),
                "module_root_source_files mismatch for hvc_console_verify_module",
            ),
            (
                "wrong_gpio_survey_path",
                lambda data: next(
                    entry.update({"path": "phase11_gpio_wdt.zig"})
                    for entry in data["module_root_source_files"]
                    if entry["module"] == "phase11_gpio_wdt_survey_module"
                ),
                "module_root_source_files mismatch for phase11_gpio_wdt_survey_module",
            ),
            (
                "wrong_dw_wdt_survey_path",
                lambda data: next(
                    entry.update({"path": "phase11_dw_wdt_registration_scaffold.zig"})
                    for entry in data["module_root_source_files"]
                    if entry["module"] == "phase11_dw_wdt_survey_module"
                ),
                "module_root_source_files mismatch for phase11_dw_wdt_survey_module",
            ),
            (
                "missing_abi_bindings_import",
                lambda data: data["module_imports"].remove({
                    "module": "layout_assert_module",
                    "import_name": "abi_bindings",
                    "imported_module": "abi_bindings_module",
                }),
                "('layout_assert_module', 'abi_bindings', 'abi_bindings_module')",
            ),
            (
                "wrong_hvc_console_root_module",
                lambda data: next(
                    entry.update({"root_module": "phase11_hvc_cleanup_module"})
                    for entry in data["test_root_modules"]
                    if entry["test"] == "phase11-hvc-console-tests"
                ),
                "test_root_modules mismatch for phase11-hvc-console-tests",
            ),
            (
                "missing_hvc_verify_depend_step",
                lambda data: data["shared_test_depend_steps"].remove("run_hvc_console_verify_tests"),
                "run_hvc_console_verify_tests",
            ),
            (
                "wrong_hvc_verify_module_path",
                lambda data: next(
                    entry.update({"path": "../../drivers/tty/hvc/hvc_console.zig"})
                    for entry in data["module_root_source_files"]
                    if entry["module"] == "hvc_console_verify_module"
                ),
                "module_root_source_files mismatch for hvc_console_verify_module",
            ),
            (
                "wrong_hvc_verify_root_module",
                lambda data: next(
                    entry.update({"root_module": "phase11_hvc_console_module"})
                    for entry in data["test_root_modules"]
                    if entry["test"] == "phase11-hvc-console-verify-tests"
                ),
                "test_root_modules mismatch for phase11-hvc-console-verify-tests",
            ),
            (
                "wrong_dw_wdt_survey_root_module",
                lambda data: next(
                    entry.update({"root_module": "phase11_dw_wdt_registration_scaffold_module"})
                    for entry in data["test_root_modules"]
                    if entry["test"] == "phase11-dw-wdt-survey-tests"
                ),
                "test_root_modules mismatch for phase11-dw-wdt-survey-tests",
            ),
            (
                "forbidden_shared_step",
                lambda data: data["shared_test_depend_steps"].append(FORBIDDEN_SHARED_DEPEND_STEP),
                FORBIDDEN_SHARED_DEPEND_STEP,
            ),
            (
                "duplicate_build_name",
                lambda data: data["build_test_names"].append("phase11-hvc-cleanup-tests"),
                "duplicate entry in build_test_names",
            ),
            (
                "missing_forbidden_marker",
                lambda data: data["forbidden_markers"].clear(),
                FORBIDDEN_BUILD_FILE_MARKER,
            ),
            (
                "missing_dedicated_survey_replay",
                lambda data: data["dedicated_survey_replays"].clear(),
                "zigux/tests/phase11_hvc_console_survey.zig",
            ),
            (
                "shared_split_replays_not_empty",
                lambda data: data["shared_split_replays"].append("zigux/tests/phase11_hvc_console_poll_retry_split.zig"),
                "expected shared_split_replays to stay empty",
            ),
            (
                "shared_adjunct_replays_not_empty",
                lambda data: data["shared_adjunct_replays"].append("zigux/tests/phase11_hvc_console_modem_control_split.zig"),
                "expected shared_adjunct_replays to stay empty",
            ),
        ]
        for case_name, mutate, fragment in base_json_cases:
            expect_failure(rewrite_json(case_name, mutate), fragment)

        replay_pair_cases = sorted(REQUIRED_REPLAY_MARKERS)
        for idx, pair in enumerate(replay_pair_cases, start=1):

            def drop_pair(data, pair=pair):
                data["shared_replay_markers"] = [
                    entry
                    for entry in data["shared_replay_markers"]
                    if (entry.get("path"), entry.get("marker")) != pair
                ]

            expect_failure(
                rewrite_json(f"missing_replay_pair_{idx}", drop_pair),
                f"missing shared replay marker pair: {pair!r}",
            )

        text_marker_cases = [
            (label, marker)
            for label, markers in TEXT_MARKERS.items()
            for marker in markers
        ]
        for idx, (label, marker) in enumerate(text_marker_cases, start=1):
            expect_failure(
                rewrite_text_case(f"missing_text_marker_{idx}", label, marker),
                marker,
            )

        build_marker_cases = [
            ('"phase11-dw-wdt-survey-tests"', '"phase11-dw-wdt-survey-tests"'),
            ("const run_phase11_dw_wdt_registration_scaffold_tests = b.addRunArtifact(", "run_phase11_dw_wdt_registration_scaffold_tests"),
            ("const run_phase11_hvc_console_tests = b.addRunArtifact(", "run_phase11_hvc_console_tests"),
            ("const run_phase11_hvc_cleanup_tests = b.addRunArtifact(", "run_phase11_hvc_cleanup_tests"),
            ('"../../drivers/watchdog/dw_wdt_verify.zig"', "../../drivers/watchdog/dw_wdt_verify.zig"),
            (".root_module = phase11_dw_wdt_survey_module", "phase11_dw_wdt_survey_module"),
            (FORBIDDEN_BUILD_FILE_MARKER, FORBIDDEN_BUILD_FILE_MARKER),
        ]
        for idx, (marker, fragment) in enumerate(build_marker_cases, start=1):
            case_root = tmpdir / f"missing_build_marker_{idx}"
            shutil.copytree(fixture, case_root, dirs_exist_ok=True)
            build_path = case_root / FILES["build_file"]
            write(
                build_path,
                build_path.read_text(encoding="utf-8").replace(marker, "", 1),
            )
            expect_failure(case_root, fragment)

        missing_build_case = tmpdir / "missing_build_file"
        shutil.copytree(fixture, missing_build_case, dirs_exist_ok=True)
        (missing_build_case / FILES["build_file"]).unlink()
        expect_failure(missing_build_case, FILES["build_file"])

        case_count = (
            len(base_json_cases)
            + len(replay_pair_cases)
            + len(text_marker_cases)
            + len(build_marker_cases)
            + 1
        )
        print("PHASE11_BUILD_INVENTORY_SELF_TEST=pass")
        print(f"PHASE11_BUILD_INVENTORY_SELF_TEST_CASE_COUNT={case_count}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    try:
        run_check(Path(args.root))
    except CheckError as exc:
        print(f"PHASE11_BUILD_INVENTORY=fail: {exc}")
        return 1

    print("PHASE11_BUILD_INVENTORY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
