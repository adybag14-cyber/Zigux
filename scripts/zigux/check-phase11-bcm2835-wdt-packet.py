#!/usr/bin/env python3
"""Fail-closed checker for the bounded Phase 11 bcm2835 watchdog packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

SCRIPT_PATH = "scripts/zigux/check-phase11-bcm2835-wdt-packet.py"

REQUIRED_FILES = {
    "manifest": "zigux/tests/phase11_bcm2835_wdt_manifest.json",
    "survey_note": "Documentation/zigux/phase11-bcm2835-wdt-survey.md",
    "validation_matrix": "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "shared_contract": "Documentation/zigux/phase11-shared-replay-contract.md",
    "closure_note": "Documentation/zigux/phase11-closure-note.md",
    "lane_note": "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "test_replay": "zigux/tests/phase11_bcm2835_wdt.zig",
    "survey_replay": "zigux/tests/phase11_bcm2835_wdt_survey.zig",
    "verify_replay": "drivers/watchdog/bcm2835_wdt_verify.zig",
}

SURVEY_NOTE_MARKERS = [
    "phase11-bcm2835-wdt-tests",
    "phase11-bcm2835-wdt-verify-tests",
    "phase11-bcm2835-wdt-survey-tests",
    "drivers/watchdog/bcm2835_wdt_verify.zig",
]

VALIDATION_MATRIX_MARKERS = [
    "phase11-bcm2835-wdt-tests",
    "phase11-bcm2835-wdt-verify-tests",
    "phase11-bcm2835-wdt-survey-tests",
    "drivers/watchdog/bcm2835_wdt_verify.zig",
    "current scheduled watchdog-family continuity for this archived bcm2835 packet is tracked through `P11-L08`",
]

# Keep this checker on the bcm2835-owned packet plus the shared Phase 11 notes
# that still describe the bounded replay surfaces. Contributor-facing README and
# checklist wording lives with the separate P11-L18 owner map.
SHARED_CONTRACT_MARKERS = [
    "bcm2835, gpio, HVC, and header-boundary notes plus their dedicated `check-phase11-*.py` scripts remain parked as continuity surfaces beside the shared packet",
    "`zigux/tests/phase11_bcm2835_wdt.zig`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
]

CLOSURE_NOTE_MARKERS = [
    "bcm2835, gpio, DesignWare, HVC, and header-boundary continuity still live in their dedicated docs-root notes and `scripts/zigux/check-phase11-*.py` packet checkers",
    "`zigux/tests/phase11_bcm2835_wdt.zig`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
]

LANE_NOTE_MARKERS = [
    "* bcm2835 lane `P11-L08` owns bcm2835 reminder-note and checker follow-through; keep the landed direct bcm2835 replay files explicit in shared summaries without widening them into broader poweroff or PM closure claims",
    "* contributor-note lane `P11-L18` owns the shared contributor-facing wording across `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`",
]

SELF_TEST_CASE_COUNT = 7


class CheckError(RuntimeError):
    pass


def read_text(root: Path, relative_path: str) -> str:
    path = root / relative_path
    if not path.is_file():
        raise CheckError(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def expect_markers(relative_path: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            raise CheckError(f"missing marker in {relative_path}: {marker}")


def run_check(root: Path) -> None:
    expect_markers(
        REQUIRED_FILES["survey_note"],
        read_text(root, REQUIRED_FILES["survey_note"]),
        SURVEY_NOTE_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["validation_matrix"],
        read_text(root, REQUIRED_FILES["validation_matrix"]),
        VALIDATION_MATRIX_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["shared_contract"],
        read_text(root, REQUIRED_FILES["shared_contract"]),
        SHARED_CONTRACT_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["closure_note"],
        read_text(root, REQUIRED_FILES["closure_note"]),
        CLOSURE_NOTE_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["lane_note"],
        read_text(root, REQUIRED_FILES["lane_note"]),
        LANE_NOTE_MARKERS,
    )
    # Existence checks for the dedicated bcm2835 packet artifacts the shared notes claim.
    read_text(root, REQUIRED_FILES["manifest"])
    read_text(root, REQUIRED_FILES["test_replay"])
    read_text(root, REQUIRED_FILES["survey_replay"])
    read_text(root, REQUIRED_FILES["verify_replay"])


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    write(root / REQUIRED_FILES["manifest"], '{\n  "lane_key": "P11-L08"\n}\n')
    write(root / REQUIRED_FILES["survey_note"], "\n".join(SURVEY_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["validation_matrix"], "\n".join(VALIDATION_MATRIX_MARKERS) + "\n")
    write(root / REQUIRED_FILES["shared_contract"], "\n".join(SHARED_CONTRACT_MARKERS) + "\n")
    write(root / REQUIRED_FILES["closure_note"], "\n".join(CLOSURE_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["lane_note"], "\n".join(LANE_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["test_replay"], "phase11-bcm2835-wdt-tests\n")
    write(root / REQUIRED_FILES["survey_replay"], "phase11-bcm2835-wdt-survey-tests\n")
    write(root / REQUIRED_FILES["verify_replay"], "phase11-bcm2835-wdt-verify-tests\n")


def expect_failure(root: Path, expected_fragment: str) -> None:
    try:
        run_check(root)
    except CheckError as exc:
        if expected_fragment not in str(exc):
            raise AssertionError(
                f"expected self-test failure containing {expected_fragment!r}, got {exc!r}"
            ) from exc
        return
    raise AssertionError(f"expected failure containing {expected_fragment!r}")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase11_bcm2835_wdt_packet_"))
    try:
        build_self_test_fixture(tmpdir)
        run_check(tmpdir)

        survey_path = tmpdir / REQUIRED_FILES["survey_note"]
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "phase11-bcm2835-wdt-verify-tests\n", "", 1
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "phase11-bcm2835-wdt-verify-tests")

        build_self_test_fixture(tmpdir)
        validation_matrix_path = tmpdir / REQUIRED_FILES["validation_matrix"]
        validation_matrix_path.write_text(
            validation_matrix_path.read_text(encoding="utf-8").replace(
                "current scheduled watchdog-family continuity for this archived bcm2835 packet is tracked through `P11-L08`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            tmpdir,
            "current scheduled watchdog-family continuity for this archived bcm2835 packet is tracked through `P11-L08`",
        )

        build_self_test_fixture(tmpdir)
        shared_contract_path = tmpdir / REQUIRED_FILES["shared_contract"]
        shared_contract_path.write_text(
            shared_contract_path.read_text(encoding="utf-8").replace(
                "`drivers/watchdog/bcm2835_wdt_verify.zig`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "`drivers/watchdog/bcm2835_wdt_verify.zig`")

        build_self_test_fixture(tmpdir)
        closure_note_path = tmpdir / REQUIRED_FILES["closure_note"]
        closure_note_path.write_text(
            closure_note_path.read_text(encoding="utf-8").replace(
                "`zigux/tests/phase11_bcm2835_wdt.zig`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "`zigux/tests/phase11_bcm2835_wdt.zig`")

        build_self_test_fixture(tmpdir)
        lane_note_path = tmpdir / REQUIRED_FILES["lane_note"]
        lane_note_path.write_text(
            lane_note_path.read_text(encoding="utf-8").replace(
                "* bcm2835 lane `P11-L08` owns bcm2835 reminder-note and checker follow-through; keep the landed direct bcm2835 replay files explicit in shared summaries without widening them into broader poweroff or PM closure claims\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "* bcm2835 lane `P11-L08` owns bcm2835 reminder-note and checker follow-through")

        build_self_test_fixture(tmpdir)
        shutil.rmtree((tmpdir / "drivers"), ignore_errors=True)
        expect_failure(tmpdir, REQUIRED_FILES["verify_replay"])

        build_self_test_fixture(tmpdir)
        (tmpdir / REQUIRED_FILES["manifest"]).unlink()
        expect_failure(tmpdir, REQUIRED_FILES["manifest"])

        print("PHASE11_BCM2835_WDT_PACKET_SELF_TEST=pass")
        print(f"PHASE11_BCM2835_WDT_PACKET_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
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
        print(f"PHASE11_BCM2835_WDT_PACKET=fail: {exc}")
        return 1

    print("PHASE11_BCM2835_WDT_PACKET=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
