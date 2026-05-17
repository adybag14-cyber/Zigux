#!/usr/bin/env python3
"""Fail-close guard for the current-head Phase 11 HVC cleanup packet.

The current `master` branch keeps the HVC cleanup packet reviewable through the
survey note plus the shared Phase 11 build inventory. The direct HVC teardown,
matrix, verify, and helper files are still inventory-backed archival members, so
this checker must validate that bounded current-head truth instead of requiring
those missing files to exist locally.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[3]

SURVEY_PATH = Path("Documentation/zigux/phase11-hvc-console-survey.md")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")

SURVEY_MARKERS = (
    "shared Phase 11 inventory-backed continuity anchors `zigux/tests/fixtures/phase11_build_inventory.json` and `scripts/zigux/check-phase11-build-inventory.py`",
    "did not rematerialize `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`",
    "The direct driver, test, split-replay, dedicated-checker, and coupled-doc companions above should stay framed as inventory-backed archival packet members until a future reread materializes them again.",
    "That archived helper keeps sysrq toggle handoff, pending-dispatch separation, literal-byte fallback on non-kernel `^O`, and post-teardown unavailability explicit without claiming live sysrq execution.",
    "Those archival companions keep direct `hvc_console` replay, verify-side helper boundaries, bounded cleanup-time teardown checks, and the targetless notifier no-unregister edge visible beside the archival survey gate",
)

REQUIRED_BUILD_TEST_NAMES = (
    "phase11-hvc-console-tests",
    "phase11-hvc-console-verify-tests",
    "phase11-hvc-cleanup-tests",
    "phase11-hvc-console-survey-tests",
)

REQUIRED_SHARED_DEPEND_STEPS = (
    "run_phase11_hvc_console_tests",
    "run_hvc_console_verify_tests",
    "run_phase11_hvc_cleanup_tests",
)

REQUIRED_MODULE_PATHS = {
    "hvc_console_module": "../../drivers/tty/hvc/hvc_console.zig",
    "hvc_console_verify_module": "../../drivers/tty/hvc/hvc_console_verify.zig",
    "phase11_hvc_console_module": "phase11_hvc_console.zig",
    "phase11_hvc_cleanup_module": "phase11_hvc_cleanup.zig",
    "phase11_hvc_console_survey_module": "phase11_hvc_console_survey.zig",
}

REQUIRED_TEST_ROOT_MODULES = {
    "phase11-hvc-console-tests": "phase11_hvc_console_module",
    "phase11-hvc-console-verify-tests": "hvc_console_verify_module",
    "phase11-hvc-cleanup-tests": "phase11_hvc_cleanup_module",
    "phase11-hvc-console-survey-tests": "phase11_hvc_console_survey_module",
}

REQUIRED_REPLAY_MARKERS = {
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
    survey_text = read_text(root / SURVEY_PATH)
    for marker in SURVEY_MARKERS:
        if marker not in survey_text:
            raise CheckError(f"missing survey marker: {marker}")

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
        "test_root_modules": [
            {"test": test_name, "root_module": module}
            for test_name, module in REQUIRED_TEST_ROOT_MODULES.items()
        ],
        "dedicated_survey_replays": ["zigux/tests/phase11_hvc_console_survey.zig"],
        "shared_replay_markers": [
            {"path": path, "marker": marker}
            for path, marker in sorted(REQUIRED_REPLAY_MARKERS)
        ],
    }


def fixture_survey() -> str:
    return "\n".join(
        [
            "# Phase 11 HVC Console Survey",
            "",
            "* current `master` still keeps the HVC archival lane reviewable through this survey note together with the shared Phase 11 inventory-backed continuity anchors `zigux/tests/fixtures/phase11_build_inventory.json` and `scripts/zigux/check-phase11-build-inventory.py`",
            "* direct contents reads in this run did not rematerialize `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, or `scripts/zigux/check-phase11-hvc-survey-packet.py`, so keep those as inventory-backed archival packet members until a future reread confirms them again",
            "* The direct driver, test, split-replay, dedicated-checker, and coupled-doc companions above should stay framed as inventory-backed archival packet members until a future reread materializes them again.",
            "* That archived helper keeps sysrq toggle handoff, pending-dispatch separation, literal-byte fallback on non-kernel `^O`, and post-teardown unavailability explicit without claiming live sysrq execution.",
            "* Those archival companions keep direct `hvc_console` replay, verify-side helper boundaries, bounded cleanup-time teardown checks, and the targetless notifier no-unregister edge visible beside the archival survey gate without promoting the lane to live tty-driver registration, notifier callback execution, khvcd execution, live sysrq dispatch, or host-backed teardown parity.",
            "",
        ]
    )


def build_fixture(root: Path) -> None:
    write(root / SURVEY_PATH, fixture_survey())
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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_cleanup_current_head_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)
        case_count = 1

        missing_survey = tmpdir / "missing_survey_marker"
        shutil.copytree(fixture, missing_survey, dirs_exist_ok=True)
        write(
            missing_survey / SURVEY_PATH,
            read_text(missing_survey / SURVEY_PATH).replace(SURVEY_MARKERS[0], "", 1),
        )
        expect_failure(missing_survey, SURVEY_MARKERS[0])
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

        missing_dedicated_survey_replay = tmpdir / "missing_dedicated_survey_replay"
        shutil.copytree(fixture, missing_dedicated_survey_replay, dirs_exist_ok=True)
        inventory = read_json(missing_dedicated_survey_replay / INVENTORY_PATH)
        inventory["dedicated_survey_replays"].clear()
        write(
            missing_dedicated_survey_replay / INVENTORY_PATH,
            json.dumps(inventory, indent=2) + "\n",
        )
        expect_failure(
            missing_dedicated_survey_replay,
            "zigux/tests/phase11_hvc_console_survey.zig",
        )
        case_count += 1

        missing_replay_pair = tmpdir / "missing_replay_pair"
        shutil.copytree(fixture, missing_replay_pair, dirs_exist_ok=True)
        inventory = read_json(missing_replay_pair / INVENTORY_PATH)
        inventory["shared_replay_markers"] = inventory["shared_replay_markers"][:-1]
        write(missing_replay_pair / INVENTORY_PATH, json.dumps(inventory, indent=2) + "\n")
        expect_failure(missing_replay_pair, "missing shared replay marker pair")
        case_count += 1

        missing_inventory = tmpdir / "missing_inventory"
        shutil.copytree(fixture, missing_inventory, dirs_exist_ok=True)
        (missing_inventory / INVENTORY_PATH).unlink()
        expect_failure(missing_inventory, str(INVENTORY_PATH))
        case_count += 1

        print("PHASE11_HVC_CLEANUP_CURRENT_HEAD_SELF_TEST=pass")
        print(f"PHASE11_HVC_CLEANUP_CURRENT_HEAD_SELF_TEST_CASE_COUNT={case_count}")
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
        print(f"PHASE11_HVC_CLEANUP_CURRENT_HEAD=fail: {exc}")
        return 1

    print("PHASE11_HVC_CLEANUP_CURRENT_HEAD=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
