#!/usr/bin/env python3
"""PHASE14_CHECK_PACKET=docs_readme_returned_companions

Fail-closed checker for the current Phase 14 docs-root returned-companion packet.

This guard keeps `Documentation/zigux/README.md` honest when it summarizes the
shared Phase 14 smoke packet by requiring the returned skbuff survey, freeze-map
owner note, and Phase 15 study-only accounting companion to stay explicit
alongside the shared release-boundary packet.
"""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

DOCS_README_PATH = Path("Documentation/zigux/README.md")
FREEZE_MAP_PATH = Path("Documentation/zigux/freeze-map.md")
STUDY_ONLY_PATH = Path("Documentation/zigux/phase15-study-only-anchor-accounting.md")
RELEASE_BOUNDARY_PATH = Path("Documentation/zigux/phase14-release-boundary-survey.md")
PRODUCTIZATION_GAP_PATH = Path("Documentation/zigux/phase14-productization-gap-survey.md")
ATTACHED_TOOLCHAIN_GUIDANCE_PATH = Path(
    "Documentation/zigux/phase14-attached-toolchain-guidance-gap.md"
)

README_PHASE14_MARKERS = (
    "- `Documentation/zigux/phase14-skbuff-bridge-survey.md`",
    "- `Documentation/zigux/freeze-map.md`",
    "- `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`, `Documentation/zigux/phase14-rcu-tree-survey.md`, `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-study-only-anchor-accounting.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `zigux/tests/phase14_end_to_end_smoke_manifest.json`",
    "the returned skbuff, freeze-map, and study-only accounting companions",
)

FREEZE_MAP_MARKERS = (
    "## Study / Boundary Only",
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
    "shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md` when they summarize that boundary set",
)

STUDY_ONLY_MARKERS = (
    "# Phase 15 Study-Only Anchor Accounting",
    "The roadmap keeps two deep-core areas in a narrower posture than the four freeze-in-C anchors: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only until years of narrower evidence justify anything stronger.",
    "- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
    "- if the governance-lane sequencing note, handoff-next-steps survey, shared-summary gap note, or landed tests-root reminder changes how the study-only anchors are summarized, this note must stay aligned with that same two-anchor inventory and maintenance boundary",
)

RELEASE_BOUNDARY_MARKERS = (
    "- `scripts/zigux/check-phase14-release-boundary-exact-counts.py` now returns through the current contents path and keeps the release-facing exact-count posture aligned with the current shared reminder packet",
    "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
    "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
)

PRODUCTIZATION_GAP_MARKERS = (
    "`scripts/zigux/check-phase14-tests-readme-smoke-summary.py` now returns through the current contents path and keeps the tests-root reminder aligned with the same recovered study-only split without promoting the broader `phase14-smoke`, `phase14-test`, or `phase14` wrappers",
    "the directly readable release-boundary exact-count guard",
    "`zigux/tests/phase14_ring_buffer_survey.zig` now returns through the current contents path as a directly readable ring-buffer survey companion",
)

ATTACHED_TOOLCHAIN_GUIDANCE_MARKERS = (
    "`Documentation/zigux/README.md` is now aligned with that returned split: its Phase 14 docs-root reminder block keeps `Documentation/zigux/phase14-skbuff-bridge-survey.md`, `Documentation/zigux/freeze-map.md`, and `Documentation/zigux/phase15-study-only-anchor-accounting.md` explicit beside the already-listed shared smoke packet members, so the docs-root summary no longer owns the smallest same-lane follow-through",
    "The docs-root, checklist, and tests-root reminders are already aligned with the returned Phase 14 packet, but the scripts-root Phase 14 summary still owns the smallest same-lane reminder repair",
)

REQUIRED_FILES = (
    DOCS_README_PATH,
    FREEZE_MAP_PATH,
    STUDY_ONLY_PATH,
    RELEASE_BOUNDARY_PATH,
    PRODUCTIZATION_GAP_PATH,
    ATTACHED_TOOLCHAIN_GUIDANCE_PATH,
)


def read_text(root: Path, rel: Path) -> str:
    path = root / rel
    if not path.exists():
        raise FileNotFoundError(rel.as_posix())
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], rel: Path, text: str, markers: tuple[str, ...]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"missing_marker:{rel.as_posix()}:{marker}")


def check(root: Path) -> list[str]:
    errors: list[str] = []

    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            errors.append(f"missing_file:{rel.as_posix()}")
    if errors:
        return errors

    require_markers(errors, DOCS_README_PATH, read_text(root, DOCS_README_PATH), README_PHASE14_MARKERS)
    require_markers(errors, FREEZE_MAP_PATH, read_text(root, FREEZE_MAP_PATH), FREEZE_MAP_MARKERS)
    require_markers(errors, STUDY_ONLY_PATH, read_text(root, STUDY_ONLY_PATH), STUDY_ONLY_MARKERS)
    require_markers(
        errors,
        RELEASE_BOUNDARY_PATH,
        read_text(root, RELEASE_BOUNDARY_PATH),
        RELEASE_BOUNDARY_MARKERS,
    )
    require_markers(
        errors,
        PRODUCTIZATION_GAP_PATH,
        read_text(root, PRODUCTIZATION_GAP_PATH),
        PRODUCTIZATION_GAP_MARKERS,
    )
    require_markers(
        errors,
        ATTACHED_TOOLCHAIN_GUIDANCE_PATH,
        read_text(root, ATTACHED_TOOLCHAIN_GUIDANCE_PATH),
        ATTACHED_TOOLCHAIN_GUIDANCE_MARKERS,
    )
    return errors


def seed_fixture(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(
        root / DOCS_README_PATH,
        "\n".join(
            (
                "# Zigux Documentation",
                "Phase 14 notes",
                *README_PHASE14_MARKERS,
                "",
            )
        ),
    )
    write_text(root / FREEZE_MAP_PATH, "\n".join(("# Zigux Freeze Map", *FREEZE_MAP_MARKERS, "")))
    write_text(
        root / STUDY_ONLY_PATH,
        "\n".join(("# Phase 15 Study-Only Anchor Accounting", *STUDY_ONLY_MARKERS, "")),
    )
    write_text(
        root / RELEASE_BOUNDARY_PATH,
        "\n".join(("# Phase 14 Release Boundary Survey", *RELEASE_BOUNDARY_MARKERS, "")),
    )
    write_text(
        root / PRODUCTIZATION_GAP_PATH,
        "\n".join(("# Phase 14 Productization Gap Survey", *PRODUCTIZATION_GAP_MARKERS, "")),
    )
    write_text(
        root / ATTACHED_TOOLCHAIN_GUIDANCE_PATH,
        "\n".join(
            (
                "# Phase 14 Attached Toolchain Guidance Gap",
                *ATTACHED_TOOLCHAIN_GUIDANCE_MARKERS,
                "",
            )
        ),
    )


def remove_once(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text.replace(marker + "\n", "", 1)
    if updated == text:
        updated = text.replace(marker, "", 1)
    path.write_text(updated, encoding="utf-8")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase14-docs-readme-returned-companions-"))
    try:
        seed_fixture(base)
        errors = check(base)
        if errors:
            print("PHASE14_DOCS_README_RETURNED_COMPANIONS_SELF_TEST=fail")
            for error in errors:
                print(error)
            return 1

        cases = [
            (DOCS_README_PATH, README_PHASE14_MARKERS[0]),
            (DOCS_README_PATH, README_PHASE14_MARKERS[3]),
            (FREEZE_MAP_PATH, FREEZE_MAP_MARKERS[3]),
            (STUDY_ONLY_PATH, STUDY_ONLY_MARKERS[2]),
            (RELEASE_BOUNDARY_PATH, RELEASE_BOUNDARY_MARKERS[0]),
            (PRODUCTIZATION_GAP_PATH, PRODUCTIZATION_GAP_MARKERS[0]),
            (ATTACHED_TOOLCHAIN_GUIDANCE_PATH, ATTACHED_TOOLCHAIN_GUIDANCE_MARKERS[0]),
        ]

        for rel, marker in cases:
            seed_fixture(base)
            remove_once(base / rel, marker)
            errors = check(base)
            expected = f"missing_marker:{rel.as_posix()}:{marker}"
            if expected not in errors:
                print("PHASE14_DOCS_README_RETURNED_COMPANIONS_SELF_TEST=fail")
                print(f"expected failure not found: {expected}")
                print("actual_errors_start")
                for error in errors:
                    print(error)
                print("actual_errors_end")
                return 1

        print("PHASE14_DOCS_README_RETURNED_COMPANIONS_SELF_TEST=pass")
        print(f"PHASE14_DOCS_README_RETURNED_COMPANIONS_SELF_TEST_CASE_COUNT={1 + len(cases)}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = check(args.root)
    if errors:
        print("PHASE14_DOCS_README_RETURNED_COMPANIONS=fail")
        print("PHASE14_DOCS_README_RETURNED_COMPANIONS_ISSUES_START")
        for error in errors:
            print(error)
        print("PHASE14_DOCS_README_RETURNED_COMPANIONS_ISSUES_END")
        return 1

    print("PHASE14_DOCS_README_RETURNED_COMPANIONS=pass")
    print(f"PHASE14_DOCS_README_RETURNED_COMPANIONS_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE14_DOCS_README_RETURNED_COMPANIONS_REQUIRED_MARKER_COUNT="
        f"{len(README_PHASE14_MARKERS) + len(FREEZE_MAP_MARKERS) + len(STUDY_ONLY_MARKERS) + len(RELEASE_BOUNDARY_MARKERS) + len(PRODUCTIZATION_GAP_MARKERS) + len(ATTACHED_TOOLCHAIN_GUIDANCE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
