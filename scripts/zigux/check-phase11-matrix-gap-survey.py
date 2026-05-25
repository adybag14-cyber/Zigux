#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import tempfile
from pathlib import Path

SURVEY_PATH = "Documentation/zigux/phase11-validation-matrix-gap-survey.md"
REQUIRED_MARKERS = [
    "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
    "lane: `P11-Y06`",
    "Authenticated GitHub contents rereads in this run rematerialize the bcm2835, gpio watchdog, HVC console, and DesignWare driver-local Phase 11 matrix notes named by the roadmap on current `master`.",
    "The currently reread driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
    "3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays",
    "The same narrower inventory also records 3 adjunct build replays through `zigux/tests/phase11_hvc_hv_ops_layout_build.zig`, `zigux/tests/phase11_hvc_export_surface_layout_build.zig`, and `zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "The same narrower continuity packet also stays `layout_assert`-backed through `zigux/tests/phase11_hvc_hv_ops_layout_proof.zig` and `zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
    "The directly readable HVC current-head packet also now includes the standalone `zigux/tests/phase11_hvc_targetless_unregister_gap.zig` witness and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig` build shard",
    "The same narrower continuity packet also keeps the dedicated `scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py` guard explicit through `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test` and `python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py`",
    "The same narrower continuity packet now also records 2 focused direct build checker routes through `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py --self-test` and `python3 scripts/zigux/check-phase11-focused-direct-build-replays.py`, together with 2 focused direct build replays through `zigux/tests/phase11_hvc_modem_control_proof_build.zig` and `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`.",
    "The shared `phase11-validate` route also now carries `zigux/tests/phase11_hvc_modem_control_proof_build.zig` as a focused HVC teardown-or-failure-mode proof outside the narrower three-entry build inventory",
    "The shared `phase11-validate` route also now carries `zigux/tests/phase11_dw_wdt_restart_build.zig` and `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig` as focused watchdog teardown-or-failure-mode proofs outside the narrower three-entry HVC build inventory, so keep those shared watchdog replay routes explicit beside the returned driver-local matrices instead of reducing the shared gate to HVC-only proof coverage.",
    "Current `master` also materializes `scripts/zigux/validate-phase11.py` and `zigux/Makefile`, and the live Makefile exposes `make -C zigux phase11-validate`",
    "`bcm2835_wdt`: authenticated GitHub contents rereads now rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "The returned bcm2835 matrix also keeps its bounded timeout, probe-summary ownership, runtime register modeling, restart-or-poweroff intent, and teardown-note packet explicit instead of reducing the bcm2835 lane to a presence-only roster entry while leaving bcm2835-only reminder wording, replay claims, and platform-backed execution in the bcm2835 owner lane.",
    "`gpio_wdt`: `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md` is directly readable on current `master`, and it keeps the bounded descriptor, platform-drvdata, teardown, registration-handoff, register-device request, and failure-mode parity review packet explicit without claiming live GPIO descriptor execution or platform registration.",
    "`dw_wdt`: authenticated GitHub contents rereads now rematerialize `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
]
FORBIDDEN_MARKERS = [
    "Authenticated GitHub contents rereads in this run rematerialize the gpio watchdog and HVC console driver-local Phase 11 matrix notes named by the roadmap, while raw `master` fallback rereads also rematerialize the bcm2835 and DesignWare driver-local Phase 11 matrix notes on current `master`",
    "`PHASE11_MATRIX_GAP_STATUS=driver_local_matrix_roster_incomplete_on_current_master`",
    "Current direct contents reads in this run rematerialize the gpio watchdog and HVC console driver-local Phase 11 matrix notes named by the roadmap, but they do not rematerialize the bcm2835 or DesignWare driver-local matrix notes on current `master`",
    "Current direct contents reads in this run do not rematerialize `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md` or `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
]
_SELF_PATH = Path(__file__).resolve()
_FIXTURE_ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) > 2 else _SELF_PATH.parent
FIXTURE_TEXT = _FIXTURE_ROOT.joinpath(SURVEY_PATH).read_text(encoding="utf-8") if _FIXTURE_ROOT.joinpath(SURVEY_PATH).exists() else ""


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


def expect_failure(root: Path, fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if fragment not in str(exc):
            raise AssertionError(fragment) from exc
        return
    raise AssertionError(fragment)


def remove_marker(text: str, marker: str) -> str:
    pattern = r"\s+".join(re.escape(part) for part in marker.split())
    updated_text, count = re.subn(pattern, "", text, flags=re.MULTILINE)
    if count < 1:
        raise AssertionError(marker)
    return updated_text


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_matrix_gap_"))
    try:
        fixture_root = tmpdir / "fixture"
        target = fixture_root / SURVEY_PATH
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(FIXTURE_TEXT, encoding="utf-8")
        run_check(fixture_root)
        for index, marker in enumerate(REQUIRED_MARKERS, start=1):
            case_root = tmpdir / f"missing_marker_{index}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / SURVEY_PATH
            path.write_text(remove_marker(path.read_text(encoding="utf-8"), marker), encoding="utf-8")
            expect_failure(case_root, marker)
        for index, marker in enumerate(FORBIDDEN_MARKERS, start=1):
            case_root = tmpdir / f"forbidden_marker_{index}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / SURVEY_PATH
            path.write_text(path.read_text(encoding="utf-8") + "\n" + marker + "\n", encoding="utf-8")
            expect_failure(case_root, marker)
        print("PHASE11_MATRIX_GAP_SURVEY_SELF_TEST=pass")
        print(
            "PHASE11_MATRIX_GAP_SURVEY_SELF_TEST_CASE_COUNT="
            f"{len(REQUIRED_MARKERS) + len(FORBIDDEN_MARKERS)}"
        )
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
