#!/usr/bin/env python3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]

required_files = [
    ROOT / "Documentation" / "zigux" / "freeze-map.md",
    ROOT / "scripts" / "zigux" / "validate-phase9.py",
    ROOT / "scripts" / "zigux" / "README.md",
    ROOT / "scripts" / "zigux" / "check-phase9-module-metadata-packet.py",
    ROOT / "Documentation" / "zigux" / "README.md",
    ROOT / "Documentation" / "zigux" / "review-checklist.md",
    ROOT / "Documentation" / "zigux" / "phase9-runtime-loader-gap-survey.md",
    ROOT / "Documentation" / "zigux" / "phase9-runtime-trace-events-survey.md",
    ROOT / "Documentation" / "zigux" / "phase9-runtime-trace-events-module-slice.md",
    ROOT / "Documentation" / "zigux" / "phase9-module-metadata-depmod-bridge-survey.md",
    ROOT / "zigux" / "Makefile",
    ROOT / "zigux" / "tests" / "README.md",
    ROOT / "zigux" / "tests" / "phase9_build.zig",
    ROOT / "zigux" / "tests" / "runtime_loader_gap_manifest.json",
    ROOT / "zigux" / "tests" / "runtime_loader_gap_survey.zig",
    ROOT / "zigux" / "tests" / "runtime_trace_events_manifest.json",
    ROOT / "zigux" / "tests" / "runtime_trace_events_survey.zig",
    ROOT / "zigux" / "tests" / "runtime_module_metadata_manifest.json",
    ROOT / "zigux" / "tests" / "runtime_module_metadata_survey.zig",
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
freeze_map = (ROOT / "Documentation" / "zigux" / "freeze-map.md").read_text(encoding="utf-8")
script_readme = (ROOT / "scripts" / "zigux" / "README.md").read_text(encoding="utf-8")
tests_readme = (ROOT / "zigux" / "tests" / "README.md").read_text(encoding="utf-8")
doc_readme = (ROOT / "Documentation" / "zigux" / "README.md").read_text(encoding="utf-8")
review_checklist = (ROOT / "Documentation" / "zigux" / "review-checklist.md").read_text(encoding="utf-8")
loader_gap_survey = (ROOT / "Documentation" / "zigux" / "phase9-runtime-loader-gap-survey.md").read_text(encoding="utf-8")
trace_events_survey = (ROOT / "Documentation" / "zigux" / "phase9-runtime-trace-events-survey.md").read_text(encoding="utf-8")
trace_events_module_slice = (ROOT / "Documentation" / "zigux" / "phase9-runtime-trace-events-module-slice.md").read_text(encoding="utf-8")
module_metadata_survey_doc = (ROOT / "Documentation" / "zigux" / "phase9-module-metadata-depmod-bridge-survey.md").read_text(encoding="utf-8")
phase9_build = (ROOT / "zigux" / "tests" / "phase9_build.zig").read_text(encoding="utf-8")
loader_gap_survey_test = (ROOT / "zigux" / "tests" / "runtime_loader_gap_survey.zig").read_text(encoding="utf-8")
loader_gap_manifest = (ROOT / "zigux" / "tests" / "runtime_loader_gap_manifest.json").read_text(encoding="utf-8")
trace_events_manifest = (ROOT / "zigux" / "tests" / "runtime_trace_events_manifest.json").read_text(encoding="utf-8")
trace_events_survey_test = (ROOT / "zigux" / "tests" / "runtime_trace_events_survey.zig").read_text(encoding="utf-8")
module_metadata_manifest = (ROOT / "zigux" / "tests" / "runtime_module_metadata_manifest.json").read_text(encoding="utf-8")
module_metadata_survey_test = (ROOT / "zigux" / "tests" / "runtime_module_metadata_survey.zig").read_text(encoding="utf-8")
module_metadata_checker = (ROOT / "scripts" / "zigux" / "check-phase9-module-metadata-packet.py").read_text(encoding="utf-8")

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
    "phase9-module-metadata-depmod-bridge-survey.md",
    "check-phase9-module-metadata-packet.py",
    "review-checklist.md",
    "manifest-backed catalog and ownership map",
]

required_tests_readme_markers = [
    "zigux/tests/phase9_build.zig",
    "zigux/tests/runtime_loader_gap_survey.zig",
    "zigux/tests/runtime_loader_gap_manifest.json",
    "zigux/tests/runtime_module_metadata_manifest.json",
    "zigux/tests/runtime_module_metadata_survey.zig",
    "scripts/zigux/check-phase9-module-metadata-packet.py",
    "scripts/zigux/validate-phase9.py",
    "manifest-backed catalog and ownership map",
]

required_doc_readme_markers = [
    "Phase 9 notes",
    "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
    "Documentation/zigux/review-checklist.md",
    "the `Documentation/zigux/phase9-runtime-trace-events-{survey,module-slice}.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` bundle now keeps the `Documentation/zigux/freeze-map.md` boundary explicit",
    "python3 scripts/zigux/validate-phase9.py",
    "make -C zigux phase9-validate",
    "zigux/tests/phase9_build.zig",
    "manifest-backed catalog and ownership map",
]

required_freeze_map_markers = [
    "## Study / Boundary Only",
    "`kernel/trace/ring_buffer.c`",
    "Architecture Council decision",
]

required_review_checklist_markers = [
    "if the change is a Phase 9 runtime slice, do the module or sample note, the manifest-backed survey or loader-gap survey, and the shared `phase9_build.zig` entrypoint still agree on the same Linux anchor, bounded blocker posture, and replay scope?",
    "if the change touches the shared Phase 9 runtime-loader evidence packet, does the manifest-backed catalog and ownership map still keep the survey note, review checklist, shared request contract, sample-side loader plans, and shared `phase9_build.zig` entrypoint in one reviewable ownership packet?",
    "if the change touches the shared Phase 9 runtime-loader handoff, are allocator ownership, `requires_runtime_substrate`, handoff stage, and the still-blocked command-name, argv-policy, or environment-derived activation controls explicit rather than implied?",
    "if a Phase 9 runtime trace-events change touches the frozen trace-core boundary, do `Documentation/zigux/freeze-map.md`, the trace-events docs, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` still keep `kernel/trace/ring_buffer.c` as `Study / Boundary Only` and require an Architecture Council decision before any status change?",
    "does the change avoid hidden runtime services, implicit allocation, or unclear panic behavior?",
    "if unsafe code exists, is it narrow, visible, and review-owned?",
]

required_loader_gap_survey_markers = [
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/runtime_loader_gap_manifest.json",
    "zigux/tests/runtime_loader_gap_survey.zig",
    "zigux/tests/phase9_build.zig",
    "zigux/kernel/runtime_loader.zig",
    "Delivery ownership map",
    "manifest-backed catalog",
    "bitmap loader-plan projection",
    "kretprobe loader-plan projection",
    "Phase 8",
    "Phase 9",
    "command or environment control surface",
    "allocator-handoff contract",
    "pre-execution",
]

required_phase9_build_markers = [
    "runtime_loader_gap_survey.zig",
    "phase9-runtime-loader-gap-survey-tests",
    "phase9-runtime-loader-tests",
    "phase9-runtime-bitmap-loader-tests",
    "phase9-runtime-kretprobe-loader-tests",
]

required_loader_gap_survey_test_markers = [
    "runtime loader gap survey manifest keeps the roadmap boundary and shared request surface explicit",
    "runtime loader gap survey doc keeps the mixed roadmap phases and remaining control-surface gap explicit",
    "runtime loader gap survey keeps the review checklist runtime guardrails explicit",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/runtime_loader_gap_manifest.json",
]

required_loader_gap_manifest_markers = [
    '"delivery_evidence_catalog": [',
    '"id": "runtime-loader-gap-manifest"',
    '"path": "zigux/kernel/runtime_loader.zig"',
    '"ownership_map": [',
    '"surface": "zigux/tests/runtime_loader_gap_manifest.json"',
    '"surface": "samples/zigux/runtime_bitmap_loader.zig"',
    '"id": "runtime-loader-review-checklist"',
    '"zigux_destination": "Documentation/zigux/review-checklist.md"',
    '"id": "runtime-loader-gap-survey-gate"',
    '"zigux_destination": "zigux/tests/runtime_loader_gap_survey.zig"',
    '"id": "phase9-build-gate"',
    '"zigux_destination": "zigux/tests/phase9_build.zig"',
]

required_trace_events_survey_markers = [
    "Documentation/zigux/freeze-map.md",
    "`kernel/trace/ring_buffer.c`",
    "Study / Boundary Only",
    "runtime task ownership",
    "polling and event-loop substrate",
    "ring-buffer parity",
    "Architecture Council",
]

required_trace_events_module_slice_markers = [
    "Documentation/zigux/freeze-map.md",
    "`kernel/trace/ring_buffer.c`",
    "Study / Boundary Only",
    "runtime task ownership or event-loop substrate parity",
    "polling-backed wake or dispatch behavior",
    "ring-buffer parity",
    "Architecture Council",
]

required_trace_events_manifest_markers = [
    '"id": "runtime-trace-events-freeze-map-boundary"',
    '"zigux_destination": "Documentation/zigux/phase9-runtime-trace-events-survey.md"',
    '"id": "runtime-trace-events-substrate-handoff"',
    '"zigux_destination": "samples/zigux/runtime_trace_events_loader.zig"',
    "`kernel/trace/ring_buffer.c`",
    "Architecture Council",
]

required_trace_events_survey_test_markers = [
    'var saw_freeze_map_boundary = false;',
    'std.mem.eql(u8, gap.id, "runtime-trace-events-freeze-map-boundary")',
    'std.mem.indexOf(u8, gap.why_now, "`kernel/trace/ring_buffer.c`")',
    'std.mem.indexOf(u8, survey_doc, "Documentation/zigux/freeze-map.md")',
    'std.mem.indexOf(u8, survey_doc, "`kernel/trace/ring_buffer.c`")',
    'std.mem.indexOf(u8, module_doc, "`kernel/trace/ring_buffer.c`")',
]

required_module_metadata_doc_markers = [
    "PHASE9_SLICE=module-metadata-depmod-bridge-survey",
    "zigux/tests/runtime_module_metadata_manifest.json",
    "zigux/tests/runtime_module_metadata_survey.zig",
    "scripts/zigux/check-phase9-module-metadata-packet.py",
]

required_module_metadata_manifest_markers = [
    '"lane_key": "P9-L09"',
    '"runtime_sample_files": [',
    '"runtime_loader_files": [',
    '"absent_depmod_markers": [',
    '"trace_events_loader_present": false',
    '"depmod_bridge_present": false',
]

required_module_metadata_survey_markers = [
    'Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md',
    'zigux/tests/runtime_module_metadata_manifest.json',
    'scripts/zigux/check-phase9-module-metadata-packet.py',
    'module metadata survey doc records the exact evidence and missing depmod bridge',
]

required_module_metadata_checker_markers = [
    'PHASE9_MODULE_METADATA_PACKET=pass',
    'Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md',
    'zigux/tests/runtime_module_metadata_manifest.json',
    'zigux/tests/runtime_module_metadata_survey.zig',
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
for marker in required_freeze_map_markers:
    if marker not in freeze_map:
        missing_markers.append(f"freeze_map:{marker}")
for marker in required_review_checklist_markers:
    if marker not in review_checklist:
        missing_markers.append(f"review_checklist:{marker}")
for marker in required_loader_gap_survey_markers:
    if marker not in loader_gap_survey:
        missing_markers.append(f"loader_gap_survey:{marker}")
for marker in required_phase9_build_markers:
    if marker not in phase9_build:
        missing_markers.append(f"phase9_build:{marker}")
for marker in required_loader_gap_survey_test_markers:
    if marker not in loader_gap_survey_test:
        missing_markers.append(f"loader_gap_survey_test:{marker}")
for marker in required_loader_gap_manifest_markers:
    if marker not in loader_gap_manifest:
        missing_markers.append(f"loader_gap_manifest:{marker}")
for marker in required_trace_events_survey_markers:
    if marker not in trace_events_survey:
        missing_markers.append(f"trace_events_survey:{marker}")
for marker in required_trace_events_module_slice_markers:
    if marker not in trace_events_module_slice:
        missing_markers.append(f"trace_events_module_slice:{marker}")
for marker in required_trace_events_manifest_markers:
    if marker not in trace_events_manifest:
        missing_markers.append(f"trace_events_manifest:{marker}")
for marker in required_trace_events_survey_test_markers:
    if marker not in trace_events_survey_test:
        missing_markers.append(f"trace_events_survey_test:{marker}")
for marker in required_module_metadata_doc_markers:
    if marker not in module_metadata_survey_doc:
        missing_markers.append(f"module_metadata_survey_doc:{marker}")
for marker in required_module_metadata_manifest_markers:
    if marker not in module_metadata_manifest:
        missing_markers.append(f"module_metadata_manifest:{marker}")
for marker in required_module_metadata_survey_markers:
    if marker not in module_metadata_survey_test:
        missing_markers.append(f"module_metadata_survey_test:{marker}")
for marker in required_module_metadata_checker_markers:
    if marker not in module_metadata_checker:
        missing_markers.append(f"module_metadata_checker:{marker}")

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
    f"{len(required_make_markers) + len(required_workflow_markers) + len(required_script_readme_markers) + len(required_tests_readme_markers) + len(required_doc_readme_markers) + len(required_freeze_map_markers) + len(required_review_checklist_markers) + len(required_loader_gap_survey_markers) + len(required_phase9_build_markers) + len(required_loader_gap_survey_test_markers) + len(required_loader_gap_manifest_markers) + len(required_trace_events_survey_markers) + len(required_trace_events_module_slice_markers) + len(required_trace_events_manifest_markers) + len(required_trace_events_survey_test_markers) + len(required_module_metadata_doc_markers) + len(required_module_metadata_manifest_markers) + len(required_module_metadata_survey_markers) + len(required_module_metadata_checker_markers)}"
)
