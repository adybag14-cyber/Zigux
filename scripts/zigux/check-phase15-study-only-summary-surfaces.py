#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
STUDY_ONLY_ACCOUNTING_PATH = "Documentation/zigux/phase15-study-only-anchor-accounting.md"
DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"

FREEZE_MAP_REQUIRED_MARKERS = [
    "# Zigux Freeze Map",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "`Documentation/zigux/README.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
]

STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS = [
    "# Phase 15 Study-Only Anchor Accounting",
    "`kernel/workqueue.c`",
    "`kernel/trace/ring_buffer.c`",
    "this note is an inventory and handoff surface, not an approval record",
    "if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it",
]

DOCS_README_REQUIRED_MARKERS = [
    "`Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain study-only anchors",
]

REVIEW_CHECKLIST_REQUIRED_MARKERS = [
    "if a shared reminder surface summarizes the study-only freeze-map anchors",
    "`Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in [
        FREEZE_MAP_PATH,
        STUDY_ONLY_ACCOUNTING_PATH,
        DOCS_README_PATH,
        REVIEW_CHECKLIST_PATH,
    ]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    freeze_map = read_text(root, FREEZE_MAP_PATH)
    for marker in FREEZE_MAP_REQUIRED_MARKERS:
        if marker not in freeze_map:
            failures.append(f"missing_marker:{FREEZE_MAP_PATH}:{marker}")

    study_only = read_text(root, STUDY_ONLY_ACCOUNTING_PATH)
    for marker in STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS:
        if marker not in study_only:
            failures.append(f"missing_marker:{STUDY_ONLY_ACCOUNTING_PATH}:{marker}")

    docs_readme = read_text(root, DOCS_README_PATH)
    for marker in DOCS_README_REQUIRED_MARKERS:
        if marker not in docs_readme:
            failures.append(f"missing_marker:{DOCS_README_PATH}:{marker}")

    review_checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    for marker in REVIEW_CHECKLIST_REQUIRED_MARKERS:
        if marker not in review_checklist:
            failures.append(f"missing_marker:{REVIEW_CHECKLIST_PATH}:{marker}")

    return failures


def build_freeze_map_fixture_text() -> str:
    return """# Zigux Freeze Map

- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- shared reminder surfaces that summarize freeze posture, especially `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md`, must keep the same study-only anchor inventory and route back to `Documentation/zigux/phase15-study-only-anchor-accounting.md`
"""


def build_study_only_accounting_fixture_text() -> str:
    return """# Phase 15 Study-Only Anchor Accounting

- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`
- this note is an inventory and handoff surface, not an approval record
- if the study-only anchor set changes in `Documentation/zigux/freeze-map.md`, this note must change with it
"""


def build_docs_readme_fixture_text() -> str:
    return """# Zigux Documentation

- `Documentation/zigux/phase15-study-only-anchor-accounting.md`
- current `master` does materialize `kernel/workqueue_bridge.zig`, while `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain study-only anchors and while `net/core/skbuff.c` and `kernel/rcu/tree.c` remain freeze-in-C anchors
"""


def build_review_checklist_fixture_text() -> str:
    return """# Zigux Review Checklist

- if a shared reminder surface summarizes the study-only freeze-map anchors, does it route that summary back through `Documentation/zigux/freeze-map.md` and `Documentation/zigux/phase15-study-only-anchor-accounting.md` so `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay explicit as study-only boundary context rather than runtime-substrate or bridge-readiness evidence?
"""


def seed_fixture_tree(base: Path) -> None:
    write_text(base / FREEZE_MAP_PATH, build_freeze_map_fixture_text())
    write_text(base / STUDY_ONLY_ACCOUNTING_PATH, build_study_only_accounting_fixture_text())
    write_text(base / DOCS_README_PATH, build_docs_readme_fixture_text())
    write_text(base / REVIEW_CHECKLIST_PATH, build_review_checklist_fixture_text())


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase15-study-only-summary-surfaces-"))
    try:
        seed_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in FREEZE_MAP_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            current = build_freeze_map_fixture_text()
            if current.count(marker) != 1:
                continue
            write_text(base / FREEZE_MAP_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{FREEZE_MAP_PATH}:{marker}")

        for marker in STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            current = build_study_only_accounting_fixture_text()
            if current.count(marker) != 1:
                continue
            write_text(base / STUDY_ONLY_ACCOUNTING_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{STUDY_ONLY_ACCOUNTING_PATH}:{marker}")

        for marker in DOCS_README_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            current = build_docs_readme_fixture_text()
            if current.count(marker) != 1:
                continue
            write_text(base / DOCS_README_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{DOCS_README_PATH}:{marker}")

        for marker in REVIEW_CHECKLIST_REQUIRED_MARKERS:
            seed_fixture_tree(base)
            current = build_review_checklist_fixture_text()
            if current.count(marker) != 1:
                continue
            write_text(base / REVIEW_CHECKLIST_PATH, current.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{REVIEW_CHECKLIST_PATH}:{marker}")

        for rel_path in [
            FREEZE_MAP_PATH,
            STUDY_ONLY_ACCOUNTING_PATH,
            DOCS_README_PATH,
            REVIEW_CHECKLIST_PATH,
        ]:
            seed_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE15_STUDY_ONLY_SUMMARY_SURFACES_SELF_TEST=pass")
    print(f"PHASE15_FREEZE_MAP_MARKER_COUNT={len(FREEZE_MAP_REQUIRED_MARKERS)}")
    print(
        "PHASE15_STUDY_ONLY_ACCOUNTING_MARKER_COUNT="
        f"{len(STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS)}"
    )
    print(f"PHASE15_DOCS_README_MARKER_COUNT={len(DOCS_README_REQUIRED_MARKERS)}")
    print(
        "PHASE15_REVIEW_CHECKLIST_MARKER_COUNT="
        f"{len(REVIEW_CHECKLIST_REQUIRED_MARKERS)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the shared study-only reminder surfaces keep the freeze-map "
            "anchor inventory and routing back to the Phase 15 accounting note explicit."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE15_STUDY_ONLY_SUMMARY_SURFACES_ERROR={failure}")
        return 1

    print(f"PHASE15_FREEZE_MAP_MARKER_COUNT={len(FREEZE_MAP_REQUIRED_MARKERS)}")
    print(
        "PHASE15_STUDY_ONLY_ACCOUNTING_MARKER_COUNT="
        f"{len(STUDY_ONLY_ACCOUNTING_REQUIRED_MARKERS)}"
    )
    print(f"PHASE15_DOCS_README_MARKER_COUNT={len(DOCS_README_REQUIRED_MARKERS)}")
    print(
        "PHASE15_REVIEW_CHECKLIST_MARKER_COUNT="
        f"{len(REVIEW_CHECKLIST_REQUIRED_MARKERS)}"
    )
    print("PHASE15_STUDY_ONLY_SUMMARY_SURFACES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
