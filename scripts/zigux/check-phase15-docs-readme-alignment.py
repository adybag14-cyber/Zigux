#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

DOCS_README_PATH = Path("Documentation/zigux/README.md")

REQUIRED_MARKERS = (
    "# Zigux Documentation",
    "Phase 14 notes",
    "`Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
    "`Documentation/zigux/phase14-shared-smoke-current-master-gap.md`",
)

FORBIDDEN_PHASE15_MARKERS = (
    "Phase 15 notes",
    "`Documentation/zigux/phase15-readiness-gate-survey.md`",
    "`Documentation/zigux/phase15-handoff-next-steps-survey.md`",
    "`Documentation/zigux/phase15-governance-lane-sequencing.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`scripts/zigux/check-phase15-docs-readme-alignment.py`",
    "`scripts/zigux/validate-phase15.py`",
)


def collect_alignment_errors(root: Path) -> list[str]:
    source = (root / DOCS_README_PATH).read_text(encoding="utf-8")
    errors: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in source:
            errors.append(f"docs_readme:missing:{marker}")
    for marker in FORBIDDEN_PHASE15_MARKERS:
        if marker in source:
            errors.append(f"docs_readme:unexpected:{marker}")
    return errors


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_docs_readme() -> str:
    return """# Zigux Documentation
Phase 14 notes
`Documentation/zigux/phase14-end-to-end-smoke-survey.md`
`Documentation/zigux/phase14-shared-smoke-current-master-gap.md`
"""


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_docs_readme_gap_") as tmp_dir:
        root = Path(tmp_dir)
        _write(root / DOCS_README_PATH, _sample_docs_readme())

        if collect_alignment_errors(root):
            raise AssertionError("baseline docs README fixture should pass")
        case_count += 1

        _write(root / DOCS_README_PATH, _sample_docs_readme().replace("Phase 14 notes\n", "", 1))
        errors = collect_alignment_errors(root)
        if errors != ["docs_readme:missing:Phase 14 notes"]:
            raise AssertionError(f"unexpected errors for missing phase-14 case: {errors}")
        case_count += 1

        _write(
            root / DOCS_README_PATH,
            _sample_docs_readme().replace(
                "`Documentation/zigux/phase14-shared-smoke-current-master-gap.md`\n",
                "",
                1,
            ),
        )
        errors = collect_alignment_errors(root)
        expected = [
            "docs_readme:missing:`Documentation/zigux/phase14-shared-smoke-current-master-gap.md`"
        ]
        if errors != expected:
            raise AssertionError(f"unexpected errors for missing phase-14 gap marker case: {errors}")
        case_count += 1

        _write(root / DOCS_README_PATH, _sample_docs_readme() + "Phase 15 notes\n")
        errors = collect_alignment_errors(root)
        if errors != ["docs_readme:unexpected:Phase 15 notes"]:
            raise AssertionError(f"unexpected errors for unexpected phase-15 header case: {errors}")
        case_count += 1

        _write(
            root / DOCS_README_PATH,
            _sample_docs_readme() + "`Documentation/zigux/phase15-readiness-gate-survey.md`\n",
        )
        errors = collect_alignment_errors(root)
        expected = [
            "docs_readme:unexpected:`Documentation/zigux/phase15-readiness-gate-survey.md`"
        ]
        if errors != expected:
            raise AssertionError(f"unexpected errors for unexpected readiness marker case: {errors}")
        case_count += 1

        _write(
            root / DOCS_README_PATH,
            _sample_docs_readme() + "`scripts/zigux/validate-phase15.py`\n",
        )
        errors = collect_alignment_errors(root)
        expected = ["docs_readme:unexpected:`scripts/zigux/validate-phase15.py`"]
        if errors != expected:
            raise AssertionError(f"unexpected errors for unexpected validator marker case: {errors}")
        case_count += 1

    print("PHASE15_DOCS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_DOCS_README_ALIGNMENT_SELF_TEST_CASES={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify that the docs-root README still aligns with the current Phase 15 shared-summary gap posture."
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

    errors = collect_alignment_errors(args.root)
    if errors:
        for item in errors:
            print(f"ERROR: {item}")
        return 1

    print("Phase 15 docs README gap alignment check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
