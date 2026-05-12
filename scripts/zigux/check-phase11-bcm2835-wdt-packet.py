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
    "scripts_readme": "scripts/zigux/README.md",
    "docs_readme": "Documentation/zigux/README.md",
    "tests_readme": "zigux/tests/README.md",
    "review_checklist": "Documentation/zigux/review-checklist.md",
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

SHARED_CONTRACT_MARKERS = [
    "The shipped bcm2835 watchdog sub-packet inside that shared route stays explicit as `phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests`.",
    "* bcm2835 watchdog: `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, and `drivers/watchdog/bcm2835_wdt_verify.zig`",
]

CLOSURE_NOTE_MARKERS = [
    "* bcm2835 watchdog: `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, and `zigux/tests/phase11_bcm2835_wdt_survey.zig`,",
    "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
]

LANE_NOTE_MARKERS = [
    "- bcm2835 lane `P11-L08` owns `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-bcm2835-wdt-survey.md`, `zigux/tests/phase11_bcm2835_wdt.zig`, `zigux/tests/phase11_bcm2835_wdt_manifest.json`, `zigux/tests/phase11_bcm2835_wdt_survey.zig`, and `drivers/watchdog/bcm2835_wdt_verify.zig`",
    "- bcm2835 packet review stays with `P11-L08` through `scripts/zigux/check-phase11-bcm2835-wdt-packet.py` together with the bcm2835 validation matrix, survey, manifest-backed replay, and verify helper",
]

SCRIPTS_README_MARKERS = [
    "- `check-phase11-bcm2835-wdt-packet.py`",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
]

DOCS_README_MARKERS = [
    "Phase 11 notes",
    "`Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`",
    "`Documentation/zigux/phase11-bcm2835-wdt-survey.md`",
    "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
]

TESTS_README_MARKERS = [
    "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
    "the dedicated bcm2835 archival checker route",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`zigux/tests/phase11_bcm2835_wdt.zig`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest.json`",
]

REVIEW_CHECKLIST_MARKERS = [
    "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`",
    "`drivers/watchdog/bcm2835_wdt_verify.zig`",
    "`zigux/tests/phase11_bcm2835_wdt.zig`",
    "`zigux/tests/phase11_bcm2835_wdt_manifest.json`",
]

SELF_TEST_CASE_COUNT = 9


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
    expect_markers(
        REQUIRED_FILES["scripts_readme"],
        read_text(root, REQUIRED_FILES["scripts_readme"]),
        SCRIPTS_README_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["docs_readme"],
        read_text(root, REQUIRED_FILES["docs_readme"]),
        DOCS_README_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["tests_readme"],
        read_text(root, REQUIRED_FILES["tests_readme"]),
        TESTS_README_MARKERS,
    )
    expect_markers(
        REQUIRED_FILES["review_checklist"],
        read_text(root, REQUIRED_FILES["review_checklist"]),
        REVIEW_CHECKLIST_MARKERS,
    )
    # Existence checks for the dedicated bcm2835 packet artifacts the shared surfaces claim.
    read_text(root, REQUIRED_FILES["manifest"])
    read_text(root, REQUIRED_FILES["test_replay"])
    read_text(root, REQUIRED_FILES["survey_replay"])
    read_text(root, REQUIRED_FILES["verify_replay"])


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_self_test_fixture(root: Path) -> None:
    write(root / SCRIPT_PATH, Path(__file__).read_text(encoding="utf-8"))
    write(root / REQUIRED_FILES["manifest"], "{\n  \"lane_key\": \"P11-L08\"\n}\n")
    write(root / REQUIRED_FILES["survey_note"], "\n".join(SURVEY_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["validation_matrix"], "\n".join(VALIDATION_MATRIX_MARKERS) + "\n")
    write(root / REQUIRED_FILES["shared_contract"], "\n".join(SHARED_CONTRACT_MARKERS) + "\n")
    write(root / REQUIRED_FILES["closure_note"], "\n".join(CLOSURE_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["lane_note"], "\n".join(LANE_NOTE_MARKERS) + "\n")
    write(root / REQUIRED_FILES["scripts_readme"], "\n".join(SCRIPTS_README_MARKERS) + "\n")
    write(root / REQUIRED_FILES["docs_readme"], "\n".join(DOCS_README_MARKERS) + "\n")
    write(root / REQUIRED_FILES["tests_readme"], "\n".join(TESTS_README_MARKERS) + "\n")
    write(root / REQUIRED_FILES["review_checklist"], "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n")
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
                "phase11-bcm2835-wdt-verify-tests\n", "",
                1,
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
                "The shipped bcm2835 watchdog sub-packet inside that shared route stays explicit as `phase11-bcm2835-wdt-tests`, `phase11-bcm2835-wdt-verify-tests`, and `phase11-bcm2835-wdt-survey-tests`.\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "The shipped bcm2835 watchdog sub-packet inside that shared route stays explicit")

        build_self_test_fixture(tmpdir)
        lane_note_path = tmpdir / REQUIRED_FILES["lane_note"]
        lane_note_path.write_text(
            lane_note_path.read_text(encoding="utf-8").replace(
                "- bcm2835 packet review stays with `P11-L08` through `scripts/zigux/check-phase11-bcm2835-wdt-packet.py` together with the bcm2835 validation matrix, survey, manifest-backed replay, and verify helper\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "- bcm2835 packet review stays with `P11-L08` through `scripts/zigux/check-phase11-bcm2835-wdt-packet.py`")

        build_self_test_fixture(tmpdir)
        tests_readme_path = tmpdir / REQUIRED_FILES["tests_readme"]
        tests_readme_path.write_text(
            tests_readme_path.read_text(encoding="utf-8").replace(
                "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "`scripts/zigux/check-phase11-bcm2835-wdt-packet.py`")

        build_self_test_fixture(tmpdir)
        review_checklist_path = tmpdir / REQUIRED_FILES["review_checklist"]
        review_checklist_path.write_text(
            review_checklist_path.read_text(encoding="utf-8").replace(
                "`drivers/watchdog/bcm2835_wdt_verify.zig`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "`drivers/watchdog/bcm2835_wdt_verify.zig`")

        build_self_test_fixture(tmpdir)
        docs_readme_path = tmpdir / REQUIRED_FILES["docs_readme"]
        docs_readme_path.write_text(
            docs_readme_path.read_text(encoding="utf-8").replace(
                "`Documentation/zigux/phase11-bcm2835-wdt-survey.md`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(tmpdir, "`Documentation/zigux/phase11-bcm2835-wdt-survey.md`")

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