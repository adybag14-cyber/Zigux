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
PROOF_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_proof.zig")
BUILD_PATH = Path("zigux/tests/phase11_hvc_cleanup_packet_build.zig")
INVENTORY_PATH = Path("zigux/tests/fixtures/phase11_build_inventory.json")

SURVEY_MARKERS = (
    "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "current authenticated contents reads in this lane still do not rematerialize",
    "current-head four-matrix packet rather than the missing starter-depth anchor",
)
COMPANION_MARKERS = (
    "`PHASE11_STATUS=current_head_companion_landed`",
    "Keep `scripts/zigux/check-phase11-hvc-survey-packet.py` framed as a repo-reality gap",
    "smaller proof-backed HVC continuity packet reviewable",
)
VERIFY_MARKERS = (
    "`drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove handoff explicit",
    "`error.CleanupRequiresFinalCloseOrHangup` keeps cleanup-time tty-port release evidence tied to a prior final-close or hangup boundary",
    "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.",
)
MATRIX_MARKERS = (
    "`hvc_cleanup()` tty-port release handoff remains explicit in the current HVC",
    "final-close and hangup-driven cleanup handoff assertions inside the shared Phase 11 replay",
    "surviving proof-backed cleanup packet",
)
PROOF_MARKERS = (
    'test "phase11 hvc cleanup packet proof keeps current-head cleanup packet explicit" {',
    'try expectContains(survey_doc, "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`");',
    'try expectContains(cleanup_companion, "smaller proof-backed HVC continuity packet reviewable");',
    'test "phase11 hvc cleanup packet proof keeps current-head cleanup handoff markers aligned" {',
    'try expectContains(matrix_doc, "surviving proof-backed cleanup packet");',
)
BUILD_MARKERS = (
    '.root_source_file = b.path("phase11_hvc_cleanup_packet_proof.zig"),',
    '.name = "phase11-hvc-cleanup-packet-proof",',
    'const test_step = b.step("test", "Run the focused Phase 11 HVC cleanup packet proof");',
)
EXPECTED_BUILD_TESTS = [
    "phase11-hvc-console-tests",
    "phase11-hvc-console-verify-tests",
    "phase11-hvc-cleanup-tests",
    "phase11-hvc-console-survey-tests",
]
EXPECTED_DEPEND_STEPS = [
    "run_phase11_hvc_console_tests",
    "run_hvc_console_verify_tests",
    "run_phase11_hvc_cleanup_tests",
]
EXPECTED_MODULES = {
    "hvc_console_module": "../../drivers/tty/hvc/hvc_console.zig",
    "hvc_console_verify_module": "../../drivers/tty/hvc/hvc_console_verify.zig",
    "phase11_hvc_console_module": "phase11_hvc_console.zig",
    "phase11_hvc_cleanup_module": "phase11_hvc_cleanup.zig",
    "phase11_hvc_console_survey_module": "phase11_hvc_console_survey.zig",
}
EXPECTED_ROOT_MODULES = {
    "phase11-hvc-console-tests": "phase11_hvc_console_module",
    "phase11-hvc-console-verify-tests": "hvc_console_verify_module",
    "phase11-hvc-cleanup-tests": "phase11_hvc_cleanup_module",
    "phase11-hvc-console-survey-tests": "phase11_hvc_console_survey_module",
}
EXPECTED_FORBIDDEN_MARKERS = [
    "test_step.dependOn(&run_phase11_hvc_console_survey_tests.step);",
]
EXPECTED_SHARED_SPLIT_REPLAYS: list[str] = []
EXPECTED_SHARED_ADJUNCT_REPLAYS = [
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
]
EXPECTED_REPLAY_MARKERS = {
    ("zigux/tests/phase11_hvc_console_modem_control_split.zig", " try std.testing.expectEqual(@as(c_int, -7), summary.tiocmset_result);"),
    ("zigux/tests/phase11_hvc_console_poll_retry_split.zig", " try std.testing.expect(dispatch.invokes_sysrq_handler);"),
}


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


def expect_mapping(payload: dict[str, object], key: str, expected: dict[str, str], key_field: str, value_field: str) -> None:
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


def run_check(root: Path) -> None:
    require_markers(root, SURVEY_PATH, "survey", SURVEY_MARKERS)
    require_markers(root, COMPANION_PATH, "companion", COMPANION_MARKERS)
    require_markers(root, VERIFY_PATH, "verify", VERIFY_MARKERS)
    require_markers(root, MATRIX_PATH, "matrix", MATRIX_MARKERS)
    require_markers(root, PROOF_PATH, "proof", PROOF_MARKERS)
    require_markers(root, BUILD_PATH, "build", BUILD_MARKERS)

    payload = read_inventory(root)
    expect_list(payload, "build_test_names", EXPECTED_BUILD_TESTS)
    expect_list(payload, "shared_test_depend_steps", EXPECTED_DEPEND_STEPS)
    expect_list(payload, "forbidden_markers", EXPECTED_FORBIDDEN_MARKERS)
    expect_list(payload, "dedicated_survey_replays", ["zigux/tests/phase11_hvc_console_survey.zig"])
    expect_list(payload, "shared_split_replays", EXPECTED_SHARED_SPLIT_REPLAYS)
    expect_list(payload, "shared_adjunct_replays", EXPECTED_SHARED_ADJUNCT_REPLAYS)
    expect_mapping(payload, "module_root_source_files", EXPECTED_MODULES, "module", "path")
    expect_mapping(payload, "test_root_modules", EXPECTED_ROOT_MODULES, "test", "root_module")
    expect_replay_markers(payload)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / SURVEY_PATH, "\n".join([
        "# Phase 11 HVC Console Survey",
        "",
        "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
        "current authenticated contents reads in this lane still do not rematerialize",
        "current-head four-matrix packet rather than the missing starter-depth anchor",
        "",
    ]))
    write(root / COMPANION_PATH, "\n".join([
        "# Phase 11 HVC Cleanup Alignment Current-Head Companion",
        "",
        "`PHASE11_STATUS=current_head_companion_landed`",
        "Keep `scripts/zigux/check-phase11-hvc-survey-packet.py` framed as a repo-reality gap",
        "smaller proof-backed HVC continuity packet reviewable",
        "",
    ]))
    write(root / VERIFY_PATH, "\n".join([
        "# Phase 11 HVC Verify Helper Boundary",
        "",
        "`drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove handoff explicit",
        "`error.CleanupRequiresFinalCloseOrHangup` keeps cleanup-time tty-port release evidence tied to a prior final-close or hangup boundary",
        "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.",
        "",
    ]))
    write(root / MATRIX_PATH, "\n".join([
        "# Phase 11 HVC Console Validation Matrix",
        "",
        "`hvc_cleanup()` tty-port release handoff remains explicit in the current HVC packet",
        "final-close and hangup-driven cleanup handoff assertions inside the shared Phase 11 replay",
        "surviving proof-backed cleanup packet",
        "",
    ]))
    write(root / PROOF_PATH, "\n".join([
        'test "phase11 hvc cleanup packet proof keeps current-head cleanup packet explicit" {',
        'try expectContains(survey_doc, "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`");',
        'try expectContains(cleanup_companion, "smaller proof-backed HVC continuity packet reviewable");',
        'test "phase11 hvc cleanup packet proof keeps current-head cleanup handoff markers aligned" {',
        'try expectContains(matrix_doc, "surviving proof-backed cleanup packet");',
        "",
    ]))
    write(root / BUILD_PATH, "\n".join([
        '.root_source_file = b.path("phase11_hvc_cleanup_packet_proof.zig"),',
        '.name = "phase11-hvc-cleanup-packet-proof",',
        'const test_step = b.step("test", "Run the focused Phase 11 HVC cleanup packet proof");',
        "",
    ]))
    write(root / INVENTORY_PATH, json.dumps({
        "build_test_names": EXPECTED_BUILD_TESTS,
        "shared_test_depend_steps": EXPECTED_DEPEND_STEPS,
        "module_root_source_files": [{"module": k, "path": v} for k, v in EXPECTED_MODULES.items()],
        "test_root_modules": [{"test": k, "root_module": v} for k, v in EXPECTED_ROOT_MODULES.items()],
        "forbidden_markers": EXPECTED_FORBIDDEN_MARKERS,
        "dedicated_survey_replays": ["zigux/tests/phase11_hvc_console_survey.zig"],
        "shared_split_replays": EXPECTED_SHARED_SPLIT_REPLAYS,
        "shared_adjunct_replays": EXPECTED_SHARED_ADJUNCT_REPLAYS,
        "shared_replay_markers": [{"path": p, "marker": m} for p, m in sorted(EXPECTED_REPLAY_MARKERS)],
    }, indent=2) + "\n")


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
        write(missing_survey / SURVEY_PATH, read_text(missing_survey / SURVEY_PATH).replace("current-head four-matrix packet rather than the missing starter-depth anchor", ""))
        expect_failure(missing_survey, "current-head four-matrix packet rather than the missing starter-depth anchor")

        missing_survey_anchor = tmpdir / "missing_survey_anchor"
        shutil.copytree(fixture, missing_survey_anchor, dirs_exist_ok=True)
        write(missing_survey_anchor / SURVEY_PATH, read_text(missing_survey_anchor / SURVEY_PATH).replace("`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`", ""))
        expect_failure(missing_survey_anchor, "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`")

        missing_companion = tmpdir / "missing_companion"
        shutil.copytree(fixture, missing_companion, dirs_exist_ok=True)
        write(missing_companion / COMPANION_PATH, read_text(missing_companion / COMPANION_PATH).replace("smaller proof-backed HVC continuity packet reviewable", ""))
        expect_failure(missing_companion, "smaller proof-backed HVC continuity packet reviewable")

        missing_companion_gap = tmpdir / "missing_companion_gap"
        shutil.copytree(fixture, missing_companion_gap, dirs_exist_ok=True)
        write(missing_companion_gap / COMPANION_PATH, read_text(missing_companion_gap / COMPANION_PATH).replace("Keep `scripts/zigux/check-phase11-hvc-survey-packet.py` framed as a repo-reality gap", ""))
        expect_failure(missing_companion_gap, "`scripts/zigux/check-phase11-hvc-survey-packet.py`")

        missing_verify = tmpdir / "missing_verify"
        shutil.copytree(fixture, missing_verify, dirs_exist_ok=True)
        write(missing_verify / VERIFY_PATH, read_text(missing_verify / VERIFY_PATH).replace("`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.", ""))
        expect_failure(missing_verify, "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`")

        missing_matrix = tmpdir / "missing_matrix"
        shutil.copytree(fixture, missing_matrix, dirs_exist_ok=True)
        write(missing_matrix / MATRIX_PATH, read_text(missing_matrix / MATRIX_PATH).replace("surviving proof-backed cleanup packet", ""))
        expect_failure(missing_matrix, "surviving proof-backed cleanup packet")

        missing_proof = tmpdir / "missing_proof"
        shutil.copytree(fixture, missing_proof, dirs_exist_ok=True)
        write(missing_proof / PROOF_PATH, read_text(missing_proof / PROOF_PATH).replace('try expectContains(matrix_doc, "surviving proof-backed cleanup packet");', ""))
        expect_failure(missing_proof, 'try expectContains(matrix_doc, "surviving proof-backed cleanup packet");')

        wrong_inventory = tmpdir / "wrong_inventory"
        shutil.copytree(fixture, wrong_inventory, dirs_exist_ok=True)
        payload = read_inventory(wrong_inventory)
        payload["build_test_names"] = payload["build_test_names"][:-1]
        write(wrong_inventory / INVENTORY_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(wrong_inventory, "build_test_names does not match the current-head HVC packet")

        wrong_adjunct = tmpdir / "wrong_adjunct"
        shutil.copytree(fixture, wrong_adjunct, dirs_exist_ok=True)
        payload = read_inventory(wrong_adjunct)
        payload["shared_adjunct_replays"] = []
        write(wrong_adjunct / INVENTORY_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(wrong_adjunct, "shared_adjunct_replays does not match the current-head HVC packet")

        wrong_forbidden = tmpdir / "wrong_forbidden"
        shutil.copytree(fixture, wrong_forbidden, dirs_exist_ok=True)
        payload = read_inventory(wrong_forbidden)
        payload["forbidden_markers"] = []
        write(wrong_forbidden / INVENTORY_PATH, json.dumps(payload, indent=2) + "\n")
        expect_failure(wrong_forbidden, "forbidden_markers does not match the current-head HVC packet")

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
