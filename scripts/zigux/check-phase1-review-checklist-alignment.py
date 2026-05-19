#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
PHASE1_PROMPT = "if the change touches the shared Phase 1 host-tools closure packet"
REQUIRED_MARKERS = (
    "`Documentation/zigux/phase1-closure.md`",
    "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/validate-phase1-closure.py`",
    "`scripts/zigux/check-phase1-string-review-packet.py`",
    "`scripts/zigux/check-phase1-direct-owner-markers.py`",
    "`scripts/zigux/check-phase1-bench.py`",
    "`zigux/tests/README.md`",
    "`zigux/tests/fixtures/phase1_helper_manifest.json`",
    "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
    "current closed-helper reminder packet",
    "historical packet members until current `master` materializes them again?",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _line_containing(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line
    return None


def collect_failures(root: Path) -> list[str]:
    checklist = _read(root / REVIEW_CHECKLIST_PATH)
    failures: list[str] = []

    phase1_line = _line_containing(checklist, PHASE1_PROMPT)
    if phase1_line is None:
        failures.append(f"phase1_prompt:missing:{PHASE1_PROMPT}")
        return failures

    for marker in REQUIRED_MARKERS:
        if marker not in phase1_line:
            failures.append(f"phase1_marker:missing:{marker}")

    return failures


def _sample_review_checklist() -> str:
    return """# Zigux Review Checklist

## Validation
  * if the change touches the shared Phase 1 host-tools closure packet, do `Documentation/zigux/phase1-closure.md`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, `scripts/zigux/check-phase1-bench.py`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase1_helper_manifest.json`, and `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig` still agree on the current closed-helper reminder packet, while the older validator-first, parity, bench-route, and replay names stay framed as historical packet members until current `master` materializes them again?
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_review_checklist_") as tmpdir:
        root = Path(tmpdir)
        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist())

        failures = collect_failures(root)
        if failures:
            raise AssertionError(f"baseline review checklist fixture should pass: {failures}")
        case_count += 1

        _write(root / REVIEW_CHECKLIST_PATH, _sample_review_checklist().replace(PHASE1_PROMPT, "", 1))
        failures = collect_failures(root)
        expected = [f"phase1_prompt:missing:{PHASE1_PROMPT}"]
        if failures != expected:
            raise AssertionError(f"unexpected prompt failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace("`scripts/zigux/check-phase1-direct-owner-markers.py`", "", 1),
        )
        failures = collect_failures(root)
        expected = ["phase1_marker:missing:`scripts/zigux/check-phase1-direct-owner-markers.py`"]
        if failures != expected:
            raise AssertionError(f"unexpected direct-owner marker failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`", "", 1
            ),
        )
        failures = collect_failures(root)
        expected = ["phase1_marker:missing:`zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`"]
        if failures != expected:
            raise AssertionError(f"unexpected smoke-route marker failure: {failures}")
        case_count += 1

        _write(
            root / REVIEW_CHECKLIST_PATH,
            _sample_review_checklist().replace(
                "historical packet members until current `master` materializes them again?",
                "",
                1,
            ),
        )
        failures = collect_failures(root)
        expected = [
            "phase1_marker:missing:historical packet members until current `master` materializes them again?"
        ]
        if failures != expected:
            raise AssertionError(f"unexpected historical-marker failure: {failures}")
        case_count += 1

    print("PHASE1_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_REVIEW_CHECKLIST_ALIGNMENT_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the Phase 1 review-checklist reminder stays aligned with the current closure packet."
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 1 review-checklist alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
