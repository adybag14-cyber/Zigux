#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase11-shared-replay-contract.py"

FILES = {
    "note": "Documentation/zigux/phase11-shared-replay-contract.md",
    "closure_note": "Documentation/zigux/phase11-closure-note.md",
    "lane_note": "Documentation/zigux/phase11-driver-lane-sequencing.md",
}

MARKERS = {
    "note": [
        "# Phase 11 Shared Replay Contract",
        "* `PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful`",
        "* `scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "* `scripts/zigux/check-phase11-build-inventory.py`",
        "* direct GitHub contents reads now materialize `zigux/tests/phase11_build.zig`",
        "* direct GitHub contents reads now materialize `zigux/tests/fixtures/phase11_build_inventory.json`",
        "* the shared `zigux/tests/fixtures/phase11_build_inventory.json` stays part of the current reminder packet and currently records fourteen Phase 11 build test names, thirteen shared `test_step.dependOn(...)` edges, one dedicated `hvc-console-survey` replay, and four explicit shared replay markers beside `zigux/tests/phase11_build.zig`",
        "* `zigux/tests/phase11_build.zig` currently materializes thirteen shared `test_step.dependOn(...)` edges across gpio, bcm2835, DesignWare, header-parity, `hvc_console`, `hvc_console_verify`, and `hvc_cleanup`, plus one dedicated `hvc-console-survey` build step",
        "* `make -C zigux phase11-contract`, `make -C zigux phase11`, and `make -C zigux phase11-hvc-survey` remain present in `zigux/Makefile`, and the bootstrap workflow still names the same shared and dedicated routes",
        "* no shared `validate-phase11.py`",
        "* no shared `make -C zigux phase11-validate` target on `master`",
        "* the shared packet currently uses the shipped `check-phase11-*.py` reminder scripts together with the directly materialized build-backed replay files and the landed inventory fixture rather than a broader validator stack",
        "## Exact Current Checks",
        "* shared reminder packet self-tests: `python3 scripts/zigux/check-phase11-shared-replay-contract.py --self-test`, `python3 scripts/zigux/check-phase11-shared-summary-surfaces.py --self-test`, and `python3 scripts/zigux/check-phase11-build-inventory.py --self-test`",
        "* shared reminder packet direct live checkers: `python3 scripts/zigux/check-phase11-shared-replay-contract.py`, `python3 scripts/zigux/check-phase11-shared-summary-surfaces.py`, and `python3 scripts/zigux/check-phase11-build-inventory.py`",
        "* shared reminder packet live route: `make -C zigux phase11-contract`",
        "* shared build replay: `zig build test --build-file zigux/tests/phase11_build.zig --summary all`",
        "* dedicated HVC archival packet self-test and live checker: `python3 scripts/zigux/check-phase11-hvc-survey-packet.py --self-test` and `python3 scripts/zigux/check-phase11-hvc-survey-packet.py`",
        "* dedicated HVC archival replay routes: `zig build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all` and `make -C zigux phase11-hvc-survey`",
        "* aggregate wrapper: `make -C zigux phase11`",
        "* DesignWare continuity on current `master` stays bounded to `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`; keep that surviving DesignWare continuity packet explicit beside the shared reminder stack while platform-registration scaffolding remains the next same-lane follow-through, and do not reintroduce removed DesignWare survey, slice, teardown, validation-matrix, manifest, or direct replay surfaces as shared evidence until current direct reads materialize them again",
        "* the dedicated HVC archival packet stays bounded to `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-slice.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `drivers/tty/hvc/hvc_console.zig`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, and `make -C zigux phase11-hvc-survey`; keep those landed bounded replay surfaces explicit in shared summaries without widening them into notifier, khvcd, or host-backed execution closure",
    ],
    "closure_note": [
        "# Phase 11 Closure Note",
        "* `PHASE11_CLOSURE_STATUS=shared_packet_truthful`",
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
        "* direct GitHub contents reads now materialize `zigux/tests/phase11_build.zig`",
        "* direct GitHub contents reads now materialize `zigux/tests/fixtures/phase11_build_inventory.json`",
        "* the shared `zigux/tests/fixtures/phase11_build_inventory.json` records the shared test inventory, the dedicated HVC replay split, and the explicit shared replay markers beside `zigux/tests/phase11_build.zig`",
        "* there is no shared `make -C zigux phase11-validate` target on `master`",
        "* no landed shared `validate-phase11.py`",
        "* DesignWare continuity on current `master` stays bounded to `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`; keep that smaller current-master packet explicit beside the shared closure surface while platform-registration scaffolding remains the next same-lane follow-through instead of reintroducing removed survey-era surfaces or collapsing the lane back to scaffold-only continuity",
    ],
    "lane_note": [
        "# Phase 11 Driver Lane Sequencing",
        "shared sequencing lane `P11-Y06`",
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json` anchor",
        "Current `master` now directly materializes `zigux/tests/phase11_build.zig` and `zigux/tests/fixtures/phase11_build_inventory.json`, so the shared sequencing lane should keep those anchors explicit as landed bounded replay evidence together with the shipped `make -C zigux phase11-contract` route instead of preserving older fallback-only wording.",
        "there is no shared `validate-phase11.py`, the shared `zigux/tests/fixtures/phase11_build_inventory.json` is materialized and should stay explicit beside `zigux/tests/phase11_build.zig`",
        "`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
        "do not reintroduce the older DesignWare survey, slice, teardown, validation-matrix, manifest, survey-gate, or direct replay files as landed packet evidence until current direct reads materialize them again",
    ],
}

FORBIDDEN_MARKERS = {
    "note": [
        "* no shared `zigux/tests/fixtures/phase11_build_inventory.json`",
        "* direct GitHub contents reads can still return 404 for `zigux/tests/phase11_build.zig`",
        "* raw GitHub fallback confirms current `master` materializes `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `drivers/tty/hvc/hvc_console_verify.zig`",
        "* `make -C zigux phase11` and `make -C zigux phase11-hvc-survey` remain present in `zigux/Makefile`, and the bootstrap workflow still names the same routes, so treat them as landed bounded replay evidence even when the direct contents bridge still 404s",
        "* DesignWare continuity on current `master` stays bounded to `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_survey.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`; keep that landed bounded DesignWare packet explicit beside the shared reminder stack while platform-registration scaffolding remains the next same-lane follow-through, and do not widen the compile-local teardown or restart proofs into broader hardware-backed closure",
    ],
    "closure_note": [
        "* no landed shared `zigux/tests/fixtures/phase11_build_inventory.json`",
        "* direct GitHub contents reads still materialize `zigux/tests/fixtures/phase11_build_inventory.json`",
        "* DesignWare continuity on current `master` now stays bounded to `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `Documentation/zigux/phase11-dw-wdt-survey.md`, `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, `drivers/watchdog/dw_wdt_verify.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_manifest.json`, `zigux/tests/phase11_dw_wdt_survey.zig`, and `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`; keep that landed bounded packet explicit beside the shared closure surface while platform-registration scaffolding remains the next same-lane follow-through instead of collapsing the lane back to scaffold-only continuity",
    ],
    "lane_note": [
        "no shared `zigux/tests/fixtures/phase11_build_inventory.json`",
        "the contents bridge still materializes `zigux/tests/fixtures/phase11_build_inventory.json`",
        "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
        "`zigux/tests/phase11_dw_wdt_manifest.json`",
    ],
}


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {label}: {marker}")


def expect_forbidden_markers_absent(label: str, text: str) -> None:
    for marker in FORBIDDEN_MARKERS.get(label, []):
        if marker in text:
            raise CheckError(f"forbidden marker in {label}: {marker}")


def run_check(root: Path) -> None:
    for label, relative_path in FILES.items():
        text = read_text(root, relative_path)
        expect_markers(label, text, MARKERS[label])
        expect_forbidden_markers_absent(label, text)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    for label, relative_path in FILES.items():
        write(root / relative_path, "\n".join(MARKERS[label]) + "\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_shared_contract_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_self_test_fixture(fixture_root)
        run_check(fixture_root)

        required_cases = [(FILES["note"], marker) for marker in MARKERS["note"]] + [
            (FILES["note"], "`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`"),
            (FILES["note"], "`scripts/zigux/check-phase11-dw-wdt-packet.py`"),
            (FILES["note"], "`drivers/watchdog/dw_wdt.zig`"),
            (FILES["note"], "`drivers/watchdog/dw_wdt_verify.zig`"),
            (FILES["note"], "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`"),
            (FILES["note"], "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`"),
            (FILES["note"], "`Documentation/zigux/phase11-hvc-console-survey.md`"),
            (FILES["note"], "`Documentation/zigux/phase11-hvc-console-slice.md`"),
            (FILES["note"], "`Documentation/zigux/phase11-hvc-console-teardown-note.md`"),
            (FILES["note"], "`drivers/tty/hvc/hvc_console.zig`"),
            (FILES["note"], "`zigux/tests/phase11_hvc_console_manifest.json`"),
            (FILES["note"], "`zigux/tests/phase11_hvc_console.zig`"),
            (FILES["note"], "`zigux/tests/phase11_hvc_console_survey.zig`"),
            (FILES["note"], "`zigux/tests/phase11_hvc_console_modem_control_split.zig`"),
            (FILES["note"], "`zigux/tests/phase11_hvc_console_poll_retry_split.zig`"),
            (FILES["note"], "`zigux/tests/phase11_hvc_cleanup.zig`"),
            (FILES["note"], "`drivers/tty/hvc/hvc_console_sysrq.zig`"),
            (FILES["note"], "`make -C zigux phase11-hvc-survey`"),
            (FILES["closure_note"], MARKERS["closure_note"][0]),
            (FILES["closure_note"], MARKERS["closure_note"][1]),
            (FILES["closure_note"], MARKERS["closure_note"][2]),
            (FILES["closure_note"], MARKERS["closure_note"][3]),
            (FILES["closure_note"], MARKERS["closure_note"][4]),
            (FILES["closure_note"], MARKERS["closure_note"][5]),
            (FILES["closure_note"], MARKERS["closure_note"][6]),
            (FILES["closure_note"], MARKERS["closure_note"][7]),
            (FILES["closure_note"], MARKERS["closure_note"][8]),
            (FILES["closure_note"], MARKERS["closure_note"][9]),
            (FILES["lane_note"], MARKERS["lane_note"][0]),
            (FILES["lane_note"], MARKERS["lane_note"][1]),
            (FILES["lane_note"], MARKERS["lane_note"][2]),
            (FILES["lane_note"], MARKERS["lane_note"][3]),
            (FILES["lane_note"], MARKERS["lane_note"][4]),
            (FILES["lane_note"], MARKERS["lane_note"][5]),
            (FILES["lane_note"], MARKERS["lane_note"][6]),
            (FILES["lane_note"], MARKERS["lane_note"][7]),
        ]

        for idx, (relative_path, marker) in enumerate(required_cases, start=1):
            case_root = tmpdir / f"required_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / relative_path
            path.write_text(
                path.read_text(encoding="utf-8").replace(marker + "\n", "", 1).replace(marker, "", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        forbidden_cases = [
            ("note", FORBIDDEN_MARKERS["note"][0]),
            ("note", FORBIDDEN_MARKERS["note"][1]),
            ("note", FORBIDDEN_MARKERS["note"][2]),
            ("note", FORBIDDEN_MARKERS["note"][3]),
            ("note", FORBIDDEN_MARKERS["note"][4]),
            ("closure_note", FORBIDDEN_MARKERS["closure_note"][0]),
            ("closure_note", FORBIDDEN_MARKERS["closure_note"][1]),
            ("closure_note", FORBIDDEN_MARKERS["closure_note"][2]),
            ("lane_note", FORBIDDEN_MARKERS["lane_note"][0]),
            ("lane_note", FORBIDDEN_MARKERS["lane_note"][1]),
            ("lane_note", FORBIDDEN_MARKERS["lane_note"][2]),
            ("lane_note", FORBIDDEN_MARKERS["lane_note"][3]),
        ]

        for idx, (label, marker) in enumerate(forbidden_cases, start=1):
            case_root = tmpdir / f"forbidden_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            expect_failure(case_root, marker)

        missing_file_cases = list(FILES.values())
        for idx, relative_path in enumerate(missing_file_cases, start=1):
            case_root = tmpdir / f"missing_file_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            (case_root / relative_path).unlink()
            expect_failure(case_root, relative_path)

        print("PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST=pass")
        print(
            "PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT="
            f"{len(required_cases) + len(forbidden_cases) + len(missing_file_cases)}"
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
        print(f"PHASE11_SHARED_REPLAY_CONTRACT=fail: {exc}")
        return 1

    print("PHASE11_SHARED_REPLAY_CONTRACT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
