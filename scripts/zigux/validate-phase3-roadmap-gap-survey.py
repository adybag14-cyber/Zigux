#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

_HERE = Path(__file__).resolve()
ROOT = _HERE.parents[2] if len(_HERE.parents) > 2 else _HERE.parent

SURVEY_REL = "Documentation/zigux/phase3-roadmap-gap-survey.md"

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_ROADMAP_ANCHORS=rust/exports.c,lib/bitmap.c,lib/rbtree.c,lib/cpumask.c",
    "PHASE3_CURRENT_EXPORT_SHIM=zigux/kernel/export_shim.zig",
    "PHASE3_CURRENT_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header",
    "PHASE3_CURRENT_UAPI=zigux/uapi/version.zig",
    "PHASE3_CURRENT_UAPI_SCOPE=version-and-boundary-header",
    "PHASE3_UAPI_BOUNDARY_GAP=version-and-boundary-header-surface-is-still-below-full-uapi-shim-destination",
    "PHASE3_CURRENT_BITMAP_CPUMASK=zigux/helpers/bitmap_view.zig,zigux/helpers/cpumask_view.zig",
    "PHASE3_CURRENT_LIST_HLIST=zigux/helpers/list_view.zig,zigux/helpers/hlist_view.zig",
    "PHASE3_CURRENT_RBTREE_STATUS=phase3-dedicated-rbtree-boundary-and-shared-abi-root-view-lift-landed",
    "PHASE3_CURRENT_RBTREE_EVIDENCE=tools/lib/rbtree.zig,lib/rbtree.zig,include/zigux/rbtree.h,zigux/bindings/rbtree.zig,include/zigux/abi.h,zigux/bindings/abi.zig,zigux/helpers/rbtree_view.zig,zigux/helpers/rbtree_root_view.zig,Documentation/zigux/phase1-closure.md,Documentation/zigux/phase3-rbtree-slice.md,Documentation/zigux/phase3-rbtree-interop-survey.md,Documentation/zigux/phase7-rbtree-slice.md,zigux/tests/phase3_rbtree_survey.zig,zigux/tests/phase3_rbtree_root_view_survey.zig,zigux/tests/phase3_rbtree_manifest.json,zigux/tests/phase3_rbtree_shared_contract.zig,zigux/tests/phase3_rbtree_dump.zig,zigux/tests/fixtures/phase3_rbtree/expected.json,zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c,zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json,scripts/zigux/check-phase3-rbtree-shared-lift-contract.py,zigux/tests/phase7_rbtree.zig,zigux/tests/phase7_rbtree_survey.zig,zigux/tests/phase7_rbtree_manifest.json",
    "PHASE3_CURRENT_SHARED_RBTREE_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json",
    "PHASE3_CURRENT_RBTREE_SHARED_CONTRACT=zigux/tests/phase3_rbtree_shared_contract.zig",
    "PHASE3_CURRENT_RBTREE_SHARED_LAYOUT_CONTRACT=shared-phase3-abi-packet-now-carries-rbtree-root-view-through-curated-shared-header-and-binding",
    "PHASE3_CURRENT_RBTREE_SHARED_CATALOG=phase3-abi-manifest-catalogs-dedicated-rbtree-boundary-shared-replay-and-the-still-open-survey-wording-gap",
    "PHASE3_REPO_REALITY=chrdev-plan-growth-exceeds-roadmap-anchors",
    "PHASE3_INTEROP_GAP=helper-slice-wording-still-lags-the-landed-shared-rbtree-lift-while-chrdev-tail-growth-keeps-expanding",
    "PHASE3_NEXT_BOUNDED_STEP=align-phase3-rbtree-helper-slice-wording-before-more-chrdev-growth",
    "PHASE3_VALIDATION_ROUTE=scripts/zigux/validate-phase3.py,make -C zigux phase3-validate,.github/workflows/zigux-bootstrap.yml",
)

REQUIRED_SURVEY_SNIPPETS = (
    "The largest roadmap-backed interop gap is no longer the total absence of a Phase 3 `rbtree` helper or boundary packet, and it is no longer the absence of the first shared Phase 3 `rbtree` root-view lift either.",
    "That packet now exists through:",
    "the dedicated Phase 3 `rbtree` survey and its validator are already aligned with the landed shared `rbtree` lift in `include/zigux/abi.h` and `zigux/bindings/abi.zig`",
    "`Documentation/zigux/phase3-rbtree-slice.md` still describes the broader shared ABI survey-and-validator alignment pass as open even though the shared root-view packet, shared replay, and shared-lift contract are already present",
    "the live Phase 3 build graph still carries deeper `chrdev_*` tail packets well beyond the original four roadmap anchors",
    "The shared ABI replay already covers `zigux_rbtree_root_view` through `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`, and `zigux/tests/fixtures/phase3_abi/expected.json`",
    "The shared ABI manifest already catalogs that shared replay alongside the dedicated packet and the review guards, so the remaining Phase 3 gap is not missing shared code.",
    "It is one bounded survey-and-validator alignment pass before more char-device expansion:",
)

REQUIRED_SURVEY_PATHS = (
    "tools/lib/rbtree.zig",
    "lib/rbtree.zig",
    "include/zigux/rbtree.h",
    "zigux/bindings/rbtree.zig",
    "include/zigux/abi.h",
    "zigux/bindings/abi.zig",
    "zigux/helpers/rbtree_view.zig",
    "zigux/helpers/rbtree_root_view.zig",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase3-rbtree-slice.md",
    "Documentation/zigux/phase3-rbtree-interop-survey.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "zigux/tests/phase3_rbtree_survey.zig",
    "zigux/tests/phase3_rbtree_root_view_survey.zig",
    "zigux/tests/phase3_rbtree_manifest.json",
    "zigux/tests/phase3_rbtree_shared_contract.zig",
    "zigux/tests/phase3_rbtree_dump.zig",
    "zigux/tests/fixtures/phase3_rbtree/expected.json",
    "zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "scripts/zigux/check-phase3-rbtree-shared-lift-contract.py",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_survey.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
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
    if survey:
        _check_snippets(survey, REQUIRED_SURVEY_MARKERS, "missing_survey_marker", issues)
        _check_snippets(survey, REQUIRED_SURVEY_SNIPPETS, "missing_survey_snippet", issues)
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
            "\n".join([*REQUIRED_SURVEY_MARKERS, *REQUIRED_SURVEY_SNIPPETS]) + "\n",
        )
        assert validate(root) == []

        _write(root, SURVEY_REL, REQUIRED_SURVEY_MARKERS[0] + "\n")
        issues = validate(root)
        assert any(issue.startswith("missing_survey_marker:") for issue in issues)
        assert any(issue.startswith("missing_survey_snippet:") for issue in issues)

        _write(
            root,
            SURVEY_REL,
            "\n".join([*REQUIRED_SURVEY_MARKERS, *REQUIRED_SURVEY_SNIPPETS[:-1]]) + "\n",
        )
        issues = validate(root)
        assert (
            "missing_survey_snippet:It is one bounded survey-and-validator alignment pass before more char-device expansion:"
            in issues
        )

        _write(root, SURVEY_REL, "\n".join([*REQUIRED_SURVEY_MARKERS, *REQUIRED_SURVEY_SNIPPETS]) + "\n")
        missing_repo_rel = REQUIRED_SURVEY_PATHS[-1]
        (root / missing_repo_rel).unlink()
        issues = validate(root)
        assert f"missing_repo_path:{missing_repo_rel}" in issues

    print("PHASE3_ROADMAP_GAP_SURVEY_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the published Phase 3 roadmap gap survey stays aligned with the live repo."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run isolated checker tests without reading the full repo.",
    )
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
