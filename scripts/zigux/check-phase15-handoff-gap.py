#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")
SHARED_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
HANDOFF_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-gap-survey.md")

MISSING_HANDOFF_PATHS = (
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "zigux/tests/phase15_handoff_next_steps_manifest.json",
    "zigux/tests/phase15_handoff_next_steps.zig",
)

DOCS_README_HANDOFF_MARKER = "`Documentation/zigux/phase15-handoff-next-steps-survey.md`"
SHARED_GAP_OVERCLAIM_MARKER = "`Documentation/zigux/phase15-handoff-next-steps-survey.md`"

REQUIRED_NOTE_MARKERS = (
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-parity-scorecard.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase15-shared-summary-gap.md`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`zigux/tests/phase15_handoff_next_steps_manifest.json`",
    "`zigux/tests/phase15_handoff_next_steps.zig`",
)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"missing file: {path}") from exc


def collect_gap_failures(root: Path) -> list[str]:
    docs_readme = _read(root / DOCS_README_PATH)
    shared_gap_note = _read(root / SHARED_GAP_NOTE_PATH)
    handoff_gap_note = _read(root / HANDOFF_GAP_NOTE_PATH)

    failures: list[str] = []

    if DOCS_README_HANDOFF_MARKER not in docs_readme:
        failures.append(
            "docs-root Phase 15 handoff marker disappeared and the handoff-gap note needs refresh: "
            + DOCS_README_HANDOFF_MARKER
        )

    if SHARED_GAP_OVERCLAIM_MARKER not in shared_gap_note:
        failures.append(
            "shared-summary handoff overclaim disappeared and the handoff-gap note needs refresh: "
            + SHARED_GAP_OVERCLAIM_MARKER
        )

    for relative_path in MISSING_HANDOFF_PATHS:
        if (root / relative_path).exists():
            failures.append(
                "previously missing handoff path now exists and the handoff-gap note must be narrowed: "
                + relative_path
            )

    for marker in REQUIRED_NOTE_MARKERS:
        if marker not in handoff_gap_note:
            failures.append(f"handoff-gap note is missing required marker: {marker}")

    return failures


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_docs_readme() -> str:
    return """# Zigux Documentation

Phase 15 notes - `Documentation/zigux/phase15-handoff-next-steps-survey.md`
"""


def _sample_shared_gap_note() -> str:
    return """# Phase 15 Shared Summary Gap

What current master does carry
- `Documentation/zigux/phase15-handoff-next-steps-survey.md`
"""


def _sample_handoff_gap_note() -> str:
    return """# Phase 15 Handoff Gap Survey

`Documentation/zigux/phase15-freeze-map-governance.md`
`Documentation/zigux/phase15-parity-scorecard.md`
`Documentation/zigux/phase15-study-only-anchor-accounting.md`
`Documentation/zigux/phase15-shared-summary-gap.md`
`Documentation/zigux/README.md`
`Documentation/zigux/phase15-handoff-next-steps-survey.md`
`zigux/tests/phase15_handoff_next_steps_manifest.json`
`zigux/tests/phase15_handoff_next_steps.zig`
"""


def _seed_missing_layout(root: Path) -> None:
    _write(root / DOCS_README_PATH, _sample_docs_readme())
    _write(root / SHARED_GAP_NOTE_PATH, _sample_shared_gap_note())
    _write(root / HANDOFF_GAP_NOTE_PATH, _sample_handoff_gap_note())
    _write(root / "Documentation/zigux/phase15-freeze-map-governance.md", "freeze-map packet\n")
    _write(root / "Documentation/zigux/phase15-parity-scorecard.md", "scorecard packet\n")
    _write(root / "Documentation/zigux/phase15-study-only-anchor-accounting.md", "study-only packet\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _seed_missing_layout(root)
        if collect_gap_failures(root):
            raise AssertionError("baseline missing-layout fixture should pass")

        materialized_root = root / "materialized"
        _seed_missing_layout(materialized_root)
        _write(materialized_root / "zigux/tests/phase15_handoff_next_steps.zig", "test {}\n")
        failures = collect_gap_failures(materialized_root)
        if len(failures) != 1 or "zigux/tests/phase15_handoff_next_steps.zig" not in failures[0]:
            raise AssertionError(f"materialized-path failure missing expected marker: {failures}")

        docs_root = root / "docs"
        _seed_missing_layout(docs_root)
        _write(docs_root / DOCS_README_PATH, "# Zigux Documentation\n")
        failures = collect_gap_failures(docs_root)
        if len(failures) != 1 or DOCS_README_HANDOFF_MARKER not in failures[0]:
            raise AssertionError(f"docs-root failure missing expected marker: {failures}")

        shared_root = root / "shared"
        _seed_missing_layout(shared_root)
        _write(shared_root / SHARED_GAP_NOTE_PATH, "# Phase 15 Shared Summary Gap\n")
        failures = collect_gap_failures(shared_root)
        if len(failures) != 1 or SHARED_GAP_OVERCLAIM_MARKER not in failures[0]:
            raise AssertionError(f"shared-gap failure missing expected marker: {failures}")

    print("PHASE15_HANDOFF_GAP_SELF_TEST=pass")
    print("PHASE15_HANDOFF_GAP_SELF_TEST_CASES=4")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the Phase 15 handoff-gap note still matches current docs-root, "
            "shared-summary, and repo-reality drift."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing the Phase 15 docs packet",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic repo layouts",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    try:
        failures = collect_gap_failures(args.root)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("Phase 15 handoff-gap check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
