#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")

FREEZE_POSTURE_PROMPT = "if the change touches the shared Phase 15 freeze-posture packet"
FREEZE_POSTURE_MARKERS = (
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "keep the same study-only anchor inventory",
    "keep the current materialized focused governance companions visible as present evidence",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "`zigux/tests/phase15_build.zig`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "repo-reality gaps rather than shipped evidence or Architecture Council approval",
)

ENTRY_REVIEW_PROMPT = "if a freeze-map anchor is entering Architecture Council status review"
ENTRY_REVIEW_FIELDS = (
    "exact Linux anchor path",
    "roadmap phase",
    "decision record ID",
    "lane owner",
    "current status bucket",
    "requested decision bucket",
    "required approver set",
    "rollback owner",
    "validation gate summary",
    "evidence archive path",
    "latest blocker disposition",
    "benchmark notes",
    "replay command",
    "rollback threshold",
    "automatic return-to-blocked trigger",
    "retained discussion state",
    "reopen triggers",
    "trigger-specific evidence refresh",
    "parity scorecard link or blocker record",
    "indefinite-C policy link or non-applicability note",
    "explicit non-goals",
    "written rationale",
)

STAY_IN_C_PROMPT = "if a freeze-map anchor is closing review with a stay-in-C outcome"
STAY_IN_C_FIELDS = (
    "retained `freeze_in_c` decision",
    "required approver set",
    "retained `retired_from_active_discussion` state",
    "current blocker",
    "evidence archive path",
    "reopen triggers",
)

BLOCKED_PROMPT = "if a freeze-map anchor remains blocked"
BLOCKED_OWNER_MARKER = "current lane owner responsible for keeping that blocked evidence packet up to date"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _line_containing(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line
    return None


def collect_failures(root: Path) -> list[str]:
    checklist = _read(root / REVIEW_CHECKLIST_PATH)
    failures: list[str] = []

    freeze_line = _line_containing(checklist, FREEZE_POSTURE_PROMPT)
    if freeze_line is None:
        failures.append(f"freeze_posture:missing:{FREEZE_POSTURE_PROMPT}")
    else:
        for marker in FREEZE_POSTURE_MARKERS:
            if marker not in freeze_line:
                failures.append(f"freeze_posture:missing:{marker}")

    entry_line = _line_containing(checklist, ENTRY_REVIEW_PROMPT)
    if entry_line is None:
        failures.append(f"entry_review:missing:{ENTRY_REVIEW_PROMPT}")
    else:
        for field in ENTRY_REVIEW_FIELDS:
            if field not in entry_line:
                failures.append(f"entry_review_field:missing:{field}")

    stay_in_c_line = _line_containing(checklist, STAY_IN_C_PROMPT)
    if stay_in_c_line is None:
        failures.append(f"stay_in_c:missing:{STAY_IN_C_PROMPT}")
    else:
        for field in STAY_IN_C_FIELDS:
            if field not in stay_in_c_line:
                failures.append(f"stay_in_c_field:missing:{field}")

    blocked_line = _line_containing(checklist, BLOCKED_PROMPT)
    if blocked_line is None:
        failures.append(f"blocked_prompt:missing:{BLOCKED_PROMPT}")
    elif BLOCKED_OWNER_MARKER not in blocked_line:
        failures.append(f"blocked_prompt:missing:{BLOCKED_OWNER_MARKER}")

    return failures


def _sample_review_checklist() -> str:
    freeze = (
        "  * if the change touches the shared Phase 15 freeze-posture packet, do "
        "`Documentation/zigux/freeze-map.md`, `Documentation/zigux/review-checklist.md`, "
        "`Documentation/zigux/phase15-study-only-anchor-accounting.md`, "
        "`Documentation/zigux/phase15-handoff-next-steps-survey.md`, and "
        "`Documentation/zigux/phase15-shared-summary-gap.md` keep the same study-only anchor "
        "inventory, keep the current materialized focused governance companions visible as present "
        "evidence, and keep only the still-missing broader validator-first companions "
        "`scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_handoff_next_steps_manifest.json`, "
        "`zigux/tests/phase15_build.zig`, and `zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig` "
        "framed as repo-reality gaps rather than shipped evidence or Architecture Council approval?\n"
    )
    entry = (
        "  * if a freeze-map anchor is entering Architecture Council status review, are the "
        "exact Linux anchor path, roadmap phase, decision record ID, lane owner, current "
        "status bucket, requested decision bucket, required approver set, rollback owner, "
        "validation gate summary, evidence archive path, latest blocker disposition, benchmark "
        "notes, replay command, rollback threshold, automatic return-to-blocked trigger, "
        "retained discussion state, reopen triggers, trigger-specific evidence refresh, parity "
        "scorecard link or blocker record, indefinite-C policy link or non-applicability note, "
        "explicit non-goals, and written rationale explicit?\n"
    )
    stay_in_c = (
        "  * if a freeze-map anchor is closing review with a stay-in-C outcome, are the "
        "retained `freeze_in_c` decision, required approver set, retained "
        "`retired_from_active_discussion` state, current blocker, evidence archive path, and "
        "reopen triggers explicit?\n"
    )
    blocked = (
        "  * if a freeze-map anchor remains blocked, does the scorecard still name the current "
        "lane owner responsible for keeping that blocked evidence packet up to date?\n"
    )
    return "# Zigux Review Checklist\n\n" + freeze + entry + stay_in_c + blocked


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_review_checklist_") as tmpdir:
        root = Path(tmpdir)
        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline review checklist fixture should pass: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`", "", 1
            ),
        )
        failures = collect_failures(root)
        expected = ["freeze_posture:missing:`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`"]
        if failures != expected:
            raise AssertionError(f"unexpected freeze-posture failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace("rollback threshold, ", "", 1),
        )
        failures = collect_failures(root)
        expected = ["entry_review_field:missing:rollback threshold"]
        if failures != expected:
            raise AssertionError(f"unexpected entry-review failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "current blocker, evidence archive path, and reopen triggers explicit?",
                "current blocker and evidence archive path explicit?",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = ["stay_in_c_field:missing:reopen triggers"]
        if failures != expected:
            raise AssertionError(f"unexpected stay-in-C failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(BLOCKED_OWNER_MARKER, "", 1),
        )
        failures = collect_failures(root)
        expected = [f"blocked_prompt:missing:{BLOCKED_OWNER_MARKER}"]
        if failures != expected:
            raise AssertionError(f"unexpected blocked-prompt failure: {failures}")
        case_count += 1

    print("PHASE15_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 15 review-checklist prompt stays aligned with the current governance packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 review-checklist alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
