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
    "contributor_sync_note": "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "scripts_readme": "scripts/zigux/README.md",
    "build_inventory": "zigux/tests/fixtures/phase11_build_inventory.json",
    "makefile": "zigux/Makefile",
    "workflow": ".github/workflows/zigux-bootstrap.yml",
}

REQUIRED_MARKERS = {
    "contract_note": [
        "# Phase 11 Shared Replay Contract",
        "PHASE11_SHARED_REPLAY_STATUS=shared_packet_truthful",
        "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "direct GitHub contents reads now materialize `zigux/tests/phase11_build.zig`",
        "direct GitHub contents reads now materialize `zigux/tests/fixtures/phase11_build_inventory.json`",
        "`make -C zigux phase11-contract`, `make -C zigux phase11`, and `make -C zigux phase11-hvc-survey` remain present in `zigux/Makefile`",
        "no shared `validate-phase11.py`",
        "no shared `make -C zigux phase11-validate` target on `master`",
        "shared reminder packet direct live checkers",
        "dedicated HVC archival replay routes: `zig build hvc-console-survey --build-file zigux/tests/phase11_build.zig --summary all` and `make -C zigux phase11-hvc-survey`",
    ],
    "closure_note": [
        "# Phase 11 Closure Note",
        "PHASE11_CLOSURE_STATUS=shared_packet_truthful",
        "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
        "`make -C zigux phase11-contract`",
        "`make -C zigux phase11`",
        "`make -C zigux phase11-hvc-survey`",
        "direct GitHub contents reads now materialize `zigux/tests/phase11_build.zig`",
        "direct GitHub contents reads now materialize `zigux/tests/fixtures/phase11_build_inventory.json`",
        "the shared `zigux/tests/fixtures/phase11_build_inventory.json` records the shared test inventory",
        "there is no shared `make -C zigux phase11-validate` target on `master`",
        "no landed shared `validate-phase11.py`",
    ],
    "lane_note": [
        "# Phase 11 Driver Lane Sequencing",
        "shared sequencing lane `P11-Y06`",
        "`Documentation/zigux/phase11-closure-note.md`",
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
        "The shared Phase 11 packet still living together on current `master` is the reminder-and-checker stack:",
        "`make -C zigux phase11-contract`",
        "current `master` now directly materializes `zigux/tests/phase11_build.zig` and `zigux/tests/fixtures/phase11_build_inventory.json`",
        "there is no shared `validate-phase11.py`",
        "the shipped `make -C zigux phase11-contract` route",
    ],
    "contributor_sync_note": [
        "# Phase 10, 11, and 13 Contributor Surface Sync",
        "## Phase 11 contributor packet",
        "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
        "`make -C zigux phase11-contract`",
        "the exact shared `zig build test --build-file zigux/tests/phase11_build.zig --summary all` replay",
    ],
    "scripts_readme": [
        "Phase 11 flow - the current shared Phase 11 scripts-root reminder on `master` is",
        "`Documentation/zigux/phase11-shared-replay-contract.md`",
        "`scripts/zigux/check-phase11-shared-replay-contract.py`",
        "`scripts/zigux/check-phase11-shared-summary-surfaces.py`",
        "`scripts/zigux/check-phase11-build-inventory.py`",
        "`zigux/tests/fixtures/phase11_build_inventory.json`",
        "`zig build test --build-file zigux/tests/phase11_build.zig --summary all`",
        "`make -C zigux phase11-contract`",
        "`make -C zigux phase11`",
        "`make -C zigux phase11-hvc-survey`",
        "`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
        "`drivers/watchdog/dw_wdt.zig`",
        "`drivers/watchdog/dw_wdt_verify.zig`",
        "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`",
    ],
    "build_inventory": [
        '"phase11-hvc-console-survey-tests"',
        '"dedicated_survey_replays"',
        '"zigux/tests/phase11_hvc_console_survey.zig"',
        '"shared_replay_markers"',
        '"zigux/tests/phase11_hvc_console_poll_retry_split.zig"',
    ],
    "makefile": [
        "PHONY += phase11-contract phase11-test phase11-hvc-survey phase11",
        "phase11-contract:",
        "phase11: phase11-contract phase11-test phase11-hvc-survey",
    ],
    "workflow": [
        "- name: Self-test Phase 11 shared replay contract checker",
        "- name: Self-test Phase 11 shared summary-surfaces checker",
        "- name: Run Phase 11 shared replay contract checker",
        "- name: Check Phase 11 shared summary surfaces",
        "- name: Run dedicated Phase 11 hvc survey replay",
        "run: zig build test --build-file zigux/tests/phase11_build.zig --summary all",
        "run: make -C zigux phase11-contract",
        "run: make -C zigux phase11-hvc-survey",
    ],
}

FORBIDDEN_MARKERS = {
    "contract_note": [
        "direct GitHub contents reads can still return 404 for `zigux/tests/phase11_build.zig`",
        "raw GitHub fallback confirms current `master` materializes `zigux/tests/phase11_build.zig`",
    ],
    "closure_note": [
        "direct GitHub contents reads can still return 404 for `zigux/tests/phase11_build.zig`",
        "raw GitHub fallback confirms current `master` materializes `zigux/tests/phase11_build.zig`",
    ],
    "lane_note": [
        "the direct contents bridge can still 404 on `zigux/tests/phase11_build.zig`",
        "raw-fallback materialization story",
    ],
    "scripts_readme": [
        "`zigux/tests/phase11_dw_wdt_survey.zig`",
        "`Documentation/zigux/phase11-dw-wdt-survey.md`",
        "`Documentation/zigux/phase11-dw-wdt-validation-matrix.md`",
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
    for label, relative_path in FILES.items():
        text = read_text(root, relative_path)
        expect_markers(label, text, REQUIRED_MARKERS[label])
        expect_forbidden_markers_absent(label, text)



def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")



def build_self_test_fixture(root: Path) -> None:
    for label, relative_path in FILES.items():
        lines = list(REQUIRED_MARKERS[label])
        if label == "scripts_readme":
            lines = [line for line in lines if line not in FORBIDDEN_MARKERS["scripts_readme"]]
        write(root / relative_path, "\n".join(lines) + "\n")



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
            (label, marker)
            for label, markers in REQUIRED_MARKERS.items()
            for marker in markers
        ]
        for idx, (label, marker) in enumerate(required_cases, start=1):
            case_root = tmpdir / f"required_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            path = case_root / FILES[label]
            path.write_text(
                path.read_text(encoding="utf-8")
                .replace(marker + "\n", "", 1)
                .replace(marker, "", 1),
                encoding="utf-8",
            )
            expect_failure(case_root, marker)

        forbidden_cases = [
            (label, marker)
            for label, markers in FORBIDDEN_MARKERS.items()
            for marker in markers
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

        missing_file_cases = list(FILES.values())
        for idx, relative_path in enumerate(missing_file_cases, start=1):
            case_root = tmpdir / f"missing_file_{idx}"
            shutil.copytree(fixture_root, case_root, dirs_exist_ok=True)
            (case_root / relative_path).unlink()
            expect_failure(case_root, relative_path)

        print("PHASE11_SHARED_SUMMARY_SURFACES_SELF_TEST=pass")
        print(
            "PHASE11_SHARED_SUMMARY_SURFACES_SELF_TEST_CASE_COUNT="
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
        print(f"PHASE11_SHARED_SUMMARY_SURFACES=fail: {exc}")
        return 1

    print("PHASE11_SHARED_SUMMARY_SURFACES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
