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
    "no-`samples/zigux/*cmdline*` boundary explicit",
    "Phase 7 helper bundle rooted in `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, and `zigux/tests/phase7_build.zig`",
]

required_checklist_markers = [
    "phase5_build.zig",
    "descriptor, manifest-backed survey, sample-backed survey note",
    "direct `zig test samples/zigux/...` replays and the paired `zig test zigux/tests/..._survey.zig` replays stay explicit",
    "kobject",
    "kretprobe",
    "trace-events",
    "ships no `samples/zigux/*string*` Phase 5 reference sample",
    "separate Phase 7 helper bundle",
    "ships no `samples/zigux/*cmdline*` Phase 5 reference sample",
    "`Documentation/zigux/phase7-cmdline-slice.md`",
    "`lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, and `zigux/tests/phase7_build.zig`",
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
    "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample",
    "zig test samples/zigux/bytestream_fifo.zig",
    "zig test samples/zigux/kobject_example.zig",
    "zig test samples/zigux/kretprobe_example.zig",
    "zig test samples/zigux/trace_events_sample.zig",
    "zig test zigux/tests/phase5_bytestream_fifo_survey.zig",
    "zig test zigux/tests/phase5_kobject_example_survey.zig",
    "zig test zigux/tests/phase5_kretprobe_example_survey.zig",
    "zig test zigux/tests/phase5_trace_events_sample_survey.zig",
    "rg '/(bytestream_fifo|kobject_example|kretprobe_example|trace_events_sample)\\.zig$'",
    "rg '/runtime_.*\\.zig$'",
    "rg '/.*string.*\\.zig$'",
    "rg '/.*cmdline.*\\.zig$'",
    "rg -n \"samples/zigux/\\\\*cmdline\\\\*|Phase 7 helper bundle|lib/cmdline.zig|phase7_cmdline.zig|phase7_build.zig\"",
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
for marker in required_sample_root_markers:
    if marker not in sample_root_readme:
        missing_markers.append(f"sample_root_readme:{marker}")
for marker in required_phase5_build_markers:
    if marker not in phase5_build:
        missing_markers.append(f"phase5_build:{marker}")

manifest_expectations = {
    "phase5_bytestream_fifo_manifest.json": {
        "lane_key": "P5-L04",
        "anchor": "samples/kfifo/bytestream-example.c",
        "sample_path": "samples/zigux/bytestream_fifo.zig",
        "validation_entrypoint": "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "survey_build_summary": "Build Summary: 17/17 steps succeeded; 27/27 tests passed",
        "non_goals": [
            "procfs parity",
            "kfifo_from_user or kfifo_to_user parity",
            "loadable module registration",
            "locking or blocking semantics",
        ],
        "exact_check_ids": [
            "initial-fill-len",
            "first-drain",
            "second-drain-and-requeue",
            "transfer-count-contract",
            "skip-and-peek",
            "wrapped-preview-prefix",
            "snapshot-before-final-drain",
            "fill-to-capacity",
            "final-drain-sequence",
            "storage-backing-contract",
            "bounded-helper-behavior",
            "short-drain-prefix",
            "preview-truncation",
            "queue-only-reset",
            "checked-focus-list",
            "lifecycle-boundary",
            "lifecycle-guards-and-counters",
        ],
    },
    "phase5_kobject_example_manifest.json": {
        "lane_key": "P5-L10",
        "anchor": "samples/kobject/kobject-example.c",
        "sample_path": "samples/zigux/kobject_example.zig",
        "validation_entrypoint": "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "survey_build_summary": "Build Summary: 17/17 steps succeeded; 27/27 tests passed",
        "non_goals": [
            "sysfs file creation parity",
            "kernel_kobj integration",
            "uevent delivery",
            "loadable module registration",
        ],
        "exact_check_ids": [
            "directory-name",
            "attribute-order",
            "attribute-mode",
            "registration-step",
            "static-name-no-uevent-boundary",
            "pre-registration-boundary",
            "initialized-exit-teardown",
            "foo-roundtrip",
            "shared-b-dispatch",
            "parse-failure",
            "exit-boundary",
        ],
    },
    "phase5_kretprobe_example_manifest.json": {
        "lane_key": "P5-L22",
        "anchor": "samples/kprobes/kretprobe_example.c",
        "sample_path": "samples/zigux/kretprobe_example.zig",
        "validation_entrypoint": "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "survey_build_summary": "Build Summary: 17/17 steps succeeded; 28/28 tests passed",
        "non_goals": [
            "register_kretprobe parity",
            "unregister_kretprobe parity",
            "pt_regs or regs_return_value parity",
            "loadable module wiring",
        ],
        "exact_check_ids": [
            "default-symbol",
            "pre-init-retargeting",
            "skip-kernel-thread",
            "private-data-shape",
            "return-duration",
            "timestamp-order-boundary",
            "maxactive-budget",
            "missed-summary",
            "outstanding-instance-boundary",
            "post-exit-rejection",
        ],
    },
    "phase5_trace_events_sample_manifest.json": {
        "lane_key": "P5-L24",
        "anchor": "samples/trace_events/trace-events-sample.c",
        "sample_path": "samples/zigux/trace_events_sample.zig",
        "validation_entrypoint": "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "survey_build_summary": "Build Summary: 17/17 steps succeeded; 28/28 tests passed",
        "non_goals": [
            "CREATE_TRACE_POINTS parity",
            "tracepoint macro parity from trace-events-sample.h",
            "kernel thread scheduling or timeout parity",
            "module registration or unregister wiring parity",
        ],
        "exact_check_ids": [
            "descriptor-anchor",
            "message-and-string-shape",
            "modulo-string-cycle",
            "iteration-cues",
            "array-and-sentinel-shape",
            "bitmask-and-rel-loc",
            "vararg-payload-path",
            "event-family-counts",
            "lifecycle-summary-counts",
            "checked-focus-order",
            "callback-registration-balance",
            "single-registration-boundary",
            "post-exit-rejection",
        ],
    },
}
