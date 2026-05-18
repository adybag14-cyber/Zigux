#!/usr/bin/env python3
"""Validate the top-level Zigux release-sequencing note stays structured."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


REQUIRED_SNIPPETS = [
    "# Zigux Release Sequencing",
    "`RELEASE_PLAN_STATE=active`",
    "`RELEASE_FOUNDATION_PHASES=phase1,phase2`",
    "`RELEASE_ACTIVE_GATING_PHASES=phase3,phase4`",
    "`RELEASE_CONDITIONAL_RELEASE_PHASES=phase5`",
    "`RELEASE_SUPPORTING_PHASES=phase6,phase8,phase13`",
    "`RELEASE_RISK_PHASE3_SHARED_REMINDER=active`",
    "`RELEASE_RISK_PHASE4_MISSING_COMPANIONS=active`",
    "`RELEASE_RISK_PHASE13_VALIDATE_ROUTE=active`",
    "`RELEASE_NEXT_PMO_STEP=",
]


def validate(doc_path: Path) -> list[str]:
    text = doc_path.read_text(encoding="utf-8")
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]
    errors = []
    if missing:
        errors.append(
            "missing required sequencing markers: " + ", ".join(missing)
        )

    required_sections = [
        "## Status",
        "## Sequencing Baseline",
        "## Current Tranche Map",
        "## Release Order For Current Master",
        "## Open Coordination Risks",
        "## Review Use",
        "## Boundaries",
        "## Next PMO Step",
    ]
    absent_sections = [section for section in required_sections if section not in text]
    if absent_sections:
        errors.append(
            "missing required sections: " + ", ".join(absent_sections)
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--doc",
        default="Documentation/zigux/release-sequencing.md",
        help="Path to the release sequencing markdown note",
    )
    args = parser.parse_args()

    doc_path = Path(args.doc)
    if not doc_path.is_file():
        print(f"release sequencing document not found: {doc_path}", file=sys.stderr)
        return 1

    errors = validate(doc_path)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"release sequencing note OK: {doc_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
