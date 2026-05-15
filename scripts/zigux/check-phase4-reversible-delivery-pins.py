#!/usr/bin/env python3
"""Validate the Phase 4 reversible-delivery handoff note."""

from __future__ import annotations

import argparse
import hashlib
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parent
NOTE_REL = Path("Documentation/zigux/phase4-reversible-delivery-evidence.md")
MAKEFILE_REL = Path("zigux/Makefile")
CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")
SEQUENCING_REL = Path("Documentation/zigux/phase4-validation-lane-sequencing.md")
PERF_CHECKER_REL = Path("scripts/zigux/check-phase4-perf-baseline-packet.py")
PERF_MANIFEST_REL = Path("zigux/tests/phase4_perf_baseline_manifest.json")
PERF_SURVEY_REL = Path("zigux/tests/phase4_perf_baseline_survey.zig")

REQUIRED_STATUS_MARKERS = [
    "PHASE4_REVERSIBLE_DELIVERY_STATUS=shared_evidence_packet_landed",
    "PHASE4_REVERSIBLE_DELIVERY_LANE_KEY=P4-L23",
    "PHASE4_REVERSIBLE_DELIVERY_PHASE=Phase 4",
    "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_DATE=",
    "PHASE4_REVERSIBLE_DELIVERY_MODE=github_connector_readback",
    "PHASE4_REVERSIBLE_DELIVERY_EXACT_READBACK_REF=master",
    "PHASE4_REVERSIBLE_DELIVERY_MAKEFILE_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_SEQUENCING_NOTE_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_CHECKER_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_MANIFEST_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_SURVEY_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true",
    "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=",
]

REQUIRED_PROSE_MARKERS = [
    "`scripts/zigux/check-phase4-reversible-delivery-pins.py`",
    "`zigux/Makefile`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase4-validation-lane-sequencing.md`",
    "`scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`",
    "`zigux/tests/phase4_perf_baseline_survey.zig`",
    "repair the shared exact-readback packet first.",
    "repair the dedicated local-only perf packet first.",
]

SELF_TEST_CASES = [
    "baseline_round_trip",
    "missing_note_file",
    "missing_makefile_file",
    "missing_review_checklist_file",
    "missing_sequencing_note_file",
    "missing_local_perf_checker_file",
    "missing_local_perf_manifest_file",
    "missing_local_perf_survey_file",
    "makefile_blob_pin_drift",
    "review_checklist_blob_pin_drift",
    "sequencing_note_blob_pin_drift",
    "local_perf_checker_blob_pin_drift",
    "local_perf_manifest_blob_pin_drift",
    "local_perf_survey_blob_pin_drift",
    "missing_checker_presence_marker",
]


def git_blob_sha1(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("utf-8")
    return hashlib.sha1(header + payload).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"missing marker: {old}")
    return text.replace(old, new, 1)


def validate_root(root: Path) -> list[str]:
    note_path = root / NOTE_REL
    makefile_path = root / MAKEFILE_REL
    checklist_path = root / CHECKLIST_REL
    sequencing_path = root / SEQUENCING_REL
    perf_checker_path = root / PERF_CHECKER_REL
    perf_manifest_path = root / PERF_MANIFEST_REL
    perf_survey_path = root / PERF_SURVEY_REL

    failures: list[str] = []
    for path in (
        note_path,
        makefile_path,
        checklist_path,
        sequencing_path,
        perf_checker_path,
        perf_manifest_path,
        perf_survey_path,
    ):
        if not path.exists():
            failures.append(f"missing_file:{path.relative_to(root).as_posix()}")
    if failures:
        return failures

    note_text = read_text(note_path)
    for marker in REQUIRED_STATUS_MARKERS:
        if marker not in note_text:
            failures.append(f"status_marker:{marker}")

    for marker in REQUIRED_PROSE_MARKERS:
        if marker not in note_text:
            failures.append(f"prose_marker:{marker}")

    expected_makefile_line = (
        "PHASE4_REVERSIBLE_DELIVERY_MAKEFILE_BLOB_SHA="
        + git_blob_sha1(makefile_path.read_bytes())
    )
    if expected_makefile_line not in note_text:
        failures.append(f"makefile_blob_pin:{expected_makefile_line}")

    expected_checklist_line = (
        "PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA="
        + git_blob_sha1(checklist_path.read_bytes())
    )
    if expected_checklist_line not in note_text:
        failures.append(f"review_checklist_blob_pin:{expected_checklist_line}")

    expected_sequencing_line = (
        "PHASE4_REVERSIBLE_DELIVERY_SEQUENCING_NOTE_BLOB_SHA="
        + git_blob_sha1(sequencing_path.read_bytes())
    )
    if expected_sequencing_line not in note_text:
        failures.append(f"sequencing_note_blob_pin:{expected_sequencing_line}")

    expected_perf_checker_line = (
        "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_CHECKER_BLOB_SHA="
        + git_blob_sha1(perf_checker_path.read_bytes())
    )
    if expected_perf_checker_line not in note_text:
        failures.append(f"local_perf_checker_blob_pin:{expected_perf_checker_line}")

    expected_perf_manifest_line = (
        "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_MANIFEST_BLOB_SHA="
        + git_blob_sha1(perf_manifest_path.read_bytes())
    )
    if expected_perf_manifest_line not in note_text:
        failures.append(f"local_perf_manifest_blob_pin:{expected_perf_manifest_line}")

    expected_perf_survey_line = (
        "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_SURVEY_BLOB_SHA="
        + git_blob_sha1(perf_survey_path.read_bytes())
    )
    if expected_perf_survey_line not in note_text:
        failures.append(f"local_perf_survey_blob_pin:{expected_perf_survey_line}")

    exact_case_count_line = (
        "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT="
        + str(len(SELF_TEST_CASES))
    )
    if exact_case_count_line not in note_text:
        failures.append(f"self_test_case_count:{exact_case_count_line}")

    return failures


def build_fixture_tree(root: Path) -> None:
    write_text(
        root / MAKEFILE_REL,
        "\n".join(
            [
                "phase4-validate:",
                "\t@true",
                "",
            ]
        ),
    )
    write_text(
        root / CHECKLIST_REL,
        "\n".join(
            [
                "# Zigux Review Checklist",
                "",
                "- `zigux/Makefile`",
                "- `Documentation/zigux/review-checklist.md`",
                "",
            ]
        ),
    )
    write_text(
        root / SEQUENCING_REL,
        "\n".join(
            [
                "# Phase 4 Validation Lane Sequencing",
                "",
                "- keep the shared exact-readback packet narrow",
                "- keep the dedicated local-only perf packet separate",
                "",
            ]
        ),
    )
    write_text(
        root / PERF_CHECKER_REL,
        "\n".join(
            [
                "#!/usr/bin/env python3",
                'print("phase4 perf packet")',
                "",
            ]
        ),
    )
    write_text(
        root / PERF_MANIFEST_REL,
        "\n".join(
            [
                "{",
                '  "lane_key": "P4-L20"',
                "}",
                "",
            ]
        ),
    )
    write_text(
        root / PERF_SURVEY_REL,
        "\n".join(
            [
                'const std = @import("std");',
                "",
                'test "phase4 perf baseline survey fixture" {',
                "    _ = std.testing.allocator;",
                "}",
                "",
            ]
        ),
    )

    makefile_sha = git_blob_sha1((root / MAKEFILE_REL).read_bytes())
    checklist_sha = git_blob_sha1((root / CHECKLIST_REL).read_bytes())
    sequencing_sha = git_blob_sha1((root / SEQUENCING_REL).read_bytes())
    perf_checker_sha = git_blob_sha1((root / PERF_CHECKER_REL).read_bytes())
    perf_manifest_sha = git_blob_sha1((root / PERF_MANIFEST_REL).read_bytes())
    perf_survey_sha = git_blob_sha1((root / PERF_SURVEY_REL).read_bytes())
    write_text(
        root / NOTE_REL,
        "\n".join(
            [
                "# Phase 4 Reversible Delivery Evidence",
                "",
                "## Status",
                "- `PHASE4_REVERSIBLE_DELIVERY_STATUS=shared_evidence_packet_landed`",
                "- `PHASE4_REVERSIBLE_DELIVERY_LANE_KEY=P4-L23`",
                "- `PHASE4_REVERSIBLE_DELIVERY_PHASE=Phase 4`",
                "- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_DATE=2026-05-15`",
                "- `PHASE4_REVERSIBLE_DELIVERY_MODE=github_connector_readback`",
                "- `PHASE4_REVERSIBLE_DELIVERY_EXACT_READBACK_REF=master`",
                f"- `PHASE4_REVERSIBLE_DELIVERY_MAKEFILE_BLOB_SHA={makefile_sha}`",
                f"- `PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA={checklist_sha}`",
                f"- `PHASE4_REVERSIBLE_DELIVERY_SEQUENCING_NOTE_BLOB_SHA={sequencing_sha}`",
                f"- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_CHECKER_BLOB_SHA={perf_checker_sha}`",
                f"- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_MANIFEST_BLOB_SHA={perf_manifest_sha}`",
                f"- `PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_SURVEY_BLOB_SHA={perf_survey_sha}`",
                "- `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
                f"- `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}`",
                "",
                "## Current Packet",
                "- `scripts/zigux/check-phase4-reversible-delivery-pins.py` keeps the `zigux/Makefile`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase4-validation-lane-sequencing.md`, `scripts/zigux/check-phase4-perf-baseline-packet.py`, `zigux/tests/phase4_perf_baseline_manifest.json`, and `zigux/tests/phase4_perf_baseline_survey.zig` blob pins exact inside this handoff note.",
                "",
                "## Review Rules",
                "- If the rollback-owner map drifts, repair the shared exact-readback packet first.",
                "- If the local benchmark commands drift, repair the dedicated local-only perf packet first.",
                "",
            ]
        ),
    )


def expect_failure(root: Path, expected_prefix: str) -> bool:
    return any(item.startswith(expected_prefix) for item in validate_root(root))


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase4_reversible_delivery_") as tmp_dir:
        root = Path(tmp_dir)
        build_fixture_tree(root)

        if validate_root(root):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("baseline fixture did not validate")
            return 1
        case_count += 1

        (root / NOTE_REL).unlink()
        if not expect_failure(root, f"missing_file:{NOTE_REL.as_posix()}"):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("missing note file case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        (root / MAKEFILE_REL).unlink()
        if not expect_failure(root, f"missing_file:{MAKEFILE_REL.as_posix()}"):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("missing makefile case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        (root / CHECKLIST_REL).unlink()
        if not expect_failure(root, f"missing_file:{CHECKLIST_REL.as_posix()}"):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("missing review checklist case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        (root / SEQUENCING_REL).unlink()
        if not expect_failure(root, f"missing_file:{SEQUENCING_REL.as_posix()}"):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("missing sequencing note case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        (root / PERF_CHECKER_REL).unlink()
        if not expect_failure(root, f"missing_file:{PERF_CHECKER_REL.as_posix()}"):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("missing local perf checker case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        (root / PERF_MANIFEST_REL).unlink()
        if not expect_failure(root, f"missing_file:{PERF_MANIFEST_REL.as_posix()}"):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("missing local perf manifest case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        (root / PERF_SURVEY_REL).unlink()
        if not expect_failure(root, f"missing_file:{PERF_SURVEY_REL.as_posix()}"):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("missing local perf survey case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        note_path = root / NOTE_REL
        note_text = read_text(note_path)
        makefile_text = read_text(root / MAKEFILE_REL)
        drifted_makefile_sha = git_blob_sha1((makefile_text + "# drift\n").encode("utf-8"))
        note_path.write_text(
            replace_once(
                note_text,
                "PHASE4_REVERSIBLE_DELIVERY_MAKEFILE_BLOB_SHA="
                + git_blob_sha1(makefile_text.encode("utf-8")),
                f"PHASE4_REVERSIBLE_DELIVERY_MAKEFILE_BLOB_SHA={drifted_makefile_sha}",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            "makefile_blob_pin:PHASE4_REVERSIBLE_DELIVERY_MAKEFILE_BLOB_SHA=",
        ):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("makefile blob pin drift case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        note_text = read_text(note_path)
        checklist_text = read_text(root / CHECKLIST_REL)
        drifted_checklist_sha = git_blob_sha1((checklist_text + "# drift\n").encode("utf-8"))
        note_path.write_text(
            replace_once(
                note_text,
                "PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA="
                + git_blob_sha1(checklist_text.encode("utf-8")),
                f"PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA={drifted_checklist_sha}",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            "review_checklist_blob_pin:PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=",
        ):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("review checklist blob pin drift case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        note_text = read_text(note_path)
        sequencing_text = read_text(root / SEQUENCING_REL)
        drifted_sequencing_sha = git_blob_sha1((sequencing_text + "# drift\n").encode("utf-8"))
        note_path.write_text(
            replace_once(
                note_text,
                "PHASE4_REVERSIBLE_DELIVERY_SEQUENCING_NOTE_BLOB_SHA="
                + git_blob_sha1(sequencing_text.encode("utf-8")),
                f"PHASE4_REVERSIBLE_DELIVERY_SEQUENCING_NOTE_BLOB_SHA={drifted_sequencing_sha}",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            "sequencing_note_blob_pin:PHASE4_REVERSIBLE_DELIVERY_SEQUENCING_NOTE_BLOB_SHA=",
        ):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("sequencing note blob pin drift case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        note_text = read_text(note_path)
        perf_checker_text = read_text(root / PERF_CHECKER_REL)
        drifted_perf_checker_sha = git_blob_sha1(
            (perf_checker_text + "# drift\n").encode("utf-8")
        )
        note_path.write_text(
            replace_once(
                note_text,
                "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_CHECKER_BLOB_SHA="
                + git_blob_sha1(perf_checker_text.encode("utf-8")),
                f"PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_CHECKER_BLOB_SHA={drifted_perf_checker_sha}",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            "local_perf_checker_blob_pin:PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_CHECKER_BLOB_SHA=",
        ):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("local perf checker blob pin drift case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        note_text = read_text(note_path)
        perf_manifest_text = read_text(root / PERF_MANIFEST_REL)
        drifted_perf_manifest_sha = git_blob_sha1(
            (perf_manifest_text + "# drift\n").encode("utf-8")
        )
        note_path.write_text(
            replace_once(
                note_text,
                "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_MANIFEST_BLOB_SHA="
                + git_blob_sha1(perf_manifest_text.encode("utf-8")),
                f"PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_MANIFEST_BLOB_SHA={drifted_perf_manifest_sha}",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            "local_perf_manifest_blob_pin:PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_MANIFEST_BLOB_SHA=",
        ):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("local perf manifest blob pin drift case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        note_text = read_text(note_path)
        perf_survey_text = read_text(root / PERF_SURVEY_REL)
        drifted_perf_survey_sha = git_blob_sha1(
            (perf_survey_text + "// drift\n").encode("utf-8")
        )
        note_path.write_text(
            replace_once(
                note_text,
                "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_SURVEY_BLOB_SHA="
                + git_blob_sha1(perf_survey_text.encode("utf-8")),
                f"PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_SURVEY_BLOB_SHA={drifted_perf_survey_sha}",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            "local_perf_survey_blob_pin:PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_SURVEY_BLOB_SHA=",
        ):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("local perf survey blob pin drift case did not fail closed")
            return 1
        case_count += 1
        build_fixture_tree(root)

        note_path.write_text(
            replace_once(
                read_text(note_path),
                "PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true",
                "PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=false",
            ),
            encoding="utf-8",
        )
        if not expect_failure(
            root,
            "status_marker:PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true",
        ):
            print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
            print("missing checker marker case did not fail closed")
            return 1
        case_count += 1

    if case_count != len(SELF_TEST_CASES):
        print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
        print(f"unexpected self-test case count {case_count} != {len(SELF_TEST_CASES)}")
        return 1

    print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=pass")
    print(f"PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST_CASE_COUNT={case_count}")
    print(
        "PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST_CASES="
        + ",".join(SELF_TEST_CASES)
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the Phase 4 reversible-delivery handoff note."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated coverage checks in a temporary workspace.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate_root(ROOT)
    if failures:
        print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK=fail")
        print("PHASE4_REVERSIBLE_DELIVERY_PIN_FAILURES_START")
        for item in failures:
            print(item)
        print("PHASE4_REVERSIBLE_DELIVERY_PIN_FAILURES_END")
        return 1

    print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK=pass")
    print("PHASE4_REVERSIBLE_DELIVERY_PIN_FILE_COUNT=7")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
