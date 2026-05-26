#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=scripts_readme_gap

Fail-closed checker for the current Phase 14 scripts-root reminder undercount.

This guard keeps the live P14-L05 packet honest while the current scripts-root
Phase 14 summary still lags the broader returned shared-smoke evidence family.
It verifies that the shared gap notes explicitly call out the scripts-root
undercount, that the returned Phase 14 reminder family still names the skbuff
stay-in-C and compile-route guards as current evidence, and that the scripts
README still omits those two skbuff guards from its own Phase 14 summary.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


MARKER = "PHASE14_CHECK_PACKET=scripts_readme_gap"

SHARED_GAP_PATH = Path("Documentation/zigux/phase14-shared-smoke-current-master-gap.md")
ATTACHED_GUIDANCE_PATH = Path(
    "Documentation/zigux/phase14-attached-toolchain-guidance-gap.md"
)
PRODUCTIZATION_GAP_PATH = Path(
    "Documentation/zigux/phase14-productization-gap-survey.md"
)
SMOKE_SURVEY_PATH = Path("Documentation/zigux/phase14-end-to-end-smoke-survey.md")
RELEASE_BOUNDARY_PATH = Path("Documentation/zigux/phase14-release-boundary-survey.md")
REVIEW_CHECKLIST_PATH = Path("Documentation/zigux/review-checklist.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")

SCRIPTS_PHASE14_START = "## Phase 14"
SCRIPTS_PHASE14_END = "## Phase 15"

REQUIRED_SHARED_GAP_MARKERS = (
    "- `PHASE14_LANE_KEY=P14-L05`",
    "Fresh repo-first comparison in the `pmo-release` lane now makes the next smallest shared reminder repair explicit: `scripts/zigux/README.md` still undercounts the returned Phase 14 packet because its Phase 14 summary omits `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py` and `scripts/zigux/check-phase14-skbuff-compile-route.py`, even though the returned shared-smoke packet already treats both skbuff guards as current reminder evidence.",
)

REQUIRED_ATTACHED_GUIDANCE_MARKERS = (
    "the scripts-root Phase 14 summary still owns the smallest same-lane reminder repair because it undercounts the returned skbuff stay-in-C guard",
    "`scripts/zigux/README.md` still lags the broader shared packet by omitting the returned dedicated skbuff stay-in-C guard and the returned shared skbuff, freeze-map, and study-only accounting companions",
)

REQUIRED_PRODUCTIZATION_MARKERS = (
    "the directly readable dedicated skbuff stay-in-C guard",
    "the directly readable dedicated skbuff compile-route guard",
    "keep shared notes aligned with the recovered documentation packet",
)

REQUIRED_SMOKE_SURVEY_MARKERS = (
    "* `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py` is directly readable again through the current contents path",
    "* `scripts/zigux/check-phase14-skbuff-compile-route.py` is directly readable again through the current contents path",
    "* some shared reminder surfaces may still lag this current route split",
)

REQUIRED_RELEASE_BOUNDARY_MARKERS = (
    "- current reminder-surface alignment: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-shared-smoke-current-master-gap.md`, `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-rcu-tree-survey.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `Documentation/zigux/review-checklist.md` already keep the recovered study-only packet explicit",
    "the directly readable shared rollback-threshold checker",
    "the directly readable dedicated RCU rollback guard",
)

REQUIRED_CHECKLIST_MARKERS = (
    "if the change touches the shared Phase 14 smoke packet",
    "`scripts/zigux/check-phase14-rollback-threshold-sequencing.py`",
    "`zigux/Makefile` framed as readable current evidence for the shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes together with the returned `make -C zigux phase14-validate` gate while `phase14-smoke`, `phase14-test`, and `phase14` stay packet-local or repo-reality-gap vocabulary",
)

REQUIRED_SCRIPTS_PHASE14_MARKERS = (
    "the returned `phase14-validate` split",
    "`scripts/zigux/check-phase14-shared-smoke-route.py`",
    "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py`",
    "`scripts/zigux/validate-phase14.py`",
    "`scripts/zigux/check-phase14-rollback-threshold-sequencing.py`",
    "`scripts/zigux/check-phase14-release-boundary-exact-counts.py`",
    "`zigux/Makefile`",
    "the broader `phase14-smoke`, `phase14-test`, and `phase14` wrappers remain absent on current `master`",
)

REQUIRED_ABSENT_SCRIPTS_PHASE14_MARKERS = (
    "`scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py`",
    "`scripts/zigux/check-phase14-skbuff-compile-route.py`",
)


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    if not path.exists():
        raise FileNotFoundError(rel.as_posix())
    return path.read_text(encoding="utf-8")


def write_text(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], rel: Path, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def require_absent(errors: list[str], rel: Path, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"unexpected_marker:{rel.as_posix()}:{marker}")


def section(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    if start == -1:
        raise ValueError(f"missing section start marker: {start_marker}")
    end = text.find(end_marker, start)
    if end == -1:
        raise ValueError(f"missing section end marker: {end_marker}")
    return text[start:end]


def check(root: Path) -> list[str]:
    errors: list[str] = []
    required_paths = (
        SHARED_GAP_PATH,
        ATTACHED_GUIDANCE_PATH,
        PRODUCTIZATION_GAP_PATH,
        SMOKE_SURVEY_PATH,
        RELEASE_BOUNDARY_PATH,
        REVIEW_CHECKLIST_PATH,
        SCRIPTS_README_PATH,
    )

    for rel in required_paths:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    require_markers(errors, SHARED_GAP_PATH, read_text(root, SHARED_GAP_PATH), REQUIRED_SHARED_GAP_MARKERS)
    require_markers(
        errors,
        ATTACHED_GUIDANCE_PATH,
        read_text(root, ATTACHED_GUIDANCE_PATH),
        REQUIRED_ATTACHED_GUIDANCE_MARKERS,
    )
    require_markers(
        errors,
        PRODUCTIZATION_GAP_PATH,
        read_text(root, PRODUCTIZATION_GAP_PATH),
        REQUIRED_PRODUCTIZATION_MARKERS,
    )
    require_markers(errors, SMOKE_SURVEY_PATH, read_text(root, SMOKE_SURVEY_PATH), REQUIRED_SMOKE_SURVEY_MARKERS)
    require_markers(
        errors,
        RELEASE_BOUNDARY_PATH,
        read_text(root, RELEASE_BOUNDARY_PATH),
        REQUIRED_RELEASE_BOUNDARY_MARKERS,
    )
    require_markers(
        errors,
        REVIEW_CHECKLIST_PATH,
        read_text(root, REVIEW_CHECKLIST_PATH),
        REQUIRED_CHECKLIST_MARKERS,
    )

    scripts_text = read_text(root, SCRIPTS_README_PATH)
    try:
        scripts_phase14 = section(scripts_text, SCRIPTS_PHASE14_START, SCRIPTS_PHASE14_END)
    except ValueError as exc:
        errors.append(f"scripts_phase14_section:{exc}")
        return errors

    require_markers(
        errors,
        SCRIPTS_README_PATH,
        scripts_phase14,
        REQUIRED_SCRIPTS_PHASE14_MARKERS,
    )
    require_absent(
        errors,
        SCRIPTS_README_PATH,
        scripts_phase14,
        REQUIRED_ABSENT_SCRIPTS_PHASE14_MARKERS,
    )
    return errors


def fixture_shared_gap() -> str:
    return "\n".join(
        [
            "# Phase 14 Shared Smoke Current-Master Gap",
            *REQUIRED_SHARED_GAP_MARKERS,
            "",
        ]
    )


def fixture_attached_guidance() -> str:
    return "\n".join(
        [
            "# Phase 14 Attached Toolchain Guidance Gap",
            *REQUIRED_ATTACHED_GUIDANCE_MARKERS,
            "",
        ]
    )


def fixture_productization_gap() -> str:
    return "\n".join(
        [
            "# Phase 14 Productization Gap Survey",
            *REQUIRED_PRODUCTIZATION_MARKERS,
            "",
        ]
    )


def fixture_smoke_survey() -> str:
    return "\n".join(
        [
            "# Phase 14 End-to-End Smoke Survey",
            *REQUIRED_SMOKE_SURVEY_MARKERS,
            "",
        ]
    )


def fixture_release_boundary() -> str:
    return "\n".join(
        [
            "# Phase 14 Release Boundary Survey",
            *REQUIRED_RELEASE_BOUNDARY_MARKERS,
            "",
        ]
    )


def fixture_review_checklist() -> str:
    return "\n".join(
        [
            "# Zigux Review Checklist",
            *REQUIRED_CHECKLIST_MARKERS,
            "",
        ]
    )


def fixture_scripts_readme() -> str:
    phase14_lines = [
        "# scripts/zigux",
        SCRIPTS_PHASE14_START,
        *REQUIRED_SCRIPTS_PHASE14_MARKERS,
        SCRIPTS_PHASE14_END,
        "",
    ]
    return "\n".join(phase14_lines)


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(root, SHARED_GAP_PATH, fixture_shared_gap())
    write_text(root, ATTACHED_GUIDANCE_PATH, fixture_attached_guidance())
    write_text(root, PRODUCTIZATION_GAP_PATH, fixture_productization_gap())
    write_text(root, SMOKE_SURVEY_PATH, fixture_smoke_survey())
    write_text(root, RELEASE_BOUNDARY_PATH, fixture_release_boundary())
    write_text(root, REVIEW_CHECKLIST_PATH, fixture_review_checklist())
    write_text(root, SCRIPTS_README_PATH, fixture_scripts_readme())


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"marker not found: {old}")
    return text.replace(old, new, 1)


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-scripts-readme-gap-"))
    try:
        write_fixture_tree(base)
        errors = check(base)
        if errors:
            print("PHASE14_SCRIPTS_README_GAP_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        cases = 1

        write_fixture_tree(base)
        text = read_text(base, SHARED_GAP_PATH)
        write_text(
            base,
            SHARED_GAP_PATH,
            replace_once(
                text,
                REQUIRED_SHARED_GAP_MARKERS[1],
                "Fresh repo-first comparison still shows a smaller scripts-root issue.",
            ),
        )
        if not any(REQUIRED_SHARED_GAP_MARKERS[1] in error for error in check(base)):
            print("PHASE14_SCRIPTS_README_GAP_SELF_TEST=fail")
            print("expected shared-gap drift failure")
            return 1
        cases += 1

        write_fixture_tree(base)
        text = read_text(base, ATTACHED_GUIDANCE_PATH)
        write_text(
            base,
            ATTACHED_GUIDANCE_PATH,
            replace_once(
                text,
                REQUIRED_ATTACHED_GUIDANCE_MARKERS[1],
                "`scripts/zigux/README.md` is fully aligned with the broader shared packet",
            ),
        )
        if not any(REQUIRED_ATTACHED_GUIDANCE_MARKERS[1] in error for error in check(base)):
            print("PHASE14_SCRIPTS_README_GAP_SELF_TEST=fail")
            print("expected attached-guidance drift failure")
            return 1
        cases += 1

        write_fixture_tree(base)
        text = read_text(base, SCRIPTS_README_PATH)
        write_text(
            base,
            SCRIPTS_README_PATH,
            replace_once(
                text,
                REQUIRED_SCRIPTS_PHASE14_MARKERS[0],
                "the returned shared packet",
            ),
        )
        if not any(REQUIRED_SCRIPTS_PHASE14_MARKERS[0] in error for error in check(base)):
            print("PHASE14_SCRIPTS_README_GAP_SELF_TEST=fail")
            print("expected scripts readme missing-marker failure")
            return 1
        cases += 1

        write_fixture_tree(base)
        text = read_text(base, SCRIPTS_README_PATH)
        injected = text.replace(
            SCRIPTS_PHASE14_END,
            "`scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py`\n" + SCRIPTS_PHASE14_END,
            1,
        )
        write_text(base, SCRIPTS_README_PATH, injected)
        if not any(
            REQUIRED_ABSENT_SCRIPTS_PHASE14_MARKERS[0] in error for error in check(base)
        ):
            print("PHASE14_SCRIPTS_README_GAP_SELF_TEST=fail")
            print("expected scripts readme absence-contract failure")
            return 1
        cases += 1

        write_fixture_tree(base)
        text = read_text(base, REVIEW_CHECKLIST_PATH)
        write_text(
            base,
            REVIEW_CHECKLIST_PATH,
            replace_once(
                text,
                REQUIRED_CHECKLIST_MARKERS[2],
                "`zigux/Makefile` keeps the shared Phase 14 route explicit",
            ),
        )
        if not any(REQUIRED_CHECKLIST_MARKERS[2] in error for error in check(base)):
            print("PHASE14_SCRIPTS_README_GAP_SELF_TEST=fail")
            print("expected review-checklist drift failure")
            return 1
        cases += 1

        print("PHASE14_SCRIPTS_README_GAP_SELF_TEST=pass")
        print(f"PHASE14_SCRIPTS_README_GAP_SELF_TEST_CASE_COUNT={cases}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root.resolve())
    if errors:
        print("PHASE14_SCRIPTS_README_GAP=fail")
        print("PHASE14_SCRIPTS_README_GAP_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_SCRIPTS_README_GAP_ISSUES_END")
        return 1

    print("PHASE14_SCRIPTS_README_GAP=pass")
    print(f"PHASE14_SCRIPTS_README_GAP_REQUIRED_FILE_COUNT=7")
    print(f"PHASE14_SCRIPTS_README_GAP_REQUIRED_MARKER_COUNT={len(REQUIRED_SCRIPTS_PHASE14_MARKERS)}")
    print(f"PHASE14_SCRIPTS_README_GAP_ABSENCE_CONTRACT_COUNT={len(REQUIRED_ABSENT_SCRIPTS_PHASE14_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
