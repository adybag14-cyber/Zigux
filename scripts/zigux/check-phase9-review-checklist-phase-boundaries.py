#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/review-checklist.md").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
PHASE9_GAP_SURVEY_PATH = "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
LOADER_GAP_MANIFEST_PATH = "zigux/tests/runtime_loader_gap_manifest.json"

PHASE9_SHARED_PACKET_MARKER = "if the change touches the shared Phase 9 runtime-loader packet"
PHASE8_EXEC_CMD_MARKER = "`tools/lib/subcmd/exec-cmd.zig`"
PHASE8_HELP_MARKER = "`tools/lib/subcmd/help.zig`"
PHASE8_BOUNDARY_MARKER = "stay explicit as Phase 8 tooling boundaries"
DEPMOD_BOUNDARY_MARKER = "the shared module-metadata and depmod-publication boundary still stays blocked"
PHASE2_CONF_BRIDGE_MARKER = "`scripts/zigux/kconfig/conf_bridge.zig`"
PHASE2_CONFDATA_BRIDGE_MARKER = "`scripts/zigux/kconfig/confdata_bridge.zig`"
PHASE3_EXPORTS_MARKER = "`rust/exports.c`"
PHASE3_EXPORT_SHIM_MARKER = "`zigux/kernel/export_shim.zig`"
PHASE2_BOUNDARY_MARKER = "remain Phase 2 config-surface bridge references"
PHASE3_BOUNDARY_MARKER = "remain Phase 3 export-boundary references rather than runtime-pilot evidence"
PHASE9_GAP_SURVEY_CHECKER_MARKER = "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py` checker now"
PHASE9_GAP_SURVEY_MANIFEST_MARKER = "`review_checklist_cross_phase_non_owner_boundary_present: true` instead"
LOADER_GAP_MANIFEST_FLAG_MARKER = '"review_checklist_cross_phase_non_owner_boundary_present": true'
LOADER_GAP_MANIFEST_CHECKER_SURFACE_MARKER = '"surface": "scripts/zigux/check-phase9-review-checklist-phase-boundaries.py"'
LOADER_GAP_MANIFEST_CHECKER_KIND_MARKER = '"kind": "shared_review_checklist_checker"'

REQUIRED_FILES = [
    REVIEW_CHECKLIST_PATH,
    PHASE9_GAP_SURVEY_PATH,
    LOADER_GAP_MANIFEST_PATH,
]

REQUIRED_MARKERS = {
    REVIEW_CHECKLIST_PATH: [
        PHASE9_SHARED_PACKET_MARKER,
        PHASE8_EXEC_CMD_MARKER,
        PHASE8_HELP_MARKER,
        PHASE8_BOUNDARY_MARKER,
        DEPMOD_BOUNDARY_MARKER,
        PHASE2_CONF_BRIDGE_MARKER,
        PHASE2_CONFDATA_BRIDGE_MARKER,
        PHASE3_EXPORTS_MARKER,
        PHASE3_EXPORT_SHIM_MARKER,
        PHASE2_BOUNDARY_MARKER,
        PHASE3_BOUNDARY_MARKER,
    ],
    PHASE9_GAP_SURVEY_PATH: [
        PHASE9_GAP_SURVEY_CHECKER_MARKER,
        PHASE9_GAP_SURVEY_MANIFEST_MARKER,
    ],
    LOADER_GAP_MANIFEST_PATH: [
        LOADER_GAP_MANIFEST_FLAG_MARKER,
        LOADER_GAP_MANIFEST_CHECKER_SURFACE_MARKER,
        LOADER_GAP_MANIFEST_CHECKER_KIND_MARKER,
    ],
}

SELF_TEST_REMOVALS = [
    (REVIEW_CHECKLIST_PATH, PHASE9_SHARED_PACKET_MARKER),
    (REVIEW_CHECKLIST_PATH, PHASE8_EXEC_CMD_MARKER),
    (REVIEW_CHECKLIST_PATH, PHASE8_HELP_MARKER),
    (REVIEW_CHECKLIST_PATH, PHASE8_BOUNDARY_MARKER),
    (REVIEW_CHECKLIST_PATH, DEPMOD_BOUNDARY_MARKER),
    (REVIEW_CHECKLIST_PATH, PHASE2_CONF_BRIDGE_MARKER),
    (REVIEW_CHECKLIST_PATH, PHASE2_CONFDATA_BRIDGE_MARKER),
    (REVIEW_CHECKLIST_PATH, PHASE3_EXPORTS_MARKER),
    (REVIEW_CHECKLIST_PATH, PHASE3_EXPORT_SHIM_MARKER),
    (REVIEW_CHECKLIST_PATH, PHASE2_BOUNDARY_MARKER),
    (REVIEW_CHECKLIST_PATH, PHASE3_BOUNDARY_MARKER),
    (PHASE9_GAP_SURVEY_PATH, PHASE9_GAP_SURVEY_CHECKER_MARKER),
    (PHASE9_GAP_SURVEY_PATH, PHASE9_GAP_SURVEY_MANIFEST_MARKER),
    (LOADER_GAP_MANIFEST_PATH, LOADER_GAP_MANIFEST_FLAG_MARKER),
    (LOADER_GAP_MANIFEST_PATH, LOADER_GAP_MANIFEST_CHECKER_SURFACE_MARKER),
    (LOADER_GAP_MANIFEST_PATH, LOADER_GAP_MANIFEST_CHECKER_KIND_MARKER),
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    return failures


def build_review_checklist_text() -> str:
    return (
        "# Zigux Review Checklist\n\n"
        f"- {PHASE9_SHARED_PACKET_MARKER}\n"
        "- the shared module-metadata and depmod-publication boundary still stays blocked so `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root, and `depmod` script or manifest state remain review-only boundary references rather than shipped publication surfaces.\n"
        f"- keep the older Phase 8 command and environment cue owners out of the packet so {PHASE8_EXEC_CMD_MARKER} and {PHASE8_HELP_MARKER} {PHASE8_BOUNDARY_MARKER}.\n"
        "- the shared Phase 9 reminder should also keep the older cross-phase non-owner boundaries explicit:\n"
        f"  {PHASE2_CONF_BRIDGE_MARKER} and {PHASE2_CONFDATA_BRIDGE_MARKER} {PHASE2_BOUNDARY_MARKER}, while\n"
        f"  {PHASE3_EXPORTS_MARKER} and {PHASE3_EXPORT_SHIM_MARKER} {PHASE3_BOUNDARY_MARKER}.\n"
    )


def build_gap_survey_text() -> str:
    return (
        "# Phase 9 Runtime Loader Gap Survey\n\n"
        f"- The dedicated {PHASE9_GAP_SURVEY_CHECKER_MARKER} fail-closes that cross-phase non-owner reminder directly.\n"
        "- `zigux/tests/runtime_loader_gap_manifest.json` now records\n"
        f"  {PHASE9_GAP_SURVEY_MANIFEST_MARKER} of leaving that reviewer-facing follow-through open.\n"
    )


def build_manifest_text() -> str:
    return (
        "{\n"
        "  \"current_repo_reality\": {\n"
        f"    {LOADER_GAP_MANIFEST_FLAG_MARKER}\n"
        "  },\n"
        "  \"delivery_evidence_catalog\": [\n"
        "    {\n"
        f"      {LOADER_GAP_MANIFEST_CHECKER_SURFACE_MARKER},\n"
        f"      {LOADER_GAP_MANIFEST_CHECKER_KIND_MARKER}\n"
        "    }\n"
        "  ]\n"
        "}\n"
    )


def build_fixture_tree(root: Path) -> None:
    write_text(root / REVIEW_CHECKLIST_PATH, build_review_checklist_text())
    write_text(root / PHASE9_GAP_SURVEY_PATH, build_gap_survey_text())
    write_text(root / LOADER_GAP_MANIFEST_PATH, build_manifest_text())


def remove_once(root: Path, rel_path: str, marker: str) -> None:
    path = root / rel_path
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(marker, "", 1), encoding="utf-8")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-review-checklist-boundaries-"))
    try:
        build_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, marker in SELF_TEST_REMOVALS:
            build_fixture_tree(base)
            remove_once(base, rel_path, marker)
            expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in REQUIRED_FILES:
            build_fixture_tree(base)
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 9 review checklist, gap-survey note, and packet manifest keep the blocked publication boundary plus the older Phase 8, Phase 2, and Phase 3 non-owner boundaries explicit."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in checker self-test and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_ERROR={failure}")
        return 1

    required_marker_count = sum(len(markers) for markers in REQUIRED_MARKERS.values())
    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_REQUIRED_MARKER_COUNT={required_marker_count}")
    print("PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
