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

TARGETS = [
    (
        "gate_evidence",
        "PHASE4_REVERSIBLE_DELIVERY_GATE_EVIDENCE_BLOB_SHA",
        Path("Documentation/zigux/phase4-gate-evidence.md"),
    ),
    (
        "matrix",
        "PHASE4_REVERSIBLE_DELIVERY_MATRIX_BLOB_SHA",
        Path("Documentation/zigux/phase4-validation-matrix.md"),
    ),
    (
        "remaining_gap_checker",
        "PHASE4_REVERSIBLE_DELIVERY_REMAINING_GAP_CHECKER_BLOB_SHA",
        Path("scripts/zigux/check-phase4-remaining-gap-matrix.py"),
    ),
    (
        "workflow_route_checker",
        "PHASE4_REVERSIBLE_DELIVERY_WORKFLOW_ROUTE_CHECKER_BLOB_SHA",
        Path("scripts/zigux/check-phase4-workflow-route-counts.py"),
    ),
    (
        "validator",
        "PHASE4_REVERSIBLE_DELIVERY_VALIDATOR_BLOB_SHA",
        Path("scripts/zigux/validate-phase4.py"),
    ),
    (
        "build",
        "PHASE4_REVERSIBLE_DELIVERY_BUILD_BLOB_SHA",
        Path("zigux/tests/phase4_build.zig"),
    ),
    (
        "makefile",
        "PHASE4_REVERSIBLE_DELIVERY_MAKEFILE_BLOB_SHA",
        Path("zigux/Makefile"),
    ),
    (
        "workflow",
        "PHASE4_REVERSIBLE_DELIVERY_WORKFLOW_BLOB_SHA",
        Path(".github/workflows/zigux-bootstrap.yml"),
    ),
    (
        "review_checklist",
        "PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA",
        Path("Documentation/zigux/review-checklist.md"),
    ),
    (
        "sequencing_note",
        "PHASE4_REVERSIBLE_DELIVERY_SEQUENCING_NOTE_BLOB_SHA",
        Path("Documentation/zigux/phase4-validation-lane-sequencing.md"),
    ),
    (
        "local_perf_checker",
        "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_CHECKER_BLOB_SHA",
        Path("scripts/zigux/check-phase4-perf-baseline-packet.py"),
    ),
    (
        "local_perf_manifest",
        "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_MANIFEST_BLOB_SHA",
        Path("zigux/tests/phase4_perf_baseline_manifest.json"),
    ),
    (
        "local_perf_survey",
        "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_SURVEY_BLOB_SHA",
        Path("zigux/tests/phase4_perf_baseline_survey.zig"),
    ),
]

REQUIRED_STATUS_MARKERS = [
    "PHASE4_REVERSIBLE_DELIVERY_STATUS=shared_evidence_packet_landed",
    "PHASE4_REVERSIBLE_DELIVERY_LANE_KEY=P4-L23",
    "PHASE4_REVERSIBLE_DELIVERY_PHASE=Phase 4",
    "PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_DATE=",
    "PHASE4_REVERSIBLE_DELIVERY_MODE=github_connector_readback",
    "PHASE4_REVERSIBLE_DELIVERY_EXACT_READBACK_REF=master",
    "PHASE4_REVERSIBLE_DELIVERY_GATE_EVIDENCE_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_MATRIX_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_REMAINING_GAP_CHECKER_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_WORKFLOW_ROUTE_CHECKER_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_VALIDATOR_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_BUILD_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_MAKEFILE_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_WORKFLOW_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_REVIEW_CHECKLIST_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_SEQUENCING_NOTE_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_CHECKER_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_MANIFEST_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_LOCAL_PERF_SURVEY_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true",
    "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT=",
]

REQUIRED_PROSE_MARKERS = [
    "`Documentation/zigux/phase4-gate-evidence.md`",
    "`Documentation/zigux/phase4-validation-matrix.md`",
    "`scripts/zigux/check-phase4-remaining-gap-matrix.py`",
    "`scripts/zigux/check-phase4-workflow-route-counts.py`",
    "`scripts/zigux/check-phase4-reversible-delivery-pins.py`",
    "`scripts/zigux/validate-phase4.py`",
    "`zigux/tests/phase4_build.zig`",
    "`zigux/Makefile`",
    "`.github/workflows/zigux-bootstrap.yml`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase4-validation-lane-sequencing.md`",
    "`scripts/zigux/check-phase4-perf-baseline-packet.py`",
    "`zigux/tests/phase4_perf_baseline_manifest.json`",
    "`zigux/tests/phase4_perf_baseline_survey.zig`",
    "repair the shared exact-readback packet first.",
    "repair the dedicated local-only perf packet first.",
]

SELF_TEST_CASES = (
    ["baseline_round_trip", "missing_note_file"]
    + [f"missing_{slug}_file" for slug, _, _ in TARGETS]
    + [f"{slug}_blob_pin_drift" for slug, _, _ in TARGETS]
    + ["missing_checker_presence_marker"]
)


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
    failures: list[str] = []
    if not note_path.exists():
        return [f"missing_file:{NOTE_REL.as_posix()}"]

    note_text = read_text(note_path)
    for _, _, rel_path in TARGETS:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path.as_posix()}")
    if failures:
        return failures

    for marker in REQUIRED_STATUS_MARKERS:
        if marker not in note_text:
            failures.append(f"status_marker:{marker}")

    for marker in REQUIRED_PROSE_MARKERS:
        if marker not in note_text:
            failures.append(f"prose_marker:{marker}")

    for slug, key, rel_path in TARGETS:
        expected_line = f"{key}=" + git_blob_sha1((root / rel_path).read_bytes())
        if expected_line not in note_text:
            failures.append(f"{slug}_blob_pin:{expected_line}")

    exact_case_count_line = (
        "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT="
        + str(len(SELF_TEST_CASES))
    )
    if exact_case_count_line not in note_text:
        failures.append(f"self_test_case_count:{exact_case_count_line}")

    return failures


def build_fixture_tree(root: Path) -> None:
    fixture_contents = {
        Path("Documentation/zigux/phase4-gate-evidence.md"): "\n".join(
            [
                "# Phase 4 Gate Evidence",
                "",
                "- exact readback packet",
                "",
            ]
        ),
        Path("Documentation/zigux/phase4-validation-matrix.md"): "\n".join(
            [
                "# Phase 4 Validation Matrix",
                "",
                "- rollback owner matrix",
                "",
            ]
        ),
        Path("scripts/zigux/check-phase4-remaining-gap-matrix.py"): "\n".join(
            [
                "#!/usr/bin/env python3",
                'print("phase4 remaining gap")',
                "",
            ]
        ),
        Path("scripts/zigux/check-phase4-workflow-route-counts.py"): "\n".join(
            [
                "#!/usr/bin/env python3",
                'print("phase4 route counts")',
                "",
            ]
        ),
        Path("scripts/zigux/validate-phase4.py"): "\n".join(
            [
                "#!/usr/bin/env python3",
                'print("phase4 validator")',
                "",
            ]
        ),
        Path("zigux/tests/phase4_build.zig"): "\n".join(
            [
                'const std = @import("std");',
                "",
                "pub fn build(_: *std.Build) void {}",
                "",
            ]
        ),
        Path("zigux/Makefile"): "\n".join(
            [
                "phase4-validate:",
                "\t@true",
                "",
            ]
        ),
        Path(".github/workflows/zigux-bootstrap.yml"): "\n".join(
            [
                "name: zigux-bootstrap",
                "on: [push]",
                "jobs:",
                "  phase4:",
                "    runs-on: ubuntu-latest",
                "",
            ]
        ),
        Path("Documentation/zigux/review-checklist.md"): "\n".join(
            [
                "# Zigux Review Checklist",
                "",
                "- `zigux/Makefile`",
                "- `Documentation/zigux/review-checklist.md`",
                "",
            ]
        ),
        Path("Documentation/zigux/phase4-validation-lane-sequencing.md"): "\n".join(
            [
                "# Phase 4 Validation Lane Sequencing",
                "",
                "- keep the shared exact-readback packet narrow",
                "- keep the dedicated local-only perf packet separate",
                "",
            ]
        ),
        Path("scripts/zigux/check-phase4-perf-baseline-packet.py"): "\n".join(
            [
                "#!/usr/bin/env python3",
                'print("phase4 perf packet")',
                "",
            ]
        ),
        Path("zigux/tests/phase4_perf_baseline_manifest.json"): "\n".join(
            [
                "{",
                '  "lane_key": "P4-L20"',
                "}",
                "",
            ]
        ),
        Path("zigux/tests/phase4_perf_baseline_survey.zig"): "\n".join(
            [
                'const std = @import("std");',
                "",
                'test "phase4 perf baseline survey fixture" {',
                "    _ = std.testing.allocator;",
                "}",
                "",
            ]
        ),
    }

    for rel_path, content in fixture_contents.items():
        write_text(root / rel_path, content)

    status_lines = [
        "- `PHASE4_REVERSIBLE_DELIVERY_STATUS=shared_evidence_packet_landed`",
        "- `PHASE4_REVERSIBLE_DELIVERY_LANE_KEY=P4-L23`",
        "- `PHASE4_REVERSIBLE_DELIVERY_PHASE=Phase 4`",
        "- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_DATE=2026-05-15`",
        "- `PHASE4_REVERSIBLE_DELIVERY_MODE=github_connector_readback`",
        "- `PHASE4_REVERSIBLE_DELIVERY_EXACT_READBACK_REF=master`",
    ]
    for _, key, rel_path in TARGETS:
        status_lines.append(f"- `{key}={git_blob_sha1((root / rel_path).read_bytes())}`")
    status_lines.extend(
        [
            "- `PHASE4_REVERSIBLE_DELIVERY_PIN_CHECKER_PRESENT=true`",
            f"- `PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}`",
        ]
    )

    note_lines = [
        "# Phase 4 Reversible Delivery Evidence",
        "",
        "## Status",
        *status_lines,
        "",
        "## Current Packet",
        "- shared exact-readback and owner-map evidence:",
        "  - `Documentation/zigux/phase4-gate-evidence.md`",
        "  - `Documentation/zigux/phase4-validation-matrix.md`",
        "  - `scripts/zigux/check-phase4-remaining-gap-matrix.py`",
        "  - `scripts/zigux/check-phase4-workflow-route-counts.py`",
        "  - `scripts/zigux/check-phase4-reversible-delivery-pins.py`",
        "  - `scripts/zigux/validate-phase4.py`",
        "  - `zigux/tests/phase4_build.zig`",
        "  - `zigux/Makefile`",
        "  - `.github/workflows/zigux-bootstrap.yml`",
        "  - `Documentation/zigux/review-checklist.md`",
        "- anti-overlap boundary:",
        "  - `Documentation/zigux/phase4-validation-lane-sequencing.md`",
        "- dedicated local-only perf packet:",
        "  - `scripts/zigux/check-phase4-perf-baseline-packet.py`",
        "  - `zigux/tests/phase4_perf_baseline_manifest.json`",
        "  - `zigux/tests/phase4_perf_baseline_survey.zig`",
        "",
        "## Review Rules",
        "- If the rollback-owner map drifts, repair the shared exact-readback packet first.",
        "- If the local benchmark commands drift, repair the dedicated local-only perf packet first.",
        "",
    ]
    write_text(root / NOTE_REL, "\n".join(note_lines))


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

        note_path = root / NOTE_REL
        for slug, key, rel_path in TARGETS:
            (root / rel_path).unlink()
            if not expect_failure(root, f"missing_file:{rel_path.as_posix()}"):
                print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
                print(f"missing {slug} file case did not fail closed")
                return 1
            case_count += 1
            build_fixture_tree(root)

        for slug, key, rel_path in TARGETS:
            target_text = (root / rel_path).read_bytes()
            drifted_sha = git_blob_sha1(target_text + b"# drift\n")
            note_path.write_text(
                replace_once(
                    read_text(note_path),
                    f"{key}=" + git_blob_sha1(target_text),
                    f"{key}={drifted_sha}",
                ),
                encoding="utf-8",
            )
            if not expect_failure(root, f"{slug}_blob_pin:{key}="):
                print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
                print(f"{slug} blob pin drift case did not fail closed")
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
    print(f"PHASE4_REVERSIBLE_DELIVERY_PIN_FILE_COUNT={len(TARGETS) + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
