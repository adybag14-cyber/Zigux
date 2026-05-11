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
        "* `PHASE11_SHARED_REPLAY_STATUS=shared_packet_drift_recorded`",
        "* `Documentation/zigux/phase11-driver-lane-sequencing.md`",
        "* there is no shared `zigux/tests/phase11_build.zig` on current `master`",
        "* there is no shared `make -C zigux phase11-hvc-survey` route in this tree",
        "Prefer one shared note or checker at a time until the surviving closure surfaces stop naming missing build routes, missing replay files, or missing helper files.",
    ],
    "closure_note": [
        "# Phase 11 Closure Note",
        "* `PHASE11_CLOSURE_STATUS=shared_packet_drift_recorded`",
        "* `Documentation/zigux/phase11-shared-replay-contract.md`",
        "* `scripts/zigux/check-phase11-shared-replay-contract.py`",
        "* DesignWare watchdog: `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `scripts/zigux/check-phase11-dw-wdt-failure-matrix.py`, and `scripts/zigux/check-phase11-dw-wdt-packet.py`",
        "* there is no shared `zigux/tests/phase11_build.zig` on current `master`",
        "The next honest shared-lane follow-through is to repair `Documentation/zigux/phase11-hvc-console-survey.md` so the surviving HVC reminder packet stops naming missing shared build routes and helper files.",
    ],
    "lane_note": [
        "# Phase 11 Driver Lane Sequencing",
        "shared sequencing lane `P11-Y06` owns the shared packet truthfulness surfaces only: `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, and `scripts/zigux/check-phase11-shared-replay-contract.py`",
        "The shared packet surfaces still living together on current `master` are only `Documentation/zigux/phase11-shared-replay-contract.md`, `Documentation/zigux/phase11-closure-note.md`, `Documentation/zigux/phase11-driver-lane-sequencing.md`, and `scripts/zigux/check-phase11-shared-replay-contract.py`.",
        "Keep the shared-versus-dedicated split explicit: the shared packet stays parked on the two shared notes, the lane-sequencing note, and the shared contract checker, while the driver-local evidence stays with the owning lane.",
        "Keep the current validator posture explicit: there is no shared `zigux/tests/phase11_build.zig`, `zigux/tests/fixtures/phase11_build_inventory.json`, `make -C zigux phase11`, `make -C zigux phase11-hvc-survey`, or `validate-phase11.py` on `master`, so reminder-surface edits should stay aligned with the surviving shared note-and-checker packet instead of implying a broader replay or validator stack.",
    ],
}

SELF_TEST_CASE_COUNT = 6


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


def run_check(root: Path) -> None:
    for label, relative_path in FILES.items():
        expect_markers(label, read_text(root, relative_path), MARKERS[label])


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
        build_self_test_fixture(tmpdir)
        run_check(tmpdir)

        cases = [
            (FILES["note"], MARKERS["note"][3]),
            (FILES["note"], MARKERS["note"][4]),
            (FILES["closure_note"], MARKERS["closure_note"][4]),
            (FILES["closure_note"], MARKERS["closure_note"][6]),
            (FILES["lane_note"], MARKERS["lane_note"][2]),
            (FILES["lane_note"], MARKERS["lane_note"][4]),
        ]

        for idx, (relative_path, marker) in enumerate(cases, start=1):
            case_root = tmpdir / f"case_{idx}"
            shutil.copytree(tmpdir, case_root, dirs_exist_ok=True)
            path = case_root / relative_path
            path.write_text(path.read_text(encoding="utf-8").replace(marker + "\n", "", 1), encoding="utf-8")
            expect_failure(case_root, marker)

        print("PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST=pass")
        print(f"PHASE11_SHARED_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
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
