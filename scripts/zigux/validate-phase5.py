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
        "runtime_bitmap_loader.zig",
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
    ],
    "Documentation/zigux/review-checklist.md": [
        "phase5_build.zig",
        "descriptor, manifest-backed survey, sample-backed survey note",
        "direct `zig test samples/zigux/...` replays and the paired `zig test zigux/tests/..._survey.zig` replays stay explicit",
        "ships no `samples/zigux/*string*` Phase 5 reference sample",
        "ships no `samples/zigux/*cmdline*` Phase 5 reference sample",
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
        "sample-only blocked Phase 9 pilot",
        "bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold is shipped now",
        "- `samples/zigux/runtime_trace_events_loader.zig`",
        "verify the shared docs still keep string-helper evidence in Phase 7 instead of `samples/zigux/`:",
        "verify the shared docs still keep cmdline evidence in Phase 7 instead of `samples/zigux/`:",
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
        "non_goals": [
            "procfs parity",
            "kfifo_from_user or kfifo_to_user parity",
            "loadable module registration",
            "locking or blocking semantics",
        ],
        "exact_ids": [
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
        "survey_note": "Documentation/zigux/phase5-kfifo-sample-survey.md",
        "survey_summary": "The shared `zigux/tests/phase5_build.zig` entrypoint remains the umbrella review gate recorded in the manifest and contributor prompts, but this bounded verification pass did not rerun the whole Phase 5 sample bundle, so this note no longer republishes the older pre-expansion shared test count.",
        "sample_test": "zig test samples/zigux/bytestream_fifo.zig",
        "sample_result": "All 5 tests passed.",
        "survey_test": "zig test zigux/tests/phase5_bytestream_fifo_survey.zig",
        "survey_result": "All 2 tests passed.",
    },
    "zigux/tests/phase5_kobject_example_manifest.json": {
        "lane_key": "P5-L12",
        "phase": "Phase 5",
        "anchor": "samples/kobject/kobject-example.c",
        "sample_path": "samples/zigux/kobject_example.zig",
        "validation_entrypoint": "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "non_goals": [
            "sysfs file creation parity",
            "kernel_kobj integration",
            "uevent delivery",
            "loadable module registration",
        ],
        "exact_ids": [
            "directory-name",
            "attribute-order",
            "attribute-mode",
            "registration-step",
            "static-name-no-uevent-boundary",
            "pre-registration-boundary",
            "replay-readiness-boundary",
            "ownership-summary",
            "initialized-exit-teardown",
            "foo-roundtrip",
            "shared-b-dispatch",
            "parse-failure",
            "exit-boundary",
        ],
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
        "non_goals": [
            "register_kretprobe parity",
            "unregister_kretprobe parity",
            "pt_regs or regs_return_value parity",
            "loadable module wiring",
        ],
        "exact_ids": [
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
        "survey_note": "Documentation/zigux/phase5-kretprobe-sample-survey.md",
        "survey_summary": "Build Summary: 18/18 steps succeeded; 29/29 tests passed",
        "sample_test": "zig test samples/zigux/kretprobe_example.zig",
        "sample_result": "All 1 tests passed.",
        "survey_test": "zig test zigux/tests/phase5_kretprobe_example_survey.zig",
        "survey_result": "All 2 tests passed.",
    },
    "zigux/tests/phase5_trace_events_sample_manifest.json": {
        "lane_key": "P5-L24",
        "phase": "Phase 5",
        "anchor": "samples/trace_events/trace-events-sample.c",
        "sample_path": "samples/zigux/trace_events_sample.zig",
        "validation_entrypoint": "zig build test --build-file zigux/tests/phase5_build.zig --summary all",
        "non_goals": [
            "CREATE_TRACE_POINTS parity",
            "tracepoint macro parity from trace-events-sample.h",
            "kernel thread scheduling or timeout parity",
            "module registration or unregister wiring parity",
        ],
        "exact_ids": [
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
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def require_text_markers(missing: list[str], root: Path) -> None:
    for rel, markers in TEXT_MARKERS.items():
        content = read_text(root, rel)
        for marker in markers:
            if marker not in content:
                missing.append(f"{rel}:missing:{marker}")


def require_manifests(missing: list[str], root: Path) -> None:
    for rel, spec in MANIFEST_EXPECTATIONS.items():
        data = json.loads(read_text(root, rel))
        if data.get("lane_key") != spec["lane_key"]:
            missing.append(f"{rel}:lane_key")
        if data.get("phase") != spec["phase"]:
            missing.append(f"{rel}:phase")
        if data.get("anchor") != spec["anchor"]:
            missing.append(f"{rel}:anchor")
        if data.get("sample_path") != spec["sample_path"]:
            missing.append(f"{rel}:sample_path")
        if data.get("validation_entrypoint") != spec["validation_entrypoint"]:
            missing.append(f"{rel}:validation_entrypoint")
        surveyed_commit = data.get("surveyed_commit")
        if not isinstance(surveyed_commit, str) or not HEX40.fullmatch(surveyed_commit):
            missing.append(f"{rel}:surveyed_commit")
        if data.get("non_goals") != spec["non_goals"]:
            missing.append(f"{rel}:non_goals")
        exact_ids = spec.get("exact_ids")
        if exact_ids is not None:
            actual = [entry.get("id") for entry in data.get("exact_checks", []) if isinstance(entry, dict)]
            if actual != exact_ids:
                missing.append(f"{rel}:exact_ids")
        note = read_text(root, spec["survey_note"])
        if f"PHASE5_LANE_KEY={spec['lane_key']}" not in note:
            missing.append(f"{rel}:survey_lane_marker")
        if isinstance(surveyed_commit, str) and f"PHASE5_SURVEYED_COMMIT={surveyed_commit}" not in note:
            missing.append(f"{rel}:survey_commit_sync")
        for marker in [spec["survey_summary"], spec["sample_test"], spec["sample_result"], spec["survey_test"], spec["survey_result"]]:
            if marker not in note:
                missing.append(f"{rel}:survey_note:{marker}")


def validate_phase5(root: Path) -> dict[str, object]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return {"ok": False, "missing_files": missing_files, "missing": []}
    missing: list[str] = []
    require_text_markers(missing, root)
    require_manifests(missing, root)
    return {"ok": not missing, "missing_files": [], "missing": missing}


def total_marker_count() -> int:
    count = sum(len(v) for v in TEXT_MARKERS.values())
    for spec in MANIFEST_EXPECTATIONS.values():
        count += 10
        count += len(spec["non_goals"])
        count += len(spec.get("exact_ids", []))
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

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        manifest_path = tmp_root / "zigux/tests/phase5_kobject_example_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["exact_checks"][0]["id"] = "directory-name-drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "zigux/tests/phase5_kobject_example_manifest.json:exact_ids" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=kobject-exact-check-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        manifest_path = tmp_root / "zigux/tests/phase5_kobject_example_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["exact_checks"][6]["id"] = "replay-readiness-boundary-drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "zigux/tests/phase5_kobject_example_manifest.json:exact_ids" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=kobject-replay-readiness-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        manifest_path = tmp_root / "zigux/tests/phase5_kretprobe_example_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["exact_checks"][-1]["id"] = "post-exit-rejection-drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "zigux/tests/phase5_kretprobe_example_manifest.json:exact_ids" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=kretprobe-exact-check-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        manifest_path = tmp_root / "zigux/tests/phase5_trace_events_sample_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["exact_checks"][9]["id"] = "checked-focus-order-drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "zigux/tests/phase5_trace_events_sample_manifest.json:exact_ids" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=trace-events-exact-check-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        note_path = tmp_root / "Documentation/zigux/phase5-kfifo-sample-survey.md"
        note_text = note_path.read_text(encoding="utf-8").replace(
            MANIFEST_EXPECTATIONS["zigux/tests/phase5_bytestream_fifo_manifest.json"]["survey_summary"],
            "Build Summary: 17/17 steps succeeded; 99/99 tests passed",
            1,
        )
        note_path.write_text(note_text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or not any("survey_note" in item for item in missing["missing"]):
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=survey-summary-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        sample_root = tmp_root / "samples/zigux/README.md"
        text = sample_root.read_text(encoding="utf-8").replace(
            "current `master` still ships no `samples/zigux/*cmdline*` Phase 5 reference sample",
            "current `master` keeps cmdline helper work separate",
            1,
        )
        sample_root.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or not any(item.startswith("samples/zigux/README.md") for item in missing["missing"]):
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=sample-root-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        sample_root = tmp_root / "samples/zigux/README.md"
        text = sample_root.read_text(encoding="utf-8").replace(
            "python3 scripts/zigux/validate-phase7.py",
            "python3 scripts/zigux/validate-phase7-phase5.py",
            1,
        )
        sample_root.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "samples/zigux/README.md:missing:python3 scripts/zigux/validate-phase7.py" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=phase7-boundary-validation-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        sample_root = tmp_root / "samples/zigux/README.md"
        text = sample_root.read_text(encoding="utf-8").replace(
            "zig test samples/zigux/kretprobe_example.zig",
            "zig test samples/zigux/kretprobe_review.zig",
            1,
        )
        sample_root.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "samples/zigux/README.md:missing:zig test samples/zigux/kretprobe_example.zig" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=sample-root-focused-replay-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        sample_root = tmp_root / "samples/zigux/README.md"
        text = sample_root.read_text(encoding="utf-8").replace(
            "- `samples/zigux/runtime_trace_events_loader.zig`\n",
            "",
            1,
        )
        sample_root.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or not any(item == "samples/zigux/README.md:missing:- `samples/zigux/runtime_trace_events_loader.zig`" for item in missing["missing"]):
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=trace-events-loader-catalog-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        checklist = tmp_root / "Documentation/zigux/review-checklist.md"
        text = checklist.read_text(encoding="utf-8").replace(
            "runtime-substrate handoff still blocked",
            "runtime-substrate handoff now cleared",
            1,
        )
        checklist.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or not any(item.startswith("Documentation/zigux/review-checklist.md") for item in missing["missing"]):
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=trace-events-loader-boundary-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        tests_readme = tmp_root / "zigux/tests/README.md"
        text = tests_readme.read_text(encoding="utf-8").replace(
            "zig test samples/zigux/kretprobe_example.zig",
            "zig test samples/zigux/kretprobe_review.zig",
            1,
        )
        tests_readme.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "zigux/tests/README.md:missing:zig test samples/zigux/kretprobe_example.zig" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=tests-readme-direct-replay-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        tests_readme = tmp_root / "zigux/tests/README.md"
        text = tests_readme.read_text(encoding="utf-8").replace(
            "zig test zigux/tests/phase5_kobject_example_survey.zig",
            "zig test zigux/tests/phase5_kobject_survey.zig",
            1,
        )
        tests_readme.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "zigux/tests/README.md:missing:zig test zigux/tests/phase5_kobject_example_survey.zig" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=tests-readme-survey-replay-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        tests_readme = tmp_root / "zigux/tests/README.md"
        text = tests_readme.read_text(encoding="utf-8").replace(
            "zig test zigux/tests/phase5_bytestream_fifo.zig",
            "zig test zigux/tests/phase5_bytestream_fifo_review.zig",
            1,
        )
        tests_readme.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "zigux/tests/README.md:missing:zig test zigux/tests/phase5_bytestream_fifo.zig" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=bytestream-helper-replay-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        tests_readme = tmp_root / "zigux/tests/README.md"
        text = tests_readme.read_text(encoding="utf-8").replace(
            "separate Phase 9 runtime bitmap survey packet",
            "later runtime bitmap follow-on work",
            1,
        )
        tests_readme.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "zigux/tests/README.md:missing:separate Phase 9 runtime bitmap survey packet" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=tests-readme-runtime-bitmap-boundary-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        tests_readme = tmp_root / "zigux/tests/README.md"
        text = tests_readme.read_text(encoding="utf-8").replace(
            "runtime-substrate handoff still stays blocked",
            "runtime-substrate handoff now cleared",
            1,
        )
        tests_readme.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "zigux/tests/README.md:missing:runtime-substrate handoff still stays blocked" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=tests-readme-runtime-trace-events-boundary-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        tests_readme = tmp_root / "zigux/tests/README.md"
        text = tests_readme.read_text(encoding="utf-8").replace(
            "current `master` still ships no `samples/zigux/*string*` or `samples/zigux/*cmdline*` Phase 5 reference sample",
            "current `master` keeps helper-only sample boundaries separate",
            1,
        )
        tests_readme.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "zigux/tests/README.md:missing:current `master` still ships no `samples/zigux/*string*` or `samples/zigux/*cmdline*` Phase 5 reference sample" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=tests-readme-phase7-boundary-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        docs_readme = tmp_root / "Documentation/zigux/README.md"
        text = docs_readme.read_text(encoding="utf-8").replace(
            "zig test zigux/tests/phase5_trace_events_sample_survey.zig",
            "zig test zigux/tests/phase5_trace_events_review.zig",
            1,
        )
        docs_readme.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "Documentation/zigux/README.md:missing:zig test zigux/tests/phase5_trace_events_sample_survey.zig" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=docs-readme-survey-replay-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        docs_readme = tmp_root / "Documentation/zigux/README.md"
        text = docs_readme.read_text(encoding="utf-8").replace(
            "ships no `samples/zigux/*string*` reference sample",
            "keeps string-helper evidence under the Phase 7 helper bundle",
            1,
        )
        docs_readme.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "Documentation/zigux/README.md:missing:ships no `samples/zigux/*string*` reference sample" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=docs-readme-string-boundary-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        docs_readme = tmp_root / "Documentation/zigux/README.md"
        text = docs_readme.read_text(encoding="utf-8").replace(
            "no-`samples/zigux/*cmdline*` boundary explicit",
            "cmdline helper evidence stays under the separate Phase 7 bundle",
            1,
        )
        docs_readme.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "Documentation/zigux/README.md:missing:no-`samples/zigux/*cmdline*` boundary explicit" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=docs-readme-cmdline-boundary-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        docs_readme = tmp_root / "Documentation/zigux/README.md"
        text = docs_readme.read_text(encoding="utf-8").replace(
            "zig test zigux/tests/phase5_bytestream_fifo.zig",
            "zig test zigux/tests/phase5_bytestream_fifo_review.zig",
            1,
        )
        docs_readme.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "Documentation/zigux/README.md:missing:zig test zigux/tests/phase5_bytestream_fifo.zig" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=docs-readme-bytestream-helper-replay-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        scripts_readme = tmp_root / "scripts/zigux/README.md"
        text = scripts_readme.read_text(encoding="utf-8").replace(
            "zig test samples/zigux/kobject_example.zig",
            "zig test samples/zigux/kobject_review.zig",
            1,
        )
        scripts_readme.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "scripts/zigux/README.md:missing:zig test samples/zigux/kobject_example.zig" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=scripts-readme-direct-replay-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        scripts_readme = tmp_root / "scripts/zigux/README.md"
        text = scripts_readme.read_text(encoding="utf-8").replace(
            "zig test zigux/tests/phase5_bytestream_fifo.zig",
            "zig test zigux/tests/phase5_bytestream_fifo_review.zig",
            1,
        )
        scripts_readme.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "scripts/zigux/README.md:missing:zig test zigux/tests/phase5_bytestream_fifo.zig" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=scripts-readme-bytestream-helper-replay-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        scripts_readme = tmp_root / "scripts/zigux/README.md"
        text = scripts_readme.read_text(encoding="utf-8").replace(
            "zig test zigux/tests/phase5_trace_events_sample_survey.zig",
            "zig test zigux/tests/phase5_trace_events_review.zig",
            1,
        )
        scripts_readme.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "scripts/zigux/README.md:missing:zig test zigux/tests/phase5_trace_events_sample_survey.zig" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=scripts-readme-survey-replay-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        build_file = tmp_root / "zigux/tests/phase5_build.zig"
        text = build_file.read_text(encoding="utf-8").replace(
            '"phase5-kretprobe-example-sample-tests"',
            '"phase5-kretprobe-example-sample-review"',
            1,
        )
        build_file.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "zigux/tests/phase5_build.zig:missing:phase5-kretprobe-example-sample-tests" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=phase5-build-kretprobe-sample-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        build_file = tmp_root / "zigux/tests/phase5_build.zig"
        text = build_file.read_text(encoding="utf-8").replace(
            '"phase5-kobject-example-survey-tests"',
            '"phase5-kobject-example-survey-review"',
            1,
        )
        build_file.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "zigux/tests/phase5_build.zig:missing:phase5-kobject-example-survey-tests" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=phase5-build-kobject-survey-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        build_file = tmp_root / "zigux/tests/phase5_build.zig"
        text = build_file.read_text(encoding="utf-8").replace(
            '"phase5-kretprobe-example-survey-tests"',
            '"phase5-kretprobe-example-survey-review"',
            1,
        )
        build_file.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or "zigux/tests/phase5_build.zig:missing:phase5-kretprobe-example-survey-tests" not in missing["missing"]:
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=phase5-build-kretprobe-survey-gap")
            return 1

        tmp_root = Path(tmp)
        copy_tree(ROOT, tmp_root)
        sample = tmp_root / "samples/zigux/trace_events_sample.zig"
        text = sample.read_text(encoding="utf-8").replace(
            ".requires_runtime_substrate = false",
            ".requires_runtime_substrate = true",
            1,
        )
        sample.write_text(text, encoding="utf-8")
        missing = validate_phase5(tmp_root)
        if missing["ok"] or not any(item.startswith("samples/zigux/trace_events_sample.zig") for item in missing["missing"]):
            print("PHASE5_VALIDATOR_SELF_TEST=fail")
            print("PHASE5_VALIDATOR_SELF_TEST_REASON=sample-descriptor-gap")
            return 1

    print("PHASE5_VALIDATOR_SELF_TEST=pass")
    print("PHASE5_VALIDATOR_SELF_TEST_CASE_COUNT=28")
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
