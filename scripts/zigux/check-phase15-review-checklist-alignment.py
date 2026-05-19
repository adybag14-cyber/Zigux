#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")

ENTRY_REVIEW_PROMPT = "if a freeze-map anchor is entering Architecture Council status review"
ENTRY_REVIEW_MARKERS = (
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
    "exact Architecture Council field inventory",
    "stay-in-C closeout record",
    "reopen-evidence details",
)
STUDY_ONLY_PROMPT = "if a shared reminder surface summarizes the study-only freeze-map anchors"
STUDY_ONLY_MARKERS = (
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "study-only boundary context",
    "runtime-substrate or bridge-readiness evidence",
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


def _check_line(line: str | None, prompt: str, markers: tuple[str, ...], prefix: str) -> list[str]:
    failures: list[str] = []
    if line is None:
        failures.append(f"{prefix}:missing:{prompt}")
        return failures
    for marker in markers:
        if marker not in line:
            failures.append(f"{prefix}_field:missing:{marker}")
    return failures


def collect_failures(root: Path) -> list[str]:
    checklist = _read(root / REVIEW_CHECKLIST_PATH)
    failures: list[str] = []
    failures.extend(
        _check_line(
            _line_containing(checklist, ENTRY_REVIEW_PROMPT),
            ENTRY_REVIEW_PROMPT,
            ENTRY_REVIEW_MARKERS,
            "entry_review",
        )
    )
    failures.extend(
        _check_line(
            _line_containing(checklist, STUDY_ONLY_PROMPT),
            STUDY_ONLY_PROMPT,
            STUDY_ONLY_MARKERS,
            "study_only",
        )
    )
    return failures


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

Use this checklist before opening or merging Zigux product work.

## Safety
  * if a freeze-map anchor is entering Architecture Council status review, does this checklist keep the shared entry-review prompt explicit while `Documentation/zigux/phase15-architecture-council-review-process.md` and `Documentation/zigux/phase15-architecture-council-decision-record-template.md` remain the owners of the exact Architecture Council field inventory, stay-in-C closeout record, and reopen-evidence details?
  * if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?
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
            _sample_review_checklist().replace(
                "`Documentation/zigux/phase15-architecture-council-decision-record-template.md`",
                "decision-record-template.md",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "entry_review_field:missing:`Documentation/zigux/phase15-architecture-council-decision-record-template.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected decision-record-template failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace("stay-in-C closeout record, and ", "", 1),
        )
        failures = collect_failures(root)
        expected = ["entry_review_field:missing:stay-in-C closeout record"]
        if failures != expected:
            raise AssertionError(f"unexpected stay-in-C-closeout failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
                "phase15-study-only-anchor-accounting.md",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "study_only_field:missing:`Documentation/zigux/phase15-study-only-anchor-accounting.md`"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected study-only-note failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace("`kernel/trace/ring_buffer.c`", "kernel/trace/ring_buffer.c", 1),
        )
        failures = collect_failures(root)
        expected = ["study_only_field:missing:`kernel/trace/ring_buffer.c`"]
        if failures != expected:
            raise AssertionError(f"unexpected ring-buffer failure: {failures}")
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
