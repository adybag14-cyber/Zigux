#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")

REQUIRED_MARKERS = (
    "Phase 15 notes",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/check-phase15-scripts-readme-alignment.py`",
    "`scripts/zigux/check-phase15-shared-summary-gap.py`",
    "`scripts/zigux/check-phase15-review-process-handoff.py`",
    "`scripts/zigux/validate-phase15.py`",
    "`zigux/tests/phase15_readiness_gate_manifest.json`",
    "`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`",
    "without implying any Architecture Council approval for a freeze-map status change",
    "the shared Phase 15 docs-root handoff should also keep",
    "the named reopen trigger",
    "deep-core blocker-posture change",
)


def collect_missing_markers(root: Path) -> list[str]:
    source = (root / DOCS_README_PATH).read_text(encoding="utf-8")
    missing: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in source:
            missing.append(f"docs_readme:{marker}")
    return missing


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_docs_readme() -> str:
    return """Scope
Phase 15 notes
`Documentation/zigux/phase15-readiness-gate-survey.md`
`Documentation/zigux/phase15-handoff-next-steps-survey.md`
`Documentation/zigux/phase15-governance-lane-sequencing.md`
`scripts/zigux/check-phase15-docs-readme-alignment.py`
`scripts/zigux/check-phase15-scripts-readme-alignment.py`
`scripts/zigux/check-phase15-shared-summary-gap.py`
`scripts/zigux/check-phase15-review-process-handoff.py`
`scripts/zigux/validate-phase15.py`
`zigux/tests/phase15_readiness_gate_manifest.json`
`zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig`
without implying any Architecture Council approval for a freeze-map status change
the shared Phase 15 docs-root handoff should also keep
the named reopen trigger
deep-core blocker-posture change
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_docs_readme_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / DOCS_README_PATH, _sample_docs_readme())

        if collect_missing_markers(root):
            raise AssertionError("baseline docs README fixture should pass")
        case_count += 1

        _write(
            root / DOCS_README_PATH,
            _sample_docs_readme().replace("`scripts/zigux/check-phase15-docs-readme-alignment.py`\n", "", 1),
        )
        missing = collect_missing_markers(root)
        if missing != ["docs_readme:`scripts/zigux/check-phase15-docs-readme-alignment.py`"]:
            raise AssertionError(f"unexpected missing markers for docs checker case: {missing}")
        case_count += 1

        _write(
            root / DOCS_README_PATH,
            _sample_docs_readme().replace(
                "without implying any Architecture Council approval for a freeze-map status change\n",
                "",
                1,
            ),
        )
        missing = collect_missing_markers(root)
        expected = [
            "docs_readme:without implying any Architecture Council approval for a freeze-map status change"
        ]
        if missing != expected:
            raise AssertionError(f"unexpected missing markers for approval-posture case: {missing}")
        case_count += 1

        _write(
            root / DOCS_README_PATH,
            _sample_docs_readme().replace("deep-core blocker-posture change\n", "", 1),
        )
        missing = collect_missing_markers(root)
        if missing != ["docs_readme:deep-core blocker-posture change"]:
            raise AssertionError(f"unexpected missing markers for blocker-posture case: {missing}")
        case_count += 1

    print("PHASE15_DOCS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_DOCS_README_ALIGNMENT_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the docs-root Phase 15 summary still names the parked governance packet honestly."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing Documentation/zigux/README.md",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="exercise the checker against synthetic docs-root fixtures",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_missing_markers(args.root)
    if missing:
        for item in missing:
            print(f"ERROR: {item}")
        return 1

    print("Phase 15 docs README alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
