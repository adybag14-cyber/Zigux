#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
MODULE_SLICE_PATH = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"
SURVEY_NOTE_PATH = "Documentation/zigux/phase9-runtime-trace-events-survey.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
EXIT_ROLLBACK_GUARD_PATH = "samples/zigux/runtime_trace_events_exit_rollback_guard.zig"

MODULE_SLICE_EXIT_SUMMARY_MARKER = (
    "The exit-rollback companion keeps failed-exit rollback explicit after reusable selftest replay by proving "
    "`error.OutstandingRegistration` leaves the selftest_complete summary unchanged until the function thread "
    "unregisters and clean exit succeeds."
)
SURVEY_NOTE_EXIT_SUMMARY_MARKER = (
    "`error.OutstandingRegistration` guard plus the later post-exit invalid-lifecycle rejections that leave the "
    "summary unchanged."
)
SAMPLES_README_EXIT_SUMMARY_MARKER = (
    "`error.OutstandingRegistration` leaves the selftest_complete summary unchanged until the function thread "
    "unregisters"
)
EXIT_ROLLBACK_GUARD_MARKERS = [
    'test "phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay" {',
    "try std.testing.expectError(error.OutstandingRegistration, module.exit());",
    "try expectSummaryStable(before_failed_exit, after_failed_exit);",
    "try std.testing.expectEqual(@as(usize, 20), before_unregister.total_events);",
    "try std.testing.expectEqual(@as(usize, 2), before_exit.unregister_transitions);",
    "try std.testing.expectEqual(ModuleStage.exited, after_exit.stage);",
    "try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);",
    "try expectSummaryStable(exited_before_rejected_ops, exited_after_rejected_ops);",
]

FILE_MARKERS = {
    MODULE_SLICE_PATH: [MODULE_SLICE_EXIT_SUMMARY_MARKER],
    SURVEY_NOTE_PATH: [SURVEY_NOTE_EXIT_SUMMARY_MARKER],
    SAMPLES_README_PATH: [SAMPLES_README_EXIT_SUMMARY_MARKER],
    EXIT_ROLLBACK_GUARD_PATH: EXIT_ROLLBACK_GUARD_MARKERS,
}


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / MODULE_SLICE_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture_text(rel_path: str, markers: list[str]) -> str:
    if rel_path.endswith(".md"):
        return "\n".join(["# fixture", "", *markers, ""])
    return "\n".join(markers) + "\n"


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path, markers in FILE_MARKERS.items():
        path = root / rel_path
        if not path.exists():
            failures.append(f"missing_file:{rel_path}")
            continue
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def seed_fixture_tree(base: Path) -> None:
    for rel_path, markers in FILE_MARKERS.items():
        write_text(base / rel_path, build_fixture_text(rel_path, markers))


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-exit-summary-proof-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in FILE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                current = read_text(base, rel_path)
                write_text(base / rel_path, current.replace(marker, "", 1))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in FILE_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        print("PHASE9_TRACE_EVENTS_EXIT_SUMMARY_PROOF_SELF_TEST=pass")
        print(f"PHASE9_TRACE_EVENTS_EXIT_SUMMARY_PROOF_FILE_COUNT={len(FILE_MARKERS)}")
        print(f"PHASE9_TRACE_EVENTS_EXIT_SUMMARY_PROOF_GUARD_MARKER_COUNT={len(EXIT_ROLLBACK_GUARD_MARKERS)}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE9_TRACE_EVENTS_EXIT_SUMMARY_PROOF=pass")
    print(f"PHASE9_TRACE_EVENTS_EXIT_SUMMARY_PROOF_FILE_COUNT={len(FILE_MARKERS)}")
    print(f"PHASE9_TRACE_EVENTS_EXIT_SUMMARY_PROOF_GUARD_MARKER_COUNT={len(EXIT_ROLLBACK_GUARD_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
