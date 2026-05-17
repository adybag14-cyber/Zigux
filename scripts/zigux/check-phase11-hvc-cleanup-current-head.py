#!/usr/bin/env python3
"""Fail-close guard for the current-head Phase 11 HVC cleanup packet.

The current `master` branch keeps the HVC cleanup packet reviewable through the
survey note, the cleanup-alignment companion, the verify-helper boundary note,
the shared Phase 11 build inventory, the direct HVC starter-depth packet that
current readback now materializes again, and the focused HVC cleanup proof
shards. This checker therefore validates the current-head wording that
explicitly names both the smaller continuity packet and the returned direct HVC
packet without widening into live tty or hypervisor execution claims.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[3]

SURVEY_PATH = Path("Documentation/zigux/phase11-hvc-console-survey.md")
COMPANION_PATH = Path("Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md")
VERIFY_HELPER_PATH = Path("Documentation/zigux/phase11-hvc-verify-helper-boundary.md")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
CLEANUP_PROOF_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_proof.zig")
CLEANUP_BUILD_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_build.zig")

SURVEY_MARKERS = (
    "current `master` still keeps the HVC lane reviewable through this survey note,",
    "public current-head readback in this lane also reconfirmed",
    "Treat the current bounded HVC continuity packet on `master` as the shared",
    "The direct HVC packet is again current-head readback evidence in this lane, so",
    "The roadmap destination family and the bounded simple-driver support packet are",
)

COMPANION_MARKERS = (
    "`PHASE11_STATUS=current_head_companion_landed`",
    "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
    "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "Keep those paths framed as archival packet vocabulary rather than current-head direct-readback evidence until a future reread proves they returned.",
)

VERIFY_HELPER_MARKERS = (
    "`drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove handoff explicit without implying live `hvc_remove()` execution.",
    "`drivers/tty/hvc/hvc_console_verify.zig` keeps the remove handoff explicit when tty teardown outlives console binding, preserving hangup-driven teardown without implying live `hvc_remove()` execution.",
    "`error.NotifierDispatchRequiresTtyRegistration` keeps notifier prerequisite failures explicit instead of implying sysrq-triggered notifier dispatch can occur before tty registration.",
    "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.",
    "the literal-fallback helpers keep both the sanitized targetless sysrq path and the non-kernel sysrq literal fallback explicit without promoting the lane to live sysrq execution.",
)

CLEANUP_PROOF_MARKERS = (
    'test "phase11 hvc cleanup packet proof keeps cleanup replay markers explicit" {',
    'try expectContains(cleanup_replay, "test \\\"phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable\\\" {");',
    'try expectContains(cleanup_companion, "phase11 hvc cleanup");',
    'test "phase11 hvc cleanup packet proof keeps teardown notes aligned with the landed cleanup handoff" {',
    'try expectContains(teardown_note, "deferred final release explicit");',
)

CLEANUP_BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_cleanup_packet_proof.zig"),',
    '.name = "phase11-hvc-cleanup-packet-proof",',
    'const test_step = b.step("test", "Run the focused Phase 11 HVC cleanup packet proof");',
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

    companion_text = read_text(root / COMPANION_PATH)
    for marker in COMPANION_MARKERS:
        if marker not in companion_text:
            raise CheckError(f"missing cleanup-companion marker: {marker}")

    verify_helper_text = read_text(root / VERIFY_HELPER_PATH)
    for marker in VERIFY_HELPER_MARKERS:
        if marker not in verify_helper_text:
            raise CheckError(f"missing verify-helper marker: {marker}")

    cleanup_proof_text = read_text(root / CLEANUP_PROOF_PATH)
    for marker in CLEANUP_PROOF_MARKERS:
        if marker not in cleanup_proof_text:
            raise CheckError(f"missing cleanup-proof marker: {marker}")

    cleanup_build_text = read_text(root / CLEANUP_BUILD_PATH)
    for marker in CLEANUP_BUILD_MARKERS:
        if marker not in cleanup_build_text:
            raise CheckError(f"missing cleanup-build marker: {marker}")

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
            "This note keeps the bounded Phase 11 `hvc_console` packet truthful on current `master`.",
            "The original archival landing happened on `P11-L13`, while the currently coupled",
            "continuity remains parked under `P11-L16`.",
            "",
            "## Status",
            "",
            "* current `master` still keeps the HVC lane reviewable through this survey note,",
            "  `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`,",
            "  `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`,",
            "  `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`,",
            "  `zigux/tests/fixtures/phase11_build_inventory.json`,",
            "  `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`,",
            "  `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, and",
            "  `zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
            "* public current-head readback in this lane also reconfirmed",
            "  `drivers/tty/hvc/hvc_console.zig`, `drivers/tty/hvc/hvc_console_verify.zig`,",
            "  `drivers/tty/hvc/hvc_console_sysrq.zig`, `zigux/tests/phase11_hvc_console.zig`,",
            "  `zigux/tests/phase11_hvc_cleanup.zig`,",
            "  `zigux/tests/phase11_hvc_console_survey.zig`,",
            "  `zigux/tests/phase11_hvc_console_manifest.json`,",
            "  `zigux/tests/phase11_hvc_console_modem_control_split.zig`,",
            "  `zigux/tests/phase11_hvc_console_poll_retry_split.zig`,",
            "  `Documentation/zigux/phase11-hvc-console-slice.md`,",
            "  `Documentation/zigux/phase11-hvc-console-teardown-note.md`,",
            "  `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and",
            "  `scripts/zigux/check-phase11-hvc-survey-packet.py` as the bounded",
            "  starter-depth packet that closes the Phase 11 simple-driver roadmap gap",
            "  without claiming live tty or hypervisor execution",
            "",
            "## Current-Head Continuity Packet",
            "",
            "Treat the current bounded HVC continuity packet on `master` as the shared",
            "inventory-backed and proof-backed packet below:",
            "",
            "- `Documentation/zigux/phase11-hvc-console-survey.md`",
            "- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
            "- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
            "- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
            "- `zigux/tests/fixtures/phase11_build_inventory.json`",
            "- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
            "- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
            "- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
            "",
            "## Current-Head Starter Packet",
            "",
            "The direct HVC packet is again current-head readback evidence in this lane, so",
            "keep the bounded starter, helper, replay, split, teardown, validation, and",
            "survey paths below tied directly to the roadmap-facing simple-driver packet:",
            "",
            "- `drivers/tty/hvc/hvc_console.zig`",
            "- `drivers/tty/hvc/hvc_console_verify.zig`",
            "- `drivers/tty/hvc/hvc_console_sysrq.zig`",
            "- `zigux/tests/phase11_hvc_console.zig`",
            "- `zigux/tests/phase11_hvc_cleanup.zig`",
            "- `zigux/tests/phase11_hvc_console_survey.zig`",
            "- `zigux/tests/phase11_hvc_console_manifest.json`",
            "- `zigux/tests/phase11_hvc_console_modem_control_split.zig`",
            "- `zigux/tests/phase11_hvc_console_poll_retry_split.zig`",
            "- `Documentation/zigux/phase11-hvc-console-slice.md`",
            "- `Documentation/zigux/phase11-hvc-console-teardown-note.md`",
            "- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
            "- `scripts/zigux/check-phase11-hvc-survey-packet.py`",
            "- `make -C zigux phase11-hvc-survey`",
            "",
            "## Bounded Meaning",
            "",
            "The roadmap destination family and the bounded simple-driver support packet are",
            "now directly readable on current `master`, so the remaining same-lane work is",
            "execution-facing follow-through rather than a missing simple-driver starter or a",
            "missing survey-backed validation packet.",
            "",
        ]
    )


def fixture_companion() -> str:
    return "\n".join(
        [
            "# Phase 11 HVC Cleanup Alignment Current-Head Companion",
            "",
            "- `PHASE11_STATUS=current_head_companion_landed`",
            "- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
            "- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
            "- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
            "- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
            "Keep those paths framed as archival packet vocabulary rather than current-head direct-readback evidence until a future reread proves they returned.",
            "",
        ]
    )


def fixture_verify_helper() -> str:
    return "\n".join(
        [
            "# Phase 11 HVC Verify Helper Boundary",
            "",
            "This note records the direct helper-facing failure-mode packet already landed in `drivers/tty/hvc/hvc_console_verify.zig`.",
            "",
            "## Verify Helper Coverage",
            "",
            "- `drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove handoff explicit without implying live `hvc_remove()` execution.",
            "- `drivers/tty/hvc/hvc_console_verify.zig` keeps the remove handoff explicit when tty teardown outlives console binding, preserving hangup-driven teardown without implying live `hvc_remove()` execution.",
            "- `error.NotifierDispatchRequiresTtyRegistration` keeps notifier prerequisite failures explicit instead of implying sysrq-triggered notifier dispatch can occur before tty registration.",
            "- `NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.",
            "- the literal-fallback helpers keep both the sanitized targetless sysrq path and the non-kernel sysrq literal fallback explicit without promoting the lane to live sysrq execution.",
            "",
        ]
    )


def fixture_cleanup_proof() -> str:
    return "\n".join(
        [
            'test "phase11 hvc cleanup packet proof keeps cleanup replay markers explicit" {',
            'try expectContains(cleanup_replay, "test \\\"phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable\\\" {");',
            'try expectContains(cleanup_companion, "phase11 hvc cleanup");',
            'test "phase11 hvc cleanup packet proof keeps teardown notes aligned with the landed cleanup handoff" {',
            'try expectContains(teardown_note, "deferred final release explicit");',
            "",
        ]
    )


def fixture_cleanup_build() -> str:
    return "\n".join(
        [
            '.root_source_file = b.path("phase11_hvc_cleanup_packet_proof.zig"),',
            '.name = "phase11-hvc-cleanup-packet-proof",',
            'const test_step = b.step("test", "Run the focused Phase 11 HVC cleanup packet proof");',
            "",
        ]
    )


def build_fixture(root: Path) -> None:
    write(root / SURVEY_PATH, fixture_survey())
    write(root / COMPANION_PATH, fixture_companion())
    write(root / VERIFY_HELPER_PATH, fixture_verify_helper())
    write(root / INVENTORY_PATH, json.dumps(fixture_inventory(), indent=2) + "\n")
    write(root / CLEANUP_PROOF_PATH, fixture_cleanup_proof())
    write(root / CLEANUP_BUILD_PATH, fixture_cleanup_build())


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

        missing_companion = tmpdir / "missing_companion_marker"
        shutil.copytree(fixture, missing_companion, dirs_exist_ok=True)
        write(
            missing_companion / COMPANION_PATH,
            read_text(missing_companion / COMPANION_PATH).replace(COMPANION_MARKERS[3], "", 1),
        )
        expect_failure(missing_companion, COMPANION_MARKERS[3])
        case_count += 1

        missing_verify_helper = tmpdir / "missing_verify_helper_marker"
        shutil.copytree(fixture, missing_verify_helper, dirs_exist_ok=True)
        write(
            missing_verify_helper / VERIFY_HELPER_PATH,
            read_text(missing_verify_helper / VERIFY_HELPER_PATH).replace(
                VERIFY_HELPER_MARKERS[1],
                "",
                1,
            ),
        )
        expect_failure(missing_verify_helper, VERIFY_HELPER_MARKERS[1])
        case_count += 1

        missing_cleanup_proof = tmpdir / "missing_cleanup_proof_marker"
        shutil.copytree(fixture, missing_cleanup_proof, dirs_exist_ok=True)
        write(
            missing_cleanup_proof / CLEANUP_PROOF_PATH,
            read_text(missing_cleanup_proof / CLEANUP_PROOF_PATH).replace(
                CLEANUP_PROOF_MARKERS[4],
                "",
                1,
            ),
        )
        expect_failure(missing_cleanup_proof, CLEANUP_PROOF_MARKERS[4])
        case_count += 1

        missing_cleanup_build = tmpdir / "missing_cleanup_build_marker"
        shutil.copytree(fixture, missing_cleanup_build, dirs_exist_ok=True)
        write(
            missing_cleanup_build / CLEANUP_BUILD_PATH,
            read_text(missing_cleanup_build / CLEANUP_BUILD_PATH).replace(
                CLEANUP_BUILD_MARKERS[2],
                "",
                1,
            ),
        )
        expect_failure(missing_cleanup_build, CLEANUP_BUILD_MARKERS[2])
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
