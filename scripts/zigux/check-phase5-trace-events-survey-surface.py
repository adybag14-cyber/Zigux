#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SURVEY_PATH = Path("Documentation/zigux/phase5-trace-events-sample-survey.md")
APPROVED_IDIOM_PATH = Path("Documentation/zigux/phase5-trace-events-approved-idiom-gap.md")
SAMPLE_ROOT_PATH = Path("samples/zigux/README.md")
FORMATTING_SAMPLE_PATH = Path("samples/zigux/trace_events_string_formatting_sample.zig")
SHARED_GUIDE_CHECKER_PATH = Path("scripts/zigux/check-phase5-review-guide-surface.py")
TESTS_README_PATH = Path("zigux/tests/README.md")
PHASE5_BUILD_PATH = Path("zigux/tests/phase5_build.zig")

PUBLIC_TREE_COMPANION_PATHS = (
    "Documentation/zigux/phase5-trace-events-sample-survey.md",
    "samples/zigux/trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample_manifest.json",
    "zigux/tests/phase5_trace_events_sample_survey.zig",
)

SURVEY_MARKERS = (
    "`PHASE5_STATUS=verified-public-fallback-companion-truthfulness`",
    "keep the broader non-runtime sample-local companions visible as public-tree-backed companion evidence while the contents route still misses them",
    "Fresh public current-`master` reread in this run also surfaced the broader sample-local companion paths again through their live GitHub blob pages:",
    "The shared `zigux/tests/phase5_build.zig` route should stay framed separately as shared companion evidence only until a fresh authenticated reread returns that path directly again.",
    "`scripts/zigux/check-phase5-review-guide-surface.py` still guards the direct-proof, public-tree-backed-companion, and no-extra-sample wording",
    "the approved formatting idiom remains the selected-string plus `iter=%d` cue described in `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`",
    "bounded destination behavior remains part of the approved idiom reminder: `formatIterationMessageInto(12, [5]u8)` stays a no-space boundary, while `formatIterationMessageInto(12, [7]u8)` stays the success-sized `iter=12` case",
)

APPROVED_IDIOM_MARKERS = (
    "Keep the approved formatting idiom bounded to the current landed reminder packet:",
    "Keep the sample-owned review contract explicit too: the bounded formatting companion now centralizes the exact `checked_focus` order `string_selection,formatted_message,bounded_destination_discipline,non_allocating_runtime_safe`",
)

SAMPLE_ROOT_MARKERS = (
    "Current `master` also keeps the bounded non-runtime trace-events packet visible through the direct formatting companion `samples/zigux/trace_events_string_formatting_sample.zig` together with the shared Phase 5 reminder packet.",
    "Keep that trace-events packet framed as the approved selected-string plus `iter=%d` formatting idiom for the Phase 5 anchor:",
)

TESTS_README_MARKERS = (
    "Keep `scripts/zigux/check-phase5-review-guide-surface.py` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording instead of treating the Phase 5 tests-root packet as docs-only guidance.",
    "Keep `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig` explicit as the direct non-runtime kretprobe tests-root packet, and keep `samples/zigux/trace_events_string_formatting_sample.zig` framed only as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.",
)

ALL_TEXT_CHECKS = (
    (SURVEY_PATH, SURVEY_MARKERS),
    (APPROVED_IDIOM_PATH, APPROVED_IDIOM_MARKERS),
    (SAMPLE_ROOT_PATH, SAMPLE_ROOT_MARKERS),
    (TESTS_README_PATH, TESTS_README_MARKERS),
)

REQUIRED_PATHS = (
    str(FORMATTING_SAMPLE_PATH),
    str(SHARED_GUIDE_CHECKER_PATH),
    str(PHASE5_BUILD_PATH),
    *PUBLIC_TREE_COMPANION_PATHS,
)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _placeholder_text(path: Path, markers: tuple[str, ...]) -> str:
    header = f"# {path.name}"
    extra_lines: list[str] = []
    if path == SURVEY_PATH:
        extra_lines.extend(f"`{rel}`" for rel in REQUIRED_PATHS)
    body = "\n\n".join((header, *markers, *extra_lines))
    return body + "\n"


def collect_failures(root: Path) -> list[str]:
    texts = {path: _read(root / path) for path, _ in ALL_TEXT_CHECKS}
    failures: list[str] = []

    for path, markers in ALL_TEXT_CHECKS:
        text = texts[path]
        for marker in markers:
            if marker not in text:
                failures.append(f"{path}:missing_text:{marker}")

    survey = texts[SURVEY_PATH]
    for rel in REQUIRED_PATHS:
        if f"`{rel}`" not in survey and rel not in survey:
            failures.append(f"survey:missing_path:{rel}")
        if not (root / rel).exists():
            failures.append(f"repo:missing_path:{rel}")

    return failures


def _seed(root: Path) -> None:
    tracked_text_paths = {path for path, _ in ALL_TEXT_CHECKS}
    for path, markers in ALL_TEXT_CHECKS:
        _write(root / path, _placeholder_text(path, markers))
    for rel in REQUIRED_PATHS:
        if Path(rel) in tracked_text_paths:
            continue
        _write(root / rel, "present\n")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 6
    with tempfile.TemporaryDirectory(prefix="phase5_trace_events_survey_surface_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        checks_run += 1

        missing_public_fallback_marker_root = root / "missing_public_fallback_marker"
        _seed(missing_public_fallback_marker_root)
        _write(
            missing_public_fallback_marker_root / SURVEY_PATH,
            _placeholder_text(
                SURVEY_PATH,
                (
                    SURVEY_MARKERS[0],
                    SURVEY_MARKERS[1],
                    SURVEY_MARKERS[3],
                    SURVEY_MARKERS[4],
                    SURVEY_MARKERS[5],
                    SURVEY_MARKERS[6],
                ),
            ),
        )
        failures = collect_failures(missing_public_fallback_marker_root)
        expected = [f"{SURVEY_PATH}:missing_text:{SURVEY_MARKERS[2]}"]
        if failures != expected:
            raise AssertionError(f"unexpected public-fallback marker failure: {failures}")
        checks_run += 1

        missing_build_split_marker_root = root / "missing_build_split_marker"
        _seed(missing_build_split_marker_root)
        _write(
            missing_build_split_marker_root / SURVEY_PATH,
            _placeholder_text(
                SURVEY_PATH,
                (
                    SURVEY_MARKERS[0],
                    SURVEY_MARKERS[1],
                    SURVEY_MARKERS[2],
                    SURVEY_MARKERS[4],
                    SURVEY_MARKERS[5],
                    SURVEY_MARKERS[6],
                ),
            ),
        )
        failures = collect_failures(missing_build_split_marker_root)
        expected = [f"{SURVEY_PATH}:missing_text:{SURVEY_MARKERS[3]}"]
        if failures != expected:
            raise AssertionError(f"unexpected build-split marker failure: {failures}")
        checks_run += 1

        missing_formatting_boundary_marker_root = root / "missing_formatting_boundary_marker"
        _seed(missing_formatting_boundary_marker_root)
        _write(
            missing_formatting_boundary_marker_root / SURVEY_PATH,
            _placeholder_text(
                SURVEY_PATH,
                (
                    SURVEY_MARKERS[0],
                    SURVEY_MARKERS[1],
                    SURVEY_MARKERS[2],
                    SURVEY_MARKERS[3],
                    SURVEY_MARKERS[4],
                    SURVEY_MARKERS[5],
                ),
            ),
        )
        failures = collect_failures(missing_formatting_boundary_marker_root)
        expected = [f"{SURVEY_PATH}:missing_text:{SURVEY_MARKERS[6]}"]
        if failures != expected:
            raise AssertionError(f"unexpected formatting-boundary failure: {failures}")
        checks_run += 1

        missing_public_companion_path_root = root / "missing_public_companion_path"
        _seed(missing_public_companion_path_root)
        _write(
            missing_public_companion_path_root / SURVEY_PATH,
            _placeholder_text(SURVEY_PATH, SURVEY_MARKERS).replace(
                "`zigux/tests/phase5_trace_events_sample_manifest.json`\n\n",
                "",
            ),
        )
        failures = collect_failures(missing_public_companion_path_root)
        expected = ["survey:missing_path:zigux/tests/phase5_trace_events_sample_manifest.json"]
        if failures != expected:
            raise AssertionError(f"unexpected public-companion path failure: {failures}")
        checks_run += 1

        missing_survey_file_root = root / "missing_survey_file"
        _seed(missing_survey_file_root)
        (missing_survey_file_root / SURVEY_PATH).unlink()
        try:
            collect_failures(missing_survey_file_root)
        except SystemExit as exc:
            if "required file missing" not in str(exc):
                raise AssertionError(f"unexpected missing-file abort: {exc}") from exc
        else:
            raise AssertionError("missing survey file did not abort")
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} checks, ran {checks_run}")
    print("PHASE5_TRACE_EVENTS_SURVEY_SURFACE_SELF_TEST=pass")
    print(f"PHASE5_TRACE_EVENTS_SURVEY_SURFACE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 5 trace-events survey note keeps the current formatting-companion and public-tree-backed companion wording aligned."
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
    print("PHASE5_TRACE_EVENTS_SURVEY_SURFACE=pass")
    print(f"PHASE5_TRACE_EVENTS_SURVEY_SURFACE_PUBLIC_TREE_COMPANION_COUNT={len(PUBLIC_TREE_COMPANION_PATHS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
