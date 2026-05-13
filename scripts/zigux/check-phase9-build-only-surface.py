#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/README.md").exists() and (candidate / "zigux/Makefile").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
PHASE9_LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
PHASE9_GAP_SURVEY_NOTE_PATH = "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
README_PATH = "Documentation/zigux/README.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"
RUNTIME_LOADER_PATH = "zigux/kernel/runtime_loader.zig"
RUNTIME_LOADER_CONTRACT_PATH = "zigux/kernel/runtime_loader_contract.zig"
ALLOCATOR_INIT_FLOW_PATH = "zigux/tests/runtime_loader_allocator_init_flow.zig"
LOADER_GAP_MANIFEST_PATH = "zigux/tests/runtime_loader_gap_manifest.json"
LOADER_GAP_SURVEY_PATH = "zigux/tests/runtime_loader_gap_survey.zig"

FREEZE_MAP_TRACE_BOUNDARY_MARKER = (
    "the shared Phase 9 runtime-loader packet stays review-only beside `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`"
)
PREPARED_STATE_LANDED_MARKER = (
    "direct readback now also shows `zigux/tests/runtime_loader_allocator_init_flow.zig` already keeps the prepared-plan drift replay explicit across rejected `requestRuntimeLoad()` calls"
)
GAP_SURVEY_DRIFT_MARKER = (
    "direct readback now also shows `scripts/zigux/README.md` and `zigux/tests/README.md` both keep `zigux/tests/runtime_loader_gap_survey.zig` explicit beside the shared loader-facing packet, so the remaining shared reminder follow-through has narrowed back to reviewer-facing truthfulness around the still-blocked module-metadata and depmod-publication boundary instead of loader-gap inventory sync"
)
GAP_SURVEY_NEXT_STEP_MARKER = (
    "refresh the smallest shipped shared summary that still drifts around the blocked module-metadata and depmod-publication boundary and the stale repo-root loader inventory, starting with `Documentation/zigux/review-checklist.md`, then `Documentation/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` one file at a time."
)
DEP_MOD_BOUNDARY_MARKER = (
    "the shared module-metadata and depmod-publication boundary is still blocked in the live loader packet: `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root, and `depmod` script or manifest state remain review-only boundary references rather than shipped publication surfaces"
)
DOCS_ROOT_DEPMOD_BOUNDARY_MARKER = (
    "`.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, module install-root, and `depmod` script or manifest state stay blocked review-only boundaries"
)
REVIEW_CHECKLIST_TRACE_EVENTS_LOADER_MARKER = (
    "with `samples/zigux/runtime_trace_events_loader.zig` kept explicit as a shipped shared-loader scaffold while `samples/zigux/runtime_trace_events.zig` plus `zigux/tests/runtime_trace_events_manifest.json` remain the sample-only blocked pilot boundary for live runtime substrate and tracepoint-registration execution"
)
REVIEW_CHECKLIST_PHASE8_BOUNDARY_MARKER = (
    "while the older Phase 8 command and environment control cues stay with `tools/lib/subcmd/exec-cmd.zig` and `tools/lib/subcmd/help.zig`"
)
LANE_NOTE_BITMAP_TOP_BIT_SPLIT_MARKER = (
    "`Documentation/zigux/review-checklist.md` now keeps the shared-loader split visible by naming the shipped `phase9-runtime-bitmap-top-bit-tests` step beside `samples/zigux/runtime_bitmap_top_bit_contract.zig`, while the bitmap-local `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig` replay stays with the family packet instead of being flattened into shared loader evidence, and it remains the reviewer-facing surface that also restates the older command and environment ownership boundaries, while the shared `python3 scripts/zigux/check-phase9-build-only-surface.py --self-test` hook stays part of the same loader-owned validation packet"
)
PHASE9_GAP_SURVEY_NOTE_STATUS_MARKER = "PHASE9_SLICE=runtime-loader-gap-survey"
PHASE9_GAP_SURVEY_NOTE_ROUTE_MARKER = "`make -C zigux phase9-runtime-loader-shared-tests`"
PHASE9_GAP_SURVEY_NOTE_BOUNDARY_MARKER = "`depmod` script or manifest state"
LOADER_GAP_MANIFEST_NOTE_SURFACE_MARKER = '"surface": "Documentation/zigux/phase9-runtime-loader-gap-survey.md"'
LOADER_GAP_MANIFEST_ROUTE_MARKER = '"current_honest_gate": "make -C zigux phase9-runtime-loader-shared-tests"'
LOADER_GAP_MANIFEST_BOUNDARY_MARKER = '"id": "runtime-loader-publication-metadata"'
OWNER_MAP_MARKERS = [
    "- `P9-L04`: owns the current runtime atomic64 manifest-backed survey-versus-module-slice packet.",
    "- `P9-L08`: owns the current runtime bitmap manifest, survey note, module-slice note, focused top-bit companion replay, and survey gate packet.",
    "- `P9-L10`: owns the current runtime trace-events manifest, survey note, module-slice note, and survey-gate packet.",
    "- `P9-L13`: owns the current runtime kretprobe manifest-backed loader-plan, survey-gate lifecycle, and tracing proof follow-through.",
]

REQUIRED_FILES = [
    FREEZE_MAP_PATH,
    PHASE9_LANE_SEQUENCING_PATH,
    PHASE9_GAP_SURVEY_NOTE_PATH,
    REVIEW_CHECKLIST_PATH,
    README_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    SAMPLES_README_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
    PHASE9_BUILD_PATH,
    RUNTIME_LOADER_PATH,
    RUNTIME_LOADER_CONTRACT_PATH,
    ALLOCATOR_INIT_FLOW_PATH,
    LOADER_GAP_MANIFEST_PATH,
    LOADER_GAP_SURVEY_PATH,
    "samples/zigux/runtime_atomic64_loader.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_bitmap_top_bit_contract.zig",
    "samples/zigux/runtime_trace_events_loader.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
]

FORBIDDEN_FILES = [
    "scripts/zigux/validate-phase9.py",
    "scripts/zigux/check-phase9-validation-flow.py",
    "scripts/zigux/check-phase9-runtime-loader-commit-alignment.py",
    "scripts/zigux/check-phase9-loader-substrate-plan.py",
]

REQUIRED_MARKERS = {
    FREEZE_MAP_PATH: [
        "kernel/workqueue.c",
        "kernel/trace/ring_buffer.c",
        FREEZE_MAP_TRACE_BOUNDARY_MARKER,
        "`scripts/zigux/check-phase9-build-only-surface.py`",
        "`zigux/tests/phase9_build.zig`",
        "`zigux/kernel/runtime_loader.zig`",
        "`zigux/kernel/runtime_loader_contract.zig`",
    ],
    PHASE9_LANE_SEQUENCING_PATH: [
        PREPARED_STATE_LANDED_MARKER,
        GAP_SURVEY_DRIFT_MARKER,
        GAP_SURVEY_NEXT_STEP_MARKER,
        DEP_MOD_BOUNDARY_MARKER,
        LANE_NOTE_BITMAP_TOP_BIT_SPLIT_MARKER,
        *OWNER_MAP_MARKERS,
        "the shipped `scripts/zigux/check-phase9-build-only-surface.py` guard should still fail closed if this note regresses around either the shared owner split or the blocked module-metadata and depmod-publication boundary markers",
    ],
    PHASE9_GAP_SURVEY_NOTE_PATH: [
        PHASE9_GAP_SURVEY_NOTE_STATUS_MARKER,
        PHASE9_GAP_SURVEY_NOTE_ROUTE_MARKER,
        "There is no dedicated shared `validate-phase9.py`",
        "samples/zigux/runtime_kretprobe_loader.zig",
        PHASE9_GAP_SURVEY_NOTE_BOUNDARY_MARKER,
    ],
    REVIEW_CHECKLIST_PATH: [
        "`scripts/zigux/check-phase9-build-only-surface.py`",
        "without overstating missing shared-loader paths as shipped current-`master` evidence",
        "the owner of the exact shared-loader target list, convenience-target names, and repo-reality blocker posture",
        REVIEW_CHECKLIST_TRACE_EVENTS_LOADER_MARKER,
        REVIEW_CHECKLIST_PHASE8_BOUNDARY_MARKER,
    ],
    README_PATH: [
        "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
        "`scripts/zigux/check-phase9-build-only-surface.py`",
        "`zigux/tests/phase9_build.zig`",
        "`zigux/kernel/runtime_loader.zig`",
        "`zigux/kernel/runtime_loader_contract.zig`",
        "the shared Phase 9 packet is still review-first rather than loadable-runtime-complete",
        DOCS_ROOT_DEPMOD_BOUNDARY_MARKER,
    ],
    SCRIPTS_README_PATH: [
        "Phase 9 flow",
        "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` remains the shared owner map",
        "there is no dedicated shared `validate-phase9.py`",
    ],
    TESTS_README_PATH: [
        "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
        "`zigux/tests/runtime_loader_gap_survey.zig`",
        "`zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`",
    ],
    SAMPLES_README_PATH: [
        "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` remains the shared owner map",
        "the focused `phase9-runtime-loader-shared-tests` step",
        "instead of implying a dedicated `validate-phase9.py` route",
    ],
    MAKEFILE_PATH: [
        "PHONY += phase9-runtime-atomic64-test phase9-runtime-bitmap-top-bit-test phase9-runtime-trace-events-test phase9-runtime-kretprobe-test phase9-runtime-loader-shared-tests phase9-test phase9",
        "phase9-runtime-loader-shared-tests:",
        "$(ZIG) build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
        "phase9-test:",
        "$(PYTHON) scripts/zigux/check-phase9-build-only-surface.py",
        "phase9: phase9-test",
    ],
    WORKFLOW_PATH: [
        "Self-test Phase 9 build-only surface checker",
        "python3 scripts/zigux/check-phase9-build-only-surface.py --self-test",
        "Check Phase 9 build-only surface",
        "python3 scripts/zigux/check-phase9-build-only-surface.py",
        "Run Phase 9 runtime helper tests",
        "make -C zigux phase9",
    ],
    PHASE9_BUILD_PATH: [
        "\"phase9-runtime-loader-shared-tests\"",
        "runtime_loader_gap_survey.zig",
        "runtime_loader_allocator_init_flow.zig",
        "\"phase9-runtime-bitmap-top-bit-tests\"",
        "runtime_bitmap_top_bit_contract.zig",
    ],
    LOADER_GAP_MANIFEST_PATH: [
        '"lane_key": "P9-L18"',
        LOADER_GAP_MANIFEST_NOTE_SURFACE_MARKER,
        '"surface": "zigux/tests/runtime_loader_gap_manifest.json"',
        LOADER_GAP_MANIFEST_ROUTE_MARKER,
        LOADER_GAP_MANIFEST_BOUNDARY_MARKER,
    ],
    LOADER_GAP_SURVEY_PATH: [
        "phase 9 runtime loader gap survey keeps note and manifest aligned with the live shared packet",
        "phase 9 runtime loader gap survey keeps the shared replay routes and no-dedicated-validator boundary explicit",
        "phase 9 runtime loader gap survey keeps rollback and metadata-only trace-events evidence explicit",
        "shared_runtime_loader_files_present",
        "shared_runtime_loader_contract_present",
        "shared_loader_shared_tests_route_present",
        "shared_phase9_bundle_route_present",
        "dedicated_validate_phase9_present",
    ],
}

FORBIDDEN_MARKERS = {
    MAKEFILE_PATH: ["phase9-validate:"],
    WORKFLOW_PATH: ["validate-phase9.py", "check-phase9-loader-substrate-plan.py"],
}


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

    for rel_path in FORBIDDEN_FILES:
        if (root / rel_path).exists():
            failures.append(f"unexpected_file:{rel_path}")

    if failures:
        return failures

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")

    for rel_path, markers in FORBIDDEN_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker in text:
                failures.append(f"forbidden_marker:{rel_path}:{marker}")

    return failures


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    for rel_path in REQUIRED_FILES:
        markers = REQUIRED_MARKERS.get(rel_path)
        if rel_path.endswith(".py"):
            title = Path(rel_path).name
            content = "\n".join([f"# {title}", *(markers or []), ""])
        elif rel_path.endswith(".md") or rel_path.endswith(".json"):
            title = Path(rel_path).name
            content = "\n".join([f"# {title}", *(markers or []), ""])
        else:
            title = Path(rel_path).name
            prefix = f"// {title}"
            content = "\n".join([prefix, *(markers or []), ""])
        write_text(root / rel_path, content)


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-build-only-surface-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        freeze_map_path = base / FREEZE_MAP_PATH
        freeze_map = freeze_map_path.read_text(encoding="utf-8")
        freeze_map_path.write_text(
            freeze_map.replace("`scripts/zigux/check-phase9-build-only-surface.py`", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "missing_marker:Documentation/zigux/freeze-map.md:`scripts/zigux/check-phase9-build-only-surface.py`",
        )

        write_fixture_tree(base)
        lane_note_path = base / PHASE9_LANE_SEQUENCING_PATH
        lane_note = lane_note_path.read_text(encoding="utf-8")
        lane_note_path.write_text(
            lane_note.replace(PREPARED_STATE_LANDED_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"missing_marker:{PHASE9_LANE_SEQUENCING_PATH}:{PREPARED_STATE_LANDED_MARKER}")

        write_fixture_tree(base)
        lane_note_path = base / PHASE9_LANE_SEQUENCING_PATH
        lane_note = lane_note_path.read_text(encoding="utf-8")
        lane_note_path.write_text(
            lane_note.replace(DEP_MOD_BOUNDARY_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"missing_marker:{PHASE9_LANE_SEQUENCING_PATH}:{DEP_MOD_BOUNDARY_MARKER}")

        write_fixture_tree(base)
        lane_note_path = base / PHASE9_LANE_SEQUENCING_PATH
        lane_note = lane_note_path.read_text(encoding="utf-8")
        lane_note_path.write_text(
            lane_note.replace(GAP_SURVEY_DRIFT_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"missing_marker:{PHASE9_LANE_SEQUENCING_PATH}:{GAP_SURVEY_DRIFT_MARKER}")

        write_fixture_tree(base)
        lane_note_path = base / PHASE9_LANE_SEQUENCING_PATH
        lane_note = lane_note_path.read_text(encoding="utf-8")
        lane_note_path.write_text(
            lane_note.replace(GAP_SURVEY_NEXT_STEP_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"missing_marker:{PHASE9_LANE_SEQUENCING_PATH}:{GAP_SURVEY_NEXT_STEP_MARKER}")

        write_fixture_tree(base)
        lane_note_path = base / PHASE9_LANE_SEQUENCING_PATH
        lane_note = lane_note_path.read_text(encoding="utf-8")
        lane_note_path.write_text(
            lane_note.replace(LANE_NOTE_BITMAP_TOP_BIT_SPLIT_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"missing_marker:{PHASE9_LANE_SEQUENCING_PATH}:{LANE_NOTE_BITMAP_TOP_BIT_SPLIT_MARKER}",
        )

        write_fixture_tree(base)
        gap_survey_note_path = base / PHASE9_GAP_SURVEY_NOTE_PATH
        gap_survey_note = gap_survey_note_path.read_text(encoding="utf-8")
        gap_survey_note_path.write_text(
            gap_survey_note.replace(PHASE9_GAP_SURVEY_NOTE_ROUTE_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"missing_marker:{PHASE9_GAP_SURVEY_NOTE_PATH}:{PHASE9_GAP_SURVEY_NOTE_ROUTE_MARKER}")

        write_fixture_tree(base)
        gap_manifest_path = base / LOADER_GAP_MANIFEST_PATH
        gap_manifest = gap_manifest_path.read_text(encoding="utf-8")
        gap_manifest_path.write_text(
            gap_manifest.replace(LOADER_GAP_MANIFEST_ROUTE_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"missing_marker:{LOADER_GAP_MANIFEST_PATH}:{LOADER_GAP_MANIFEST_ROUTE_MARKER}")

        write_fixture_tree(base)
        checklist_path = base / REVIEW_CHECKLIST_PATH
        checklist = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(
            checklist.replace(
                "the owner of the exact shared-loader target list, convenience-target names, and repo-reality blocker posture",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "missing_marker:Documentation/zigux/review-checklist.md:the owner of the exact shared-loader target list, convenience-target names, and repo-reality blocker posture",
        )

        write_fixture_tree(base)
        checklist_path = base / REVIEW_CHECKLIST_PATH
        checklist = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(
            checklist.replace(REVIEW_CHECKLIST_TRACE_EVENTS_LOADER_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"missing_marker:{REVIEW_CHECKLIST_PATH}:{REVIEW_CHECKLIST_TRACE_EVENTS_LOADER_MARKER}",
        )

        write_fixture_tree(base)
        checklist_path = base / REVIEW_CHECKLIST_PATH
        checklist = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(
            checklist.replace(REVIEW_CHECKLIST_PHASE8_BOUNDARY_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"missing_marker:{REVIEW_CHECKLIST_PATH}:{REVIEW_CHECKLIST_PHASE8_BOUNDARY_MARKER}",
        )

        write_fixture_tree(base)
        docs_root_path = base / README_PATH
        docs_root = docs_root_path.read_text(encoding="utf-8")
        docs_root_path.write_text(
            docs_root.replace(DOCS_ROOT_DEPMOD_BOUNDARY_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(
            base,
            f"missing_marker:{README_PATH}:{DOCS_ROOT_DEPMOD_BOUNDARY_MARKER}",
        )

        write_fixture_tree(base)
        makefile_path = base / MAKEFILE_PATH
        makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            makefile.replace("phase9-runtime-loader-shared-tests:", "", 1),
            encoding="utf-8",
        )
        expect_failure(base, "missing_marker:zigux/Makefile:phase9-runtime-loader-shared-tests:")

        write_fixture_tree(base)
        build_path = base / PHASE9_BUILD_PATH
        build = build_path.read_text(encoding="utf-8")
        build_path.write_text(
            build.replace("runtime_loader_gap_survey.zig", "", 1),
            encoding="utf-8",
        )
        expect_failure(base, "missing_marker:zigux/tests/phase9_build.zig:runtime_loader_gap_survey.zig")

        write_fixture_tree(base)
        survey_path = base / LOADER_GAP_SURVEY_PATH
        survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            survey.replace("shared_phase9_bundle_route_present", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "missing_marker:zigux/tests/runtime_loader_gap_survey.zig:shared_phase9_bundle_route_present",
        )

        write_fixture_tree(base)
        forbidden_path = base / "scripts/zigux/check-phase9-loader-substrate-plan.py"
        write_text(forbidden_path, "# forbidden\n")
        expect_failure(base, "unexpected_file:scripts/zigux/check-phase9-loader-substrate-plan.py")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE9_BUILD_ONLY_SURFACE_SELF_TEST=pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the shared Phase 9 runtime-pilot build-only packet.")
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
            print(f"PHASE9_BUILD_ONLY_SURFACE_ERROR={failure}")
        return 1

    print(f"PHASE9_BUILD_ONLY_SURFACE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE9_BUILD_ONLY_SURFACE_REQUIRED_SURFACE_COUNT={len(REQUIRED_MARKERS)}")
    print("PHASE9_BUILD_ONLY_SURFACE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())