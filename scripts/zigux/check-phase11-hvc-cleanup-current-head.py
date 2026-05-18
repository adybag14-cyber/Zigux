#!/usr/bin/env python3
"""Fail-close guard for the current-head Phase 11 HVC cleanup packet.

The current `master` branch keeps the HVC cleanup packet reviewable through the
survey note, the cleanup-alignment companion, the verify-helper boundary note,
the shared Phase 11 build inventory, and the focused HVC cleanup proof shards.
This checker therefore validates wording that keeps the smaller continuity
packet explicit while treating the older starter-depth HVC packet and the
dedicated survey-checker path as survey-recorded or repo-reality-gap evidence
until direct readback proves they returned again.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


_SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = _SELF_PATH.parents[3] if len(_SELF_PATH.parents) > 3 else _SELF_PATH.parent

SURVEY_PATH = Path("Documentation/zigux/phase11-hvc-console-survey.md")
COMPANION_PATH = Path(
    "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md"
)
VERIFY_HELPER_PATH = Path("Documentation/zigux/phase11-hvc-verify-helper-boundary.md")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")
EXPORT_PROOF_PATH = Path("zigux/tests/phase11_hvc_export_surface_layout_proof.zig")
HV_OPS_PROOF_PATH = Path("zigux/tests/phase11_hvc_hv_ops_layout_proof.zig")
HV_OPS_BUILD_PATH = Path("zigux/tests/phase11_hvc_hv_ops_layout_build.zig")
CLEANUP_PROOF_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_proof.zig")
CLEANUP_BUILD_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_build.zig")

SURVEY_MARKERS = (
    "current `master` still keeps the HVC lane reviewable through this survey note,",
    "current direct contents reads in this lane still do not rematerialize",
    "current direct contents reads do rematerialize",
    "shared matrix explicit as returned current-head readback evidence",
    "Treat the current bounded HVC continuity packet on `master` as the shared",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "The survey still records the bounded HVC starter, helper, replay, split,",
    "The survey still preserves the roadmap-facing starter-depth packet as archival",
    "returned validation matrix stays part of the",
    "current-head four-matrix packet rather than the missing starter-depth anchor",
)

COMPANION_MARKERS = (
    "`PHASE11_STATUS=current_head_companion_landed`",
    "`PHASE11_FAMILY=hvc-console-cleanup-alignment`",
    "Current `master` keeps the bounded HVC continuity packet reviewable through these live surfaces:",
    "Current direct contents reads in this lane still do not rematerialize `drivers/tty/hvc/hvc_console.zig` or `zigux/tests/phase11_hvc_console_manifest.json`,",
    "Keep `scripts/zigux/check-phase11-hvc-survey-packet.py` framed as a repo-reality gap until a future reread proves that dedicated checker has returned.",
    "Until then, keep the smaller inventory-backed continuity packet explicit across the broad Phase 11 reminder surfaces without promoting the older starter-depth packet or missing survey checker as live current-head evidence.",
)

VERIFY_HELPER_MARKERS = (
    "`drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove handoff explicit without implying live `hvc_remove()` execution.",
    "`drivers/tty/hvc/hvc_console_verify.zig` keeps the remove handoff explicit when tty teardown outlives console binding, preserving hangup-driven teardown without implying live `hvc_remove()` execution.",
    "`error.NotifierDispatchRequiresTtyRegistration` keeps notifier prerequisite failures explicit instead of implying sysrq-triggered notifier dispatch can occur before tty registration.",
    "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.",
    "the literal-fallback helpers keep both the sanitized targetless sysrq path and the non-kernel sysrq literal fallback explicit without promoting the lane to live sysrq execution.",
)

EXPORT_PROOF_MARKERS = (
    'test "phase11 HVC exported helper proof keeps winsize layout explicit" {',
    "layout_assert.assertSize(WinsizeLayout, 8);",
    'test "phase11 HVC exported helper proof keeps hv_ops callback table layout explicit" {',
    'test "phase11 HVC exported helper proof keeps the exported helper surface layout explicit" {',
    'assertExactType(@FieldType(HvcExportSurface, "notifier_hangup_irq"), HvcNotifierHangupIrqFn);',
)

HV_OPS_PROOF_MARKERS = (
    'test "phase11 hvc hv_ops layout proof keeps callback table explicit" {',
    "try layout_assert.assertSize(HvOps, 72);",
    'test "phase11 hvc hv_ops layout proof stays tied to the exported header" {',
    'try expectContains(hvc_header, "struct hv_ops {");',
    'try expectContains(hvc_header, "(*dtr_rts)");',
)

HV_OPS_BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_hv_ops_layout_proof.zig"),',
    '.name = "phase11-hvc-hv-ops-layout-proof-tests",',
    'const test_step = b.step("test", "Run the focused Phase 11 hv_ops layout proof");',
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


def require_markers(root: Path, path: Path, label: str, markers: tuple[str, ...]) -> None:
    text = read_text(root / path)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing {label} marker: {marker}")


def run_check(root: Path) -> None:
    require_markers(root, SURVEY_PATH, "survey", SURVEY_MARKERS)
    require_markers(root, COMPANION_PATH, "cleanup-companion", COMPANION_MARKERS)
    require_markers(root, VERIFY_HELPER_PATH, "verify-helper", VERIFY_HELPER_MARKERS)
    require_markers(root, EXPORT_PROOF_PATH, "export-proof", EXPORT_PROOF_MARKERS)
    require_markers(root, HV_OPS_PROOF_PATH, "hv-ops-proof", HV_OPS_PROOF_MARKERS)
    require_markers(root, HV_OPS_BUILD_PATH, "hv-ops-build", HV_OPS_BUILD_MARKERS)
    require_markers(root, CLEANUP_PROOF_PATH, "cleanup-proof", CLEANUP_PROOF_MARKERS)
    require_markers(root, CLEANUP_BUILD_PATH, "cleanup-build", CLEANUP_BUILD_MARKERS)

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
            "  `Documentation/zigux/phase11-hvc-console-validation-matrix.md`,",
            "  `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`,",
            "  `zigux/tests/fixtures/phase11_build_inventory.json`,",
            "  `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`,",
            "  `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`,",
            "  `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`,",
            "  `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`, and",
            "  `zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
            "* current direct contents reads in this lane still do not rematerialize",
            "  `drivers/tty/hvc/hvc_console.zig` or",
            "  `zigux/tests/phase11_hvc_console_manifest.json`, so keep the broader",
            "  starter-depth packet framed as survey-recorded same-lane archival vocabulary",
            "  until a future reread proves those anchor paths returned again",
            "* current direct contents reads do rematerialize",
            "  `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, so keep that",
            "  shared matrix explicit as returned current-head readback evidence instead of",
            "  folding it back into the missing starter-depth anchor set",
            "",
            "## Current-Head Continuity Packet",
            "",
            "Treat the current bounded HVC continuity packet on `master` as the shared",
            "inventory-backed and proof-backed packet below:",
            "",
            "- `Documentation/zigux/phase11-hvc-console-survey.md`",
            "- `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
            "- `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
            "- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
            "- `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
            "- `zigux/tests/fixtures/phase11_build_inventory.json`",
            "- `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
            "- `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
            "- `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
            "- `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
            "- `zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
            "",
            "## Survey-Recorded Starter Packet",
            "",
            "The survey still records the bounded HVC starter, helper, replay, split,",
            "teardown, validation, and survey paths below as the roadmap-facing",
            "starter-depth packet for this lane:",
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
            "",
            "## Bounded Meaning",
            "",
            "The survey still preserves the roadmap-facing starter-depth packet as archival",
            "continuity vocabulary, while the returned validation matrix stays part of the",
            "current-head four-matrix packet rather than the missing starter-depth anchor",
            "set.",
            "",
        ]
    )


def fixture_companion() -> str:
    return "\n".join(
        [
            "# Phase 11 HVC Cleanup Alignment Current-Head Companion",
            "",
            "- `PHASE11_STATUS=current_head_companion_landed`",
            "- `PHASE11_FAMILY=hvc-console-cleanup-alignment`",
            "Current `master` keeps the bounded HVC continuity packet reviewable through these live surfaces:",
            "Current direct contents reads in this lane still do not rematerialize `drivers/tty/hvc/hvc_console.zig` or `zigux/tests/phase11_hvc_console_manifest.json`, so keep the broader direct HVC starter-depth packet framed as survey-recorded same-lane archival vocabulary until a future reread proves those anchor paths returned again.",
            "Keep `scripts/zigux/check-phase11-hvc-survey-packet.py` framed as a repo-reality gap until a future reread proves that dedicated checker has returned.",
            "Until then, keep the smaller inventory-backed continuity packet explicit across the broad Phase 11 reminder surfaces without promoting the older starter-depth packet or missing survey checker as live current-head evidence.",
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


def fixture_export_proof() -> str:
    return "\n".join(
        [
            'test "phase11 HVC exported helper proof keeps winsize layout explicit" {',
            "layout_assert.assertSize(WinsizeLayout, 8);",
            'test "phase11 HVC exported helper proof keeps hv_ops callback table layout explicit" {',
            'test "phase11 HVC exported helper proof keeps the exported helper surface layout explicit" {',
            'assertExactType(@FieldType(HvcExportSurface, "notifier_hangup_irq"), HvcNotifierHangupIrqFn);',
            "",
        ]
    )


def fixture_hv_ops_proof() -> str:
    return "\n".join(
        [
            'test "phase11 hvc hv_ops layout proof keeps callback table explicit" {',
            "try layout_assert.assertSize(HvOps, 72);",
            'test "phase11 hvc hv_ops layout proof stays tied to the exported header" {',
            'try expectContains(hvc_header, "struct hv_ops {");',
            'try expectContains(hvc_header, "(*dtr_rts)");',
            "",
        ]
    )


def fixture_hv_ops_build() -> str:
    return "\n".join(
        [
            '.root_source_file = b.path("phase11_hvc_hv_ops_layout_proof.zig"),',
            '.name = "phase11-hvc-hv-ops-layout-proof-tests",',
            'const test_step = b.step("test", "Run the focused Phase 11 hv_ops layout proof");',
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
    write(root / EXPORT_PROOF_PATH, fixture_export_proof())
    write(root / HV_OPS_PROOF_PATH, fixture_hv_ops_proof())
    write(root / HV_OPS_BUILD_PATH, fixture_hv_ops_build())
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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_cleanup_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        missing_survey_root = tmpdir / "missing_survey_marker"
        shutil.copytree(fixture, missing_survey_root, dirs_exist_ok=True)
        survey_path = missing_survey_root / SURVEY_PATH
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "current-head four-matrix packet rather than the missing starter-depth anchor",
                "",
            ),
            encoding="utf-8",
        )
        expect_failure(
            missing_survey_root,
            "current-head four-matrix packet rather than the missing starter-depth anchor",
        )

        missing_hv_ops_root = tmpdir / "missing_hv_ops_marker"
        shutil.copytree(fixture, missing_hv_ops_root, dirs_exist_ok=True)
        hv_ops_path = missing_hv_ops_root / HV_OPS_PROOF_PATH
        hv_ops_path.writeText = None
        hv_ops_path.write_text(
            hv_ops_path.read_text(encoding="utf-8").replace(
                'try expectContains(hvc_header, "(*dtr_rts)");',
                "",
            ),
            encoding="utf-8",
        )
        expect_failure(missing_hv_ops_root, 'try expectContains(hvc_header, "(*dtr_rts)");')

        missing_companion_root = tmpdir / "missing_companion_marker"
        shutil.copytree(fixture, missing_companion_root, dirs_exist_ok=True)
        companion_path = missing_companion_root / COMPANION_PATH
        companion_path.write_text(
            companion_path.read_text(encoding="utf-8").replace(
                "Keep `scripts/zigux/check-phase11-hvc-survey-packet.py` framed as a repo-reality gap until a future reread proves that dedicated checker has returned.",
                "",
            ),
            encoding="utf-8",
        )
        expect_failure(
            missing_companion_root,
            "Keep `scripts/zigux/check-phase11-hvc-survey-packet.py` framed as a repo-reality gap until a future reread proves that dedicated checker has returned.",
        )

        missing_file_root = tmpdir / "missing_file"
        shutil.copytree(fixture, missing_file_root, dirs_exist_ok=True)
        (missing_file_root / SURVEY_PATH).unlink()
        expect_failure(missing_file_root, str(SURVEY_PATH))

        print("PHASE11_HVC_CLEANUP_CURRENT_HEAD_SELF_TEST=pass")
        print("PHASE11_HVC_CLEANUP_CURRENT_HEAD_SELF_TEST_CASE_COUNT=5")
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
        run_check(args.root)
    except CheckError as exc:
        print(f"PHASE11_HVC_CLEANUP_CURRENT_HEAD=fail: {exc}")
        return 1

    print("PHASE11_HVC_CLEANUP_CURRENT_HEAD=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
