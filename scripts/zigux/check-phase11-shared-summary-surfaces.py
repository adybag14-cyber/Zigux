#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

FILES = {
    "contract_note": "Documentation/zigux/phase11-shared-replay-contract.md",
    "closure_note": "Documentation/zigux/phase11-closure-note.md",
    "lane_note": "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "docs_root": "Documentation/zigux/README.md",
    "review_checklist": "Documentation/zigux/review-checklist.md",
    "scripts_root": "scripts/zigux/README.md",
    "tests_root": "zigux/tests/README.md",
    "tests_companion": "Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md",
}

CONTRACT_MARKERS = [
    "# Phase 11 Shared Replay Contract",
    "* `PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful`",
    "* `scripts/zigux/check-phase11-build-inventory.py`",
    "* direct GitHub contents reads can still return 404 for `zigux/tests/phase11_build.zig`",
    "* direct GitHub contents reads still materialize `zigux/tests/fixtures/phase11_build_inventory.json`",
    "* raw GitHub fallback confirms current `master` materializes `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `drivers/tty/hvc/hvc_console_verify.zig`",
    "* the shared `zigux/tests/fixtures/phase11_build_inventory.json` stays part of the current reminder packet and records the shared test inventory, the dedicated HVC replay split, and the explicit shared replay markers beside `zigux/tests/phase11_build.zig`",
    "* `make -C zigux phase11` and `make -C zigux phase11-hvc-survey` remain present in `zigux/Makefile`, and the bootstrap workflow still names the same routes, so treat them as landed bounded replay evidence even when the direct contents bridge still 404s",
    "* no shared `validate-phase11.py`",
    "* no shared `make -C zigux phase11-validate` target on `master`",
    "* DesignWare continuity on current `master` stays bounded to `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, and `drivers/watchdog/dw_wdt_verify.zig`; platform-registration scaffolding remains the next same-lane follow-through, while the direct teardown and restart proofs stay compile-local and host-free rather than broader hardware-backed closure",
    "* the dedicated HVC archival packet stays bounded to `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-survey.md`, `Documentation/zigux/phase11-hvc-console-teardown-note.md`, `zigux/tests/phase11_hvc_console_manifest.json`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_console_survey.zig`, `zigux/tests/phase11_hvc_console_modem_control_split.zig`, `zigux/tests/phase11_hvc_console_poll_retry_split.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `drivers/tty/hvc/hvc_console_verify.zig`, `drivers/tty/hvc/hvc_console_sysrq.zig`, and `make -C zigux phase11-hvc-survey`; keep those landed bounded replay surfaces explicit in shared summaries without widening them into notifier, khvcd, or host-backed execution closure",
]

REQUIRED_MARKERS = {
    "closure_note": [
        "# Phase 11 Closure Note",
        "`Documentation/zigux/phase11-shared-replay-contract.md`",
        "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
        "direct GitHub contents reads still materialize `zigux/tests/fixtures/phase11_build_inventory.json`",
        "`zigux/tests/phase11_hvc_console.zig`",
        "`zigux/tests/phase11_hvc_console_manifest.json`",
        "`zigux/tests/phase11_hvc_console_survey.zig`",
        "`zigux/tests/phase11_hvc_cleanup.zig`",
        "`drivers/tty/hvc/hvc_console_verify.zig`",
        "`drivers/tty/hvc/hvc_console_sysrq.zig`",
        "`make -C zigux phase11-hvc-survey`",
        "the shared `zigux/tests/fixtures/phase11_build_inventory.json` records the shared test inventory",
        "no landed shared `validate-phase11.py`",
    ],
    "lane_note": [
        "# Phase 11 Driver Lane Sequencing",
        "shared sequencing lane `P11-Y06`",
        "`Documentation/zigux/phase11-closure-note.md`",
        "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
        "the contents bridge still materializes `zigux/tests/fixtures/phase11_build_inventory.json`",
        "there is no shared `validate-phase11.py`, the shared `zigux/tests/fixtures/phase11_build_inventory.json` is materialized and should stay explicit beside `zigux/tests/phase11_build.zig`",
        "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
        "`drivers/tty/hvc/hvc_console.zig`",
        "`zigux/tests/phase11_hvc_console_manifest.json`",
        "`zigux/tests/phase11_hvc_console.zig`",
        "`zigux/tests/phase11_hvc_console_survey.zig`",
        "`zigux/tests/phase11_hvc_cleanup.zig`",
        "`drivers/tty/hvc/hvc_console_verify.zig`",
        "`drivers/tty/hvc/hvc_console_sysrq.zig`",
        "`make -C zigux phase11-hvc-survey`",
        "DesignWare lane `P11-L10` owns `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, and `drivers/watchdog/dw_wdt_verify.zig` as the surviving bounded DesignWare packet",
        "the surviving DesignWare lane evidence is `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, and `drivers/watchdog/dw_wdt_verify.zig`, pinned to `P11-L10`",
    ],
    "docs_root": [
        "Phase 11 notes -",
        "`Documentation/zigux/phase11-shared-replay-contract.md`",
        "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
        "`zigux/tests/phase11_hvc_console_manifest.json`",
        "`zigux/tests/phase11_hvc_console_survey.zig`",
        "`zigux/tests/phase11_hvc_console_modem_control_split.zig`",
        "`zigux/tests/phase11_hvc_console_poll_retry_split.zig`",
        "`zigux/tests/phase11_hvc_cleanup.zig`",
        "`drivers/tty/hvc/hvc_console_verify.zig`",
        "`drivers/tty/hvc/hvc_console_sysrq.zig`",
        "`make -C zigux phase11-hvc-survey`",
    ],
    "review_checklist": [
        "if the change touches the shared Phase 11 simple-driver packet",
        "`Documentation/zigux/phase11-shared-replay-contract.md`",
        "`zigux/tests/phase11_hvc_cleanup.zig`",
        "`drivers/tty/hvc/hvc_console_verify.zig`",
    ],
    "scripts_root": [
        "Phase 11 flow -",
        "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
        "`zigux/tests/phase11_hvc_console.zig`",
        "`drivers/tty/hvc/hvc_console_verify.zig`",
        "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
        "`zigux/tests/phase11_hvc_console_modem_control_split.zig`",
        "`zigux/tests/phase11_hvc_console_poll_retry_split.zig`",
        "`drivers/tty/hvc/hvc_console_sysrq.zig`",
        "`make -C zigux phase11-contract`",
        "`make -C zigux phase11-hvc-survey`",
    ],
    "tests_root": [
        "keep the shared Phase 11 simple-driver packet explicit in the tests root too",
        "`Documentation/zigux/phase11-shared-replay-contract.md`",
        "`zigux/tests/phase11_hvc_cleanup.zig`",
        "`drivers/tty/hvc/hvc_console_verify.zig`",
    ],
    "tests_companion": [
        "## Phase 11 tests-root packet",
        "`Documentation/zigux/phase11-shared-replay-contract.md`",
        "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "`zigux/tests/phase11_hvc_cleanup.zig`",
        "`drivers/tty/hvc/hvc_console_verify.zig`",
    ],
}

FORBIDDEN_MARKERS = {
    "contract_note": [
        "* no shared `zigux/tests/fixtures/phase11_build_inventory.json`",
        "* the shared packet currently uses the shipped `check-phase11-*.py` reminder scripts together with the materialized build-backed replay files rather than a broader validator stack",
        "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
        "`Documentation/zigux/phase11-dw-wdt-survey.md`",
    ],
    "lane_note": [
        "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
        "`Documentation/zigux/phase11-dw-wdt-survey.md`",
    ],
    "scripts_root": [
        "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
        "`Documentation/zigux/phase11-dw-wdt-survey.md`",
        "`Documentation/zigux/phase11-dw-wdt-teardown-note.md`",
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
    contract_text = read_text(root, FILES["contract_note"])
    expect_markers("contract_note", contract_text, CONTRACT_MARKERS)
    expect_forbidden_markers_absent("contract_note", contract_text)

    for label, markers in REQUIRED_MARKERS.items():
        text = read_text(root, FILES[label])
        expect_markers(label, text, markers)
        expect_forbidden_markers_absent(label, text)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / FILES["contract_note"], "\n".join(CONTRACT_MARKERS) + "\n")
    for label, markers in REQUIRED_MARKERS.items():
        write(root / FILES[label], "\n".join(markers) + "\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(f"expected {expected_fragment!r}, got {exc!r}") from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_shared_summary_"))
    try:
        fixture_root = tmpdir / "fixture"
        build_self_test_fixture(fixture_root)
        run_check(fixture_root)

        required_cases = [
            (FILES["contract_note"], CONTRACT_MARKERS[2]),
            (FILES["contract_note"], CONTRACT_MARKERS[4]),
            (FILES["contract_note"], CONTRACT_MARKERS[5]),
            (FILES["contract_note"], CONTRACT_MARKERS[6]),
            (FILES["contract_note"], CONTRACT_MARKERS[10]),
            (FILES["closure_note"], REQUIRED_MARKERS["closure_note"][3]),
            (FILES["closure_note"], REQUIRED_MARKERS["closure_note"][5]),
            (FILES["closure_note"], REQUIRED_MARKERS["closure_note"][6]),
            (FILES["closure_note"], REQUIRED_MARKERS["closure_note"][7]),
            (FILES["closure_note"], REQUIRED_MARKERS["closure_note"][8]),
            (FILES["closure_note"], REQUIRED_MARKERS["closure_note"][9]),
            (FILES["closure_note"], REQUIRED_MARKERS["closure_note"][10]),
            (FILES["closure_note"], REQUIRED_MARKERS["closure_note"][11]),
            (FILES["closure_note"], REQUIRED_MARKERS["closure_note"][12]),
            (FILES["lane_note"], REQUIRED_MARKERS["lane_note"][4]),
            (FILES["lane_note"], REQUIRED_MARKERS["lane_note"][6]),
            (FILES["lane_note"], REQUIRED_MARKERS["lane_note"][7]),
            (FILES["lane_note"], REQUIRED_MARKERS["lane_note"][10]),
            (FILES["lane_note"], REQUIRED_MARKERS["lane_note"][12]),
            (FILES["lane_note"], REQUIRED_MARKERS["lane_note"][13]),
            (FILES["lane_note"], REQUIRED_MARKERS["lane_note"][15]),
            (FILES["lane_note"], REQUIRED_MARKERS["lane_note"][16]),
            (FILES["lane_note"], REQUIRED_MARKERS["lane_note"][17]),
            (FILES["lane_note"], REQUIRED_MARKERS["lane_note"][18]),
            (FILES["docs_root"], REQUIRED_MARKERS["docs_root"][2]),
            (FILES["docs_root"], REQUIRED_MARKERS["docs_root"][3]),
            (FILES["docs_root"], REQUIRED_MARKERS["docs_root"][4]),
            (FILES["docs_root"], REQUIRED_MARKERS["docs_root"][5]),
            (FILES["docs_root"], REQUIRED_MARKERS["docs_root"][6]),
            (FILES["docs_root"], REQUIRED_MARKERS["docs_root"][7]),
            (FILES["docs_root"], REQUIRED_MARKERS["docs_root"][8]),
            (FILES["docs_root"], REQUIRED_MARKERS["docs_root"][9]),
            (FILES["docs_root"], REQUIRED_MARKERS["docs_root"][10]),
            (FILES["review_checklist"], REQUIRED_MARKERS["review_checklist"][2]),
            (FILES["review_checklist"], REQUIRED_MARKERS["review_checklist"][3]),
            (FILES["scripts_root"], REQUIRED_MARKERS["scripts_root"][2]),
            (FILES["scripts_root"], REQUIRED_MARKERS["scripts_root"][3]),
            (FILES["scripts_root"], REQUIRED_MARKERS["scripts_root"][4]),
            (FILES["scripts_root"], REQUIRED_MARKERS["scripts_root"][5]),
            (FILES["scripts_root"], REQUIRED_MARKERS["scripts_root"][6]),
            (FILES["scripts_root"], REQUIRED_MARKERS["scripts_root"][11]),
            (FILES["tests_root"], REQUIRED_MARKERS["tests_root"][2]),
            (FILES["tests_root"], REQUIRED_MARKERS["tests_root"][3]),
            (FILES["tests_companion"], REQUIRED_MARKERS["tests_companion"][0]),
            (FILES["tests_companion"], REQUIRED_MARKERS["tests_companion"][2]),
        ]

        for idx, (relative_path, marker) in enumerate(required_cases, start=1):
            case_root = tmpdir / f"required_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / relative_path
            path.write_text(
                path.read_text(encoding="utf-8").replace(marker + "\n", "", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        forbidden_cases = [
            ("contract_note", FORBIDDEN_MARKERS["contract_note"][0]),
            ("contract_note", FORBIDDEN_MARKERS["contract_note"][1]),
            ("contract_note", FORBIDDEN_MARKERS["contract_note"][2]),
            ("contract_note", FORBIDDEN_MARKERS["contract_note"][3]),
            ("lane_note", FORBIDDEN_MARKERS["lane_note"][0]),
            ("lane_note", FORBIDDEN_MARKERS["lane_note"][1]),
            ("scripts_root", FORBIDDEN_MARKERS["scripts_root"][0]),
            ("scripts_root", FORBIDDEN_MARKERS["scripts_root"][1]),
            ("scripts_root", FORBIDDEN_MARKERS["scripts_root"][2]),
        ]

        for idx, (label, marker) in enumerate(forbidden_cases, start=1):
            case_root = tmpdir / f"forbidden_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            expect_failure(case_root, marker)

        print("PHASE11_SHARED_SUMMARY_SURFACES_SELF_TEST=pass")
        print(
            f"PHASE11_SHARED_SUMMARY_SURFACES_SELF_TEST_CASE_COUNT="
            f"{len(required_cases) + len(forbidden_cases)}"
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
        print(f"PHASE11_SHARED_SUMMARY_SURFACES=fail: {exc}")
        return 1

    print("PHASE11_SHARED_SUMMARY_SURFACES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
