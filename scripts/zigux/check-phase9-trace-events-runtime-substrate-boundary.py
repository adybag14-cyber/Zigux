#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile

SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
SURVEY_PATH = "Documentation/zigux/phase9-runtime-trace-events-survey.md"
MODULE_SLICE_PATH = "Documentation/zigux/phase9-runtime-trace-events-module-slice.md"

REQUIRED_FILES = (
    SEQUENCING_PATH,
    SURVEY_PATH,
    MODULE_SLICE_PATH,
)

BOUNDARY_MARKER = (
    "runtime task ownership, polling and event-loop substrate, and polling-backed wake or dispatch behavior"
)

FILE_MARKERS: dict[str, tuple[str, ...]] = {
    SEQUENCING_PATH: (
        "`scripts/zigux/check-phase9-trace-events-runtime-substrate-boundary.py`",
        "blocked runtime task ownership, polling and event-loop substrate, and polling-backed wake or dispatch behavior",
        "the new dedicated `scripts/zigux/check-phase9-trace-events-runtime-substrate-boundary.py` guard now keeps the scheduler-adjacent blocked boundary explicit",
    ),
    SURVEY_PATH: (
        "The remaining blocker is the broader Phase 9 runtime substrate:",
        BOUNDARY_MARKER,
        "Keep the blocked runtime task ownership, polling and event-loop substrate, and polling-backed wake or dispatch behavior explicit",
    ),
    MODULE_SLICE_PATH: (
        "The broader runtime substrate is still blocked as well:",
        BOUNDARY_MARKER,
        "Do not treat blocked runtime task ownership, polling and event-loop substrate, or polling-backed wake or dispatch behavior as solved",
    ),
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
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


def build_fixture(root: Path) -> None:
    for rel_path, markers in FILE_MARKERS.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(["# fixture", *markers, ""]) , encoding="utf-8")


def run_self_test() -> int:
    temp_root = Path(tempfile.mkdtemp(prefix="phase9-runtime-substrate-boundary-"))
    try:
        build_fixture(temp_root)
        failures = validate(temp_root)
        if failures:
            for failure in failures:
                print(failure)
            return 1

        broken_path = temp_root / SURVEY_PATH
        broken_path.write_text("# fixture\nmissing boundary\n", encoding="utf-8")
        failures = validate(temp_root)
        expected = f"missing_marker:{SURVEY_PATH}:{BOUNDARY_MARKER}"
        if expected not in failures:
            print(f"expected failure not found: {expected}")
            for failure in failures:
                print(failure)
            return 1

        print("PHASE9_TRACE_EVENTS_RUNTIME_SUBSTRATE_BOUNDARY_SELF_TEST=pass")
        print(f"PHASE9_TRACE_EVENTS_RUNTIME_SUBSTRATE_BOUNDARY_MARKER_COUNT={sum(len(markers) for markers in FILE_MARKERS.values())}")
        return 0
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
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

    print("PHASE9_TRACE_EVENTS_RUNTIME_SUBSTRATE_BOUNDARY=pass")
    print(f"PHASE9_TRACE_EVENTS_RUNTIME_SUBSTRATE_BOUNDARY_MARKER_COUNT={sum(len(markers) for markers in FILE_MARKERS.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
