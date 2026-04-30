#!/usr/bin/env python3
import json
from pathlib import Path
import re
import subprocess
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
    ROOT / "zigux" / "tests" / "phase7_string_helpers_survey.zig",
    ROOT / "zigux" / "tests" / "phase7_cmdline.zig",
    ROOT / "zigux" / "tests" / "phase7_cmdline_survey.zig",
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
phase7_string_helpers_tests = (ROOT / "zigux" / "tests" / "phase7_string_helpers.zig").read_text(encoding="utf-8")
phase7_string_helpers_survey = (ROOT / "zigux" / "tests" / "phase7_string_helpers_survey.zig").read_text(encoding="utf-8")
phase7_string_helpers_doc = (ROOT / "Documentation" / "zigux" / "phase7-string-helpers-slice.md").read_text(encoding="utf-8")
phase7_cmdline_survey = (ROOT / "zigux" / "tests" / "phase7_cmdline_survey.zig").read_text(encoding="utf-8")
phase7_cmdline_tests = (ROOT / "zigux" / "tests" / "phase7_cmdline.zig").read_text(encoding="utf-8")
phase7_argv_split_doc = (ROOT / "Documentation" / "zigux" / "phase7-argv-split-slice.md").read_text(encoding="utf-8")
phase7_argv_split_manifest = json.loads(
    (ROOT / "zigux" / "tests" / "phase7_argv_split_manifest.json").read_text(encoding="utf-8")
)
phase7_argv_split_survey = (ROOT / "zigux" / "tests" / "phase7_argv_split_survey.zig").read_text(encoding="utf-8")
phase7_argv_split_tests = (ROOT / "zigux" / "tests" / "phase7_argv_split.zig").read_text(encoding="utf-8")
phase7_rbtree_tests = (ROOT / "zigux" / "tests" / "phase7_rbtree.zig").read_text(encoding="utf-8")
phase7_rbtree_survey = (ROOT / "zigux" / "tests" / "phase7_rbtree_survey.zig").read_text(encoding="utf-8")
phase7_cmdline_doc = (ROOT / "Documentation" / "zigux" / "phase7-cmdline-slice.md").read_text(encoding="utf-8")
phase7_rbtree_doc = (ROOT / "Documentation" / "zigux" / "phase7-rbtree-slice.md").read_text(encoding="utf-8")

required_make_markers = [
    "PHONY += phase7-validate phase7-test phase7",
    "phase7-validate:",
    "scripts/zigux/validate-phase7.py",
    "scripts/zigux/check-phase7-rbtree-parity.py",
    "phase7-test:",
    "$(ZIG) build test --build-file zigux/tests/phase7_build.zig --summary all",
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
    "phase7_string_helpers_survey.zig",
    "phase7_cmdline_survey.zig",
    "phase7_argv_split_manifest.json",
    "phase7_rbtree_manifest.json",
    "phase7-rbtree-slice.md",
    "helper-only string and cmdline slices keep their roadmap-backed review notes explicit",
    "setting those survey runs to `repo_root`",
]

required_tests_readme_markers = [
    "zigux/tests/phase7_build.zig",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_string_helpers_survey.zig",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_cmdline_survey.zig",
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
    "`zigux/tests/phase7_string_helpers_survey.zig` and `zigux/tests/phase7_cmdline_survey.zig` stay standalone so the helper-only string and cmdline slices keep their roadmap-backed review notes explicit without widening into extra helper-local bootstrap rules or later-phase sample claims",
    "`zigux/tests/phase7_argv_split_survey.zig` and `zigux/tests/phase7_rbtree_survey.zig` rely on repo-root reads of `zigux/tests/phase7_argv_split_manifest.json` and `zigux/tests/phase7_rbtree_manifest.json`",
    "phase7_build.zig` keeps those survey runs rooted at `repo_root`",
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
    "zigux/tests/phase7_string_helpers_survey.zig",
    "zigux/tests/phase7_cmdline_survey.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/phase7_rbtree_manifest.json",
    "helper-only string and cmdline slices keep their roadmap and sample-root boundary explicit",
    "running those survey steps from `repo_root`",
]

required_phase7_build_markers = [
    "fn createImportedTestRoot(",
    "fn createStandaloneTestRoot(",
    "fn addTestRun(",
    'const repo_root = b.path("../..");',
    "../../lib/string_helpers.zig",
    "../../lib/cmdline.zig",
    "../../lib/argv_split.zig",
    "../../lib/rbtree.zig",
    "phase7_string_helpers.zig",
    "phase7_string_helpers_survey.zig",
    "phase7_cmdline.zig",
    "phase7_cmdline_survey.zig",
    "phase7_argv_split.zig",
    "phase7_argv_split_survey.zig",
    "phase7_rbtree.zig",
    "phase7_rbtree_survey.zig",
    'root_module.addImport(import_name, imported_module);',
    "Helper tests keep the shipped lib imports explicit, while survey tests stay standalone.",
    "phase7-string-helpers-tests",
    "phase7-string-helpers-survey-tests",
    "phase7-cmdline-tests",
    "phase7-cmdline-survey-tests",
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

required_phase7_string_helpers_survey_markers = [
    "Documentation/zigux/phase7-string-helpers-slice.md",
    "samples/zigux/README.md",
    "no `samples/zigux/*string*` Phase 5 reference sample",
]

required_phase7_string_helpers_test_markers = [
    'const escape_vectors = @import("fixtures/phase7_string_helpers_escape_vectors.zig");',
    "phase 7 parseIntArrayUser keeps count-bounded copy semantics explicit",
    "phase 7 kstrdupQuotable reuses the bounded escape subset for log-safe duplication",
    "phase 7 kstrdupAndReplace keeps ownership and first-NUL replacement boundaries explicit",
    "phase 7 kasprintfStrarray returns sequential owned strings with a null-pointer terminator",
    "phase 7 kfreeStrarray keeps first-NUL prefixes, zero-count reuse, and repeated teardown safe",
    "phase 7 string helper wrappers keep shared any-flag and C-string ownership rules",
]

required_phase7_string_helpers_doc_markers = [
    "PHASE7_STATUS=landed",
    "zigux/tests/phase7_string_helpers.zig",
    "zigux/tests/phase7_string_helpers_survey.zig",
    "zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig",
    "small allocator-backed `parse_int_array()` and `parse_int_array_user()` starters",
    "one log-safe `kstrdup_quotable()` duplication helper",
    "one ownership-safe `kstrdup_and_replace()` duplication helper",
    "one sequential string-array allocator plus teardown starter landed",
    "shared deterministic escape fixtures under `zigux/tests/fixtures/phase7_string_helpers_escape_vectors.zig`",
]

required_phase7_cmdline_survey_markers = [
    "zigux/tests/phase7_cmdline_survey.zig",
    "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
    "helper roots in `zigux/tests/phase7_build.zig` receive `string_helpers`, `cmdline`, `argv_split`, and `rbtree` through `addImport(...)`",
    "cannot import fixtures outside the helper module path",
]

required_phase7_cmdline_test_markers = [
    'const next_arg_vectors = @import("fixtures/phase7_cmdline_next_arg_vectors.zig");',
    "phase 7 getOptions preserves descending-range and partial-parse stop behavior",
    "phase 7 getOptions keeps array-capacity stop behavior explicit when a range is only partially stored",
    "phase 7 memparse preserves suffix scaling and stop index semantics",
    "phase 7 parseOptionStr matches only exact bare options",
    "phase 7 numeric helpers reject explicit leading plus signs to stay with cmdline.c simple_strtoull semantics",
    'try std.testing.expect(!cmdline.parseOptionStr("quiet,debug\\x00,nohlt", "nohlt"));',
    "phase 7 getOption matches malformed-token classification from the Linux KUnit corpus",
    "phase 7 getOption matches leading-integer pointer advance from the Linux KUnit corpus",
    "phase 7 getOption matches trailing-integer pointer advance from the Linux KUnit corpus",
    "phase 7 getOptions matches malformed-range counting from the Linux KUnit corpus",
    "phase 7 nextArg matches serialized edge fixtures",
    'try std.testing.expectEqual(@as(u64, 0), cmdline.memparse("+0x10", &index));',
]

required_phase7_argv_split_survey_markers = [
    "zigux/tests/phase7_argv_split_manifest.json",
]

required_phase7_argv_split_doc_markers = [
    "PHASE7_STATUS=parked",
    "`argv_free()` via `argvFree()`",
    "zigux/tests/phase7_argv_split.zig",
    "zigux/tests/phase7_argv_split_survey.zig",
    "zigux/tests/phase7_argv_split_manifest.json",
    "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "machine-checked survey record",
]

required_phase7_argv_split_test_markers = [
    'const phase7_vectors = @import("fixtures/phase7_argv_split_vectors.zig");',
    "phase 7 argvFree keeps the explicit argv_free ownership mirror reviewable",
    "phase 7 argvSplit deinit stays safe when called after teardown already cleared the result",
    "phase 7 argvSplit frees intermediate allocations when allocator failure interrupts setup",
]

required_phase7_cmdline_doc_markers = [
    "PHASE7_STATUS=parked",
    "zigux/tests/phase7_cmdline.zig",
    "zigux/tests/phase7_cmdline_survey.zig",
    "zigux/tests/fixtures/phase7_cmdline_next_arg_vectors.zig",
    "descending-range and unparseable-suffix early stop behavior",
    "array-capacity stop behavior when a hyphen range is only partially stored and the upper bound remains pending in the remaining cursor",
    "the full KUnit malformed-token classification corpus now also runs through the shared `zigux/tests/phase7_cmdline.zig` gate instead of only the helper-local `zig test lib/cmdline.zig` path",
    "KUnit-derived pointer-advance semantics for malformed-prefix, leading-integer, and trailing-integer `get_option()` inputs",
    "memory-size suffix scaling with accurate parse-stop reporting",
    "rejection of explicit leading-plus numeric inputs, including autodetected radix forms like `+0x10`",
    "exact bare-option matching for comma-delimited flags",
    "C-style stop-at-NUL handling for bare-option scans",
    "serialized `next_arg()` edge cases covering quoted values, quoted bare tokens, empty quoted values, unquoted punctuation-rich values, first-equals splitting, leading-equals sentinel handling, and empty-rest termination",
    "helper-local test runs cannot import that fixture from outside the helper module path; keep both packets aligned when those serialized cases change",
]

required_phase7_rbtree_survey_markers = [
    "zigux/tests/phase7_rbtree_manifest.json",
]

required_phase7_rbtree_test_markers = [
    '@embedFile("fixtures/phase7_rbtree.json")',
    "phase 7 rbtree balancing helpers keep ordered insert erase traversal stable",
    "phase 7 rbtree eraseInit detaches erased nodes for reuse",
    "phase 7 rbtree detached nodes stay non-empty until callers clear them",
    "phase 7 rbtree clearNode marks detached nodes as empty",
    "phase 7 rbtree find helpers walk duplicate-key ranges",
    "phase 7 rbtree iterateMatches streams duplicate-key ranges",
    "phase 7 rbtree findAdd inserts new nodes and returns existing duplicates",
    "phase 7 rbtree postorder traversal matches committed parity fixture",
]

expected_phase7_build_paths = {
    "../..",
    "../../lib/string_helpers.zig",
    "../../lib/cmdline.zig",
    "../../lib/argv_split.zig",
    "../../lib/rbtree.zig",
    "phase7_string_helpers.zig",
    "phase7_string_helpers_survey.zig",
    "phase7_cmdline.zig",
    "phase7_cmdline_survey.zig",
    "phase7_argv_split.zig",
    "phase7_argv_split_survey.zig",
    "phase7_rbtree.zig",
    "phase7_rbtree_survey.zig",
}

expected_phase7_import_calls = {
    "string_helpers": r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"phase7_string_helpers\.zig",\s*"string_helpers",\s*"\.\./\.\./lib/string_helpers\.zig",',
    "cmdline": r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"phase7_cmdline\.zig",\s*"cmdline",\s*"\.\./\.\./lib/cmdline\.zig",',
    "argv_split": r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"phase7_argv_split\.zig",\s*"argv_split",\s*"\.\./\.\./lib/argv_split\.zig",',
    "rbtree": r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"phase7_rbtree\.zig",\s*"rbtree",\s*"\.\./\.\./lib/rbtree\.zig",',
}

expected_phase7_run_labels = {
    "phase7-string-helpers-tests",
    "phase7-string-helpers-survey-tests",
    "phase7-cmdline-tests",
    "phase7-cmdline-survey-tests",
    "phase7-argv-split-tests",
    "phase7-argv-split-survey-tests",
    "phase7-rbtree-tests",
    "phase7-rbtree-survey-tests",
}

expected_phase7_run_cwds = {
    "phase7-string-helpers-tests": "null",
    "phase7-cmdline-tests": "null",
    "phase7-cmdline-survey-tests": "repo_root",
    "phase7-argv-split-tests": "null",
    "phase7-argv-split-survey-tests": "repo_root",
    "phase7-string-helpers-survey-tests": "repo_root",
    "phase7-rbtree-tests": "null",
    "phase7-rbtree-survey-tests": "repo_root",
}

unexpected_phase7_build_markers = [
    "../../tools/lib/",
    "zigux/tests/build.zig",
]

expected_make_expansions = {
    "phase7-validate": [
        "python3 scripts/zigux/validate-phase7.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
    ],
    "phase7-test": [
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    ],
    "phase7": [
        "python3 scripts/zigux/validate-phase7.py",
        "python3 scripts/zigux/check-phase7-rbtree-parity.py",
        "zig build test --build-file zigux/tests/phase7_build.zig --summary all",
    ],
}

checks = [
    ("zigux/Makefile", makefile, required_make_markers),
    (".github/workflows/zigux-bootstrap.yml", workflow, required_workflow_markers),
    ("scripts/zigux/README.md", script_readme, required_script_readme_markers),
    ("zigux/tests/README.md", tests_readme, required_tests_readme_markers),
    ("Documentation/zigux/README.md", doc_readme, required_doc_readme_markers),
    ("zigux/tests/phase7_build.zig", phase7_build, required_phase7_build_markers),
    ("zigux/tests/phase7_string_helpers_survey.zig", phase7_string_helpers_survey, required_phase7_string_helpers_survey_markers),
    ("zigux/tests/phase7_string_helpers.zig", phase7_string_helpers_tests, required_phase7_string_helpers_test_markers),
    ("Documentation/zigux/phase7-string-helpers-slice.md", phase7_string_helpers_doc, required_phase7_string_helpers_doc_markers),
    ("zigux/tests/phase7_cmdline_survey.zig", phase7_cmdline_survey, required_phase7_cmdline_survey_markers),
    ("zigux/tests/phase7_cmdline.zig", phase7_cmdline_tests, required_phase7_cmdline_test_markers),
    ("Documentation/zigux/phase7-argv-split-slice.md", phase7_argv_split_doc, required_phase7_argv_split_doc_markers),
    ("zigux/tests/phase7_argv_split_survey.zig", phase7_argv_split_survey, required_phase7_argv_split_survey_markers),
    ("zigux/tests/phase7_argv_split.zig", phase7_argv_split_tests, required_phase7_argv_split_test_markers),
    ("zigux/tests/phase7_rbtree_survey.zig", phase7_rbtree_survey, required_phase7_rbtree_survey_markers),
    ("zigux/tests/phase7_rbtree.zig", phase7_rbtree_tests, required_phase7_rbtree_test_markers),
    ("Documentation/zigux/phase7-cmdline-slice.md", phase7_cmdline_doc, required_phase7_cmdline_doc_markers),
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

expected_argv_split_gap_destinations = {
    "phase7-build-gate": "zigux/tests/phase7_build.zig",
    "phase7-argv-split-helper": "lib/argv_split.zig",
    "phase7-argv-split-dedicated-tests": "zigux/tests/phase7_argv_split.zig",
    "phase7-argv-split-shared-fixtures": "zigux/tests/fixtures/phase7_argv_split_vectors.zig",
    "phase7-argv-split-slice-note": "Documentation/zigux/phase7-argv-split-slice.md",
    "phase7-argv-split-survey-gate": "zigux/tests/phase7_argv_split_survey.zig",
}

manifest_shape_errors: list[str] = []
if phase7_argv_split_manifest.get("lane_key") != "P7-L12":
    manifest_shape_errors.append("lane_key")
if phase7_argv_split_manifest.get("phase") != "Phase 7":
    manifest_shape_errors.append("phase")
if phase7_argv_split_manifest.get("anchor") != "lib/argv_split.c":
    manifest_shape_errors.append("anchor")
if phase7_argv_split_manifest.get("roadmap_destinations") != ["lib/argv_split.zig"]:
    manifest_shape_errors.append("roadmap_destinations")

survey_summary = phase7_argv_split_manifest.get("survey_summary", {})
expected_summary = {
    "argv_split_c_lines": 95,
    "preexisting_phase7_test_files": 1,
    "preexisting_phase7_fixture_modules": 1,
    "preexisting_phase7_build_present": True,
    "preexisting_phase7_doc_present": True,
    "preexisting_phase7_helper_present": True,
}
for key, expected_value in expected_summary.items():
    if survey_summary.get(key) != expected_value:
        manifest_shape_errors.append(f"survey_summary:{key}")

gaps = phase7_argv_split_manifest.get("gaps")
if not isinstance(gaps, list):
    manifest_shape_errors.append("gaps")
else:
    for gap_id, destination in expected_argv_split_gap_destinations.items():
        matches = [gap for gap in gaps if gap.get("id") == gap_id]
        if len(matches) != 1:
            manifest_shape_errors.append(f"gaps:{gap_id}")
            continue
        gap = matches[0]
        if gap.get("status") != "starter_landed":
            manifest_shape_errors.append(f"gaps:{gap_id}:status")
        if gap.get("zigux_destination") != destination:
            manifest_shape_errors.append(f"gaps:{gap_id}:zigux_destination")
        if not gap.get("why_now"):
            manifest_shape_errors.append(f"gaps:{gap_id}:why_now")

if manifest_shape_errors:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_ARGV_SPLIT_MANIFEST_SHAPE_START")
    for item in manifest_shape_errors:
        print(item)
    print("PHASE7_ARGV_SPLIT_MANIFEST_SHAPE_END")
    sys.exit(1)

phase7_build_paths = set(re.findall(r'b\.path\("([^"]+)"\)', phase7_build))
for root_path, import_path in re.findall(
    r'createImportedTestRoot\(\s*b,\s*target,\s*optimize,\s*"([^"]+)",\s*"[^"]+",\s*"([^"]+)"',
    phase7_build,
    re.S,
):
    phase7_build_paths.add(root_path)
    phase7_build_paths.add(import_path)

for root_path in re.findall(
    r'createStandaloneTestRoot\(\s*b,\s*target,\s*optimize,\s*"([^"]+)"',
    phase7_build,
    re.S,
):
    phase7_build_paths.add(root_path)
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

run_call_pattern = re.compile(
    r'const\s+\w+\s*=\s*addTestRun\(\s*'
    r'b,\s*"([^"]+)",\s*\w+,\s*(null|repo_root)\s*,?\s*\)',
    re.S,
)
actual_run_cwds = {label: cwd for label, cwd in run_call_pattern.findall(phase7_build)}
if actual_run_cwds != expected_phase7_run_cwds:
    print("PHASE7_VALIDATION=fail")
    print("PHASE7_BUILD_CWD_DRIFT_START")
    for label in sorted(expected_phase7_run_cwds):
        actual = actual_run_cwds.get(label)
        expected = expected_phase7_run_cwds[label]
        if actual != expected:
            print(f"{label}: expected={expected} actual={actual or 'missing'}")
    for label in sorted(actual_run_cwds):
        if label not in expected_phase7_run_cwds:
            print(f"{label}: unexpected={actual_run_cwds[label]}")
    print("PHASE7_BUILD_CWD_DRIFT_END")
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

for target_name, expected_lines in expected_make_expansions.items():
    result = subprocess.run(
        ["make", "-n", "-C", str(ROOT / "zigux"), target_name],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("PHASE7_VALIDATION=fail")
        print("PHASE7_MAKE_WRAPPER_CHECK_FAILED_START")
        print(f"{target_name}: returncode={result.returncode}")
        stderr = result.stderr.strip()
        if stderr:
            print(stderr)
        print("PHASE7_MAKE_WRAPPER_CHECK_FAILED_END")
        sys.exit(1)

    wrapper_output = result.stdout
    missing_wrapper_lines = [
        line for line in expected_lines if line not in wrapper_output
    ]
    if missing_wrapper_lines:
        print("PHASE7_VALIDATION=fail")
        print("PHASE7_MAKE_WRAPPER_DRIFT_START")
        print(f"{target_name}: missing expected wrapper expansion")
        for line in missing_wrapper_lines:
            print(line)
        print("PHASE7_MAKE_WRAPPER_DRIFT_END")
        sys.exit(1)

print("PHASE7_VALIDATION=pass")
print(f"PHASE7_REQUIRED_FILE_COUNT={len(required_files)}")
print(
    "PHASE7_REQUIRED_MARKER_COUNT="
    f"{sum(len(markers) for _, _, markers in checks)}"
)
