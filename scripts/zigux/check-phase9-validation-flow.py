#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile


_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) > 2 else _SELF_PATH.parent

MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
SURVEY_PATH = "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
MODULE_METADATA_SURVEY_PATH = "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md"
TRACE_EVENTS_SURVEY_PATH = "Documentation/zigux/phase9-runtime-trace-events-survey.md"
KRETPROBE_SURVEY_PATH = "Documentation/zigux/phase9-runtime-kretprobe-survey.md"
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"
LOADER_SUBSTRATE_PLAN_PATH = "Documentation/zigux/phase9-runtime-loader-substrate-plan.md"
NON_OWNER_BOUNDARY_SURVEY_PATH = "zigux/tests/runtime_loader_non_owner_boundary_survey.zig"
MODULE_METADATA_SURVEY_TEST_PATH = "zigux/tests/runtime_module_metadata_survey.zig"
LOADER_ALLOCATOR_INIT_FLOW_TEST_PATH = "zigux/tests/runtime_loader_allocator_init_flow.zig"
LOADER_SUBSTRATE_CHECKER_PATH = "scripts/zigux/check-phase9-loader-substrate-plan.py"
COMMIT_ALIGNMENT_CHECKER_PATH = "scripts/zigux/check-phase9-runtime-loader-commit-alignment.py"
NON_OWNER_BOUNDARY_CHECKER_PATH = "scripts/zigux/check-phase9-loader-non-owner-boundary.py"
MODULE_METADATA_CHECKER_PATH = "scripts/zigux/check-phase9-module-metadata-packet.py"

REQUIRED_FILES = [
    MAKEFILE_PATH,
    WORKFLOW_PATH,
    SURVEY_PATH,
    MODULE_METADATA_SURVEY_PATH,
    TRACE_EVENTS_SURVEY_PATH,
    KRETPROBE_SURVEY_PATH,
    PHASE9_BUILD_PATH,
    LOADER_SUBSTRATE_PLAN_PATH,
    NON_OWNER_BOUNDARY_SURVEY_PATH,
    MODULE_METADATA_SURVEY_TEST_PATH,
    LOADER_ALLOCATOR_INIT_FLOW_TEST_PATH,
    LOADER_SUBSTRATE_CHECKER_PATH,
    COMMIT_ALIGNMENT_CHECKER_PATH,
    NON_OWNER_BOUNDARY_CHECKER_PATH,
    MODULE_METADATA_CHECKER_PATH,
]

MAKEFILE_MARKERS = [
    "PHONY += phase9-validate phase9-test phase9-loader-gap-survey phase9-non-owner-boundary-survey phase9-module-metadata-survey phase9-kretprobe-survey phase9-trace-events-survey phase9",
    "phase9-validate:",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase9.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-validation-flow.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-module-metadata-packet.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase9.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-validation-flow.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-non-owner-boundary.py\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-module-metadata-packet.py\n",
    "phase9-loader-gap-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_loader_gap_survey.zig\n",
    "phase9-non-owner-boundary-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_loader_non_owner_boundary_survey.zig\n",
    "phase9-module-metadata-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_module_metadata_survey.zig\n",
    "phase9-kretprobe-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_kretprobe_survey.zig\n",
    "phase9-trace-events-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig\n",
    "phase9: phase9-validate phase9-test",
]

MAKEFILE_EXACT_ONCE_MARKERS = [
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test\n",
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py\n",
    "phase9-loader-gap-survey:\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_loader_gap_survey.zig\n",
    "phase9-module-metadata-survey:\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_module_metadata_survey.zig\n",
    "phase9-kretprobe-survey:\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_kretprobe_survey.zig\n",
    "phase9-trace-events-survey:\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig\n",
]

WORKFLOW_MARKERS = [
    "Self-test Phase 9 runtime validator",
    "Validate Phase 9 runtime gates",
    "make -C zigux phase9-validate",
    "Run Phase 9 runtime helper tests",
    "zigux/tests/phase9_build.zig",
]

SURVEY_MARKERS = [
    "- `python3 scripts/zigux/validate-phase9.py --self-test`\n",
    "- `python3 scripts/zigux/check-phase9-validation-flow.py --self-test`\n",
    "- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test`\n",
    "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`\n",
    "- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test`\n",
    "- `python3 scripts/zigux/validate-phase9.py`\n",
    "- `python3 scripts/zigux/check-phase9-validation-flow.py`\n",
    "- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py`\n",
    "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n",
    "- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py`\n",
    "- `make -C zigux phase9-validate`\n",
    "- `make -C zigux phase9-loader-gap-survey`\n",
    "- `make -C zigux phase9`\n",
]

SURVEY_EXACT_ONCE_MARKERS = [
    "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`\n",
    "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n",
    "- `make -C zigux phase9-loader-gap-survey`\n",
]

MODULE_METADATA_SURVEY_MARKERS = [
    "- `python3 scripts/zigux/validate-phase9.py --self-test`\n",
    "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`\n",
    "- `python3 scripts/zigux/validate-phase9.py`\n",
    "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`\n",
    "- `make -C zigux phase9-validate`\n",
    "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`\n",
    "- `zig test zigux/tests/runtime_module_metadata_survey.zig`\n",
    "- `make -C zigux phase9-module-metadata-survey`\n",
]

MODULE_METADATA_SURVEY_EXACT_ONCE_MARKERS = [
    "- `make -C zigux phase9-module-metadata-survey`\n",
]

TRACE_EVENTS_SURVEY_MARKERS = [
    "- `zig test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig`\n",
    "- `make -C zigux phase9-trace-events-survey`\n",
    "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`\n",
    "phase9-runtime-trace-events-module-tests",
    "phase9-runtime-trace-events-survey-tests",
]

TRACE_EVENTS_SURVEY_EXACT_ONCE_MARKERS = [
    "- `make -C zigux phase9-trace-events-survey`\n",
]

KRETPROBE_SURVEY_MARKERS = [
    "- `zig test zigux/tests/runtime_kretprobe_survey.zig`\n",
    "- `make -C zigux phase9-kretprobe-survey`\n",
    "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`\n",
    "- `make -C zigux phase9`\n",
    "phase9-runtime-kretprobe-sample-tests",
    "phase9-runtime-kretprobe-module-tests",
    "phase9-runtime-kretprobe-diff-tests",
    "phase9-runtime-kretprobe-loader-tests",
    "phase9-runtime-kretprobe-survey-tests",
]

KRETPROBE_SURVEY_EXACT_ONCE_MARKERS = [
    "- `make -C zigux phase9-kretprobe-survey`\n",
]

PHASE9_BUILD_MARKERS = [
    "phase9-runtime-loader-gap-survey-tests",
    "phase9-runtime-loader-non-owner-boundary-survey-tests",
    "phase9-runtime-loader-allocator-init-flow-tests",
    "phase9-runtime-module-metadata-survey-tests",
    "phase9-runtime-trace-events-survey-tests",
    "phase9-runtime-kretprobe-survey-tests",
]

LOADER_SUBSTRATE_PLAN_MARKERS = [
    "`PHASE9_SLICE=shared-runtime-loader-substrate-plan`",
    "`zigux/kernel/runtime_loader.zig`",
    "`samples/zigux/runtime_trace_events_loader.zig`",
    "allocator_handoff",
    "make -C zigux phase9-validate",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


def count_exact_occurrence(text: str, marker: str) -> int:
    return text.count(marker)


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    missing_files = collect_missing_files(root)
    if missing_files:
        failures.extend(f"missing_file:{rel_path}" for rel_path in missing_files)
        return failures

    texts = {
        "makefile": read_text(root, MAKEFILE_PATH),
        "workflow": read_text(root, WORKFLOW_PATH),
        "survey": read_text(root, SURVEY_PATH),
        "module_metadata_survey": read_text(root, MODULE_METADATA_SURVEY_PATH),
        "trace_events_survey": read_text(root, TRACE_EVENTS_SURVEY_PATH),
        "kretprobe_survey": read_text(root, KRETPROBE_SURVEY_PATH),
        "phase9_build": read_text(root, PHASE9_BUILD_PATH),
        "loader_substrate_plan": read_text(root, LOADER_SUBSTRATE_PLAN_PATH),
    }

    for marker in MAKEFILE_MARKERS:
        if marker not in texts["makefile"]:
            failures.append(f"makefile:{marker}")
    for marker in MAKEFILE_EXACT_ONCE_MARKERS:
        if count_exact_occurrence(texts["makefile"], marker) != 1:
            failures.append(f"makefile_exact:{marker}")
    for marker in WORKFLOW_MARKERS:
        if marker not in texts["workflow"]:
            failures.append(f"workflow:{marker}")
    for marker in SURVEY_MARKERS:
        if marker not in texts["survey"]:
            failures.append(f"survey:{marker}")
    for marker in SURVEY_EXACT_ONCE_MARKERS:
        if count_exact_occurrence(texts["survey"], marker) != 1:
            failures.append(f"survey_exact:{marker}")
    for marker in MODULE_METADATA_SURVEY_MARKERS:
        if marker not in texts["module_metadata_survey"]:
            failures.append(f"module_metadata_survey:{marker}")
    for marker in MODULE_METADATA_SURVEY_EXACT_ONCE_MARKERS:
        if count_exact_occurrence(texts["module_metadata_survey"], marker) != 1:
            failures.append(f"module_metadata_survey_exact:{marker}")
    for marker in TRACE_EVENTS_SURVEY_MARKERS:
        if marker not in texts["trace_events_survey"]:
            failures.append(f"trace_events_survey:{marker}")
    for marker in TRACE_EVENTS_SURVEY_EXACT_ONCE_MARKERS:
        if count_exact_occurrence(texts["trace_events_survey"], marker) != 1:
            failures.append(f"trace_events_survey_exact:{marker}")
    for marker in KRETPROBE_SURVEY_MARKERS:
        if marker not in texts["kretprobe_survey"]:
            failures.append(f"kretprobe_survey:{marker}")
    for marker in KRETPROBE_SURVEY_EXACT_ONCE_MARKERS:
        if count_exact_occurrence(texts["kretprobe_survey"], marker) != 1:
            failures.append(f"kretprobe_survey_exact:{marker}")
    for marker in PHASE9_BUILD_MARKERS:
        if marker not in texts["phase9_build"]:
            failures.append(f"phase9_build:{marker}")
    for marker in LOADER_SUBSTRATE_PLAN_MARKERS:
        if marker not in texts["loader_substrate_plan"]:
            failures.append(f"loader_substrate_plan:{marker}")

    return failures


def write_fixture_tree(root: Path) -> None:
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
    (root / "zigux").mkdir(parents=True, exist_ok=True)
    (root / ".github/workflows").mkdir(parents=True, exist_ok=True)
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)

    (root / MAKEFILE_PATH).write_text(
        "\n".join(
            [
                MAKEFILE_MARKERS[0],
                "",
                "phase9-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase9.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-validation-flow.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-module-metadata-packet.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase9.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-validation-flow.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-non-owner-boundary.py",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-module-metadata-packet.py",
                "",
                "phase9-test:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase9_build.zig --summary all",
                "",
                "phase9-loader-gap-survey:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_loader_gap_survey.zig",
                "",
                "phase9-non-owner-boundary-survey:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_loader_non_owner_boundary_survey.zig",
                "",
                "phase9-module-metadata-survey:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_module_metadata_survey.zig",
                "",
                "phase9-kretprobe-survey:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_kretprobe_survey.zig",
                "",
                "phase9-trace-events-survey:",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig",
                "",
                "phase9: phase9-validate phase9-test",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / WORKFLOW_PATH).write_text(
        "\n".join(
            [
                "jobs:",
                "  bootstrap:",
                "    steps:",
                "      - name: Self-test Phase 9 runtime validator",
                "        run: python3 scripts/zigux/validate-phase9.py --self-test",
                "      - name: Validate Phase 9 runtime gates",
                "        run: make -C zigux phase9-validate",
                "      - name: Run Phase 9 runtime helper tests",
                "        run: zig build test --build-file zigux/tests/phase9_build.zig --summary all",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / SURVEY_PATH).write_text(
        "\n".join(
            [
                "# Phase 9 Runtime Loader Gap Survey",
                "",
                "## Gates",
                "",
                "- `python3 scripts/zigux/validate-phase9.py --self-test`",
                "- `python3 scripts/zigux/check-phase9-validation-flow.py --self-test`",
                "- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test`",
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`",
                "- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test`",
                "- `python3 scripts/zigux/validate-phase9.py`",
                "- `python3 scripts/zigux/check-phase9-validation-flow.py`",
                "- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py`",
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`",
                "- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py`",
                "- `make -C zigux phase9-validate`",
                "- `make -C zigux phase9-loader-gap-survey`",
                "- `make -C zigux phase9`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / MODULE_METADATA_SURVEY_PATH).write_text(
        "\n".join(
            [
                "# Phase 9 Module Metadata and Depmod Bridge Survey",
                "",
                "## Gates",
                "",
                "- `python3 scripts/zigux/validate-phase9.py --self-test`",
                "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`",
                "- `python3 scripts/zigux/validate-phase9.py`",
                "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`",
                "- `make -C zigux phase9-validate`",
                "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`",
                "- `zig test zigux/tests/runtime_module_metadata_survey.zig`",
                "- `make -C zigux phase9-module-metadata-survey`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / TRACE_EVENTS_SURVEY_PATH).write_text(
        "\n".join(
            [
                "# Phase 9 Runtime Trace-Events Survey",
                "",
                "## Gates",
                "",
                "- `zig test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig`",
                "- `make -C zigux phase9-trace-events-survey`",
                "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`",
                "phase9-runtime-trace-events-module-tests",
                "phase9-runtime-trace-events-survey-tests",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / KRETPROBE_SURVEY_PATH).write_text(
        "\n".join(
            [
                "# Phase 9 Runtime Kretprobe Survey",
                "",
                "## Gates",
                "",
                "- `zig test zigux/tests/runtime_kretprobe_survey.zig`",
                "- `make -C zigux phase9-kretprobe-survey`",
                "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`",
                "- `make -C zigux phase9`",
                "phase9-runtime-kretprobe-sample-tests",
                "phase9-runtime-kretprobe-module-tests",
                "phase9-runtime-kretprobe-diff-tests",
                "phase9-runtime-kretprobe-loader-tests",
                "phase9-runtime-kretprobe-survey-tests",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / PHASE9_BUILD_PATH).write_text(
        "\n".join(
            [
                "phase9-runtime-loader-gap-survey-tests",
                "phase9-runtime-loader-non-owner-boundary-survey-tests",
                "phase9-runtime-loader-allocator-init-flow-tests",
                "phase9-runtime-module-metadata-survey-tests",
                "phase9-runtime-trace-events-survey-tests",
                "phase9-runtime-kretprobe-survey-tests",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / LOADER_SUBSTRATE_PLAN_PATH).write_text(
        "\n".join(
            [
                "# Phase 9 Shared Runtime Loader Substrate Plan",
                "",
                "- `PHASE9_SLICE=shared-runtime-loader-substrate-plan`",
                "- `zigux/kernel/runtime_loader.zig`",
                "- `samples/zigux/runtime_trace_events_loader.zig`",
                "allocator_handoff",
                "make -C zigux phase9-validate",
                "",
            ]
        ),
        encoding="utf-8",
    )
    for rel_path in (
        NON_OWNER_BOUNDARY_SURVEY_PATH,
        MODULE_METADATA_SURVEY_TEST_PATH,
        LOADER_ALLOCATOR_INIT_FLOW_TEST_PATH,
        LOADER_SUBSTRATE_CHECKER_PATH,
        COMMIT_ALIGNMENT_CHECKER_PATH,
        NON_OWNER_BOUNDARY_CHECKER_PATH,
        MODULE_METADATA_CHECKER_PATH,
    ):
        (root / rel_path).write_text("# fixture placeholder\n", encoding="utf-8")


def expect_failure(label: str, root: Path, expected_failure: str) -> None:
    failures = validate(root)
    if expected_failure not in failures:
        actual = ",".join(failures) if failures else "none"
        raise SystemExit(
            f"phase9-validation-flow-selftest:{label}:expected_failure:{expected_failure}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_validation_flow_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        baseline_failures = validate(tmp_root)
        if baseline_failures:
            raise SystemExit(
                "phase9-validation-flow-selftest:baseline_failed:" + ",".join(baseline_failures)
            )

        makefile_path = tmp_root / MAKEFILE_PATH
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "phase9-module-metadata-survey phase9-kretprobe-survey",
                "phase9-kretprobe-survey",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure("module_metadata_phony", tmp_root, f"makefile:{MAKEFILE_MARKERS[0]}")
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-module-metadata-packet.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "module_metadata_self_test_hook",
            tmp_root,
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-module-metadata-packet.py --self-test\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-module-metadata-packet.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "module_metadata_live_hook",
            tmp_root,
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-module-metadata-packet.py\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "commit_alignment_self_test_hook",
            tmp_root,
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "commit_alignment_duplicate_self_test_hook",
            tmp_root,
            "makefile_exact:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "commit_alignment_live_hook",
            tmp_root,
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py\n",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "commit_alignment_duplicate_live_hook",
            tmp_root,
            "makefile_exact:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace("phase9-module-metadata-survey:\n", "", 1),
            encoding="utf-8",
        )
        expect_failure("module_metadata_target", tmp_root, "makefile:phase9-module-metadata-survey:")
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_module_metadata_survey.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "module_metadata_command",
            tmp_root,
            "makefile:\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_module_metadata_survey.zig\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        module_metadata_survey_path = tmp_root / MODULE_METADATA_SURVEY_PATH
        original_module_metadata_survey = module_metadata_survey_path.read_text(encoding="utf-8")
        module_metadata_survey_path.write_text(
            original_module_metadata_survey.replace(
                "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "module_metadata_survey_self_test_gate",
            tmp_root,
            "module_metadata_survey:- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`\n",
        )
        module_metadata_survey_path.write_text(original_module_metadata_survey, encoding="utf-8")

        module_metadata_survey_path.write_text(
            original_module_metadata_survey.replace(
                "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "module_metadata_survey_live_gate",
            tmp_root,
            "module_metadata_survey:- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`\n",
        )
        module_metadata_survey_path.write_text(original_module_metadata_survey, encoding="utf-8")

        module_metadata_survey_path.write_text(
            original_module_metadata_survey.replace(
                "- `make -C zigux phase9-module-metadata-survey`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "module_metadata_survey_make_gate",
            tmp_root,
            "module_metadata_survey:- `make -C zigux phase9-module-metadata-survey`\n",
        )
        module_metadata_survey_path.write_text(original_module_metadata_survey, encoding="utf-8")

        module_metadata_survey_path.write_text(
            original_module_metadata_survey.replace(
                "- `make -C zigux phase9-module-metadata-survey`\n",
                "- `make -C zigux phase9-module-metadata-survey`\n- `make -C zigux phase9-module-metadata-survey`\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "module_metadata_survey_duplicate_make_gate",
            tmp_root,
            "module_metadata_survey_exact:- `make -C zigux phase9-module-metadata-survey`\n",
        )
        module_metadata_survey_path.write_text(original_module_metadata_survey, encoding="utf-8")

        workflow_path = tmp_root / WORKFLOW_PATH
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace("Validate Phase 9 runtime gates", "Validate runtime gates", 1),
            encoding="utf-8",
        )
        expect_failure("workflow_validate_step", tmp_root, "workflow:Validate Phase 9 runtime gates")
        workflow_path.write_text(original_workflow, encoding="utf-8")

        survey_path = tmp_root / SURVEY_PATH
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace(
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "loader_gap_commit_alignment_self_test_gate",
            tmp_root,
            "survey:- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`\n",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`\n",
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`\n- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "loader_gap_duplicate_commit_alignment_self_test_gate",
            tmp_root,
            "survey_exact:- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`\n",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "loader_gap_commit_alignment_live_gate",
            tmp_root,
            "survey:- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n",
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "loader_gap_duplicate_commit_alignment_live_gate",
            tmp_root,
            "survey_exact:- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace("- `make -C zigux phase9-loader-gap-survey`\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            "loader_gap_make_gate",
            tmp_root,
            "survey:- `make -C zigux phase9-loader-gap-survey`\n",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "- `make -C zigux phase9-loader-gap-survey`\n",
                "- `make -C zigux phase9-loader-gap-survey`\n- `make -C zigux phase9-loader-gap-survey`\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "loader_gap_duplicate_make_gate",
            tmp_root,
            "survey_exact:- `make -C zigux phase9-loader-gap-survey`\n",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        trace_events_survey_path = tmp_root / TRACE_EVENTS_SURVEY_PATH
        original_trace_events_survey = trace_events_survey_path.read_text(encoding="utf-8")
        trace_events_survey_path.write_text(
            original_trace_events_survey.replace("phase9-runtime-trace-events-survey-tests", "phase9-runtime-trace-events-review-tests", 1),
            encoding="utf-8",
        )
        expect_failure(
            "trace_events_shared_build_leg",
            tmp_root,
            "trace_events_survey:phase9-runtime-trace-events-survey-tests",
        )
        trace_events_survey_path.write_text(original_trace_events_survey, encoding="utf-8")

        trace_events_survey_path.write_text(
            original_trace_events_survey.replace("- `make -C zigux phase9-trace-events-survey`\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            "trace_events_make_gate",
            tmp_root,
            "trace_events_survey:- `make -C zigux phase9-trace-events-survey`\n",
        )
        trace_events_survey_path.write_text(original_trace_events_survey, encoding="utf-8")

        trace_events_survey_path.write_text(
            original_trace_events_survey.replace(
                "- `make -C zigux phase9-trace-events-survey`\n",
                "- `make -C zigux phase9-trace-events-survey`\n- `make -C zigux phase9-trace-events-survey`\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "trace_events_duplicate_make_gate",
            tmp_root,
            "trace_events_survey_exact:- `make -C zigux phase9-trace-events-survey`\n",
        )
        trace_events_survey_path.write_text(original_trace_events_survey, encoding="utf-8")

        kretprobe_survey_path = tmp_root / KRETPROBE_SURVEY_PATH
        original_kretprobe_survey = kretprobe_survey_path.read_text(encoding="utf-8")
        kretprobe_survey_path.write_text(
            original_kretprobe_survey.replace("phase9-runtime-kretprobe-loader-tests", "phase9-runtime-kretprobe-replay-tests", 1),
            encoding="utf-8",
        )
        expect_failure(
            "kretprobe_loader_leg",
            tmp_root,
            "kretprobe_survey:phase9-runtime-kretprobe-loader-tests",
        )
        kretprobe_survey_path.write_text(original_kretprobe_survey, encoding="utf-8")

        kretprobe_survey_path.write_text(
            original_kretprobe_survey.replace("- `make -C zigux phase9-kretprobe-survey`\n", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            "kretprobe_make_gate",
            tmp_root,
            "kretprobe_survey:- `make -C zigux phase9-kretprobe-survey`\n",
        )
        kretprobe_survey_path.write_text(original_kretprobe_survey, encoding="utf-8")

        kretprobe_survey_path.write_text(
            original_kretprobe_survey.replace(
                "- `make -C zigux phase9-kretprobe-survey`\n",
                "- `make -C zigux phase9-kretprobe-survey`\n- `make -C zigux phase9-kretprobe-survey`\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "kretprobe_duplicate_make_gate",
            tmp_root,
            "kretprobe_survey_exact:- `make -C zigux phase9-kretprobe-survey`\n",
        )
        kretprobe_survey_path.write_text(original_kretprobe_survey, encoding="utf-8")

        phase9_build_path = tmp_root / PHASE9_BUILD_PATH
        original_phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            original_phase9_build.replace("phase9-runtime-loader-non-owner-boundary-survey-tests", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            "phase9_build_non_owner_boundary_leg",
            tmp_root,
            "phase9_build:phase9-runtime-loader-non-owner-boundary-survey-tests",
        )
        phase9_build_path.write_text(original_phase9_build, encoding="utf-8")

        phase9_build_path.write_text(
            original_phase9_build.replace("phase9-runtime-loader-allocator-init-flow-tests", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            "phase9_build_allocator_init_flow_leg",
            tmp_root,
            "phase9_build:phase9-runtime-loader-allocator-init-flow-tests",
        )
        phase9_build_path.write_text(original_phase9_build, encoding="utf-8")

        phase9_build_path.write_text(
            original_phase9_build.replace("phase9-runtime-module-metadata-survey-tests", "", 1),
            encoding="utf-8",
        )
        expect_failure(
            "phase9_build_module_metadata_leg",
            tmp_root,
            "phase9_build:phase9-runtime-module-metadata-survey-tests",
        )
        phase9_build_path.write_text(original_phase9_build, encoding="utf-8")

        loader_substrate_plan_path = tmp_root / LOADER_SUBSTRATE_PLAN_PATH
        original_loader_substrate_plan = loader_substrate_plan_path.read_text(encoding="utf-8")
        loader_substrate_plan_path.write_text(
            original_loader_substrate_plan.replace("allocator_handoff", "allocator boundary", 1),
            encoding="utf-8",
        )
        expect_failure(
            "loader_substrate_allocator_marker",
            tmp_root,
            "loader_substrate_plan:allocator_handoff",
        )
        loader_substrate_plan_path.write_text(original_loader_substrate_plan, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "phase9-module-metadata-survey:\n",
                "phase9-module-metadata-survey:\n\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_module_metadata_survey.zig\n\nphase9-module-metadata-survey:\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "module_metadata_duplicate_target",
            tmp_root,
            "makefile_exact:phase9-module-metadata-survey:\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "phase9-kretprobe-survey:\n",
                "phase9-kretprobe-survey:\n\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_kretprobe_survey.zig\n\nphase9-kretprobe-survey:\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "kretprobe_duplicate_target",
            tmp_root,
            "makefile_exact:phase9-kretprobe-survey:\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_kretprobe_survey.zig\n",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_kretprobe_survey.zig\n\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_kretprobe_survey.zig\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "kretprobe_duplicate_command",
            tmp_root,
            "makefile_exact:\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_kretprobe_survey.zig\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "phase9-trace-events-survey:\n",
                "phase9-trace-events-survey:\n\tcd $(ZIGUX_ROOT) && $(ZIG) test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig\n\nphase9-trace-events-survey:\n",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure(
            "trace_events_duplicate_target",
            tmp_root,
            "makefile_exact:phase9-trace-events-survey:\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        checker_path = tmp_root / MODULE_METADATA_CHECKER_PATH
        checker_path.unlink()
        expect_failure(
            "module_metadata_checker_file",
            tmp_root,
            f"missing_file:{MODULE_METADATA_CHECKER_PATH}",
        )

    print("PHASE9_VALIDATION_FLOW_SELF_TEST=pass")
    print("PHASE9_VALIDATION_FLOW_SELF_TEST_CASE_COUNT=31")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 9 validation-flow review surface."
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
        help="Run the built-in fixture-based self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        print("PHASE9_VALIDATION_FLOW=fail")
        print("PHASE9_VALIDATION_FLOW_FAILURES_START")
        for failure in failures:
            print(failure)
        print("PHASE9_VALIDATION_FLOW_FAILURES_END")
        return 1

    print("PHASE9_VALIDATION_FLOW=pass")
    print(
        "PHASE9_VALIDATION_FLOW_MARKER_COUNT="
        f"{len(MAKEFILE_MARKERS) + len(MAKEFILE_EXACT_ONCE_MARKERS) + len(WORKFLOW_MARKERS) + len(SURVEY_MARKERS) + len(SURVEY_EXACT_ONCE_MARKERS) + len(MODULE_METADATA_SURVEY_MARKERS) + len(MODULE_METADATA_SURVEY_EXACT_ONCE_MARKERS) + len(TRACE_EVENTS_SURVEY_MARKERS) + len(TRACE_EVENTS_SURVEY_EXACT_ONCE_MARKERS) + len(KRETPROBE_SURVEY_MARKERS) + len(KRETPROBE_SURVEY_EXACT_ONCE_MARKERS) + len(PHASE9_BUILD_MARKERS) + len(LOADER_SUBSTRATE_PLAN_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
