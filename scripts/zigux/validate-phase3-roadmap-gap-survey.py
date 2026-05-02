#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-roadmap-gap-survey.md"

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_ROADMAP_ANCHORS=rust/exports.c,lib/bitmap.c,lib/rbtree.c,lib/cpumask.c",
    "PHASE3_CURRENT_EXPORT_SHIM=zigux/kernel/export_shim.zig",
    "PHASE3_CURRENT_UAPI=zigux/uapi/version.zig",
    "PHASE3_CURRENT_BITMAP_CPUMASK=zigux/helpers/bitmap_view.zig,zigux/helpers/cpumask_view.zig",
    "PHASE3_CURRENT_LIST_HLIST=zigux/helpers/list_view.zig,zigux/helpers/hlist_view.zig",
    "PHASE3_CURRENT_RBTREE_STATUS=phase3-helper-packet-exists-but-curated-c-binding-surface-is-still-missing",
    "PHASE3_INTEROP_GAP=curated-rbtree-c-binding-surface-still-missing",
    "PHASE3_NEXT_BOUNDED_STEP=curated-rbtree-boundary-header-and-parity-fixture-before-more-chrdev-growth",
)

REQUIRED_SURVEY_PATHS = (
    "zigux/helpers/rbtree_view.zig",
    "Documentation/zigux/phase3-rbtree-slice.md",
    "zigux/tests/phase3_rbtree_survey.zig",
    "zigux/tests/phase3_rbtree_manifest.json",
    "lib/rbtree.zig",
    "tools/lib/rbtree.zig",
)


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey_path = root / SURVEY_REL
    try:
        survey = survey_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing_file:{SURVEY_REL}"]

    for marker in REQUIRED_SURVEY_MARKERS:
        if marker not in survey:
            issues.append(f"missing_survey_marker:{marker}")

    for rel in REQUIRED_SURVEY_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_repo_path:{rel}")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_gap_survey_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        for rel in REQUIRED_SURVEY_PATHS:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("// ok\n", encoding="utf-8")

        survey_path = root / SURVEY_REL
        survey_path.parent.mkdir(parents=True, exist_ok=True)
        survey_path.write_text("\n".join(REQUIRED_SURVEY_MARKERS) + "\n", encoding="utf-8")
        assert validate(root) == []

        survey_path.write_text(REQUIRED_SURVEY_MARKERS[0] + "\n", encoding="utf-8")
        issues = validate(root)
        assert any(issue.startswith("missing_survey_marker:") for issue in issues)

    print("PHASE3_ROADMAP_GAP_SURVEY_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the published Phase 3 roadmap gap survey stays aligned with the live repo.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker tests without reading the full repo.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(ROOT)
    if issues:
        print("PHASE3_ROADMAP_GAP_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_ROADMAP_GAP_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
