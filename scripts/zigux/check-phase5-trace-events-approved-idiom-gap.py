#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

APPROVED_IDIOM_PATH = Path("Documentation/zigux/phase5-trace-events-approved-idiom-gap.md")

REQUIRED_PATHS = (
    "samples/trace_events/trace-events-sample.c",
    "Documentation/zigux/phase5-trace-events-sample-survey.md",
    "Documentation/zigux/phase5-sample-review-guide.md",
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/trace_events_string_formatting_sample.zig",
    "samples/zigux/trace_events_callback_focus_contract.zig",
    "samples/zigux/trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample_manifest.json",
    "zigux/tests/phase5_trace_events_sample_survey.zig",
    "zigux/tests/phase5_build.zig",
    "scripts/zigux/check-phase5-review-guide-surface.py",
)

REQUIRED_MARKERS = (
    "# Phase 5 Trace-Events Approved Idiom Gap",
    "The roadmap-backed Phase 5 trace-events anchor is still:",
    "samples/trace_events/trace-events-sample.c",
    "samples/zigux/trace_events_string_formatting_sample.zig",
    "samples/zigux/trace_events_callback_focus_contract.zig",
    "Documentation/zigux/phase5-trace-events-sample-survey.md",
    "samples/zigux/trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample_manifest.json",
    "zigux/tests/phase5_trace_events_sample_survey.zig",
    "zigux/tests/phase5_build.zig",
    "scripts/zigux/check-phase5-review-guide-surface.py",
    "selected-string plus `iter=%d`",
    "runStringFormattingCycleReplay()",
    "formatSelectedIterationMessageInto(3, [12]u8)",
    "checked_focus",
    "Current `master` still ships no standalone `samples/zigux/*printf*` or `*vsprintf*` Phase 5 reference sample",
    "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
    "Do not treat this note as proof of:",
    "standalone formatting-helper delivery",
    "standalone broad `*format*` sample delivery",
    "standalone string-helper delivery",
    "a fifth approved Phase 5 sample",
    "## Next bounded step",
)

FORBIDDEN_MARKERS = (
    "returned full trace-events port",
    "standalone Phase 5 formatting sample",
)


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def placeholder_note() -> str:
    lines = [marker for marker in REQUIRED_MARKERS if not marker.startswith("# ")]
    path_lines = [f"`{rel}`" for rel in REQUIRED_PATHS]
    return "# Phase 5 Trace-Events Approved Idiom Gap\n\n" + "\n\n".join(lines + path_lines) + "\n"


def strip_reference(text: str, rel: str) -> str:
    text = text.replace(f"`{rel}`", "", 1)
    text = text.replace(rel, "", 1)
    return text


def seed(root: Path) -> None:
    write_text(root, APPROVED_IDIOM_PATH, placeholder_note())
    for rel in REQUIRED_PATHS:
        write_text(root, Path(rel), "present\n")


def collect_failures(root: Path) -> list[str]:
    note = read_text(root, APPROVED_IDIOM_PATH)
    failures: list[str] = []

    for marker in REQUIRED_MARKERS:
        if marker not in note:
            failures.append(f"missing_text:{marker}")

    for rel in REQUIRED_PATHS:
        if f"`{rel}`" not in note and rel not in note:
            failures.append(f"missing_path_reference:{rel}")
        if not (root / rel).exists():
            failures.append(f"missing_repo_path:{rel}")

    for marker in FORBIDDEN_MARKERS:
        if marker in note:
            failures.append(f"forbidden_text:{marker}")

    return failures


def expect_exact(label: str, actual: list[str], expected: list[str]) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 8
    with tempfile.TemporaryDirectory(prefix="phase5_trace_events_approved_idiom_") as tmpdir:
        root = Path(tmpdir)

        seed(root)
        expect_exact("baseline", collect_failures(root), [])
        checks_run += 1

        mutated = root / "missing_marker"
        seed(mutated)
        write_text(
            mutated,
            APPROVED_IDIOM_PATH,
            placeholder_note().replace("selected-string plus `iter=%d`", "", 1),
        )
        expect_exact(
            "missing selected-string marker",
            collect_failures(mutated),
            ["missing_text:selected-string plus `iter=%d`"],
        )
        checks_run += 1

        mutated = root / "missing_path_reference"
        seed(mutated)
        write_text(
            mutated,
            APPROVED_IDIOM_PATH,
            strip_reference(placeholder_note(), "zigux/tests/phase5_build.zig"),
        )
        expect_exact(
            "missing shared build path reference",
            collect_failures(mutated),
            [
                "missing_text:zigux/tests/phase5_build.zig",
                "missing_path_reference:zigux/tests/phase5_build.zig",
            ],
        )
        checks_run += 1

        mutated = root / "missing_repo_path"
        seed(mutated)
        (mutated / "samples/zigux/trace_events_callback_focus_contract.zig").unlink()
        expect_exact(
            "missing repo path",
            collect_failures(mutated),
            ["missing_repo_path:samples/zigux/trace_events_callback_focus_contract.zig"],
        )
        checks_run += 1

        mutated = root / "missing_no_extra_sample_marker"
        seed(mutated)
        write_text(
            mutated,
            APPROVED_IDIOM_PATH,
            placeholder_note().replace(
                "a fifth approved Phase 5 sample",
                "",
                1,
            ),
        )
        expect_exact(
            "missing no-extra-sample marker",
            collect_failures(mutated),
            ["missing_text:a fifth approved Phase 5 sample"],
        )
        checks_run += 1

        mutated = root / "forbidden_full_port_claim"
        seed(mutated)
        write_text(
            mutated,
            APPROVED_IDIOM_PATH,
            placeholder_note() + "\nreturned full trace-events port\n",
        )
        expect_exact(
            "forbidden full-port claim",
            collect_failures(mutated),
            ["forbidden_text:returned full trace-events port"],
        )
        checks_run += 1

        mutated = root / "forbidden_standalone_sample_claim"
        seed(mutated)
        write_text(
            mutated,
            APPROVED_IDIOM_PATH,
            placeholder_note() + "\nstandalone Phase 5 formatting sample\n",
        )
        expect_exact(
            "forbidden standalone-sample claim",
            collect_failures(mutated),
            ["forbidden_text:standalone Phase 5 formatting sample"],
        )
        checks_run += 1

        mutated = root / "plain_path_allowed"
        seed(mutated)
        write_text(
            mutated,
            APPROVED_IDIOM_PATH,
            placeholder_note().replace("`samples/trace_events/trace-events-sample.c`", "samples/trace_events/trace-events-sample.c", 1),
        )
        expect_exact("plain path allowed", collect_failures(mutated), [])
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} self-test cases, ran {checks_run}")

    print("PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP_SELF_TEST=pass")
    print(f"PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP_SELF_TEST_CASES={checks_run}")
    return 0


def write_sample_root(root: Path) -> int:
    seed(root)
    print(f"WROTE_SAMPLE_ROOT={root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    parser.add_argument("--write-sample-root", type=Path, help="materialize a passing sample tree")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        return write_sample_root(args.write_sample_root)

    failures = collect_failures(args.root)
    if failures:
        print("PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP=pass")
    print(f"PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}")
    print(f"PHASE5_TRACE_EVENTS_APPROVED_IDIOM_GAP_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
