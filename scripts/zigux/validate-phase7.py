#!/usr/bin/env python3
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
PHASE7_BUILD_PATH = ROOT / "zigux" / "tests" / "phase7_build.zig"

required_files = [
    ROOT / "scripts" / "zigux" / "validate-phase7.py",
    ROOT / "scripts" / "zigux" / "check-phase7-rbtree-parity.py",
    ROOT / "scripts" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "phase7-string-helpers-slice.md",
    ROOT / "Documentation" / "zigux" / "phase7-cmdline-slice.md",
    ROOT / "Documentation" / "zigux" / "phase7-argv-split-slice.md",
    ROOT / "Documentation" / "zigux" / "phase7-rbtree-slice.md",
    ROOT / "zigux" / "Makefile",
    ROOT / "zigux" / "tests" / "README.md",
    ROOT / "zigux" / "tests" / "phase7_build.zig",
    ROOT / "zigux" / "tests" / "phase7_string_helpers.zig",
    ROOT / "zigux" / "tests" / "phase7_cmdline.zig",
    ROOT / "zigux" / "tests" / "phase7_argv_split.zig",
    ROOT / "zigux" / "tests" / "phase7_argv_split_survey.zig",
    ROOT / "zigux" / "tests" / "phase7_argv_split_manifest.json",
    ROOT / "zigux" / "tests" / "phase7_rbtree.zig",
    ROOT / "zigux" / "tests" / "phase7_rbtree_survey.zig",
    ROOT / "zigux" / "tests" / "phase7_rbtree_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_string_helpers_escape_vectors.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_cmdline_next_arg_vectors.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_argv_split_vectors.zig",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_rbtree.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase7_rbtree_c_harness.c",
    ROOT / "lib" / "string_helpers.zig",
    ROOT / "lib" / "cmdline.zig",
    ROOT / "lib" / "argv_split.zig",
    ROOT / "lib" / "rbtree.zig",
    ROOT / ".github" / "workflows" / "zigux-bootstrap.yml",
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print("PHASE7_VALIDATION=fail")
    print("MISSING_PHASE7_FILES_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE7_FILES_END")
    sys.exit(1)

makefile = (ROOT / "zigux" / "Makefile").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
script_readme = (ROOT / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
tests_readme = (ROOT / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
doc_readme = (ROOT / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
phase7_build = (ROOT / "zigux" / "tests" / "phase7_build.zig").read_text(encoding="utf-8")
phase7_argv_split_survey = (ROOT / "zigux" / "tests" / "phase7_argv_split_survey.zig").read_text(encoding="utf-8")
phase7_rbtree_survey = (ROOT / "zigux" / "tests" / "phase7_rbtree_survey.zig").read_text(encoding="utf-8")
phase7_rbtree_doc = (ROOT / "Documentation" / "zigux" / "phase7-rbtree-slice.md").read_text(encoding="utf-8")

required_make_markers = [
    "PHONY += phase7-validate phase7-test phase7",
    "phase7-validate:",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "phase7-test:",
    "$(ZIG) build test --build-file zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_build.zig",
    "phase7: phase7-validate phase7-test",
]

required_workflow_markers = [
    "Validate Phase 7 runtime helper gates",
    "make -C zigux phase7-validate",
    "Run Phase 7 runtime helper tests",
    "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    "zigux/tests/phase7_build.zig",
]

required_script_readme_markers = [
    "validate-phase7.py",
    "check-phase7-rbtree-parity.py",
    "Phase 7 flow",
    "make -C zigux phase7-validate",
    "make -C zigux phase7-test",
    "make -C zigux phase7",
    "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    "zigux/tests/phase7_build.zig",
    "phase7_argv_split_manifest.json",
    "phase7_rbtree_manifest.json",
    "phase7-rbtree-slice.md",
]

required_tests_readme_markers = [
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_survey.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/phase7_rbtree.zig",
    "zigux/tests/phase7_rbtree_survey.zig",
    "zigux/tests/phase7_rbtree_manifest.json",
    "zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig",
    "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "zigux/tests/fixtures/phase7_rbtree.json",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "helper roots in `zigux/tests/phase7_build.zig` receive `string_helpers`, `cmdline`, `argv_split`, and `rbtree` through `addImport(...)`",
    "`zigux/tests/phase7_argv_split_survey.zig` and `zigux/tests/phase7_rbtree_survey.zig` rely on repo-root reads of `zigux/tests/phase7_argv_split_manifest.json` and `zigux/tests/phase7_rbtree_manifest.json`",
]

required_doc_readme_markers = [
    "Phase 7 notes",
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "Documentation/zigux/phase7-cmdline-slice.md",
    "Documentation/zigux/phase7-argv-split-slice.md",
    "Documentation/zigux/phase7-rbtree-slice.md",
    "python3 scripts/zigux/validate-phase7.py",
    "make -C zigux phase7-validate",
    "make -C zigux phase7-test",
    "make -C zigux phase7",
    "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    "python3 scripts/zigux/check-phase7-rbtree-parity.py",
    "zigux/tests/phase7_build.zig",
    "the current Phase 7 build handoff is intentionally split",
    "explicit `addImport(...)` aliases",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/phase7_rbtree_manifest.json",
]

required_phase7_build_markers = [
    "fn createImportedTestRoot(",
    "fn createStandaloneTestRoot(",
    "fn addTestRun(",
    "../../lib/string_helpers.zig",
    "../../lib/cmdline.zig",
    "../../lib/argv_split.zig",
    "../../lib/rbtree.zig",
    "phase7_string_helpers.zig",
    "phase7_cmdline.zig",
    "phase7_argv_split.zig",
    "phase7_argv_split_survey.zig",
    "phase7_rbtree.zig",
    "phase7_rbtree_survey.zig",
    'root_module.addImport(import_name, imported_module);',
    "Helper tests keep the shipped lib imports explicit, while survey tests stay standalone.",
    "phase7-string-helpers-tests",
    "phase7-cmdline-tests",
    "phase7-argv-split-tests",
    "phase7-argv-split-survey-tests",
    "phase7-rbtree-tests",
    "phase7-rbtree-survey-tests",
    'b.step("test", "Run Phase 7 runtime helper tests")',
]

required_phase7_rbtree_doc_markers = [
    "PHASE7_STATUS=parked",
    "zigux/tests/phase7_build.zig",
    "python3 scripts/zigux/check-phase7-rbtree-parity.py",
    "zigux/tests/fixtures/phase7_rbtree.json",
    "zigux/tests/fixtures/phase7_rbtree_c_harness.c",
]

required_phase7_argv_split_survey_markers = [
    "zigux/tests/phase7_argv_split_manifest.json",
]

required_phase7_rbtree_survey_markers = [
    "zigux/tests/phase7_rbtree_manifest.json",
]

expected_phase7_build_paths = {
    "../../lib/string_helpers.zig",
    "../../lib/cmdline.zig",
    "../../lib/argv_split.zig",
    "../../lib/rbtree.zig",
    "phase7_string_helpers.zig",
    "phase7_cmdline.zig",
    "phase7_argv_split.zig",
    "phase7_argv_split_survey.zig",
    "phase7_rbtree.zig",
    "phase7_rbtree_survey.zig",
}

expected_phase7_import_calls = {
    "string_helpers": r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"phase7_string_helpers\\.zig",\s*"string_helpers",\s*"\.\./\.\./lib/string_helpers\\.zig",',
    "cmdline": r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"phase7_cmdline\\.zig",\s*"cmdline",\s*"\.\./\.\./lib/cmdline\\.zig",',
    "argv_split": r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"phase7_argv_split\\.zig",\s*"argv_split",\s*"\.\./\.\./lib/argv_split\\.zig",',
    "rbtree": r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"phase7_rbtree\\.zig",\s*"rbtree",\s*"\.\./\.\./lib/rbtree\\.zig",',
}

expected_phase7_run_labels = {
    "phase7-string-helpers-tests",
    "phase7-cmdline-tests",
    "phase7-argv-split-tests",
    "phase7-argv-split-survey-tests",
    "phase7-rbtree-tests",
    "phase7-rbtree-survey-tests",
}

unexpected_phase7_build_markers = [
    "../../tools/lib/",
    "zigux/tests/build.zig",
]

checks = [
    ("zigux/Makefile", makefile, required_make_markers),
    (".github/workflows/zigux-bootstrap.yml", workflow, required_workflow_markers),
    ("scripts/zigux/README.md", script_readme, required_script_readme_markers),
    ("zigux/tests/README.md", tests_readme, required_tests_readme_markers),
    ("Documentation/zigux/README.md", doc_readme, required_doc_readme_markers),
    ("zigux/tests/phase7_build.zig", phase7_build, required_phase7_build_markers),
    ("zigux/tests/phase7_argv_split_survey.zig", phase7_argv_split_survey, required_phase7_argv_split_survey_markers),
    ("zigux/tests/phase7_rbtree_survey.zig", phase7_rbtree_survey, required_phase7_rbtree_survey_markers),
    ("Documentation/zigux/phase7-rbtree-slice.md", phase7_rbtree_doc, required_phase7_rbtree_doc_markers),
]

missing_markers: list[tuple[str, str]] = []
for label, content, markers in checks:
    for marker in markers:
        if marker not in content:
            missing_markers.append((label, marker))

if missing_markers:
    print("PHASE7_VALIDATION=fail")
    print("MISSING_PHASE7_MARKERS_START")
    for label, marker in missing_markers:
        print(f"{label}: {marker}")
    print("MISSING_PHASE7_MARKERS_END")
    sys.exit(1)

phase7_build_paths = set(re.findall(r'b\.path\("([^"]+)"\)', phase7_build))
if phase7_build_paths != expected_phase7_build_paths:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_BUILD_PATH_DRIFT_START")
    missing_paths = sorted(expected_phase7_build_paths - phase7_build_paths)
    unexpected_paths = sorted(phase7_build_paths - expected_phase7_build_paths)
    for rel_path in missing_paths:
        print(f"missing:{rel_path}")
    for rel_path in unexpected_paths:
        print(f"unexpected:{rel_path}")
    print("PHASE7_BUILD_PATH_DRIFT_END")
    sys.exit(1)

missing_build_inputs = []
for rel_path in sorted(expected_phase7_build_paths):
    resolved = (PHASE7_BUILD_PATH.parent / rel_path).resolve()
    if not resolved.exists():
        missing_build_inputs.append(str(resolved.relative_to(ROOT)))

if missing_build_inputs:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_BUILD_INPUTS_MISSING_START")
    for rel_path in missing_build_inputs:
        print(rel_path)
    print("PHASE7_BUILD_INPUTS_MISSING_END")
    sys.exit(1)

missing_imports = sorted(
    name
    for name, pattern in expected_phase7_import_calls.items()
    if not re.search(pattern, phase7_build, re.S)
)
if missing_imports:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_BUILD_IMPORT_DRIFT_START")
    for name in missing_imports:
        print(name)
    print("PHASE7_BUILD_IMPORT_DRIFT_END")
    sys.exit(1)

missing_run_labels = sorted(label for label in expected_phase7_run_labels if label not in phase7_build)
if missing_run_labels:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_BUILD_RUN_LABEL_DRIFT_START")
    for label in missing_run_labels:
        print(label)
    print("PHASE7_BUILD_RUN_LABEL_DRIFT_END")
    sys.exit(1)

unexpected_build_hits = [
    marker for marker in unexpected_phase7_build_markers if marker in phase7_build
]
if unexpected_build_hits:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_BUILD_STALE_MARKERS_START")
    for marker in unexpected_build_hits:
        print(marker)
    print("PHASE7_BUILD_STALE_MARKERS_END")
    sys.exit(1)

print("PHASE7_VALIDATION=pass")
print(f"PHASE7_REQUIRED_FILE_COUNT={len(required_files)}")
print(
    "PHASE7_REQUIRED_MARKER_COUNT="
    f"{sum(len(markers) for _, _, markers in checks)}"
)
