#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


_HERE = Path(__file__).resolve()
ROOT = _HERE.parents[2] if len(_HERE.parents) > 2 else _HERE.parent
SURVEY_REL = "Documentation/zigux/phase3-roadmap-gap-survey.md"
DOCS_README_REL = "Documentation/zigux/README.md"

FULL_SUPPORTING_CHECKS_SNIPPET = (
    "`python3 scripts/zigux/validate-phase3-roadmap-gap-survey.py`, "
    "`python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py`, "
    "`python3 scripts/zigux/check-phase3-rbtree-shared-lift-contract.py`, "
    "`python3 scripts/zigux/validate-phase3-export-uapi-survey.py`, "
    "`python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py`, "
    "`python3 scripts/zigux/validate-phase3-policy-unsafe-survey.py`, "
    "`python3 scripts/zigux/check-phase3-policy-unsafe-mmio-consumer.py`, "
    "`python3 scripts/zigux/check-phase3-abi-duplicate-declarations.py`, "
    "`python3 scripts/zigux/check-phase3-abi-layout-packet.py`, "
    "`python3 scripts/zigux/check-phase3-abi-binding-constants.py`, "
    "`python3 scripts/zigux/check-phase3-tooling-packet.py`, "
    "`python3 scripts/zigux/check-phase3-readme-tooling-inventory.py`, "
    "`python3 scripts/zigux/check-phase3-validation-flow.py`, "
    "`python3 scripts/zigux/check-phase3-build-roots.py`, and "
    "`python3 scripts/zigux/check-phase3-canonical-survey-manifest.py` stay as "
    "supporting checks inside that same validator-first route instead of standalone release paths"
)

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_ROADMAP_ANCHORS=rust/exports.c,lib/bitmap.c,lib/rbtree.c,lib/cpumask.c",
    "PHASE3_CURRENT_EXPORT_SHIM=zigux/kernel/export_shim.zig",
    "PHASE3_CURRENT_EXPORT_SHIM_SCOPE=explicit-status-plus-boundary-header",
    "PHASE3_CURRENT_UAPI=zigux/uapi/version.zig",
    "PHASE3_CURRENT_UAPI_SCOPE=version-and-boundary-header",
    "PHASE3_CURRENT_BITMAP_CPUMASK=zigux/helpers/bitmap_view.zig,zigux/helpers/cpumask_view.zig",
    "PHASE3_CURRENT_LIST_HLIST=zigux/helpers/list_view.zig,zigux/helpers/hlist_view.zig",
    "PHASE3_CURRENT_RBTREE_STATUS=phase3-dedicated-rbtree-boundary-and-shared-abi-root-view-lift-landed",
    "PHASE3_CURRENT_RBTREE_EVIDENCE=tools/lib/rbtree.zig,lib/rbtree.zig,include/zigux/rbtree.h,zigux/bindings/rbtree.zig,include/zigux/abi.h,zigux/bindings/abi.zig,zigux/helpers/rbtree_view.zig,zigux/helpers/rbtree_root_view.zig,Documentation/zigux/phase1-closure.md,Documentation/zigux/phase3-rbtree-slice.md,Documentation/zigux/phase3-rbtree-interop-survey.md,Documentation/zigux/phase7-rbtree-slice.md,zigux/tests/phase3_rbtree_survey.zig,zigux/tests/phase3_rbtree_root_view_survey.zig,zigux/tests/phase3_rbtree_manifest.json,zigux/tests/phase3_rbtree_shared_contract.zig,zigux/tests/phase3_rbtree_dump.zig,zigux/tests/fixtures/phase3_rbtree/expected.json,zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c,zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json,scripts/zigux/check-phase3-rbtree-shared-lift-contract.py,zigux/tests/phase7_rbtree.zig,zigux/tests/phase7_rbtree_survey.zig,zigux/tests/phase7_rbtree_manifest.json",
    "PHASE3_CURRENT_SHARED_RBTREE_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json",
    "PHASE3_CURRENT_RBTREE_SHARED_CONTRACT=zigux/tests/phase3_rbtree_shared_contract.zig",
    "PHASE3_CURRENT_RBTREE_SHARED_LAYOUT_CONTRACT=shared-phase3-abi-packet-now-carries-rbtree-root-view-through-curated-shared-header-and-binding",
    "PHASE3_CURRENT_RBTREE_SHARED_CATALOG=phase3-abi-manifest-catalogs-dedicated-rbtree-boundary-shared-replay-and-the-still-open-survey-wording-gap",
    "PHASE3_REPO_REALITY=chrdev-plan-growth-exceeds-roadmap-anchors",
    "PHASE3_INTEROP_GAP=survey-and-validator-wording-still-lag-the-landed-shared-rbtree-lift-while-chrdev-tail-growth-keeps-expanding",
    "PHASE3_NEXT_BOUNDED_STEP=align-shared-phase3-survey-and-validator-wording-before-more-chrdev-growth",
    "PHASE3_VALIDATION_ROUTE=scripts/zigux/validate-phase3.py,make -C zigux phase3-validate,.github/workflows/zigux-bootstrap.yml",
)

REQUIRED_SURVEY_SNIPPETS = (
    "The largest roadmap-backed interop gap is no longer the total absence of a Phase 3 `rbtree` helper or boundary packet, and it is no longer the absence of the first shared Phase 3 `rbtree` root-view lift either.",
    "the roadmap wording and some survey-owned wording still lag the landed shared `rbtree` lift in `include/zigux/abi.h` and `zigux/bindings/abi.zig`",
    "the shared ABI replay already covers `zigux_rbtree_root_view` through `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`, and `zigux/tests/fixtures/phase3_abi/expected.json`",
    "The shared ABI manifest already catalogs that shared replay alongside the dedicated packet and the review guards, so the remaining Phase 3 gap is not missing shared code. It is the smaller survey and validator wording drift around already-landed shared ABI reality.",
    "The dedicated roadmap-gap survey is still meant to be reviewed through the shared validator-first path rather than as a standalone bootstrap or release entrypoint.",
    "`python3 scripts/zigux/validate-phase3.py`",
    "`make -C zigux phase3-validate`",
    "the bootstrap workflow replays the same shared validator route before the broader Phase 3 ABI and interop tests run",
    FULL_SUPPORTING_CHECKS_SNIPPET,
    "`python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py` should now be treated as the next bounded follow-on surface for wording alignment around the already-landed shared lift rather than as proof that the shared lift itself is still missing",
    "align the remaining shared Phase 3 survey wording with the landed shared `zigux_rbtree_root_view` lift in `include/zigux/abi.h` and `zigux/bindings/abi.zig`",
    "keep the shared ABI replay, manifest catalog, and dedicated `rbtree` packet explicit in that wording",
    "stop there; do not widen this lane into more `chrdev_*` tail growth or unrelated Phase 3 packet churn",
)

EXACT_ONCE_SURVEY_SNIPPETS = (
    "The dedicated roadmap-gap survey is still meant to be reviewed through the shared validator-first path rather than as a standalone bootstrap or release entrypoint.",
    "`python3 scripts/zigux/validate-phase3.py`",
    "`make -C zigux phase3-validate`",
    "the bootstrap workflow replays the same shared validator route before the broader Phase 3 ABI and interop tests run",
    FULL_SUPPORTING_CHECKS_SNIPPET,
    "`python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py` should now be treated as the next bounded follow-on surface for wording alignment around the already-landed shared lift rather than as proof that the shared lift itself is still missing",
)

REQUIRED_SURVEY_PATHS = (
    "zigux/helpers/rbtree_view.zig",
    "zigux/helpers/rbtree_root_view.zig",
    "include/zigux/rbtree.h",
    "zigux/bindings/rbtree.zig",
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase3-rbtree-slice.md",
    "Documentation/zigux/phase3-rbtree-interop-survey.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "zigux/tests/phase3_rbtree_survey.zig",
    "zigux/tests/phase3_rbtree_root_view_survey.zig",
    "zigux/tests/phase3_rbtree_manifest.json",
    "zigux/tests/phase3_rbtree_dump.zig",
    "zigux/tests/phase3_rbtree_shared_contract.zig",
    "zigux/tests/fixtures/phase3_rbtree/expected.json",
    "zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_survey.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
    "scripts/zigux/check-phase3-rbtree-shared-lift-contract.py",
    "lib/rbtree.zig",
    "tools/lib/rbtree.zig",
)

REQUIRED_DOCS_README_SNIPPETS = (
    "`Documentation/zigux/phase3-roadmap-gap-survey.md`",
    "`scripts/zigux/validate-phase3.py`, `make -C zigux phase3-validate`, and the bootstrap workflow are the validator-first route for the shared Phase 3 review packet",
    "the dedicated survey scripts listed below stay supporting checks inside that shared gate rather than standalone release entrypoints",
    "`scripts/zigux/validate-phase3-roadmap-gap-survey.py` remains a supporting survey check inside that shared validator-first route",
    "`scripts/zigux/validate-phase3-export-uapi-survey.py` remains a supporting survey check inside that shared validator-first route",
    "`scripts/zigux/validate-phase3-low-level-wrapper-survey.py` remains a supporting survey check inside that shared validator-first route",
    "`scripts/zigux/validate-phase3-policy-unsafe-survey.py` remains a supporting survey check inside that shared validator-first route",
    "the current export shim and current `zigux/uapi/version.zig` boundary",
    "the landed dedicated `rbtree` boundary packet and shared `zigux_rbtree_root_view` lift inside `include/zigux/abi.h` and `zigux/bindings/abi.zig`",
    "the remaining survey-and-validator wording gap before more `chrdev_*` tail growth",
    "the note that the longer `chrdev_*` planning ladder should not be mistaken for roadmap closure",
)

EXACT_ONCE_DOCS_README_SNIPPETS = (
    "`scripts/zigux/validate-phase3.py`, `make -C zigux phase3-validate`, and the bootstrap workflow are the validator-first route for the shared Phase 3 review packet",
    "the dedicated survey scripts listed below stay supporting checks inside that shared gate rather than standalone release entrypoints",
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


def _check_exact_count(
    text: str,
    snippets: tuple[str, ...],
    prefix: str,
    expected_count: int,
    issues: list[str],
) -> None:
    for snippet in snippets:
        actual_count = text.count(snippet)
        if actual_count != expected_count:
            issues.append(f"{prefix}:{actual_count}:{snippet}")


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey = _read_text(root, SURVEY_REL, issues)
    docs_readme = _read_text(root, DOCS_README_REL, issues)

    if survey:
        _check_snippets(survey, REQUIRED_SURVEY_MARKERS, "missing_survey_marker", issues)
        _check_snippets(survey, REQUIRED_SURVEY_SNIPPETS, "missing_survey_snippet", issues)
        _check_exact_count(
            survey,
            EXACT_ONCE_SURVEY_SNIPPETS,
            "unexpected_survey_snippet_count",
            1,
            issues,
        )

    if docs_readme:
        _check_snippets(docs_readme, REQUIRED_DOCS_README_SNIPPETS, "missing_docs_readme_snippet", issues)
        _check_exact_count(
            docs_readme,
            EXACT_ONCE_DOCS_README_SNIPPETS,
            "unexpected_docs_readme_snippet_count",
            1,
            issues,
        )

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
            "missing_survey_snippet:stop there; do not widen this lane into more `chrdev_*` tail growth or unrelated Phase 3 packet churn"
            in issues
        )

        _write(root, SURVEY_REL, "\n".join([*REQUIRED_SURVEY_MARKERS, *REQUIRED_SURVEY_SNIPPETS]) + "\n")
        _write(root, DOCS_README_REL, "\n".join(REQUIRED_DOCS_README_SNIPPETS[:-1]) + "\n")
        issues = validate(root)
        assert (
            "missing_docs_readme_snippet:the note that the longer `chrdev_*` planning ladder should not be mistaken for roadmap closure"
            in issues
        )

        _write(
            root,
            SURVEY_REL,
            "\n".join(
                [
                    *REQUIRED_SURVEY_MARKERS,
                    *REQUIRED_SURVEY_SNIPPETS,
                    EXACT_ONCE_SURVEY_SNIPPETS[0],
                ]
            )
            + "\n",
        )
        _write(root, DOCS_README_REL, "\n".join(REQUIRED_DOCS_README_SNIPPETS) + "\n")
        issues = validate(root)
        assert (
            "unexpected_survey_snippet_count:2:"
            + EXACT_ONCE_SURVEY_SNIPPETS[0]
            in issues
        )

        _write(root, SURVEY_REL, "\n".join([*REQUIRED_SURVEY_MARKERS, *REQUIRED_SURVEY_SNIPPETS]) + "\n")
        _write(
            root,
            DOCS_README_REL,
            "\n".join(
                [
                    *REQUIRED_DOCS_README_SNIPPETS,
                    EXACT_ONCE_DOCS_README_SNIPPETS[0],
                ]
            )
            + "\n",
        )
        issues = validate(root)
        assert (
            "unexpected_docs_readme_snippet_count:2:"
            + EXACT_ONCE_DOCS_README_SNIPPETS[0]
            in issues
        )

        _write(root, DOCS_README_REL, "\n".join(REQUIRED_DOCS_README_SNIPPETS) + "\n")
        missing_repo_rel = REQUIRED_SURVEY_PATHS[-1]
        missing_repo_path = root / missing_repo_rel
        missing_repo_path.unlink()
        issues = validate(root)
        assert f"missing_repo_path:{missing_repo_rel}" in issues

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