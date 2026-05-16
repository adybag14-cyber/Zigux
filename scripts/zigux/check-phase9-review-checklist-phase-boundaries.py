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

REQUIRED_MARKERS = [
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
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    checklist_path = root / REVIEW_CHECKLIST_PATH
    if not checklist_path.exists():
        return [f"missing_file:{REVIEW_CHECKLIST_PATH}"]

    checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    for marker in REQUIRED_MARKERS:
        if marker not in checklist:
            failures.append(f"missing_marker:{REVIEW_CHECKLIST_PATH}:{marker}")

    return failures


def build_fixture_text() -> str:
    return (
        "# Zigux Review Checklist\n\n"
        f"- {PHASE9_SHARED_PACKET_MARKER}\n"
        "- the shared module-metadata and depmod-publication boundary still stays blocked so `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root, and `depmod` script or manifest state remain review-only boundary references rather than shipped publication surfaces.\n"
        f"- keep the older Phase 8 command and environment cue owners out of the packet so {PHASE8_EXEC_CMD_MARKER} and {PHASE8_HELP_MARKER} {PHASE8_BOUNDARY_MARKER}.\n"
        "- the shared Phase 9 reminder should also keep the older cross-phase non-owner boundaries explicit:\n"
        f"  {PHASE2_CONF_BRIDGE_MARKER} and {PHASE2_CONFDATA_BRIDGE_MARKER} {PHASE2_BOUNDARY_MARKER}, while\n"
        f"  {PHASE3_EXPORTS_MARKER} and {PHASE3_EXPORT_SHIM_MARKER} {PHASE3_BOUNDARY_MARKER}.\n"
    )


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-review-checklist-boundaries-"))
    try:
        fixture_path = base / REVIEW_CHECKLIST_PATH
        write_text(fixture_path, build_fixture_text())
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in REQUIRED_MARKERS:
            write_text(fixture_path, build_fixture_text().replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{REVIEW_CHECKLIST_PATH}:{marker}")
            write_text(fixture_path, build_fixture_text())

        shutil.rmtree(base / "Documentation", ignore_errors=True)
        expect_failure(base, f"missing_file:{REVIEW_CHECKLIST_PATH}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 9 review checklist keeps the blocked publication boundary plus the older Phase 8, Phase 2, and Phase 3 non-owner boundaries explicit."
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

    print(f"PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES_REQUIRED_MARKER_COUNT={len(REQUIRED_MARKERS)}")
    print("PHASE9_REVIEW_CHECKLIST_PHASE_BOUNDARIES=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
