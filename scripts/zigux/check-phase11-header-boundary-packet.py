#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase11-uapi-header-parity-survey.md")
MATRIX_PATH = Path("Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md")
CHECKER_COVERAGE_PATH = Path(
    "Documentation/zigux/phase11-uapi-header-parity-checker-coverage-note.md"
)
HV_OPS_FOLLOWUP_PATH = Path(
    "Documentation/zigux/phase11-uapi-header-parity-hv-ops-followup.md"
)

SURVEY_REQUIRED_MARKERS = (
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`scripts/zigux/check-phase11-header-boundary-packet.py`",
    "`python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase11-header-boundary-packet.py`",
    "`zigux/helpers/layout_assert.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`drivers/tty/hvc/hvc_console.h`",
    "`drivers/tty/hvc/hvc_console.zig`",
    "returned `zigux/helpers/layout_assert.zig` substrate",
    "adjacent failure-mode continuity rather than a restored shared header-parity replay roster",
    "documentation-level continuity evidence",
    "bounded modem-control callback proof",
    "`phase11-focused-direct-build-checker`",
    "`scripts/zigux/check-phase11-focused-direct-build-replays.py`",
    "machine-checked evidence rather than inventory-only prose",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
)

SURVEY_FORBIDDEN_MARKERS = (
    "  - `scripts/zigux/check-phase11-header-boundary-packet.py`\n- current shared reminder and machine-checked HVC header-boundary evidence therefore still lives",
    "no directly readable shared survey source, manifest, checker, or shared Phase 11 build route currently rematerializes the older cross-driver packet",
)

MATRIX_REQUIRED_MARKERS = (
    "`Documentation/zigux/phase11-shared-replay-contract.md`",
    "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`Documentation/zigux/phase11-uapi-header-parity-checker-coverage-note.md`",
    "`Documentation/zigux/phase11-uapi-header-parity-hv-ops-followup.md`",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`scripts/zigux/check-phase11-header-boundary-packet.py`",
    "`python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase11-header-boundary-packet.py`",
    "`zigux/helpers/layout_assert.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`drivers/tty/hvc/hvc_console.h`",
    "`drivers/tty/hvc/hvc_console.zig`",
    "returned `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "returned `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "keep the returned header-boundary checker framed as note-side evidence only",
    "Keep the adjacent cleanup, modem-control, and targetless-unregister companions explicit as directly readable HVC failure-mode continuity evidence",
    "`scripts/zigux/check-phase11-focused-direct-build-replays.py`",
    "`python3 scripts/zigux/check-phase11-focused-direct-build-replays.py --self-test`",
    "`python3 scripts/zigux/check-phase11-focused-direct-build-replays.py`",
    "`scripts/zigux/validate-phase11.py`",
    "`zigux/Makefile`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "returned checker-coverage note",
    "returned `hv_ops` follow-up note",
    "| header-boundary note stack |",
)

MATRIX_FORBIDDEN_MARKERS = (
    "- `zigux/tests/phase11_build.zig`\n  - `scripts/zigux/check-phase11-header-boundary-packet.py`",
    "without reviving missing shared replay, manifest, or checker paths",
)

CHECKER_COVERAGE_REQUIRED_MARKERS = (
    "`PHASE11_UAPI_HEADER_CHECKER_COVERAGE_STATUS=returned_note_side_checker_and_adjacent_packet_truthful`",
    "`Documentation/zigux/phase11-uapi-header-parity-checker-coverage-note.md`",
    "`Documentation/zigux/phase11-uapi-header-parity-hv-ops-followup.md`",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`scripts/zigux/check-phase11-header-boundary-packet.py`",
    "`python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase11-header-boundary-packet.py`",
    "`scripts/zigux/check-phase11-focused-direct-build-replays.py`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "returned dedicated shared checker now exists",
    "note-side evidence only",
    "missing shared manifest, survey source, or build route",
)

CHECKER_COVERAGE_FORBIDDEN_MARKERS = (
    "the dedicated shared checker itself does not read back on current `master`",
    "- `scripts/zigux/check-phase11-header-boundary-packet.py`\n- `zigux/tests/phase11_build.zig`",
)

HV_OPS_FOLLOWUP_REQUIRED_MARKERS = (
    "`PHASE11_HV_OPS_FOLLOWUP_STATUS=adjacent_hv_ops_proof_returned_shared_replay_still_missing`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
    "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
    "`zigux/helpers/layout_assert.zig`",
    "`drivers/tty/hvc/hvc_console.h`",
    "`drivers/tty/hvc/hvc_console.zig`",
    "`scripts/zigux/check-phase11-header-boundary-packet.py`",
    "adjacent proof-shard evidence",
    "shared manifest, survey source, and build route remain absent",
)

HV_OPS_FOLLOWUP_FORBIDDEN_MARKERS = (
    "Draft PR `#302`",
    "not yet part of the shared `phase11-uapi-header-parity-survey-tests` route",
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


def require_markers(path: Path, text: str, required: tuple[str, ...], forbidden: tuple[str, ...]) -> None:
    normalized = normalize_whitespace(text)
    for marker in required:
        if normalize_whitespace(marker) not in normalized:
            raise CheckError(f"missing marker in {path}: {marker}")
    for marker in forbidden:
        if normalize_whitespace(marker) in normalized:
            raise CheckError(f"forbidden marker in {path}: {marker}")


def run_check(root: Path) -> None:
    survey_text = read_text(root, SURVEY_PATH)
    matrix_text = read_text(root, MATRIX_PATH)
    checker_coverage_text = read_text(root, CHECKER_COVERAGE_PATH)
    hv_ops_followup_text = read_text(root, HV_OPS_FOLLOWUP_PATH)
    require_markers(SURVEY_PATH, survey_text, SURVEY_REQUIRED_MARKERS, SURVEY_FORBIDDEN_MARKERS)
    require_markers(MATRIX_PATH, matrix_text, MATRIX_REQUIRED_MARKERS, MATRIX_FORBIDDEN_MARKERS)
    require_markers(
        CHECKER_COVERAGE_PATH,
        checker_coverage_text,
        CHECKER_COVERAGE_REQUIRED_MARKERS,
        CHECKER_COVERAGE_FORBIDDEN_MARKERS,
    )
    require_markers(
        HV_OPS_FOLLOWUP_PATH,
        hv_ops_followup_text,
        HV_OPS_FOLLOWUP_REQUIRED_MARKERS,
        HV_OPS_FOLLOWUP_FORBIDDEN_MARKERS,
    )


def remove_marker(text: str, marker: str) -> str:
    pattern = r"\s+".join(re.escape(part) for part in marker.split())
    updated, count = re.subn(pattern, "", text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise AssertionError(marker)
    return updated


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def run_self_test() -> int:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_header_boundary_"))
    try:
        fixture_root = tmpdir / "fixture"
        for path, source in (
            (SURVEY_PATH, Path(__file__).resolve().parents[2] / SURVEY_PATH),
            (MATRIX_PATH, Path(__file__).resolve().parents[2] / MATRIX_PATH),
            (CHECKER_COVERAGE_PATH, Path(__file__).resolve().parents[2] / CHECKER_COVERAGE_PATH),
            (HV_OPS_FOLLOWUP_PATH, Path(__file__).resolve().parents[2] / HV_OPS_FOLLOWUP_PATH),
        ):
            (fixture_root / path).parent.mkdir(parents=True, exist_ok=True)
            (fixture_root / path).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        run_check(fixture_root)
        case_count = 1

        survey_missing = tmpdir / "survey_missing"
        shutil.copytree(fixture_root, survey_missing, dirs_exist_ok=True)
        path = survey_missing / SURVEY_PATH
        survey_unique_marker = "documentation-level continuity evidence"
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), survey_unique_marker), encoding="utf-8")
        expect_failure(survey_missing, survey_unique_marker)
        case_count += 1

        matrix_hvc_module_missing = tmpdir / "matrix_hvc_module_missing"
        shutil.copytree(fixture_root, matrix_hvc_module_missing, dirs_exist_ok=True)
        path = matrix_hvc_module_missing / MATRIX_PATH
        hvc_module_marker = "`drivers/tty/hvc/hvc_console.zig`"
        path.write_text(
            remove_marker(path.read_text(encoding="utf-8"), hvc_module_marker),
            encoding="utf-8",
        )
        expect_failure(matrix_hvc_module_missing, hvc_module_marker)
        case_count += 1

        matrix_missing = tmpdir / "matrix_missing"
        shutil.copytree(fixture_root, matrix_missing, dirs_exist_ok=True)
        path = matrix_missing / MATRIX_PATH
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), MATRIX_REQUIRED_MARKERS[-1]), encoding="utf-8")
        expect_failure(matrix_missing, MATRIX_REQUIRED_MARKERS[-1])
        case_count += 1

        checker_missing = tmpdir / "checker_missing"
        shutil.copytree(fixture_root, checker_missing, dirs_exist_ok=True)
        path = checker_missing / CHECKER_COVERAGE_PATH
        path.write_text(
            remove_marker(path.read_text(encoding="utf-8"), CHECKER_COVERAGE_REQUIRED_MARKERS[10]),
            encoding="utf-8",
        )
        expect_failure(checker_missing, CHECKER_COVERAGE_REQUIRED_MARKERS[10])
        case_count += 1

        hv_ops_missing = tmpdir / "hv_ops_missing"
        shutil.copytree(fixture_root, hv_ops_missing, dirs_exist_ok=True)
        path = hv_ops_missing / HV_OPS_FOLLOWUP_PATH
        path.write_text(
            remove_marker(path.read_text(encoding="utf-8"), HV_OPS_FOLLOWUP_REQUIRED_MARKERS[1]),
            encoding="utf-8",
        )
        expect_failure(hv_ops_missing, HV_OPS_FOLLOWUP_REQUIRED_MARKERS[1])
        case_count += 1

        checker_forbidden = tmpdir / "checker_forbidden"
        shutil.copytree(fixture_root, checker_forbidden, dirs_exist_ok=True)
        path = checker_forbidden / CHECKER_COVERAGE_PATH
        path.write_text(
            path.read_text(encoding="utf-8")
            + "\nthe dedicated shared checker itself does not read back on current `master`\n",
            encoding="utf-8",
        )
        expect_failure(checker_forbidden, CHECKER_COVERAGE_FORBIDDEN_MARKERS[0])
        case_count += 1

        hv_ops_forbidden = tmpdir / "hv_ops_forbidden"
        shutil.copytree(fixture_root, hv_ops_forbidden, dirs_exist_ok=True)
        path = hv_ops_forbidden / HV_OPS_FOLLOWUP_PATH
        path.write_text(
            path.read_text(encoding="utf-8") + "\nDraft PR `#302` remains the active source.\n",
            encoding="utf-8",
        )
        expect_failure(hv_ops_forbidden, HV_OPS_FOLLOWUP_FORBIDDEN_MARKERS[0])
        case_count += 1

        print("PHASE11_HEADER_BOUNDARY_PACKET_SELF_TEST=pass")
        print(f"PHASE11_HEADER_BOUNDARY_PACKET_SELF_TEST_CASE_COUNT={case_count}")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    try:
        run_check(args.root.resolve())
    except CheckError as exc:
        print(f"PHASE11_HEADER_BOUNDARY_PACKET=fail: {exc}")
        return 1
    print("PHASE11_HEADER_BOUNDARY_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
