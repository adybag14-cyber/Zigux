#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SURVEY_REL = "Documentation/zigux/phase3-rbtree-interop-survey.md"
ROADMAP_GAP_SURVEY_REL = "Documentation/zigux/phase3-roadmap-gap-survey.md"
SLICE_REL = "Documentation/zigux/phase3-rbtree-slice.md"
SHARED_LIFT_CHECK_REL = "scripts/zigux/check-phase3-rbtree-shared-lift-contract.py"
ABI_MANIFEST_REL = "zigux/tests/fixtures/phase3_abi_manifest.json"

REQUIRED_SURVEY_MARKERS = (
    "PHASE3_RBTREE_ROADMAP_ANCHOR=lib/rbtree.c",
    "PHASE3_RBTREE_PHASE1_EVIDENCE=tools/lib/rbtree.zig,Documentation/zigux/phase1-closure.md",
    "PHASE3_RBTREE_PHASE7_EVIDENCE=lib/rbtree.zig,Documentation/zigux/phase7-rbtree-slice.md,zigux/tests/phase7_rbtree.zig,zigux/tests/phase7_rbtree_survey.zig,zigux/tests/phase7_rbtree_manifest.json",
    "PHASE3_RBTREE_PHASE3_HELPER=zigux/helpers/rbtree_view.zig,zigux/helpers/rbtree_root_view.zig",
    "PHASE3_RBTREE_PHASE3_BOUNDARY=include/zigux/rbtree.h,zigux/bindings/rbtree.zig,zigux/tests/phase3_rbtree_dump.zig,zigux/tests/fixtures/phase3_rbtree/expected.json,zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c",
    "PHASE3_RBTREE_PHASE3_SURVEY=zigux/tests/phase3_rbtree_survey.zig,zigux/tests/phase3_rbtree_root_view_survey.zig,zigux/tests/phase3_rbtree_manifest.json",
    "PHASE3_RBTREE_PHASE3_SLICE=Documentation/zigux/phase3-rbtree-slice.md",
    "PHASE3_RBTREE_PHASE3_BOUNDARY_STATUS=dedicated-boundary-landed-shared-abi-lift-still-missing",
    "PHASE3_RBTREE_NON_GOALS=no-balancing-port,no-export-shim-growth,no-uapi-growth",
    "PHASE3_RBTREE_NEXT_BOUNDED_STEP=one-shared-phase3-abi-rbtree-root-view",
    "PHASE3_RBTREE_SHARED_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json",
    "PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT=zigux_rbtree_root_view-reused-unchanged-in-shared-phase3-abi-packet",
    "PHASE3_RBTREE_SHARED_CONSTANT_CONTRACT=root_flag_empty,root_flag_cached,root_flag_leftmost_valid",
    "PHASE3_RBTREE_SHARED_CONTRACT=zigux/tests/phase3_rbtree_shared_contract.zig",
    "PHASE3_RBTREE_SHARED_PACKET_CATALOG=phase3_abi_manifest-catalogs-dedicated-rbtree-boundary-packet",
    "PHASE3_RBTREE_SURVEY_GATE=python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py",
    "PHASE3_RBTREE_SHARED_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py --slug abi",
    "PHASE3_RBTREE_SHARED_MAKE_GATE=make -C zigux phase3-validate",
)

REQUIRED_SURVEY_SNIPPETS = (
    "That means the remaining Phase 3 gap is no longer “no curated C header, bindings record, or parity fixture exists.” The remaining gap is that current `master` still has no shared `rbtree` record inside `include/zigux/abi.h` and `zigux/bindings/abi.zig`, and the shared `phase3_abi` replay still reaches `rbtree` through `include/zigux/rbtree.h` and `zigux/bindings/rbtree.zig` rather than through a curated shared record.",
    "`python3 scripts/zigux/validate-phase3-rbtree-interop-survey.py` keeps this dedicated survey note, the broader `Documentation/zigux/phase3-roadmap-gap-survey.md` note, and the repo-backed evidence paths aligned",
    "`python3 scripts/zigux/validate-phase3.py --slug abi` keeps that dedicated `rbtree` gap visible inside the shared Phase 3 ABI validation packet instead of leaving it as prose-only context",
    "`make -C zigux phase3-validate` remains the shared wrapper entrypoint for the broader bounded ABI packet, so this survey stays reviewable through the same published Phase 3 gate",
    "no curated `rbtree` record in `include/zigux/abi.h`",
    "no matching shared `zigux/bindings/abi.zig` layout type for a Phase 3 `rbtree` boundary packet",
    "no shared Phase 3 ABI replay path for that `rbtree` root view that no longer depends on `include/zigux/rbtree.h` and `zigux/bindings/rbtree.zig`",
    "one curated read-mostly ABI record in the shared packet",
    "one matching shared Zig binding shape",
    "one shared ABI replay path that no longer depends on the dedicated `rbtree` header and binding include path",
    "`include/zigux/rbtree.h` and `zigux/bindings/rbtree.zig` now expose direct constructor, validation, and canonicalization helpers for that dedicated root-view packet",
    "`zigux/helpers/rbtree_root_view.zig` now adds a reusable constructor and canonicalization helper around the dedicated `RootView` binding so later shared-packet work can reuse one explicit flag-policy path",
)

REQUIRED_REPO_PATHS = (
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase3-rbtree-slice.md",
    "Documentation/zigux/phase3-roadmap-gap-survey.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "lib/rbtree.zig",
    "tools/lib/rbtree.zig",
    "include/zigux/rbtree.h",
    "zigux/bindings/rbtree.zig",
    "zigux/helpers/rbtree_view.zig",
    "zigux/helpers/rbtree_root_view.zig",
    "zigux/tests/phase3_rbtree_survey.zig",
    "zigux/tests/phase3_rbtree_root_view_survey.zig",
    "zigux/tests/phase3_rbtree_manifest.json",
    "zigux/tests/phase3_rbtree_dump.zig",
    "zigux/tests/fixtures/phase3_rbtree/expected.json",
    "zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c",
    "zigux/tests/phase3_rbtree_shared_contract.zig",
    "zigux/tests/phase3_abi.zig",
    "zigux/tests/phase3_abi_dump.zig",
    "zigux/tests/fixtures/phase3_abi/expected.json",
    "zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_survey.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
    SHARED_LIFT_CHECK_REL,
    ABI_MANIFEST_REL,
)

REQUIRED_ROADMAP_GAP_MARKERS = (
    "PHASE3_CURRENT_RBTREE_STATUS=phase3-dedicated-rbtree-boundary-exists-shared-abi-lift-still-missing",
    "PHASE3_CURRENT_SHARED_RBTREE_REPLAY=zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c,zigux/tests/fixtures/phase3_abi/expected.json",
    "PHASE3_INTEROP_GAP=shared-phase3-abi-rbtree-lift-still-missing",
    "PHASE3_NEXT_BOUNDED_STEP=shared-abi-rbtree-root-view-before-more-chrdev-growth",
)

REQUIRED_SLICE_MARKERS = (
    "PHASE3_RBTREE_DEDICATED_BOUNDARY_PARITY=zigux/tests/fixtures/phase3_rbtree/expected.json,zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c",
    "PHASE3_RBTREE_SHARED_BOUNDARY_STATUS=shared-parity-replay-present-shared-root-view-lift-still-missing",
    "PHASE3_RBTREE_SHARED_BOUNDARY_GAP=shared-abi-root-view-lift-still-missing",
    "PHASE3_RBTREE_SHARED_BOUNDARY_GUARDS=scripts/zigux/check-phase3-abi-layout-packet.py,scripts/zigux/check-phase3-rbtree-shared-lift-contract.py",
)

REQUIRED_SLICE_SNIPPETS = (
    "This slice already carries:",
    "a dedicated `rbtree` root-view record in `include/zigux/rbtree.h` and `zigux/bindings/rbtree.zig`",
    "direct constructor, validation, and canonicalization helpers on both the dedicated C header and Zig binding paths",
    "a dedicated C-vs-Zig parity replay in `zigux/tests/fixtures/phase3_rbtree/expected.json` and `zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c`",
    "a shared Phase 3 ABI parity replay that still reuses the dedicated `rbtree` header and Zig binding in `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, and `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c`",
    "This slice does not yet claim:",
    "a shared `rbtree` record in `include/zigux/abi.h` and `zigux/bindings/abi.zig`",
    "a shared Phase 3 ABI root-view implementation that no longer depends on `include/zigux/rbtree.h` and `zigux/bindings/rbtree.zig`",
    "The remaining honest Phase 3 `rbtree` gap after this step is the shared ABI lift, not the absence of a dedicated boundary packet.",
    "one shared ABI replay path that no longer depends on the dedicated `rbtree` header and binding include path",
)

RBTREE_FREE_BOUNDARY_PATHS = (
    "include/zigux/abi.h",
    "zigux/bindings/abi.zig",
)

REQUIRED_SHARED_LIFT_CHECK_SNIPPETS = (
    "PHASE3_RBTREE_SHARED_LIFT_CONTRACT=fail",
    "PHASE3_RBTREE_SHARED_LAYOUT_CONTRACT=zigux_rbtree_root_view-reused-unchanged-in-shared-phase3-abi-packet",
    "PHASE3_RBTREE_SHARED_CONSTANT_CONTRACT=root_flag_empty,root_flag_cached,root_flag_leftmost_valid",
    "Documentation/zigux/phase3-rbtree-interop-survey.md",
    "Documentation/zigux/phase3-roadmap-gap-survey.md",
    "Documentation/zigux/phase3-rbtree-slice.md",
    "zigux/tests/phase3_rbtree_shared_contract.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
)

REQUIRED_ABI_MANIFEST_ENTRIES = (
    '"scripts/zigux/check-phase3-rbtree-shared-lift-contract.py"',
    '"Documentation/zigux/phase3-rbtree-interop-survey.md"',
    '"Documentation/zigux/phase3-rbtree-slice.md"',
    '"zigux/tests/phase3_rbtree_shared_contract.zig"',
    '"zigux/tests/phase3_rbtree_dump.zig"',
    '"zigux/tests/fixtures/phase3_rbtree/expected.json"',
    '"zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c"',
)


def _read_text(root: Path, rel: str, issues: list[str]) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        issues.append(f"missing_file:{rel}")
        return ""


def validate(root: Path) -> list[str]:
    issues: list[str] = []
    survey = _read_text(root, SURVEY_REL, issues)
    roadmap_gap = _read_text(root, ROADMAP_GAP_SURVEY_REL, issues)
    slice_text = _read_text(root, SLICE_REL, issues)
    shared_lift_check = _read_text(root, SHARED_LIFT_CHECK_REL, issues)
    abi_manifest = _read_text(root, ABI_MANIFEST_REL, issues)

    if survey:
        for marker in REQUIRED_SURVEY_MARKERS:
            if marker not in survey:
                issues.append(f"missing_survey_marker:{marker}")
        for snippet in REQUIRED_SURVEY_SNIPPETS:
            if snippet not in survey:
                issues.append(f"missing_survey_snippet:{snippet}")

    for rel in REQUIRED_REPO_PATHS:
        if not (root / rel).exists():
            issues.append(f"missing_repo_path:{rel}")

    if roadmap_gap:
        for marker in REQUIRED_ROADMAP_GAP_MARKERS:
            if marker not in roadmap_gap:
                issues.append(f"missing_roadmap_gap_marker:{marker}")

    if slice_text:
        for marker in REQUIRED_SLICE_MARKERS:
            if marker not in slice_text:
                issues.append(f"missing_slice_marker:{marker}")
        for snippet in REQUIRED_SLICE_SNIPPETS:
            if snippet not in slice_text:
                issues.append(f"missing_slice_snippet:{snippet}")

    if shared_lift_check:
        for snippet in REQUIRED_SHARED_LIFT_CHECK_SNIPPETS:
            if snippet not in shared_lift_check:
                issues.append(f"missing_shared_lift_check_snippet:{snippet}")

    if abi_manifest:
        for entry in REQUIRED_ABI_MANIFEST_ENTRIES:
            if entry not in abi_manifest:
                issues.append("missing_abi_manifest_entry:" + entry.strip('"'))

    for rel in RBTREE_FREE_BOUNDARY_PATHS:
        text = _read_text(root, rel, issues)
        if text and "rbtree" in text.lower():
            issues.append(f"boundary_mentions_rbtree:{rel}")

    return issues


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_rbtree_interop_") as tmp_dir_str:
        root = Path(tmp_dir_str)
        (root / "Documentation" / "zigux").mkdir(parents=True, exist_ok=True)
        (root / "zigux" / "tests").mkdir(parents=True, exist_ok=True)
        (root / "zigux" / "tests" / "fixtures" / "phase3_rbtree").mkdir(parents=True, exist_ok=True)
        (root / "zigux" / "tests" / "fixtures" / "phase3_abi").mkdir(parents=True, exist_ok=True)
        (root / "zigux" / "bindings").mkdir(parents=True, exist_ok=True)
        (root / "zigux" / "helpers").mkdir(parents=True, exist_ok=True)
        (root / "include" / "zigux").mkdir(parents=True, exist_ok=True)
        (root / "lib").mkdir(parents=True, exist_ok=True)
        (root / "tools" / "lib").mkdir(parents=True, exist_ok=True)

        survey_path = root / SURVEY_REL
        survey_path.write_text(
            "\n".join((*REQUIRED_SURVEY_MARKERS, *REQUIRED_SURVEY_SNIPPETS)) + "\n",
            encoding="utf-8",
        )
        roadmap_gap_path = root / ROADMAP_GAP_SURVEY_REL
        roadmap_gap_path.write_text("\n".join(REQUIRED_ROADMAP_GAP_MARKERS) + "\n", encoding="utf-8")
        slice_path = root / SLICE_REL
        slice_path.write_text(
            "\n".join((*REQUIRED_SLICE_MARKERS, *REQUIRED_SLICE_SNIPPETS)) + "\n",
            encoding="utf-8",
        )
        shared_lift_check_path = root / SHARED_LIFT_CHECK_REL
        shared_lift_check_path.parent.mkdir(parents=True, exist_ok=True)
        shared_lift_check_path.write_text(
            "\n".join(REQUIRED_SHARED_LIFT_CHECK_SNIPPETS) + "\n",
            encoding="utf-8",
        )
        abi_manifest_path = root / ABI_MANIFEST_REL
        abi_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        abi_manifest_path.write_text(
            "\n".join(REQUIRED_ABI_MANIFEST_ENTRIES) + "\n",
            encoding="utf-8",
        )

        for rel in REQUIRED_REPO_PATHS:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                path.write_text("// ok\n", encoding="utf-8")

        for rel in RBTREE_FREE_BOUNDARY_PATHS:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("// ok\n", encoding="utf-8")

        assert validate(root) == []

        survey_path.write_text(REQUIRED_SURVEY_MARKERS[0] + "\n", encoding="utf-8")
        issues = validate(root)
        assert any(issue.startswith("missing_survey_marker:") for issue in issues)
        assert any(issue.startswith("missing_survey_snippet:") for issue in issues)
        survey_path.write_text(
            "\n".join((*REQUIRED_SURVEY_MARKERS, *REQUIRED_SURVEY_SNIPPETS)) + "\n",
            encoding="utf-8",
        )

        roadmap_gap_path.write_text(REQUIRED_ROADMAP_GAP_MARKERS[0] + "\n", encoding="utf-8")
        issues = validate(root)
        assert any(issue.startswith("missing_roadmap_gap_marker:") for issue in issues)
        roadmap_gap_path.write_text("\n".join(REQUIRED_ROADMAP_GAP_MARKERS) + "\n", encoding="utf-8")

        slice_path.write_text(REQUIRED_SLICE_MARKERS[0] + "\n", encoding="utf-8")
        issues = validate(root)
        assert any(issue.startswith("missing_slice_marker:") for issue in issues)
        assert any(issue.startswith("missing_slice_snippet:") for issue in issues)
        slice_path.write_text(
            "\n".join((*REQUIRED_SLICE_MARKERS, *REQUIRED_SLICE_SNIPPETS)) + "\n",
            encoding="utf-8",
        )

        missing_repo_rel = REQUIRED_REPO_PATHS[-1]
        missing_repo_path = root / missing_repo_rel
        missing_repo_path.unlink()
        issues = validate(root)
        assert f"missing_repo_path:{missing_repo_rel}" in issues
        missing_repo_path.write_text("// ok\n", encoding="utf-8")

        shared_lift_check_path.write_text(REQUIRED_SHARED_LIFT_CHECK_SNIPPETS[0] + "\n", encoding="utf-8")
        issues = validate(root)
        assert any(issue.startswith("missing_shared_lift_check_snippet:") for issue in issues)
        shared_lift_check_path.write_text(
            "\n".join(REQUIRED_SHARED_LIFT_CHECK_SNIPPETS) + "\n",
            encoding="utf-8",
        )

        abi_manifest_path.write_text(REQUIRED_ABI_MANIFEST_ENTRIES[0] + "\n", encoding="utf-8")
        issues = validate(root)
        assert any(issue.startswith("missing_abi_manifest_entry:") for issue in issues)
        abi_manifest_path.write_text(
            "\n".join(REQUIRED_ABI_MANIFEST_ENTRIES) + "\n",
            encoding="utf-8",
        )

        for rel in RBTREE_FREE_BOUNDARY_PATHS:
            for clean_rel in RBTREE_FREE_BOUNDARY_PATHS:
                boundary_path = root / clean_rel
                boundary_path.write_text("// ok\n", encoding="utf-8")
            boundary = root / rel
            boundary.write_text("// rbtree drift\n", encoding="utf-8")
            issues = validate(root)
            assert f"boundary_mentions_rbtree:{rel}" in issues

    print("PHASE3_RBTREE_INTEROP_SURVEY_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check that the dedicated Phase 3 rbtree interop survey stays aligned with the live repo.")
    parser.add_argument("--self-test", action="store_true", help="Run isolated checker tests without reading the full repo.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate(ROOT)
    if issues:
        print("PHASE3_RBTREE_INTEROP_SURVEY=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE3_RBTREE_INTEROP_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
