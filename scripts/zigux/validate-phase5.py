#!/usr/bin/env python3
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / "scripts" / "zigux" / "validate-phase5.py",
    ROOT / "scripts" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "review-checklist.md",
    ROOT / "Documentation" / "zigux" / "phase5-kfifo-sample-survey.md",
    ROOT / "Documentation" / "zigux" / "phase5-kobject-sample-survey.md",
    ROOT / "Documentation" / "zigux" / "phase5-kretprobe-sample-survey.md",
    ROOT / "Documentation" / "zigux" / "phase5-trace-events-sample-survey.md",
    ROOT / "samples" / "zigux" / "README.md",
    ROOT / "samples" / "zigux" / "bytestream_fifo.zig",
    ROOT / "samples" / "zigux" / "kobject_example.zig",
    ROOT / "samples" / "zigux" / "kretprobe_example.zig",
    ROOT / "samples" / "zigux" / "trace_events_sample.zig",
    ROOT / "zigux" / "Makefile",
    ROOT / "zigux" / "tests" / "README.md",
    ROOT / "zigux" / "tests" / "phase5_build.zig",
    ROOT / "zigux" / "tests" / "phase5_bytestream_fifo.zig",
    ROOT / "zigux" / "tests" / "phase5_bytestream_fifo_manifest.json",
    ROOT / "zigux" / "tests" / "phase5_bytestream_fifo_survey.zig",
    ROOT / "zigux" / "tests" / "phase5_kobject_example.zig",
    ROOT / "zigux" / "tests" / "phase5_kobject_example_manifest.json",
    ROOT / "zigux" / "tests" / "phase5_kobject_example_survey.zig",
    ROOT / "zigux" / "tests" / "phase5_kretprobe_example.zig",
    ROOT / "zigux" / "tests" / "phase5_kretprobe_example_manifest.json",
    ROOT / "zigux" / "tests" / "phase5_kretprobe_example_survey.zig",
    ROOT / "zigux" / "tests" / "phase5_trace_events_sample.zig",
    ROOT / "zigux" / "tests" / "phase5_trace_events_sample_manifest.json",
    ROOT / "zigux" / "tests" / "phase5_trace_events_sample_survey.zig",
    ROOT / ".github" / "workflows" / "zigux-bootstrap.yml",
]

missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
if missing:
    print("PHASE5_VALIDATION=fail")
    print("MISSING_PHASE5_FILES_START")
    for item in missing:
        print(item)
    print("MISSING_PHASE5_FILES_END")
    sys.exit(1)

makefile = (ROOT / "zigux" / "Makefile").read_text(encoding="utf-8")
workflow = (ROOT / ".github" / "workflows" / "zigux-bootstrap.yml").read_text(encoding="utf-8")
script_readme = (ROOT / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
tests_readme = (ROOT / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
doc_readme = (ROOT / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
review_checklist = (ROOT / "Documentation" / "zigux" / "review-checklist.md").read_text(encoding="utf-8")
sample_root_readme = (ROOT / "samples" / "zigux" / "README.md").read_text(encoding="utf-8")
phase5_build = (ROOT / "zigux" / "tests" / "phase5_build.zig").read_text(encoding="utf-8")

required_make_markers = [
    "PHONY += phase5-validate phase5-test phase5",
    "phase5-validate:",
    "scripts/zigux/validate-phase5.py",
    "phase5-test:",
    "zigux/tests/phase5_build.zig",
    "phase5: phase5-validate phase5-test",
]

required_workflow_markers = [
    "Validate Phase 5 reference sample packet",
    "make -C zigux phase5-validate",
    "Run Phase 5 reference sample tests",
    "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
]

required_script_readme_markers = [
    "validate-phase5.py",
    "Phase 5 flow",
    "make -C zigux phase5-validate",
    "make -C zigux phase5",
    "zigux/tests/phase5_build.zig",
    "samples/zigux/README.md",
]

required_tests_readme_markers = [
    "zigux/tests/phase5_build.zig",
    "zigux/tests/phase5_bytestream_fifo.zig",
    "zigux/tests/phase5_bytestream_fifo_manifest.json",
    "zigux/tests/phase5_bytestream_fifo_survey.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_kobject_example_manifest.json",
    "zigux/tests/phase5_kobject_example_survey.zig",
    "zigux/tests/phase5_kretprobe_example.zig",
    "zigux/tests/phase5_kretprobe_example_manifest.json",
    "zigux/tests/phase5_kretprobe_example_survey.zig",
    "zigux/tests/phase5_trace_events_sample.zig",
    "zigux/tests/phase5_trace_events_sample_manifest.json",
    "zigux/tests/phase5_trace_events_sample_survey.zig",
    "scripts/zigux/validate-phase5.py",
    "make -C zigux phase5-validate",
    "samples/zigux/README.md",
]

required_doc_readme_markers = [
    "Phase 5 notes",
    "samples/zigux/README.md",
    "phase5-kfifo-sample-survey.md",
    "phase5-kobject-sample-survey.md",
    "phase5-kretprobe-sample-survey.md",
    "phase5-trace-events-sample-survey.md",
    "python3 scripts/zigux/validate-phase5.py",
    "make -C zigux phase5-validate",
    "make -C zigux phase5",
    "zigux/tests/phase5_build.zig",
    "ships no `samples/zigux/*string*` reference sample",
    "sample-root follow-up should not treat that absence as a missing Phase 5 port",
]

required_checklist_markers = [
    "phase5_build.zig",
    "descriptor, manifest-backed survey, sample-backed survey note",
    "kobject",
    "kretprobe",
    "trace-events",
    "ships no `samples/zigux/*string*` Phase 5 reference sample",
    "separate Phase 7 helper bundle",
]

required_sample_root_markers = [
    "Phase 5 reference samples",
    "Bytestream FIFO review packet",
    "Kobject review packet",
    "Kretprobe review packet",
    "Trace-events review packet",
    "Documentation/zigux/phase5-kfifo-sample-survey.md",
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "Documentation/zigux/phase5-kretprobe-sample-survey.md",
    "Documentation/zigux/phase5-trace-events-sample-survey.md",
    "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
    "current approved Phase 5 reference sample inventory still resolves to the four roadmap anchors only",
    "later `runtime_*` starters still stay cataloged separately from the approved Phase 5 anchors",
    "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample",
    "rg '/(bytestream_fifo|kobject_example|kretprobe_example|trace_events_sample)\\.zig$'",
    "rg '/runtime_.*\\.zig$'",
    "rg '/.*string.*\\.zig$'",
    "python3 scripts/zigux/validate-phase7.py",
]

required_phase5_build_markers = [
    "fn addTestRun(",
    "run.setCwd(path);",
    'const repo_root = b.path("../..");',
    "../../samples/zigux/bytestream_fifo.zig",
    "../../samples/zigux/kobject_example.zig",
    "../../samples/zigux/kretprobe_example.zig",
    "../../samples/zigux/trace_events_sample.zig",
    "phase5_bytestream_fifo.zig",
    "phase5_bytestream_fifo_survey.zig",
    "phase5_kobject_example.zig",
    "phase5_kobject_example_survey.zig",
    "phase5_kretprobe_example.zig",
    "phase5_kretprobe_example_survey.zig",
    "phase5_trace_events_sample.zig",
    "phase5_trace_events_sample_survey.zig",
    "phase5-bytestream-fifo-tests",
    "phase5-bytestream-fifo-survey-tests",
    "phase5-kobject-example-tests",
    "phase5-kobject-example-survey-tests",
    "phase5-kretprobe-example-tests",
    "phase5-kretprobe-example-survey-tests",
    "phase5-trace-events-sample-tests",
    "phase5-trace-events-sample-survey-tests",
    "phase5_bytestream_fifo_survey_module,\n        repo_root,",
    "phase5_kobject_example_survey_module,\n        repo_root,",
    "phase5_kretprobe_example_survey_module,\n        repo_root,",
    "phase5_trace_events_sample_survey_module,\n        repo_root,",
    'b.step("test", "Run Phase 5 reference sample checks")',
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
for marker in required_checklist_markers:
    if marker not in review_checklist:
        missing_markers.append(f"review_checklist:{marker}")
for marker in required_sample_root_markers 