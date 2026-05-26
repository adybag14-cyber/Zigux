#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")
HANDOFF_NOTE_PATH = Path("Documentation/zigux/phase15-handoff-next-steps-survey.md")
SHARED_GAP_NOTE_PATH = Path("Documentation/zigux/phase15-shared-summary-gap.md")
LANE_SEQ_NOTE_PATH = Path("Documentation/zigux/phase15-governance-lane-sequencing.md")

DOCS_REQUIRED_MARKERS = (
    "Phase 15 notes",
    "`Documentation/zigux/freeze-map.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase15-freeze-map-governance.md`",
    "`Documentation/zigux/phase15-architecture-council-review-process.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_build.zig`",
)

HANDOFF_REQUIRED_MARKERS = (
    "`Documentation/zigux/README.md`, which remains the one broad docs-root reminder surface that still needs the dedicated Phase 15 packet carried directly in the docs root rather than only in neighboring handoff and shared-gap notes, so reread it with `scripts/zigux/check-phase15-docs-readme-alignment.py` before widening any other shared-summary follow-through",
    "keep the broad docs-root reminder surface `Documentation/zigux/README.md` as the next explicit same-lane follow-through target until that dedicated Phase 15 reminder lands there, while the blocked broader wrapper-route and shared-CI route gaps remain separate current-`master` route-level gaps",
)

SHARED_GAP_REQUIRED_MARKERS = (
    "## Current shared-summary watchpoints",
    "`Documentation/zigux/README.md`",
    "if docs-root, checklist, scripts-root, tests-root, the Architecture Council review-process owner note, the decision-record template, readiness note, handoff note, the checklist-specific study-only anchor summary boundary, or adjacent stay-in-C wording drifts, fix only the smallest truthful reminder surface instead of widening into freeze-map approval or deep-core implementation claims",
    "keep the docs-root reminder gap distinct from the still-missing broader wrapper-route and shared-CI route vocabulary so lane follow-through can land the docs-root packet without implying those broader route bodies already returned",
)

LANE_SEQ_REQUIRED_MARKERS = (
    "`Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` are shared reminder surfaces that may summarize the parked packet, but they do not own freeze-map status decisions themselves",
)

def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for rel in (DOCS_README_PATH, HANDOFF_NOTE_PATH, SHARED_GAP_NOTE_PATH, LANE_SEQ_NOTE_PATH):
        if not (root / rel).exists():
            failures.append(f"missing_file:{rel}")
    if failures:
        return failures
    docs_readme = _read(root / DOCS_README_PATH)
    handoff_note = _read(root / HANDOFF_NOTE_PATH)
    shared_gap_note = _read(root / SHARED_GAP_NOTE_PATH)
    lane_seq_note = _read(root / LANE_SEQ_NOTE_PATH)
    for marker in DOCS_REQUIRED_MARKERS:
        if marker not in docs_readme:
            failures.append(f"docs_readme:missing:{marker}")
    for marker in HANDOFF_REQUIRED_MARKERS:
        if marker not in handoff_note:
            failures.append(f"handoff:missing:{marker}")
    for marker in SHARED_GAP_REQUIRED_MARKERS:
        if marker not in shared_gap_note:
            failures.append(f"shared_gap:missing:{marker}")
    for marker in LANE_SEQ_REQUIRED_MARKERS:
        if marker not in lane_seq_note:
            failures.append(f"lane_seq:missing:{marker}")
    return failures

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path.cwd())
    args = parser.parse_args()
    failures = collect_failures(args.root)
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1
    print('Phase 15 docs README alignment check passed.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
