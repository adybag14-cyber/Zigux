#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")

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
    "`retired_from_active_discussion` state",
    "reopen triggers",
    "trigger-specific evidence refresh",
    "parity scorecard link or blocker record",
    "indefinite-C policy link or explicit non-applicability note",
    "explicit non-goals",
    "written rationale",
)
FORBIDDEN_MARKERS = (
    "retained discussion state",
    "indefinite-C policy link or non-applicability note",
)


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

    entry_line = _line_containing(checklist, ENTRY_REVIEW_PROMPT)
    if entry_line is None:
        failures.append(f"entry_review:missing:{ENTRY_REVIEW_PROMPT}")
    else:
        for field in ENTRY_REVIEW_FIELDS:
            if field not in entry_line:
                failures.append(f"entry_review_field:missing:{field}")

    for marker in FORBIDDEN_MARKERS:
        if marker in checklist:
            failures.append(f"entry_review:forbidden:{marker}")

    return failures


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

Use this checklist before opening or merging Zigux product work.

## Safety

  * if a freeze-map anchor is entering Architecture Council status review, are the exact Linux anchor path, roadmap phase, decision record ID, lane owner, current status bucket, requested decision bucket, required approver set, rollback owner, validation gate summary, evidence archive path, latest blocker disposition, benchmark notes, replay command, rollback threshold, automatic return-to-blocked trigger, `retired_from_active_discussion` state, reopen triggers, trigger-specific evidence refresh, parity scorecard link or blocker record, indefinite-C policy link or explicit non-applicability note, explicit non-goals, and written rationale explicit?
"""


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
            _sample_review_checklist().replace("explicit non-goals, and ", "", 1),
        )
        failures = collect_failures(root)
        expected = ["entry_review_field:missing:explicit non-goals"]
        if failures != expected:
            raise AssertionError(f"unexpected explicit-non-goals failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "`retired_from_active_discussion` state",
                "retained discussion state",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "entry_review_field:missing:`retired_from_active_discussion` state",
            "entry_review:forbidden:retained discussion state",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected retained-discussion failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "indefinite-C policy link or explicit non-applicability note",
                "indefinite-C policy link or non-applicability note",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "entry_review_field:missing:indefinite-C policy link or explicit non-applicability note",
            "entry_review:forbidden:indefinite-C policy link or non-applicability note",
        ]
        if failures != expected:
            raise AssertionError(f"unexpected non-applicability wording failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                ENTRY_REVIEW_PROMPT,
                "if some other review packet is entering status review",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [f"entry_review:missing:{ENTRY_REVIEW_PROMPT}"]
        if failures != expected:
            raise AssertionError(f"unexpected entry-prompt failure: {failures}")
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
