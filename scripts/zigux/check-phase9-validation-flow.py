#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
SURVEY_PATH = "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
MODULE_METADATA_SURVEY_PATH = "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md"
TRACE_EVENTS_SURVEY_PATH = "Documentation/zigux/phase9-runtime-trace-events-survey.md"
LOADER_SUBSTRATE_CHECKER_PATH = "scripts/zigux/check-phase9-loader-substrate-plan.py"
MODULE_METADATA_CHECKER_PATH = "scripts/zigux/check-phase9-module-metadata-packet.py"

REQUIRED_FILES = [
    MAKEFILE_PATH,
    WORKFLOW_PATH,
    SURVEY_PATH,
    MODULE_METADATA_SURVEY_PATH,
    TRACE_EVENTS_SURVEY_PATH,
    LOADER_SUBSTRATE_CHECKER_PATH,
    MODULE_METADATA_CHECKER_PATH,
]

MAKEFILE_MARKERS = [
    "PHONY += phase9-validate phase9-test phase9-loader-gap-survey phase9-kretprobe-survey phase9-trace-events-survey phase9",
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
    "phase9-kretprobe-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_kretprobe_survey.zig\n",
    "phase9-trace-events-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig\n",
    "phase9: phase9-validate phase9-test",
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

MODULE_METADATA_SURVEY_MARKERS = [
    "- `python3 scripts/zigux/validate-phase9.py --self-test`\n",
    "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`\n",
    "- `python3 scripts/zigux/validate-phase9.py`\n",
    "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`\n",
    "- `make -C zigux phase9-validate`\n",
    "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`\n",
    "- `zig test zigux/tests/runtime_module_metadata_survey.zig`\n",
]

TRACE_EVENTS_SURVEY_MARKERS = [
    "- `zig test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig`\n",
    "- `make -C zigux phase9-trace-events-survey`\n",
    "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`\n",
    "phase9-runtime-trace-events-module-tests",
    "phase9-runtime-trace-events-survey-tests",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    missing_files = collect_missing_files(root)
    if missing_files:
        failures.extend(f"missing_file:{rel_path}" for rel_path in missing_files)
        return failures

    makefile = read_text(root, MAKEFILE_PATH)
    workflow = read_text(root, WORKFLOW_PATH)
    survey = read_text(root, SURVEY_PATH)
    module_metadata_survey = read_text(root, MODULE_METADATA_SURVEY_PATH)
    trace_events_survey = read_text(root, TRACE_EVENTS_SURVEY_PATH)

    for marker in MAKEFILE_MARKERS:
        if marker not in makefile:
            failures.append(f"makefile:{marker}")
    for marker in WORKFLOW_MARKERS:
        if marker not in workflow:
            failures.append(f"workflow:{marker}")
    for marker in SURVEY_MARKERS:
        if marker not in survey:
            failures.append(f"survey:{marker}")
    for marker in MODULE_METADATA_SURVEY_MARKERS:
        if marker not in module_metadata_survey:
            failures.append(f"module_metadata_survey:{marker}")
    for marker in TRACE_EVENTS_SURVEY_MARKERS:
        if marker not in trace_events_survey:
            failures.append(f"trace_events_survey:{marker}")

    return failures


def write_fixture_tree(root: Path) -> None:
    (root / "zigux").mkdir(parents=True, exist_ok=True)
    (root / ".github/workflows").mkdir(parents=True, exist_ok=True)
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)

    (root / MAKEFILE_PATH).write_text(
        "\n".join(
            [
                "PHONY += phase9-validate phase9-test phase9-loader-gap-survey phase9-kretprobe-survey phase9-trace-events-survey phase9",
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
                "1. run the validator self-test first",
                "- `python3 scripts/zigux/validate-phase9.py --self-test`",
                "",
                "2. run the shared Phase 9 validation-flow self-test and the dedicated runtime-loader packet self-tests",
                "- `python3 scripts/zigux/check-phase9-validation-flow.py --self-test`",
                "- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test`",
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`",
                "- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test`",
                "",
                "3. run the release-discipline validator and the dedicated runtime-loader packet checks",
                "- `python3 scripts/zigux/validate-phase9.py`",
                "- `python3 scripts/zigux/check-phase9-validation-flow.py`",
                "- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py`",
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`",
                "- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py`",
                "",
                "4. run the shared Phase 9 runtime survey bundle",
                "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`",
                "",
                "5. run the focused loader-gap replay",
                "- `make -C zigux phase9-loader-gap-survey`",
                "",
                "6. run the convenience targets",
                "- `make -C zigux phase9-validate`",
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
                "1. run the shared validator self-test plus the dedicated metadata checker self-test",
                "- `python3 scripts/zigux/validate-phase9.py --self-test`",
                "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`",
                "",
                "2. run the shared validator and the dedicated metadata checker",
                "- `python3 scripts/zigux/validate-phase9.py`",
                "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`",
                "",
                "3. run the shared Phase 9 runtime bundle",
                "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`",
                "",
                "4. run the focused metadata survey replay",
                "- `zig test zigux/tests/runtime_module_metadata_survey.zig`",
                "",
                "5. run the shared convenience target",
                "- `make -C zigux phase9-validate`",
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
                "1. run the focused trace-events survey replays",
                "- `zig test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig`",
                "- `make -C zigux phase9-trace-events-survey`",
                "",
                "2. run the shared Phase 9 runtime packet replay",
                "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`",
                "- this shared build now includes `phase9-runtime-trace-events-module-tests` and `phase9-runtime-trace-events-survey-tests` so the starter, diff, and survey evidence stay explicit in one shared packet",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / LOADER_SUBSTRATE_CHECKER_PATH).write_text(
        "# fixture placeholder for the dedicated loader-substrate-plan checker\n",
        encoding="utf-8",
    )
    (root / MODULE_METADATA_CHECKER_PATH).write_text(
        "# fixture placeholder for the dedicated module-metadata packet checker\n",
        encoding="utf-8",
    )


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    failures = validate(root)
    if expected_marker not in failures:
        actual = ",".join(failures) if failures else "none"
        raise SystemExit(
            f"phase9-validation-flow-selftest:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_validation_flow_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        baseline_failures = validate(tmp_root)
        if baseline_failures:
            raise SystemExit(
                "phase9-validation-flow-selftest:baseline_failed:"
                + ",".join(baseline_failures)
            )

        makefile_path = tmp_root / MAKEFILE_PATH
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-validation-flow.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_flow_self_test_hook",
            tmp_root,
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-validation-flow.py --self-test\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        survey_path = tmp_root / SURVEY_PATH
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace(
                "- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_loader_substrate_gate",
            tmp_root,
            "survey:- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py`\n",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        workflow_path = tmp_root / WORKFLOW_PATH
        original_workflow = workflow_path.read_text(encoding="utf-8")
        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Validate Phase 9 runtime gates\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_phase9_validate_step",
            tmp_root,
            "workflow:Validate Phase 9 runtime gates",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        workflow_path.write_text(
            original_workflow.replace(
                "      - name: Run Phase 9 runtime helper tests\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "workflow_phase9_runtime_helper_step",
            tmp_root,
            "workflow:Run Phase 9 runtime helper tests",
        )
        workflow_path.write_text(original_workflow, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_non_owner_self_test_gate",
            tmp_root,
            "survey:- `python3 scripts/zigux/check-phase9-loader-non-owner-boundary.py --self-test`\n",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_loader_substrate_self_test_hook",
            tmp_root,
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py --self-test\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_loader_substrate_self_test_gate",
            tmp_root,
            "survey:- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test`\n",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "phase9-loader-gap-survey:\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_loader_gap_target",
            tmp_root,
            "makefile:phase9-loader-gap-survey:",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "- `make -C zigux phase9-loader-gap-survey`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_loader_gap_replay",
            tmp_root,
            "survey:- `make -C zigux phase9-loader-gap-survey`\n",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        loader_checker_path = tmp_root / LOADER_SUBSTRATE_CHECKER_PATH
        original_loader_checker = loader_checker_path.read_text(encoding="utf-8")
        loader_checker_path.unlink()
        expect_missing_marker(
            "loader_substrate_checker_file",
            tmp_root,
            "missing_file:scripts/zigux/check-phase9-loader-substrate-plan.py",
        )
        loader_checker_path.write_text(original_loader_checker, encoding="utf-8")

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
        expect_missing_marker(
            "module_metadata_self_test_gate",
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
        expect_missing_marker(
            "module_metadata_live_gate",
            tmp_root,
            "module_metadata_survey:- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`\n",
        )
        module_metadata_survey_path.write_text(original_module_metadata_survey, encoding="utf-8")

        module_metadata_survey_path.write_text(
            original_module_metadata_survey.replace(
                "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "module_metadata_shared_build_gate",
            tmp_root,
            "module_metadata_survey:- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`\n",
        )
        module_metadata_survey_path.write_text(original_module_metadata_survey, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-module-metadata-packet.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_module_metadata_self_test_hook",
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
        expect_missing_marker(
            "makefile_module_metadata_live_hook",
            tmp_root,
            "makefile:\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-module-metadata-packet.py\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        module_metadata_checker_path = tmp_root / MODULE_METADATA_CHECKER_PATH
        original_module_metadata_checker = module_metadata_checker_path.read_text(encoding="utf-8")
        module_metadata_checker_path.unlink()
        expect_missing_marker(
            "module_metadata_checker_file",
            tmp_root,
            "missing_file:scripts/zigux/check-phase9-module-metadata-packet.py",
        )
        module_metadata_checker_path.write_text(original_module_metadata_checker, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "phase9-kretprobe-survey:\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_kretprobe_target",
            tmp_root,
            "makefile:phase9-kretprobe-survey:",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_trace_events_command",
            tmp_root,
            "makefile:\tcd $(ZIGUX_ROOT) && $(ZIG) test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        trace_events_survey_path = tmp_root / TRACE_EVENTS_SURVEY_PATH
        original_trace_events_survey = trace_events_survey_path.read_text(encoding="utf-8")
        trace_events_survey_path.write_text(
            original_trace_events_survey.replace(
                "- `make -C zigux phase9-trace-events-survey`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "trace_events_survey_make_target",
            tmp_root,
            "trace_events_survey:- `make -C zigux phase9-trace-events-survey`\n",
        )
        trace_events_survey_path.write_text(original_trace_events_survey, encoding="utf-8")

        trace_events_survey_path.write_text(
            original_trace_events_survey.replace(
                "phase9-runtime-trace-events-survey-tests",
                "phase9-runtime-trace-events-review-tests",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "trace_events_survey_shared_build_leg",
            tmp_root,
            "trace_events_survey:phase9-runtime-trace-events-survey-tests",
        )
        trace_events_survey_path.write_text(original_trace_events_survey, encoding="utf-8")

        makefile_path.write_text(
            original_makefile.replace(
                "phase9-trace-events-survey:\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_trace_events_target",
            tmp_root,
            "makefile:phase9-trace-events-survey:",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

    print("PHASE9_VALIDATION_FLOW_SELF_TEST=pass")
    print("PHASE9_VALIDATION_FLOW_SELF_TEST_CASE_COUNT=20")
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
        f"PHASE9_VALIDATION_FLOW_MARKER_COUNT={len(MAKEFILE_MARKERS) + len(WORKFLOW_MARKERS) + len(SURVEY_MARKERS) + len(MODULE_METADATA_SURVEY_MARKERS) + len(TRACE_EVENTS_SURVEY_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
