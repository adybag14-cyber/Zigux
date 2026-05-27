#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

LANE_NOTE_PATH = Path("Documentation/zigux/phase5-sample-lane-sequencing.md")
BUILD_PATH = Path("zigux/tests/phase5_build.zig")

LANE_NOTE_MARKERS = (
    "Keep `phase5-kobject-example-sample-selfcheck` explicit too as the named shared `zigux/tests/phase5_build.zig` step that reruns the sample-owned `zig test samples/zigux/kobject_example.zig` self-check, so contributor guidance does not leave that owner-side rerun handle buried in the build wiring alone.",
)

BUILD_MARKERS = (
    "\"phase5-kobject-example-sample-selfcheck\",",
    "\"Run the Phase 5 kobject example sample-owned self-checks\",",
    "phase5_kobject_example_sample_selfcheck_step.dependOn(",
)


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def placeholder_note() -> str:
    return "# Phase 5 Sample Lane Sequencing\n\n" + "\n\n".join(LANE_NOTE_MARKERS) + "\n"


def placeholder_build() -> str:
    return "const std = @import(\"std\");\n\npub fn build(b: *std.Build) void {\n" + "\n".join(
        f"    {marker}" for marker in BUILD_MARKERS
    ) + "\n}\n"


def seed(root: Path) -> None:
    write_text(root, LANE_NOTE_PATH, placeholder_note())
    write_text(root, BUILD_PATH, placeholder_build())


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    lane_note = read_text(root, LANE_NOTE_PATH)
    build = read_text(root, BUILD_PATH)

    for marker in LANE_NOTE_MARKERS:
        if marker not in lane_note:
            failures.append(f"{LANE_NOTE_PATH}:missing_text:{marker}")
    for marker in BUILD_MARKERS:
        if marker not in build:
            failures.append(f"{BUILD_PATH}:missing_text:{marker}")
    return failures


def expect_exact(label: str, failures: list[str], expected: list[str]) -> None:
    if failures != expected:
        raise AssertionError(f"{label}: expected {expected}, got {failures}")


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 4
    with tempfile.TemporaryDirectory(prefix="phase5_kobject_selfcheck_packet_") as tmpdir:
        root = Path(tmpdir)
        seed(root)
        expect_exact("baseline", collect_failures(root), [])
        checks_run += 1

        mutated = root / "missing_lane_note_marker"
        seed(mutated)
        write_text(mutated, LANE_NOTE_PATH, "# Phase 5 Sample Lane Sequencing\n")
        expect_exact(
            "missing lane-note marker",
            collect_failures(mutated),
            [f"{LANE_NOTE_PATH}:missing_text:{LANE_NOTE_MARKERS[0]}"],
        )
        checks_run += 1

        mutated = root / "missing_build_step_name"
        seed(mutated)
        write_text(mutated, BUILD_PATH, placeholder_build().replace(BUILD_MARKERS[0], ""))
        expect_exact(
            "missing build step name",
            collect_failures(mutated),
            [f"{BUILD_PATH}:missing_text:{BUILD_MARKERS[0]}"],
        )
        checks_run += 1

        mutated = root / "missing_build_dependency"
        seed(mutated)
        write_text(mutated, BUILD_PATH, placeholder_build().replace(BUILD_MARKERS[2], ""))
        expect_exact(
            "missing build dependency",
            collect_failures(mutated),
            [f"{BUILD_PATH}:missing_text:{BUILD_MARKERS[2]}"],
        )
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} self-test cases, ran {checks_run}")

    print("PHASE5_KOBJECT_SAMPLE_SELFCHECK_PACKET_SELF_TEST=pass")
    print(f"PHASE5_KOBJECT_SAMPLE_SELFCHECK_PACKET_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT.parent, help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        print("PHASE5_KOBJECT_SAMPLE_SELFCHECK_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE5_KOBJECT_SAMPLE_SELFCHECK_PACKET=pass")
    print(f"PHASE5_KOBJECT_SAMPLE_SELFCHECK_PACKET_LANE_NOTE_MARKER_COUNT={len(LANE_NOTE_MARKERS)}")
    print(f"PHASE5_KOBJECT_SAMPLE_SELFCHECK_PACKET_BUILD_MARKER_COUNT={len(BUILD_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
