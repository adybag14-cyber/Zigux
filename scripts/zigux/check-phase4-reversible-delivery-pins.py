#!/usr/bin/env python3
"""Validate the Phase 4 reversible-delivery handoff note."""

from __future__ import annotations

import argparse
import hashlib
import tempfile
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
ROOT = SCRIPT_PATH.parents[2] if len(SCRIPT_PATH.parents) > 2 else SCRIPT_PATH.parent
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
    (
        "kprobe_gap_note",
        "PHASE4_REVERSIBLE_DELIVERY_KPROBE_GAP_NOTE_BLOB_SHA",
        Path("Documentation/zigux/phase4-kprobe-example-gap-survey.md"),
    ),
    (
        "kprobe_gap_manifest",
        "PHASE4_REVERSIBLE_DELIVERY_KPROBE_GAP_MANIFEST_BLOB_SHA",
        Path("zigux/tests/phase4_kprobe_example_manifest.json"),
    ),
    (
        "kprobe_gap_survey",
        "PHASE4_REVERSIBLE_DELIVERY_KPROBE_GAP_SURVEY_BLOB_SHA",
        Path("zigux/tests/phase4_kprobe_example_survey.zig"),
    ),
    (
        "test_fsmount_gap_note",
        "PHASE4_REVERSIBLE_DELIVERY_TEST_FSMOUNT_GAP_NOTE_BLOB_SHA",
        Path("Documentation/zigux/phase4-test-fsmount-gap-survey.md"),
    ),
    (
        "test_fsmount_gap_manifest",
        "PHASE4_REVERSIBLE_DELIVERY_TEST_FSMOUNT_GAP_MANIFEST_BLOB_SHA",
        Path("zigux/tests/phase4_test_fsmount_manifest.json"),
    ),
    (
        "test_fsmount_gap_survey",
        "PHASE4_REVERSIBLE_DELIVERY_TEST_FSMOUNT_GAP_SURVEY_BLOB_SHA",
        Path("zigux/tests/phase4_test_fsmount_survey.zig"),
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
    "PHASE4_REVERSIBLE_DELIVERY_KPROBE_GAP_NOTE_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_KPROBE_GAP_MANIFEST_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_KPROBE_GAP_SURVEY_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_TEST_FSMOUNT_GAP_NOTE_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_TEST_FSMOUNT_GAP_MANIFEST_BLOB_SHA=",
    "PHASE4_REVERSIBLE_DELIVERY_TEST_FSMOUNT_GAP_SURVEY_BLOB_SHA=",
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
    "`Documentation/zigux/phase4-kprobe-example-gap-survey.md`",
    "`zigux/tests/phase4_kprobe_example_manifest.json`",
    "`zigux/tests/phase4_kprobe_example_survey.zig`",
    "`make -C zigux phase4-kprobe-example-survey`",
    "`zig test zigux/tests/phase4_kprobe_example_survey.zig`",
    "`Documentation/zigux/phase4-test-fsmount-gap-survey.md`",
    "`zigux/tests/phase4_test_fsmount_manifest.json`",
    "`zigux/tests/phase4_test_fsmount_survey.zig`",
    "`make -C zigux phase4-test-fsmount-survey`",
    "`zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`",
    "repair the shared exact-readback packet first.",
    "repair the dedicated local-only perf packet first.",
    "repair the parked kprobe packet first",
    "repair the parked test_fsmount packet first",
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

    case_count_line = (
        "PHASE4_REVERSIBLE_DELIVERY_PIN_SELF_TEST_CASE_COUNT="
        + str(len(SELF_TEST_CASES))
    )
    if case_count_line not in note_text:
        failures.append(f"self_test_case_count:{case_count_line}")

    return failures


def build_fixture_tree(root: Path) -> None:
    fixture_contents = {
        Path("Documentation/zigux/phase4-gate-evidence.md"): "# gate evidence\n",
        Path("Documentation/zigux/phase4-validation-matrix.md"): "# validation matrix\n",
        Path("scripts/zigux/check-phase4-remaining-gap-matrix.py"): "#!/usr/bin/env python3\nprint('remaining gap')\n",
        Path("scripts/zigux/check-phase4-workflow-route-counts.py"): "#!/usr/bin/env python3\nprint('route counts')\n",
        Path("scripts/zigux/validate-phase4.py"): "#!/usr/bin/env python3\nprint('validate phase4')\n",
        Path("zigux/tests/phase4_build.zig"): 'pub fn build(_: *std.Build) void {}\n',
        Path("zigux/Makefile"): "phase4-validate:\n\t@true\n",
        Path(".github/workflows/zigux-bootstrap.yml"): "name: zigux-bootstrap\n",
        Path("Documentation/zigux/review-checklist.md"): "# review checklist\n",
        Path("Documentation/zigux/phase4-validation-lane-sequencing.md"): "# sequencing\n",
        Path("scripts/zigux/check-phase4-perf-baseline-packet.py"): "#!/usr/bin/env python3\nprint('perf packet')\n",
        Path("zigux/tests/phase4_perf_baseline_manifest.json"): '{"lane_key":"P4-L20"}\n',
        Path("zigux/tests/phase4_perf_baseline_survey.zig"): 'test "perf" {}\n',
        Path("Documentation/zigux/phase4-kprobe-example-gap-survey.md"): "# kprobe gap\n",
        Path("zigux/tests/phase4_kprobe_example_manifest.json"): '{"lane_key":"P4-L19"}\n',
        Path("zigux/tests/phase4_kprobe_example_survey.zig"): 'test "kprobe" {}\n',
        Path("Documentation/zigux/phase4-test-fsmount-gap-survey.md"): "# test_fsmount gap\n",
        Path("zigux/tests/phase4_test_fsmount_manifest.json"): '{"lane_key":"P4-L19"}\n',
        Path("zigux/tests/phase4_test_fsmount_survey.zig"): 'test "test_fsmount" {}\n',
    }
    for rel_path, content in fixture_contents.items():
        write_text(root / rel_path, content)

    status_lines = [
        "- `PHASE4_REVERSIBLE_DELIVERY_STATUS=shared_evidence_packet_landed`",
        "- `PHASE4_REVERSIBLE_DELIVERY_LANE_KEY=P4-L23`",
        "- `PHASE4_REVERSIBLE_DELIVERY_PHASE=Phase 4`",
        "- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE_DATE=2026-05-16`",
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
        "- dedicated local-only perf packet:",
        "  - `scripts/zigux/check-phase4-perf-baseline-packet.py`",
        "  - `zigux/tests/phase4_perf_baseline_manifest.json`",
        "  - `zigux/tests/phase4_perf_baseline_survey.zig`",
        "- dedicated parked kprobe reversible-delivery packet:",
        "  - `Documentation/zigux/phase4-kprobe-example-gap-survey.md`",
        "  - `zigux/tests/phase4_kprobe_example_manifest.json`",
        "  - `zigux/tests/phase4_kprobe_example_survey.zig`",
        "- dedicated parked test_fsmount reversible-delivery packet:",
        "  - `Documentation/zigux/phase4-test-fsmount-gap-survey.md`",
        "  - `zigux/tests/phase4_test_fsmount_manifest.json`",
        "  - `zigux/tests/phase4_test_fsmount_survey.zig`",
        "- anti-overlap boundary:",
        "  - `Documentation/zigux/phase4-validation-lane-sequencing.md`",
        "",
        "The parked kprobe packet stays measurable through `make -C zigux phase4-kprobe-example-survey` and `zig test zigux/tests/phase4_kprobe_example_survey.zig`.",
        "The parked test_fsmount packet stays measurable through `make -C zigux phase4-test-fsmount-survey` and `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`.",
        "",
        "## Review Rules",
        "- If the rollback-owner map drifts, repair the shared exact-readback packet first.",
        "- If the local benchmark commands drift, repair the dedicated local-only perf packet first.",
        "- If the parked kprobe packet drifts, repair the parked kprobe packet first before refreshing this shared handoff note.",
        "- If the parked test_fsmount packet drifts, repair the parked test_fsmount packet first before refreshing this shared handoff note.",
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
        for slug, _, rel_path in TARGETS:
            (root / rel_path).unlink()
            if not expect_failure(root, f"missing_file:{rel_path.as_posix()}"):
                print("PHASE4_REVERSIBLE_DELIVERY_PIN_CHECK_SELF_TEST=fail")
                print(f"missing {slug} file case did not fail closed")
                return 1
            case_count += 1
            build_fixture_tree(root)

        for slug, key, rel_path in TARGETS:
            target_bytes = (root / rel_path).read_bytes()
            drifted_sha = git_blob_sha1(target_bytes + b"# drift\n")
            note_path.write_text(
                replace_once(
                    read_text(note_path),
                    f"{key}=" + git_blob_sha1(target_bytes),
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
