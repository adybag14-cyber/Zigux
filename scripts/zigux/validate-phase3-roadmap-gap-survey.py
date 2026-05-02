#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


_HERE = Path(__file__).resolve()
ROOT = _HERE.parents[2] if len(_HERE.parents) > 2 else _HERE.parent
SURVEY_REL = "Documentation/zigux/phase3-roadmap-gap-survey.md"
DOCS_README_REL = "Documentation/zigux/README.md"

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_ROADMAP_ANCHORS=rust/exports.c,lib/bitmap.c,lib/rbtree.c,lib/cpumask.c",
    "PHASE3_CURRENT_EXPORT_SHIM=zigux/kernel/export_shim.zig",
    "PHASE3_CURRENT_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header",
    "PHASE3_CURRENT_UAPI=zigux/uapi/version.zig",
    "PHASE3_CURRENT_UAPI_SCOPE=version-and-boundary-header",
    "PHASE3_CURRENT_BITMAP_CPUMASK=zigux/helpers/bitmap_view.zig,zigux/helpers/cpumask_view.zig",
    "PHASE3_CURRENT_LIST_HLIST=zigux/helpers/list_view.zig,zigux/helpers/hlist_view.zig",
    "PHASE3_CURRENT_RBTREE_STATUS=phase3-helper-packet-exists-but-curated-c-binding-surface-is-still-missing",
    "PHASE3_CURRENT_RBTREE_EVIDENCE=tools/lib/rbtree.zig,lib/rbtree.zig,zigux/helpers/rbtree_view.zig,Documentation/zigux/phase1-closure.md,Documentation/zigux/phase3-rbtree-slice.md,Documentation/zigux/phase7-rbtree-slice.md,zigux/tests/phase3_rbtree_survey.zig,zigux/tests/phase3_rbtree_manifest.json,zigux/tests/phase7_rbtree.zig,zigux/tests/phase7_rbtree_survey.zig,zigux/tests/phase7_rbtree_manifest.json",
    "PHASE3_REPO_REALITY=chrdev-plan-growth-exceeds-roadmap-anchors",
    "PHASE3_INTEROP_GAP=curated-rbtree-c-binding-surface-still-missing",
    "PHASE3_NEXT_BOUNDED_STEP=curated-rbtree-boundary-header-and-parity-fixture-before-more-chrdev-growth",
)

REQUIRED_SURVEY_SNIPPETS = (
    "The largest roadmap-backed interop gap is no longer the total absence of a Phase 3 `rbtree` helper family.",
    "there is still no curated `rbtree` record in `include/zigux/abi.h`",
    "there is still no matching `zigux/bindings/abi.zig` layout type for a Phase 3 `rbtree` boundary packet",
    "there is still no C-vs-Zig parity fixture for a Phase 3 `rbtree` boundary shape",
    "one header-and-binding shape",
    "one focused parity fixture",
    "one validator-backed note refresh",
)

REQUIRED_SURVEY_PATHS = (
    "zigux/helpers/rbtree_view.zig",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase3-rbtree-slice.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "zigux/tests/phase3_rbtree_survey.zig",
    "zigux/tests/phase3_rbtree_manifest.json",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_survey.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
    "lib/rbtree.zig",
    "tools/lib/rbtree.zig",
)

REQUIRED_DOCS_README_SNIPPETS = (
    "`Documentation/zigux/phase3-roadmap-gap-survey.md`",
    "`scripts/zigux/validate-phase3-roadmap-gap-survey.py`",
    "`make -C zigux phase3-validate`",
    "the current export shim and current `zigux/uapi/version.zig` boundary",
    "the current `rbtree` gap",
    "the existing Phase 1 and Phase 7 `rbtree` evidence that does not yet close the Phase 3 boundary packet",
    "the note that the longer `chrdev_*` planning ladder should not be mistaken for roadmap closure",
)


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def _check_snippets(text: str, snippets: tuple[str, ...], prefix: str, issues: list[str]) -> None:
    for snippet in snippets:
        if snippet not in text:
            issues.append(f"{prefix}:{snippet}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey = _read_text(root, SURVEY_REL, issues)
    docs_readme = _read_text(root, DOCS_README_REL, issues)

    if survey:
        _check_snippets(survey, REQUIRED_SURVEY_MARKERS, "missing_survey_marker", issues)
        _check_snippets(survey, REQUIRED_SURVEY_SNIPPETS, "missing_survey_snippet", issues)

    if docs_readme:
        _check_snippets(docs_readme, REQUIRED_DOCS_README_SNIPPETS, "missing_docs_readme_snippet", issues)

    for rel in REQUIRED_SURVEY_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_repo_path:{rel}")

    return issues


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_gap_survey_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        for rel in REQUIRED_SURVEY_PATHS:
            _write(root, rel, "// ok\n")

        _write(
            root,
            SURVEY_REL,
            "\n".join(
                [
                    *REQUIRED_SURVEY_MARKERS,
                    *REQUIRED_SURVEY_SNIPPETS,
                ]
            )
            + "\n",
        )
        _write(root, DOCS_README_REL, "\n".join(REQUIRED_DOCS_README_SNIPPETS) + "\n")
        assert validate(root) == []

        _write(root, SURVEY_REL, REQUIRED_SURVEY_MARKERS[0] + "\n")
        issues = validate(root)
        assert any(issue.startswith("missing_survey_marker:") for issue in issues)
        assert any(issue.startswith("missing_survey_snippet:") for issue in issues)

        _write(
            root,
            SURVEY_REL,
            "\n".join(
                [
                    *REQUIRED_SURVEY_MARKERS,
                    *REQUIRED_SURVEY_SNIPPETS[:-1],
                ]
            )
            + "\n",
        )
        issues = validate(root)
        assert (
            "missing_survey_snippet:one validator-backed note refresh"
            in issues
        )

        _write(root, SURVEY_REL, "\n".join([*REQUIRED_SURVEY_MARKERS, *REQUIRED_SURVEY_SNIPPETS]) + "\n")
        _write(root, DOCS_README_REL, "\n".join(REQUIRED_DOCS_README_SNIPPETS[:-1]) + "\n")
        issues = validate(root)
        assert (
            "missing_docs_readme_snippet:the note that the longer `chrdev_*` planning ladder should not be mistaken for roadmap closure"
            in issues
        )

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
