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
    "* `scripts/zigux/check-phase11-shared-summary-surfaces.py`",
    "* direct GitHub contents reads can still return 404 for `zigux/tests/phase11_build.zig`",
    "* raw GitHub fallback confirms current `master` materializes `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `drivers/tty/hvc/hvc_console_verify.zig`",
    "* `make -C zigux phase11` and `make -C zigux phase11-hvc-survey` remain present in `zigux/Makefile`, and the bootstrap workflow still names the same routes, so treat them as landed bounded replay evidence even when the direct contents bridge still 404s",
    "* no shared `validate-phase11.py`",
    "* no shared `make -C zigux phase11-validate` target on `master`",
    "* no shared `zigux/tests/fixtures/phase11_build_inventory.json`",
    "* DesignWare continuity on current `master` stays bounded to `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, `drivers/watchdog/dw_wdt.zig`, and `drivers/watchdog/dw_wdt_verify.zig`; platform-registration scaffolding remains the next same-lane follow-through, while the direct teardown and restart proofs stay compile-local and host-free rather than broader hardware-backed closure",
]

REQUIRED_MARKERS = {
    "closure_note": [
        "# Phase 11 Closure Note",
        "`Documentation/zigux/phase11-shared-replay-contract.md`",
        "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "`drivers/tty/hvc/hvc_console_verify.zig`",
        "no landed shared `validate-phase11.py`",
    ],
    "lane_note": [
        "# Phase 11 Driver Lane Sequencing",
        "shared sequencing lane `P11-Y06`",
        "`Documentation/zigux/phase11-closure-note.md`",
        "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "`drivers/tty/hvc/hvc_console_verify.zig`",
        "there is no shared `validate-phase11.py`",
    ],
    "docs_root": [
        "Phase 11 notes -",
        "`Documentation/zigux/phase11-shared-replay-contract.md`",
        "`hvc_cleanup()`",
        "`drivers/tty/hvc/hvc_console_verify.zig`",
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
        "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
        "`zigux/tests/phase11_hvc_console_modem_control_split.zig`",
        "`zigux/tests/phase11_hvc_console_poll_retry_split.zig`",
        "`drivers/tty/hvc/hvc_console_sysrq.zig`",
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
        "`zigux/tests/phase11_hvc_cleanup.zig`",
        "`drivers/tty/hvc/hvc_console_verify.zig`",
    ],
}

FORBIDDEN_MARKERS = {
    "contract_note": [
        "* direct GitHub contents reads do not materialize `zigux/tests/phase11_build.zig`",
        "* direct GitHub contents reads also do not materialize the previously referenced direct replay files `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, and `drivers/tty/hvc/hvc_console_verify.zig`",
        "* `make -C zigux phase11` and `make -C zigux phase11-hvc-survey` remain present in `zigux/Makefile`, and the bootstrap workflow still names the same routes, but treat them as reminder-only configuration markers until the missing Phase 11 build file and direct replay files land again",
        "* raw GitHub fallback confirms current `master` materializes `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `drivers/watchdog/dw_wdt.zig`, and `drivers/tty/hvc/hvc_console_verify.zig`",
        "* DesignWare continuity on current `master` stays bounded to `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-packet.py`, and `drivers/watchdog/dw_wdt.zig`; direct teardown and failure-mode parity remains a future same-lane follow-through rather than shipped `drivers/watchdog/dw_wdt_verify.zig` evidence",
    ],
}

REQUIRED_CONTRACT_MARKER_INDICES = [3, 4, 5, 8, 9]


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

        required_cases: list[tuple[str, str]] = [
            (FILES["contract_note"], CONTRACT_MARKERS[idx])
            for idx in REQUIRED_CONTRACT_MARKER_INDICES
        ]
        for label, markers in REQUIRED_MARKERS.items():
            for marker in markers:
                required_cases.append((FILES[label], marker))

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
        ]

        for idx, (label, marker) in enumerate(forbidden_cases, start=1):
            case_root = tmpdir / f"forbidden_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(
                path.read_text(encoding="utf-8") + marker + "\n",
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        total_case_count = len(required_cases) + len(forbidden_cases)
        print("PHASE11_SHARED_SUMMARY_SURFACES_SELF_TEST=pass")
        print(f"PHASE11_SHARED_SUMMARY_SURFACES_SELF_TEST_CASE_COUNT={total_case_count}")
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
