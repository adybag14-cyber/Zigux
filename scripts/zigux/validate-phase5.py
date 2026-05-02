#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SELF_TEST_HEAD = "0123456789abcdef0123456789abcdef01234567"
SELF_TEST_MUTATED_HEAD = "fedcba9876543210fedcba9876543210fedcba98"

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
    "`samples/zigux/runtime_bitmap.zig` plus `samples/zigux/runtime_bitmap_loader.zig` stay cataloged as the separate Phase 9 runtime bitmap survey packet rather than a fifth approved Phase 5 sample",
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
    "`samples/zigux/runtime_bitmap.zig` plus `samples/zigux/runtime_bitmap_loader.zig`",
    "separate Phase 9 runtime bitmap survey packet",
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

sample_source_expectations = {
    "phase5_bytestream_fifo_sample": {
        "path": "samples/zigux/bytestream_fifo.zig",
        "markers": [
            "pub fn descriptor() SampleDescriptor {",
            '.name = "bytestream_fifo"',
            '.anchor = "samples/kfifo/bytestream-example.c"',
            ".requires_runtime_substrate = false",
            ".provides_selfcheck = true",
            ".storage_backing = .embedded_fixed_buffer",
        ],
    },
    "phase5_kobject_example_sample": {
        "path": "samples/zigux/kobject_example.zig",
        "markers": [
            "pub fn descriptor() SampleDescriptor {",
            '.name = "kobject_example"',
            '.anchor = "samples/kobject/kobject-example.c"',
            ".requires_runtime_substrate = false",
            ".provides_selfcheck = true",
        ],
    },
    "phase5_kretprobe_example_sample": {
        "path": "samples/zigux/kretprobe_example.zig",
        "markers": [
            "pub fn descriptor() SampleDescriptor {",
            '.name = "kretprobe_example"',
            '.anchor = "samples/kprobes/kretprobe_example.c"',
            ".requires_runtime_substrate = false",
            ".provides_selfcheck = true",
        ],
    },
    "phase5_trace_events_sample": {
        "path": "samples/zigux/trace_events_sample.zig",
        "markers": [
            "pub fn descriptor() SampleDescriptor {",
            '.name = "trace_events_sample"',
            '.anchor = "samples/trace_events/trace-events-sample.c"',
            ".requires_runtime_substrate = false",
            ".provides_selfcheck = true",
        ],
    },
}

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
        "lane_key": "P5-L01",
        "anchor": "samples/kfifo/bytestream-example.c",
        "sample_path": "samples/zigux/bytestream_fifo.zig",
        "survey_note_path": "Documentation/zigux/phase5-kfifo-sample-survey.md",
        "validation_entrypoint": "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "reference_patterns": [
            "fixed embedded 32-byte ring buffer keeps the Phase 5 sample in memory and reviewable",
            "exact queue-order replay mirrors the Linux bytestream anchor without claiming procfs or module parity",
            "wraparound requeue, skip, and peek stay explicit as bounded FIFO operations rather than hidden helper behavior",
            "non-destructive snapshot keeps reviewer inspection separate from the final drain sequence",
            "init, replay, and exit keep ownership and lifetime boundaries explicit for the bytestream sample",
        ],
        "survey_build_summary": "Build Summary: 17/17 steps succeeded; 28/28 tests passed",
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
        "lane_key": "P5-L12",
        "anchor": "samples/kobject/kobject-example.c",
        "sample_path": "samples/zigux/kobject_example.zig",
        "survey_note_path": "Documentation/zigux/phase5-kobject-sample-survey.md",
        "validation_entrypoint": "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "survey_build_summary": "The shared `zigux/tests/phase5_build.zig` entrypoint remains the umbrella review gate recorded in the manifest and contributor prompts, but this bounded verification pass did not rerun the whole Phase 5 sample bundle.",
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
        "survey_note_path": "Documentation/zigux/phase5-kretprobe-sample-survey.md",
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
        "survey_note_path": "Documentation/zigux/phase5-trace-events-sample-survey.md",
        "validation_entrypoint": "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "survey_build_summary": "Build Summary: 17/17 steps succeeded; 29/29 tests passed",
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
            "pre-registration-callback-rejection",
            "single-registration-boundary",
            "registration-underflow-and-armed-exit",
            "post-exit-rejection",
        ],
    },
}

review_prompt_expectations = {
    "phase5_bytestream_fifo_manifest.json": [
        {
            "id": "descriptor_storage",
            "markers": [
                "requires_runtime_substrate false",
                "fixed embedded storage",
            ],
        },
        {
            "id": "surveyed_commit_sync",
            "markers": [
                "surveyed_commit",
                "PHASE5_SURVEYED_COMMIT",
                "floating branch label",
            ],
        },
        {
            "id": "helper_surface",
            "markers": [
                "phase5_bytestream_fifo.zig",
                "preview truncation",
                "capacity ceiling",
            ],
        },
        {
            "id": "sample_root_boundary",
            "markers": [
                "samples/zigux/README.md",
                "four Phase 5 reference samples",
                "runtime starters",
                "review-packet stanza",
                "helper-only review surface",
                "out-of-scope runtime claims",
            ],
        },
    ],
    "phase5_kobject_example_manifest.json": [
        {
            "id": "attribute_contract",
            "markers": [
                "foo/baz/bar attribute order",
                "0664 attribute mode pattern",
            ],
        },
        {
            "id": "docs_sync",
            "markers": [
                "sample-backed survey note",
                "sample-root catalog",
                "review checklist",
                "phase5_build.zig",
            ],
        },
        {
            "id": "group_boundary",
            "markers": [
                "unnamed attribute group",
                "initialized-only exit summary",
                "post-exit",
            ],
        },
        {
            "id": "pre_registration",
            "markers": [
                "initialized-but-not-registered stage",
                "registerAttributes claims ownership",
            ],
        },
    ],
    "phase5_kretprobe_example_manifest.json": [
        {
            "id": "surveyed_commit_sync",
            "markers": [
                "surveyed_commit",
                "exact inspected master head",
                "floating branch label",
            ],
        },
        {
            "id": "docs_sync",
            "markers": [
                "sample-backed survey note",
                "shared sample-root catalog",
                "top-level Phase 5 README note",
                "shared review checklist",
                "Phase 9 runtime starter",
            ],
        },
        {
            "id": "private_data",
            "markers": [
                "private entry timestamp",
                "my_data",
            ],
        },
        {
            "id": "maxactive_budget",
            "markers": [
                "maxactive budget",
                "fixed helper-backed reviewable ceiling",
            ],
        },
    ],
    "phase5_trace_events_sample_manifest.json": [
        {
            "id": "surveyed_commit_sync",
            "markers": [
                "surveyed_commit",
                "exact inspected master head",
                "floating branch label",
            ],
        },
        {
            "id": "docs_sync",
            "markers": [
                "sample-backed survey note",
                "samples/zigux/README.md",
                "Documentation/zigux/README.md",
                "Documentation/zigux/review-checklist.md",
                "approved payload-and-callback idiom",
                "reviewable and repeatable",
                "Phase 9 runtime pilot",
            ],
        },
        {
            "id": "payload_contract",
            "markers": [
                "selected-string-slot",
                "payload-length",
                "main-iteration",
                "callback-iteration",
                "vararg-payload",
                "lifecycle-summary",
                "relative-location",
                "callback-path",
            ],
        },
        {
            "id": "exit_boundary",
            "markers": [
                "after `exit()`",
                "replayFunctionIteration",
                "unregisterFunctionCallback",
            ],
        },
    ],
}

survey_note_expectations = {
    "phase5_bytestream_fifo_manifest.json": {
        "sample_test_command": "zig test samples/zigux/bytestream_fifo.zig",
        "sample_test_result": "All 4 tests passed.",
        "survey_test_command": "zig test zigux/tests/phase5_bytestream_fifo_survey.zig",
        "survey_test_result": "All 2 tests passed.",
    },
    "phase5_kobject_example_manifest.json": {
        "sample_test_command": "zig test samples/zigux/kobject_example.zig",
        "sample_test_result": "All 5 tests passed.",
        "survey_test_command": "zig test zigux/tests/phase5_kobject_example_survey.zig",
        "survey_test_result": "All 2 tests passed.",
    },
    "phase5_kretprobe_example_manifest.json": {
        "sample_test_command": "zig test samples/zigux/kretprobe_example.zig",
        "sample_test_result": "All 1 tests passed.",
        "survey_test_command": "zig test zigux/tests/phase5_kretprobe_example_survey.zig",
        "survey_test_result": "All 2 tests passed.",
    },
    "phase5_trace_events_sample_manifest.json": {
        "sample_test_command": "zig test samples/zigux/trace_events_sample.zig",
        "sample_test_result": "All 5 tests passed.",
        "survey_test_command": "zig test zigux/tests/phase5_trace_events_sample_survey.zig",
        "survey_test_result": "All 2 tests passed.",
    },
}

def text(root: Path, path: str) -> str:
    return (root / path).read_text(encoding="utf-8")


def load_json(root: Path, path: str) -> object:
    return json.loads(text(root, path))


def collect_missing_files(root: Path) -> list[str]:
    return [str(path.relative_to(root)) for path in required_files if not path.exists()]


def require_markers(missing: list[str], label: str, source: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            missing.append(f"{label}:missing:{marker}")


def require_manifest_equal(
    missing: list[str], label: str, manifest: dict[str, object], key: str, expected: object
) -> None:
    if manifest.get(key) != expected:
        missing.append(f"{label}:{key}")


def require_manifest_string_list(
    missing: list[str], label: str, manifest: dict[str, object], key: str, expected: list[str]
) -> None:
    actual = manifest.get(key)
    if actual != expected:
        missing.append(f"{label}:{key}")


def require_exact_check_ids(
    missing: list[str], label: str, manifest: dict[str, object], expected_ids: list[str]
) -> None:
    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        missing.append(f"{label}:exact_checks")
        return

    actual_ids: list[str] = []
    for entry in exact_checks:
        if not isinstance(entry, dict):
            missing.append(f"{label}:exact_checks")
            return
        check_id = entry.get("id")
        kind = entry.get("kind")
        expected = entry.get("expected")
        if not isinstance(check_id, str) or not isinstance(kind, str) or not isinstance(expected, str):
            missing.append(f"{label}:exact_checks")
            return
        actual_ids.append(check_id)

    if actual_ids != expected_ids:
        missing.append(f"{label}:exact_check_ids")


def require_review_prompt_groups(
    missing: list[str],
    label: str,
    manifest: dict[str, object],
    expected_groups: list[dict[str, object]],
) -> None:
    review_prompts = manifest.get("review_prompts")
    if not isinstance(review_prompts, list) or not review_prompts or not all(
        isinstance(prompt, str) and prompt for prompt in review_prompts
    ):
        missing.append(f"{label}:review_prompts")
        return

    for group in expected_groups:
        group_id = group["id"]
        markers = group["markers"]
        if not isinstance(group_id, str) or not isinstance(markers, list):
            missing.append(f"{label}:review_prompts")
            return
        if not any(
            isinstance(prompt, str) and all(isinstance(marker, str) and marker in prompt for marker in markers)
            for prompt in review_prompts
        ):
            missing.append(f"{label}:review_prompt:{group_id}")


def total_marker_count() -> int:
    marker_count = (
        len(required_make_markers)
        + len(required_workflow_markers)
        + len(required_script_readme_markers)
        + len(required_tests_readme_markers)
        + len(required_doc_readme_markers)
        + len(required_checklist_markers)
        + len(required_sample_root_markers)
        + len(required_phase5_build_markers)
    )
    for spec in sample_source_expectations.values():
        marker_count += len(spec["markers"])
    for manifest_name, spec in manifest_expectations.items():
        marker_count += 6  # phase, lane, anchor, sample path, entrypoint, surveyed commit shape
        marker_count += len(spec.get("reference_patterns", []))
        marker_count += len(spec["non_goals"])
        marker_count += len(spec["exact_check_ids"])
        marker_count += 3 + len(review_prompt_expectations[manifest_name])
        marker_count += 1 if spec["survey_note_path"] else 0
        marker_count += 4 if manifest_name in survey_note_expectations else 0
    return marker_count


def validate_phase5(root: Path) -> dict[str, object]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return {"ok": False, "missing_files": missing_files, "missing": []}

    makefile = text(root, "zigux/Makefile")
    workflow = text(root, ".github/workflows/zigux-bootstrap.yml")
    script_readme = text(root, "scripts/zigux/README.md")
    tests_readme = text(root, "zigux/tests/README.md")
    doc_readme = text(root, "Documentation/zigux/README.md")
    review_checklist = text(root, "Documentation/zigux/review-checklist.md")
    sample_root_readme = text(root, "samples/zigux/README.md")
    phase5_build = text(root, "zigux/tests/phase5_build.zig")

    missing: list[str] = []
    require_markers(missing, "make", makefile, required_make_markers)
    require_markers(missing, "workflow", workflow, required_workflow_markers)
    require_markers(missing, "script_readme", script_readme, required_script_readme_markers)
    require_markers(missing, "tests_readme", tests_readme, required_tests_readme_markers)
    require_markers(missing, "doc_readme", doc_readme, required_doc_readme_markers)
    require_markers(missing, "review_checklist", review_checklist, required_checklist_markers)
    require_markers(missing, "sample_root_readme", sample_root_readme, required_sample_root_markers)
    require_markers(missing, "phase5_build", phase5_build, required_phase5_build_markers)
    for label, spec in sample_source_expectations.items():
        require_markers(missing, f"sample_source:{label}", text(root, spec["path"]), spec["markers"])

    for manifest_name, spec in manifest_expectations.items():
        manifest_obj = load_json(root, f"zigux/tests/{manifest_name}")
        label = manifest_name.removesuffix(".json")
        if not isinstance(manifest_obj, dict):
            missing.append(f"{label}:root")
            continue

        surveyed_commit = manifest_obj.get("surveyed_commit")
        if not isinstance(surveyed_commit, str) or not HEX40.fullmatch(surveyed_commit):
            missing.append(f"{label}:surveyed_commit")

        require_manifest_equal(missing, label, manifest_obj, "phase", "Phase 5")
        require_manifest_equal(missing, label, manifest_obj, "lane_key", spec["lane_key"])
        require_manifest_equal(missing, label, manifest_obj, "anchor", spec["anchor"])
        require_manifest_equal(missing, label, manifest_obj, "sample_path", spec["sample_path"])
        require_manifest_equal(
            missing,
            label,
            manifest_obj,
            "validation_entrypoint",
            spec["validation_entrypoint"],
        )
        reference_patterns = spec.get("reference_patterns")
        if isinstance(reference_patterns, list):
            require_manifest_string_list(
                missing,
                label,
                manifest_obj,
                "reference_patterns",
                reference_patterns,
            )
        require_manifest_string_list(missing, label, manifest_obj, "non_goals", spec["non_goals"])
        require_exact_check_ids(missing, label, manifest_obj, spec["exact_check_ids"])
        require_review_prompt_groups(
            missing,
            label,
            manifest_obj,
            review_prompt_expectations[manifest_name],
        )

        note_spec = survey_note_expectations[manifest_name]
        survey_note = text(root, spec["survey_note_path"])
        if f"PHASE5_LANE_KEY={spec['lane_key']}" not in survey_note:
            missing.append(f"{label}:lane_key_sync")
        if isinstance(surveyed_commit, str) and f"PHASE5_SURVEYED_COMMIT={surveyed_commit}" not in survey_note:
            missing.append(f"{label}:surveyed_commit_sync")
        if spec["survey_build_summary"] not in survey_note:
            missing.append(f"{label}:survey_build_summary")
        if note_spec["sample_test_command"] not in survey_note:
            missing.append(f"{label}:sample_test_command")
        if note_spec["sample_test_result"] not in survey_note:
            missing.append(f"{label}:sample_test_result")
        if note_spec["survey_test_command"] not in survey_note:
            missing.append(f"{label}:survey_test_command")
        if note_spec["survey_test_result"] not in survey_note:
            missing.append(f"{label}:survey_test_result")

    return {"ok": not missing, "missing_files": [], "missing": missing}


def report_validation(result: dict[str, object]) -> int:
    missing_files = result["missing_files"]
    if missing_files:
        print("PHASE5_VALIDATION=fail")
        print("MISSING_PHASE5_FILES_START")
        for path in missing_files:
            print(path)
        print("MISSING_PHASE5_FILES_END")
        return 1

    missing = result["missing"]
    if missing:
        print("PHASE5_VALIDATION=fail")
        print("MISSING_PHASE5_MARKERS_START")
        for item in missing:
            print(item)
        print("MISSING_PHASE5_MARKERS_END")
        return 1

    print("PHASE5_VALIDATION=pass")
    print(f"PHASE5_REQUIRED_FILE_COUNT={len(required_files)}")
    print(f"PHASE5_REQUIRED_MARKER_COUNT={total_marker_count()}")
    return 0


def _copy_required_tree(src_root: Path, dst_root: Path) -> None:
    for src_path in required_files:
        dst_path = dst_root / src_path.relative_to(src_root)
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        dst_path.write_text(src_path.read_text(encoding="utf-8"), encoding="utf-8")


def run_self_test() -> int:
    live_result = validate_phase5(ROOT)
    if not live_result["ok"]:
        print("PHASE5_VALIDATOR_SELF_TEST=fail")
        print("PHASE5_VALIDATOR_SELF_TEST_REASON=live-tree-validation-failed")
        for item in live_result["missing"]:
            print(item)
        return 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase5_validator_selftest_") as tmp_dir_str:
        tmp_root = Path(tmp_dir_str)
        _copy_required_tree(ROOT, tmp_root)

        manifest_path = tmp_root / "zigux/tests/phase5_trace_events_sample_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["surveyed_commit"] = SELF_TEST_HEAD
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        note_path = tmp_root / manifest_expectations["phase5_trace_events_sample_manifest.json"]["survey_note_path"]
        note_text = note_path.read_text(encoding="utf-8")
        note_text = re.sub(
            r"PHASE5_SURVEYED_COMMIT=[0-9a-f]{40}",
            f"PHASE5_SURVEYED_COMMIT={SELF_TEST_HEAD}",
            note_text,
        )
        note_path.write_text(note_text, encoding="utf-8")

        if not validate_phase5(tmp_root)["ok"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=seeded-tree-should-pass")
            return 1

        bytestream_manifest_path = tmp_root / "zigux/tests/phase5_bytestream_fifo_manifest.json"
        bytestream_manifest = json.loads(bytestream_manifest_path.read_text(encoding="utf-8"))
        reference_patterns = bytestream_manifest.get("reference_patterns")
        if not isinstance(reference_patterns, list) or not reference_patterns:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=reference-pattern-seed-missing")
            return 1
        bytestream_manifest["reference_patterns"] = list(reference_patterns)
        bytestream_manifest["reference_patterns"][0] = "mutated reference pattern"
        bytestream_manifest_path.write_text(json.dumps(bytestream_manifest, indent=2) + "\n", encoding="utf-8")
        reference_pattern_result = validate_phase5(tmp_root)
        if reference_pattern_result["ok"] or "phase5_bytestream_fifo_manifest:reference_patterns" not in reference_pattern_result["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=reference-pattern-gap")
            return 1

        bytestream_manifest = json.loads(
            (ROOT / "zigux/tests/phase5_bytestream_fifo_manifest.json").read_text(encoding="utf-8")
        )
        bytestream_manifest_path.write_text(json.dumps(bytestream_manifest, indent=2) + "\n", encoding="utf-8")

        manifest["surveyed_commit"] = SELF_TEST_MUTATED_HEAD
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        mutated_result = validate_phase5(tmp_root)
        if mutated_result["ok"] or "phase5_trace_events_sample_manifest:surveyed_commit_sync" not in mutated_result["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=survey-note-sync-gap")
            return 1

        manifest["surveyed_commit"] = SELF_TEST_HEAD
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        note_text = note_path.read_text(encoding="utf-8")
        note_text = note_text.replace(
            manifest_expectations["phase5_trace_events_sample_manifest.json"]["survey_build_summary"],
            "Build Summary: 17/17 steps succeeded; 99/99 tests passed",
            1,
        )
        note_path.write_text(note_text, encoding="utf-8")
        summary_result = validate_phase5(tmp_root)
        if summary_result["ok"] or "phase5_trace_events_sample_manifest:survey_build_summary" not in summary_result["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=survey-build-summary-gap")
            return 1

        root_manifest = json.loads(
            (ROOT / "zigux/tests/phase5_trace_events_sample_manifest.json").read_text(encoding="utf-8")
        )
        root_manifest["surveyed_commit"] = SELF_TEST_HEAD
        manifest_path.write_text(json.dumps(root_manifest, indent=2) + "\n", encoding="utf-8")
        note_text = (
            ROOT / manifest_expectations["phase5_trace_events_sample_manifest.json"]["survey_note_path"]
        ).read_text(encoding="utf-8")
        note_text = re.sub(
            r"PHASE5_SURVEYED_COMMIT=[0-9a-f]{40}",
            f"PHASE5_SURVEYED_COMMIT={SELF_TEST_HEAD}",
            note_text,
        )
        note_path.write_text(note_text, encoding="utf-8")

        for index, prompt in enumerate(root_manifest["review_prompts"]):
            if "selected-string-slot" in prompt and "callback-path" in prompt:
                root_manifest["review_prompts"][index] = prompt.replace(
                    "callback-path, and teardown contract",
                    "teardown contract",
                )
                break
        else:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=review-prompt-seed-missing")
            return 1

        manifest_path.write_text(json.dumps(root_manifest, indent=2) + "\n", encoding="utf-8")
        prompt_result = validate_phase5(tmp_root)
        if prompt_result["ok"] or "phase5_trace_events_sample_manifest:review_prompt:payload_contract" not in prompt_result["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=review-prompt-gap")
            return 1

        root_manifest = json.loads(
            (ROOT / "zigux/tests/phase5_trace_events_sample_manifest.json").read_text(encoding="utf-8")
        )
        root_manifest["surveyed_commit"] = SELF_TEST_HEAD
        manifest_path.write_text(json.dumps(root_manifest, indent=2) + "\n", encoding="utf-8")
        note_text = (
            ROOT / manifest_expectations["phase5_trace_events_sample_manifest.json"]["survey_note_path"]
        ).read_text(encoding="utf-8")
        note_text = re.sub(
            r"PHASE5_SURVEYED_COMMIT=[0-9a-f]{40}",
            f"PHASE5_SURVEYED_COMMIT={SELF_TEST_HEAD}",
            note_text,
        )
        note_path.write_text(note_text, encoding="utf-8")

        note_text = note_path.read_text(encoding="utf-8").replace(
            survey_note_expectations["phase5_trace_events_sample_manifest.json"]["sample_test_command"],
            "zig test samples/zigux/trace_events_sample_missing.zig",
        )
        note_path.write_text(note_text, encoding="utf-8")
        evidence_result = validate_phase5(tmp_root)
        if evidence_result["ok"] or "phase5_trace_events_sample_manifest:sample_test_command" not in evidence_result["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=survey-note-evidence-gap")
            return 1

        note_text = (
            ROOT / manifest_expectations["phase5_trace_events_sample_manifest.json"]["survey_note_path"]
        ).read_text(encoding="utf-8")
        note_text = re.sub(
            r"PHASE5_SURVEYED_COMMIT=[0-9a-f]{40}",
            f"PHASE5_SURVEYED_COMMIT={SELF_TEST_HEAD}",
            note_text,
        )
        note_path.write_text(note_text, encoding="utf-8")

        sample_root_path = tmp_root / "samples/zigux/README.md"
        sample_root_text = sample_root_path.read_text(encoding="utf-8").replace(
            "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample",
            "current `master` keeps the cmdline helper bundle separate from Phase 5 reference samples",
            1,
        )
        sample_root_path.write_text(sample_root_text, encoding="utf-8")
        sample_root_result = validate_phase5(tmp_root)
        if sample_root_result["ok"] or (
            "sample_root_readme:missing:current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample"
            not in sample_root_result["missing"]
        ):
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=sample-root-cmdline-boundary-gap")
            return 1

        sample_root_path.write_text((ROOT / "samples/zigux/README.md").read_text(encoding="utf-8"), encoding="utf-8")

        script_readme_path = tmp_root / "scripts/zigux/README.md"
        script_readme_text = script_readme_path.read_text(encoding="utf-8").replace(
            "`samples/zigux/runtime_bitmap.zig` plus `samples/zigux/runtime_bitmap_loader.zig` stay cataloged as the separate Phase 9 runtime bitmap survey packet rather than a fifth approved Phase 5 sample",
            "`samples/zigux/runtime_bitmap.zig` and `samples/zigux/runtime_bitmap_loader.zig` stay cataloged as later runtime work",
            1,
        )
        script_readme_path.write_text(script_readme_text, encoding="utf-8")
        script_readme_result = validate_phase5(tmp_root)
        if script_readme_result["ok"] or (
            "script_readme:missing:`samples/zigux/runtime_bitmap.zig` plus `samples/zigux/runtime_bitmap_loader.zig` stay cataloged as the separate Phase 9 runtime bitmap survey packet rather than a fifth approved Phase 5 sample"
            not in script_readme_result["missing"]
        ):
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=script-readme-runtime-bitmap-boundary-gap")
            return 1

        script_readme_path.write_text((ROOT / "scripts/zigux/README.md").read_text(encoding="utf-8"), encoding="utf-8")

        tests_readme_path = tmp_root / "zigux/tests/README.md"
        tests_readme_text = tests_readme_path.read_text(encoding="utf-8").replace(
            "zig test zigux/tests/phase5_trace_events_sample_survey.zig",
            "zig test zigux/tests/phase5_trace_events_sample_missing_survey.zig",
            1,
        )
        tests_readme_path.write_text(tests_readme_text, encoding="utf-8")
        tests_readme_result = validate_phase5(tmp_root)
        if tests_readme_result["ok"] or (
            "tests_readme:missing:zig test zigux/tests/phase5_trace_events_sample_survey.zig"
            not in tests_readme_result["missing"]
        ):
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=tests-readme-replay-gap")
            return 1

        tests_readme_path.write_text((ROOT / "zigux/tests/README.md").read_text(encoding="utf-8"), encoding="utf-8")

        sample_path = tmp_root / sample_source_expectations["phase5_trace_events_sample"]["path"]
        sample_text = sample_path.read_text(encoding="utf-8")
        sample_text = sample_text.replace(
            ".requires_runtime_substrate = false",
            ".requires_runtime_substrate = true",
            1,
        )
        sample_path.write_text(sample_text, encoding="utf-8")
        sample_result = validate_phase5(tmp_root)
        if sample_result["ok"] or "sample_source:phase5_trace_events_sample:missing:.requires_runtime_substrate = false" not in sample_result["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=sample-descriptor-gap")
            return 1

    print("PHASE5_VALIDATOR_SELF_TEST=pass")
    print("PHASE5_VALIDATOR_SELF_TEST_CASE_COUNT=10")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the shared Phase 5 sample review packet.")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in validator drift checks against a temporary Phase 5 fixture tree.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    return report_validation(validate_phase5(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
