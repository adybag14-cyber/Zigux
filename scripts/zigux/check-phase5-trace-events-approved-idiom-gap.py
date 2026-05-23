#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

NOTE_PATH = Path("Documentation/zigux/phase5-trace-events-approved-idiom-gap.md")

DIRECT_PATHS = (
    "samples/zigux/trace_events_string_formatting_sample.zig",
    "zigux/tests/phase5_build.zig",
)

PUBLIC_TREE_COMPANION_PATHS = (
    "Documentation/zigux/phase5-trace-events-sample-survey.md",
    "samples/zigux/trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample_manifest.json",
    "zigux/tests/phase5_trace_events_sample_survey.zig",
)

SHARED_SURFACE_PATHS = (
    "Documentation/zigux/phase5-sample-review-guide.md",
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-phase5-review-guide-surface.py",
    "zigux/tests/README.md",
)

REQUIRED_MARKERS = (
    "Authenticated sample-root readback still directly exposes this bounded non-runtime formatting companion:",
    "The shared `zigux/tests/phase5_build.zig` route remains useful support material too, and the current lane reread now returns that path directly again. Keep it framed as returned shared build-route evidence rather than as part of the broader sample-local companion set.",
    "Keep the approved formatting idiom bounded to the current landed reminder packet:",
    "Keep the bounded destination discipline explicit in that same reminder packet too: `formatIterationMessageInto(12, [5]u8)` still returns `error.NoSpaceLeft` without advancing the sample stage or `replay_runs`, while `formatIterationMessageInto(12, [7]u8)` still returns `\\\"iter=12\\\"` and keeps the sample in `.initialized`.",
    "Keep the direct modulo-selected cycle explicit too: `runStringFormattingCycleReplay()` now walks all five selected strings through the bounded `iter=%d` formatter while keeping the companion in `.initialized` and leaving `replay_runs` unchanged.",
    "Keep the sample-owned review contract explicit too: the bounded formatting companion now centralizes the exact `checked_focus` order `string_selection,formatted_message,bounded_destination_discipline,non_allocating_runtime_safe`, and the approved-idiom reminder should preserve that same reading order beside the selected-string slot and `iter=%d` cue instead of reducing the trace-events packet to message text alone.",
    "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
    "Leave this note parked unless a fresh reread shows that another shared trace-events reminder surface still collapses the current split by treating the broader sample-local packet as fully missing, or by promoting it to fully returned authenticated proof before the contents route actually does so, or by losing the selected-string plus `iter=%d` cue, the exact `checked_focus` review order, or the shipped guide-surface guard.",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def placeholder_note() -> str:
    lines = [
        "# Phase 5 Trace-Events Approved Idiom Gap",
        "",
        "Authenticated sample-root readback still directly exposes this bounded non-runtime formatting companion:",
        "",
    ]
    lines.extend(f"- `{path}`" for path in DIRECT_PATHS[:1])
    lines.extend(
        (
            "",
            "Fresh mixed reread on 2026-05-20 keeps the broader non-runtime trace-events sample-local companions in a split state rather than a missing state:",
            "",
        )
    )
    lines.extend(f"- `{path}`" for path in PUBLIC_TREE_COMPANION_PATHS)
    lines.extend(
        (
            "",
            "The shared `zigux/tests/phase5_build.zig` route remains useful support material too, and the current lane reread now returns that path directly again. Keep it framed as returned shared build-route evidence rather than as part of the broader sample-local companion set.",
            "",
            "- `zigux/tests/phase5_build.zig`",
            "",
            "Keep the approved formatting idiom bounded to the current landed reminder packet:",
            "",
            f"- `{NOTE_PATH}`",
        )
    )
    lines.extend(f"- `{path}`" for path in SHARED_SURFACE_PATHS)
    lines.extend(
        (
            "",
            "Keep the bounded destination discipline explicit in that same reminder packet too: `formatIterationMessageInto(12, [5]u8)` still returns `error.NoSpaceLeft` without advancing the sample stage or `replay_runs`, while `formatIterationMessageInto(12, [7]u8)` still returns `\\\"iter=12\\\"` and keeps the sample in `.initialized`.",
            "",
            "Keep the direct modulo-selected cycle explicit too: `runStringFormattingCycleReplay()` now walks all five selected strings through the bounded `iter=%d` formatter while keeping the companion in `.initialized` and leaving `replay_runs` unchanged.",
            "",
            "Keep the sample-owned review contract explicit too: the bounded formatting companion now centralizes the exact `checked_focus` order `string_selection,formatted_message,bounded_destination_discipline,non_allocating_runtime_safe`, and the approved-idiom reminder should preserve that same reading order beside the selected-string slot and `iter=%d` cue instead of reducing the trace-events packet to message text alone.",
            "",
            "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
            "",
            "Leave this note parked unless a fresh reread shows that another shared trace-events reminder surface still collapses the current split by treating the broader sample-local packet as fully missing, or by promoting it to fully returned authenticated proof before the contents route actually does so, or by losing the selected-string plus `iter=%d` cue, the exact `checked_focus` review order, or the shipped guide-surface guard.",
            "",
        )
    )
    return "\n".join(lines)


def seed(root: Path) -> None:
    write_text(root / NOTE_PATH, placeholder_note())
    for path in DIRECT_PATHS + PUBLIC_TREE_COMPANION_PATHS + SHARED_SURFACE_PATHS:
        write_text(root / path, "present\n")


def collect_failures(root: Path) -> list[str]:
    note = read_text(root / NOTE_PATH)
    failures: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in note:
            failures.append(f"note:missing_text:{marker}")

    for path in DIRECT_PATHS:
        if f"`{path}`" not in note:
            failures.append(f"note:missing_direct_path:{path}")
        if not (root / path).exists():
            failures.append(f"repo:missing_direct_path:{path}")

    for path in PUBLIC_TREE_COMPANION_PATHS:
        if f"`{path}`" not in note:
            failures.append(f"note:missing_public_path:{path}")
        if not (root / path).exists():
            failures.append(f"repo:missing_public_path:{path}")

    for path in SHARED_SURFACE_PATHS:
        if f"`{path}`" not in note:
            failures.append(f"note:missing_shared_surface_path:{path}")
        if not (root / path).exists():
            failures.append(f"repo:missing_shared_surface_path:{path}")

    return failures


def expect_exact(label: str, failures: list[str], expected: list[str]) -> None:
    if failures != expected:
        raise AssertionError(f"{label}: expected {expected}, got {failures}")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 7
    with tempfile.TemporaryDirectory(prefix="phase5_trace_events_idiom_gap_") as tmpdir:
        root = Path(tmpdir)
        seed(root)

        expect_exact("baseline", collect_failures(root), [])
        checks_run += 1

        mutated = root / "missing_build_route_marker"
        seed(mutated)
        write_text(mutated / NOTE_PATH, placeholder_note().replace(REQUIRED_MARKERS[1], "", 1))
        expect_exact(
            "missing_build_route_marker",
            collect_failures(mutated),
            [f"note:missing_text:{REQUIRED_MARKERS[1]}"],
        )
        checks_run += 1

        mutated = root / "missing_checked_focus_marker"
        seed(mutated)
        write_text(mutated / NOTE_PATH, placeholder_note().replace(REQUIRED_MARKERS[5], "", 1))
        expect_exact(
            "missing_checked_focus_marker",
            collect_failures(mutated),
            [f"note:missing_text:{REQUIRED_MARKERS[5]}"],
        )
        checks_run += 1

        mutated = root / "missing_cycle_marker"
        seed(mutated)
        write_text(mutated / NOTE_PATH, placeholder_note().replace(REQUIRED_MARKERS[4], "", 1))
        expect_exact(
            "missing_cycle_marker",
            collect_failures(mutated),
            [f"note:missing_text:{REQUIRED_MARKERS[4]}"],
        )
        checks_run += 1

        mutated = root / "missing_direct_repo_path"
        seed(mutated)
        (mutated / DIRECT_PATHS[1]).unlink()
        expect_exact(
            "missing_direct_repo_path",
            collect_failures(mutated),
            [f"repo:missing_direct_path:{DIRECT_PATHS[1]}"],
        )
        checks_run += 1

        mutated = root / "missing_public_repo_path"
        seed(mutated)
        (mutated / PUBLIC_TREE_COMPANION_PATHS[-1]).unlink()
        expect_exact(
            "missing_public_repo_path",
            collect_failures(mutated),
            [f"repo:missing_public_path:{PUBLIC_TREE_COMPANION_PATHS[-1]}"],
        )
        checks_run += 1

        mutated = root / "missing_note"
        seed(mutated)
        (mutated / NOTE_PATH).unlink()
        try:
            collect_failures(mutated)
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
        description="Verify that the Phase 5 trace-events approved-idiom note keeps its bounded formatting packet truthful."
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
    print(f"PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP_DIRECT_PATH_COUNT={len(DIRECT_PATHS)}")
    print(f"PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP_PUBLIC_PATH_COUNT={len(PUBLIC_TREE_COMPANION_PATHS)}")
    print(f"PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP_SHARED_SURFACE_COUNT={len(SHARED_SURFACE_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
