#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import tempfile
from pathlib import Path

SURVEY_PATH = Path("Documentation/zigux/phase11-uapi-header-parity-survey.md")
MATRIX_PATH = Path("Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md")

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
    "returned `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`",
    "returned `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "keep the returned header-boundary checker framed as note-side evidence only",
    "Keep the adjacent cleanup, modem-control, and targetless-unregister companions explicit as directly readable HVC failure-mode continuity evidence",
)

MATRIX_FORBIDDEN_MARKERS = (
    "- `zigux/tests/phase11_build.zig`\n  - `scripts/zigux/check-phase11-header-boundary-packet.py`",
    "without reviving missing shared replay, manifest, or checker paths",
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
    require_markers(SURVEY_PATH, survey_text, SURVEY_REQUIRED_MARKERS, SURVEY_FORBIDDEN_MARKERS)
    require_markers(MATRIX_PATH, matrix_text, MATRIX_REQUIRED_MARKERS, MATRIX_FORBIDDEN_MARKERS)


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
    fixture_survey = """# Phase 11 UAPI Header Parity Survey
## Status

- `PHASE11_HEADER_BOUNDARY_STATUS=adjacent_proof_shard_readback_only`
- lane: `P11-L02`
- reviewed against live `master` readback on `2026-05-23`
- scope: keep the Phase 11 public-header evidence truthful around the bounded HVC header boundary and the roadmap-backed watchdog/HVC review surface without widening into tty-core or watchdog-core ownership

## Current Repo Reality
- this note still ships on current `master` beside the adjacent current-head header-boundary packet:
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
  - `Documentation/zigux/phase11-driver-lane-sequencing.md`
  - `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
  - `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
  - `zigux/helpers/layout_assert.zig`
  - `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
  - `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
  - `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
  - `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
  - `zigux/tests/phase11_hvc_modem_control_proof.zig`
  - `zigux/tests/phase11_hvc_modem_control_proof_build.zig`
  - `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
  - `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
  - `scripts/zigux/check-phase11-build-inventory.py`
  - `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
  - `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
  - `drivers/tty/hvc/hvc_console.h`
  - `drivers/tty/hvc/hvc_console.zig`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`
- the older shared header-packet companions named by earlier continuity still do not read back at their former paths on current `master`:
  - `zigux/tests/phase11_uapi_header_parity_manifest.json`
  - `zigux/tests/phase11_uapi_header_parity_survey.zig`
  - `zigux/tests/phase11_build.zig`
- current shared reminder and machine-checked HVC header-boundary evidence therefore still lives in the newer focused proof packet and its adjacent current-head companion stack.
- that narrower proof packet remains `layout_assert`-backed through the returned `zigux/helpers/layout_assert.zig` substrate.
- the adjacent HVC failure-mode companion stack remains adjacent failure-mode continuity rather than a restored shared header-parity replay roster.
- the current note also needs to keep the newer bounded modem-control callback proof explicit beside cleanup and targetless-unregister continuity.
- the returned `Documentation/zigux/phase11-shared-replay-contract.md` note is documentation-level continuity evidence.
- `phase11-header-boundary-checker`: `scripts/zigux/check-phase11-header-boundary-packet.py` now fail-closes on the survey note and validation matrix through `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test` and `python3 scripts/zigux/check-phase11-header-boundary-packet.py`.
"""

    fixture_matrix = """# Phase 11 UAPI Header Parity Validation Matrix
## Review Rules

- Treat `Documentation/zigux/phase11-shared-replay-contract.md`, `scripts/zigux/check-phase11-build-inventory.py`, `scripts/zigux/check-phase11-header-boundary-packet.py`, the returned `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`, and the returned `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` as returned reminder-only continuity evidence unless the missing shared replay files rematerialize beside them.
- Keep the adjacent cleanup, modem-control, and targetless-unregister companions explicit as directly readable HVC failure-mode continuity evidence without promoting them into shared header-parity replay coverage.

## Status

- current direct-readback packet:
  - `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
  - `Documentation/zigux/phase11-uapi-header-parity-survey.md`
  - `Documentation/zigux/phase11-shared-replay-contract.md`
  - `Documentation/zigux/phase11-driver-lane-sequencing.md`
  - `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
  - `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
  - `Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`
  - `Documentation/zigux/phase11-hvc-verify-helper-boundary.md`
  - `zigux/helpers/layout_assert.zig`
  - `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`
  - `zigux/tests/phase11_hvc_export_surface_layout_build.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`
  - `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`
  - `zigux/tests/phase11_hvc_cleanup_packet_proof.zig`
  - `zigux/tests/phase11_hvc_cleanup_packet_build.zig`
  - `zigux/tests/phase11_hvc_modem_control_proof.zig`
  - `zigux/tests/phase11_hvc_modem_control_proof_build.zig`
  - `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
  - `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
  - `scripts/zigux/check-phase11-build-inventory.py`
  - `scripts/zigux/check-phase11-hvc-cleanup-current-head.py`
  - `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
  - `drivers/tty/hvc/hvc_console.h`
  - `scripts/zigux/check-phase11-header-boundary-packet.py`
- current direct contents reads in this lane do not rematerialize:
  - `zigux/tests/phase11_uapi_header_parity_manifest.json`
  - `zigux/tests/phase11_uapi_header_parity_survey.zig`
  - `zigux/tests/phase11_build.zig`
- keep the returned header-boundary checker framed as note-side evidence only through `python3 scripts/zigux/check-phase11-header-boundary-packet.py --self-test` and `python3 scripts/zigux/check-phase11-header-boundary-packet.py`.
"""

    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_header_boundary_"))
    try:
        fixture_root = tmpdir / "fixture"
        (fixture_root / SURVEY_PATH).parent.mkdir(parents=True, exist_ok=True)
        (fixture_root / MATRIX_PATH).parent.mkdir(parents=True, exist_ok=True)
        (fixture_root / SURVEY_PATH).write_text(fixture_survey, encoding="utf-8")
        (fixture_root / MATRIX_PATH).write_text(fixture_matrix, encoding="utf-8")
        run_check(fixture_root)
        case_count = 1

        survey_missing = tmpdir / "survey_missing"
        shutil.copytree(fixture_root, survey_missing, dirs_exist_ok=True)
        path = survey_missing / SURVEY_PATH
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), SURVEY_REQUIRED_MARKERS[23]), encoding="utf-8")
        expect_failure(survey_missing, SURVEY_REQUIRED_MARKERS[23])
        case_count += 1

        survey_companion_missing = tmpdir / "survey_companion_missing"
        shutil.copytree(fixture_root, survey_companion_missing, dirs_exist_ok=True)
        path = survey_companion_missing / SURVEY_PATH
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), SURVEY_REQUIRED_MARKERS[22]), encoding="utf-8")
        expect_failure(survey_companion_missing, SURVEY_REQUIRED_MARKERS[22])
        case_count += 1

        survey_modem_missing = tmpdir / "survey_modem_missing"
        shutil.copytree(fixture_root, survey_modem_missing, dirs_exist_ok=True)
        path = survey_modem_missing / SURVEY_PATH
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), SURVEY_REQUIRED_MARKERS[17]), encoding="utf-8")
        expect_failure(survey_modem_missing, SURVEY_REQUIRED_MARKERS[17])
        case_count += 1

        matrix_missing = tmpdir / "matrix_missing"
        shutil.copytree(fixture_root, matrix_missing, dirs_exist_ok=True)
        path = matrix_missing / MATRIX_PATH
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), MATRIX_REQUIRED_MARKERS[22]), encoding="utf-8")
        expect_failure(matrix_missing, MATRIX_REQUIRED_MARKERS[22])
        case_count += 1

        matrix_companion_missing = tmpdir / "matrix_companion_missing"
        shutil.copytree(fixture_root, matrix_companion_missing, dirs_exist_ok=True)
        path = matrix_companion_missing / MATRIX_PATH
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), MATRIX_REQUIRED_MARKERS[21]), encoding="utf-8")
        expect_failure(matrix_companion_missing, MATRIX_REQUIRED_MARKERS[21])
        case_count += 1

        matrix_modem_missing = tmpdir / "matrix_modem_missing"
        shutil.copytree(fixture_root, matrix_modem_missing, dirs_exist_ok=True)
        path = matrix_modem_missing / MATRIX_PATH
        path.write_text(remove_marker(path.read_text(encoding="utf-8"), MATRIX_REQUIRED_MARKERS[17]), encoding="utf-8")
        expect_failure(matrix_modem_missing, MATRIX_REQUIRED_MARKERS[17])
        case_count += 1

        survey_forbidden = tmpdir / "survey_forbidden"
        shutil.copytree(fixture_root, survey_forbidden, dirs_exist_ok=True)
        path = survey_forbidden / SURVEY_PATH
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "- `zigux/tests/phase11_build.zig`\n",
                "- `zigux/tests/phase11_build.zig`\n  - `scripts/zigux/check-phase11-header-boundary-packet.py`\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(survey_forbidden, SURVEY_FORBIDDEN_MARKERS[0])
        case_count += 1

        matrix_forbidden = tmpdir / "matrix_forbidden"
        shutil.copytree(fixture_root, matrix_forbidden, dirs_exist_ok=True)
        path = matrix_forbidden / MATRIX_PATH
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "- `zigux/tests/phase11_build.zig`\n",
                "- `zigux/tests/phase11_build.zig`\n  - `scripts/zigux/check-phase11-header-boundary-packet.py`\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(matrix_forbidden, MATRIX_FORBIDDEN_MARKERS[0])
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
