#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
BUILD_TEST_NAME_RE = re.compile(r'\.name = "(phase12-[^"]+)"')
BUILD_DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
BUILD_MODULE_RE = re.compile(
    r'const ([A-Za-z0-9_]+) = b\.createModule\(\.\{\s*'
    r'\.root_source_file = b\.path\("([^"]+)"\),',
    re.S,
)
BUILD_IMPORT_RE = re.compile(r'([A-Za-z0-9_]+)\.addImport\("([^"]+)", ([A-Za-z0-9_]+)\);')
BUILD_TEST_ROOT_MODULE_RE = re.compile(
    r'\.name = "(phase12-[^"]+)",\s*'
    r'\.root_module = ([A-Za-z0-9_]+),',
    re.S,
)

REQUIRED_FILES = [
    "scripts/zigux/check-phase12-libbpf-focused-replay.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/validate-phase12.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase12_libbpf_only_build.zig",
    "zigux/tests/phase12_libbpf_manifest.json",
    "zigux/tests/phase12_libbpf_segments.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "Documentation/zigux/phase12-shared-replay-contract.md",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-cross-compile-smoke.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
    "scripts/zigux/check-phase12-release-readiness-packet.py",
    "zigux/tests/phase12_raw_github_coverage_manifest.json",
    "zigux/tests/phase12_raw_github_coverage_survey.zig",
]
EXPECTED_BUILD_TEST_NAMES = [
    "phase12-libbpf-segment-survey-tests",
    "phase12-libbpf-reviewability-tests",
]
EXPECTED_DEPEND_STEPS = [
    "run_phase12_libbpf_segments_tests",
    "run_phase12_libbpf_reviewability_tests",
]
EXPECTED_MODULE_ROOTS = [
    {"module": "phase12_libbpf_segments_module", "path": "phase12_libbpf_segments.zig"},
    {"module": "libbpf_cpu_mask_module", "path": "../../tools/lib/bpf/zigux_segments/cpu_mask.zig"},
    {"module": "libbpf_type_names_module", "path": "../../tools/lib/bpf/zigux_segments/type_names.zig"},
    {"module": "libbpf_logging_module", "path": "../../tools/lib/bpf/zigux_segments/logging.zig"},
    {"module": "libbpf_pin_path_module", "path": "../../tools/lib/bpf/zigux_segments/pin_path.zig"},
    {
        "module": "libbpf_file_path_handle_bridge_module",
        "path": "../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
    },
    {"module": "phase12_libbpf_reviewability_module", "path": "phase12_libbpf_reviewability.zig"},
]
EXPECTED_IMPORTS = [
    {
        "module": "phase12_libbpf_reviewability_module",
        "import_name": "cpu_mask",
        "imported_module": "libbpf_cpu_mask_module",
    },
    {
        "module": "phase12_libbpf_reviewability_module",
        "import_name": "bpf_type_names",
        "imported_module": "libbpf_type_names_module",
    },
    {
        "module": "phase12_libbpf_reviewability_module",
        "import_name": "logging",
        "imported_module": "libbpf_logging_module",
    },
    {
        "module": "phase12_libbpf_reviewability_module",
        "import_name": "pin_path",
        "imported_module": "libbpf_pin_path_module",
    },
    {
        "module": "phase12_libbpf_reviewability_module",
        "import_name": "file_path_handle_bridge",
        "imported_module": "libbpf_file_path_handle_bridge_module",
    },
]
EXPECTED_TEST_ROOT_MODULES = [
    {
        "test": "phase12-libbpf-segment-survey-tests",
        "root_module": "phase12_libbpf_segments_module",
    },
    {
        "test": "phase12-libbpf-reviewability-tests",
        "root_module": "phase12_libbpf_reviewability_module",
    },
]
REVIEWABILITY_MARKERS = [
    'const perf_buffer_poll = @import("../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");',
    "const perf_summary = try perf_buffer_poll.summarizePoll(",
    "try std.testing.expectEqual(perf_buffer_poll.WaitClass.bounded, perf_summary.wait_class);",
]
SURVEY_NOTE_MARKERS = [
    "python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test",
    "python3 scripts/zigux/check-phase12-libbpf-focused-replay.py",
    "zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all",
]
CONTRACT_NOTE_MARKERS = [
    "The focused libbpf-only replay checker is intentionally part of that stack before the broader validator runs",
    "- `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test`",
    "- `zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all`",
    "the same shared contract now also stays coupled to `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-cross-compile-smoke.md`, and `Documentation/zigux/phase12-raw-github-coverage-survey.md`, so the release-facing PMO packet, the approved non-native smoke packet, and the mixed public-read fallback packet name the same pre-replay checker stack instead of drifting into parallel Phase 12 stories.",
]
RELEASE_SURVEY_MARKERS = [
    "scripts/zigux/check-phase12-libbpf-focused-replay.py",
    "zigux/tests/phase12_libbpf_only_build.zig",
    "Documentation/zigux/phase12-shared-replay-contract.md",
    "Documentation/zigux/phase12-cross-compile-smoke.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "while the release packet now also keeps the focused libbpf-only replay shard explicit through `scripts/zigux/check-phase12-libbpf-focused-replay.py` and `zigux/tests/phase12_libbpf_only_build.zig`; public-read fallback still remains shared-tree-only rather than map-pinned or catalog-pinned",
    "Documentation/zigux/phase12-shared-replay-contract.md` now stays inside the same release packet as the shared-versus-focused replay contract note",
]
RELEASE_SURVEY_EXACT_COUNTS = {
    RELEASE_SURVEY_MARKERS[5]: 1,
    RELEASE_SURVEY_MARKERS[6]: 1,
}
CROSS_SMOKE_MARKERS = [
    "python3 scripts/zigux/check-phase12-release-readiness-packet.py",
    "python3 scripts/zigux/validate-phase12.py",
    "make -C zigux phase12-validate",
]
RAW_COVERAGE_MARKERS = [
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "tools/lib/bpf/libbpf.c",
    "shared-tree-only",
]
MANIFEST_MARKERS = [
    "check-phase12-libbpf-focused-replay.py --self-test",
    "check-phase12-libbpf-focused-replay.py",
    "phase12_libbpf_only_build.zig",
]
SCRIPTS_README_BOUNDARY_MARKER = (
    "make -C zigux phase12 keeps the current Phase 12 bundle reviewable through one shared tranche entrypoint "
    "instead of ad hoc complex-driver commands, while the direct `zig build test --build-file "
    "zigux/tests/phase12_libbpf_only_build.zig --summary all` replay intentionally stays outside that "
    "shared wrapper as the dedicated focused libbpf-only shard."
)
SCRIPTS_README_MARKERS = [
    "check-phase12-libbpf-focused-replay.py",
    "phase12_libbpf_only_build.zig",
    "focused libbpf-only replay hook",
]
SCRIPTS_README_EXACT_COUNTS = {
    SCRIPTS_README_BOUNDARY_MARKER: 1,
}
DOCS_ROOT_README_MARKERS = [
    "the active Phase 12 heavy-helper survey packet now also keeps the bounded `tools/lib/bpf/zigux_segments/` helper foundations, the reproducibility snapshot, the focused libbpf-only replay shard rooted in `scripts/zigux/check-phase12-libbpf-focused-replay.py` plus `zigux/tests/phase12_libbpf_only_build.zig`, the still-deferred file-path-and-handle bridge and perf-buffer-online-cpu-routing boundaries, and the blocked object-model, loader, and relocation split visible from the top-level docs index.",
]
DOCS_ROOT_README_EXACT_COUNTS = {
    DOCS_ROOT_README_MARKERS[0]: 1,
}
TESTS_README_MARKERS = [
    "keep `Documentation/zigux/phase12-shared-replay-contract.md`, `zigux/tests/phase12_build.zig`, `zigux/tests/phase12_libbpf_only_build.zig`, `scripts/zigux/check-phase12-libbpf-focused-replay.py`, `scripts/zigux/validate-phase12.py`, and `zigux/tests/phase12_libbpf_manifest.json` aligned so the tests root names the same shared-versus-focused libbpf replay boundary as the docs-root contract note instead of leaving the dedicated shard implied behind the broader shared build inventory.",
]
TESTS_README_EXACT_COUNTS = {
    TESTS_README_MARKERS[0]: 1,
}
REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the focused Phase 12 libbpf-only replay packet, do `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test`, `scripts/zigux/check-phase12-libbpf-focused-replay.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_libbpf_only_build.zig`, `zigux/tests/phase12_libbpf_manifest.json`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` still agree on the same dedicated replay shard, review-note hook, and validator-first rollback path instead of leaving that narrower libbpf gate implied behind the broader packet checks?",
]
REVIEW_CHECKLIST_EXACT_COUNTS = {
    REVIEW_CHECKLIST_MARKERS[0]: 1,
}
VALIDATE_PHASE12_MARKERS = [
    "check-phase12-libbpf-focused-replay.py --self-test",
    "check-phase12-libbpf-focused-replay.py",
    "phase12_libbpf_only_build.zig",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]
VALIDATE_PHASE12_EXACT_COUNTS = {
    REVIEW_CHECKLIST_MARKERS[0]: 1,
}
MAKEFILE_MARKERS = [
    "scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test",
    "scripts/zigux/check-phase12-libbpf-focused-replay.py",
]
MAKEFILE_EXACT_COUNTS = {
    "scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test": 1,
    "scripts/zigux/check-phase12-libbpf-focused-replay.py": 2,
}
WORKFLOW_MARKERS = [
    "check-phase12-libbpf-focused-replay.py --self-test",
    "check-phase12-libbpf-focused-replay.py",
]
WORKFLOW_EXACT_COUNTS = {
    "check-phase12-libbpf-focused-replay.py --self-test": 1,
    "check-phase12-libbpf-focused-replay.py": 2,
}


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def collect_marker_misses(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


def collect_exact_count_misses(text: str, expected_counts: dict[str, int], prefix: str) -> list[str]:
    missing: list[str] = []
    for marker, expected_count in expected_counts.items():
        actual_count = text.count(marker)
        if actual_count != expected_count:
            missing.append(f"{prefix}:{marker}:expected={expected_count}:actual={actual_count}")
    return missing


def collect_build_misses(build_text: str) -> list[str]:
    missing: list[str] = []

    actual_build_test_names = BUILD_TEST_NAME_RE.findall(build_text)
    if actual_build_test_names != EXPECTED_BUILD_TEST_NAMES:
        missing.append("build:build_test_names")

    actual_depend_steps = BUILD_DEPEND_STEP_RE.findall(build_text)
    if actual_depend_steps != EXPECTED_DEPEND_STEPS:
        missing.append("build:shared_test_depend_steps")

    actual_module_roots = [
        {"module": module_name, "path": root_path}
        for module_name, root_path in BUILD_MODULE_RE.findall(build_text)
    ]
    if actual_module_roots != EXPECTED_MODULE_ROOTS:
        missing.append("build:module_root_source_files")

    actual_imports = [
        {
            "module": module_name,
            "import_name": import_name,
            "imported_module": imported_module,
        }
        for module_name, import_name, imported_module in BUILD_IMPORT_RE.findall(build_text)
    ]
    if actual_imports != EXPECTED_IMPORTS:
        missing.append("build:module_imports")

    actual_test_root_modules = [
        {"test": test_name, "root_module": root_module}
        for test_name, root_module in BUILD_TEST_ROOT_MODULE_RE.findall(build_text)
    ]
    if actual_test_root_modules != EXPECTED_TEST_ROOT_MODULES:
        missing.append("build:test_root_modules")

    return missing


def collect_missing(
    *,
    present_files: set[str],
    build_text: str,
    reviewability_text: str,
    survey_note_text: str,
    contract_note_text: str,
    release_survey_text: str,
    cross_smoke_text: str,
    raw_coverage_text: str,
    manifest_text: str,
    scripts_readme_text: str,
    docs_root_readme_text: str,
    tests_readme_text: str,
    review_checklist_text: str,
    validate_phase12_text: str,
    makefile_text: str,
    workflow_text: str,
) -> list[str]:
    missing = [f"missing_file:{path}" for path in REQUIRED_FILES if path not in present_files]
    missing.extend(collect_build_misses(build_text))
    missing.extend(collect_marker_misses(reviewability_text, REVIEWABILITY_MARKERS, "reviewability"))
    missing.extend(collect_marker_misses(survey_note_text, SURVEY_NOTE_MARKERS, "survey_note"))
    missing.extend(collect_marker_misses(contract_note_text, CONTRACT_NOTE_MARKERS, "contract_note"))
    missing.extend(collect_marker_misses(release_survey_text, RELEASE_SURVEY_MARKERS, "release_survey"))
    missing.extend(
        collect_exact_count_misses(
            release_survey_text,
            RELEASE_SURVEY_EXACT_COUNTS,
            "release_survey_count",
        )
    )
    missing.extend(collect_marker_misses(cross_smoke_text, CROSS_SMOKE_MARKERS, "cross_smoke"))
    missing.extend(collect_marker_misses(raw_coverage_text, RAW_COVERAGE_MARKERS, "raw_coverage"))
    missing.extend(collect_marker_misses(manifest_text, MANIFEST_MARKERS, "manifest"))
    missing.extend(collect_marker_misses(scripts_readme_text, SCRIPTS_README_MARKERS, "scripts_readme"))
    missing.extend(
        collect_exact_count_misses(
            scripts_readme_text,
            SCRIPTS_README_EXACT_COUNTS,
            "scripts_readme_count",
        )
    )
    missing.extend(collect_marker_misses(docs_root_readme_text, DOCS_ROOT_README_MARKERS, "docs_root_readme"))
    missing.extend(
        collect_exact_count_misses(
            docs_root_readme_text,
            DOCS_ROOT_README_EXACT_COUNTS,
            "docs_root_readme_count",
        )
    )
    missing.extend(collect_marker_misses(tests_readme_text, TESTS_README_MARKERS, "tests_readme"))
    missing.extend(
        collect_exact_count_misses(
            tests_readme_text,
            TESTS_README_EXACT_COUNTS,
            "tests_readme_count",
        )
    )
    missing.extend(collect_marker_misses(review_checklist_text, REVIEW_CHECKLIST_MARKERS, "review_checklist"))
    missing.extend(
        collect_exact_count_misses(
            review_checklist_text,
            REVIEW_CHECKLIST_EXACT_COUNTS,
            "review_checklist_count",
        )
    )
    missing.extend(collect_marker_misses(validate_phase12_text, VALIDATE_PHASE12_MARKERS, "validate_phase12"))
    missing.extend(
        collect_exact_count_misses(
            validate_phase12_text,
            VALIDATE_PHASE12_EXACT_COUNTS,
            "validate_phase12_count",
        )
    )
    missing.extend(collect_marker_misses(makefile_text, MAKEFILE_MARKERS, "makefile"))
    missing.extend(collect_exact_count_misses(makefile_text, MAKEFILE_EXACT_COUNTS, "makefile_count"))
    missing.extend(collect_marker_misses(workflow_text, WORKFLOW_MARKERS, "workflow"))
    missing.extend(collect_exact_count_misses(workflow_text, WORKFLOW_EXACT_COUNTS, "workflow_count"))
    return missing


def build_synthetic_build_text() -> str:
    lines: list[str] = []
    for module in EXPECTED_MODULE_ROOTS:
        lines.extend(
            [
                f'const {module["module"]} = b.createModule(.{{',
                f'    .root_source_file = b.path("{module["path"]}"),',
                "});",
            ]
        )
    for item in EXPECTED_IMPORTS:
        lines.append(
            f'{item["module"]}.addImport("{item["import_name"]}", {item["imported_module"]});'
        )
    for item in EXPECTED_TEST_ROOT_MODULES:
        lines.extend(
            [
                "const test_target = b.addTest(.{",
                f'    .name = "{item["test"]}",',
                f'    .root_module = {item["root_module"]},',
                "});",
            ]
        )
    for step in EXPECTED_DEPEND_STEPS:
        lines.append(f"test_step.dependOn(&{step}.step);")
    return "\n".join(lines) + "\n"


def build_live_inputs() -> dict[str, object]:
    return {
        "present_files": {path for path in REQUIRED_FILES if (ROOT / path).exists()},
        "build_text": read_text("zigux/tests/phase12_libbpf_only_build.zig"),
        "reviewability_text": read_text("zigux/tests/phase12_libbpf_reviewability.zig"),
        "survey_note_text": read_text("Documentation/zigux/phase12-libbpf-segment-survey.md"),
        "contract_note_text": read_text("Documentation/zigux/phase12-shared-replay-contract.md"),
        "release_survey_text": read_text("Documentation/zigux/phase12-release-readiness-survey.md"),
        "cross_smoke_text": read_text("Documentation/zigux/phase12-cross-compile-smoke.md"),
        "raw_coverage_text": read_text("Documentation/zigux/phase12-raw-github-coverage-survey.md"),
        "manifest_text": read_text("zigux/tests/phase12_libbpf_manifest.json"),
        "scripts_readme_text": read_text("scripts/zigux/README.md"),
        "docs_root_readme_text": read_text("Documentation/zigux/README.md"),
        "tests_readme_text": read_text("zigux/tests/README.md"),
        "review_checklist_text": read_text("Documentation/zigux/review-checklist.md"),
        "validate_phase12_text": read_text("scripts/zigux/validate-phase12.py"),
        "makefile_text": read_text("zigux/Makefile"),
        "workflow_text": read_text(".github/workflows/zigux-bootstrap.yml"),
    }


def expect_contains(label: str, missing: list[str], expected_item: str) -> None:
    if expected_item not in missing:
        raise SystemExit(f"phase12-libbpf-focused-replay-self-test:{label}:{expected_item}")


def run_self_test() -> int:
    base_inputs = {
        "present_files": set(REQUIRED_FILES),
        "build_text": build_synthetic_build_text(),
        "reviewability_text": "\n".join(REVIEWABILITY_MARKERS) + "\n",
        "survey_note_text": "\n".join(SURVEY_NOTE_MARKERS) + "\n",
        "contract_note_text": "\n".join(CONTRACT_NOTE_MARKERS) + "\n",
        "release_survey_text": "\n".join(RELEASE_SURVEY_MARKERS) + "\n",
        "cross_smoke_text": "\n".join(CROSS_SMOKE_MARKERS) + "\n",
        "raw_coverage_text": "\n".join(RAW_COVERAGE_MARKERS) + "\n",
        "manifest_text": "\n".join(MANIFEST_MARKERS) + "\n",
        "scripts_readme_text": "\n".join([*SCRIPTS_README_MARKERS, SCRIPTS_README_BOUNDARY_MARKER]) + "\n",
        "docs_root_readme_text": "\n".join(DOCS_ROOT_README_MARKERS) + "\n",
        "tests_readme_text": "\n".join(TESTS_README_MARKERS) + "\n",
        "review_checklist_text": "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
        "validate_phase12_text": "\n".join(
            [
                REVIEW_CHECKLIST_MARKERS[0],
                *VALIDATE_PHASE12_MARKERS,
            ]
        )
        + "\n",
        "makefile_text": "\n".join(MAKEFILE_MARKERS) + "\n",
        "workflow_text": "\n".join(WORKFLOW_MARKERS) + "\n",
    }

    missing = collect_missing(**base_inputs)
    if missing:
        raise SystemExit(
            "phase12-libbpf-focused-replay-self-test:unexpected_failures:" + ",".join(missing)
        )

    missing = collect_missing(**{**base_inputs, "present_files": set(REQUIRED_FILES[1:])})
    expect_contains("missing_file_detection", missing, f"missing_file:{REQUIRED_FILES[0]}")

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {
                path for path in REQUIRED_FILES if path != "zigux/tests/phase12_libbpf_only_build.zig"
            },
        }
    )
    expect_contains(
        "missing_build_shard_detection",
        missing,
        "missing_file:zigux/tests/phase12_libbpf_only_build.zig",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {
                path for path in REQUIRED_FILES if path != "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"
            },
        }
    )
    expect_contains(
        "perf_buffer_poll_file_detection",
        missing,
        "missing_file:tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {
                path
                for path in REQUIRED_FILES
                if path != "Documentation/zigux/phase12-shared-replay-contract.md"
            },
        }
    )
    expect_contains(
        "contract_note_file_detection",
        missing,
        "missing_file:Documentation/zigux/phase12-shared-replay-contract.md",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "present_files": {path for path in REQUIRED_FILES if path != "zigux/tests/README.md"},
        }
    )
    expect_contains(
        "tests_readme_file_detection",
        missing,
        "missing_file:zigux/tests/README.md",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "build_text": base_inputs["build_text"].replace(
                '    .name = "phase12-libbpf-reviewability-tests",',
                '    .name = "phase12-libbpf-reviewability-drift",',
                1,
            ),
        }
    )
    expect_contains("build_test_name_detection", missing, "build:build_test_names")

    missing = collect_missing(
        **{
            **base_inputs,
            "build_text": base_inputs["build_text"].replace(
                "test_step.dependOn(&run_phase12_libbpf_reviewability_tests.step);\n",
                "",
                1,
            ),
        }
    )
    expect_contains("depend_step_detection", missing, "build:shared_test_depend_steps")

    missing = collect_missing(
        **{
            **base_inputs,
            "build_text": base_inputs["build_text"].replace(
                '    .root_source_file = b.path("phase12_libbpf_reviewability.zig"),',
                '    .root_source_file = b.path("phase12_libbpf_reviewability_drift.zig"),',
                1,
            ),
        }
    )
    expect_contains("module_root_detection", missing, "build:module_root_source_files")

    missing = collect_missing(
        **{
            **base_inputs,
            "build_text": base_inputs["build_text"].replace(
                'phase12_libbpf_reviewability_module.addImport("logging", libbpf_logging_module);',
                'phase12_libbpf_reviewability_module.addImport("logging", libbpf_pin_path_module);',
                1,
            ),
        }
    )
    expect_contains("module_import_detection", missing, "build:module_imports")

    missing = collect_missing(
        **{
            **base_inputs,
            "build_text": base_inputs["build_text"].replace(
                "    .root_module = phase12_libbpf_reviewability_module,",
                "    .root_module = phase12_libbpf_segments_module,",
                1,
            ),
        }
    )
    expect_contains("test_root_module_detection", missing, "build:test_root_modules")

    missing = collect_missing(
        **{
            **base_inputs,
            "reviewability_text": base_inputs["reviewability_text"].replace(
                REVIEWABILITY_MARKERS[0] + "\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "reviewability_import_detection",
        missing,
        f"reviewability:{REVIEWABILITY_MARKERS[0]}",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "reviewability_text": base_inputs["reviewability_text"].replace(
                REVIEWABILITY_MARKERS[1] + "\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "reviewability_summary_detection",
        missing,
        f"reviewability:{REVIEWABILITY_MARKERS[1]}",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "reviewability_text": base_inputs["reviewability_text"].replace(
                REVIEWABILITY_MARKERS[2] + "\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "reviewability_wait_class_detection",
        missing,
        f"reviewability:{REVIEWABILITY_MARKERS[2]}",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "survey_note_text": base_inputs["survey_note_text"].replace(
                "python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "survey_note_marker_detection",
        missing,
        "survey_note:python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "contract_note_text": base_inputs["contract_note_text"].replace(
                CONTRACT_NOTE_MARKERS[0] + "\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "contract_note_marker_detection",
        missing,
        f"contract_note:{CONTRACT_NOTE_MARKERS[0]}",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "release_survey_text": base_inputs["release_survey_text"].replace(
                RELEASE_SURVEY_MARKERS[5] + "\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "release_survey_marker_detection",
        missing,
        f"release_survey:{RELEASE_SURVEY_MARKERS[5]}",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "release_survey_text": base_inputs["release_survey_text"]
            + RELEASE_SURVEY_MARKERS[6]
            + "\n",
        }
    )
    expect_contains(
        "release_survey_exact_count_detection",
        missing,
        f"release_survey_count:{RELEASE_SURVEY_MARKERS[6]}:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "cross_smoke_text": base_inputs["cross_smoke_text"].replace(
                CROSS_SMOKE_MARKERS[0] + "\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "cross_smoke_marker_detection",
        missing,
        f"cross_smoke:{CROSS_SMOKE_MARKERS[0]}",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "raw_coverage_text": base_inputs["raw_coverage_text"].replace(
                RAW_COVERAGE_MARKERS[0] + "\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "raw_coverage_marker_detection",
        missing,
        f"raw_coverage:{RAW_COVERAGE_MARKERS[0]}",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "manifest_text": base_inputs["manifest_text"].replace(
                "phase12_libbpf_only_build.zig\n",
                "",
                1,
            ),
        }
    )
    expect_contains("manifest_marker_detection", missing, "manifest:phase12_libbpf_only_build.zig")

    missing = collect_missing(
        **{
            **base_inputs,
            "scripts_readme_text": base_inputs["scripts_readme_text"].replace(
                "focused libbpf-only replay hook\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "scripts_readme_marker_detection",
        missing,
        "scripts_readme:focused libbpf-only replay hook",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "scripts_readme_text": base_inputs["scripts_readme_text"]
            + SCRIPTS_README_BOUNDARY_MARKER
            + "\n",
        }
    )
    expect_contains(
        "scripts_readme_exact_count_detection",
        missing,
        f"scripts_readme_count:{SCRIPTS_README_BOUNDARY_MARKER}:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "docs_root_readme_text": base_inputs["docs_root_readme_text"].replace(
                DOCS_ROOT_README_MARKERS[0] + "\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "docs_root_readme_marker_detection",
        missing,
        f"docs_root_readme:{DOCS_ROOT_README_MARKERS[0]}",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "docs_root_readme_text": base_inputs["docs_root_readme_text"]
            + DOCS_ROOT_README_MARKERS[0]
            + "\n",
        }
    )
    expect_contains(
        "docs_root_readme_exact_count_detection",
        missing,
        f"docs_root_readme_count:{DOCS_ROOT_README_MARKERS[0]}:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "tests_readme_text": base_inputs["tests_readme_text"].replace(
                TESTS_README_MARKERS[0] + "\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "tests_readme_marker_detection",
        missing,
        f"tests_readme:{TESTS_README_MARKERS[0]}",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "tests_readme_text": base_inputs["tests_readme_text"]
            + TESTS_README_MARKERS[0]
            + "\n",
        }
    )
    expect_contains(
        "tests_readme_exact_count_detection",
        missing,
        f"tests_readme_count:{TESTS_README_MARKERS[0]}:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "review_checklist_text": base_inputs["review_checklist_text"].replace(
                REVIEW_CHECKLIST_MARKERS[0] + "\n",
                "",
            ),
        }
    )
    expect_contains(
        "review_checklist_marker_detection",
        missing,
        f"review_checklist:{REVIEW_CHECKLIST_MARKERS[0]}",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "review_checklist_text": base_inputs["review_checklist_text"]
            + REVIEW_CHECKLIST_MARKERS[0]
            + "\n",
        }
    )
    expect_contains(
        "review_checklist_exact_count_detection",
        missing,
        f"review_checklist_count:{REVIEW_CHECKLIST_MARKERS[0]}:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "validate_phase12_text": base_inputs["validate_phase12_text"]
            .replace(REVIEW_CHECKLIST_MARKERS[0] + "\n", "", 1)
            .replace(
                "zigux/Makefile\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "validate_phase12_marker_detection",
        missing,
        "validate_phase12:zigux/Makefile",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "validate_phase12_text": base_inputs["validate_phase12_text"]
            .replace(REVIEW_CHECKLIST_MARKERS[0] + "\n", "", 1)
            .replace(
                "phase12_libbpf_only_build.zig\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "validate_phase12_build_shard_detection",
        missing,
        "validate_phase12:phase12_libbpf_only_build.zig",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "validate_phase12_text": base_inputs["validate_phase12_text"]
            .replace(REVIEW_CHECKLIST_MARKERS[0] + "\n", "", 1)
            .replace(
                "check-phase12-libbpf-focused-replay.py --self-test\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "validate_phase12_self_test_marker_detection",
        missing,
        "validate_phase12:check-phase12-libbpf-focused-replay.py --self-test",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "validate_phase12_text": base_inputs["validate_phase12_text"]
            + REVIEW_CHECKLIST_MARKERS[0]
            + "\n",
        }
    )
    expect_contains(
        "validate_phase12_exact_count_detection",
        missing,
        f"validate_phase12_count:{REVIEW_CHECKLIST_MARKERS[0]}:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "validate_phase12_text": base_inputs["validate_phase12_text"]
            .replace(REVIEW_CHECKLIST_MARKERS[0] + "\n", "", 1)
            .replace(
                "Documentation/zigux/phase12-libbpf-segment-survey.md\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "validate_phase12_survey_note_detection",
        missing,
        "validate_phase12:Documentation/zigux/phase12-libbpf-segment-survey.md",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "makefile_text": base_inputs["makefile_text"].replace(
                "scripts/zigux/check-phase12-libbpf-focused-replay.py",
                "scripts/zigux/check-phase12-libbpf-focused-replay-drift.py",
            ),
        }
    )
    expect_contains(
        "makefile_marker_detection",
        missing,
        "makefile:scripts/zigux/check-phase12-libbpf-focused-replay.py",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "makefile_text": base_inputs["makefile_text"]
            + "scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test\n",
        }
    )
    expect_contains(
        "makefile_exact_count_detection",
        missing,
        "makefile_count:scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test:expected=1:actual=2",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "workflow_text": base_inputs["workflow_text"].replace(
                "check-phase12-libbpf-focused-replay.py --self-test\n",
                "",
                1,
            ),
        }
    )
    expect_contains(
        "workflow_marker_detection",
        missing,
        "workflow:check-phase12-libbpf-focused-replay.py --self-test",
    )

    missing = collect_missing(
        **{
            **base_inputs,
            "workflow_text": base_inputs["workflow_text"]
            + "check-phase12-libbpf-focused-replay.py\n",
        }
    )
    expect_contains(
        "workflow_exact_count_detection",
        missing,
        "workflow_count:check-phase12-libbpf-focused-replay.py:expected=2:actual=3",
    )

    print("PHASE12_LIBBPF_FOCUSED_REPLAY_SELF_TEST=pass")
    print("PHASE12_LIBBPF_FOCUSED_REPLAY_SELF_TEST_CASE_COUNT=37")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


live_inputs = build_live_inputs()
missing = collect_missing(**live_inputs)
if missing:
    print("PHASE12_LIBBPF_FOCUSED_REPLAY=fail")
    print("PHASE12_LIBBPF_FOCUSED_REPLAY_MISSING_START")
    for item in missing:
        print(item)
    print("PHASE12_LIBBPF_FOCUSED_REPLAY_MISSING_END")
    sys.exit(1)

print("PHASE12_LIBBPF_FOCUSED_REPLAY=pass")
print(f"PHASE12_LIBBPF_FOCUSED_REPLAY_FILE_COUNT={len(REQUIRED_FILES)}")
print(f"PHASE12_LIBBPF_FOCUSED_REPLAY_TEST_COUNT={len(EXPECTED_BUILD_TEST_NAMES)}")
print(f"PHASE12_LIBBPF_FOCUSED_REPLAY_IMPORT_COUNT={len(EXPECTED_IMPORTS)}")
