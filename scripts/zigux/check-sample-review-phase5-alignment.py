#!/usr/bin/env python3
"""Fail-closed Phase 5 shared reviewer-surface alignment checker."""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path


REQUIRED_MARKERS = {
    "Documentation/zigux/README.md": [
        "Phase 5 notes - `Documentation/zigux/phase5-kfifo-sample-survey.md` now records the current sample-root-only bytestream packet",
        "`Documentation/zigux/phase5-kobject-sample-survey.md` now records the current directly readable kobject packet",
        "`Documentation/zigux/phase5-kretprobe-sample-survey.md` now records the current directly readable kretprobe packet",
        "`Documentation/zigux/phase5-trace-events-sample-survey.md` now records the directly readable `samples/zigux/trace_events_sample.zig` reference packet",
        "the docs-root Phase 5 summary should also keep the current shared-route split explicit",
    ],
    "Documentation/zigux/phase5-sample-review-guide.md": [
        "* `samples/kfifo/bytestream-example.c`",
        "* `samples/kobject/kobject-example.c`",
        "* `samples/kprobes/kretprobe_example.c`",
        "* `samples/trace_events/trace-events-sample.c`",
        "Keep later runtime-facing sample work in the separate Phase 9 lane",
    ],
    "Documentation/zigux/review-checklist.md": [
        "if the change touches the shared Phase 5 reviewer packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still describe the same four-anchor non-runtime packet",
        "if the change updates the landed Phase 5 `kobject_example` sample packet",
        "if the change updates the landed Phase 5 `trace-events` sample packet",
        "if the change touches the shared Phase 5 sample packet, do the docs still say clearly that there is no standalone `samples/zigux/*bitmap*` reference sample",
    ],
    "samples/zigux/README.md": [
        "* `samples/zigux/bytestream_fifo.zig`",
        "* `samples/zigux/kobject_example.zig`",
        "* `samples/zigux/kretprobe_example.zig`",
        "* `samples/zigux/trace_events_sample.zig`",
        "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample.",
    ],
    "scripts/zigux/README.md": [
        "Phase 5 flow - the current shared Phase 5 review surface on `master` is",
        "current `master` still ships no `validate-phase5.py`, no `check-phase5-*.py` checker packet, and no `phase5-validate` target",
        "Later `samples/zigux/runtime_atomic64*.zig`, `runtime_bitmap*.zig`, `runtime_kretprobe*.zig`, and `runtime_trace_events*.zig` families stay under the separate Phase 9 lane",
    ],
    "zigux/tests/README.md": [
        "* `Documentation/zigux/phase5-kfifo-sample-survey.md`",
        "* `Documentation/zigux/phase5-kobject-sample-survey.md`",
        "* `zigux/tests/phase5_kretprobe_example_survey.zig`",
        "* `zigux/tests/phase5_trace_events_sample_survey.zig`",
        "* current public-tree Phase 5 shared-build gap: `zigux/tests/phase5_build.zig`",
    ],
}


class AlignmentError(Exception):
    pass


def check_repo(repo_root: Path) -> None:
    missing: list[str] = []
    for rel_path, markers in REQUIRED_MARKERS.items():
        path = repo_root / rel_path
        if not path.is_file():
            missing.append(f"{rel_path}: file missing")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                missing.append(f"{rel_path}: missing marker -> {marker}")
    if missing:
        raise AlignmentError("\n".join(missing))


def make_fixture(root: Path) -> None:
    for rel_path, markers in REQUIRED_MARKERS.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(markers) + "\n", encoding="utf-8")


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase5-readme-alignment-"))
    try:
        make_fixture(tempdir)
        check_repo(tempdir)

        broken_root = tempdir / "broken"
        shutil.copytree(tempdir, broken_root)
        broken_path = broken_root / "scripts/zigux/README.md"
        broken_text = broken_path.read_text(encoding="utf-8").replace(
            "current `master` still ships no `validate-phase5.py`, no `check-phase5-*.py` checker packet, and no `phase5-validate` target",
            "phase5 drift",
            1,
        )
        broken_path.write_text(broken_text, encoding="utf-8")

        try:
            check_repo(broken_root)
        except AlignmentError as exc:
            if "scripts/zigux/README.md" not in str(exc):
                print("PHASE5_README_ALIGNMENT_SELF_TEST=fail", file=sys.stderr)
                print(exc, file=sys.stderr)
                return 1
        else:
            print("PHASE5_README_ALIGNMENT_SELF_TEST=fail", file=sys.stderr)
            print("expected missing-marker failure", file=sys.stderr)
            return 1
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)

    print("PHASE5_README_ALIGNMENT_SELF_TEST=pass")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the shared Phase 5 reminder surfaces still describe the "
            "same four-anchor non-runtime packet and shared-build gap posture."
        )
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root to inspect (default: current directory).",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the embedded fixture-based self-test.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    try:
        check_repo(Path(args.repo_root).resolve())
    except AlignmentError as exc:
        print("PHASE5_README_ALIGNMENT=fail", file=sys.stderr)
        print(exc, file=sys.stderr)
        return 1

    print("PHASE5_README_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
