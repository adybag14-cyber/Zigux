#!/usr/bin/env python3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / "scripts" / "zigux" / "validate-phase9.py",
    ROOT / "scripts" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "review-checklist.md",
    ROOT / "Documentation" / "zigux" / "phase9-runtime-loader-gap-survey.md",
    ROOT / "zigux" / "Makefile",
    ROOT / "zigux" / "tests" / "README.md",
    ROOT / "zigux" / "tests" / "phase9_build.zig",
    ROOT / ".github" / "workflows" / "zigux-bootstrap.yml",
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print("PHASE9_VALIDATION=fail")
    print("MISSING_PHASE9_FILES_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE9_FILES_END")
    sys.exit(1)

makefile = (ROOT / "zigux" / "Makefile").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
script_readme = (ROOT / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
tests_readme = (ROOT / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
doc_readme = (ROOT / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
review_checklist = (ROOT / "Documentation" / "zigux" / "review-checklist.md").read_text(encoding="utf-8")
phase9_survey = (ROOT / "Documentation" / "zigux" / "phase9-runtime-loader-gap-survey.md").read_text(encoding="utf-8")
phase9_build = (ROOT / "zigux" / "tests" / "phase9_build.zig").read_text(encoding="utf-8")

required_make_markers = [
    "PHONY += phase9-validate phase9-test phase9",
    "phase9-validate:",
    "scripts/zigux/validate-phase9.py",
    "phase9-test:",
    "zigux/tests/phase9_build.zig",
    "phase9: phase9-validate phase9-test",
]

required_workflow_markers = [
    "Validate Phase 9 runtime gates",
    "make -C zigux phase9-validate",
    "Run Phase 9 runtime helper tests",
    "zigux/tests/phase9_build.zig",
]

required_script_readme_markers = [
    "validate-phase9.py",
    "Phase 9 flow",
    "make -C zigux phase9-validate",
    "phase9_build.zig",
    "phase9-runtime-loader-gap-survey.md",
    "review-checklist.md",
]

required_tests_readme_markers = [
    "zigux/tests/phase9_build.zig",
    "scripts/zigux/validate-phase9.py",
]

required_doc_readme_markers = [
    "Phase 9 notes",
    "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/phase9_build.zig",
    "python3 scripts/zigux/validate-phase9.py",
    "make -C zigux phase9-validate",
    "make -C zigux phase9",
]

required_review_checklist_markers = [
    "if the change is a Phase 9 runtime slice",
    "phase9_build.zig",
    "if the change touches the shared Phase 9 runtime-loader handoff",
    "requires_runtime_substrate",
    "command-name, argv-policy, or environment-derived activation controls",
]

required_survey_markers = [
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/phase9_build.zig",
    "python3 scripts/zigux/validate-phase9.py",
    "make -C zigux phase9-validate",
    "make -C zigux phase9",
    "allocator plus init or exit handoff machine-checkable",
    "command or environment control surface",
]

required_phase9_build_markers = [
    "runtime_atomic64_module.zig",
    "runtime_bitmap_module.zig",
    "runtime_trace_events_module.zig",
    "runtime_kretprobe_module.zig",
    "runtime_loader_gap_survey.zig",
    "phase9-runtime-loader-tests",
    "phase9-runtime-loader-gap-survey-tests",
]

missing_markers = []

for marker in required_make_markers:
    if marker not in makefile:
        missing_markers.append(f"make:{marker}")
for marker in required_workflow_markers:
    if marker not in workflow:
        missing_markers.append(f"workflow:{marker}")
for marker in required_script_readme_markers:
    if marker not in script_readme:
        missing_markers.append(f"script_readme:{marker}")
for marker in required_tests_readme_markers:
    if marker not in tests_readme:
        missing_markers.append(f"tests_readme:{marker}")
for marker in required_doc_readme_markers:
    if marker not in doc_readme:
        missing_markers.append(f"doc_readme:{marker}")
for marker in required_review_checklist_markers:
    if marker not in review_checklist:
        missing_markers.append(f"review_checklist:{marker}")
for marker in required_survey_markers:
    if marker not in phase9_survey:
        missing_markers.append(f"phase9_survey:{marker}")
for marker in required_phase9_build_markers:
    if marker not in phase9_build:
        missing_markers.append(f"phase9_build:{marker}")

if missing_markers:
    print("PHASE9_VALIDATION=fail")
    print("MISSING_PHASE9_MARKERS_START")
    for marker in missing_markers:
        print(marker)
    print("MISSING_PHASE9_MARKERS_END")
    sys.exit(1)

print("PHASE9_VALIDATION=pass")
print(f"PHASE9_REQUIRED_FILE_COUNT={len(required_files)}")
print(
    "PHASE9_REQUIRED_MARKER_COUNT="
    f"{len(required_make_markers) + len(required_workflow_markers) + len(required_script_readme_markers) + len(required_tests_readme_markers) + len(required_doc_readme_markers) + len(required_review_checklist_markers) + len(required_survey_markers) + len(required_phase9_build_markers)}"
)
