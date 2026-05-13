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
        "* direct GitHub contents reads can still return 404 for `zigux/tests/phase11_build.zig`",
        "* direct GitHub contents reads still materialize `zigux/tests/fixtures/phase11_build_inventory.json`",
        "* raw GitHub fallback confirms current `master` materializes `zigux/tests/phase11_build.zig`, `zigux/tests/phase11_gpio_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`, `zigux/tests/phase11_dw_wdt_registration_scaffold.zig`, `zigux/tests/phase11_hvc_console.zig`, `zigux/tests/phase11_hvc_cleanup.zig`, `drivers/watchdog/bcm2835_wdt_verify.zig`, `drivers/watchdog/dw_wdt_verify.zig`, and `drivers/tty/hvc/hvc_console_verify.zig`",
        "* the shared `zigux/tests/fixtures/phase11_build_inventory.json` stays part of the current reminder packet and records the shared test inventory, the dedicated HVC replay split, and the explicit shared replay markers beside `zigux/tests/phase11_build.zig`",
        "* `make -C zigux phase11` and `make -C zigux phase11-hvc-survey` remain present in `zigux/Makefile`, and the bootstrap workflow still names the same routes, so treat them as landed bounded replay evidence even when the direct contents bridge still 404s",
        "* no shared `validate-phase11.py`",
        "* no shared `make -C zigux phase11-validate` target on `master`",
        "* the shared packet currently uses the shipped `check-phase11-*.py` reminder scripts together with the materialized build-backed replay files and the landed inventory fixture rather than a broader validator stack",
    ],
    "closure_note": [
        "# Phase 11 Closure Note",
        "* `PHASE11_CLOSURE_STATUS=shared_packet_truthful`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
        "* direct GitHub contents reads still materialize `zigux/tests/fixtures/phase11_build_inventory.json`",
        "* the shared `zigux/tests/fixtures/phase11_build_inventory.json` records the shared test inventory, the dedicated HVC replay split, and the explicit shared replay markers beside `zigux/tests/phase11_build.zig`",
        "* there is no shared `make -C zigux phase11-validate` target on `master`",
        "* no landed shared `validate-phase11.py`",
    ],
    "lane_note": [
        "# Phase 11 Driver Lane Sequencing",
        "shared sequencing lane `P11-Y06`",
        "`zigux/tests/fixtures/phase11_build_inventory.json` anchor",
        "the contents bridge still materializes `zigux/tests/fixtures/phase11_build_inventory.json`",
        "there is no shared `validate-phase11.py`, the shared `zigux/tests/fixtures/phase11_build_inventory.json` is materialized and should stay explicit beside `zigux/tests/phase11_build.zig`",
    ],
}

FORBIDDEN_MARKERS = {
    "note": [
        "* no shared `zigux/tests/fixtures/phase11_build_inventory.json`",
        "* the shared packet currently uses the shipped `check-phase11-*.py` reminder scripts together with the materialized build-backed replay files rather than a broader validator stack",
    ],
    "closure_note": [
        "* no landed shared `zigux/tests/fixtures/phase11_build_inventory.json`",
    ],
    "lane_note": [
        "no shared `zigux/tests/fixtures/phase11_build_inventory.json`",
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

        required_cases = [
            (FILES["note"], MARKERS["note"][4]),
            (FILES["note"], MARKERS["note"][5]),
            (FILES["note"], MARKERS["note"][6]),
            (FILES["closure_note"], MARKERS["closure_note"][3]),
            (FILES["closure_note"], MARKERS["closure_note"][4]),
            (FILES["lane_note"], MARKERS["lane_note"][2]),
            (FILES["lane_note"], MARKERS["lane_note"][3]),
            (FILES["lane_note"], MARKERS["lane_note"][4]),
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
            ("note", FORBIDDEN_MARKERS["note"][0]),
            ("closure_note", FORBIDDEN_MARKERS["closure_note"][0]),
            ("lane_note", FORBIDDEN_MARKERS["lane_note"][0]),
        ]

        for idx, (label, marker) in enumerate(forbidden_cases, start=1):
            case_root = tmpdir / f"forbidden_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(path.read_text(encoding="utf-8") + marker + "\n", encoding="utf-8")
            expect_failure(case_root, marker)

        print("PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST=pass")
        print(f"PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT={len(required_cases) + len(forbidden_cases)}")
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
