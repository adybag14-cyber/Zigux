#!/usr/bin/env python3
"""Fail-closed checker for the current Phase 11 matrix-gap survey."""

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
from pathlib import Path


SURVEY_PATH = "Documentation/zigux/phase11-validation-matrix-gap-survey.md"

REQUIRED_MARKERS = [
    "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
    "lane: `P11-L01`",
    "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`",
    "`scripts/zigux/check-phase11-matrix-gap-survey.py`",
    "Current Repo Reality - `Documentation/zigux/phase11-validation-matrix-gap-survey.md` - `Documentation/zigux/phase11-driver-lane-sequencing.md` - `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` - `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` - `Documentation/zigux/phase11-hvc-console-validation-matrix.md` - `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` - `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`",
    "`python3 scripts/zigux/check-phase11-matrix-gap-survey.py`",
    "`scripts/zigux/check-phase11-validation-matrix-gap-survey.py`",
    "`python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`",
    "`scripts/zigux/check-phase11-build-inventory.py`",
    "`scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "`python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "Authenticated GitHub contents rereads in this run rematerialize the gpio watchdog and HVC console driver-local Phase 11 matrix notes named by the roadmap, while raw `master` fallback rereads also rematerialize the bcm2835 and DesignWare driver-local matrix notes on current `master`",
    "The reread driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "Authenticated contents reads in this run still do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` or `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, but raw `master` fallback does",
    "`Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains useful adjacent shared evidence, but it is not one of the driver-local Phase 11 validation matrices named by the roadmap",
    "`zigux/tests/fixtures/phase11_build_inventory.json` still records the narrower current-head HVC continuity packet",
    "3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays",
    "does not stand in for a whole-Phase-11 replay roster while the current reread expansion now covers all four driver-local matrix notes plus the existing HVC continuity packet",
    "The same narrower inventory also records 3 adjunct build replays through `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "The same narrower continuity packet also stays `layout_assert`-backed through `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` and `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "That adjacent HVC-only proof packet still leaves a roadmap-facing ABI proof gap on current `master`: the repo does not yet rematerialize a broader shared replay or survey route that would carry cross-driver public-struct ABI proof beyond those surviving `layout_assert` shards",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "The directly readable HVC current-head packet also now includes the standalone `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` witness and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` build shard",
    "The same narrower continuity packet also keeps the dedicated `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` guard explicit through `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test` and `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "The dedicated `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` route also stays directly readable beside that smaller proof inventory and standalone witness pair",
    "The standalone `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` witness and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` build shard also stay directly readable beside that smaller proof inventory",
    "`bcm2835_wdt`: raw `master` fallback rereads rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` on current `master`",
    "`gpio_wdt`: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` is directly readable on current `master`",
    "`hvc_console`: `Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "`dw_wdt`: raw `master` fallback rereads rematerialize `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` on current `master`",
]

FORBIDDEN_MARKERS = [
    "`PHASE11_MATRIX_GAP_STATUS=gpio_and_hvc_matrices_direct_readback_only`",
    "Current repo rereads in this run rematerialize the gpio watchdog and HVC console driver-local Phase 11 matrix notes named by the roadmap, but they do not rematerialize the bcm2835 or DesignWare driver-local matrix notes on current `master`",
    "The directly readable driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` and `Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
    "Current direct contents reads in this run do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` or `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "`bcm2835_wdt`: current direct contents reads do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`dw_wdt`: current direct contents reads do not rematerialize `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
]

FIXTURE_TEXT = """# Phase 11 Validation Matrix Gap Survey

- `PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`
- lane: `P11-L01`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `scripts/zigux/check-phase11-matrix-gap-survey.py`
- Current Repo Reality
- `Documentation/zigux/phase11-validation-matrix-gap-survey.md`
- `Documentation/zigux/phase11-driver-lane-sequencing.md`
- `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md`
- `python3 scripts/zigux/check-phase11-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `python3 scripts/zigux/check-phase11-validation-matrix-gap-survey.py`
- `scripts/zigux/check-phase11-build-inventory.py`
- `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`
- Authenticated GitHub contents rereads in this run rematerialize the gpio watchdog and HVC console driver-local Phase 11 matrix notes named by the roadmap, while raw `master` fallback rereads also rematerialize the bcm2835 and DesignWare driver-local matrix notes on current `master`, so the shared matrix packet should keep all four driver-local validation matrices explicit while recording that the contents bridge in this runtime still clips the bcm2835 and DesignWare notes.
- The reread driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`.
- Authenticated contents reads in this run still do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` or `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, but raw `master` fallback does.
- `Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md` remains useful adjacent shared evidence, but it is not one of the driver-local Phase 11 validation matrices named by the roadmap.
- `zigux/tests/fixtures/phase11_build_inventory.json` still records the narrower current-head HVC continuity packet.
- 3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.
- the shared build inventory does not stand in for a whole-Phase-11 replay roster while the current reread expansion now covers all four driver-local matrix notes plus the existing HVC continuity packet.
- The same narrower inventory also records 3 adjunct build replays through `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig`, so keep those current-head HVC build routes explicit as adjacent continuity evidence rather than treating them as a cross-driver replay roster.
- The same narrower continuity packet also stays `layout_assert`-backed through `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` and `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`, so keep those surviving ABI proof shards explicit as adjacent HVC continuity evidence instead of treating the three build routes as prose-only review support.
- That adjacent HVC-only proof packet still leaves a roadmap-facing ABI proof gap on current `master`: the repo does not yet rematerialize a broader shared replay or survey route that would carry cross-driver public-struct ABI proof beyond those surviving `layout_assert` shards.
- `zigux/tests/phase11_hvc_targetless_unregister_gap.zig`
- `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`
- The directly readable HVC current-head packet also now includes the standalone `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` witness and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` build shard, so keep that targetless-unregister failure-mode evidence explicit beside the narrower three-proof inventory instead of silently collapsing it into the shared proof-backed roster.
- The same narrower continuity packet also keeps the dedicated `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` guard explicit through `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test` and `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`, so keep that focused witness-check route explicit beside the standalone witness pair instead of treating the pair as unchecked prose evidence.
- `bcm2835_wdt`: raw `master` fallback rereads rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` on current `master`
- `gpio_wdt`: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` is directly readable on current `master`
- `hvc_console`: `Documentation/zigux/phase11-hvc-console-validation-matrix.md`
- The dedicated `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` route also stays directly readable beside that smaller proof inventory and standalone witness pair.
- The standalone `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` witness and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` build shard also stay directly readable beside that smaller proof inventory.
- `dw_wdt`: raw `master` fallback rereads rematerialize `Documentation/zigux/phase11-dw-wdt-validation-matrix.md` on current `master`
"""


class CheckError(RuntimeError):
    pass


def normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def run_check(root: Path) -> None:
    survey_text = read_text(root, SURVEY_PATH)
    normalized = normalize_whitespace(survey_text)
    for marker in REQUIRED_MARKERS:
        if normalize_whitespace(marker) not in normalized:
            raise CheckError(f"missing marker in {SURVEY_PATH}: {marker}")
    for marker in FORBIDDEN_MARKERS:
        if normalize_whitespace(marker) in normalized:
            raise CheckError(f"forbidden marker in {SURVEY_PATH}: {marker}")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root / SURVEY_PATH, FIXTURE_TEXT)


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {fragment!r}")


def remove_marker(text: str, marker: str) -> str:
    pattern = r"\s+".join(re.escape(part) for part in marker.split())
    updated_text, count = re.subn(pattern, "", text, flags=re.MULTILINE)
    if count < 1:
        raise AssertionError(f"expected to remove marker from fixture: {marker!r}")
    return updated_text


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_matrix_gap_"))
    try:
        fixture = tmpdir / "fixture"
        build_fixture(fixture)
        run_check(fixture)

        required_self_test_markers = (
            REQUIRED_MARKERS[0],
            REQUIRED_MARKERS[9],
            REQUIRED_MARKERS[14],
            REQUIRED_MARKERS[20],
            REQUIRED_MARKERS[22],
            REQUIRED_MARKERS[25],
            REQUIRED_MARKERS[26],
            REQUIRED_MARKERS[27],
            REQUIRED_MARKERS[28],
        )
        for index, marker in enumerate(required_self_test_markers, start=1):
            case_root = tmpdir / f"missing_marker_{index}"
            shutil.copytree(fixture, case_root, dirs_exist_ok=True)
            survey_path = case_root / SURVEY_PATH
            survey_text = survey_path.read_text(encoding="utf-8")
            survey_path.write_text(remove_marker(survey_text, marker), encoding="utf-8")
            expect_failure(case_root, marker)

        for index, marker in enumerate(FORBIDDEN_MARKERS, start=1):
            case_root = tmpdir / f"forbidden_marker_{index}"
            shutil.copytree(fixture, case_root, dirs_exist_ok=True)
            survey_path = case_root / SURVEY_PATH
            survey_path.write_text(
                survey_path.read_text(encoding="utf-8") + "\n" + marker + "\n",
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        missing_file_root = tmpdir / "missing_file"
        shutil.copytree(fixture, missing_file_root, dirs_exist_ok=True)
        (missing_file_root / SURVEY_PATH).unlink()
        expect_failure(missing_file_root, SURVEY_PATH)

        print("PHASE11_MATRIX_GAP_SURVEY_SELF_TEST=pass")
        print("PHASE11_MATRIX_GAP_SURVEY_SELF_TEST_CASE_COUNT=16")
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
        print(f"PHASE11_MATRIX_GAP_SURVEY=fail: {exc}")
        return 1

    print("PHASE11_MATRIX_GAP_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
