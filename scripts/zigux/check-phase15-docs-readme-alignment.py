#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

DOCS_README_REL = "Documentation/zigux/README.md"
READINESS_SURVEY_REL = "Documentation/zigux/phase15-readiness-gate-survey.md"

DOCS_README_MARKERS = (
    "Phase 15 notes",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-freeze-map-governance.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
    "Documentation/zigux/phase15-parity-scorecard-survey.md",
    "Documentation/zigux/phase15-parity-scorecard.md",
    "Documentation/zigux/phase15-indefinite-c-policy.md",
    "Documentation/zigux/phase15-readiness-gate-survey.md",
    "Documentation/zigux/phase15-handoff-next-steps-survey.md",
    "Documentation/zigux/phase15-governance-lane-sequencing.md",
    "scripts/zigux/check-phase15-review-process-handoff.py",
    "scripts/zigux/check-phase15-scripts-readme-alignment.py",
    "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig",
    "zigux/tests/phase15_build.zig",
    "make -C zigux phase15-validate",
    "make -C zigux phase15-test",
    "make -C zigux phase15",
    "no Architecture Council approval is recorded yet",
    "named reopen trigger",
    "deep-core blocker-posture change",
)

READINESS_SURVEY_MARKERS = (
    "python3 scripts/zigux/check-phase15-docs-readme-alignment.py",
    "the docs-root Phase 15 summary stays reviewable through `Documentation/zigux/README.md`, `python3 scripts/zigux/check-phase15-docs-readme-alignment.py`, `scripts/zigux/check-phase15-scripts-readme-alignment.py`, `python3 scripts/zigux/check-phase15-shared-summary-gap.py`, and `python3 scripts/zigux/validate-phase15.py`",
    "phase15-docs-root-summary-alignment",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    for rel in (DOCS_README_REL, READINESS_SURVEY_REL):
        if not (root / rel).exists():
            issues.append(f"missing_file:{rel}")
    if issues:
        return issues

    docs_readme = _read(root / DOCS_README_REL)
    for marker in DOCS_README_MARKERS:
        if marker not in docs_readme:
            issues.append(f"docs_readme:missing:{marker}")

    readiness_survey = _read(root / READINESS_SURVEY_REL)
    for marker in READINESS_SURVEY_MARKERS:
        if marker not in readiness_survey:
            issues.append(f"readiness_survey:missing:{marker}")

    return issues


def _seed(root: Path) -> None:
    _write(root / DOCS_README_REL, "\n".join(DOCS_README_MARKERS) + "\n")
    _write(root / READINESS_SURVEY_REL, "\n".join(READINESS_SURVEY_MARKERS) + "\n")


def _assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        got = ",".join(actual) or "none"
        want = ",".join(expected) or "none"
        raise SystemExit(f"phase15-docs-readme-alignment-self-test:{label}:got={got}:want={want}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase15_docs_readme_alignment_") as tmp_dir:
        root = Path(tmp_dir)
        _seed(root)
        _assert_only(validate(root), [], "baseline")
        case_count += 1

        path = root / DOCS_README_REL
        _write(path, _read(path).replace("Documentation/zigux/phase15-parity-scorecard.md\n", "", 1))
        _assert_only(
            validate(root),
            ["docs_readme:missing:Documentation/zigux/phase15-parity-scorecard.md"],
            "docs_missing_scorecard",
        )
        _seed(root)
        case_count += 1

        path = root / DOCS_README_REL
        _write(path, _read(path).replace("scripts/zigux/check-phase15-review-process-handoff.py\n", "", 1))
        _assert_only(
            validate(root),
            ["docs_readme:missing:scripts/zigux/check-phase15-review-process-handoff.py"],
            "docs_missing_review_process_handoff_checker",
        )
        _seed(root)
        case_count += 1

        path = root / DOCS_README_REL
        _write(path, _read(path).replace("zigux/tests/phase15_build.zig\n", "", 1))
        _assert_only(
            validate(root),
            ["docs_readme:missing:zigux/tests/phase15_build.zig"],
            "docs_missing_build_surface",
        )
        _seed(root)
        case_count += 1

        path = root / DOCS_README_REL
        _write(path, _read(path).replace("make -C zigux phase15-validate\n", "", 1))
        _assert_only(
            validate(root),
            ["docs_readme:missing:make -C zigux phase15-validate"],
            "docs_missing_validate_route",
        )
        _seed(root)
        case_count += 1

        path = root / READINESS_SURVEY_REL
        _write(path, _read(path).replace("phase15-docs-root-summary-alignment\n", "", 1))
        _assert_only(
            validate(root),
            ["readiness_survey:missing:phase15-docs-root-summary-alignment"],
            "readiness_missing_docs_root_gap",
        )
        _seed(root)
        case_count += 1

    print("PHASE15_DOCS_README_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE15_DOCS_README_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 15 docs-root summary aligned with the parked governance packet."
    )
    parser.add_argument("--self-test", action="store_true", help="Run isolated fixture coverage.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(args.root)
    if issues:
        print("PHASE15_DOCS_README_ALIGNMENT=fail")
        print("PHASE15_DOCS_README_ALIGNMENT_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE15_DOCS_README_ALIGNMENT_ISSUES_END")
        return 1

    print("PHASE15_DOCS_README_ALIGNMENT=pass")
    print(f"PHASE15_DOCS_README_ALIGNMENT_REQUIRED_MARKER_COUNT={len(DOCS_README_MARKERS) + len(READINESS_SURVEY_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
