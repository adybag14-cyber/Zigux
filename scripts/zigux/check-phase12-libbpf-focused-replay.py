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


def run_self_test() -> int:
    if len(REQUIRED_FILES) != 9:
        raise SystemExit("phase12-libbpf-focused-replay-self-test:required_file_count")
    if EXPECTED_BUILD_TEST_NAMES != [
        "phase12-libbpf-segment-survey-tests",
        "phase12-libbpf-reviewability-tests",
    ]:
        raise SystemExit("phase12-libbpf-focused-replay-self-test:build_test_names")
    if EXPECTED_DEPEND_STEPS != [
        "run_phase12_libbpf_segments_tests",
        "run_phase12_libbpf_reviewability_tests",
    ]:
        raise SystemExit("phase12-libbpf-focused-replay-self-test:depend_steps")
    if len(EXPECTED_IMPORTS) != 5:
        raise SystemExit("phase12-libbpf-focused-replay-self-test:import_count")

    # PHASE12_LIBBPF_FOCUSED_REPLAY_SELF_TEST_PASS_TOKEN
    print("PHASE12_LIBBPF_FOCUSED_REPLAY_SELF_TEST=pass")
    # PHASE12_LIBBPF_FOCUSED_REPLAY_SELF_TEST_CASE_COUNT_TOKEN
    print("PHASE12_LIBBPF_FOCUSED_REPLAY_SELF_TEST_CASE_COUNT=4")
    return 0


if "--self-test" in sys.argv[1:]:
    raise SystemExit(run_self_test())


missing_files = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
if missing_files:
    print("PHASE12_LIBBPF_FOCUSED_REPLAY=fail")
    print("PHASE12_LIBBPF_FOCUSED_REPLAY_MISSING_FILES_START")
    for path in missing_files:
        print(path)
    print("PHASE12_LIBBPF_FOCUSED_REPLAY_MISSING_FILES_END")
    sys.exit(1)

build_text = read_text("zigux/tests/phase12_libbpf_only_build.zig")
survey_note_text = read_text("Documentation/zigux/phase12-libbpf-segment-survey.md")
manifest_text = read_text("zigux/tests/phase12_libbpf_manifest.json")
scripts_readme_text = read_text("scripts/zigux/README.md")
makefile_text = read_text("zigux/Makefile")
workflow_text = read_text(".github/workflows/zigux-bootstrap.yml")

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

for marker in SURVEY_NOTE_MARKERS:
    if marker not in survey_note_text:
        missing.append(f"survey_note:{marker}")

for marker in MANIFEST_MARKERS:
    if marker not in manifest_text:
        missing.append(f"manifest:{marker}")

for marker in SCRIPTS_README_MARKERS:
    if marker not in scripts_readme_text:
        missing.append(f"scripts_readme:{marker}")

for marker in MAKEFILE_MARKERS:
    if marker not in makefile_text:
        missing.append(f"makefile:{marker}")

for marker in WORKFLOW_MARKERS:
    if marker not in workflow_text:
        missing.append(f"workflow:{marker}")

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
