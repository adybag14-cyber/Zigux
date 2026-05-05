#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile


SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[0]

DOCS_README_PATH = "Documentation/zigux/README.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
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
    "`Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds now keep the current runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle reviewable through one shared runtime-loader lane together with the shipped loader facade, contract, shared build, and Linux-style `make -C zigux phase9` replay route instead of widening into ad hoc per-slice checks or overstating removed loader-gap or dedicated-validator surfaces on `master`.",
]

REQUIRED_SCRIPT_README_MARKERS = [
    "Phase 9 flow",
    "`Documentation/zigux/review-checklist.md`",
    "`zig build test --build-file zigux/tests/phase9_build.zig` and `make -C zigux phase9` rerun that same bounded runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle together with the shared runtime-loader facade, loader contract, allocator/init-flow replay, and Linux-style replay route.",
    "there is no dedicated shared `validate-phase9.py`, `check-phase9-validation-flow.py`, or `phase9-validate` target on `master`",
]

REQUIRED_TESTS_README_MARKERS = [
    "keep the bounded Phase 9 runtime-loader packet wired through `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/phase9_build.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `make -C zigux phase9`, the four survey entrypoints `zigux/tests/runtime_atomic64_survey.zig`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_trace_events_survey.zig`, and `zigux/tests/runtime_kretprobe_survey.zig`, the four `samples/zigux/runtime_*_loader.zig` scaffolds, and the shared `zigux/kernel/runtime_loader.zig` plus `zigux/kernel/runtime_loader_contract.zig` surfaces so the loader-handoff packet stays reviewable without implying shared runtime substrate closure or a dedicated `validate-phase9.py` surface that does not exist on `master`",
]

REQUIRED_REVIEW_CHECKLIST_MARKERS = [
    "no dedicated `validate-phase9.py` posture",
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
    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)

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
    for marker in REQUIRED_MAKEFILE_MARKERS:
        if marker not in makefile:
            failures.append(f"makefile:{marker}")
    for marker in REQUIRED_WORKFLOW_MARKERS:
        if marker not in workflow:
            failures.append(f"workflow:{marker}")
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
- `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds now keep the current runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle reviewable through one shared runtime-loader lane together with the shipped loader facade, contract, shared build, and Linux-style `make -C zigux phase9` replay route instead of widening into ad hoc per-slice checks or overstating removed loader-gap or dedicated-validator surfaces on `master`.
""",
    )
    write_text(
        root / SCRIPTS_README_PATH,
        """# scripts/zigux

Phase 9 flow
- the current shared Phase 9 review surface on `master` is `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, the four runtime survey-and-module note pairs (`Documentation/zigux/phase9-runtime-atomic64-module-slice.md`, `Documentation/zigux/phase9-runtime-atomic64-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, and `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`, and `Documentation/zigux/phase9-runtime-kretprobe-survey.md`, `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`, and `Documentation/zigux/phase9-runtime-trace-events-survey.md`), `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds.
- `zig build test --build-file zigux/tests/phase9_build.zig` and `make -C zigux phase9` rerun that same bounded runtime atomic64, bitmap, trace-events, and kretprobe pilot bundle together with the shared runtime-loader facade, loader contract, allocator/init-flow replay, and Linux-style replay route.
- there is no dedicated shared `validate-phase9.py`, `check-phase9-validation-flow.py`, or `phase9-validate` target on `master`; future runtime-pilot follow-through should stay inside the next smallest shared runtime-loader substrate, validation, or review-surface step that keeps those four loader handoffs plus the shared `zigux/kernel/runtime_loader.zig` facade and `zigux/kernel/runtime_loader_contract.zig` allocator/init-flow contract reviewable without widening into a larger runtime-module implementation.
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

- if the change touches the shared Phase 9 runtime-loader packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/review-checklist.md`, the four runtime survey-and-module note pairs, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, and the four `samples/zigux/runtime_*_loader.zig` scaffolds still agree on the same bounded loader-handoff packet and no dedicated `validate-phase9.py` posture without recasting those earlier-phase references as Phase 9 runtime evidence or understating the shipped shared runtime-loader facade, contract, or allocator/init-flow replay on `master`?
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
    write_text(root / PHASE9_BUILD_PATH, "const std = @import(\"std\");\n")
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
        makefile_path = root / MAKEFILE_PATH
        makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.writeText = None
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

        write_fixture_tree(root)
        (root / "Documentation/zigux/phase9-runtime-trace-events-module-slice.md").unlink()
        expect_failure(
            root,
            "missing_file:Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
            "missing_trace_events_module_slice",
        )

    print("PHASE9_BUILD_ONLY_SURFACE_SELF_TEST=pass")
    print("PHASE9_BUILD_ONLY_SURFACE_SELF_TEST_CASE_COUNT=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 9 runtime-loader release surface without inventing a separate validator route."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the current directory.",
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
        f"{len(REQUIRED_DOCS_README_MARKERS) + len(REQUIRED_SCRIPT_README_MARKERS) + len(REQUIRED_TESTS_README_MARKERS) + len(REQUIRED_REVIEW_CHECKLIST_MARKERS) + len(REQUIRED_MAKEFILE_MARKERS) + len(REQUIRED_WORKFLOW_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())