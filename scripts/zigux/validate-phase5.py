#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SELF_TEST_HEAD = "0123456789abcdef0123456789abcdef01234567"

REQUIRED_FILES = [
    "scripts/zigux/validate-phase5.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase5-kfifo-sample-survey.md",
    "Documentation/zigux/phase5-kobject-sample-survey.md",
    "Documentation/zigux/phase5-kretprobe-sample-survey.md",
    "Documentation/zigux/phase5-trace-events-sample-survey.md",
    "samples/zigux/README.md",
    "samples/zigux/bytestream_fifo.zig",
    "samples/zigux/kobject_example.zig",
    "samples/zigux/kretprobe_example.zig",
    "samples/zigux/trace_events_sample.zig",
    "zigux/Makefile",
    "zigux/tests/README.md",
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
    ".github/workflows/zigux-bootstrap.yml",
]

TEXT_MARKERS = {
    "zigux/Makefile": [
        "PHONY += phase5-validate phase5-test phase5",
        "phase5-validate:",
        "scripts/zigux/validate-phase5.py",
        "phase5-test:",
        "zigux/tests/phase5_build.zig",
        "phase5: phase5-validate phase5-test",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "Validate Phase 5 reference sample packet",
        "make -C zigux phase5-validate",
        "Run Phase 5 reference sample tests",
        "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
    ],
    "scripts/zigux/README.md": [
        "validate-phase5.py",
        "make -C zigux phase5-validate",
        "make -C zigux phase5",
        "zigux/tests/phase5_build.zig",
        "samples/zigux/README.md",
        "zig test samples/zigux/bytestream_fifo.zig",
        "zig test zigux/tests/phase5_bytestream_fifo.zig",
        "zig test samples/zigux/kobject_example.zig",
        "zig test samples/zigux/kretprobe_example.zig",
        "zig test samples/zigux/trace_events_sample.zig",
        "zig test zigux/tests/phase5_bytestream_fifo_survey.zig",
        "zig test zigux/tests/phase5_kobject_example_survey.zig",
        "zig test zigux/tests/phase5_kretprobe_example_survey.zig",
        "zig test zigux/tests/phase5_trace_events_sample_survey.zig",
        "zigux/tests/phase5_kobject_example.zig",
        "zigux/tests/phase5_kretprobe_example.zig",
        "zigux/tests/phase5_trace_events_sample.zig",
        "runtime_bitmap_loader.zig",
        "samples/zigux/runtime_trace_events.zig",
        "samples/zigux/runtime_trace_events_loader.zig",
        "runtime-substrate handoff still stays blocked",
    ],
    "zigux/tests/README.md": [
        "zigux/tests/phase5_build.zig",
        "zigux/tests/phase5_bytestream_fifo_manifest.json",
        "zigux/tests/phase5_kobject_example_manifest.json",
        "zigux/tests/phase5_kretprobe_example_manifest.json",
        "zigux/tests/phase5_trace_events_sample_manifest.json",
        "zig test samples/zigux/bytestream_fifo.zig",
        "zig test zigux/tests/phase5_bytestream_fifo.zig",
        "zig test samples/zigux/kobject_example.zig",
        "zig test samples/zigux/kretprobe_example.zig",
        "zig test samples/zigux/trace_events_sample.zig",
        "zig test zigux/tests/phase5_bytestream_fifo_survey.zig",
        "zig test zigux/tests/phase5_kobject_example_survey.zig",
        "zig test zigux/tests/phase5_kretprobe_example_survey.zig",
        "zig test zigux/tests/phase5_trace_events_sample_survey.zig",
        "make -C zigux phase5-validate",
        "samples/zigux/runtime_bitmap.zig",
        "samples/zigux/runtime_bitmap_loader.zig",
        "separate Phase 9 runtime bitmap survey packet",
        "samples/zigux/runtime_trace_events.zig",
        "sample-only blocked Phase 9 pilot",
        "samples/zigux/runtime_trace_events_loader.zig",
        "runtime-substrate handoff still stays blocked",
        "current `master` still ships no `samples/zigux/*string*` or `samples/zigux/*cmdline*` Phase 5 reference sample",
        "lib/string_helpers.zig",
        "zigux/tests/phase7_string_helpers.zig",
        "lib/cmdline.zig",
        "zigux/tests/phase7_cmdline.zig",
        "zigux/tests/phase7_build.zig",
        "verify no Phase 5 rbtree sample has appeared under this sample root:",
        "verify the shared docs still keep rbtree evidence in Phase 7 instead of `samples/zigux/`:",
        "lib/rbtree.zig",
        "zigux/tests/phase7_rbtree.zig",
    ],
    "Documentation/zigux/README.md": [
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
        "zig test samples/zigux/bytestream_fifo.zig",
        "zig test zigux/tests/phase5_bytestream_fifo.zig",
        "zig test samples/zigux/kobject_example.zig",
        "zig test samples/zigux/kretprobe_example.zig",
        "zig test samples/zigux/trace_events_sample.zig",
        "zig test zigux/tests/phase5_bytestream_fifo_survey.zig",
        "zig test zigux/tests/phase5_kobject_example_survey.zig",
        "zig test zigux/tests/phase5_kretprobe_example_survey.zig",
        "zig test zigux/tests/phase5_trace_events_sample_survey.zig",
        "ships no `samples/zigux/*string*` reference sample",
        "no-`samples/zigux/*cmdline*` boundary explicit",
        "no-`samples/zigux/*rbtree*` boundary explicit",
        "lib/rbtree.zig",
        "zigux/tests/phase7_rbtree.zig",
    ],
    "Documentation/zigux/review-checklist.md": [
        "phase5_build.zig",
        "descriptor, manifest-backed survey, sample-backed survey note",
        "direct `zig test samples/zigux/...` replays and the paired `zig test zigux/tests/..._survey.zig` replays stay explicit",
        "ships no `samples/zigux/*string*` Phase 5 reference sample",
        "ships no `samples/zigux/*cmdline*` Phase 5 reference sample",
        "ships no `samples/zigux/*rbtree*` Phase 5 reference sample",
        "lib/rbtree.zig",
        "zigux/tests/phase7_rbtree.zig",
        "runtime_bitmap_loader.zig",
        "bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold is now shipped",
        "runtime-substrate handoff still blocked",
    ],
    "samples/zigux/README.md": [
        "Phase 5 reference samples",
        "Bytestream FIFO review packet",
        "Kobject review packet",
        "Kretprobe review packet",
        "Trace-events review packet",
        "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "zig test samples/zigux/bytestream_fifo.zig",
        "zig test zigux/tests/phase5_bytestream_fifo.zig",
        "zig test samples/zigux/kobject_example.zig",
        "zig test samples/zigux/kretprobe_example.zig",
        "zig test samples/zigux/trace_events_sample.zig",
        "zig test zigux/tests/phase5_bytestream_fifo_survey.zig",
        "zig test zigux/tests/phase5_kobject_example_survey.zig",
        "zig test zigux/tests/phase5_kretprobe_example_survey.zig",
        "zig test zigux/tests/phase5_trace_events_sample_survey.zig",
        "approved payload-and-callback idiom",
        "current `master` still ships no `samples/zigux/*string*` Phase 5 reference sample",
        "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample",
        "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample",
        "sample-only blocked Phase 9 pilot",
        "bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold is shipped now",
        "- `samples/zigux/runtime_trace_events_loader.zig`",
        "verify the shared docs still keep string-helper evidence in Phase 7 instead of `samples/zigux/`:",
        "verify the shared docs still keep cmdline evidence in Phase 7 instead of `samples/zigux/`:",
        "verify the shared docs still keep rbtree evidence in Phase 7 instead of `samples/zigux/`:",
        "lib/rbtree.zig",
        "zigux/tests/phase7_rbtree.zig",
        "python3 scripts/zigux/validate-phase7.py",
    ],
    "zigux/tests/phase5_build.zig": [
        '../../samples/zigux/bytestream_fifo.zig',
        '../../samples/zigux/kobject_example.zig',
        '../../samples/zigux/kretprobe_example.zig',
        '../../samples/zigux/trace_events_sample.zig',
        'phase5-bytestream-fifo-sample-tests',
        'phase5-bytestream-fifo-tests',
        'phase5-kobject-example-sample-tests',
        'phase5-kobject-example-tests',
        'phase5-kretprobe-example-sample-tests',
        'phase5-kretprobe-example-tests',
        'phase5-trace-events-sample-tests',
        'phase5-bytestream-fifo-survey-tests',
        'phase5-kobject-example-survey-tests',
        'phase5-kretprobe-example-survey-tests',
        'phase5-trace-events-sample-survey-tests',
    ],
    "samples/zigux/bytestream_fifo.zig": [
        '.name = "bytestream_fifo"',
        '.anchor = "samples/kfifo/bytestream-example.c"',
        '.requires_runtime_substrate = false',
        '.provides_selfcheck = true',
        '.storage_backing = .embedded_fixed_buffer',
    ],
    "samples/zigux/kobject_example.zig": [
        '.name = "kobject_example"',
        '.anchor = "samples/kobject/kobject-example.c"',
        '.requires_runtime_substrate = false',
        '.provides_selfcheck = true',
    ],
    "samples/zigux/kretprobe_example.zig": [
        '.name = "kretprobe_example"',
        '.anchor = "samples/kprobes/kretprobe_example.c"',
        '.requires_runtime_substrate = false',
        '.provides_selfcheck = true',
    ],
    "samples/zigux/trace_events_sample.zig": [
        '.name = "trace_events_sample"',
        '.anchor = "samples/trace_events/trace-events-sample.c"',
        '.requires_runtime_substrate = false',
        '.provides_selfcheck = true',
    ],
}

MANIFEST_EXPECTATIONS = {
    "zigux/tests/phase5_bytestream_fifo_manifest.json": {
        "lane_key": "P5-L04",
        "phase": "Phase 5",
        "anchor": "samples/kfifo/bytestream-example.c",
        "sample_path": "samples/zigux/bytestream_fifo.zig",
        "validation_entrypoint": "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "non_goals": ["procfs parity", "kfifo_from_user or kfifo_to_user parity", "loadable module registration", "locking or blocking semantics"],
        "exact_ids": ["initial-fill-len", "first-drain", "second-drain-and-requeue", "transfer-count-contract", "skip-and-peek", "wrapped-preview-prefix", "snapshot-before-final-drain", "fill-to-capacity", "final-drain-sequence", "storage-backing-contract", "bounded-helper-behavior", "short-drain-prefix", "preview-truncation", "queue-only-reset", "checked-focus-list", "lifecycle-boundary", "lifecycle-guards-and-counters"],
        "survey_note": "Documentation/zigux/phase5-kfifo-sample-survey.md",
        "survey_summary": "The shared `zigux/tests/phase5_build.zig` entrypoint remains the umbrella review gate recorded in the manifest and contributor prompts, but this bounded verification pass did not rerun the whole Phase 5 sample bundle, so this note no longer republishes the older pre-expansion shared test count.",
        "sample_test": "zig test samples/zigux/bytestream_fifo.zig",
        "sample_result": "All 5 tests passed.",
        "survey_test": "zig test zigux/tests/phase5_bytestream_fifo_survey.zig",
        "survey_result": "All 2 tests passed.",
    },
    "zigux/tests/phase5_kobject_example_manifest.json": {
        "lane_key": "P5-L10",
        "phase": "Phase 5",
        "anchor": "samples/kobject/kobject-example.c",
        "sample_path": "samples/zigux/kobject_example.zig",
        "validation_entrypoint": "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "non_goals": ["sysfs file creation parity", "kernel_kobj integration", "uevent delivery", "loadable module registration"],
        "exact_ids": ["directory-name", "attribute-order", "attribute-mode", "registration-step", "static-name-no-uevent-boundary", "pre-registration-boundary", "replay-readiness-boundary", "ownership-summary", "initialized-exit-teardown", "foo-roundtrip", "shared-b-dispatch", "parse-failure", "exit-boundary"],
        "survey_note": "Documentation/zigux/phase5-kobject-sample-survey.md",
        "survey_summary": "The shared `zigux/tests/phase5_build.zig` entrypoint remains the umbrella review gate recorded in the manifest and contributor prompts, but this bounded verification pass did not rerun the whole Phase 5 sample bundle.",
        "sample_test": "zig test samples/zigux/kobject_example.zig",
        "sample_result": "All 6 tests passed.",
        "survey_test": "zig test zigux/tests/phase5_kobject_example_survey.zig",
        "survey_result": "All 2 tests passed.",
    },
    "zigux/tests/phase5_kretprobe_example_manifest.json": {
        "lane_key": "P5-L22",
        "phase": "Phase 5",
        "anchor": "samples/kprobes/kretprobe_example.c",
        "sample_path": "samples/zigux/kretprobe_example.zig",
        "validation_entrypoint": "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "non_goals": ["register_kretprobe parity", "unregister_kretprobe parity", "pt_regs or regs_return_value parity", "loadable module wiring"],
        "exact_ids": ["default-symbol", "pre-init-retargeting", "skip-kernel-thread", "private-data-shape", "return-duration", "timestamp-order-boundary", "maxactive-budget", "lifecycle-guard-boundaries", "missed-summary", "outstanding-instance-boundary", "post-exit-rejection"],
        "survey_note": "Documentation/zigux/phase5-kretprobe-sample-survey.md",
        "survey_summary": "- this lane-local refresh used a focused survey-packet scratch replay with the directly coupled note, manifest, shared sample-root catalog, shared tests-root guide, top-level docs-root guide, and shared review checklist; no live repo checkout was available for a fresh `zig test samples/zigux/kretprobe_example.zig` or `zig build test --build-file zigux/tests/phase5_build.zig --summary all` replay in this run",
        "sample_test": "zig test samples/zigux/kretprobe_example.zig",
        "sample_result": "All 5 tests passed.",
        "survey_test": "zig test zigux/tests/phase5_kretprobe_example_survey.zig",
        "survey_result": "All 2 tests passed.",
    },
    "zigux/tests/phase5_trace_events_sample_manifest.json": {
        "lane_key": "P5-L24",
        "phase": "Phase 5",
        "anchor": "samples/trace_events/trace-events-sample.c",
        "sample_path": "samples/zigux/trace_events_sample.zig",
        "validation_entrypoint": "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "non_goals": ["CREATE_TRACE_POINTS parity", "tracepoint macro parity from trace-events-sample.h", "kernel thread scheduling or timeout parity", "module registration or unregister wiring parity"],
        "exact_ids": ["descriptor-anchor", "message-and-string-shape", "modulo-string-cycle", "iteration-cues", "array-and-sentinel-shape", "bitmask-and-rel-loc", "vararg-payload-path", "event-family-counts", "lifecycle-summary-counts", "checked-focus-order", "callback-registration-balance", "pre-registration-callback-rejection", "single-registration-boundary", "registration-underflow-and-armed-exit", "post-exit-rejection"],
        "survey_note": "Documentation/zigux/phase5-trace-events-sample-survey.md",
        "survey_summary": "Build Summary: 18/18 steps succeeded; 29/29 tests passed",
        "sample_test": "zig test samples/zigux/trace_events_sample.zig",
        "sample_result": "All 5 tests passed.",
        "survey_test": "zig test zigux/tests/phase5_trace_events_sample_survey.zig",
        "survey_result": "All 2 tests passed.",
    },
}


def read_text(root: Path, rel: str) -> str:
    return (root / rel).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def require_text_markers(missing: list[str], root: Path) -> None:
    for rel, markers in TEXT_MARKERS.items():
        content = read_text(root, rel)
        for marker in markers:
            if marker not in content:
                missing.append(f"{rel}:missing:{marker}")


def require_manifests(missing: list[str], root: Path) -> None:
    for rel, spec in MANIFEST_EXPECTATIONS.items():
        data = json.loads(read_text(root, rel))
        for field in ("lane_key", "phase", "anchor", "sample_path", "validation_entrypoint"):
            if data.get(field) != spec[field]:
                missing.append(f"{rel}:{field}")
        surveyed_commit = data.get("surveyed_commit")
        if not isinstance(surveyed_commit, str) or not HEX40.fullmatch(surveyed_commit):
            missing.append(f"{rel}:surveyed_commit")
        if data.get("non_goals") != spec["non_goals"]:
            missing.append(f"{rel}:non_goals")
        actual_ids = [entry.get("id") for entry in data.get("exact_checks", []) if isinstance(entry, dict)]
        if actual_ids != spec["exact_ids"]:
            missing.append(f"{rel}:exact_ids")
        note = read_text(root, spec["survey_note"])
        if f"PHASE5_LANE_KEY={spec['lane_key']}" not in note:
            missing.append(f"{rel}:survey_lane_marker")
        if f"PHASE5_SURVEYED_COMMIT={surveyed_commit}" not in note:
            missing.append(f"{rel}:survey_commit_sync")
        for marker in [spec["survey_summary"], spec["sample_test"], spec["sample_result"], spec["survey_test"], spec["survey_result"]]:
            if marker not in note:
                missing.append(f"{rel}:survey_note:{marker}")


def validate_phase5(root: Path) -> dict[str, object]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return {"ok": False, "missing_files": missing_files, "missing": []}
    missing = []
    require_text_markers(missing, root)
    require_manifests(missing, root)
    return {"ok": not missing, "missing_files": [], "missing": missing}


def total_marker_count() -> int:
    count = sum(len(markers) for markers in TEXT_MARKERS.values())
    for spec in MANIFEST_EXPECTATIONS.values():
        count += 10 + len(spec["non_goals"]) + len(spec["exact_ids"])
    return count


def report_validation(result: dict[str, object]) -> int:
    if result["missing_files"]:
        print("PHASE5_VALIDATION=fail")
        print("MISSING_PHASE5_FILES_START")
        for item in result["missing_files"]:
            print(item)
        print("MISSING_PHASE5_FILES_END")
        return 1
    if result["missing"]:
        print("PHASE5_VALIDATION=fail")
        print("MISSING_PHASE5_MARKERS_START")
        for item in result["missing"]:
            print(item)
        print("MISSING_PHASE5_MARKERS_END")
        return 1
    print("PHASE5_VALIDATION=pass")
    print(f"PHASE5_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE5_REQUIRED_MARKER_COUNT={total_marker_count()}")
    return 0


def copy_tree(src_root: Path, dst_root: Path) -> None:
    for rel in REQUIRED_FILES:
        dst = dst_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(read_text(src_root, rel), encoding="utf-8")


def require_missing(result: dict[str, object], expected: str) -> bool:
    return (not result["ok"]) and expected in result["missing"]


def run_self_test() -> int:
    live = validate_phase5(ROOT)
    if not live["ok"]:
        print("PHASE5_VALIDATOR_SELF_TEST=fail")
        print("PHASE5_VALIDATOR_SELF_TEST_REASON=live-tree-validation-failed")
        for item in live["missing"]:
            print(item)
        return 1

    with tempfile.TemporaryDirectory(prefix="zigux_phase5_validator_selftest_") as tmp:
        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        manifest_path = tmp_root / "zigux/tests/phase5_bytestream_fifo_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["surveyed_commit"] = SELF_TEST_HEAD
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if validate_phase5(tmp_root)["ok"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=surveyed-commit-sync-gap")
            return 1

        for rel, index, value, reason in [
            ("zigux/tests/phase5_kobject_example_manifest.json", 0, "directory-name-drift", "kobject-exact-check-gap"),
            ("zigux/tests/phase5_kretprobe_example_manifest.json", -1, "post-exit-rejection-drift", "kretprobe-exact-check-gap"),
            ("zigux/tests/phase5_trace_events_sample_manifest.json", 9, "checked-focus-order-drift", "trace-events-exact-check-gap"),
        ]:
            tmp_root = Path(tmp)
            copy_tree(ROOT, tmp_root)
            manifest_path = tmp_root / rel
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["exact_checks"][index]["id"] = value
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            if not require_missing(validate_phase5(tmp_root), f"{rel}:exact_ids"):
                print("PHASE5_VALIDATOR_SELF_TEST=fail")
                print(f"PHASE5_VALIDATOR_SELF_TEST_REASON={reason}")
                return 1

        for rel, old, new, expected, reason in [
            ("Documentation/zigux/phase5-kfifo-sample-survey.md", MANIFEST_EXPECTATIONS["zigux/tests/phase5_bytestream_fifo_manifest.json"]["survey_summary"], "Build Summary: 17/17 steps succeeded; 99/99 tests passed", "zigux/tests/phase5_bytestream_fifo_manifest.json:survey_note:Build Summary: 17/17 steps succeeded; 99/99 tests passed", "survey-summary-gap"),
            ("samples/zigux/README.md", "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample", "current `master` keeps cmdline helper work separate", "samples/zigux/README.md:missing:current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample", "sample-root-cmdline-boundary-gap"),
            ("samples/zigux/README.md", "current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample", "current `master` keeps rbtree helper work separate", "samples/zigux/README.md:missing:current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample", "sample-root-rbtree-boundary-gap"),
            ("Documentation/zigux/review-checklist.md", "runtime-substrate handoff still blocked", "runtime-substrate handoff now cleared", "Documentation/zigux/review-checklist.md:missing:runtime-substrate handoff still blocked", "review-checklist-runtime-handoff-gap"),
            ("Documentation/zigux/README.md", "zig test zigux/tests/phase5_trace_events_sample_survey.zig", "zig test zigux/tests/phase5_trace_events_review.zig", "Documentation/zigux/README.md:missing:zig test zigux/tests/phase5_trace_events_sample_survey.zig", "docs-readme-survey-replay-gap"),
            ("scripts/zigux/README.md", "zig test samples/zigux/kobject_example.zig", "zig test samples/zigux/kobject_review.zig", "scripts/zigux/README.md:missing:zig test samples/zigux/kobject_example.zig", "scripts-readme-direct-replay-gap"),
            ("scripts/zigux/README.md", "zigux/tests/phase5_kretprobe_example.zig", "zigux/tests/phase5_kretprobe_review.zig", "scripts/zigux/README.md:missing:zigux/tests/phase5_kretprobe_example.zig", "scripts-readme-focused-replay-gap"),
            ("scripts/zigux/README.md", "runtime-substrate handoff still stays blocked", "runtime-substrate handoff now cleared", "scripts/zigux/README.md:missing:runtime-substrate handoff still stays blocked", "scripts-readme-runtime-handoff-gap"),
            ("zigux/tests/phase5_build.zig", '"phase5-kretprobe-example-sample-tests"', '"phase5-kretprobe-example-sample-review"', "zigux/tests/phase5_build.zig:missing:phase5-kretprobe-example-sample-tests", "phase5-build-kretprobe-sample-gap"),
            ("samples/zigux/trace_events_sample.zig", ".requires_runtime_substrate = false", ".requires_runtime_substrate = true", "samples/zigux/trace_events_sample.zig:missing:.requires_runtime_substrate = false", "sample-descriptor-gap"),
        ]:
            tmp_root = Path(tmp)
            copy_tree(ROOT, tmp_root)
            path = tmp_root / rel
            path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")
            if not require_missing(validate_phase5(tmp_root), expected):
                print("PHASE5_VALIDATOR_SELF_TEST=fail")
                print(f"PHASE5_VALIDATOR_SELF_TEST_REASON={reason}")
                return 1

    print("PHASE5_VALIDATOR_SELF_TEST=pass")
    print("PHASE5_VALIDATOR_SELF_TEST_CASE_COUNT=13")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the shared Phase 5 sample review packet.")
    parser.add_argument("--self-test", action="store_true", help="Run built-in validator drift checks against a temporary Phase 5 fixture tree.")
    args = parser.parse_args(argv)
    if args.self_test:
        return run_self_test()
    return report_validation(validate_phase5(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
