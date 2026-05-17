#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()
SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
DOCS_README_PATH = "Documentation/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / SEQUENCING_PATH).exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

SEQUENCING_PATH_MARKER = "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`"
REVIEW_CHECKLIST_PATH_MARKER = "`Documentation/zigux/review-checklist.md`"
SCRIPTS_README_PATH_MARKER = "`scripts/zigux/README.md`"
CHECKLIST_BOUNDARY_CHECKER_MARKER = "`scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`"
TRACE_EVENTS_PACKET_CHECKER_MARKER = "`scripts/zigux/check-phase9-trace-events-runtime-packet.py`"
TESTS_README_MARKER = "`zigux/tests/README.md`"
TRACE_EVENTS_SAMPLE_MARKER = "`samples/zigux/runtime_trace_events.zig`"
UNREGISTERED_GATE_MARKER = "`samples/zigux/runtime_trace_events_unregistered_gate.zig`"
SELFTEST_HOOK_MARKER = "`.provides_selftest_hook = true`"
LIFECYCLE_MARKER = "initialized, selftest_complete, and exited lifecycle tracking"
ABSENT_SHARED_LOADER_MARKER = "does not currently expose the broader shared runtime-loader packet"
ABSENT_PHASE9_BUILD_MARKER = "`zigux/tests/phase9_build.zig`"
ABSENT_RUNTIME_TEST_FAMILY_MARKER = "shared `zigux/tests/runtime_*` replay family"
ABSENT_RUNTIME_LOADER_KERNEL_MARKER = "`zigux/kernel/runtime_loader.zig`"
ABSENT_RUNTIME_LOADER_CONTRACT_MARKER = "`zigux/kernel/runtime_loader_contract.zig`"
ABSENT_MAKEFILE_MARKER = "`zigux/Makefile`"
ABSENT_WORKFLOW_MARKER = "`.github/workflows/zigux-bootstrap.yml`"
ABSENT_LOADER_SCAFFOLD_MARKER = "`samples/zigux/runtime_*_loader.zig` scaffolds"
PHASE2_CONF_BRIDGE_MARKER = "`scripts/zigux/kconfig/conf_bridge.zig`"
PHASE2_CONFDATA_BRIDGE_MARKER = "`scripts/zigux/kconfig/confdata_bridge.zig`"
PHASE3_EXPORTS_MARKER = "`rust/exports.c`"
PHASE3_EXPORT_SHIM_MARKER = "`zigux/kernel/export_shim.zig`"
BITMAP_BACKLOG_MARKER = "runtime bitmap family stays framed as backlog-only Phase 9 support material"

DOCS_README_REQUIRED_MARKERS = [
    SEQUENCING_PATH_MARKER,
    REVIEW_CHECKLIST_PATH_MARKER,
    CHECKLIST_BOUNDARY_CHECKER_MARKER,
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    TESTS_README_MARKER,
    TRACE_EVENTS_SAMPLE_MARKER,
    UNREGISTERED_GATE_MARKER,
    SELFTEST_HOOK_MARKER,
    LIFECYCLE_MARKER,
    ABSENT_SHARED_LOADER_MARKER,
    ABSENT_PHASE9_BUILD_MARKER,
    ABSENT_RUNTIME_TEST_FAMILY_MARKER,
    ABSENT_RUNTIME_LOADER_KERNEL_MARKER,
    ABSENT_RUNTIME_LOADER_CONTRACT_MARKER,
    ABSENT_MAKEFILE_MARKER,
    ABSENT_WORKFLOW_MARKER,
    ABSENT_LOADER_SCAFFOLD_MARKER,
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    BITMAP_BACKLOG_MARKER,
]

REVIEW_CHECKLIST_REQUIRED_MARKERS = [
    SEQUENCING_PATH_MARKER,
    REVIEW_CHECKLIST_PATH_MARKER,
    CHECKLIST_BOUNDARY_CHECKER_MARKER,
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    TESTS_README_MARKER,
    TRACE_EVENTS_SAMPLE_MARKER,
    UNREGISTERED_GATE_MARKER,
    SELFTEST_HOOK_MARKER,
    LIFECYCLE_MARKER,
    ABSENT_SHARED_LOADER_MARKER,
    ABSENT_PHASE9_BUILD_MARKER,
    ABSENT_RUNTIME_TEST_FAMILY_MARKER,
    ABSENT_RUNTIME_LOADER_KERNEL_MARKER,
    ABSENT_RUNTIME_LOADER_CONTRACT_MARKER,
    ABSENT_MAKEFILE_MARKER,
    ABSENT_WORKFLOW_MARKER,
    ABSENT_LOADER_SCAFFOLD_MARKER,
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
    BITMAP_BACKLOG_MARKER,
]

SCRIPTS_README_REQUIRED_MARKERS = [
    SEQUENCING_PATH_MARKER,
    REVIEW_CHECKLIST_PATH_MARKER,
    CHECKLIST_BOUNDARY_CHECKER_MARKER,
    TRACE_EVENTS_PACKET_CHECKER_MARKER,
    TESTS_README_MARKER,
    TRACE_EVENTS_SAMPLE_MARKER,
    UNREGISTERED_GATE_MARKER,
    SELFTEST_HOOK_MARKER,
    LIFECYCLE_MARKER,
    ABSENT_PHASE9_BUILD_MARKER,
    ABSENT_RUNTIME_TEST_FAMILY_MARKER,
    ABSENT_RUNTIME_LOADER_KERNEL_MARKER,
    ABSENT_RUNTIME_LOADER_CONTRACT_MARKER,
    ABSENT_MAKEFILE_MARKER,
    ABSENT_WORKFLOW_MARKER,
    ABSENT_LOADER_SCAFFOLD_MARKER,
    PHASE2_CONF_BRIDGE_MARKER,
    PHASE2_CONFDATA_BRIDGE_MARKER,
    PHASE3_EXPORTS_MARKER,
    PHASE3_EXPORT_SHIM_MARKER,
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    required = [
        SEQUENCING_PATH,
        DOCS_README_PATH,
        REVIEW_CHECKLIST_PATH,
        SCRIPTS_README_PATH,
    ]
    for rel_path in required:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    for rel_path, markers in [
        (DOCS_README_PATH, DOCS_README_REQUIRED_MARKERS),
        (REVIEW_CHECKLIST_PATH, REVIEW_CHECKLIST_REQUIRED_MARKERS),
        (SCRIPTS_README_PATH, SCRIPTS_README_REQUIRED_MARKERS),
    ]:
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def build_sequencing_fixture_text() -> str:
    return f"""# Phase 9 Runtime Pilot Lane Sequencing

Current `master` keeps a narrow surviving runtime-pilot packet.

- surviving direct runtime-module sample: {TRACE_EVENTS_SAMPLE_MARKER}
- surviving fail-closed runtime companion: {UNREGISTERED_GATE_MARKER}
- surviving runtime-module evidence inside that direct sample: {SELFTEST_HOOK_MARKER} together with {LIFECYCLE_MARKER}

Current `master` {ABSENT_SHARED_LOADER_MARKER}.
Fresh repo-first rereads did not find {ABSENT_PHASE9_BUILD_MARKER}, the {ABSENT_RUNTIME_TEST_FAMILY_MARKER}, {ABSENT_RUNTIME_LOADER_KERNEL_MARKER}, {ABSENT_RUNTIME_LOADER_CONTRACT_MARKER}, {ABSENT_MAKEFILE_MARKER}, {ABSENT_WORKFLOW_MARKER}, or the older {ABSENT_LOADER_SCAFFOLD_MARKER} on `master`.
"""


def build_docs_readme_fixture_text() -> str:
    return f"""# Zigux Documentation

Phase 9 notes - {SEQUENCING_PATH_MARKER} - {REVIEW_CHECKLIST_PATH_MARKER} - {CHECKLIST_BOUNDARY_CHECKER_MARKER} - {TRACE_EVENTS_PACKET_CHECKER_MARKER} - {TESTS_README_MARKER} - {TRACE_EVENTS_SAMPLE_MARKER} - {UNREGISTERED_GATE_MARKER} now keep the current narrow runtime-pilot packet reviewable from the docs root: the surviving direct runtime-module sample still exposes {SELFTEST_HOOK_MARKER} together with {LIFECYCLE_MARKER}, while the shipped unregistered-gate companion keeps unregistered function-thread failures fail-closed, and current `master` {ABSENT_SHARED_LOADER_MARKER} that earlier reminder surfaces described.
  * the same shared Phase 9 summary should keep the older non-owner boundaries explicit: {PHASE2_CONF_BRIDGE_MARKER} and {PHASE2_CONFDATA_BRIDGE_MARKER} remain Phase 2 config-surface bridge references, while {PHASE3_EXPORTS_MARKER} and {PHASE3_EXPORT_SHIM_MARKER} remain Phase 3 export-boundary references rather than runtime-pilot evidence.
  * the current bounded Phase 9 decision is to keep reminder surfaces truthful one at a time: do not present {ABSENT_PHASE9_BUILD_MARKER}, the {ABSENT_RUNTIME_TEST_FAMILY_MARKER}, {ABSENT_RUNTIME_LOADER_KERNEL_MARKER}, {ABSENT_RUNTIME_LOADER_CONTRACT_MARKER}, {ABSENT_MAKEFILE_MARKER}, {ABSENT_WORKFLOW_MARKER}, or the older {ABSENT_LOADER_SCAFFOLD_MARKER} as shipped current-`master` evidence unless a fresh repo reread proves they have returned.
Current `master` still ships no standalone `samples/zigux/*bitmap*` Phase 5 reference sample, so reviewers should keep direct bitmap helper reviewability under `tools/lib/bitmap.zig`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `Documentation/zigux/phase4-reversible-delivery-evidence.md`. Keep the broader {BITMAP_BACKLOG_MARKER} unless a fresh repo reread proves those surfaces have actually returned on current `master`.
"""


def build_review_checklist_fixture_text() -> str:
    return f"""# Zigux Review Checklist

  * if the change touches the shared Phase 5 sample packet, do the docs still say clearly that there is no standalone `samples/zigux/*bitmap*` reference sample and that direct bitmap helper reviewability remains under `tools/lib/bitmap.zig`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `Documentation/zigux/phase4-reversible-delivery-evidence.md`, while the separate {BITMAP_BACKLOG_MARKER} in `samples/zigux/README.md`, `Documentation/zigux/README.md`, and {REVIEW_CHECKLIST_PATH_MARKER} unless a fresh repo reread proves `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, {ABSENT_RUNTIME_LOADER_KERNEL_MARKER}, {ABSENT_RUNTIME_LOADER_CONTRACT_MARKER}, and {ABSENT_PHASE9_BUILD_MARKER} have returned on current `master`, rather than the four shipped Phase 5 samples?
  * if the change touches the shared Phase 9 runtime-pilot packet, does {SEQUENCING_PATH_MARKER} remain the owner of the exact repo-reality posture, with {REVIEW_CHECKLIST_PATH_MARKER}, {CHECKLIST_BOUNDARY_CHECKER_MARKER}, {TRACE_EVENTS_PACKET_CHECKER_MARKER}, {TESTS_README_MARKER}, and the surviving direct runtime-module sample {TRACE_EVENTS_SAMPLE_MARKER} all keeping the same narrow current-`master` packet explicit: {SELFTEST_HOOK_MARKER} together with {LIFECYCLE_MARKER}, plus the companion {UNREGISTERED_GATE_MARKER} reminder that unregistered function-thread failures fail-closed? Do the shared reminders also keep saying clearly that current `master` {ABSENT_SHARED_LOADER_MARKER}, so {ABSENT_PHASE9_BUILD_MARKER}, the {ABSENT_RUNTIME_TEST_FAMILY_MARKER}, {ABSENT_RUNTIME_LOADER_KERNEL_MARKER}, {ABSENT_RUNTIME_LOADER_CONTRACT_MARKER}, {ABSENT_MAKEFILE_MARKER}, {ABSENT_WORKFLOW_MARKER}, and the older {ABSENT_LOADER_SCAFFOLD_MARKER} stay absent backlog references unless a fresh repo reread proves they have returned, while {PHASE2_CONF_BRIDGE_MARKER} and {PHASE2_CONFDATA_BRIDGE_MARKER} remain Phase 2 config-surface bridge references and {PHASE3_EXPORTS_MARKER} and {PHASE3_EXPORT_SHIM_MARKER} remain Phase 3 export-boundary references rather than runtime-pilot evidence?
"""


def build_scripts_readme_fixture_text() -> str:
    return f"""# scripts/zigux

## Phase 9

- Phase 9 flow - the current shared runtime-pilot packet is narrow and review-first: {SEQUENCING_PATH_MARKER}, {REVIEW_CHECKLIST_PATH_MARKER}, {CHECKLIST_BOUNDARY_CHECKER_MARKER}, {TRACE_EVENTS_PACKET_CHECKER_MARKER}, {TESTS_README_MARKER}, {TRACE_EVENTS_SAMPLE_MARKER}, and {UNREGISTERED_GATE_MARKER} keep the live reminder surface honest from the scripts root
- `python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test`, `python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test`, `python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py`, and `python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py` replay the shipped bounded Phase 9 reminder checks
- {TRACE_EVENTS_SAMPLE_MARKER} remains the surviving direct runtime-module sample and still exposes {SELFTEST_HOOK_MARKER} together with {LIFECYCLE_MARKER}, while {UNREGISTERED_GATE_MARKER} keeps the same narrow packet's unregistered function-thread failures fail-closed, so keep that exact selftest-hook, lifecycle, and fail-closed companion packet explicit instead of rebuilding a broader runtime family from older route names
- current `master` still does not materialize {ABSENT_PHASE9_BUILD_MARKER}, the {ABSENT_RUNTIME_TEST_FAMILY_MARKER}, {ABSENT_RUNTIME_LOADER_KERNEL_MARKER}, {ABSENT_RUNTIME_LOADER_CONTRACT_MARKER}, {ABSENT_MAKEFILE_MARKER}, {ABSENT_WORKFLOW_MARKER}, or the older {ABSENT_LOADER_SCAFFOLD_MARKER}, so treat those loader, build, kernel, workflow, and sample paths as absent backlog evidence until a fresh reread proves they returned
- keep the older non-owner boundaries explicit here too: {PHASE2_CONF_BRIDGE_MARKER} and {PHASE2_CONFDATA_BRIDGE_MARKER} remain Phase 2 config-surface bridge references, while {PHASE3_EXPORTS_MARKER} and {PHASE3_EXPORT_SHIM_MARKER} remain Phase 3 export-boundary references rather than runtime-pilot evidence
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-shared-owner-map-packet-"))
    try:
        write_text(base / SEQUENCING_PATH, build_sequencing_fixture_text())
        write_text(base / DOCS_README_PATH, build_docs_readme_fixture_text())
        write_text(base / REVIEW_CHECKLIST_PATH, build_review_checklist_fixture_text())
        write_text(base / SCRIPTS_README_PATH, build_scripts_readme_fixture_text())

        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for rel_path, builder, markers in [
            (DOCS_README_PATH, build_docs_readme_fixture_text, DOCS_README_REQUIRED_MARKERS),
            (REVIEW_CHECKLIST_PATH, build_review_checklist_fixture_text, REVIEW_CHECKLIST_REQUIRED_MARKERS),
            (SCRIPTS_README_PATH, build_scripts_readme_fixture_text, SCRIPTS_README_REQUIRED_MARKERS),
        ]:
            for marker in markers:
                write_text(base / SEQUENCING_PATH, build_sequencing_fixture_text())
                write_text(base / DOCS_README_PATH, build_docs_readme_fixture_text())
                write_text(base / REVIEW_CHECKLIST_PATH, build_review_checklist_fixture_text())
                write_text(base / SCRIPTS_README_PATH, build_scripts_readme_fixture_text())
                write_text(base / rel_path, builder().replace(marker, ""))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")

        for rel_path in [
            SEQUENCING_PATH,
            DOCS_README_PATH,
            REVIEW_CHECKLIST_PATH,
            SCRIPTS_README_PATH,
        ]:
            write_text(base / SEQUENCING_PATH, build_sequencing_fixture_text())
            write_text(base / DOCS_README_PATH, build_docs_readme_fixture_text())
            write_text(base / REVIEW_CHECKLIST_PATH, build_review_checklist_fixture_text())
            write_text(base / SCRIPTS_README_PATH, build_scripts_readme_fixture_text())
            (base / rel_path).unlink()
            expect_failure(base, f"missing_file:{rel_path}")

        print("PHASE9_SHARED_OWNER_MAP_PACKET_SELF_TEST=pass")
        print(f"PHASE9_SHARED_OWNER_MAP_PACKET_DOCS_MARKER_COUNT={len(DOCS_README_REQUIRED_MARKERS)}")
        print(f"PHASE9_SHARED_OWNER_MAP_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_CHECKLIST_REQUIRED_MARKERS)}")
        print(f"PHASE9_SHARED_OWNER_MAP_PACKET_SCRIPTS_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PHASE9_SHARED_OWNER_MAP_PACKET=pass")
    print(f"PHASE9_SHARED_OWNER_MAP_PACKET_DOCS_MARKER_COUNT={len(DOCS_README_REQUIRED_MARKERS)}")
    print(f"PHASE9_SHARED_OWNER_MAP_PACKET_REVIEW_MARKER_COUNT={len(REVIEW_CHECKLIST_REQUIRED_MARKERS)}")
    print(f"PHASE9_SHARED_OWNER_MAP_PACKET_SCRIPTS_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())