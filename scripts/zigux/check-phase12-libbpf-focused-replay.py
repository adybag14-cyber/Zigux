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
    "scripts/zigux/validate-phase12.py",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase12_libbpf_only_build.zig",
    "zigux/tests/phase12_libbpf_manifest.json",
    "zigux/tests/phase12_libbpf_segments.zig",
    "zigux/tests/phase12_libbpf_reviewability.zig",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
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
SURVEY_NOTE_MARKERS = [
    "python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test",
    "python3 scripts/zigux/check-phase12-libbpf-focused-replay.py",
    "zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all",
]
MANIFEST_MARKERS = [
    "check-phase12-libbpf-focused-replay.py --self-test",
    "check-phase12-libbpf-focused-replay.py",
    "phase12_libbpf_only_build.zig",
]
SCRIPTS_README_MARKERS = [
    "check-phase12-libbpf-focused-replay.py",
    "phase12_libbpf_only_build.zig",
    "focused libbpf-only replay hook",
]
VALIDATE_PHASE12_MARKERS = [
    "check-phase12-libbpf-focused-replay.py --self-test",
    "check-phase12-libbpf-focused-replay.py",
    "phase12_libbpf_only_build.zig",
    "Documentation/zigux/phase12-libbpf-segment-survey.md",
    "zigux/Makefile",
    ".github/workflows/zigux-bootstrap.yml",
]
MAKEFILE_MARKERS = [
    "scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test",
    "scripts/zigux/check-phase12-libbpf-focused-replay.py",
]
WORKFLOW_MARKERS = [
    "check-phase12-libbpf-focused-replay.py --self-test",
    "check-phase12-libbpf-focused-replay.py",
]


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def collect_marker_misses(text: str, markers: list[str], prefix: str) -> list[str]:
    return [f"{prefix}:{marker}" for marker in markers if marker not in text]


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
    survey_note_text: str,
    manifest_text: str,
    scripts_readme_text: str,
    validate_phase12_text: str,
    makefile_text: str,
    workflow_text: str,
) -> list[str]:
    missing = [f"missing_file:{path}" for path in REQUIRED_FILES if path not in present_files]
    missing.extend(collect_build_misses(build_text))
    missing.extend(collect_marker_misses(survey_note_text, SURVEY_NOTE_MARKERS, "survey_note"))
    missing.extend(collect_marker_misses(manifest_text, MANIFEST_MARKERS, "manifest"))
    missing.extend(collect_marker_misses(scripts_readme_text, SCRIPTS_README_MARKERS, "scripts_readme"))
    missing.extend(collect_marker_misses(validate_phase12_text, VALIDATE_PHASE12_MARKERS, "validate_phase12"))
    missing.extend(collect_marker_misses(makefile_text, MAKEFILE_MARKERS, "makefile"))
    missing.extend(collect_marker_misses(workflow_text, WORKFLOW_MARKERS, "workflow"))
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
        "survey_note_text": read_text("Documentation/zigux/phase12-libbpf-segment-survey.md"),
        "manifest_text": read_text("zigux/tests/phase12_libbpf_manifest.json"),
        "scripts_readme_text": read_text("scripts/zigux/README.md"),
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
        "survey_note_text": "\n".join(SURVEY_NOTE_MARKERS) + "\n",
        "manifest_text": "\n".join(MANIFEST_MARKERS) + "\n",
        "scripts_readme_text": "\n".join(SCRIPTS_README_MARKERS) + "\n",
        "validate_phase12_text": "\n".join(VALIDATE_PHASE12_MARKERS) + "\n",
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
            "validate_phase12_text": base_inputs["validate_phase12_text"].replace(
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

    print("PHASE12_LIBBPF_FOCUSED_REPLAY_SELF_TEST=pass")
    print("PHASE12_LIBBPF_FOCUSED_REPLAY_SELF_TEST_CASE_COUNT=10")
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