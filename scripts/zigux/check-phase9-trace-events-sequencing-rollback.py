#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
EXIT_ROLLBACK_GUARD_SAMPLE_PATH = (
    "samples/zigux/runtime_trace_events_exit_rollback_guard.zig"
)


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / SEQUENCING_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

SEQUENCING_REQUIRED_MARKERS = [
    "surviving exit-rollback runtime companion: `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
    "the failed-exit rollback replay in `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
    "keep `samples/zigux/runtime_trace_events_exit_rollback_guard.zig` explicit as the same packet's failed-exit rollback and post-exit invalid-lifecycle companion",
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
]

SAMPLE_REQUIRED_MARKERS = [
    'test "phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay" {',
    "error.OutstandingRegistration",
    "const before_failed_exit = module.summary();",
    "try std.testing.expectError(error.OutstandingRegistration, module.exit());",
    "try expectSummaryStable(before_failed_exit, after_failed_exit);",
    "try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());",
]

FILE_MARKERS = {
    SEQUENCING_PATH: SEQUENCING_REQUIRED_MARKERS,
    EXIT_ROLLBACK_GUARD_SAMPLE_PATH: SAMPLE_REQUIRED_MARKERS,
}


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
    for rel_path in FILE_MARKERS:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in FILE_MARKERS.items():
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
    base = Path(tempfile.mkdtemp(prefix="phase9-trace-events-sequencing-rollback-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, markers in FILE_MARKERS.items():
            for marker in markers:
                seed_fixture_tree(base)
                write_text(base / rel_path, "missing target marker fixture\n")
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in FILE_MARKERS:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        print("PHASE9_TRACE_EVENTS_SEQUENCING_ROLLBACK_SELF_TEST=pass")
        print(
            "PHASE9_TRACE_EVENTS_SEQUENCING_ROLLBACK_SEQUENCING_MARKER_COUNT="
            f"{len(FILE_MARKERS[SEQUENCING_PATH])}"
        )
        print(
            "PHASE9_TRACE_EVENTS_SEQUENCING_ROLLBACK_SAMPLE_MARKER_COUNT="
            f"{len(FILE_MARKERS[EXIT_ROLLBACK_GUARD_SAMPLE_PATH])}"
        )
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the Phase 9 runtime-pilot sequencing note keeps the "
            "surviving exit-rollback companion explicit and that the paired "
            "trace-events exit-rollback guard sample still carries the key "
            "rollback proof markers."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE9_TRACE_EVENTS_SEQUENCING_ROLLBACK=pass")
    print(
        "PHASE9_TRACE_EVENTS_SEQUENCING_ROLLBACK_SEQUENCING_MARKER_COUNT="
        f"{len(FILE_MARKERS[SEQUENCING_PATH])}"
    )
    print(
        "PHASE9_TRACE_EVENTS_SEQUENCING_ROLLBACK_SAMPLE_MARKER_COUNT="
        f"{len(FILE_MARKERS[EXIT_ROLLBACK_GUARD_SAMPLE_PATH])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
