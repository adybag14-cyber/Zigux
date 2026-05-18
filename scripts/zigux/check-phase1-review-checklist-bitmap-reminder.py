#!/usr/bin/env python3
"""Guard the Phase 1 bitmap reminder line in the shared review checklist."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
REVIEW_CHECKLIST_REL = Path("Documentation/zigux/review-checklist.md")

EXPECTED_BITMAP_REMINDER_LINE = (
    "  * if the change touches the shared Phase 5 sample packet, do the docs "
    "still say clearly that there is no standalone "
    "`samples/zigux/*bitmap*` reference sample and that direct bitmap helper "
    "reviewability remains under `tools/lib/bitmap.zig`, "
    "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and "
    "`Documentation/zigux/phase4-reversible-delivery-evidence.md`, while "
    "runtime bitmap work stays in the separate Phase 9 lane through "
    "`Documentation/zigux/phase9-runtime-bitmap-survey.md`, "
    "`samples/zigux/runtime_bitmap.zig`, "
    "`samples/zigux/runtime_bitmap_loader.zig`, "
    "`samples/zigux/runtime_bitmap_top_bit_contract.zig`, and "
    "`zigux/tests/phase9_build.zig` rather than the four shipped Phase 5 "
    "samples?"
)

FORBIDDEN_SNIPPETS = (
    "`Documentation/zigux/phase1-closure.md`",
    "`Documentation/zigux/phase4-validation-matrix.md`",
    "`samples/zigux/README.md`, `Documentation/zigux/phase9-runtime-bitmap-survey.md`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def collect_failures(root: Path) -> list[str]:
    target = root / REVIEW_CHECKLIST_REL
    if not target.exists():
        return [f"missing_file:{REVIEW_CHECKLIST_REL.as_posix()}"]

    text = target.read_text(encoding="utf-8")
    failures: list[str] = []

    count = sum(
        1
        for line in text.splitlines()
        if line.strip() == EXPECTED_BITMAP_REMINDER_LINE.strip()
    )
    if count != 1:
        failures.append(f"expected_bitmap_reminder_line_once:actual={count}")

    for snippet in FORBIDDEN_SNIPPETS:
        if snippet in text:
            failures.append(f"forbidden_snippet_present:{snippet}")

    return failures


def write_sample(root: Path, line: str) -> None:
    target = root / REVIEW_CHECKLIST_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# sample\n\n" + line + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = (
        ("success", EXPECTED_BITMAP_REMINDER_LINE, None),
        (
            "old_phase1_closure_reference",
            EXPECTED_BITMAP_REMINDER_LINE.replace(
                "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`",
                "`Documentation/zigux/phase1-closure.md`",
            ),
            "forbidden_snippet_present:`Documentation/zigux/phase1-closure.md`",
        ),
        (
            "old_phase4_matrix_reference",
            EXPECTED_BITMAP_REMINDER_LINE.replace(
                "`Documentation/zigux/phase4-reversible-delivery-evidence.md`",
                "`Documentation/zigux/phase4-validation-matrix.md`",
            ),
            "forbidden_snippet_present:`Documentation/zigux/phase4-validation-matrix.md`",
        ),
    )

    with tempfile.TemporaryDirectory(prefix="phase1-bitmap-reminder-") as tmpdir:
        root = Path(tmpdir)
        for label, line, expected_failure in cases:
            write_sample(root, line)
            failures = collect_failures(root)
            if expected_failure is None:
                if failures:
                    print("PHASE1_REVIEW_CHECKLIST_BITMAP_REMINDER_SELF_TEST=fail")
                    print(f"CASE={label}")
                    for failure in failures:
                        print(f"FAILURE={failure}")
                    return 1
            else:
                if expected_failure not in failures:
                    print("PHASE1_REVIEW_CHECKLIST_BITMAP_REMINDER_SELF_TEST=fail")
                    print(f"CASE={label}")
                    print(f"EXPECTED_FAILURE={expected_failure}")
                    print(f"ACTUAL_FAILURES={failures}")
                    return 1

    print("PHASE1_REVIEW_CHECKLIST_BITMAP_REMINDER_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=None,
        help="repository root containing Documentation/zigux/review-checklist.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in self-test cases",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.repo_root))
    if failures:
        print("PHASE1_REVIEW_CHECKLIST_BITMAP_REMINDER_CHECK=fail")
        for failure in failures:
            print(f"FAILURE={failure}")
        return 1

    print("PHASE1_REVIEW_CHECKLIST_BITMAP_REMINDER_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
