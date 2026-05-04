#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile


_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) > 2 else _SELF_PATH.parent

README_PATH = "scripts/zigux/README.md"
MAKEFILE_PATH = "zigux/Makefile"
WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
SURVEY_PATH = "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
MODULE_METADATA_SURVEY_PATH = (
    "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md"
)
TRACE_EVENTS_SURVEY_PATH = "Documentation/zigux/phase9-runtime-trace-events-survey.md"
KRETPROBE_SURVEY_PATH = "Documentation/zigux/phase9-runtime-kretprobe-survey.md"
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"
LOADER_SUBSTRATE_PLAN_PATH = (
    "Documentation/zigux/phase9-runtime-loader-substrate-plan.md"
)
SAMPLES_README_PATH = "samples/zigux/README.md"
NON_OWNER_BOUNDARY_SURVEY_PATH = "zigux/tests/runtime_loader_non_owner_boundary_survey.zig"
MODULE_METADATA_SURVEY_TEST_PATH = "zigux/tests/runtime_module_metadata_survey.zig"
LOADER_ALLOCATOR_INIT_FLOW_TEST_PATH = (
    "zigux/tests/runtime_loader_allocator_init_flow.zig"
)
LOADER_SUBSTRATE_CHECKER_PATH = "scripts/zigux/check-phase9-loader-substrate-plan.py"
COMMIT_ALIGNMENT_CHECKER_PATH = (
    "scripts/zigux/check-phase9-runtime-loader-commit-alignment.py"
)
NON_OWNER_BOUNDARY_CHECKER_PATH = "scripts/zigux/check-phase9-loader-non-owner-boundary.py"
MODULE_METADATA_CHECKER_PATH = "scripts/zigux/check-phase9-module-metadata-packet.py"

REQUIRED_FILES = [
    README_PATH,
    MAKEFILE_PATH,
    WORKFLOW_PATH,
    SURVEY_PATH,
    MODULE_METADATA_SURVEY_PATH,
    TRACE_EVENTS_SURVEY_PATH,
    KRETPROBE_SURVEY_PATH,
    PHASE9_BUILD_PATH,
    LOADER_SUBSTRATE_PLAN_PATH,
    SAMPLES_README_PATH,
    NON_OWNER_BOUNDARY_SURVEY_PATH,
    MODULE_METADATA_SURVEY_TEST_PATH,
    LOADER_ALLOCATOR_INIT_FLOW_TEST_PATH,
    LOADER_SUBSTRATE_CHECKER_PATH,
    COMMIT_ALIGNMENT_CHECKER_PATH,
    NON_OWNER_BOUNDARY_CHECKER_PATH,
    MODULE_METADATA_CHECKER_PATH,
]

README_MARKERS = [
    "Phase 9 flow\n",
    "- `validate-phase9.py` is the validator-first entrypoint for the shared runtime-pilot packet across `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`, `zigux/tests/README.md`, `zigux/tests/phase9_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.\n",
    "- `check-phase9-validation-flow.py --self-test` and `check-phase9-validation-flow.py` keep the shared Phase 9 release-discipline route aligned across `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, the loader-gap survey, the module-metadata survey, the trace-events survey, the kretprobe survey, and `zigux/tests/phase9_build.zig` before the broader runtime bundle claims reviewable progress.\n",
    "- `check-phase9-loader-substrate-plan.py --self-test` and `check-phase9-loader-substrate-plan.py` keep `Documentation/zigux/phase9-runtime-loader-substrate-plan.md`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `samples/zigux/README.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `samples/zigux/runtime_trace_events_loader.zig`, and the shared `phase9-validate` route aligned around the manifest-backed catalog and ownership map for the loader-stage packet.\n",
    "- `check-phase9-module-metadata-packet.py --self-test` and `check-phase9-module-metadata-packet.py` keep `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`, `zigux/tests/runtime_module_metadata_manifest.json`, `zigux/tests/runtime_module_metadata_survey.zig`, `zigux/tests/README.md`, `zigux/kernel/runtime_loader.zig`, and the four loader-plan files aligned around the starter-descriptor surface and absent depmod-facing metadata.\n",
    "- `make -C zigux phase9-validate` and `make -C zigux phase9` are the validator-first entrypoints for the shared runtime-pilot packet, while `make -C zigux phase9-loader-gap-survey`, `make -C zigux phase9-loader-commit-alignment-survey`, `make -C zigux phase9-non-owner-boundary-survey`, `make -C zigux phase9-module-metadata-survey`, `make -C zigux phase9-kretprobe-survey`, and `make -C zigux phase9-trace-events-survey` keep the focused survey replays explicit beside `zigux/tests/phase9_build.zig`.\n",
    "- keep the runtime-pilot ownership packet explicit here too: the current Phase 9 evidence stays rooted in the manifest-backed catalog and ownership map, the roadmap selftest-hook markers, and the bounded lifecycle-parity posture instead of implying a ready loadable-module path.\n",
    "- keep `samples/zigux/runtime_trace_events.zig` explicit as the sample-only blocked Phase 9 pilot even though `samples/zigux/runtime_trace_events_loader.zig` is now shipped as a bounded scaffold, and keep `Documentation/zigux/freeze-map.md` plus `kernel/trace/ring_buffer.c` visible at `Study / Boundary Only` inside the same runtime packet.\n",
]

README_EXACT_ONCE_MARKERS = [
    "Phase 9 flow\n",
    "- `check-phase9-validation-flow.py --self-test` and `check-phase9-validation-flow.py` keep the shared Phase 9 release-discipline route aligned across `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, the loader-gap survey, the module-metadata survey, the trace-events survey, the kretprobe survey, and `zigux/tests/phase9_build.zig` before the broader runtime bundle claims reviewable progress.\n",
]

COMMIT_ALIGNMENT_SURVEY_BLOCK = (
    "phase9-loader-commit-alignment-survey:\n"
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test\n"
    "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py\n"
)

MAKEFILE_MARKERS = [
    "PHONY += phase9-validate phase9-test phase9-loader-gap-survey phase9-loader-commit-alignment-survey phase9-non-owner-boundary-survey phase9-module-metadata-survey phase9-kretprobe-survey phase9-trace-events-survey phase9",
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
    COMMIT_ALIGNMENT_SURVEY_BLOCK,
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
    "phase9-loader-gap-survey:\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_loader_gap_survey.zig\n",
    "phase9-loader-commit-alignment-survey:\n",
    "phase9-non-owner-boundary-survey:\n",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_loader_non_owner_boundary_survey.zig\n",
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

SAMPLES_README_MARKERS = [
    "- the current Phase 9 loader-side packet now depends on the shared `zigux/kernel/runtime_loader.zig` `RuntimeLoadRequest` boundary for `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_kretprobe_loader.zig`; keep `samples/zigux/runtime_trace_events_loader.zig` explicit as an adjacent scaffold until the trace-events blocker can truthfully adopt that same shared request path\n",
]

SAMPLES_README_EXACT_ONCE_MARKERS = [
    "- the current Phase 9 loader-side packet now depends on the shared `zigux/kernel/runtime_loader.zig` `RuntimeLoadRequest` boundary for `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_kretprobe_loader.zig`; keep `samples/zigux/runtime_trace_events_loader.zig` explicit as an adjacent scaffold until the trace-events blocker can truthfully adopt that same shared request path\n",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


def count_exact_occurrence(text: str, marker: str) -> int:
    return text.count(marker)


def require_markers(
    failures: list[str], label: str, text: str, markers: list[str], exact_once: list[str]
) -> None:
    for marker in markers:
        if marker not in text:
            failures.append(f"{label}:{marker}")
    for marker in exact_once:
        if count_exact_occurrence(text, marker) != 1:
            failures.append(f"{label}_exact:{marker}")


def validate(root: Path) -> list[str]:
    failures: list[str] = []

    missing_files = collect_missing_files(root)
    if missing_files:
        failures.extend(f"missing_file:{rel_path}" for rel_path in missing_files)
        return failures

    texts = {
        "readme": read_text(root, README_PATH),
        "makefile": read_text(root, MAKEFILE_PATH),
        "workflow": read_text(root, WORKFLOW_PATH),
        "survey": read_text(root, SURVEY_PATH),
        "module_metadata_survey": read_text(root, MODULE_METADATA_SURVEY_PATH),
        "trace_events_survey": read_text(root, TRACE_EVENTS_SURVEY_PATH),
        "kretprobe_survey": read_text(root, KRETPROBE_SURVEY_PATH),
        "phase9_build": read_text(root, PHASE9_BUILD_PATH),
        "loader_substrate_plan": read_text(root, LOADER_SUBSTRATE_PLAN_PATH),
        "samples_readme": read_text(root, SAMPLES_README_PATH),
    }

    require_markers(
        failures,
        "readme",
        texts["readme"],
        README_MARKERS,
        README_EXACT_ONCE_MARKERS,
    )
    require_markers(
        failures,
        "makefile",
        texts["makefile"],
        MAKEFILE_MARKERS,
        MAKEFILE_EXACT_ONCE_MARKERS,
    )
    require_markers(
        failures,
        "workflow",
        texts["workflow"],
        WORKFLOW_MARKERS,
        [],
    )
    require_markers(
        failures,
        "survey",
        texts["survey"],
        SURVEY_MARKERS,
        SURVEY_EXACT_ONCE_MARKERS,
    )
    require_markers(
        failures,
        "module_metadata_survey",
        texts["module_metadata_survey"],
        MODULE_METADATA_SURVEY_MARKERS,
        MODULE_METADATA_SURVEY_EXACT_ONCE_MARKERS,
    )
    require_markers(
        failures,
        "trace_events_survey",
        texts["trace_events_survey"],
        TRACE_EVENTS_SURVEY_MARKERS,
        TRACE_EVENTS_SURVEY_EXACT_ONCE_MARKERS,
    )
    require_markers(
        failures,
        "kretprobe_survey",
        texts["kretprobe_survey"],
        KRETPROBE_SURVEY_MARKERS,
        KRETPROBE_SURVEY_EXACT_ONCE_MARKERS,
    )
    require_markers(
        failures,
        "phase9_build",
        texts["phase9_build"],
        PHASE9_BUILD_MARKERS,
        [],
    )
    require_markers(
        failures,
        "loader_substrate_plan",
        texts["loader_substrate_plan"],
        LOADER_SUBSTRATE_PLAN_MARKERS,
        [],
    )
    require_markers(
        failures,
        "samples_readme",
        texts["samples_readme"],
        SAMPLES_README_MARKERS,
        SAMPLES_README_EXACT_ONCE_MARKERS,
    )

    return failures


def write_fixture_tree(root: Path) -> None:
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
    (root / "zigux").mkdir(parents=True, exist_ok=True)
    (root / ".github/workflows").mkdir(parents=True, exist_ok=True)
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)
    (root / "samples/zigux").mkdir(parents=True, exist_ok=True)

    (root / README_PATH).write_text(
        "\n".join(
            [
                "# scripts/zigux",
                "",
                "This directory holds Zigux-specific bootstrap and validation helpers.",
                "",
                "Phase 9 flow",
                README_MARKERS[1].rstrip("\n"),
                README_MARKERS[2].rstrip("\n"),
                README_MARKERS[3].rstrip("\n"),
                README_MARKERS[4].rstrip("\n"),
                README_MARKERS[5].rstrip("\n"),
                README_MARKERS[6].rstrip("\n"),
                README_MARKERS[7].rstrip("\n"),
                "",
            ]
        ),
        encoding="utf-8",
    )

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
                "phase9-loader-commit-alignment-survey:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-runtime-loader-commit-alignment.py",
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
    (root / SAMPLES_README_PATH).write_text(
        "\n".join(
            [
                "# Zigux Samples",
                "",
                "Later runtime starters, loader-side follow-ons, and blocked pilots",
                SAMPLES_README_MARKERS[0].rstrip("\n"),
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


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise SystemExit(f"selftest_missing_source_marker:{old}")
    return text.replace(old, new, 1)


def expect_failure(label: str, root: Path, expected_failure: str) -> None:
    failures = validate(root)
    if expected_failure not in failures:
        actual = ",".join(failures) if failures else "none"
        raise SystemExit(
            f"phase9-validation-flow-selftest:{label}:expected_failure:{expected_failure}:actual:{actual}"
        )


def mutate_and_expect(
    root: Path, rel_path: str, label: str, old: str, new: str, expected_failure: str
) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(replace_once(original, old, new), encoding="utf-8")
    expect_failure(label, root, expected_failure)
    path.write_text(original, encoding="utf-8")


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

        cases = [
            (
                README_PATH,
                "readme_heading_missing",
                "Phase 9 flow\n",
                "Phase Nine flow\n",
                "readme:Phase 9 flow\n",
            ),
            (
                README_PATH,
                "readme_heading_duplicate",
                "Phase 9 flow\n",
                "Phase 9 flow\nPhase 9 flow\n",
                "readme_exact:Phase 9 flow\n",
            ),
            (
                README_PATH,
                "readme_validation_flow_bullet_missing",
                README_MARKERS[2],
                "",
                f"readme:{README_MARKERS[2]}",
            ),
            (
                README_PATH,
                "readme_validation_flow_bullet_duplicate",
                README_MARKERS[2],
                README_MARKERS[2] + README_MARKERS[2],
                f"readme_exact:{README_MARKERS[2]}",
            ),
            (
                README_PATH,
                "readme_validate_phase9_entrypoint_missing",
                README_MARKERS[1],
                "",
                f"readme:{README_MARKERS[1]}",
            ),
            (
                README_PATH,
                "readme_ownership_bullet_missing",
                README_MARKERS[6],
                "",
                f"readme:{README_MARKERS[6]}",
            ),
            (
                MAKEFILE_PATH,
                "makefile_module_metadata_phony",
                "phase9-module-metadata-survey phase9-kretprobe-survey",
                "phase9-kretprobe-survey",
                f"makefile:{MAKEFILE_MARKERS[0]}",
            ),
            (
                MAKEFILE_PATH,
                "makefile_commit_alignment_survey_block_missing",
                COMMIT_ALIGNMENT_SURVEY_BLOCK,
                "",
                f"makefile:{COMMIT_ALIGNMENT_SURVEY_BLOCK}",
            ),
            (
                MAKEFILE_PATH,
                "makefile_loader_gap_target_duplicate",
                "phase9-loader-gap-survey:\n",
                "phase9-loader-gap-survey:\nphase9-loader-gap-survey:\n",
                "makefile_exact:phase9-loader-gap-survey:\n",
            ),
            (
                MAKEFILE_PATH,
                "makefile_commit_alignment_target_duplicate",
                "phase9-loader-commit-alignment-survey:\n",
                "phase9-loader-commit-alignment-survey:\nphase9-loader-commit-alignment-survey:\n",
                "makefile_exact:phase9-loader-commit-alignment-survey:\n",
            ),
            (
                MAKEFILE_PATH,
                "makefile_trace_events_command_duplicate",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig\n",
                "\tcd $(ZIGUX_ROOT) && $(ZIG) test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig\n\tcd $(ZIGUX_ROOT) && $(ZIG) test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig\n",
                "makefile_exact:\tcd $(ZIGUX_ROOT) && $(ZIG) test --dep runtime_trace_events_sample -Mroot=zigux/tests/runtime_trace_events_survey.zig -Mruntime_trace_events_sample=samples/zigux/runtime_trace_events.zig\n",
            ),
            (
                WORKFLOW_PATH,
                "workflow_validate_step_missing",
                "Validate Phase 9 runtime gates",
                "Validate runtime gates",
                "workflow:Validate Phase 9 runtime gates",
            ),
            (
                SURVEY_PATH,
                "survey_commit_alignment_self_test_missing",
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`\n",
                "",
                "survey:- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py --self-test`\n",
            ),
            (
                SURVEY_PATH,
                "survey_commit_alignment_live_duplicate",
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n",
                "- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n",
                "survey_exact:- `python3 scripts/zigux/check-phase9-runtime-loader-commit-alignment.py`\n",
            ),
            (
                SURVEY_PATH,
                "survey_make_gate_missing",
                "- `make -C zigux phase9-loader-gap-survey`\n",
                "",
                "survey:- `make -C zigux phase9-loader-gap-survey`\n",
            ),
            (
                MODULE_METADATA_SURVEY_PATH,
                "module_metadata_self_test_missing",
                "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`\n",
                "",
                "module_metadata_survey:- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`\n",
            ),
            (
                MODULE_METADATA_SURVEY_PATH,
                "module_metadata_make_duplicate",
                "- `make -C zigux phase9-module-metadata-survey`\n",
                "- `make -C zigux phase9-module-metadata-survey`\n- `make -C zigux phase9-module-metadata-survey`\n",
                "module_metadata_survey_exact:- `make -C zigux phase9-module-metadata-survey`\n",
            ),
            (
                TRACE_EVENTS_SURVEY_PATH,
                "trace_events_build_leg_missing",
                "phase9-runtime-trace-events-survey-tests",
                "phase9-runtime-trace-events-review-tests",
                "trace_events_survey:phase9-runtime-trace-events-survey-tests",
            ),
            (
                TRACE_EVENTS_SURVEY_PATH,
                "trace_events_make_duplicate",
                "- `make -C zigux phase9-trace-events-survey`\n",
                "- `make -C zigux phase9-trace-events-survey`\n- `make -C zigux phase9-trace-events-survey`\n",
                "trace_events_survey_exact:- `make -C zigux phase9-trace-events-survey`\n",
            ),
            (
                KRETPROBE_SURVEY_PATH,
                "kretprobe_loader_leg_missing",
                "phase9-runtime-kretprobe-loader-tests",
                "phase9-runtime-kretprobe-replay-tests",
                "kretprobe_survey:phase9-runtime-kretprobe-loader-tests",
            ),
            (
                KRETPROBE_SURVEY_PATH,
                "kretprobe_make_missing",
                "- `make -C zigux phase9-kretprobe-survey`\n",
                "",
                "kretprobe_survey:- `make -C zigux phase9-kretprobe-survey`\n",
            ),
            (
                PHASE9_BUILD_PATH,
                "phase9_build_non_owner_missing",
                "phase9-runtime-loader-non-owner-boundary-survey-tests",
                "",
                "phase9_build:phase9-runtime-loader-non-owner-boundary-survey-tests",
            ),
            (
                PHASE9_BUILD_PATH,
                "phase9_build_allocator_missing",
                "phase9-runtime-loader-allocator-init-flow-tests",
                "",
                "phase9_build:phase9-runtime-loader-allocator-init-flow-tests",
            ),
            (
                LOADER_SUBSTRATE_PLAN_PATH,
                "loader_plan_allocator_missing",
                "allocator_handoff",
                "allocator boundary",
                "loader_substrate_plan:allocator_handoff",
            ),
            (
                SAMPLES_README_PATH,
                "samples_readme_runtime_load_request_missing",
                SAMPLES_README_MARKERS[0],
                "",
                f"samples_readme:{SAMPLES_README_MARKERS[0]}",
            ),
            (
                SAMPLES_README_PATH,
                "samples_readme_runtime_load_request_duplicate",
                SAMPLES_README_MARKERS[0],
                SAMPLES_README_MARKERS[0] + SAMPLES_README_MARKERS[0],
                f"samples_readme_exact:{SAMPLES_README_MARKERS[0]}",
            ),
        ]

        for rel_path, label, old, new, expected_failure in cases:
            mutate_and_expect(tmp_root, rel_path, label, old, new, expected_failure)

        checker_path = tmp_root / MODULE_METADATA_CHECKER_PATH
        checker_path.unlink()
        expect_failure(
            "module_metadata_checker_file",
            tmp_root,
            f"missing_file:{MODULE_METADATA_CHECKER_PATH}",
        )

    print("PHASE9_VALIDATION_FLOW_SELF_TEST=pass")
    print(f"PHASE9_VALIDATION_FLOW_SELF_TEST_CASE_COUNT={len(cases) + 1}")
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

    marker_count = (
        len(README_MARKERS)
        + len(README_EXACT_ONCE_MARKERS)
        + len(MAKEFILE_MARKERS)
        + len(MAKEFILE_EXACT_ONCE_MARKERS)
        + len(WORKFLOW_MARKERS)
        + len(SURVEY_MARKERS)
        + len(SURVEY_EXACT_ONCE_MARKERS)
        + len(MODULE_METADATA_SURVEY_MARKERS)
        + len(MODULE_METADATA_SURVEY_EXACT_ONCE_MARKERS)
        + len(TRACE_EVENTS_SURVEY_MARKERS)
        + len(TRACE_EVENTS_SURVEY_EXACT_ONCE_MARKERS)
        + len(KRETPROBE_SURVEY_MARKERS)
        + len(KRETPROBE_SURVEY_EXACT_ONCE_MARKERS)
        + len(PHASE9_BUILD_MARKERS)
        + len(LOADER_SUBSTRATE_PLAN_MARKERS)
        + len(SAMPLES_README_MARKERS)
        + len(SAMPLES_README_EXACT_ONCE_MARKERS)
    )

    print("PHASE9_VALIDATION_FLOW=pass")
    print(f"PHASE9_VALIDATION_FLOW_MARKER_COUNT={marker_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
