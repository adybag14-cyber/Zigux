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

PHASE9_LANE_SEQUENCING_PATH = "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"
RUNTIME_LOADER_PATH = "zigux/kernel/runtime_loader.zig"
RUNTIME_LOADER_CONTRACT_PATH = "zigux/kernel/runtime_loader_contract.zig"
ALLOCATOR_INIT_FLOW_PATH = "zigux/tests/runtime_loader_allocator_init_flow.zig"
LOADER_GAP_SURVEY_PATH = "zigux/tests/runtime_loader_gap_survey.zig"

REQUIRED_FILES = [
    PHASE9_LANE_SEQUENCING_PATH,
    REVIEW_CHECKLIST_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    SAMPLES_README_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
    PHASE9_BUILD_PATH,
    RUNTIME_LOADER_PATH,
    RUNTIME_LOADER_CONTRACT_PATH,
    ALLOCATOR_INIT_FLOW_PATH,
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
]

OWNER_SPLIT_MARKER = (
    "the exact `P9-L04`/`P9-L08`/`P9-L10`/`P9-L13` split before another broader shared reminder pass"
)
PREPARED_STATE_LANDED_MARKER = (
    "`zigux/tests/runtime_loader_allocator_init_flow.zig` already keeps the prepared-plan drift replay explicit"
)
GAP_SURVEY_DRIFT_MARKER = (
    "`scripts/zigux/README.md` and `zigux/tests/README.md` still omit `zigux/tests/runtime_loader_gap_survey.zig`"
)
GAP_SURVEY_NEXT_STEP_MARKER = (
    "starting with `scripts/zigux/README.md` and then `zigux/tests/README.md`"
)
OWNER_MAP_MARKERS = [
    "- `P9-L04`: owns the current runtime atomic64 manifest-backed survey-versus-module-slice packet.",
    "- `P9-L08`: owns the current runtime bitmap manifest, survey note, module-slice note, focused top-bit companion replay, and survey gate packet.",
    "- `P9-L10`: owns the current runtime trace-events manifest, survey note, module-slice note, and survey-gate packet.",
    "- `P9-L13`: owns the current runtime kretprobe manifest-backed loader-plan, survey-gate lifecycle, and tracing proof follow-through.",
]

REQUIRED_MARKERS = {
    PHASE9_LANE_SEQUENCING_PATH: [
        OWNER_SPLIT_MARKER,
        PREPARED_STATE_LANDED_MARKER,
        GAP_SURVEY_DRIFT_MARKER,
        GAP_SURVEY_NEXT_STEP_MARKER,
        *OWNER_MAP_MARKERS,
        "the shipped `scripts/zigux/check-phase9-build-only-surface.py` guard should fail closed",
    ],
    REVIEW_CHECKLIST_PATH: [
        "`scripts/zigux/check-phase9-build-only-surface.py`",
        "workflow-backed `make -C zigux phase9` route",
        "the dedicated owner-map split recorded in `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
        "the focused bitmap top-bit companion replay `samples/zigux/runtime_bitmap_top_bit_contract.zig` plus the shipped `phase9-runtime-bitmap-top-bit-tests` step in `zigux/tests/phase9_build.zig`",
        "no-dedicated-`validate-phase9.py` posture",
    ],
    SCRIPTS_README_PATH: [
        "Phase 9 flow",
        "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` remains the shared owner map for how that scripts-root summary stays split between the loader lane and the four pilot-family packets.",
        "there is no dedicated shared `validate-phase9.py`, `check-phase9-validation-flow.py`, `check-phase9-runtime-loader-commit-alignment.py`, or `phase9-validate` target on `master`",
    ],
    TESTS_README_PATH: [
        "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
        "`scripts/zigux/check-phase9-build-only-surface.py`",
        "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
        "`zigux/kernel/runtime_loader.zig` plus `zigux/kernel/runtime_loader_contract.zig`",
    ],
    SAMPLES_README_PATH: [
        "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` remains the shared owner map for the `runtime_loader` lane versus the four pilot-family packets",
        "the focused `phase9-runtime-loader-shared-tests` step",
        "keep those shared loader-handoff surfaces explicit instead of implying a dedicated `validate-phase9.py` route",
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
        '"phase9-runtime-loader-shared-tests"',
        "runtime_loader_gap_survey.zig",
        "runtime_loader_allocator_init_flow.zig",
        '"phase9-runtime-bitmap-top-bit-tests"',
        "runtime_bitmap_top_bit_contract.zig",
    ],
    LOADER_GAP_SURVEY_PATH: [
        "phase 9 runtime loader gap survey keeps manifest and note aligned",
        "phase 9 runtime loader gap survey keeps phase 8 argv and environment controls out of the shared runtime surface",
    ],
}

FORBIDDEN_MARKERS = {
    MAKEFILE_PATH: ["phase9-validate:"],
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
        if markers is None:
            if rel_path.endswith(".py"):
                content = "# placeholder\n"
            elif rel_path.endswith(".md"):
                content = "# placeholder\n"
            else:
                content = "// placeholder\n"
        else:
            title = Path(rel_path).name
            content = "\n".join([f"# {title}", *markers, ""])
        write_text(root / rel_path, content)


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase9-build-only-surface-"))
    try:
        write_fixture_tree(base)
        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        lane_note_path = base / PHASE9_LANE_SEQUENCING_PATH
        lane_note = lane_note_path.read_text(encoding="utf-8")
        lane_note_path.write_text(lane_note.replace(OWNER_SPLIT_MARKER, "", 1), encoding="utf-8")
        expect_failure(base, f"missing_marker:{PHASE9_LANE_SEQUENCING_PATH}:{OWNER_SPLIT_MARKER}")

        write_fixture_tree(base)
        lane_note_path = base / PHASE9_LANE_SEQUENCING_PATH
        lane_note = lane_note_path.read_text(encoding="utf-8")
        lane_note_path.write_text(
            lane_note.replace(GAP_SURVEY_DRIFT_MARKER, "", 1),
            encoding="utf-8",
        )
        expect_failure(base, f"missing_marker:{PHASE9_LANE_SEQUENCING_PATH}:{GAP_SURVEY_DRIFT_MARKER}")

        write_fixture_tree(base)
        checklist_path = base / REVIEW_CHECKLIST_PATH
        checklist = checklist_path.read_text(encoding="utf-8")
        checklist_path.write_text(
            checklist.replace(
                "the dedicated owner-map split recorded in `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            base,
            "missing_marker:Documentation/zigux/review-checklist.md:the dedicated owner-map split recorded in `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
        )

        write_fixture_tree(base)
        makefile_path = base / MAKEFILE_PATH
        makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(makefile.replace("phase9-runtime-loader-shared-tests:", "", 1), encoding="utf-8")
        expect_failure(base, "missing_marker:zigux/Makefile:phase9-runtime-loader-shared-tests:")

        write_fixture_tree(base)
        build_path = base / PHASE9_BUILD_PATH
        build = build_path.read_text(encoding="utf-8")
        build_path.write_text(build.replace("runtime_loader_gap_survey.zig", "", 1), encoding="utf-8")
        expect_failure(base, "missing_marker:zigux/tests/phase9_build.zig:runtime_loader_gap_survey.zig")

        write_fixture_tree(base)
        forbidden_path = base / "scripts/zigux/validate-phase9.py"
        write_text(forbidden_path, "# forbidden\n")
        expect_failure(base, "unexpected_file:scripts/zigux/validate-phase9.py")
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
