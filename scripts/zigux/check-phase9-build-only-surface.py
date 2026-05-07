#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "Documentation/zigux/README.md").exists() and (candidate / "zigux/Makefile").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()

DOCS_README_PATH = "Documentation/zigux/README.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
FREEZE_MAP_PATH = "Documentation/zigux/freeze-map.md"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"
RUNTIME_LOADER_PATH = "zigux/kernel/runtime_loader.zig"
RUNTIME_LOADER_CONTRACT_PATH = "zigux/kernel/runtime_loader_contract.zig"

REQUIRED_PHASE9_NOTE_PATHS = [
    "Documentation/zigux/phase9-runtime-atomic64-module-slice.md",
    "Documentation/zigux/phase9-runtime-atomic64-survey.md",
    "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
    "Documentation/zigux/phase9-runtime-bitmap-survey.md",
    "Documentation/zigux/phase9-runtime-kretprobe-module-slice.md",
    "Documentation/zigux/phase9-runtime-kretprobe-survey.md",
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
]

REQUIRED_PHASE9_LOADER_SCAFFOLD_PATHS = [
    "samples/zigux/runtime_atomic64_loader.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_trace_events_loader.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
]

PHASE9_NON_OWNER_BOUNDARY_MARKER = (
    "- the same shared Phase 9 summary should keep the older non-owner boundaries explicit: "
    "`scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain "
    "Phase 2 config-surface bridge references, while `rust/exports.c` and "
    "`zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references rather than "
    "runtime-pilot evidence."
)

PHASE9_REVIEW_CHECKLIST_BOUNDARY_MARKER = (
    "the Phase 2 config-surface references `scripts/zigux/kconfig/conf_bridge.zig` and "
    "`scripts/zigux/kconfig/confdata_bridge.zig`, and the Phase 3 export-boundary references "
    "`rust/exports.c` and `zigux/kernel/export_shim.zig`"
)

PHASE9_SCRIPTS_README_OWNER_MAP_MARKER = (
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` remains the shared owner map for how "
    "that scripts-root summary stays split between the loader lane and the four pilot-family packets."
)

PHASE9_DOCS_README_SHARED_SUMMARY_MARKER = (
    "`Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, "
    "`zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, "
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`, `scripts/zigux/check-phase9-build-only-surface.py`, "
    "`zigux/tests/phase9_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the four "
    "`samples/zigux/runtime_*_loader.zig` scaffolds now keep the current runtime atomic64, bitmap, trace-events, "
    "and kretprobe pilot bundle reviewable through one shared runtime-loader lane together with the shipped "
    "build-only surface checker, loader facade, contract, shared build, and workflow-backed Linux-style "
    "`make -C zigux phase9` replay route instead of widening into ad hoc per-slice checks or overstating removed "
    "loader-gap or dedicated-validator surfaces on `master`."
)

REQUIRED_DOCS_README_MARKERS = [
    "Phase 9 notes",
    PHASE9_DOCS_README_SHARED_SUMMARY_MARKER,
    PHASE9_NON_OWNER_BOUNDARY_MARKER,
]

REQUIRED_DOCS_README_EXACT_COUNTS = {
    PHASE9_DOCS_README_SHARED_SUMMARY_MARKER: 1,
    PHASE9_NON_OWNER_BOUNDARY_MARKER: 1,
}

REQUIRED_SCRIPT_README_MARKERS = [
    "Phase 9 flow",
    "`Documentation/zigux/review-checklist.md`",
    "`zig build test --build-file zigux/tests/phase9_build.zig` and `make -C zigux phase9` rerun that same "
    "bounded runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle together with the shared "
    "runtime-loader facade, loader contract, allocator/init-flow replay, and Linux-style replay route.",
    PHASE9_SCRIPTS_README_OWNER_MAP_MARKER,
    "there is no dedicated shared `validate-phase9.py`, `check-phase9-validation-flow.py`, "
    "`check-phase9-runtime-loader-commit-alignment.py`, or `phase9-validate` target on `master`",
]

REQUIRED_SCRIPT_README_EXACT_COUNTS = {
    PHASE9_SCRIPTS_README_OWNER_MAP_MARKER: 1,
}

REQUIRED_TESTS_README_MARKERS = [
    "keep the bounded Phase 9 runtime-loader packet wired through `Documentation/zigux/README.md`, "
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `scripts/zigux/README.md`, "
    "`Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-build-only-surface.py`, "
    "`zigux/tests/phase9_build.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, "
    "`make -C zigux phase9`, the four survey entrypoints `zigux/tests/runtime_atomic64_survey.zig`, "
    "`zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_trace_events_survey.zig`, and "
    "`zigux/tests/runtime_kretprobe_survey.zig`, the four `samples/zigux/runtime_*_loader.zig` scaffolds, "
    "and the shared `zigux/kernel/runtime_loader.zig` plus `zigux/kernel/runtime_loader_contract.zig` surfaces "
    "so the loader-handoff packet stays reviewable through the same shipped build-only checker and workflow-backed "
    "replay route without implying shared runtime substrate closure or a dedicated `validate-phase9.py` surface "
    "that does not exist on `master`",
]

REQUIRED_TESTS_README_EXACT_COUNTS = {
    REQUIRED_TESTS_README_MARKERS[0]: 1,
}

REQUIRED_SAMPLES_README_MARKERS = [
    "Separate Phase 9 runtime pilot family",
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` remains the shared owner map for the `runtime_loader` lane versus the four pilot-family packets, so the focused `phase9-runtime-bitmap-top-bit-tests` companion stays bitmap-local instead of drifting into shared loader evidence",
    "keep the older command and environment control boundary explicit too: `tools/lib/subcmd/exec-cmd.zig` still owns the deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` tooling cues, while `tools/lib/subcmd/help.zig` still owns the `LINES` and `COLUMNS` terminal-formatting cues; the Phase 9 loader packet remains a metadata-only handoff and should not be read as shipped runtime command or environment activation control on current `master`",
    "review the shipped Phase 9 runtime pilot family through `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, the focused `phase9-runtime-loader-shared-tests` step, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `.github/workflows/zigux-bootstrap.yml`, and `make -C zigux phase9`; keep those shared loader-handoff surfaces explicit instead of implying a dedicated `validate-phase9.py` route, a missing shared checker, or a cleared runtime-substrate handoff on current `master`",
]

REQUIRED_SAMPLES_README_EXACT_COUNTS = {
    REQUIRED_SAMPLES_README_MARKERS[1]: 1,
    REQUIRED_SAMPLES_README_MARKERS[2]: 1,
    REQUIRED_SAMPLES_README_MARKERS[3]: 1,
}

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "`scripts/zigux/check-phase9-build-only-surface.py`",
    "the shipped build-only surface checker",
    "workflow-backed `make -C zigux phase9` route",
    "roadmap-backed selftest-hook and runtime module lifecycle parity cues",
    "no-dedicated-`validate-phase9.py` posture",
    PHASE9_REVIEW_CHECKLIST_BOUNDARY_MARKER,
    "if the change touches a freeze-map anchor, is the parity scorecard evidence or blocker state explicit?",
]

REQUIRED_REVIEW_CHECKLIST_EXACT_COUNTS = {
    PHASE9_REVIEW_CHECKLIST_BOUNDARY_MARKER: 1,
}

REQUIRED_FREEZE_MAP_MARKERS = [
    "the shared Phase 9 runtime-loader packet stays review-only beside `kernel/workqueue.c` and "
    "`kernel/trace/ring_buffer.c`: `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, "
    "`zigux/tests/README.md`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, "
    "`zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the four "
    "`samples/zigux/runtime_*_loader.zig` scaffolds keep the bounded loader handoff explicit without implying "
    "scheduler-facing substrate closure or a freeze-map status change",
]

REQUIRED_FREEZE_MAP_EXACT_COUNTS = {
    REQUIRED_FREEZE_MAP_MARKERS[0]: 1,
}

REQUIRED_MAKEFILE_MARKERS = [
    "PHONY += phase9-test phase9",
    "phase9-test:",
    "$(PYTHON) scripts/zigux/check-phase9-build-only-surface.py",
    "$(ZIG) build test --build-file zigux/tests/phase9_build.zig",
    "phase9: phase9-test",
]

REQUIRED_WORKFLOW_MARKERS = [
    "Self-test Phase 9 build-only surface checker",
    "python3 scripts/zigux/check-phase9-build-only-surface.py --self-test",
    "Check Phase 9 build-only surface",
    "python3 scripts/zigux/check-phase9-build-only-surface.py",
    "Run Phase 9 runtime helper tests",
    "make -C zigux phase9",
]

REQUIRED_PHASE9_BUILD_MARKERS = [
    'const runtime_loader_contract_module = b.createModule(.{',
    '.root_source_file = b.path("../kernel/runtime_loader_contract.zig"),',
    'const runtime_loader_facade_module = b.createModule(.{',
    '.root_source_file = b.path("../kernel/runtime_loader.zig"),',
    'const runtime_atomic64_loader_module = b.createModule(.{',
    '.root_source_file = b.path("../../samples/zigux/runtime_atomic64_loader.zig"),',
    'const runtime_bitmap_loader_module = b.createModule(.{',
    '.root_source_file = b.path("../../samples/zigux/runtime_bitmap_loader.zig"),',
    'const runtime_trace_events_loader_module = b.createModule(.{',
    '.root_source_file = b.path("../../samples/zigux/runtime_trace_events_loader.zig"),',
    'const runtime_kretprobe_loader_module = b.createModule(.{',
    '.root_source_file = b.path("../../samples/zigux/runtime_kretprobe_loader.zig"),',
    'const runtime_loader_contract_tests = b.addTest(.{',
    '.name = "phase9-runtime-loader-contract-tests",',
    '.root_module = runtime_loader_contract_module,',
    "const run_runtime_loader_contract_tests = b.addRunArtifact(runtime_loader_contract_tests);",
    "test_step.dependOn(&run_runtime_loader_contract_tests.step);",
    'const runtime_loader_facade_tests = b.addTest(.{',
    '.name = "phase9-runtime-loader-facade-tests",',
    '.root_module = runtime_loader_facade_module,',
    "const run_runtime_loader_facade_tests = b.addRunArtifact(runtime_loader_facade_tests);",
    "test_step.dependOn(&run_runtime_loader_facade_tests.step);",
    'const runtime_loader_allocator_init_flow_module = b.createModule(.{',
    '.root_source_file = b.path("runtime_loader_allocator_init_flow.zig"),',
    'const runtime_loader_allocator_init_flow_tests = b.addTest(.{',
    '.name = "phase9-runtime-loader-allocator-init-flow-tests",',
    '.root_module = runtime_loader_allocator_init_flow_module,',
    "const run_runtime_loader_allocator_init_flow_tests = b.addRunArtifact(runtime_loader_allocator_init_flow_tests);",
    "test_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);",
    'const runtime_loader_shared_tests_step = b.step(',
    '"phase9-runtime-loader-shared-tests",',
    '"Run the focused Phase 9 runtime-loader facade, contract, and allocator/init-flow tests",',
    "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_contract_tests.step);",
    "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_facade_tests.step);",
    "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);",
    'const runtime_atomic64_loader_tests = b.addTest(.{',
    '.name = "phase9-runtime-atomic64-loader-tests",',
    '.root_module = runtime_atomic64_loader_module,',
    "const run_runtime_atomic64_loader_tests = b.addRunArtifact(runtime_atomic64_loader_tests);",
    "test_step.dependOn(&run_runtime_atomic64_loader_tests.step);",
    'const runtime_bitmap_loader_tests = b.addTest(.{',
    '.name = "phase9-runtime-bitmap-loader-tests",',
    '.root_module = runtime_bitmap_loader_module,',
    "const run_runtime_bitmap_loader_tests = b.addRunArtifact(runtime_bitmap_loader_tests);",
    "test_step.dependOn(&run_runtime_bitmap_loader_tests.step);",
    'const runtime_trace_events_loader_tests = b.addTest(.{',
    '.name = "phase9-runtime-trace-events-loader-tests",',
    '.root_module = runtime_trace_events_loader_module,',
    "const run_runtime_trace_events_loader_tests = b.addRunArtifact(runtime_trace_events_loader_tests);",
    "test_step.dependOn(&run_runtime_trace_events_loader_tests.step);",
    'const runtime_kretprobe_loader_tests = b.addTest(.{',
    '.name = "phase9-runtime-kretprobe-loader-tests",',
    '.root_module = runtime_kretprobe_loader_module,',
    "const run_runtime_kretprobe_loader_tests = b.addRunArtifact(runtime_kretprobe_loader_tests);",
    "test_step.dependOn(&run_runtime_kretprobe_loader_tests.step);",
    'const runtime_atomic64_survey_module = b.createModule(.{',
    '.root_source_file = b.path("runtime_atomic64_survey.zig"),',
    'const runtime_atomic64_survey_tests = b.addTest(.{',
    '.name = "phase9-runtime-atomic64-survey-tests",',
    '.root_module = runtime_atomic64_survey_module,',
    "const run_runtime_atomic64_survey_tests = b.addRunArtifact(runtime_atomic64_survey_tests);",
    "test_step.dependOn(&run_runtime_atomic64_survey_tests.step);",
    'const runtime_bitmap_survey_module = b.createModule(.{',
    '.root_source_file = b.path("runtime_bitmap_survey.zig"),',
    'const runtime_bitmap_survey_tests = b.addTest(.{',
    '.name = "phase9-runtime-bitmap-survey-tests",',
    '.root_module = runtime_bitmap_survey_module,',
    "const run_runtime_bitmap_survey_tests = b.addRunArtifact(runtime_bitmap_survey_tests);",
    "test_step.dependOn(&run_runtime_bitmap_survey_tests.step);",
    'const runtime_trace_events_survey_module = b.createModule(.{',
    '.root_source_file = b.path("runtime_trace_events_survey.zig"),',
    'const runtime_trace_events_survey_tests = b.addTest(.{',
    '.name = "phase9-runtime-trace-events-survey-tests",',
    '.root_module = runtime_trace_events_survey_module,',
    "const run_runtime_trace_events_survey_tests = b.addRunArtifact(runtime_trace_events_survey_tests);",
    "test_step.dependOn(&run_runtime_trace_events_survey_tests.step);",
    'const runtime_kretprobe_survey_module = b.createModule(.{',
    '.root_source_file = b.path("runtime_kretprobe_survey.zig"),',
    'const runtime_kretprobe_survey_tests = b.addTest(.{',
    '.name = "phase9-runtime-kretprobe-survey-tests",',
    '.root_module = runtime_kretprobe_survey_module,',
    "const run_runtime_kretprobe_survey_tests = b.addRunArtifact(runtime_kretprobe_survey_tests);",
    "test_step.dependOn(&run_runtime_kretprobe_survey_tests.step);",
]

REQUIRED_RUNTIME_LOADER_CONTRACT_MARKERS = [
    'test "shared runtime loader contract keeps command, environment, registration-summary, depmod-facing, and study-only core-boundary control surfaces outside the request contract" {',
    'try std.testing.expect(!@hasField(LoadPlan, "modinfo"));',
    'try std.testing.expect(!@hasField(LoadPlan, "module_alias"));',
    'try std.testing.expect(!@hasField(LoadPlan, "module_aliases"));',
    'try std.testing.expect(!@hasField(LoadPlan, "modules_alias_path"));',
    'try std.testing.expect(!@hasField(LoadPlan, "depmod_script"));',
    'try std.testing.expect(!@hasField(LoadPlan, "depmod_manifest"));',
    'try std.testing.expect(!@hasField(LoadPlan, "depmod_aliases"));',
    'try std.testing.expect(!@hasField(PreparedRequest, "modinfo"));',
    'try std.testing.expect(!@hasField(PreparedRequest, "module_aliases"));',
    'try std.testing.expect(!@hasField(PreparedRequest, "modules_alias_path"));',
    'try std.testing.expect(!@hasField(PreparedRequest, "depmod_script"));',
]

REQUIRED_PHASE9_BUILD_EXACT_COUNTS = {marker: 1 for marker in REQUIRED_PHASE9_BUILD_MARKERS}

FORBIDDEN_FILES = [
    "scripts/zigux/validate-phase9.py",
    "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
    "zigux/tests/runtime_module_metadata_manifest.json",
    "zigux/tests/runtime_module_metadata_survey.zig",
    "scripts/zigux/check-phase9-module-metadata-packet.py",
]

FORBIDDEN_MAKEFILE_MARKERS = [
    "PHONY += phase9-validate",
    "phase9-validate:",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def ensure_contains(failures: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:{marker}")


def ensure_exact_counts(failures: list[str], label: str, text: str, counts: dict[str, int]) -> None:
    for marker, expected_count in counts.items():
        actual_count = text.count(marker)
        if actual_count != expected_count:
            failures.append(f"{label}_exact_count:{marker}:expected={expected_count}:actual={actual_count}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in [
        DOCS_README_PATH,
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
        SAMPLES_README_PATH,
        REVIEW_CHECKLIST_PATH,
        FREEZE_MAP_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
        PHASE9_BUILD_PATH,
        RUNTIME_LOADER_PATH,
        RUNTIME_LOADER_CONTRACT_PATH,
        *REQUIRED_PHASE9_NOTE_PATHS,
        *REQUIRED_PHASE9_LOADER_SCAFFOLD_PATHS,
    ]:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")

    for rel_path in FORBIDDEN_FILES:
        if (root / rel_path).exists():
            failures.append(f"unexpected_file:{rel_path}")

    if failures:
        return failures

    docs_readme = read_text(root, DOCS_README_PATH)
    scripts_readme = read_text(root, SCRIPTS_README_PATH)
    tests_readme = read_text(root, TESTS_README_PATH)
    samples_readme = read_text(root, SAMPLES_README_PATH)
    review_checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    freeze_map = read_text(root, FREEZE_MAP_PATH)
    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)
    phase9_build = read_text(root, PHASE9_BUILD_PATH)
    runtime_loader_contract = read_text(root, RUNTIME_LOADER_CONTRACT_PATH)

    ensure_contains(failures, "docs_readme", docs_readme, REQUIRED_DOCS_README_MARKERS)
    ensure_contains(failures, "scripts_readme", scripts_readme, REQUIRED_SCRIPT_README_MARKERS)
    ensure_contains(failures, "tests_readme", tests_readme, REQUIRED_TESTS_README_MARKERS)
    ensure_contains(failures, "samples_readme", samples_readme, REQUIRED_SAMPLES_README_MARKERS)
    ensure_contains(failures, "review_checklist", review_checklist, REQUIRED_REVIEW_CHECKLIST_MARKERS)
    ensure_contains(failures, "freeze_map", freeze_map, REQUIRED_FREEZE_MAP_MARKERS)
    ensure_contains(failures, "makefile", makefile, REQUIRED_MAKEFILE_MARKERS)
    ensure_contains(failures, "workflow", workflow, REQUIRED_WORKFLOW_MARKERS)
    ensure_contains(failures, "phase9_build", phase9_build, REQUIRED_PHASE9_BUILD_MARKERS)
    ensure_contains(
        failures,
        "runtime_loader_contract",
        runtime_loader_contract,
        REQUIRED_RUNTIME_LOADER_CONTRACT_MARKERS,
    )

    ensure_exact_counts(failures, "docs_readme", docs_readme, REQUIRED_DOCS_README_EXACT_COUNTS)
    ensure_exact_counts(failures, "scripts_readme", scripts_readme, REQUIRED_SCRIPT_README_EXACT_COUNTS)
    ensure_exact_counts(failures, "tests_readme", tests_readme, REQUIRED_TESTS_README_EXACT_COUNTS)
    ensure_exact_counts(failures, "samples_readme", samples_readme, REQUIRED_SAMPLES_README_EXACT_COUNTS)
    ensure_exact_counts(failures, "review_checklist", review_checklist, REQUIRED_REVIEW_CHECKLIST_EXACT_COUNTS)
    ensure_exact_counts(failures, "freeze_map", freeze_map, REQUIRED_FREEZE_MAP_EXACT_COUNTS)
    ensure_exact_counts(failures, "phase9_build", phase9_build, REQUIRED_PHASE9_BUILD_EXACT_COUNTS)

    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        if marker in makefile:
            failures.append(f"makefile_forbidden:{marker}")

    return failures


def phase9_build_fixture() -> str:
    return "\n".join(REQUIRED_PHASE9_BUILD_MARKERS) + "\n"


def runtime_loader_contract_fixture() -> str:
    return "\n".join(REQUIRED_RUNTIME_LOADER_CONTRACT_MARKERS) + "\n"


def minimal_marker_doc(title: str, markers: list[str]) -> str:
    return "\n".join([f"# {title}", *markers, ""])


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)

    write_text(root / DOCS_README_PATH, minimal_marker_doc("Zigux Documentation", REQUIRED_DOCS_README_MARKERS))
    write_text(root / SCRIPTS_README_PATH, minimal_marker_doc("scripts/zigux", REQUIRED_SCRIPT_README_MARKERS))
    write_text(root / TESTS_README_PATH, minimal_marker_doc("zigux/tests", REQUIRED_TESTS_README_MARKERS))
    write_text(root / SAMPLES_README_PATH, minimal_marker_doc("samples/zigux", REQUIRED_SAMPLES_README_MARKERS))
    write_text(root / REVIEW_CHECKLIST_PATH, minimal_marker_doc("Zigux Review Checklist", REQUIRED_REVIEW_CHECKLIST_MARKERS))
    write_text(root / FREEZE_MAP_PATH, minimal_marker_doc("Zigux Freeze Map", REQUIRED_FREEZE_MAP_MARKERS))
    write_text(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_MARKERS + [""]))
    write_text(root / WORKFLOW_PATH, "\n".join(REQUIRED_WORKFLOW_MARKERS + [""]))
    write_text(root / PHASE9_BUILD_PATH, phase9_build_fixture())
    write_text(root / RUNTIME_LOADER_PATH, "// facade placeholder\n")
    write_text(root / RUNTIME_LOADER_CONTRACT_PATH, runtime_loader_contract_fixture())
    write_text(root / "zigux/tests/runtime_loader_allocator_init_flow.zig", "// allocator/init-flow placeholder\n")

    for rel_path in REQUIRED_PHASE9_NOTE_PATHS + REQUIRED_PHASE9_LOADER_SCAFFOLD_PATHS:
        write_text(root / rel_path, "// placeholder\n")


def expect_failure(root: Path, expected_failure: str, label: str) -> None:
    failures = validate(root)
    if expected_failure not in failures:
        raise SystemExit(f"{label}:expected {expected_failure!r}, got {failures!r}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase9-build-only-surface-") as tmpdir:
        root = Path(tmpdir) / "fixture"

        write_fixture_tree(root)
        failures = validate(root)
        if failures:
            raise SystemExit(f"default_fixture_failed:{failures!r}")

        write_fixture_tree(root)
        makefile_path = root / MAKEFILE_PATH
        makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            makefile.replace("$(PYTHON) scripts/zigux/check-phase9-build-only-surface.py\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(root, "makefile:$(PYTHON) scripts/zigux/check-phase9-build-only-surface.py", "missing_makefile_checker_call")

        write_fixture_tree(root)
        workflow_path = root / WORKFLOW_PATH
        workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            workflow.replace("make -C zigux phase9", "zig build test --build-file zigux/tests/phase9_build.zig", 1),
            encoding="utf-8",
        )
        expect_failure(root, "workflow:make -C zigux phase9", "missing_workflow_make_route")

        write_fixture_tree(root)
        docs_readme_path = root / DOCS_README_PATH
        docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            docs_readme.replace(
                "Phase 3 export-boundary references rather than runtime-pilot evidence.",
                "Phase 3 export references rather than runtime-pilot evidence.",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(root, f"docs_readme:{PHASE9_NON_OWNER_BOUNDARY_MARKER}", "missing_docs_non_owner_boundary_marker")

        write_fixture_tree(root)
        docs_readme_path = root / DOCS_README_PATH
        docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            docs_readme + PHASE9_DOCS_README_SHARED_SUMMARY_MARKER + "\n",
            encoding="utf-8",
        )
        expect_failure(
            root,
            f"docs_readme_exact_count:{PHASE9_DOCS_README_SHARED_SUMMARY_MARKER}:expected=1:actual=2",
            "duplicate_docs_root_shared_phase9_summary",
        )

        write_fixture_tree(root)
        scripts_readme_path = root / SCRIPTS_README_PATH
        scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            scripts_readme.replace(
                PHASE9_SCRIPTS_README_OWNER_MAP_MARKER,
                "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` stays nearby as context for the shared Phase 9 packet.",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            f"scripts_readme:{PHASE9_SCRIPTS_README_OWNER_MAP_MARKER}",
            "missing_scripts_root_owner_map_marker",
        )

        write_fixture_tree(root)
        scripts_readme_path = root / SCRIPTS_README_PATH
        scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            scripts_readme + PHASE9_SCRIPTS_README_OWNER_MAP_MARKER + "\n",
            encoding="utf-8",
        )
        expect_failure(
            root,
            f"scripts_readme_exact_count:{PHASE9_SCRIPTS_README_OWNER_MAP_MARKER}:expected=1:actual=2",
            "duplicate_scripts_root_owner_map_marker",
        )

        write_fixture_tree(root)
        tests_readme_path = root / TESTS_README_PATH
        tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            tests_readme.replace(
                "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, ",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            f"tests_readme:{REQUIRED_TESTS_README_MARKERS[0]}",
            "missing_tests_root_lane_sequencing_note",
        )

        write_fixture_tree(root)
        tests_readme_path = root / TESTS_README_PATH
        tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            tests_readme + REQUIRED_TESTS_README_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        expect_failure(
            root,
            f"tests_readme_exact_count:{REQUIRED_TESTS_README_MARKERS[0]}:expected=1:actual=2",
            "duplicate_tests_root_lane_sequencing_note",
        )

        write_fixture_tree(root)
        samples_readme_path = root / SAMPLES_README_PATH
        samples_readme = samples_readme_path.read_text(encoding="utf-8")
        samples_readme_path.write_text(
            samples_readme.replace(
                "the focused `phase9-runtime-bitmap-top-bit-tests` companion stays bitmap-local instead of drifting into shared loader evidence",
                "the focused bitmap companion stays bitmap-local instead of drifting into shared loader evidence",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            f"samples_readme:{REQUIRED_SAMPLES_README_MARKERS[1]}",
            "missing_samples_root_bitmap_top_bit_boundary",
        )

        write_fixture_tree(root)
        samples_readme_path = root / SAMPLES_README_PATH
        samples_readme = samples_readme_path.read_text(encoding="utf-8")
        samples_readme_path.write_text(
            samples_readme + REQUIRED_SAMPLES_README_MARKERS[1] + "\n",
            encoding="utf-8",
        )
        expect_failure(
            root,
            f"samples_readme_exact_count:{REQUIRED_SAMPLES_README_MARKERS[1]}:expected=1:actual=2",
            "duplicate_samples_root_bitmap_top_bit_boundary",
        )

        write_fixture_tree(root)
        samples_readme_path = root / SAMPLES_README_PATH
        samples_readme = samples_readme_path.read_text(encoding="utf-8")
        samples_readme_path.write_text(
            samples_readme.replace(
                "keep the older command and environment control boundary explicit too: `tools/lib/subcmd/exec-cmd.zig` still owns the deferred `command_name`, exec-path, `PERF_EXEC_PATH`, and `PATH` tooling cues, while `tools/lib/subcmd/help.zig` still owns the `LINES` and `COLUMNS` terminal-formatting cues; the Phase 9 loader packet remains a metadata-only handoff and should not be read as shipped runtime command or environment activation control on current `master`",
                "keep the older boundary explicit too: `tools/lib/subcmd/help.zig` still owns terminal-formatting cues",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            f"samples_readme:{REQUIRED_SAMPLES_README_MARKERS[2]}",
            "missing_samples_root_command_environment_boundary",
        )

        write_fixture_tree(root)
        samples_readme_path = root / SAMPLES_README_PATH
        samples_readme = samples_readme_path.read_text(encoding="utf-8")
        samples_readme_path.write_text(
            samples_readme + REQUIRED_SAMPLES_README_MARKERS[2] + "\n",
            encoding="utf-8",
        )
        expect_failure(
            root,
            f"samples_readme_exact_count:{REQUIRED_SAMPLES_README_MARKERS[2]}:expected=1:actual=2",
            "duplicate_samples_root_command_environment_boundary",
        )

        write_fixture_tree(root)
        samples_readme_path = root / SAMPLES_README_PATH
        samples_readme = samples_readme_path.read_text(encoding="utf-8")
        samples_readme_path.write_text(
            samples_readme + REQUIRED_SAMPLES_README_MARKERS[3] + "\n",
            encoding="utf-8",
        )
        expect_failure(
            root,
            f"samples_readme_exact_count:{REQUIRED_SAMPLES_README_MARKERS[3]}:expected=1:actual=2",
            "duplicate_samples_root_shared_phase9_review_route",
        )

        write_fixture_tree(root)
        freeze_map_path = root / FREEZE_MAP_PATH
        freeze_map = freeze_map_path.read_text(encoding="utf-8")
        freeze_map_path.write_text(
            freeze_map + REQUIRED_FREEZE_MAP_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        expect_failure(
            root,
            f"freeze_map_exact_count:{REQUIRED_FREEZE_MAP_MARKERS[0]}:expected=1:actual=2",
            "duplicate_freeze_map_phase9_boundary",
        )

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build.replace('const runtime_atomic64_survey_module = b.createModule(.{\n', "", 1),
            encoding="utf-8",
        )
        expect_failure(root, "phase9_build:const runtime_atomic64_survey_module = b.createModule(.{", "missing_atomic64_survey_module")

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build.replace('const runtime_trace_events_loader_module = b.createModule(.{\n', "", 1),
            encoding="utf-8",
        )
        expect_failure(root, "phase9_build:const runtime_trace_events_loader_module = b.createModule(.{", "missing_trace_events_loader_module")

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build.replace('.name = "phase9-runtime-atomic64-loader-tests",\n', '.name = "phase9-runtime-atomic64-build-tests",\n', 1),
            encoding="utf-8",
        )
        expect_failure(root, 'phase9_build:.name = "phase9-runtime-atomic64-loader-tests",', "missing_atomic64_loader_test_name")

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build.replace('.name = "phase9-runtime-bitmap-survey-tests",\n', '.name = "phase9-runtime-bitmap-build-tests",\n', 1),
            encoding="utf-8",
        )
        expect_failure(root, 'phase9_build:.name = "phase9-runtime-bitmap-survey-tests",', "missing_bitmap_survey_test_name")

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build.replace("test_step.dependOn(&run_runtime_bitmap_loader_tests.step);\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(root, "phase9_build:test_step.dependOn(&run_runtime_bitmap_loader_tests.step);", "missing_bitmap_loader_dependency")

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build.replace("test_step.dependOn(&run_runtime_trace_events_survey_tests.step);\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(root, "phase9_build:test_step.dependOn(&run_runtime_trace_events_survey_tests.step);", "missing_trace_events_survey_dependency")

        write_fixture_tree(root)
        runtime_loader_contract_path = root / RUNTIME_LOADER_CONTRACT_PATH
        runtime_loader_contract = runtime_loader_contract_path.read_text(encoding="utf-8")
        runtime_loader_contract_path.write_text(
            runtime_loader_contract.replace('try std.testing.expect(!@hasField(LoadPlan, "depmod_script"));\n', "", 1),
            encoding="utf-8",
        )
        expect_failure(
            root,
            'runtime_loader_contract:try std.testing.expect(!@hasField(LoadPlan, "depmod_script"));',
            "missing_depmod_script_boundary",
        )

        write_fixture_tree(root)
        review_checklist_path = root / REVIEW_CHECKLIST_PATH
        review_checklist = review_checklist_path.read_text(encoding="utf-8")
        review_checklist_path.write_text(
            review_checklist.replace("scripts/zigux/kconfig/confdata_bridge.zig", "scripts/zigux/confdata_bridge.zig", 1),
            encoding="utf-8",
        )
        expect_failure(root, f"review_checklist:{PHASE9_REVIEW_CHECKLIST_BOUNDARY_MARKER}", "missing_phase9_non_owner_boundary_paths")

        write_fixture_tree(root)
        review_checklist_path = root / REVIEW_CHECKLIST_PATH
        review_checklist = review_checklist_path.read_text(encoding="utf-8")
        review_checklist_path.write_text(
            review_checklist.replace(
                "roadmap-backed selftest-hook and runtime module lifecycle parity cues",
                "roadmap-backed runtime module lifecycle parity cues",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            "review_checklist:roadmap-backed selftest-hook and runtime module lifecycle parity cues",
            "missing_phase9_selftest_lifecycle_marker",
        )

        write_fixture_tree(root)
        review_checklist_path = root / REVIEW_CHECKLIST_PATH
        review_checklist = review_checklist_path.read_text(encoding="utf-8")
        review_checklist_path.write_text(
            review_checklist.replace(
                "if the change touches a freeze-map anchor, is the parity scorecard evidence or blocker state explicit?\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            "review_checklist:if the change touches a freeze-map anchor, is the parity scorecard evidence or blocker state explicit?",
            "missing_phase9_freeze_map_anchor_prompt",
        )

        write_fixture_tree(root)
        review_checklist_path = root / REVIEW_CHECKLIST_PATH
        review_checklist = review_checklist_path.read_text(encoding="utf-8")
        review_checklist_path.write_text(review_checklist + PHASE9_REVIEW_CHECKLIST_BOUNDARY_MARKER + "\n", encoding="utf-8")
        expect_failure(
            root,
            f"review_checklist_exact_count:{PHASE9_REVIEW_CHECKLIST_BOUNDARY_MARKER}:expected=1:actual=2",
            "duplicate_phase9_non_owner_boundary_paths",
        )

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build + "test_step.dependOn(&run_runtime_kretprobe_loader_tests.step);\n",
            encoding="utf-8",
        )
        expect_failure(
            root,
            "phase9_build_exact_count:test_step.dependOn(&run_runtime_kretprobe_loader_tests.step);:expected=1:actual=2",
            "duplicate_kretprobe_loader_dependency",
        )

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build + "test_step.dependOn(&run_runtime_kretprobe_survey_tests.step);\n",
            encoding="utf-8",
        )
        expect_failure(
            root,
            "phase9_build_exact_count:test_step.dependOn(&run_runtime_kretprobe_survey_tests.step);:expected=1:actual=2",
            "duplicate_kretprobe_survey_dependency",
        )

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build.replace('const runtime_loader_contract_tests = b.addTest(.{\n', "", 1),
            encoding="utf-8",
        )
        expect_failure(root, 'phase9_build:const runtime_loader_contract_tests = b.addTest(.{', "missing_phase9_build_contract_test_declaration")

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build.replace('const runtime_loader_shared_tests_step = b.step(\n', "", 1),
            encoding="utf-8",
        )
        expect_failure(root, 'phase9_build:const runtime_loader_shared_tests_step = b.step(', "missing_phase9_build_shared_loader_step")

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build + "runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_contract_tests.step);\n",
            encoding="utf-8",
        )
        expect_failure(
            root,
            "phase9_build_exact_count:runtime_loader_shared_tests_step.dependOn(&run_runtime_loader_contract_tests.step);:expected=1:actual=2",
            "duplicate_phase9_build_shared_loader_contract_dependency",
        )

        write_fixture_tree(root)
        write_text(root / "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md", "# stale note\n")
        expect_failure(
            root,
            "unexpected_file:Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
            "unexpected_metadata_note",
        )

        write_fixture_tree(root)
        write_text(root / "scripts/zigux/check-phase9-module-metadata-packet.py", "# stale checker\n")
        expect_failure(
            root,
            "unexpected_file:scripts/zigux/check-phase9-module-metadata-packet.py",
            "unexpected_metadata_checker",
        )

        write_fixture_tree(root)
        script_path = root / "scripts/zigux/check-phase9-build-only-surface.py"
        write_text(script_path, SELF_PATH.read_text(encoding="utf-8"))
        probe = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if probe.returncode != 0 or "PHASE9_BUILD_ONLY_SURFACE=pass" not in probe.stdout:
            raise SystemExit(
                "default_root_probe_failed:"
                f"returncode={probe.returncode}:stdout={probe.stdout!r}:stderr={probe.stderr!r}"
            )

    print("PHASE9_BUILD_ONLY_SURFACE_SELF_TEST=pass")
    print("PHASE9_BUILD_ONLY_SURFACE_SELF_TEST_CASE_COUNT=33")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 9 runtime-loader release surface without inventing a separate validator route."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the repository root inferred from this script.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the fixture-backed self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE9_BUILD_ONLY_SURFACE=fail")
        print("PHASE9_BUILD_ONLY_SURFACE_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE9_BUILD_ONLY_SURFACE_FAILURES_END")
        return 1

    print("PHASE9_BUILD_ONLY_SURFACE=pass")
    print(
        "PHASE9_BUILD_ONLY_SURFACE_MARKER_COUNT="
        f"{len(REQUIRED_DOCS_README_MARKERS) + len(REQUIRED_SCRIPT_README_MARKERS) + len(REQUIRED_TESTS_README_MARKERS) + len(REQUIRED_SAMPLES_README_MARKERS) + len(REQUIRED_REVIEW_CHECKLIST_MARKERS) + len(REQUIRED_FREEZE_MAP_MARKERS) + len(REQUIRED_MAKEFILE_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_PHASE9_BUILD_MARKERS) + len(REQUIRED_RUNTIME_LOADER_CONTRACT_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
