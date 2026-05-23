#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

APPROVED_IDIOM_PATH = Path("Documentation/zigux/phase5-trace-events-approved-idiom-gap.md")
LANE_SEQUENCING_PATH = Path("Documentation/zigux/phase5-sample-lane-sequencing.md")
SAMPLE_ROOT_PATH = Path("samples/zigux/README.md")
TESTS_ROOT_PATH = Path("zigux/tests/README.md")

REQUIRED_MARKERS = {
    APPROVED_IDIOM_PATH: (
        "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
        "Current `master` still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample outside the bounded trace-events companion.",
        "Keep the approved formatting idiom bounded to the current landed reminder packet:",
        "`samples/zigux/trace_events_string_formatting_sample.zig`",
    ),
    LANE_SEQUENCING_PATH: (
        "there is no standalone `samples/zigux/*kasprintf*` Phase 5 reference sample on current `master`",
        "there is no standalone `samples/zigux/*strarray*` Phase 5 reference sample on current `master`",
        "there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep that formatting boundary tied to `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` and the bounded `samples/zigux/trace_events_string_formatting_sample.zig` companion",
        "Treat `samples/zigux/trace_events_string_formatting_sample.zig` as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.",
    ),
    SAMPLE_ROOT_PATH: (
        "* `*kasprintf*`",
        "* `*strarray*`",
        "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here.",
        "Current `master` does ship one bounded `*string*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`, but keep it tied to the non-runtime `trace_events` anchor instead of treating it as a standalone helper packet or a fifth Phase 5 sample.",
    ),
    TESTS_ROOT_PATH: (
        "Keep `samples/zigux/runtime_*.zig` plus standalone `*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 tests-root packet.",
        "keep `samples/zigux/trace_events_string_formatting_sample.zig` framed only as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample",
    ),
}

FORBIDDEN_MARKERS = (
    "standalone formatting-helper delivery",
    "a fifth approved Phase 5 sample",
)


def read_text(root: Path, rel: Path) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {rel}") from exc


def write_text(root: Path, rel: Path, text: str) -> None:
    full = root / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(text, encoding="utf-8")


def seed(root: Path) -> None:
    for rel, markers in REQUIRED_MARKERS.items():
        write_text(root, rel, "\n".join(markers) + "\n")


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    texts = {rel: read_text(root, rel) for rel in REQUIRED_MARKERS}

    for rel, markers in REQUIRED_MARKERS.items():
        text = texts[rel]
        for marker in markers:
            if marker not in text:
                failures.append(f"{rel}:missing_text:{marker}")

    approved_text = texts[APPROVED_IDIOM_PATH]
    if "Keep the approved formatting idiom bounded to the current landed reminder packet:" in approved_text:
        for forbidden in FORBIDDEN_MARKERS:
            if forbidden not in approved_text:
                failures.append(f"{APPROVED_IDIOM_PATH}:missing_boundary:{forbidden}")

    return failures


def expect_exact(label: str, failures: list[str], expected: list[str]) -> None:
    if failures != expected:
        raise AssertionError(f"{label}: expected {expected}, got {failures}")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 7

    with tempfile.TemporaryDirectory(prefix="phase5_string_formatting_gap_") as tmpdir:
        root = Path(tmpdir)
        seed(root)

        expect_exact(
            "baseline",
            collect_failures(root),
            [
                f"{APPROVED_IDIOM_PATH}:missing_boundary:{FORBIDDEN_MARKERS[0]}",
                f"{APPROVED_IDIOM_PATH}:missing_boundary:{FORBIDDEN_MARKERS[1]}",
            ],
        )
        checks_run += 1

        approved = read_text(root, APPROVED_IDIOM_PATH)
        write_text(
            root,
            APPROVED_IDIOM_PATH,
            approved + "\nstandalone formatting-helper delivery\na fifth approved Phase 5 sample\n",
        )
        expect_exact("approved_boundary_repaired", collect_failures(root), [])
        checks_run += 1

        mutated = Path(tmpdir) / "missing_kasprintf"
        seed(mutated)
        write_text(
            mutated,
            SAMPLE_ROOT_PATH,
            read_text(mutated, SAMPLE_ROOT_PATH).replace("* `*kasprintf*`\n", ""),
        )
        expect_exact(
            "missing_kasprintf",
            collect_failures(mutated),
            [
                f"{SAMPLE_ROOT_PATH}:missing_text:* `*kasprintf*`",
                f"{APPROVED_IDIOM_PATH}:missing_boundary:{FORBIDDEN_MARKERS[0]}",
                f"{APPROVED_IDIOM_PATH}:missing_boundary:{FORBIDDEN_MARKERS[1]}",
            ],
        )
        checks_run += 1

        mutated = Path(tmpdir) / "missing_strarray"
        seed(mutated)
        write_text(
            mutated,
            LANE_SEQUENCING_PATH,
            read_text(mutated, LANE_SEQUENCING_PATH).replace(REQUIRED_MARKERS[LANE_SEQUENCING_PATH][1], ""),
        )
        expect_exact(
            "missing_strarray",
            collect_failures(mutated),
            [
                f"{LANE_SEQUENCING_PATH}:missing_text:{REQUIRED_MARKERS[LANE_SEQUENCING_PATH][1]}",
                f"{APPROVED_IDIOM_PATH}:missing_boundary:{FORBIDDEN_MARKERS[0]}",
                f"{APPROVED_IDIOM_PATH}:missing_boundary:{FORBIDDEN_MARKERS[1]}",
            ],
        )
        checks_run += 1

        mutated = Path(tmpdir) / "missing_format_boundary"
        seed(mutated)
        write_text(
            mutated,
            TESTS_ROOT_PATH,
            read_text(mutated, TESTS_ROOT_PATH).replace(REQUIRED_MARKERS[TESTS_ROOT_PATH][0], ""),
        )
        expect_exact(
            "missing_format_boundary",
            collect_failures(mutated),
            [
                f"{TESTS_ROOT_PATH}:missing_text:{REQUIRED_MARKERS[TESTS_ROOT_PATH][0]}",
                f"{APPROVED_IDIOM_PATH}:missing_boundary:{FORBIDDEN_MARKERS[0]}",
                f"{APPROVED_IDIOM_PATH}:missing_boundary:{FORBIDDEN_MARKERS[1]}",
            ],
        )
        checks_run += 1

        mutated = Path(tmpdir) / "missing_companion"
        seed(mutated)
        write_text(
            mutated,
            APPROVED_IDIOM_PATH,
            read_text(mutated, APPROVED_IDIOM_PATH).replace("`samples/zigux/trace_events_string_formatting_sample.zig`", ""),
        )
        expect_exact(
            "missing_companion",
            collect_failures(mutated),
            [
                f"{APPROVED_IDIOM_PATH}:missing_text:`samples/zigux/trace_events_string_formatting_sample.zig`",
                f"{APPROVED_IDIOM_PATH}:missing_boundary:{FORBIDDEN_MARKERS[0]}",
                f"{APPROVED_IDIOM_PATH}:missing_boundary:{FORBIDDEN_MARKERS[1]}",
            ],
        )
        checks_run += 1

        mutated = Path(tmpdir) / "missing_required_file"
        seed(mutated)
        (mutated / SAMPLE_ROOT_PATH).unlink()
        try:
            collect_failures(mutated)
        except SystemExit as exc:
            if "required file missing" not in str(exc):
                raise AssertionError(f"unexpected missing-file abort: {exc}") from exc
        else:
            raise AssertionError("missing required file did not abort")
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} checks, ran {checks_run}")

    print("PHASE5_STRING_FORMATTING_APPROVED_IDIOM_GAP_SELF_TEST=pass")
    print(f"PHASE5_STRING_FORMATTING_APPROVED_IDIOM_GAP_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 5 approved string-formatting idiom stays bounded to the trace-events companion and no-extra-sample reminder packet."
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

    print("PHASE5_STRING_FORMATTING_APPROVED_IDIOM_GAP=pass")
    print(f"PHASE5_STRING_FORMATTING_APPROVED_IDIOM_GAP_FILE_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
