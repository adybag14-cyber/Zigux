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

REQUIRED_MODULE_PATHS = {
    "gpio_wdt_module": "../../drivers/watchdog/gpio_wdt.zig",
    "bcm2835_wdt_verify_module": "../../drivers/watchdog/bcm2835_wdt_verify.zig",
    "dw_wdt_verify_module": "../../drivers/watchdog/dw_wdt_verify.zig",
    "hvc_console_module": "../../drivers/tty/hvc/hvc_console.zig",
    "hvc_console_verify_module": "../../drivers/tty/hvc/hvc_console_verify.zig",
    "phase11_hvc_cleanup_module": "phase11_hvc_cleanup.zig",
    "phase11_hvc_console_survey_module": "phase11_hvc_console_survey.zig",
    "phase11_uapi_header_parity_survey_module": "phase11_uapi_header_parity_survey.zig",
}

REQUIRED_IMPORT_TRIPLES = {
    ("phase11_gpio_wdt_module", "gpio_wdt", "gpio_wdt_module"),
    ("phase11_dw_wdt_registration_scaffold_module", "dw_wdt", "dw_wdt_module"),
    ("phase11_hvc_cleanup_module", "hvc_console", "hvc_console_module"),
    ("phase11_hvc_console_survey_module", "layout_assert", "layout_assert_module"),
    (
        "phase11_uapi_header_parity_survey_module",
        "layout_assert",
        "layout_assert_module",
    ),
}

REQUIRED_TEST_ROOT_MODULES = {
    "phase11-bcm2835-wdt-verify-tests": "bcm2835_wdt_verify_module",
    "phase11-dw-wdt-registration-scaffold-tests": "phase11_dw_wdt_registration_scaffold_module",
    "phase11-dw-wdt-verify-tests": "dw_wdt_verify_module",
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


def run_check(root: Path) -> None:
    inventory = read_json(root, FILES["inventory"])
    read_text(root, FILES["build_file"])

    build_test_names = expect_unique_strings("build_test_names", inventory.get("build_test_names"))
    for name in REQUIRED_BUILD_TEST_NAMES:
        if name not in build_test_names:
            raise CheckError(f"missing {name!r} in build_test_names")

    shared_steps = expect_unique_strings(
        "shared_test_depend_steps", inventory.get("shared_test_depend_steps")
    )
    for step in REQUIRED_SHARED_DEPEND_STEPS:
        if step not in shared_steps:
            raise CheckError(f"missing {step!r} in shared_test_depend_steps")
    if FORBIDDEN_SHARED_DEPEND_STEP in shared_steps:
        raise CheckError(
            f"forbidden dedicated survey step present in shared_test_depend_steps: {FORBIDDEN_SHARED_DEPEND_STEP}"
        )

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

    forbidden_markers = expect_unique_strings(
        "forbidden_markers", inventory.get("forbidden_markers")
    )
    marker = "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);"
    if marker not in forbidden_markers:
        raise CheckError(f"missing {marker!r} in forbidden_markers")

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
            {"module": "layout_assert_module", "path": "../helpers/layout_assert.zig"},
            {"module": "gpio_wdt_module", "path": "../../drivers/watchdog/gpio_wdt.zig"},
            {
                "module": "bcm2835_wdt_verify_module",
                "path": "../../drivers/watchdog/bcm2835_wdt_verify.zig",
            },
            {"module": "dw_wdt_module", "path": "../../drivers/watchdog/dw_wdt.zig"},
            {
                "module": "dw_wdt_verify_module",
                "path": "../../drivers/watchdog/dw_wdt_verify.zig",
            },
            {
                "module": "phase11_gpio_wdt_module",
                "path": "phase11_gpio_wdt.zig",
            },
            {
                "module": "phase11_dw_wdt_registration_scaffold_module",
                "path": "phase11_dw_wdt_registration_scaffold.zig",
            },
            {
                "module": "hvc_console_module",
                "path": "../../drivers/tty/hvc/hvc_console.zig",
            },
            {
                "module": "hvc_console_verify_module",
                "path": "../../drivers/tty/hvc/hvc_console_verify.zig",
            },
            {
                "module": "phase11_hvc_cleanup_module",
                "path": "phase11_hvc_cleanup.zig",
            },
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
                "module": "phase11_gpio_wdt_module",
                "import_name": "gpio_wdt",
                "imported_module": "gpio_wdt_module",
            },
            {
                "module": "phase11_dw_wdt_registration_scaffold_module",
                "import_name": "dw_wdt",
                "imported_module": "dw_wdt_module",
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
            {
                "test": "phase11-bcm2835-wdt-verify-tests",
                "root_module": "bcm2835_wdt_verify_module",
            },
            {
                "test": "phase11-dw-wdt-registration-scaffold-tests",
                "root_module": "phase11_dw_wdt_registration_scaffold_module",
            },
            {
                "test": "phase11-dw-wdt-verify-tests",
                "root_module": "dw_wdt_verify_module",
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
        "forbidden_markers": [
            "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
        ],
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
    write(root / FILES["build_file"], "const std = @import(\"std\");\n")
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

        expect_failure(
            rewrite_json("missing_build_name", lambda data: data["build_test_names"].remove("phase11-hvc-cleanup-tests")),
            "phase11-hvc-cleanup-tests",
        )
        expect_failure(
            rewrite_json(
                "wrong_module_path",
                lambda data: next(
                    entry.update({"path": "drivers/tty/hvc/hvc_console_verify.zig"})
                    for entry in data["module_root_source_files"]
                    if entry["module"] == "hvc_console_verify_module"
                ),
            ),
            "module_root_source_files mismatch for hvc_console_verify_module",
        )
        expect_failure(
            rewrite_json(
                "forbidden_shared_step",
                lambda data: data["shared_test_depend_steps"].append(FORBIDDEN_SHARED_DEPEND_STEP),
            ),
            FORBIDDEN_SHARED_DEPEND_STEP,
        )
        expect_failure(
            rewrite_json(
                "duplicate_build_name",
                lambda data: data["build_test_names"].append("phase11-hvc-cleanup-tests"),
            ),
            "duplicate entry in build_test_names",
        )

        marker_case = tmpdir / "missing_contract_marker"
        shutil.copytree(fixture, marker_case, dirs_exist_ok=True)
        marker = "`scripts/zigux/check-phase11-build-inventory.py`"
        write(
            marker_case / FILES["contract_note"],
            read_text(marker_case, FILES["contract_note"]).replace(marker, "", 1),
        )
        expect_failure(marker_case, marker)

        missing_build_case = tmpdir / "missing_build_file"
        shutil.copytree(fixture, missing_build_case, dirs_exist_ok=True)
        (missing_build_case / FILES["build_file"]).unlink()
        expect_failure(missing_build_case, FILES["build_file"])

        print("PHASE11_BUILD_INVENTORY_SELF_TEST=pass")
        print("PHASE11_BUILD_INVENTORY_SELF_TEST_CASE_COUNT=6")
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
