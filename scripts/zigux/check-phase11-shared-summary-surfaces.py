#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path


PHASE11_CONTRACT = Path("Documentation/zigux/phase11-shared-replay-contract.md")
DOCS_README = Path("Documentation/zigux/README.md")
REVIEW_CHECKLIST = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README = Path("scripts/zigux/README.md")

CONTRACT_REQUIRED_MARKERS = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "still skip Phase 11",
    "next same-lane reminder follow-through",
)

DOCS_README_FORBIDDEN_MARKERS = (
    "Phase 11 notes",
    "phase11",
)

REVIEW_CHECKLIST_REQUIRED_MARKERS = (
    "shared Phase 11",
    "make -C zigux phase11-validate",
)

SCRIPTS_README_FORBIDDEN_MARKERS = (
    "## Phase 11",
    "phase11",
)


@dataclass(frozen=True)
class CheckResult:
    label: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check the current shared Phase 11 broad-summary gap packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repository root to inspect.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in pass/fail fixture tests.",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a current-master-like sample root and exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"PHASE11_SHARED_SUMMARY_SURFACES_SAMPLE_ROOT={args.write_sample_root}")
        return 0

    result = check_root(args.root)
    if result is None:
        print("PHASE11_SHARED_SUMMARY_SURFACES=pass")
        print("PHASE11_SHARED_SUMMARY_SURFACES_MODE=current_gap_truthful")
        return 0

    print("PHASE11_SHARED_SUMMARY_SURFACES=fail")
    print(f"PHASE11_SHARED_SUMMARY_SURFACES_DETAIL={result.label}: {result.detail}")
    return 1


def run_self_test() -> int:
    cases = (
        ("pass", None),
        (
            "contract_missing_skip_marker",
            CheckResult(
                "contract",
                "missing marker: still skip Phase 11",
            ),
        ),
        (
            "docs_root_claims_phase11",
            CheckResult(
                "docs_readme",
                "unexpected marker present: Phase 11 notes",
            ),
        ),
        (
            "review_checklist_missing_shared_phase11",
            CheckResult(
                "review_checklist",
                "missing marker: shared Phase 11",
            ),
        ),
        (
            "review_checklist_missing_phase11_validate",
            CheckResult(
                "review_checklist",
                "missing marker: make -C zigux phase11-validate",
            ),
        ),
        (
            "scripts_readme_claims_phase11",
            CheckResult(
                "scripts_readme",
                "unexpected marker present: ## Phase 11",
            ),
        ),
    )

    for name, expected in cases:
        with tempfile.TemporaryDirectory(prefix="phase11_shared_summary_") as tmp_dir:
            root = Path(tmp_dir)
            write_sample_root(root)
            apply_case_mutation(root, name)
            actual = check_root(root)
            if actual != expected:
                raise SystemExit(
                    "self-test failed for "
                    f"{name}: expected {expected!r}, got {actual!r}"
                )

    print("PHASE11_SHARED_SUMMARY_SURFACES_SELF_TEST=pass")
    print(f"PHASE11_SHARED_SUMMARY_SURFACES_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def check_root(root: Path) -> CheckResult | None:
    contract_text = read_text(root, PHASE11_CONTRACT)
    for marker in CONTRACT_REQUIRED_MARKERS:
        if marker not in contract_text:
            return CheckResult("contract", f"missing marker: {marker}")

    docs_readme_text = read_text(root, DOCS_README)
    for marker in DOCS_README_FORBIDDEN_MARKERS:
        if marker in docs_readme_text:
            return CheckResult("docs_readme", f"unexpected marker present: {marker}")

    review_checklist_text = read_text(root, REVIEW_CHECKLIST)
    for marker in REVIEW_CHECKLIST_REQUIRED_MARKERS:
        if marker not in review_checklist_text:
            return CheckResult("review_checklist", f"missing marker: {marker}")

    scripts_readme_text = read_text(root, SCRIPTS_README)
    for marker in SCRIPTS_README_FORBIDDEN_MARKERS:
        if marker in scripts_readme_text:
            return CheckResult("scripts_readme", f"unexpected marker present: {marker}")

    return None


def read_text(root: Path, relative_path: Path) -> str:
    path = root / relative_path
    if not path.is_file():
        raise SystemExit(f"missing required file: {relative_path}")
    return path.read_text(encoding="utf-8")


def write_sample_root(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)

    (root / PHASE11_CONTRACT).write_text(
        "\n".join(
            (
                "# Phase 11 Shared Replay Contract",
                "",
                "Keep the shared reminder surface narrow until the broader summaries catch up.",
                "Documentation/zigux/README.md and scripts/zigux/README.md still skip Phase 11 in their active broad-summary wording,",
                "but Documentation/zigux/review-checklist.md already carries the active shared Phase 11 packet and make -C zigux phase11-validate route,",
                "so treat those two broader summaries as the next same-lane reminder follow-through instead of as already current packet members.",
                "scripts/zigux/README.md remains outside the active shared packet until that follow-through lands.",
                "",
            )
        )
        + "\n",
        encoding="utf-8",
    )
    (root / DOCS_README).write_text(
        "# Zigux Documentation\n\nPhase 10 notes\n\nPhase 12 notes\n",
        encoding="utf-8",
    )
    (root / REVIEW_CHECKLIST).write_text(
        "\n".join(
            (
                "# Zigux Review Checklist",
                "",
                "- shared Phase 10 packet alignment",
                "- if the change touches the shared Phase 11 packet, keep make -C zigux phase11-validate explicit",
                "- shared Phase 12 packet alignment",
                "",
            )
        ),
        encoding="utf-8",
    )
    (root / SCRIPTS_README).write_text(
        "# scripts/zigux\n\n## Phase 10\n\n## Phase 12\n",
        encoding="utf-8",
    )


def apply_case_mutation(root: Path, case_name: str) -> None:
    if case_name == "pass":
        return

    if case_name == "contract_missing_skip_marker":
        path = root / PHASE11_CONTRACT
        path.write_text(
            path.read_text(encoding="utf-8").replace("still skip Phase 11", "still skip later-driver packet"),
            encoding="utf-8",
        )
        return

    if case_name == "docs_root_claims_phase11":
        path = root / DOCS_README
        path.write_text(path.read_text(encoding="utf-8") + "\nPhase 11 notes\n", encoding="utf-8")
        return

    if case_name == "review_checklist_missing_shared_phase11":
        path = root / REVIEW_CHECKLIST
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "- if the change touches the shared Phase 11 packet, keep make -C zigux phase11-validate explicit\n",
                "- if the change touches the shared simple-driver packet, keep make -C zigux phase11-validate explicit\n",
            ),
            encoding="utf-8",
        )
        return

    if case_name == "review_checklist_missing_phase11_validate":
        path = root / REVIEW_CHECKLIST
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "make -C zigux phase11-validate",
                "make -C zigux phase11-review",
            ),
            encoding="utf-8",
        )
        return

    if case_name == "scripts_readme_claims_phase11":
        path = root / SCRIPTS_README
        path.write_text(path.read_text(encoding="utf-8") + "\n## Phase 11\n", encoding="utf-8")
        return

    raise SystemExit(f"unknown self-test case: {case_name}")


if __name__ == "__main__":
    raise SystemExit(main())
