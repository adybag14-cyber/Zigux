#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOTE_PATH = Path("Documentation/zigux/phase5-trace-events-approved-idiom-gap.md")

REMINDER_PACKET_PATHS = (
    "Documentation/zigux/phase5-sample-review-guide.md",
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "samples/zigux/trace_events_string_formatting_sample.zig",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase5-review-guide-surface.py",
    "zigux/tests/README.md",
)

SPLIT_PACKET_PATHS = (
    "Documentation/zigux/phase5-trace-events-sample-survey.md",
    "samples/zigux/trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample_manifest.json",
    "zigux/tests/phase5_trace_events_sample_survey.zig",
    "zigux/tests/phase5_build.zig",
)

REQUIRED_TEXT = (
    "The roadmap-backed Phase 5 trace-events anchor is still:",
    "Authenticated sample-root readback still directly exposes this bounded non-runtime formatting companion:",
    "Fresh mixed reread on 2026-05-19 keeps the broader non-runtime trace-events sample-local companions in a split state rather than a missing state:",
    "Those paths are again carried by the live trace-events reminder packet and current public-tree-backed reread surfaces, but the authenticated contents route used for this lane still did not return them directly on 2026-05-19.",
    "The shared `zigux/tests/phase5_build.zig` route remains useful support material too, but keep it framed as current public-tree-backed companion evidence until authenticated contents reread returns that path directly again.",
    "That packet should keep the selected-string plus `iter=%d` formatting cue explicit while staying honest about the current split: the bounded formatting companion remains directly readable through the authenticated sample-root route, the broader non-runtime trace-events sample-local companions are visible again through the live public-tree-backed packet but are not yet returned authenticated proof in this lane, the shared `zigux/tests/phase5_build.zig` path is still public-tree-backed companion evidence rather than returned authenticated proof, and `scripts/zigux/check-phase5-review-guide-surface.py` remains the shipped shared guard for that reminder family rather than an optional extra.",
    "This run verified the current formatting companion with the attached Zig toolchain `0.17.0-dev.87+9b177a7d2` using a focused `zig test` against the current `master` file body.",
    "- `phase 5 trace-events formatting companion keeps the selected-string cue reviewable`",
    "- `phase 5 trace-events formatting companion keeps lifecycle boundaries explicit`",
    "- `phase 5 trace-events formatting companion keeps bounded destination failures explicit`",
    "- `runAnchorReplay(7)` still keeps the roadmap anchor explicit, transitions from `.initialized` to `.replay_complete`, selects `\"Gandalf\"`, and renders `\"iter=7\"` with length `6` while keeping four focus cues visible.",
    "- bounded destination behavior is now directly covered too: `formatIterationMessageInto(12, [5]u8)` returns `error.NoSpaceLeft` without changing the sample stage or incrementing `replay_runs`, while `formatIterationMessageInto(12, [7]u8)` returns `\"iter=12\"` and keeps the sample in the `.initialized` stage.",
    "Current `master` still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample outside the bounded trace-events companion.",
    "Current `master` also still ships no standalone Phase 5 `samples/zigux/*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
    "Keep that no-extra-sample boundary separate from the bounded trace-events formatting companion so this note does not blur helper-family reminders into trace-events proof.",
    "Do not treat this note as proof of:",
    "- standalone formatting-helper delivery",
    "- standalone broad `*format*` sample delivery",
    "- standalone `printf` parity",
    "- standalone `vsprintf` parity",
    "- standalone string-helper delivery",
    "- standalone `*cmdline*` sample delivery",
    "- standalone `*argv*` sample delivery",
    "- standalone `*rbtree*` sample delivery",
    "- standalone `*bitmap*` sample delivery",
    "- a fifth approved Phase 5 sample",
    "Keep standalone formatting-helper evidence under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 helper reminders, keep `cmdline`, `argv_split`, and `rbtree` evidence under the bounded Phase 7 helper packet, keep direct bitmap helper reviewability under the closed Phase 1 plus bounded Phase 4 reminder packet, and keep runtime-facing trace-events loader work under the separate Phase 9 lane.",
    "Leave this note parked unless a fresh reread shows that another shared trace-events reminder surface still collapses the current split by treating the broader sample-local packet as fully missing, or by promoting it to fully returned authenticated proof before the contents route actually does so, or by losing the selected-string plus `iter=%d` cue or the shipped guide-surface guard.",
)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    note = _read(root / NOTE_PATH)
    failures: list[str] = []

    for marker in REQUIRED_TEXT:
        if marker not in note:
            failures.append(f"note:missing_text:{marker}")

    for rel in REMINDER_PACKET_PATHS:
        marker = f"`{rel}`"
        if marker not in note:
            failures.append(f"note:missing_reminder_path:{marker}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_reminder_path:{rel}")

    for rel in SPLIT_PACKET_PATHS:
        marker = f"`{rel}`"
        if marker not in note:
            failures.append(f"note:missing_split_path:{marker}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_split_path:{rel}")

    return failures


def _sample_note() -> str:
    reminder_paths = "\n".join(f"- `{rel}`" for rel in REMINDER_PACKET_PATHS)
    split_paths = "\n".join(f"- `{rel}`" for rel in SPLIT_PACKET_PATHS[:-1])
    return f"""# Phase 5 Trace-Events Approved Idiom Gap

This note keeps the roadmap-backed Phase 5 trace-events packet truthful when shared reviewer surfaces need to mention the bounded formatting idiom that current `master` still approves.

## Current approved cue on `master`

The roadmap-backed Phase 5 trace-events anchor is still:

- `samples/trace_events/trace-events-sample.c`

Authenticated sample-root readback still directly exposes this bounded non-runtime formatting companion:

- `samples/zigux/trace_events_string_formatting_sample.zig`

Fresh mixed reread on 2026-05-19 keeps the broader non-runtime trace-events sample-local companions in a split state rather than a missing state:

{split_paths}

Those paths are again carried by the live trace-events reminder packet and current public-tree-backed reread surfaces, but the authenticated contents route used for this lane still did not return them directly on 2026-05-19.

The shared `zigux/tests/phase5_build.zig` route remains useful support material too, but keep it framed as current public-tree-backed companion evidence until authenticated contents reread returns that path directly again.

Keep the approved formatting idiom bounded to the current landed reminder packet:

{reminder_paths}

That packet should keep the selected-string plus `iter=%d` formatting cue explicit while staying honest about the current split: the bounded formatting companion remains directly readable through the authenticated sample-root route, the broader non-runtime trace-events sample-local companions are visible again through the live public-tree-backed packet but are not yet returned authenticated proof in this lane, the shared `zigux/tests/phase5_build.zig` path is still public-tree-backed companion evidence rather than returned authenticated proof, and `scripts/zigux/check-phase5-review-guide-surface.py` remains the shipped shared guard for that reminder family rather than an optional extra.

## Exact checks run on 2026-05-19

This run verified the current formatting companion with the attached Zig toolchain `0.17.0-dev.87+9b177a7d2` using a focused `zig test` against the current `master` file body.

The exact checks that passed were:

- `phase 5 trace-events formatting companion keeps the selected-string cue reviewable`
- `phase 5 trace-events formatting companion keeps lifecycle boundaries explicit`
- `phase 5 trace-events formatting companion keeps bounded destination failures explicit`

Those checks confirmed this current sample behavior:

- `runAnchorReplay(7)` still keeps the roadmap anchor explicit, transitions from `.initialized` to `.replay_complete`, selects `"Gandalf"`, and renders `"iter=7"` with length `6` while keeping four focus cues visible.
- lifecycle boundaries still fail closed: replay before `init()` and `exit()` before initialization both reject with `error.InvalidLifecycleTransition`; negative replay input rejects with `error.InvalidIterationCount`; replay after `exit()` rejects again; the successful replay-plus-exit path leaves `init_runs`, `replay_runs`, and `exit_runs` at `1` each.
- bounded destination behavior is now directly covered too: `formatIterationMessageInto(12, [5]u8)` returns `error.NoSpaceLeft` without changing the sample stage or incrementing `replay_runs`, while `formatIterationMessageInto(12, [7]u8)` returns `"iter=12"` and keeps the sample in the `.initialized` stage.

## Review boundary

Current `master` still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample outside the bounded trace-events companion.
Current `master` also still ships no standalone Phase 5 `samples/zigux/*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.
Keep that no-extra-sample boundary separate from the bounded trace-events formatting companion so this note does not blur helper-family reminders into trace-events proof.

Use this note only to restate the bounded formatting cue that Phase 5 reviewers should preserve inside the roadmap-backed `trace_events` anchor.

Do not treat this note as proof of:

- standalone formatting-helper delivery
- standalone broad `*format*` sample delivery
- standalone `printf` parity
- standalone `vsprintf` parity
- standalone string-helper delivery
- standalone `*cmdline*` sample delivery
- standalone `*argv*` sample delivery
- standalone `*rbtree*` sample delivery
- standalone `*bitmap*` sample delivery
- a fifth approved Phase 5 sample

Keep standalone formatting-helper evidence under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 helper reminders, keep `cmdline`, `argv_split`, and `rbtree` evidence under the bounded Phase 7 helper packet, keep direct bitmap helper reviewability under the closed Phase 1 plus bounded Phase 4 reminder packet, and keep runtime-facing trace-events loader work under the separate Phase 9 lane.

## Next bounded step

Leave this note parked unless a fresh reread shows that another shared trace-events reminder surface still collapses the current split by treating the broader sample-local packet as fully missing, or by promoting it to fully returned authenticated proof before the contents route actually does so, or by losing the selected-string plus `iter=%d` cue or the shipped guide-surface guard.
"""


def _seed(root: Path) -> None:
    _write(root / NOTE_PATH, _sample_note())
    for rel in REMINDER_PACKET_PATHS + SPLIT_PACKET_PATHS:
        _write(root / rel, "present\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 7
    with tempfile.TemporaryDirectory(prefix="phase5_trace_events_approved_idiom_gap_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        checks_run += 1

        missing_required_text_root = root / "missing_required_text"
        _seed(missing_required_text_root)
        _write(
            missing_required_text_root / NOTE_PATH,
            _sample_note().replace(REQUIRED_TEXT[6], "", 1),
        )
        failures = collect_failures(missing_required_text_root)
        expected = [f"note:missing_text:{REQUIRED_TEXT[6]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-required-text failure: {failures}")
        checks_run += 1

        missing_reminder_path_root = root / "missing_reminder_path"
        _seed(missing_reminder_path_root)
        _write(
            missing_reminder_path_root / NOTE_PATH,
            _sample_note().replace("`samples/zigux/README.md`", "", 1),
        )
        failures = collect_failures(missing_reminder_path_root)
        expected = ["note:missing_reminder_path:`samples/zigux/README.md`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-reminder-path failure: {failures}")
        checks_run += 1

        missing_split_path_root = root / "missing_split_path"
        _seed(missing_split_path_root)
        _write(
            missing_split_path_root / NOTE_PATH,
            _sample_note().replace("`zigux/tests/phase5_trace_events_sample_manifest.json`", "", 1),
        )
        failures = collect_failures(missing_split_path_root)
        expected = ["note:missing_split_path:`zigux/tests/phase5_trace_events_sample_manifest.json`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-split-path failure: {failures}")
        checks_run += 1

        missing_repo_file_root = root / "missing_repo_file"
        _seed(missing_repo_file_root)
        (missing_repo_file_root / "zigux/tests/phase5_build.zig").unlink()
        failures = collect_failures(missing_repo_file_root)
        expected = ["repo:missing_split_path:zigux/tests/phase5_build.zig"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-repo-file failure: {failures}")
        checks_run += 1

        missing_boundary_root = root / "missing_boundary"
        _seed(missing_boundary_root)
        _write(
            missing_boundary_root / NOTE_PATH,
            _sample_note().replace("- a fifth approved Phase 5 sample", "", 1),
        )
        failures = collect_failures(missing_boundary_root)
        expected = ["note:missing_text:- a fifth approved Phase 5 sample"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-boundary failure: {failures}")
        checks_run += 1

        missing_note_root = root / "missing_note"
        _seed(missing_note_root)
        (missing_note_root / NOTE_PATH).unlink()
        try:
            collect_failures(missing_note_root)
        except SystemExit as exc:
            if "required file missing" not in str(exc):
                raise AssertionError(f"unexpected missing-note abort: {exc}") from exc
        else:
            raise AssertionError("missing note did not abort")
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} checks, ran {checks_run}")
    print("PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP_SELF_TEST=pass")
    print(f"PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 5 trace-events approved-idiom note stays aligned with the current reminder packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1
    print("PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP=pass")
    print(f"PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP_REMINDER_PACKET_COUNT={len(REMINDER_PACKET_PATHS)}")
    print(f"PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP_SPLIT_PACKET_COUNT={len(SPLIT_PACKET_PATHS)}")
    print(f"PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP_REQUIRED_TEXT_COUNT={len(REQUIRED_TEXT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
