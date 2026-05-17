#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
DOCS_README = ROOT / "Documentation" / "zigux" / "README.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"

SHIPPED_BENCH_CHECKER = (
    "current `master` does ship `scripts/zigux/check-phase1-bench.py`, "
    "and `.github/workflows/zigux-bootstrap.yml` self-tests it"
)
HISTORICAL_GAP_HINT = "`scripts/zigux/check-phase1-bench.py`"
HISTORICAL_GAP_CONTEXT = "historical"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def contains_historical_gap(path: Path, text: str) -> bool:
    if HISTORICAL_GAP_HINT not in text:
        return False
    return HISTORICAL_GAP_CONTEXT in text.lower() or "missing" in text.lower()


def validate_current_split(
    scripts_readme: str,
    docs_readme: str,
    review_checklist: str,
    tests_readme: str,
) -> tuple[str, str]:
    if SHIPPED_BENCH_CHECKER not in scripts_readme:
        return (
            "scripts_readme_missing_shipped_checker_wording",
            "scripts/zigux/README.md no longer records the shipped Phase 1 bench checker wording",
        )

    if not contains_historical_gap(DOCS_README, docs_readme):
        return (
            "docs_readme_missing_gap_marker",
            "Documentation/zigux/README.md no longer carries the tracked Phase 1 bench wording gap",
        )

    if not contains_historical_gap(REVIEW_CHECKLIST, review_checklist):
        return (
            "review_checklist_missing_gap_marker",
            "Documentation/zigux/review-checklist.md no longer carries the tracked Phase 1 bench wording gap",
        )

    if not contains_historical_gap(TESTS_README, tests_readme):
        return (
            "tests_readme_missing_gap_marker",
            "zigux/tests/README.md no longer carries the tracked Phase 1 bench wording gap",
        )

    return (
        "pass",
        "The shipped scripts-root bench checker wording is present while the three shared reminder surfaces still track the historical bench wording gap.",
    )


def run_self_test() -> None:
    case_count = 0
    scripts_ok = SHIPPED_BENCH_CHECKER
    shared_gap = (
        "keep the broader bench packet framed as a historical gap because "
        "`scripts/zigux/check-phase1-bench.py` still sits inside the missing-route wording"
    )

    kind, _ = validate_current_split(scripts_ok, shared_gap, shared_gap, shared_gap)
    assert kind == "pass"
    case_count += 1

    kind, _ = validate_current_split("no shipped checker wording", shared_gap, shared_gap, shared_gap)
    assert kind == "scripts_readme_missing_shipped_checker_wording"
    case_count += 1

    kind, _ = validate_current_split(scripts_ok, "gap removed", shared_gap, shared_gap)
    assert kind == "docs_readme_missing_gap_marker"
    case_count += 1

    kind, _ = validate_current_split(scripts_ok, shared_gap, "gap removed", shared_gap)
    assert kind == "review_checklist_missing_gap_marker"
    case_count += 1

    kind, _ = validate_current_split(scripts_ok, shared_gap, shared_gap, "gap removed")
    assert kind == "tests_readme_missing_gap_marker"
    case_count += 1

    print("PHASE1_BENCH_REMINDER_SPLIT_SELF_TEST=pass")
    print(f"PHASE1_BENCH_REMINDER_SPLIT_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the current Phase 1 bench reminder split is recorded truthfully: "
            "scripts-root says the bench checker ships, while the three shared reminder "
            "surfaces still treat the broader bench packet as historical-gap material."
        )
    )
    parser.add_argument("--self-test", action="store_true", help="run the checker self-test suite")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    scripts_readme = read_text(SCRIPTS_README)
    docs_readme = read_text(DOCS_README)
    review_checklist = read_text(REVIEW_CHECKLIST)
    tests_readme = read_text(TESTS_README)

    kind, detail = validate_current_split(
        scripts_readme=scripts_readme,
        docs_readme=docs_readme,
        review_checklist=review_checklist,
        tests_readme=tests_readme,
    )
    if kind != "pass":
        print("PHASE1_BENCH_REMINDER_SPLIT=fail")
        print(f"PHASE1_BENCH_REMINDER_SPLIT_REASON={kind}")
        print(detail)
        return 1

    print("PHASE1_BENCH_REMINDER_SPLIT=pass")
    print("PHASE1_BENCH_REMINDER_SPLIT_MODE=gap_tracked")
    print(detail)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
