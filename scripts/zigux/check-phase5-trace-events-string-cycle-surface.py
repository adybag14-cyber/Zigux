#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

SURVEY_PATH = Path("Documentation/zigux/phase5-trace-events-sample-survey.md")
MANIFEST_PATH = Path("zigux/tests/phase5_trace_events_sample_manifest.json")
FOCUSED_TEST_PATH = Path("zigux/tests/phase5_trace_events_sample.zig")
SAMPLE_PATH = Path("samples/zigux/trace_events_sample.zig")

STRING_CYCLE = (
    "Mother Goose",
    "Snoopy",
    "Gandalf",
    "Frodo",
    "One ring to rule them all",
)

SURVEY_REQUIRED_TEXT = (
    "`runStringFormattingCycleReplay()` still keeps the full modulo-selected string cycle explicit across counts `0` through `4`",
    "`iter=%d`",
    "selected-string plus `iter=%d` replay",
)

MANIFEST_REQUIRED_TEXT = (
    "`runStringFormattingCycleReplay()` summary still keep the array payload, the full modulo-selected string cycle, selected-string slot cues, and iter-format messages reviewable",
)

FOCUSED_TEST_REQUIRED_TEXT = (
    'test "phase 5 trace-events sample keeps the full string and formatting cycle explicit"',
    "runStringFormattingCycleReplay()",
    "review_contract.modulo_selected_strings.len",
    '"iter={d}"',
)

SAMPLE_REQUIRED_TEXT = (
    "pub fn runStringFormattingCycleReplay(self: *Self) !StringFormattingCycleSummary",
    ".modulo_selected_strings = &random_strings",
)


def _read(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"required file missing: {path}")
    return path.read_text(encoding="utf-8")


def _check_markers(text: str, prefix: str, markers: tuple[str, ...]) -> list[str]:
    failures: list[str] = []
    for marker in markers:
        if marker not in text:
            failures.append(f"{prefix}:missing_text:{marker}")
    return failures


def collect_failures(root: Path) -> list[str]:
    survey = _read(root / SURVEY_PATH)
    manifest = _read(root / MANIFEST_PATH)
    focused_test = _read(root / FOCUSED_TEST_PATH)
    sample = _read(root / SAMPLE_PATH)

    failures: list[str] = []
    failures.extend(_check_markers(survey, "survey", SURVEY_REQUIRED_TEXT))
    failures.extend(_check_markers(manifest, "manifest", MANIFEST_REQUIRED_TEXT))
    failures.extend(_check_markers(focused_test, "focused_test", FOCUSED_TEST_REQUIRED_TEXT))
    failures.extend(_check_markers(sample, "sample", SAMPLE_REQUIRED_TEXT))

    for count, selected in enumerate(STRING_CYCLE):
        if selected not in survey:
            failures.append(f"survey:missing_cycle_string:{selected}")
        count_marker = f"`{count}`"
        if count_marker not in survey:
            failures.append(f"survey:missing_cycle_count:{count_marker}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_survey() -> str:
    cycle_entries = ", ".join(
        f"`{count}`: `{value}`" for count, value in enumerate(STRING_CYCLE)
    )
    return f"""# Phase 5 Trace-Events Sample Survey
Aligned reminder surfaces keep the selected-string plus `iter=%d` replay explicit.
`runStringFormattingCycleReplay()` still keeps the full modulo-selected string cycle explicit across counts `0` through `4`: {cycle_entries}
"""


def _sample_manifest() -> str:
    return """{
  \"review_prompts\": [
    \"the in-memory replay and dedicated `runStringFormattingCycleReplay()` summary still keep the array payload, the full modulo-selected string cycle, selected-string slot cues, and iter-format messages reviewable instead of hiding them behind runtime thread state\"
  ]
}
"""


def _sample_focused_test() -> str:
    return """const std = @import(\"std\");

test \"phase 5 trace-events sample keeps the full string and formatting cycle explicit\" {
    const review_contract = sample.TraceEventsReferenceSample.reviewContract();
    _ = review_contract.modulo_selected_strings.len;
    try std.testing.expectEqualStrings(
        try std.fmt.bufPrint(&message_buffer, \"iter={d}\", .{count}),
        case.formatted_message[0..case.formatted_message_len],
    );
    _ = try module.runStringFormattingCycleReplay();
}
"""


def _sample_module() -> str:
    return """pub const ReviewContract = struct {
    modulo_selected_strings: []const []const u8,
};

const random_strings = [_][]const u8{
    \"Mother Goose\",
    \"Snoopy\",
    \"Gandalf\",
    \"Frodo\",
    \"One ring to rule them all\",
};

pub fn reviewContract() ReviewContract {
    return .{
        .modulo_selected_strings = &random_strings,
    };
}

pub fn runStringFormattingCycleReplay(self: *Self) !StringFormattingCycleSummary {
    _ = self;
}
"""


def _seed(root: Path) -> None:
    _write(root / SURVEY_PATH, _sample_survey())
    _write(root / MANIFEST_PATH, _sample_manifest())
    _write(root / FOCUSED_TEST_PATH, _sample_focused_test())
    _write(root / SAMPLE_PATH, _sample_module())


def run_self_test() -> int:
    checks_run = 0
    expected_checks = 5
    with tempfile.TemporaryDirectory(prefix="phase5_trace_events_string_cycle_surface_") as tmpdir:
        root = Path(tmpdir)

        ok_root = root / "ok"
        _seed(ok_root)
        failures = collect_failures(ok_root)
        if failures:
            raise AssertionError(f"unexpected seeded failures: {failures}")
        checks_run += 1

        missing_string_root = root / "missing_string"
        _seed(missing_string_root)
        _write(
            missing_string_root / SURVEY_PATH,
            _sample_survey().replace("`Gandalf`, ", "", 1),
        )
        failures = collect_failures(missing_string_root)
        expected = ["survey:missing_cycle_string:Gandalf"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-string failure: {failures}")
        checks_run += 1

        missing_manifest_root = root / "missing_manifest_marker"
        _seed(missing_manifest_root)
        _write(
            missing_manifest_root / MANIFEST_PATH,
            _sample_manifest().replace("iter-format messages", "format messages", 1),
        )
        failures = collect_failures(missing_manifest_root)
        expected = [f"manifest:missing_text:{MANIFEST_REQUIRED_TEXT[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected manifest-marker failure: {failures}")
        checks_run += 1

        missing_test_root = root / "missing_test_marker"
        _seed(missing_test_root)
        _write(
            missing_test_root / FOCUSED_TEST_PATH,
            _sample_focused_test().replace('"iter={d}"', '"iter=%d"', 1),
        )
        failures = collect_failures(missing_test_root)
        expected = ['focused_test:missing_text:"iter={d}"']
        if failures != expected:
            raise AssertionError(f"unexpected focused-test failure: {failures}")
        checks_run += 1

        missing_file_root = root / "missing_file"
        _seed(missing_file_root)
        (missing_file_root / SAMPLE_PATH).unlink()
        try:
            collect_failures(missing_file_root)
        except SystemExit as exc:
            if "required file missing" not in str(exc):
                raise AssertionError(f"unexpected missing-file abort: {exc}") from exc
        else:
            raise AssertionError("missing sample file did not abort")
        checks_run += 1

    if checks_run != expected_checks:
        raise AssertionError(f"expected {expected_checks} checks, ran {checks_run}")
    print("PHASE5_TRACE_EVENTS_STRING_CYCLE_SURFACE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE5_TRACE_EVENTS_STRING_CYCLE_SURFACE=pass")
    print(f"PHASE5_TRACE_EVENTS_STRING_CYCLE_SURVEY_MARKER_COUNT={len(SURVEY_REQUIRED_TEXT)}")
    print(f"PHASE5_TRACE_EVENTS_STRING_CYCLE_STRING_COUNT={len(STRING_CYCLE)}")
    print(f"PHASE5_TRACE_EVENTS_STRING_CYCLE_MANIFEST_MARKER_COUNT={len(MANIFEST_REQUIRED_TEXT)}")
    print(f"PHASE5_TRACE_EVENTS_STRING_CYCLE_FOCUSED_TEST_MARKER_COUNT={len(FOCUSED_TEST_REQUIRED_TEXT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
