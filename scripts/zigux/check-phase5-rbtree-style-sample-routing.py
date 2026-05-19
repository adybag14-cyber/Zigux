#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
NOTE_PATH = Path("Documentation/zigux/phase5-rbtree-style-sample-routing.md")

REQUIRED_PATH_MARKERS = (
    "samples/zigux/kobject_example.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "Documentation/zigux/phase5-sample-review-guide.md",
    "samples/zigux/README.md",
    "tools/lib/rbtree.zig",
)

REQUIRED_TEXT = (
    "`PHASE5_STATUS=routing-note`",
    "`PHASE5_LANE_KEY=P5-L20`",
    "Current `master` still ships no standalone `samples/zigux/*rbtree*` Phase 5 reference sample.",
    "`samples/zigux/kobject_example.zig` is the nearest live ownership-tree Phase 5 sample packet",
    "`tools/lib/rbtree.zig` remains helper-owned Phase 1 evidence rather than Phase 5 sample-root proof",
    "do not invent a fifth approved sample anchor under `samples/zigux/`",
)

FORBIDDEN_TEXT = (
    "landed Phase 5 rbtree sample",
    "fifth approved sample anchor has landed",
)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def collect_failures(root: Path) -> list[str]:
    note = _read(root / NOTE_PATH)
    failures: list[str] = []

    for marker in REQUIRED_TEXT:
        if marker not in note:
            failures.append(f"note:missing_text:{marker}")

    for marker in REQUIRED_PATH_MARKERS:
        if f"`{marker}`" not in note:
            failures.append(f"note:missing_path:`{marker}`")

    for text in FORBIDDEN_TEXT:
        if text in note:
            failures.append(f"note:forbidden_text:{text}")

    return failures


def _sample_note() -> str:
    return """# Phase 5 Rbtree-Style Sample Routing

This note keeps the mismatched Phase 5 `rbtree`-style sample wording honest against the current Zigux tree.

## Status

- `PHASE5_STATUS=routing-note`
- `PHASE5_LANE_KEY=P5-L20`
- scope: route the sample wording to the nearest live Phase 5 ownership-tree packet without inventing a fifth approved sample

## Current routing on `master`

The roadmap-backed Phase 5 sample anchors are still limited to:

- `samples/kfifo/bytestream-example.c`
- `samples/kobject/kobject-example.c`
- `samples/kprobes/kretprobe_example.c`
- `samples/trace_events/trace-events-sample.c`

Current `master` still ships no standalone `samples/zigux/*rbtree*` Phase 5 reference sample.

When the lane wording says `rbtree`-style sample work, route review through these bounded surfaces instead:

- `samples/zigux/kobject_example.zig` is the nearest live ownership-tree Phase 5 sample packet
- `zigux/tests/phase5_kobject_example.zig` is the directly coupled focused replay for that ownership-tree packet
- `Documentation/zigux/phase5-kobject-sample-survey.md` records the current kobject packet and its mixed direct-plus-public-tree-backed evidence
- `tools/lib/rbtree.zig` remains helper-owned Phase 1 evidence rather than Phase 5 sample-root proof
- `Documentation/zigux/phase5-sample-review-guide.md` and `samples/zigux/README.md` keep the no-extra-sample boundary explicit

## Boundary rules

Keep this lane narrow:

- do not describe `tools/lib/rbtree.zig` as a landed Phase 5 sample
- do not invent a fifth approved sample anchor under `samples/zigux/`
- do not widen this routing note into runtime-pilot, sysfs, procfs, or module-registration claims
- do not reopen helper semantics unless the helper-owned `tools/lib/rbtree.zig` packet itself changes

## Next bounded step

Leave this lane parked unless one of these moves together:

- `samples/zigux/kobject_example.zig`
- `zigux/tests/phase5_kobject_example.zig`
- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `samples/zigux/README.md`
- `tools/lib/rbtree.zig`

If one changes, reread the same ownership-tree and helper-boundary packet first and repair only the smallest same-lane routing drift.
"""


def _seed(root: Path) -> None:
    _write(root / NOTE_PATH, _sample_note())


def run_self_test() -> int:
    checks_run = 0
    expected_case_count = 4
    with tempfile.TemporaryDirectory(prefix="phase5_rbtree_style_sample_routing_") as tmpdir:
        root = Path(tmpdir)
        _seed(root)
        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline fixture should pass: {failures}")
        checks_run += 1

        missing_text_root = root / "missing_text"
        _seed(missing_text_root)
        _write(
            missing_text_root / NOTE_PATH,
            _sample_note().replace(REQUIRED_TEXT[4], "", 1),
        )
        failures = collect_failures(missing_text_root)
        expected = [f"note:missing_text:{REQUIRED_TEXT[4]}"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-text failure: {failures}")
        checks_run += 1

        missing_path_root = root / "missing_path"
        _seed(missing_path_root)
        _write(
            missing_path_root / NOTE_PATH,
            _sample_note().replace(f"`{REQUIRED_PATH_MARKERS[1]}`", "", 2),
        )
        failures = collect_failures(missing_path_root)
        expected = [f"note:missing_path:`{REQUIRED_PATH_MARKERS[1]}`"]
        if failures != expected:
            raise AssertionError(f"unexpected missing-path failure: {failures}")
        checks_run += 1

        forbidden_text_root = root / "forbidden_text"
        _seed(forbidden_text_root)
        _write(
            forbidden_text_root / NOTE_PATH,
            _sample_note() + "\nlanded Phase 5 rbtree sample\n",
        )
        failures = collect_failures(forbidden_text_root)
        expected = [f"note:forbidden_text:{FORBIDDEN_TEXT[0]}"]
        if failures != expected:
            raise AssertionError(f"unexpected forbidden-text failure: {failures}")
        checks_run += 1

    if checks_run != expected_case_count:
        raise AssertionError(f"expected {expected_case_count} checks, ran {checks_run}")
    print("PHASE5_RBTREE_STYLE_SAMPLE_ROUTING_SELF_TEST=pass")
    print(f"PHASE5_RBTREE_STYLE_SAMPLE_ROUTING_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the bounded Phase 5 rbtree-style routing note stays honest about sample-versus-helper ownership."
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
    print("PHASE5_RBTREE_STYLE_SAMPLE_ROUTING=pass")
    print(f"PHASE5_RBTREE_STYLE_SAMPLE_ROUTING_REQUIRED_TEXT_COUNT={len(REQUIRED_TEXT)}")
    print(f"PHASE5_RBTREE_STYLE_SAMPLE_ROUTING_REQUIRED_PATH_COUNT={len(REQUIRED_PATH_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
