#!/usr/bin/env python3
"""Fail-close guard for the current-head Phase 11 HVC cleanup packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[3] if len(SELF_PATH.parents) > 3 else SELF_PATH.parent

SURVEY_PATH = Path("Documentation/zigux/phase11-hvc-console-survey.md")
COMPANION_PATH = Path("Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md")
VERIFY_PATH = Path("Documentation/zigux/phase11-hvc-verify-helper-boundary.md")
MATRIX_PATH = Path("Documentation/zigux/phase11-hvc-console-validation-matrix.md")
EXPORT_PROOF_PATH = Path("zigux/tests/phase11_hvc_export_surface_layout_proof.zig")
EXPORT_BUILD_PATH = Path("zigux/tests/phase11_hvc_export_surface_layout_build.zig")
HV_OPS_PROOF_PATH = Path("zigux/tests/phase11_hvc_hv_ops_layout_proof.zig")
HV_OPS_BUILD_PATH = Path("zigux/tests/phase11_hvc_hv_ops_layout_build.zig")
PROOF_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_proof.zig")
BUILD_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_build.zig")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")

REQUIRED_PROOF_ROUTE = {
    "proof_build_file": "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "proof_replay_command": "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "proof_step_name": "test",
    "proof_step_description": "Run the focused Phase 11 HVC cleanup packet proof",
    "proof_test_artifact_name": "phase11-hvc-cleanup-packet-proof",
    "proof_root_source_file": "phase11_hvc_cleanup_packet_proof.zig",
}

EXACT_CURRENT_CHECKS = [
    "python3 scripts/zigux/check-phase11-build-inventory.py --self-test",
    "python3 scripts/zigux/check-phase11-build-inventory.py",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test",
    "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py",
    "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
]

SURVEY_MARKERS = (
    "`PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`",
    "current authenticated contents readback keeps the bounded HVC current-head",
    "keep the deeper verify helper, sysrq helper, focused survey replay, manifest,",
)
COMPANION_MARKERS = (
    "`PHASE11_STATUS=current_head_companion_landed`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "Keep `scripts/zigux/check-phase11-hvc-survey-packet.py` framed as a repo-reality gap",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "returned HVC validation matrix",
    "smaller proof-backed HVC continuity packet reviewable",
)
VERIFY_MARKERS = (
    "`drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove handoff explicit",
    "`drivers/tty/hvc/hvc_console_verify.zig` keeps the remove handoff explicit when tty teardown outlives console binding, preserving hangup-driven teardown without implying live `hvc_remove()` execution.",
    "`error.CleanupRequiresFinalCloseOrHangup` keeps cleanup-time tty-port release evidence tied to a prior final-close or hangup boundary",
    "Current direct contents reads on `master` still do not rematerialize `drivers/tty/hvc/hvc_console_verify.zig`, so keep this note as the current-head reminder surface for those landed helper edges rather than treating the helper file itself as returned direct-readback evidence.",
    "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.",
    "do not treat this note as proof that `drivers/tty/hvc/hvc_console_verify.zig` has returned to direct current-head readback",
)
MATRIX_MARKERS = (
    "`PHASE11_HVC_CONSOLE_STATUS=current_head_companion_packet_truthful`",
    "the current matrix packet now stays aligned with the smaller",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "keep helper-local failure-mode edges reviewable through",
    "do not treat the deeper verify helper, sysrq helper, manifest, teardown note,",
)
EXPORT_PROOF_MARKERS = (
    'test "phase11 HVC exported helper proof keeps winsize layout explicit" {',
    'layout_assert.assertOffset(HvcExportSurface, "notifier_hangup_irq", 64);',
    'try expectContains(hvc_header, "void notifier_hangup_irq(struct hvc_struct *hp, int irq);");',
)
EXPORT_BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig"),',
    '.name = "phase11-hvc-export-surface-layout-proof",',
    'const test_step = b.step("test", "Run the focused Phase 11 HVC exported-helper ABI proof");',
)
HV_OPS_PROOF_MARKERS = (
    'test "phase11 hvc hv_ops layout proof keeps callback table explicit" {',
    'try layout_assert.expectOffset(HvOps, "notifier_hangup", 40);',
    'try expectContains(hvc_header, "(*dtr_rts)");',
)
HV_OPS_BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_hv_ops_layout_proof.zig"),',
    '.name = "phase11-hvc-hv-ops-layout-proof-tests",',
    '.root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig"),',
    '.name = "phase11-hvc-export-surface-layout-proof-tests",',
    'const test_step = b.step("test", "Run the focused Phase 11 exported-header proofs");',
)
PROOF_MARKERS = (
    'test "phase11 hvc cleanup packet proof keeps current-head cleanup packet explicit" {',
    'try expectContains(survey_doc, "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`");',
    'try expectContains(survey_doc, "current authenticated contents readback keeps the bounded HVC current-head");',
    'try expectContains(cleanup_companion, "smaller proof-backed HVC continuity packet reviewable");',
    'test "phase11 hvc cleanup packet proof keeps current-head cleanup handoff markers aligned" {',
    'try expectContains(matrix_doc, "the current matrix packet now stays aligned with the smaller");',
    'try expectContains(matrix_doc, "keep helper-local failure-mode edges reviewable through");',
)
BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_cleanup_packet_proof.zig"),',
    '.name = "phase11-hvc-cleanup-packet-proof",',
    'const test_step = b.step("test", "Run the focused Phase 11 HVC cleanup packet proof");',
)
EXPECTED_BUILD_TESTS = [
    "phase11-hvc-hv-ops-layout-proof-tests",
    "phase11-hvc-export-surface-layout-proof-tests",
    "phase11-hvc-cleanup-packet-proof",
]
EXPECTED_DEPEND_STEPS: list[str] = []
EXPECTED_MODULES = {
    "hv_ops_proof_module": "phase11_hvc_hv_ops_layout_proof.zig",
    "export_surface_proof_module": "phase11_hvc_export_surface_layout_proof.zig",
    "proof_module": "phase11_hvc_cleanup_packet_proof.zig",
}
EXPECTED_ROOT_MODULES = {
    "phase11-hvc-hv-ops-layout-proof-tests": "hv_ops_proof_module",
    "phase11-hvc-export-surface-layout-proof-tests": "export_surface_proof_module",
    "phase11-hvc-cleanup-packet-proof": "proof_module",
}
EXPECTED_FORBIDDEN_MARKERS = [
    "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
]
EXPECTED_SHARED_SPLIT_REPLAYS: list[str] = []
EXPECTED_SHARED_ADJUNCT_REPLAYS = [
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
]
EXPECTED_REPLAY_MARKERS: set[tuple[str, str]] = set()


class CheckError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    if not path.is_file():
        raise CheckError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def require_markers(root: Path, rel: Path, label: str, markers: tuple[str, ...]) -> None:
    text = read_text(root / rel)
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing {label} marker: {marker}")


def read_inventory(root: Path) -> dict[str, object]:
    try:
        payload = json.loads(read_text(root / INVENTORY_PATH))
    except json.JSONDecodeError as exc:
        raise CheckError(f"invalid JSON in {INVENTORY_PATH}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckError(f"expected object in {INVENTORY_PATH}")
    return payload


def expect_list(payload: dict[str, object], key: str, expected: list[str]) -> None:
    value = payload.get(key)
    if value != expected:
        raise CheckError(f"{key} does not match the current-head HVC packet")


def expect_exact_string(payload: dict[str, object], key: str, expected: str) -> str:
    value = payload.get(key)
    if value != expected:
        raise CheckError(f"{key} does not match the current-head HVC packet")
    return value


def expect_mapping(
    payload: dict[str, object],
    key: str,
    expected: dict[str, str],
    key_field: str,
    value_field: str,
) -> None:
    value = payload.get(key)
    if not isinstance(value, list):
        raise CheckError(f"expected list for {key}")
    actual: dict[str, str] = {}
    for entry in value:
        if not isinstance(entry, dict):
            raise CheckError(f"expected object entries for {key}")
        lhs = entry.get(key_field)
        rhs = entry.get(value_field)
        if not isinstance(lhs, str) or not isinstance(rhs, str):
            raise CheckError(f"invalid entry in {key}")
        actual[lhs] = rhs
    if actual != expected:
        raise CheckError(f"{key} does not match the current-head HVC packet")


def expect_replay_markers(payload: dict[str, object]) -> None:
    value = payload.get("shared_replay_markers")
    if not isinstance(value, list):
        raise CheckError("expected list for shared_replay_markers")
    actual = set()
    for entry in value:
        if not isinstance(entry, dict):
            raise CheckError("expected object entries for shared_replay_markers")
        path = entry.get("path")
        marker = entry.get("marker")
        if not isinstance(path, str) or not isinstance(marker, str):
            raise CheckError("invalid entry in shared_replay_markers")
        actual.add((path, marker))
    if actual != EXPECTED_REPLAY_MARKERS:
        raise CheckError("shared_replay_markers does not match the current-head HVC packet")


def build_route_markers_from_inventory(payload: dict[str, object]) -> tuple[str, str, str]:
    proof_build_file = expect_exact_string(
        payload,
        "proof_build_file",
        REQUIRED_PROOF_ROUTE["proof_build_file"],
    )
    proof_replay_command = expect_exact_string(
        payload,
        "proof_replay_command",
        REQUIRED_PROOF_ROUTE["proof_replay_command"],
    )
    proof_step_name = expect_exact_string(
        payload,
        "proof_step_name",
        REQUIRED_PROOF_ROUTE["proof_step_name"],
    )
    proof_step_description = expect_exact_string(
        payload,
        "proof_step_description",
        REQUIRED_PROOF_ROUTE["proof_step_description"],
    )
    proof_test_artifact_name = expect_exact_string(
        payload,
        "proof_test_artifact_name",
        REQUIRED_PROOF_ROUTE["proof_test_artifact_name"],
    )
    proof_root_source_file = expect_exact_string(
        payload,
        "proof_root_source_file",
        REQUIRED_PROOF_ROUTE["proof_root_source_file"],
    )
    if proof_replay_command != f"zig build test --build-file {proof_build_file}":
        raise CheckError("proof_replay_command does not match the current-head HVC packet")
    return (
        f'.root_source_file = b.path("{proof_root_source_file}"),',
        f'.name = "{proof_test_artifact_name}"',
        f'const test_step = b.step("{proof_step_name}", "{proof_step_description}");',
    )


def run_check(root: Path) -> None:
    require_markers(root, SURVEY_PATH, "survey", SURVEY_MARKERS)
    require_markers(root, COMPANION_PATH, "companion", COMPANION_MARKERS)
    require_markers(root, VERIFY_PATH, "verify", VERIFY_MARKERS)
    require_markers(root, MATRIX_PATH, "matrix", MATRIX_MARKERS)
    require_markers(root, EXPORT_PROOF_PATH, "export proof", EXPORT_PROOF_MARKERS)
    require_markers(root, EXPORT_BUILD_PATH, "export build", EXPORT_BUILD_MARKERS)
    require_markers(root, HV_OPS_PROOF_PATH, "hv_ops proof", HV_OPS_PROOF_MARKERS)
    require_markers(root, HV_OPS_BUILD_PATH, "hv_ops build", HV_OPS_BUILD_MARKERS)
    require_markers(root, PROOF_PATH, "proof", PROOF_MARKERS)
    require_markers(root, BUILD_PATH, "build", BUILD_MARKERS)

    payload = read_inventory(root)
    build_text = read_text(root / BUILD_PATH)
    for marker in build_route_markers_from_inventory(payload):
        if marker not in build_text:
            raise CheckError(f"missing build marker: {marker}")

    expect_list(payload, "exact_current_checks", EXACT_CURRENT_CHECKS)
    expect_list(payload, "build_test_names", EXPECTED_BUILD_TESTS)
    expect_list(payload, "shared_test_depend_steps", EXPECTED_DEPEND_STEPS)
    expect_list(payload, "forbidden_markers", EXPECTED_FORBIDDEN_MARKERS)
    expect_list(payload, "dedicated_survey_replays", [])
    expect_list(payload, "shared_split_replays", EXPECTED_SHARED_SPLIT_REPLAYS)
    expect_list(payload, "shared_adjunct_replays", EXPECTED_SHARED_ADJUNCT_REPLAYS)
    expect_mapping(payload, "module_root_source_files", EXPECTED_MODULES, "module", "path")
    expect_mapping(payload, "test_root_modules", EXPECTED_ROOT_MODULES, "test", "root_module")
    expect_replay_markers(payload)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(
        root / SURVEY_PATH,
        "\n".join(
            [
                "# Phase 11 HVC Console Survey",
                "",
                "`PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`",
                "current authenticated contents readback keeps the bounded HVC current-head packet reviewable through:",
                "keep the deeper verify helper, sysrq helper, focused survey replay, manifest, teardown note, slice, and dedicated survey checker framed as archival or repo-reality-gap vocabulary until a future reread proves they returned beside the smaller companion packet.",
                "",
            ]
        ),
    )
    write(
        root / COMPANION_PATH,
        "\n".join(
            [
                "# Phase 11 HVC Cleanup Alignment Current-Head Companion",
                "",
                "`PHASE11_STATUS=current_head_companion_landed`",
                "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
                "Keep `scripts/zigux/check-phase11-hvc-survey-packet.py` framed as a repo-reality gap",
                "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
                "the returned HVC validation matrix stays explicit beside this companion",
                "smaller proof-backed HVC continuity packet reviewable",
                "",
            ]
        ),
    )
    write(
        root / VERIFY_PATH,
        "\n".join(
            [
                "# Phase 11 HVC Verify Helper Boundary",
                "",
                "`drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove handoff explicit",
                "`drivers/tty/hvc/hvc_console_verify.zig` keeps the remove handoff explicit when tty teardown outlives console binding, preserving hangup-driven teardown without implying live `hvc_remove()` execution.",
                "`error.CleanupRequiresFinalCloseOrHangup` keeps cleanup-time tty-port release evidence tied to a prior final-close or hangup boundary",
                "Current direct contents reads on `master` still do not rematerialize `drivers/tty/hvc/hvc_console_verify.zig`, so keep this note as the current-head reminder surface for those landed helper edges rather than treating the helper file itself as returned direct-readback evidence.",
                "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.",
                "do not treat this note as proof that `drivers/tty/hvc/hvc_console_verify.zig` has returned to direct current-head readback",
                "",
            ]
        ),
    )
    write(
        root / MATRIX_PATH,
        "\n".join(
            [
                "# Phase 11 HVC Console Validation Matrix",
                "",
                "`PHASE11_HVC_CONSOLE_STATUS=current_head_companion_packet_truthful`",
                "the current matrix packet now stays aligned with the smaller authenticated-readback companion stack rather than the older starter-depth public-readback packet",
                "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
                "keep helper-local failure-mode edges reviewable through `Documentation/zigux/phase11-hvc-verify-helper-boundary.md` rather than treating `drivers/tty/hvc/hvc_console_verify.zig` as a returned direct-readback anchor",
                "do not treat the deeper verify helper, sysrq helper, manifest, teardown note, dedicated survey checker, or focused survey and cleanup replays as current-head direct-readback evidence",
                "",
            ]
        ),
    )
    write(
        root / EXPORT_PROOF_PATH,
        "\n".join(
            [
                'test "phase11 HVC exported helper proof keeps winsize layout explicit" {',
                'layout_assert.assertOffset(HvcExportSurface, "notifier_hangup_irq", 64);',
                'try expectContains(hvc_header, "void notifier_hangup_irq(struct hvc_struct *hp, int irq);");',
                "",
            ]
        ),
    )
    write(
        root / EXPORT_BUILD_PATH,
        "\n".join(
            [
                '.root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig"),',
                '.name = "phase11-hvc-export-surface-layout-proof",',
                'const test_step = b.step("test", "Run the focused Phase 11 HVC exported-helper ABI proof");',
                "",
            ]
        ),
    )
    write(
        root / HV_OPS_PROOF_PATH,
        "\n".join(
            [
                'test "phase11 hvc hv_ops layout proof keeps callback table explicit" {',
                'try layout_assert.expectOffset(HvOps, "notifier_hangup", 40);',
                'try expectContains(hvc_header, "(*dtr_rts)");',
                "",
            ]
        ),
    )
    write(
        root / HV_OPS_BUILD_PATH,
        "\n".join(
            [
                '.root_source_file = b.path("phase11_hvc_hv_ops_layout_proof.zig"),',
                '.name = "phase11-hvc-hv-ops-layout-proof-tests",',
                '.root_source_file = b.path("phase11_hvc_export_surface_layout_proof.zig"),',
                '.name = "phase11-hvc-export-surface-layout-proof-tests",',
                'const test_step = b.step("test", "Run the focused Phase 11 exported-header proofs");',
                "",
            ]
        ),
    )
    write(
        root / PROOF_PATH,
        "\n".join(
            [
                'test "phase11 hvc cleanup packet proof keeps current-head cleanup packet explicit" {',
                'try expectContains(survey_doc, "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`");',
                'try expectContains(survey_doc, "current authenticated contents readback keeps the bounded HVC current-head");',
                'try expectContains(cleanup_companion, "smaller proof-backed HVC continuity packet reviewable");',
                'test "phase11 hvc cleanup packet proof keeps current-head cleanup handoff markers aligned" {',
                'try expectContains(matrix_doc, "the current matrix packet now stays aligned with the smaller");',
                'try expectContains(matrix_doc, "keep helper-local failure-mode edges reviewable through");',
                "",
            ]
        ),
    )
    write(
        root / BUILD_PATH,
        "\n".join(
            [
                '.root_source_file = b.path("phase11_hvc_cleanup_packet_proof.zig"),',
                '.name = "phase11-hvc-cleanup-packet-proof",',
                'const test_step = b.step("test", "Run the focused Phase 11 HVC cleanup packet proof");',
                "",
            ]
        ),
    )
    write(
        root / INVENTORY_PATH,
        json.dumps(
            {
                **REQUIRED_PROOF_ROUTE,
                "exact_current_checks": EXACT_CURRENT_CHECKS,
                "build_test_names": EXPECTED_BUILD_TESTS,
                "shared_test_depend_steps": EXPECTED_DEPEND_STEPS,
                "module_root_source_files": [{"module": k, "path": v} for k, v in EXPECTED_MODULES.items()],
                "test_root_modules": [{"test": k, "root_module": v} for k, v in EXPECTED_ROOT_MODULES.items()],
                "forbidden_markers": EXPECTED_FORBIDDEN_MARKERS,
                "dedicated_survey_replays": [],
                "shared_split_replays": EXPECTED_SHARED_SPLIT_REPLAYS,
                "shared_adjunct_replays": EXPECTED_SHARED_ADJUNCT_REPLAYS,
                "shared_replay_markers": [],
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
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_hvc_cleanup_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        missing_survey = tmpdir / "missing_survey"
        shutil.copytree(fixture, missing_survey, dirs_exist_ok=True)
        write(
            missing_survey / SURVEY_PATH,
            read_text(missing_survey / SURVEY_PATH).replace(
                "keep the deeper verify helper, sysrq helper, focused survey replay, manifest, teardown note, slice, and dedicated survey checker framed as archival or repo-reality-gap vocabulary until a future reread proves they returned beside the smaller companion packet.",
                "",
            ),
        )
        expect_failure(missing_survey, "keep the deeper verify helper")

        missing_companion = tmpdir / "missing_companion"
        shutil.copytree(fixture, missing_companion, dirs_exist_ok=True)
        write(
            missing_companion / COMPANION_PATH,
            read_text(missing_companion / COMPANION_PATH).replace(
                "Keep `scripts/zigux/check-phase11-hvc-survey-packet.py` framed as a repo-reality gap",
                "",
            ),
        )
        expect_failure(missing_companion, "`scripts/zigux/check-phase11-hvc-survey-packet.py`")

        missing_companion_export_build = tmpdir / "missing_companion_export_build"
        shutil.copytree(fixture, missing_companion_export_build, dirs_exist_ok=True)
        write(
            missing_companion_export_build / COMPANION_PATH,
            read_text(missing_companion_export_build / COMPANION_PATH).replace(
                "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
                "",
            ),
        )
        expect_failure(missing_companion_export_build, "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`")

        missing_verify = tmpdir / "missing_verify"
        shutil.copytree(fixture, missing_verify, dirs_exist_ok=True)
        write(
            missing_verify / VERIFY_PATH,
            read_text(missing_verify / VERIFY_PATH).replace(
                "Current direct contents reads on `master` still do not rematerialize `drivers/tty/hvc/hvc_console_verify.zig`, so keep this note as the current-head reminder surface for those landed helper edges rather than treating the helper file itself as returned direct-readback evidence.",
                "",
            ),
        )
        expect_failure(missing_verify, "Current direct contents reads on `master` still do not rematerialize `drivers/tty/hvc/hvc_console_verify.zig`")

        missing_matrix = tmpdir / "missing_matrix"
        shutil.copytree(fixture, missing_matrix, dirs_exist_ok=True)
        write(
            missing_matrix / MATRIX_PATH,
            read_text(missing_matrix / MATRIX_PATH).replace(
                "do not treat the deeper verify helper, sysrq helper, manifest, teardown note, dedicated survey checker, or focused survey and cleanup replays as current-head direct-readback evidence",
                "",
            ),
        )
        expect_failure(missing_matrix, "do not treat the deeper verify helper")

        missing_matrix_export_build = tmpdir / "missing_matrix_export_build"
        shutil.copytree(fixture, missing_matrix_export_build, dirs_exist_ok=True)
        write(
            missing_matrix_export_build / MATRIX_PATH,
            read_text(missing_matrix_export_build / MATRIX_PATH).replace(
                "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
                "",
            ),
        )
        expect_failure(missing_matrix_export_build, "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`")

        missing_export_build_marker = tmpdir / "missing_export_build_marker"
        shutil.copytree(fixture, missing_export_build_marker, dirs_exist_ok=True)
        write(
            missing_export_build_marker / EXPORT_BUILD_PATH,
            read_text(missing_export_build_marker / EXPORT_BUILD_PATH).replace(
                '.name = "phase11-hvc-export-surface-layout-proof",',
                "",
            ),
        )
        expect_failure(missing_export_build_marker, 'phase11-hvc-export-surface-layout-proof')

        missing_export_build_file = tmpdir / "missing_export_build_file"
        shutil.copytree(fixture, missing_export_build_file, dirs_exist_ok=True)
        (missing_export_build_file / EXPORT_BUILD_PATH).unlink()
        expect_failure(missing_export_build_file, str(EXPORT_BUILD_PATH))

        wrong_exact_checks = tmpdir / "wrong_exact_checks"
        shutil.copytree(fixture, wrong_exact_checks, dirs_exist_ok=True)
        payload = read_inventory(wrong_exact_checks)
        payload["exact_current_checks"] = payload["exact_current_checks"][:-1]
        write(wrong_exact_checks / INVENTORY_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(wrong_exact_checks, "exact_current_checks does not match the current-head HVC packet")

        wrong_adjunct = tmpdir / "wrong_adjunct"
        shutil.copytree(fixture, wrong_adjunct, dirs_exist_ok=True)
        payload = read_inventory(wrong_adjunct)
        payload["shared_adjunct_replays"] = []
        write(wrong_adjunct / INVENTORY_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(wrong_adjunct, "shared_adjunct_replays does not match the current-head HVC packet")

        wrong_proof_command = tmpdir / "wrong_proof_command"
        shutil.copytree(fixture, wrong_proof_command, dirs_exist_ok=True)
        payload = read_inventory(wrong_proof_command)
        payload["proof_replay_command"] = "zig build test --build-file zigux/tests/phase11_build.zig"
        write(wrong_proof_command / INVENTORY_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(wrong_proof_command, "proof_replay_command does not match the current-head HVC packet")

        missing_file = tmpdir / "missing_file"
        shutil.copytree(fixture, missing_file, dirs_exist_ok=True)
        (missing_file / SURVEY_PATH).unlink()
        expect_failure(missing_file, str(SURVEY_PATH))

        print("PHASE11_HVC_CLEANUP_CURRENT_HEAD_SELF_TEST=pass")
        print("PHASE11_HVC_CLEANUP_CURRENT_HEAD_SELF_TEST_CASE_COUNT=12")
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
