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

REQUIRED_DOCS_README_MARKERS = [
    "Phase 9 notes",
    "`Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds now keep the current runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle reviewable through one shared runtime-loader lane together with the shipped build-only surface checker, loader facade, contract, shared build, and workflow-backed Linux-style `make -C zigux phase9` replay route instead of widening into ad hoc per-slice checks or overstating removed loader-gap or dedicated-validator surfaces on `master`.",
]

REQUIRED_SCRIPT_README_MARKERS = [
    "Phase 9 flow",
    "`Documentation/zigux/review-checklist.md`",
    "`zig build test --build-file zigux/tests/phase9_build.zig` and `make -C zigux phase9` rerun that same bounded runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle together with the shared runtime-loader facade, loader contract, allocator/init-flow replay, and Linux-style replay route.",
    "there is no dedicated shared `validate-phase9.py`, `check-phase9-validation-flow.py`, `check-phase9-runtime-loader-commit-alignment.py`, or `phase9-validate` target on `master`",
]

REQUIRED_TESTS_README_MARKERS = [
    "keep the bounded Phase 9 runtime-loader packet wired through `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase9_build.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `make -C zigux phase9`, the four survey entrypoints `zigux/tests/runtime_atomic64_survey.zig`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_trace_events_survey.zig`, and `zigux/tests/runtime_kretprobe_survey.zig`, the four `samples/zigux/runtime_*_loader.zig` scaffolds, and the shared `zigux/kernel/runtime_loader.zig` plus `zigux/kernel/runtime_loader_contract.zig` surfaces so the loader-handoff packet stays reviewable without implying shared runtime substrate closure or a dedicated `validate-phase9.py` surface that does not exist on `master`",
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "`scripts/zigux/check-phase9-build-only-surface.py`",
    "the shipped build-only surface checker",
    "workflow-backed `make -C zigux phase9` route",
    "no-dedicated-`validate-phase9.py` posture",
]

REQUIRED_FREEZE_MAP_MARKERS = [
    "the shared Phase 9 runtime-loader packet stays review-only beside `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`: `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds keep the bounded loader handoff explicit without implying scheduler-facing substrate closure or a freeze-map status change",
]

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
]

REQUIRED_PHASE9_BUILD_MARKERS = [
    'const runtime_loader_facade_module = b.createModule(.{',
    '.root_source_file = b.path("../kernel/runtime_loader.zig"),',
    'const runtime_loader_facade_tests = b.addTest(.{',
    '.name = "phase9-runtime-loader-facade-tests",',
    '.root_module = runtime_loader_facade_module,',
    "const run_runtime_loader_facade_tests = b.addRunArtifact(runtime_loader_facade_tests);",
    "test_step.dependOn(&run_runtime_loader_facade_tests.step);",
]

REQUIRED_PHASE9_BUILD_EXACT_COUNTS = {
    'const runtime_loader_facade_module = b.createModule(.{': 1,
    '.root_source_file = b.path("../kernel/runtime_loader.zig"),': 1,
    'const runtime_loader_facade_tests = b.addTest(.{': 1,
    '.name = "phase9-runtime-loader-facade-tests",': 1,
    '.root_module = runtime_loader_facade_module,': 1,
    "const run_runtime_loader_facade_tests = b.addRunArtifact(runtime_loader_facade_tests);": 1,
    "test_step.dependOn(&run_runtime_loader_facade_tests.step);": 1,
}

FORBIDDEN_FILES = [
    "scripts/zigux/validate-phase9.py",
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


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    for rel_path in [
        DOCS_README_PATH,
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
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
    review_checklist = read_text(root, REVIEW_CHECKLIST_PATH)
    freeze_map = read_text(root, FREEZE_MAP_PATH)
    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)
    phase9_build = read_text(root, PHASE9_BUILD_PATH)

    for marker in REQUIRED_DOCS_README_MARKERS:
        if marker not in docs_readme:
            failures.append(f"docs_readme:{marker}")
    for marker in REQUIRED_SCRIPT_README_MARKERS:
        if marker not in scripts_readme:
            failures.append(f"scripts_readme:{marker}")
    for marker in REQUIRED_TESTS_README_MARKERS:
        if marker not in tests_readme:
            failures.append(f"tests_readme:{marker}")
    for marker in REQUIRED_REVIEW_CHECKLIST_MARKERS:
        if marker not in review_checklist:
            failures.append(f"review_checklist:{marker}")
    for marker in REQUIRED_FREEZE_MAP_MARKERS:
        if marker not in freeze_map:
            failures.append(f"freeze_map:{marker}")
    for marker in REQUIRED_MAKEFILE_MARKERS:
        if marker not in makefile:
            failures.append(f"makefile:{marker}")
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if marker not in workflow:
            failures.append(f"workflow:{marker}")
    for marker in REQUIRED_PHASE9_BUILD_MARKERS:
        if marker not in phase9_build:
            failures.append(f"phase9_build:{marker}")
    for marker, expected_count in REQUIRED_PHASE9_BUILD_EXACT_COUNTS.items():
        actual_count = phase9_build.count(marker)
        if actual_count != expected_count:
            failures.append(
                f"phase9_build_exact_count:{marker}:expected={expected_count}:actual={actual_count}"
            )
    for marker in FORBIDDEN_MAKEFILE_MARKERS:
        if marker in makefile:
            failures.append(f"makefile_forbidden:{marker}")

    return failures


def write_fixture_tree(root: Path) -> None:
    if root.exists():
        shutil.rmtree(root)
    write_text(
        root / DOCS_README_PATH,
        """# Zigux Documentation

Phase 9 notes
- `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds now keep the current runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle reviewable through one shared runtime-loader lane together with the shipped build-only surface checker, loader facade, contract, shared build, and workflow-backed Linux-style `make -C zigux phase9` replay route instead of widening into ad hoc per-slice checks or overstating removed loader-gap or dedicated-validator surfaces on `master`.
""",
    )
    write_text(
        root / SCRIPTS_README_PATH,
        """# scripts/zigux

Phase 9 flow
- the current shared Phase 9 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, the four runtime survey-and-module note pairs (`Documentation/zigux/phase9-runtime-atomic64-module-slice.md`, `Documentation/zigux/phase9-runtime-atomic64-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, and `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`, and `Documentation/zigux/phase9-runtime-kretprobe-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, and `Documentation/zigux/phase9-runtime-trace-events-survey.md`), `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds.
- `zig build test --build-file zigux/tests/phase9_build.zig` and `make -C zigux phase9` rerun that same bounded runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle together with the shared runtime-loader facade, loader contract, allocator/init-flow replay, and Linux-style replay route.
- there is no dedicated shared `validate-phase9.py`, `check-phase9-validation-flow.py`, `check-phase9-runtime-loader-commit-alignment.py`, or `phase9-validate` target on `master`; future runtime-pilot follow-through should stay inside the next smallest shared runtime-loader substrate, validation, or review-surface step that keeps those four loader handoffs plus the shared `zigux/kernel/runtime_loader.zig` facade and `zigux/kernel/runtime_loader_contract.zig` allocator/init-flow contract reviewable without widening into a larger runtime-module implementation.
""",
    )
    write_text(
        root / TESTS_README_PATH,
        """# zigux/tests

- keep the bounded Phase 9 runtime-loader packet wired through `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase9_build.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `make -C zigux phase9`, the four survey entrypoints `zigux/tests/runtime_atomic64_survey.zig`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_trace_events_survey.zig`, and `zigux/tests/runtime_kretprobe_survey.zig`, the four `samples/zigux/runtime_*_loader.zig` scaffolds, and the shared `zigux/kernel/runtime_loader.zig` plus `zigux/kernel/runtime_loader_contract.zig` surfaces so the loader-handoff packet stays reviewable without implying shared runtime substrate closure or a dedicated `validate-phase9.py` surface that does not exist on `master`
""",
    )
    write_text(
        root / REVIEW_CHECKLIST_PATH,
        """# Zigux Review Checklist

- if the change touches the shared Phase 9 runtime-loader packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, the four runtime survey-and-module note pairs, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, the four `samples/zigux/runtime_*_loader.zig` scaffolds, the Phase 2 config-surface references `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig`, and the Phase 3 export-boundary references `rust/exports.c` and `zigux/kernel/export_shim.zig` still agree on the same bounded loader-handoff packet, the shipped build-only surface checker, and the no-dedicated-`validate-phase9.py` posture without recasting those earlier-phase references as Phase 9 runtime evidence or understating the shipped shared runtime-loader facade, contract, allocator/init-flow replay, or workflow-backed `make -C zigux phase9` route on `master`?
""",
    )
    write_text(
        root / FREEZE_MAP_PATH,
        """# Zigux Freeze Map

This file records code that should not move into active Zigux delivery without an explicit Architecture Council decision.

## Freeze In C Initially
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

## Study / Boundary Only
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

## Governance For Freeze-Map Changes
- changes to either list require an explicit Architecture Council decision with written rationale
- any lane that touches a listed anchor must declare owner, phase, status bucket, validation gate, and rollback owner in the reviewable record for that lane
- direct Zig port or bridge claims for a freeze-in-C anchor stay blocked until the repo carries a parity scorecard entry and the Architecture Council records why the status can change

## Stay-In-C Policy
- the existing C implementation remains the product source of truth for every freeze-in-C anchor
- allowed near-term Zigux work on those anchors is limited to survey notes, boundary manifests, validation gates, and explicit non-goal records
- wrapper-first or helper-first experiments may continue only for study-only anchors, and they still must keep scheduler, MM, RCU, skbuff, and other deep-core ownership explicit
- the shared Phase 9 runtime-loader packet stays review-only beside `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`: `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds keep the bounded loader handoff explicit without implying scheduler-facing substrate closure or a freeze-map status change
- if validation is incomplete, contradictory, or too weak to justify a status change, keep the code in C and record the blocker
- closing a freeze-in-C review without a status change must retain the blocker, record the closeout as `retired_from_active_discussion`, and keep the reopen triggers attached to the evidence archive
- there is no silent exception path around the stay-in-C policy; only an explicit Architecture Council reopen request with fresh linked evidence may reopen status review

## Policy
- deep-core files do not become sprint targets by enthusiasm alone
- research is allowed
- product commitments require explicit gates, validation, and ownership
- if evidence is not overwhelming, keep the code in C and document why
""",
    )
    write_text(
        root / MAKEFILE_PATH,
        """PHONY += phase9-test phase9

phase9-test:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-build-only-surface.py
	cd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase9_build.zig

phase9: phase9-test
""",
    )
    write_text(
        root / WORKFLOW_PATH,
        """jobs:
  bootstrap:
    steps:
      - name: Self-test Phase 9 build-only surface checker
        run: python3 scripts/zigux/check-phase9-build-only-surface.py --self-test
      - name: Check Phase 9 build-only surface
        run: python3 scripts/zigux/check-phase9-build-only-surface.py
      - name: Run Phase 9 runtime helper tests
        run: zig build test --build-file zigux/tests/phase9_build.zig --summary all
""",
    )
    write_text(
        root / PHASE9_BUILD_PATH,
        """const runtime_loader_facade_module = b.createModule(.{
    .root_source_file = b.path("../kernel/runtime_loader.zig"),
});
const runtime_loader_facade_tests = b.addTest(.{
    .name = "phase9-runtime-loader-facade-tests",
    .root_module = runtime_loader_facade_module,
});
const run_runtime_loader_facade_tests = b.addRunArtifact(runtime_loader_facade_tests);
test_step.dependOn(&run_runtime_loader_facade_tests.step);
""",
    )
    write_text(root / RUNTIME_LOADER_PATH, "pub fn placeholder() void {}\n")
    write_text(root / RUNTIME_LOADER_CONTRACT_PATH, "pub fn placeholder() void {}\n")
    for rel_path in REQUIRED_PHASE9_NOTE_PATHS:
        write_text(root / rel_path, "# Phase 9 note\n")
    for rel_path in REQUIRED_PHASE9_LOADER_SCAFFOLD_PATHS:
        write_text(root / rel_path, "pub fn placeholder() void {}\n")


def expect_failure(root: Path, expected: str, label: str) -> None:
    failures = validate(root)
    if expected not in failures:
        actual = ",".join(failures) if failures else "none"
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_build_only_") as tmp_dir:
        root = Path(tmp_dir)
        write_fixture_tree(root)

        baseline = validate(root)
        if baseline:
            raise SystemExit("baseline_failed:" + ",".join(baseline))

        write_text(root / "scripts/zigux/validate-phase9.py", "print('unexpected')\n")
        expect_failure(
            root,
            "unexpected_file:scripts/zigux/validate-phase9.py",
            "unexpected_validate_script",
        )

        write_fixture_tree(root)
        docs_readme_path = root / DOCS_README_PATH
        docs_readme = docs_readme_path.read_text(encoding="utf-8")
        docs_readme_path.write_text(
            docs_readme.replace(
                "`scripts/zigux/check-phase9-build-only-surface.py`, ",
                "",
                1,
            ).replace(
                "workflow-backed Linux-style `make -C zigux phase9` replay route",
                "Linux-style `make -C zigux phase9` replay route",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            "docs_readme:`Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds now keep the current runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle reviewable through one shared runtime-loader lane together with the shipped build-only surface checker, loader facade, contract, shared build, and workflow-backed Linux-style `make -C zigux phase9` replay route instead of widening into ad hoc per-slice checks or overstating removed loader-gap or dedicated-validator surfaces on `master`.",
            "missing_docs_build_only_surface_marker",
        )

        write_fixture_tree(root)
        scripts_readme_path = root / SCRIPTS_README_PATH
        scripts_readme = scripts_readme_path.read_text(encoding="utf-8")
        scripts_readme_path.write_text(
            scripts_readme.replace(
                "`check-phase9-runtime-loader-commit-alignment.py`, ",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            "scripts_readme:there is no dedicated shared `validate-phase9.py`, `check-phase9-validation-flow.py`, `check-phase9-runtime-loader-commit-alignment.py`, or `phase9-validate` target on `master`",
            "missing_scripts_removed_checker_marker",
        )

        write_fixture_tree(root)
        freeze_map_path = root / FREEZE_MAP_PATH
        freeze_map = freeze_map_path.read_text(encoding="utf-8")
        freeze_map_path.write_text(
            freeze_map.replace(
                "- the shared Phase 9 runtime-loader packet stays review-only beside `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`: `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds keep the bounded loader handoff explicit without implying scheduler-facing substrate closure or a freeze-map status change\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            "freeze_map:the shared Phase 9 runtime-loader packet stays review-only beside `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`: `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/check-phase9-build-only-surface.py`, `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds keep the bounded loader handoff explicit without implying scheduler-facing substrate closure or a freeze-map status change",
            "missing_freeze_map_phase9_boundary_marker",
        )

        write_fixture_tree(root)
        makefile_path = root / MAKEFILE_PATH
        makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-build-only-surface.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            "makefile:$(PYTHON) scripts/zigux/check-phase9-build-only-surface.py",
            "missing_makefile_checker_call",
        )

        write_fixture_tree(root)
        workflow_path = root / WORKFLOW_PATH
        workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            workflow.replace("Self-test Phase 9 build-only surface checker", "Phase 9 build-only surface checker", 1),
            encoding="utf-8",
        )
        expect_failure(
            root,
            "workflow:Self-test Phase 9 build-only surface checker",
            "missing_workflow_self_test_marker",
        )

        write_fixture_tree(root)
        makefile_path = root / MAKEFILE_PATH
        makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(makefile + "\nphase9-validate:\n\ttrue\n", encoding="utf-8")
        expect_failure(
            root,
            "makefile_forbidden:phase9-validate:",
            "unexpected_phase9_validate_target",
        )

        write_fixture_tree(root)
        (root / "samples/zigux/runtime_trace_events_loader.zig").unlink()
        expect_failure(
            root,
            "missing_file:samples/zigux/runtime_trace_events_loader.zig",
            "missing_trace_events_loader_scaffold",
        )

        write_fixtureTree(root)
        (root / "Documentation/zigux/phase9-runtime-trace-events-module-slice.md").unlink()
        expect_failure(
            root,
            "missing_file:Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
            "missing_trace_events_module_slice",
        )

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build.replace(
                'const runtime_loader_facade_module = b.createModule(.{\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            'phase9_build:const runtime_loader_facade_module = b.createModule(.{',
            "missing_phase9_build_facade_module_declaration",
        )

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build.replace(
                '    .root_source_file = b.path("../kernel/runtime_loader.zig"),\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            'phase9_build:.root_source_file = b.path("../kernel/runtime_loader.zig"),',
            "missing_phase9_build_facade_source_path",
        )

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build.replace(
                '    .name = "phase9-runtime-loader-facade-tests",\n',
                '    .name = "phase9-runtime-loader-tests",\n',
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            'phase9_build:.name = "phase9-runtime-loader-facade-tests",',
            "missing_phase9_build_facade_test_name",
        )

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build.replace(
                "test_step.dependOn(&run_runtime_loader_facade_tests.step);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            "phase9_build:test_step.dependOn(&run_runtime_loader_facade_tests.step);",
            "missing_phase9_build_facade_replay_dependency",
        )

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build + "test_step.dependOn(&run_runtime_loader_facade_tests.step);\n",
            encoding="utf-8",
        )
        expect_failure(
            root,
            "phase9_build_exact_count:test_step.dependOn(&run_runtime_loader_facade_tests.step);:expected=1:actual=2",
            "duplicate_phase9_build_facade_replay_dependency",
        )

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build.replace(
                ".root_module = runtime_loader_facade_module,\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            "phase9_build:.root_module = runtime_loader_facade_module,",
            "missing_phase9_build_facade_root_module",
        )

        write_fixture_tree(root)
        phase9_build_path = root / PHASE9_BUILD_PATH
        phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            phase9_build.replace(
                "const run_runtime_loader_facade_tests = b.addRunArtifact(runtime_loader_facade_tests);\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            root,
            "phase9_build:const run_runtime_loader_facade_tests = b.addRunArtifact(runtime_loader_facade_tests);",
            "missing_phase9_build_facade_run_artifact",
        )

        write_fixture_tree(root)
        write_text(root / "scripts/zigux/check-phase9-build-only-surface.py", SELF_PATH.read_text(encoding="utf-8"))
        probe = subprocess.run(
            [sys.executable, str(root / "scripts/zigux/check-phase9-build-only-surface.py")],
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
    print("PHASE9_BUILD_ONLY_SURFACE_SELF_TEST_CASE_COUNT=16")
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
        f"{len(REQUIRED_DOCS_README_MARKERS) + len(REQUIRED_SCRIPT_README_MARKERS) + len(REQUIRED_TESTS_README_MARKERS) + len(REQUIRED_REVIEW_CHECKLIST_MARKERS) + len(REQUIRED_FREEZE_MAP_MARKERS) + len(REQUIRED_MAKEFILE_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS) + len(REQUIRED_PHASE9_BUILD_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
