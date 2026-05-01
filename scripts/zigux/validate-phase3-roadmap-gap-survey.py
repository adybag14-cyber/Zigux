#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-roadmap-gap-survey.md"
DOCS_README_REL = "Documentation/zigux/README.md"
SCRIPTS_README_REL = "scripts/zigux/README.md"

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_ROADMAP_ANCHORS=rust/exports.c,lib/bitmap.c,lib/rbtree.c,lib/cpumask.c",
    "PHASE3_CURRENT_EXPORT_SHIM=zigux/kernel/export_shim.zig",
    "PHASE3_CURRENT_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header",
    "PHASE3_CURRENT_UAPI=zigux/uapi/version.zig",
    "PHASE3_CURRENT_UAPI_SCOPE=version-and-boundary-header",
    "PHASE3_UAPI_BOUNDARY_GAP=version-and-boundary-header-surface-is-still-below-full-uapi-shim-destination",
    "PHASE3_CURRENT_BITMAP_CPUMASK=zigux/helpers/bitmap_view.zig,zigux/helpers/cpumask_view.zig",
    "PHASE3_CURRENT_LIST_HLIST=zigux/helpers/list_view.zig,zigux/helpers/hlist_view.zig",
    "PHASE3_CURRENT_RBTREE_STATUS=phase7-helper-exists-but-phase3-interop-slice-is-missing",
    "PHASE3_CURRENT_RBTREE_EVIDENCE=tools/lib/rbtree.zig,lib/rbtree.zig,Documentation/zigux/phase1-closure.md,Documentation/zigux/phase7-rbtree-slice.md,zigux/tests/phase7_rbtree.zig,zigux/tests/phase7_rbtree_survey.zig,zigux/tests/phase7_rbtree_manifest.json",
    "PHASE3_REPO_REALITY=chrdev-plan-growth-exceeds-roadmap-anchors",
    "PHASE3_INTEROP_GAP=rbtree-interop-slice-still-missing",
    "PHASE3_NEXT_BOUNDED_STEP=roadmap-backed-rbtree-interop-survey-or-slice-before-more-chrdev-growth",
)

REQUIRED_SURVEY_PATHS = (
    "include/zigux/abi.h",
    "zigux/bindings/abi.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "zigux/kernel/export_shim.zig",
    "zigux/uapi/version.zig",
    "zigux/helpers/bitmap_view.zig",
    "zigux/helpers/cpumask_view.zig",
    "zigux/helpers/list_view.zig",
    "zigux/helpers/hlist_view.zig",
    "zigux/helpers/cdev_add_plan.zig",
    "zigux/helpers/chrdev_open_plan.zig",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "lib/rbtree.zig",
    "tools/lib/rbtree.zig",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_survey.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
)

RBTREE_FREE_BOUNDARY_PATHS = (
    "include/zigux/abi.h",
    "zigux/bindings/abi.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
)

DISALLOWED_PHASE3_RBTREE_PATH_PATTERNS = (
    ("Documentation/zigux", "phase3-rbtree"),
    ("zigux/tests", "phase3_rbtree"),
    ("zigux/helpers", "rbtree"),
)

REQUIRED_DOCS_README_SNIPPETS = (
    "`Documentation/zigux/phase3-roadmap-gap-survey.md`",
    "`scripts/zigux/validate-phase3-roadmap-gap-survey.py`",
    "`make -C zigux phase3-validate`",
    "current export shim and current `zigux/uapi/version.zig` boundary",
    "existing Phase 1 and Phase 7 `rbtree` evidence",
)

REQUIRED_SCRIPTS_README_SNIPPETS = (
    "`validate-phase3-roadmap-gap-survey.py`",
    "`Documentation/zigux/phase3-roadmap-gap-survey.md`",
    "current export shim and current `zigux/uapi/version.zig` boundary",
    "Phase 1 plus Phase 7 `rbtree` evidence",
)


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def _find_matching_relpaths(root: Path, base_rel: str, needle: str) -> list[str]:
    base = root / base_rel
    if not base.exists():
        return []
    return sorted(
        path.relative_to(root).as_posix()
        for path in base.rglob("*")
        if path.is_file() and needle in path.name
    )


def validate(root: Path) -> list[str]:
    issues: list[str] = []

    survey = _read_text(root, SURVEY_REL, issues)
    docs_readme = _read_text(root, DOCS_README_REL, issues)
    scripts_readme = _read_text(root, SCRIPTS_README_REL, issues)

    if survey:
        for marker in REQUIRED_SURVEY_MARKERS:
            if marker not in survey:
                issues.append(f"missing_survey_marker:{marker}")

    for rel in REQUIRED_SURVEY_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_repo_path:{rel}")

    for rel in RBTREE_FREE_BOUNDARY_PATHS:
        text = _read_text(root, rel, issues)
        if text and "rbtree" in text.lower():
            issues.append(f"stale_rbtree_gap_claim_in_boundary:{rel}")

    for base_rel, needle in DISALLOWED_PHASE3_RBTREE_PATH_PATTERNS:
        for rel in _find_matching_relpaths(root, base_rel, needle):
            issues.append(f"stale_rbtree_gap_claim:{rel}")

    if docs_readme:
        for snippet in REQUIRED_DOCS_README_SNIPPETS:
            if snippet not in docs_readme:
                issues.append(f"missing_docs_readme_snippet:{snippet}")

    if scripts_readme:
        for snippet in REQUIRED_SCRIPTS_README_SNIPPETS:
            if snippet not in scripts_readme:
                issues.append(f"missing_scripts_readme_snippet:{snippet}")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_gap_survey_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        (root / "Documentation" / "zigux").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "zigux").mkdir(parents=True, exist_ok=True)
        (root / "zigux" / "kernel").mkdir(parents=True, exist_ok=True)
        (root / "zigux" / "helpers").mkdir(parents=True, exist_ok=True)
        (root / "zigux" / "tests").mkdir(parents=True, exist_ok=True)
        (root / "zigux" / "uapi").mkdir(parents=True, exist_ok=True)
        (root / "lib").mkdir(parents=True, exist_ok=True)
        (root / "tools" / "lib").mkdir(parents=True, exist_ok=True)

        for rel in REQUIRED_SURVEY_PATHS:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("// ok\n", encoding="utf-8")

        survey_path = root / SURVEY_REL
        survey_path.write_text("\n".join(REQUIRED_SURVEY_MARKERS) + "\n", encoding="utf-8")
        docs_readme_path = root / DOCS_README_REL
        docs_readme_path.write_text("\n".join(REQUIRED_DOCS_README_SNIPPETS) + "\n", encoding="utf-8")
        scripts_readme_path = root / SCRIPTS_README_REL
        scripts_readme_path.write_text("\n".join(REQUIRED_SCRIPTS_README_SNIPPETS) + "\n", encoding="utf-8")

        assert validate(root) == []

        survey_path.write_text(REQUIRED_SURVEY_MARKERS[0] + "\n", encoding="utf-8")
        issues = validate(root)
        assert any(issue.startswith("missing_survey_marker:") for issue in issues)
        survey_path.write_text("\n".join(REQUIRED_SURVEY_MARKERS) + "\n", encoding="utf-8")

        removed_docs_snippet = REQUIRED_DOCS_README_SNIPPETS[0]
        docs_readme_path.write_text("\n".join(REQUIRED_DOCS_README_SNIPPETS[1:]) + "\n", encoding="utf-8")
        issues = validate(root)
        assert f"missing_docs_readme_snippet:{removed_docs_snippet}" in issues
        docs_readme_path.write_text("\n".join(REQUIRED_DOCS_README_SNIPPETS) + "\n", encoding="utf-8")

        removed_scripts_snippet = REQUIRED_SCRIPTS_README_SNIPPETS[0]
        scripts_readme_path.write_text("\n".join(REQUIRED_SCRIPTS_README_SNIPPETS[1:]) + "\n", encoding="utf-8")
        issues = validate(root)
        assert f"missing_scripts_readme_snippet:{removed_scripts_snippet}" in issues
        scripts_readme_path.write_text("\n".join(REQUIRED_SCRIPTS_README_SNIPPETS) + "\n", encoding="utf-8")

        missing_path = root / "zigux" / "uapi" / "version.zig"
        missing_path.unlink()
        issues = validate(root)
        assert "missing_repo_path:zigux/uapi/version.zig" in issues
        missing_path.write_text("// ok\n", encoding="utf-8")

        stale_phase3_doc = root / "Documentation" / "zigux" / "phase3-rbtree-slice.md"
        stale_phase3_doc.write_text("# stale\n", encoding="utf-8")
        issues = validate(root)
        assert "stale_rbtree_gap_claim:Documentation/zigux/phase3-rbtree-slice.md" in issues
        stale_phase3_doc.unlink()

        abi_header = root / "include" / "zigux" / "abi.h"
        abi_header.parent.mkdir(parents=True, exist_ok=True)
        abi_header.write_text("// rbtree drift\n", encoding="utf-8")
        issues = validate(root)
        assert "stale_rbtree_gap_claim_in_boundary:include/zigux/abi.h" in issues

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
