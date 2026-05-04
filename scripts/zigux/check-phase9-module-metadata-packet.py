#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

SURVEY_PATH = "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md"
MANIFEST_PATH = "zigux/tests/runtime_module_metadata_manifest.json"
SURVEY_TEST_PATH = "zigux/tests/runtime_module_metadata_survey.zig"
CHECKER_PATH = "scripts/zigux/check-phase9-module-metadata-packet.py"
VALIDATE_PHASE9_PATH = "scripts/zigux/validate-phase9.py"
MAKEFILE_PATH = "zigux/Makefile"
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"
RUNTIME_LOADER_PATH = "zigux/kernel/runtime_loader.zig"
TESTS_README_PATH = "zigux/tests/README.md"
ATOMIC64_LOADER_PATH = "samples/zigux/runtime_atomic64_loader.zig"
BITMAP_LOADER_PATH = "samples/zigux/runtime_bitmap_loader.zig"
KRETPROBE_LOADER_PATH = "samples/zigux/runtime_kretprobe_loader.zig"
TRACE_EVENTS_LOADER_PATH = "samples/zigux/runtime_trace_events_loader.zig"

REQUIRED_FILES = [
    SURVEY_PATH,
    MANIFEST_PATH,
    SURVEY_TEST_PATH,
    CHECKER_PATH,
    VALIDATE_PHASE9_PATH,
    MAKEFILE_PATH,
    PHASE9_BUILD_PATH,
    RUNTIME_LOADER_PATH,
    TESTS_README_PATH,
    ATOMIC64_LOADER_PATH,
    BITMAP_LOADER_PATH,
    KRETPROBE_LOADER_PATH,
    TRACE_EVENTS_LOADER_PATH,
]

SURVEY_REQUIRED_MARKERS = [
    "`PHASE9_SLICE=runtime-module-metadata-depmod-bridge-survey`",
    "ModuleDescriptor",
    "requires_runtime_substrate",
    "provides_selftest_hook",
    "RuntimeLoadRequest",
    "module_name",
    "command_name",
    "entry_symbol",
    "exit_symbol",
    "handoff_stage",
    "allocator_handoff",
    "samples/zigux/runtime_trace_events_loader.zig",
    "four landed loader-plan files now stay at",
    "the shared runtime loader currently exposes three tagged loader lanes: `atomic64`, `bitmap`, and `kretprobe`",
    "still stops outside that shared `RuntimeLoadRequest` union",
    "MODULE_INFO()",
    "MODULE_ALIAS()",
    ".modinfo",
    "modules.alias",
    "modules.order",
    "modules.builtin",
    "Module.symvers",
    "scripts/depmod.sh",
    "- `python3 scripts/zigux/validate-phase9.py --self-test`",
    "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`",
    "- `python3 scripts/zigux/validate-phase9.py`",
    "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`",
    "- `make -C zigux phase9-validate`",
    "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`",
    "- `zig test zigux/tests/runtime_module_metadata_survey.zig`",
    "- `make -C zigux phase9-module-metadata-survey`",
]

MODULE_METADATA_SURVEY_EXACT_ONCE_MARKERS = [
    "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`\n",
    "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`\n",
    "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`\n",
    "- `zig test zigux/tests/runtime_module_metadata_survey.zig`\n",
    "- `make -C zigux phase9-module-metadata-survey`\n",
]

VALIDATE_PHASE9_REQUIRED_MARKERS = [
    "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
    "zigux/tests/runtime_module_metadata_manifest.json",
    "zigux/tests/runtime_module_metadata_survey.zig",
    "scripts/zigux/check-phase9-module-metadata-packet.py",
    "phase9-runtime-module-metadata-survey-tests",
]

MAKEFILE_REQUIRED_MARKERS = [
    "PHONY += phase9-validate phase9-test phase9-loader-gap-survey phase9-loader-commit-alignment-survey phase9-non-owner-boundary-survey phase9-module-metadata-survey phase9-kretprobe-survey phase9-trace-events-survey phase9",
    "phase9-module-metadata-survey:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_module_metadata_survey.zig\n",
]

PHASE9_BUILD_REQUIRED_MARKERS = [
    "runtime_module_metadata_survey.zig",
    "phase9-runtime-module-metadata-survey-tests",
]

SURVEY_TEST_REQUIRED_MARKERS = [
    'test "runtime module metadata manifest keeps the dedicated descriptor and depmod-gap packet explicit" {',
    'test "runtime module metadata docs stay aligned with the manifest-backed surveyed commit" {',
    'test "runtime module metadata survey note keeps descriptor fields, shared loader metadata, and depmod gaps explicit" {',
    'test "runtime module metadata survey proves the landed loader-plan scaffolds stay explicit and the shared metadata boundary stays narrow" {',
    'test "runtime module metadata survey proves the live starter descriptors and shared loader metadata surface directly" {',
    'test "runtime module metadata survey keeps the shared phase9 validator route explicit" {',
    '"Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md"',
    '"zigux/tests/runtime_module_metadata_manifest.json"',
    '"zigux/kernel/runtime_loader.zig"',
    '"samples/zigux/runtime_atomic64_loader.zig"',
    '"samples/zigux/runtime_bitmap_loader.zig"',
    '"samples/zigux/runtime_kretprobe_loader.zig"',
    '"samples/zigux/runtime_trace_events_loader.zig"',
    '"samples/zigux/runtime_trace_events.zig"',
    '"scripts/zigux/check-phase9-module-metadata-packet.py"',
    '"scripts/zigux/validate-phase9.py"',
    '"zigux/tests/phase9_build.zig"',
    '"zigux/tests/README.md"',
    '"MODULE_INFO()"',
    '"MODULE_ALIAS()"',
    '"scripts/depmod.sh"',
    '"RuntimeLoadRequest"',
    'std.testing.expect(std.mem.indexOf(u8, runtime_trace_events_loader, "RuntimeLoadRequest") == null);',
    'try expectContainsAll(validate_phase9, &.{',
    '"Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md"',
    '"zigux/tests/runtime_module_metadata_manifest.json"',
    '"zigux/tests/runtime_module_metadata_survey.zig"',
    '"scripts/zigux/check-phase9-module-metadata-packet.py"',
    '"phase9-runtime-module-metadata-survey-tests"',
    "waitingOnRuntimeSubstrate",
    "releasedWithoutSubstrate",
    "register_kretprobe",
    "foo_bar_reg",
    "foo_bar_unreg",
]

RUNTIME_LOADER_REQUIRED_MARKERS = [
    "pub const RuntimeLoadRequest = struct",
    "module_name",
    "command_name",
    "entry_symbol",
    "exit_symbol",
    "handoff_stage",
    "allocator_handoff",
]

ATOMIC64_LOADER_REQUIRED_MARKERS = [
    "pub const RuntimeAtomic64LoadPlan = struct",
    "pub fn toSharedRequest(plan: RuntimeAtomic64LoadPlan) runtime_loader.RuntimeLoadRequest",
    '"zigux_runtime_atomic64_init"',
    '"zigux_runtime_atomic64_exit"',
    "waitingOnRuntimeSubstrate",
    "releasedWithoutSubstrate",
    "perf-runtime-atomic64",
]

BITMAP_LOADER_REQUIRED_MARKERS = [
    "pub const RuntimeBitmapLoadPlan = struct",
    "pub fn toSharedRequest(plan: RuntimeBitmapLoadPlan) runtime_loader.RuntimeLoadRequest",
    '"zigux_runtime_bitmap_init"',
    '"zigux_runtime_bitmap_exit"',
    "waitingOnRuntimeSubstrate",
    "releasedWithoutSubstrate",
    "perf-runtime-bitmap",
]

KRETPROBE_LOADER_REQUIRED_MARKERS = [
    "pub const RuntimeKretprobeLoadPlan = struct",
    "pub fn toSharedRequest(plan: RuntimeKretprobeLoadPlan) runtime_loader.RuntimeLoadRequest",
    '"register_kretprobe"',
    '"unregister_kretprobe"',
    '"zigux_runtime_kretprobe_init"',
    '"zigux_runtime_kretprobe_exit"',
    "waitingOnRuntimeSubstrate",
    "releasedWithoutSubstrate",
    "perf-runtime-kretprobe",
]

TRACE_EVENTS_LOADER_REQUIRED_MARKERS = [
    'const runtime_loader = @import("runtime_loader");',
    "pub const LoaderStage = runtime_loader.LoaderStage;",
    "pub const RuntimeTraceEventsLoadPlan = struct",
    "register_api",
    "unregister_api",
    "main_thread_label",
    "function_thread_label",
    "pub fn requestRuntimeLoad",
    "pub fn releaseWithoutSubstrate",
    '"zigux_runtime_trace_events_init"',
    '"zigux_runtime_trace_events_exit"',
    '"foo_bar_reg"',
    '"foo_bar_unreg"',
]

LOADER_PLAN_FORBIDDEN_MARKERS = [
    "MODULE_INFO(",
    "MODULE_ALIAS(",
    ".modinfo",
    "modules.alias",
    "scripts/depmod.sh",
]

TESTS_README_REQUIRED_MARKERS = [
    "`zigux/tests/runtime_module_metadata_survey.zig`",
    "`zigux/tests/runtime_module_metadata_manifest.json`",
    "`scripts/zigux/validate-phase9.py`",
    "`make -C zigux phase9-validate`",
    "keep the dedicated Phase 9 module-metadata packet explicit beside the loader-gap packet",
    "`Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`",
    "absent depmod-facing metadata without implying `.modinfo`, `MODULE_ALIAS()`, or `scripts/depmod.sh` parity",
]

EXPECTED_DEPMOD_GAP_SURFACES = [
    "MODULE_INFO()",
    "MODULE_ALIAS()",
    ".modinfo",
    "modules.alias",
    "modules.order",
    "modules.builtin",
    "Module.symvers",
    "scripts/depmod.sh",
]

EXPECTED_REVIEW_PROMPTS = [
    "the four runtime starter descriptors still agree on name, anchor, requires_runtime_substrate, and provides_selftest_hook instead of drifting into sample-local metadata stories",
    "the four landed loader plans stay explicit, and the shared RuntimeLoadRequest metadata surface still stays limited to the current reviewable fields and three landed loader lanes instead of pretending the trace-events loader has already joined the shared union",
    "the dedicated survey packet still keeps MODULE_INFO(), MODULE_ALIAS(), .modinfo, modules.alias, modules.order, modules.builtin, Module.symvers, and scripts/depmod.sh explicit as absent depmod-facing surfaces instead of counting starter descriptors or loader scaffolds as shipped loadable-module parity",
]

def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")

def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]

def count_exact_occurrence(text: str, marker: str) -> int:
    return text.count(marker)

def extract_markdown_surveyed_commit(text: str, label: str) -> tuple[str | None, str | None]:
    match = re.search(r"`PHASE9_SURVEYED_COMMIT=([0-9a-f]{40})`", text)
    if not match:
        return None, f"{label}:missing_or_invalid_surveyed_commit_marker"
    return match.group(1), None

def validate_manifest_packet(root: Path) -> list[str]:
    survey_text = read_text(root, SURVEY_PATH)
    manifest_text = read_text(root, MANIFEST_PATH)
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        return ["manifest:json_decode_failed"]
    failures: list[str] = []
    manifest_commit = manifest.get("surveyed_commit")
    if not isinstance(manifest_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", manifest_commit):
        failures.append("manifest:invalid_surveyed_commit")
    else:
        survey_commit, survey_error = extract_markdown_surveyed_commit(survey_text, "survey")
        if survey_error:
            failures.append(survey_error)
        elif survey_commit != manifest_commit:
            failures.append("survey:surveyed_commit_mismatch")
    if manifest.get("lane_key") != "P9-L07":
        failures.append("manifest:lane_key_drift")
    if manifest.get("phase") != "Phase 9":
        failures.append("manifest:phase_drift")
    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        failures.append("manifest:survey_summary_missing")
    else:
        expected_summary = {
            "runtime_descriptor_count": 4,
            "runtime_loader_lane_count": 3,
            "runtime_loader_plan_count": 4,
            "runtime_sample_only_blocked_count": 0,
            "shared_metadata_field_count": 9,
            "depmod_gap_count": 8,
            "shared_runtime_loader_present": True,
            "runtime_trace_events_loader_present": True,
        }
        for key, value in expected_summary.items():
            if summary.get(key) != value:
                failures.append(f"manifest:summary_{key}_drift")
    if manifest.get("depmod_gap_surfaces") != EXPECTED_DEPMOD_GAP_SURFACES:
        failures.append("manifest:depmod_gap_surfaces_drift")
    if manifest.get("runtime_loader_plans") != [
        "samples/zigux/runtime_atomic64_loader.zig",
        "samples/zigux/runtime_bitmap_loader.zig",
        "samples/zigux/runtime_kretprobe_loader.zig",
        "samples/zigux/runtime_trace_events_loader.zig",
    ]:
        failures.append("manifest:runtime_loader_plans_drift")
    sample_only_blocked = manifest.get("runtime_sample_only_blocked")
    if sample_only_blocked != []:
        failures.append("manifest:runtime_sample_only_blocked_drift")
    delivery_evidence = manifest.get("delivery_evidence_catalog")
    if not isinstance(delivery_evidence, list):
        failures.append("manifest:delivery_evidence_catalog_missing")
    else:
        expected_pairs = {
            ("runtime-module-metadata-survey-note", SURVEY_PATH),
            ("runtime-module-metadata-manifest", MANIFEST_PATH),
            ("runtime-module-metadata-survey-gate", SURVEY_TEST_PATH),
            ("runtime-module-metadata-packet-checker", CHECKER_PATH),
            ("phase9-build-gate", PHASE9_BUILD_PATH),
            ("phase9-tests-readme-guide", TESTS_README_PATH),
            ("shared-runtime-loader-contract", RUNTIME_LOADER_PATH),
            ("runtime-trace-events-loader-plan", TRACE_EVENTS_LOADER_PATH),
        }
        actual_pairs = {
            (entry.get("id"), entry.get("path"))
            for entry in delivery_evidence
            if isinstance(entry, dict)
        }
        if actual_pairs != expected_pairs:
            failures.append("manifest:delivery_evidence_catalog_drift")
    ownership_map = manifest.get("ownership_map")
    if not isinstance(ownership_map, list):
        failures.append("manifest:ownership_map_missing")
    else:
        required_surfaces = {
            SURVEY_PATH,
            MANIFEST_PATH,
            SURVEY_TEST_PATH,
            CHECKER_PATH,
            PHASE9_BUILD_PATH,
            TESTS_README_PATH,
            RUNTIME_LOADER_PATH,
            TRACE_EVENTS_LOADER_PATH,
        }
        actual_surfaces = {entry.get("surface") for entry in ownership_map if isinstance(entry, dict)}
        if actual_surfaces != required_surfaces:
            failures.append("manifest:ownership_map_drift")
    review_prompts = manifest.get("review_prompts")
    if review_prompts != EXPECTED_REVIEW_PROMPTS:
        failures.append("manifest:review_prompts_drift")
    return failures

def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []
    survey_text = read_text(root, SURVEY_PATH)
    survey_test_text = read_text(root, SURVEY_TEST_PATH)
    validate_phase9_text = read_text(root, VALIDATE_PHASE9_PATH)
    makefile_text = read_text(root, MAKEFILE_PATH)
    phase9_build_text = read_text(root, PHASE9_BUILD_PATH)
    runtime_loader_text = read_text(root, RUNTIME_LOADER_PATH)
    tests_readme_text = read_text(root, TESTS_README_PATH)
    atomic64_loader_text = read_text(root, ATOMIC64_LOADER_PATH)
    bitmap_loader_text = read_text(root, BITMAP_LOADER_PATH)
    kretprobe_loader_text = read_text(root, KRETPROBE_LOADER_PATH)
    trace_events_loader_text = read_text(root, TRACE_EVENTS_LOADER_PATH)
    failures: list[str] = []
    for marker in SURVEY_REQUIRED_MARKERS:
        if marker not in survey_text:
            failures.append(f"survey:{marker}")
    for marker in MODULE_METADATA_SURVEY_EXACT_ONCE_MARKERS:
        if count_exact_occurrence(survey_text, marker) != 1:
            failures.append(f"survey_exact:{marker}")
    for marker in VALIDATE_PHASE9_REQUIRED_MARKERS:
        if marker not in validate_phase9_text:
            failures.append(f"validate_phase9:{marker}")
    for marker in MAKEFILE_REQUIRED_MARKERS:
        if marker not in makefile_text:
            failures.append(f"makefile:{marker}")
    for marker in PHASE9_BUILD_REQUIRED_MARKERS:
        if marker not in phase9_build_text:
            failures.append(f"phase9_build:{marker}")
    for marker in SURVEY_TEST_REQUIRED_MARKERS:
        if marker not in survey_test_text:
            failures.append(f"survey_test:{marker}")
    for marker in RUNTIME_LOADER_REQUIRED_MARKERS:
        if marker not in runtime_loader_text:
            failures.append(f"runtime_loader:{marker}")
    for marker in ATOMIC64_LOADER_REQUIRED_MARKERS:
        if marker not in atomic64_loader_text:
            failures.append(f"atomic64_loader:{marker}")
    for marker in BITMAP_LOADER_REQUIRED_MARKERS:
        if marker not in bitmap_loader_text:
            failures.append(f"bitmap_loader:{marker}")
    for marker in KRETPROBE_LOADER_REQUIRED_MARKERS:
        if marker not in kretprobe_loader_text:
            failures.append(f"kretprobe_loader:{marker}")
    for marker in TRACE_EVENTS_LOADER_REQUIRED_MARKERS:
        if marker not in trace_events_loader_text:
            failures.append(f"trace_events_loader:{marker}")
    for marker in LOADER_PLAN_FORBIDDEN_MARKERS:
        if marker in atomic64_loader_text:
            failures.append(f"atomic64_loader_forbidden:{marker}")
        if marker in bitmap_loader_text:
            failures.append(f"bitmap_loader_forbidden:{marker}")
        if marker in kretprobe_loader_text:
            failures.append(f"kretprobe_loader_forbidden:{marker}")
        if marker in trace_events_loader_text:
            failures.append(f"trace_events_loader_forbidden:{marker}")
    for marker in TESTS_README_REQUIRED_MARKERS:
        if marker not in tests_readme_text:
            failures.append(f"tests_readme:{marker}")
    failures.extend(validate_manifest_packet(root))
    return [], failures

def write_fixture_tree(root: Path) -> None:
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
    (root / "scripts/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux/kernel").mkdir(parents=True, exist_ok=True)
    (root / "zigux").mkdir(parents=True, exist_ok=True)
    (root / "samples/zigux").mkdir(parents=True, exist_ok=True)
    commit = "949994db4046ec70abf044d1b2ea874fde9bc4a6"
    manifest = {
        "lane_key": "P9-L07",
        "phase": "Phase 9",
        "surveyed_commit": commit,
        "survey_summary": {
            "runtime_descriptor_count": 4,
            "runtime_loader_lane_count": 3,
            "runtime_loader_plan_count": 4,
            "runtime_sample_only_blocked_count": 0,
            "shared_metadata_field_count": 9,
            "depmod_gap_count": 8,
            "shared_runtime_loader_present": True,
            "runtime_trace_events_loader_present": True,
        },
        "runtime_loader_plans": [
            "samples/zigux/runtime_atomic64_loader.zig",
            "samples/zigux/runtime_bitmap_loader.zig",
            "samples/zigux/runtime_kretprobe_loader.zig",
            "samples/zigux/runtime_trace_events_loader.zig",
        ],
        "runtime_sample_only_blocked": [],
        "depmod_gap_surfaces": EXPECTED_DEPMOD_GAP_SURFACES,
        "delivery_evidence_catalog": [
            {"id": "runtime-module-metadata-survey-note", "path": SURVEY_PATH},
            {"id": "runtime-module-metadata-manifest", "path": MANIFEST_PATH},
            {"id": "runtime-module-metadata-survey-gate", "path": SURVEY_TEST_PATH},
            {"id": "runtime-module-metadata-packet-checker", "path": CHECKER_PATH},
            {"id": "phase9-build-gate", "path": PHASE9_BUILD_PATH},
            {"id": "phase9-tests-readme-guide", "path": TESTS_README_PATH},
            {"id": "shared-runtime-loader-contract", "path": RUNTIME_LOADER_PATH},
            {"id": "runtime-trace-events-loader-plan", "path": TRACE_EVENTS_LOADER_PATH},
        ],
        "ownership_map": [
            {"surface": SURVEY_PATH},
            {"surface": MANIFEST_PATH},
            {"surface": SURVEY_TEST_PATH},
            {"surface": CHECKER_PATH},
            {"surface": PHASE9_BUILD_PATH},
            {"surface": TESTS_README_PATH},
            {"surface": RUNTIME_LOADER_PATH},
            {"surface": TRACE_EVENTS_LOADER_PATH},
        ],
        "review_prompts": EXPECTED_REVIEW_PROMPTS,
    }
    (root / SURVEY_PATH).write_text("\n".join([
        "# Phase 9 Module Metadata and Depmod Bridge Survey",
        "",
        "- `PHASE9_SLICE=runtime-module-metadata-depmod-bridge-survey`",
        f"- `PHASE9_SURVEYED_COMMIT={commit}`",
        "ModuleDescriptor keeps requires_runtime_substrate and provides_selftest_hook explicit.",
        "RuntimeLoadRequest keeps module_name, command_name, entry_symbol, exit_symbol, handoff_stage, and allocator_handoff explicit.",
        "The current survey packet is pinned to `master` commit `949994db4046ec70abf044d1b2ea874fde9bc4a6`.",
        "the shared runtime loader currently exposes three tagged loader lanes: `atomic64`, `bitmap`, and `kretprobe`.",
        "four landed loader-plan files now stay at `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, and `samples/zigux/runtime_trace_events_loader.zig`.",
        "The dedicated `samples/zigux/runtime_trace_events_loader.zig` scaffold is now landed too, but it still stops outside that shared `RuntimeLoadRequest` union.",
        "The packet names MODULE_INFO(), MODULE_ALIAS(), .modinfo, modules.alias, modules.order, modules.builtin, Module.symvers, and scripts/depmod.sh directly.",
        "## Gates",
        "",
        "1. run the shared validator self-test plus the dedicated metadata checker self-test",
        "- `python3 scripts/zigux/validate-phase9.py --self-test`",
        "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`",
        "",
        "2. run the shared validator and the dedicated metadata checker",
        "- `python3 scripts/zigux/validate-phase9.py`",
        "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`",
        "",
        "3. run the shared Phase 9 runtime bundle",
        "- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`",
        "",
        "4. run the focused metadata survey replay",
        "- `zig test zigux/tests/runtime_module_metadata_survey.zig`",
        "- `make -C zigux phase9-module-metadata-survey`",
        "",
        "5. run the shared convenience target",
        "- `make -C zigux phase9-validate`",
        "",
    ]) + "\n", encoding='utf-8')
    (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding='utf-8')
    (root / SURVEY_TEST_PATH).write_text("\n".join([
        'test "runtime module metadata manifest keeps the dedicated descriptor and depmod-gap packet explicit" {',
        'test "runtime module metadata docs stay aligned with the manifest-backed surveyed commit" {',
        'test "runtime module metadata survey note keeps descriptor fields, shared loader metadata, and depmod gaps explicit" {',
        'test "runtime module metadata survey proves the landed loader-plan scaffolds stay explicit and the shared metadata boundary stays narrow" {',
        'test "runtime module metadata survey proves the live starter descriptors and shared loader metadata surface directly" {',
        'test "runtime module metadata survey keeps the shared phase9 validator route explicit" {',
        '"Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md"',
        '"zigux/tests/runtime_module_metadata_manifest.json"',
        '"zigux/kernel/runtime_loader.zig"',
        '"samples/zigux/runtime_atomic64_loader.zig"',
        '"samples/zigux/runtime_bitmap_loader.zig"',
        '"samples/zigux/runtime_kretprobe_loader.zig"',
        '"samples/zigux/runtime_trace_events_loader.zig"',
        '"samples/zigux/runtime_trace_events.zig"',
        '"scripts/zigux/check-phase9-module-metadata-packet.py"',
        '"scripts/zigux/validate-phase9.py"',
        '"zigux/tests/phase9_build.zig"',
        '"zigux/tests/README.md"',
        '"MODULE_INFO()"',
        '"MODULE_ALIAS()"',
        '"scripts/depmod.sh"',
        '"RuntimeLoadRequest"',
        'std.testing.expect(std.mem.indexOf(u8, runtime_trace_events_loader, "RuntimeLoadRequest") == null);',
        'try expectContainsAll(validate_phase9, &.{',
        '"Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md"',
        '"zigux/tests/runtime_module_metadata_manifest.json"',
        '"zigux/tests/runtime_module_metadata_survey.zig"',
        '"scripts/zigux/check-phase9-module-metadata-packet.py"',
        '"phase9-runtime-module-metadata-survey-tests"',
        'waitingOnRuntimeSubstrate',
        'releasedWithoutSubstrate',
        'register_kretprobe',
        'foo_bar_reg',
        'foo_bar_unreg',
        ''
    ]), encoding='utf-8')
    (root / CHECKER_PATH).write_text('self checker fixture marker\n', encoding='utf-8')
    (root / VALIDATE_PHASE9_PATH).write_text("\n".join(VALIDATE_PHASE9_REQUIRED_MARKERS) + "\n", encoding='utf-8')
    (root / MAKEFILE_PATH).write_text("\n".join([
        "PHONY += phase9-validate phase9-test phase9-loader-gap-survey phase9-loader-commit-alignment-survey phase9-non-owner-boundary-survey phase9-module-metadata-survey phase9-kretprobe-survey phase9-trace-events-survey phase9",
        "",
        "phase9-module-metadata-survey:",
        "\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_module_metadata_survey.zig",
    ]) + "\n", encoding='utf-8')
    (root / PHASE9_BUILD_PATH).write_text("\n".join(["runtime_module_metadata_survey.zig", "phase9-runtime-module-metadata-survey-tests", ""]) , encoding='utf-8')
    (root / RUNTIME_LOADER_PATH).write_text("\n".join([
        "pub const RuntimeLoadRequest = struct {",
        "    module_name: []const u8,",
        "    command_name: ?[]const u8,",
        "    entry_symbol: []const u8,",
        "    exit_symbol: []const u8,",
        "    handoff_stage: u8,",
        "    allocator_handoff: u8,",
        "};",
        "",
    ]), encoding='utf-8')
    (root / ATOMIC64_LOADER_PATH).write_text("\n".join([
        "pub const RuntimeAtomic64LoadPlan = struct {};",
        "pub fn toSharedRequest(plan: RuntimeAtomic64LoadPlan) runtime_loader.RuntimeLoadRequest {",
        '    _ = "zigux_runtime_atomic64_init";',
        '    _ = "zigux_runtime_atomic64_exit";',
        '    _ = "perf-runtime-atomic64";',
        "    return undefined.waitingOnRuntimeSubstrate().releasedWithoutSubstrate();",
        "}",
        "",
    ]), encoding='utf-8')
    (root / BITMAP_LOADER_PATH).write_text("\n".join([
        "pub const RuntimeBitmapLoadPlan = struct {};",
        "pub fn toSharedRequest(plan: RuntimeBitmapLoadPlan) runtime_loader.RuntimeLoadRequest {",
        '    _ = "zigux_runtime_bitmap_init";',
        '    _ = "zigux_runtime_bitmap_exit";',
        '    _ = "perf-runtime-bitmap";',
        "    return undefined.waitingOnRuntimeSubstrate().releasedWithoutSubstrate();",
        "}",
        "",
    ]), encoding='utf-8')
    (root / KRETPROBE_LOADER_PATH).write_text("\n".join([
        "pub const RuntimeKretprobeLoadPlan = struct {};",
        "pub fn toSharedRequest(plan: RuntimeKretprobeLoadPlan) runtime_loader.RuntimeLoadRequest {",
        '    _ = "register_kretprobe";',
        '    _ = "unregister_kretprobe";',
        '    _ = "zigux_runtime_kretprobe_init";',
        '    _ = "zigux_runtime_kretprobe_exit";',
        '    _ = "perf-runtime-kretprobe";',
        "    return undefined.waitingOnRuntimeSubstrate().releasedWithoutSubstrate();",
        "}",
        "",
    ]), encoding='utf-8')
    (root / TRACE_EVENTS_LOADER_PATH).write_text("\n".join([
        'const runtime_loader = @import("runtime_loader");',
        "pub const LoaderStage = runtime_loader.LoaderStage;",
        "pub const RuntimeTraceEventsLoadPlan = struct {",
        "    register_api: []const u8,",
        "    unregister_api: []const u8,",
        "    main_thread_label: []const u8,",
        "    function_thread_label: []const u8,",
        "};",
        'pub fn requestRuntimeLoad() void { _ = "waitingOnRuntimeSubstrate"; }',
        'pub fn releaseWithoutSubstrate() void { _ = "releasedWithoutSubstrate"; }',
        'const _entry = "zigux_runtime_trace_events_init";',
        'const _exit = "zigux_runtime_trace_events_exit";',
        'const _register = "foo_bar_reg";',
        'const _unregister = "foo_bar_unreg";',
        "",
    ]), encoding='utf-8')
    (root / TESTS_README_PATH).write_text("\n".join([
        "# zigux/tests",
        "",
        "- keep the current Phase 9 runtime bundle reviewable through `zigux/tests/phase9_build.zig`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_module_metadata_survey.zig`, `zigux/tests/runtime_module_metadata_manifest.json`, `scripts/zigux/validate-phase9.py`, `make -C zigux phase9-validate`, and the focused `make -C zigux phase9-trace-events-survey` replay instead of widening into ad hoc runtime-slice checks",
        "- keep the dedicated Phase 9 module-metadata packet explicit beside the loader-gap packet: `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`, `zigux/tests/runtime_module_metadata_manifest.json`, and `zigux/tests/runtime_module_metadata_survey.zig` should continue to record the starter-descriptor surface and absent depmod-facing metadata without implying `.modinfo`, `MODULE_ALIAS()`, or `scripts/depmod.sh` parity",
        "",
    ]), encoding='utf-8')

def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(f"phase9-module-metadata-selftest:{label}:unexpected_missing_files:{','.join(missing_files)}")
    if expected_marker not in missing_markers:
        actual = ','.join(missing_markers) if missing_markers else 'none'
        raise SystemExit(f"phase9-module-metadata-selftest:{label}:expected_missing_marker:{expected_marker}:actual:{actual}")

def expect_missing_file(label: str, root: Path, expected_file: str) -> None:
    missing_files, missing_markers = validate(root)
    if expected_file not in missing_files:
        actual_files = ','.join(missing_files) if missing_files else 'none'
        actual_markers = ','.join(missing_markers) if missing_markers else 'none'
        raise SystemExit(f"phase9-module-metadata-selftest:{label}:expected_missing_file:{expected_file}:actual_files:{actual_files}:actual_markers:{actual_markers}")

def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_module_metadata_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)
        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit("phase9-module-metadata-selftest:baseline_failed:" + f"files={','.join(missing_files) if missing_files else 'none'}:" + f"markers={','.join(missing_markers) if missing_markers else 'none'}")
        trace_events_loader_path = tmp_root / TRACE_EVENTS_LOADER_PATH
        original_trace_events_loader = trace_events_loader_path.read_text(encoding='utf-8')
        trace_events_loader_path.unlink()
        expect_missing_file('trace_events_loader_required_file', tmp_root, TRACE_EVENTS_LOADER_PATH)
        trace_events_loader_path.write_text(original_trace_events_loader, encoding='utf-8')
        survey_path = tmp_root / SURVEY_PATH
        original_survey = survey_path.read_text(encoding='utf-8')
        survey_path.write_text(original_survey.replace('MODULE_ALIAS()', '', 1), encoding='utf-8')
        expect_missing_marker('survey_depmod_surface', tmp_root, 'survey:MODULE_ALIAS()')
        survey_path.write_text(original_survey, encoding='utf-8')
        manifest_path = tmp_root / MANIFEST_PATH
        original_manifest = manifest_path.read_text(encoding='utf-8')
        manifest = json.loads(original_manifest)
        manifest['survey_summary']['depmod_gap_count'] = 7
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        expect_missing_marker('manifest_depmod_count', tmp_root, 'manifest:summary_depmod_gap_count_drift')
        manifest_path.write_text(original_manifest, encoding='utf-8')
        manifest = json.loads(original_manifest)
        manifest['delivery_evidence_catalog'] = manifest['delivery_evidence_catalog'][:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        expect_missing_marker('manifest_delivery_packet', tmp_root, 'manifest:delivery_evidence_catalog_drift')
        manifest_path.write_text(original_manifest, encoding='utf-8')
        manifest = json.loads(original_manifest)
        manifest['review_prompts'][2] = 'prompt drift'
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        expect_missing_marker('manifest_review_prompts', tmp_root, 'manifest:review_prompts_drift')
        manifest_path.write_text(original_manifest, encoding='utf-8')
        manifest = json.loads(original_manifest)
        manifest['runtime_loader_plans'][3] = 'samples/zigux/runtime_trace_events_loader_plan.zig'
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        expect_missing_marker('manifest_runtime_loader_plans', tmp_root, 'manifest:runtime_loader_plans_drift')
        manifest_path.write_text(original_manifest, encoding='utf-8')
        survey_test_path = tmp_root / SURVEY_TEST_PATH
        original_survey_test = survey_test_path.read_text(encoding='utf-8')
        survey_test_path.write_text(original_survey_test.replace('"samples/zigux/runtime_trace_events_loader.zig"', '', 1), encoding='utf-8')
        expect_missing_marker('survey_test_trace_events_loader_path', tmp_root, 'survey_test:"samples/zigux/runtime_trace_events_loader.zig"')
        survey_test_path.write_text(original_survey_test, encoding='utf-8')
        trace_events_loader_path.write_text(original_trace_events_loader.replace('"foo_bar_reg"', '', 1), encoding='utf-8')
        expect_missing_marker('trace_events_loader_register_label', tmp_root, 'trace_events_loader:"foo_bar_reg"')
        trace_events_loader_path.write_text(original_trace_events_loader, encoding='utf-8')
        validate_phase9_path = tmp_root / VALIDATE_PHASE9_PATH
        original_validate_phase9 = validate_phase9_path.read_text(encoding='utf-8')
        validate_phase9_path.write_text(original_validate_phase9.replace('Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md', 'Documentation/zigux/phase9-module-metadata-survey.md', 1), encoding='utf-8')
        expect_missing_marker('validate_phase9_module_metadata_survey_path', tmp_root, 'validate_phase9:Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md')
        validate_phase9_path.write_text(original_validate_phase9, encoding='utf-8')
        phase9_build_path = tmp_root / PHASE9_BUILD_PATH
        original_phase9_build = phase9_build_path.read_text(encoding='utf-8')
        phase9_build_path.write_text(original_phase9_build.replace('phase9-runtime-module-metadata-survey-tests', '', 1), encoding='utf-8')
        expect_missing_marker('phase9_build_module_metadata_step', tmp_root, 'phase9_build:phase9-runtime-module-metadata-survey-tests')
        phase9_build_path.write_text(original_phase9_build, encoding='utf-8')
        survey_path.write_text(original_survey.replace('- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`\n', '', 1), encoding='utf-8')
        expect_missing_marker('survey_checker_self_test_gate', tmp_root, 'survey:- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`')
        survey_path.write_text(original_survey, encoding='utf-8')
        survey_path.write_text(original_survey.replace('- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`\n', '- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`\n- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`\n', 1), encoding='utf-8')
        expect_missing_marker('survey_checker_duplicate_self_test_gate', tmp_root, 'survey_exact:- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`\n')
        survey_path.write_text(original_survey, encoding='utf-8')
        survey_path.write_text(original_survey.replace('- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`\n', '', 1), encoding='utf-8')
        expect_missing_marker('survey_checker_live_gate', tmp_root, 'survey:- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`')
        survey_path.write_text(original_survey, encoding='utf-8')
        survey_path.write_text(original_survey.replace('- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`\n', '- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`\n- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`\n', 1), encoding='utf-8')
        expect_missing_marker('survey_checker_duplicate_live_gate', tmp_root, 'survey_exact:- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`\n')
        survey_path.write_text(original_survey, encoding='utf-8')
        makefile_path = tmp_root / MAKEFILE_PATH
        original_makefile = makefile_path.read_text(encoding='utf-8')
        makefile_path.write_text(original_makefile.replace('phase9-loader-commit-alignment-survey ', '', 1), encoding='utf-8')
        expect_missing_marker('makefile_loader_commit_alignment_route', tmp_root, 'makefile:PHONY += phase9-validate phase9-test phase9-loader-gap-survey phase9-loader-commit-alignment-survey phase9-non-owner-boundary-survey phase9-module-metadata-survey phase9-kretprobe-survey phase9-trace-events-survey phase9')
        makefile_path.write_text(original_makefile, encoding='utf-8')
        makefile_path.write_text(original_makefile.replace('phase9-module-metadata-survey:\n', '', 1), encoding='utf-8')
        expect_missing_marker('makefile_metadata_target', tmp_root, 'makefile:phase9-module-metadata-survey:')
        makefile_path.write_text(original_makefile, encoding='utf-8')
        makefile_path.write_text(original_makefile.replace('\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_module_metadata_survey.zig\n', '', 1), encoding='utf-8')
        expect_missing_marker('makefile_metadata_command', tmp_root, 'makefile:\tcd $(ZIGUX_ROOT) && $(ZIG) test zigux/tests/runtime_module_metadata_survey.zig\n')
        makefile_path.write_text(original_makefile, encoding='utf-8')
        survey_path.write_text(original_survey.replace('- `make -C zigux phase9-module-metadata-survey`\n', '', 1), encoding='utf-8')
        expect_missing_marker('survey_make_target_gate', tmp_root, 'survey:- `make -C zigux phase9-module-metadata-survey`')
        survey_path.write_text(original_survey, encoding='utf-8')
        survey_path.write_text(original_survey.replace('- `make -C zigux phase9-module-metadata-survey`\n', '- `make -C zigux phase9-module-metadata-survey`\n- `make -C zigux phase9-module-metadata-survey`\n', 1), encoding='utf-8')
        expect_missing_marker('survey_duplicate_make_target_gate', tmp_root, 'survey_exact:- `make -C zigux phase9-module-metadata-survey`\n')
        survey_path.write_text(original_survey, encoding='utf-8')
        survey_path.write_text(original_survey.replace('- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`\n', '- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`\n- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`\n', 1), encoding='utf-8')
        expect_missing_marker('survey_duplicate_shared_build_gate', tmp_root, 'survey_exact:- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`\n')
        survey_path.write_text(original_survey, encoding='utf-8')
        survey_path.write_text(original_survey.replace('- `zig test zigux/tests/runtime_module_metadata_survey.zig`\n', '- `zig test zigux/tests/runtime_module_metadata_survey.zig`\n- `zig test zigux/tests/runtime_module_metadata_survey.zig`\n', 1), encoding='utf-8')
        expect_missing_marker('survey_duplicate_direct_zig_test_gate', tmp_root, 'survey_exact:- `zig test zigux/tests/runtime_module_metadata_survey.zig`\n')
        survey_path.write_text(original_survey, encoding='utf-8')
        tests_readme_path = tmp_root / TESTS_README_PATH
        original_tests_readme = tests_readme_path.read_text(encoding='utf-8')
        tests_readme_path.write_text(original_tests_readme.replace('keep the dedicated Phase 9 module-metadata packet explicit beside the loader-gap packet', 'keep the dedicated Phase 9 packet explicit beside the loader-gap packet', 1), encoding='utf-8')
        expect_missing_marker('tests_readme_packet_summary', tmp_root, 'tests_readme:keep the dedicated Phase 9 module-metadata packet explicit beside the loader-gap packet')
        tests_readme_path.write_text(original_tests_readme, encoding='utf-8')
        tests_readme_path.write_text(original_tests_readme.replace('`Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`', '`Documentation/zigux/phase9-module-metadata-survey.md`', 1), encoding='utf-8')
        expect_missing_marker('tests_readme_survey_note_path', tmp_root, 'tests_readme:`Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`')
        tests_readme_path.write_text(original_tests_readme, encoding='utf-8')
        tests_readme_path.write_text(original_tests_readme.replace('absent depmod-facing metadata without implying `.modinfo`, `MODULE_ALIAS()`, or `scripts/depmod.sh` parity', 'absent depmod-facing metadata without implying loadable-module parity', 1), encoding='utf-8')
        expect_missing_marker('tests_readme_depmod_parity_warning', tmp_root, 'tests_readme:absent depmod-facing metadata without implying `.modinfo`, `MODULE_ALIAS()`, or `scripts/depmod.sh` parity')
        tests_readme_path.write_text(original_tests_readme, encoding='utf-8')
    print('PHASE9_MODULE_METADATA_PACKET_SELF_TEST=pass')
    print('PHASE9_MODULE_METADATA_PACKET_SELF_TEST_CASE_COUNT=24')
    return 0

def main() -> int:
    parser = argparse.ArgumentParser(description='Validate the dedicated Phase 9 runtime module-metadata packet.')
    parser.add_argument('--root', type=Path, default=ROOT, help='Repository root to validate. Defaults to the current directory.')
    parser.add_argument('--self-test', action='store_true', help='Run the built-in module-metadata packet self-test.')
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    missing_files, missing_markers = validate(args.root)
    if missing_files:
        print('PHASE9_MODULE_METADATA_PACKET=fail')
        print('MISSING_PHASE9_MODULE_METADATA_PACKET_FILES_START')
        for item in missing_files:
            print(item)
        print('MISSING_PHASE9_MODULE_METADATA_PACKET_FILES_END')
        return 1
    if missing_markers:
        print('PHASE9_MODULE_METADATA_PACKET=fail')
        print('MISSING_PHASE9_MODULE_METADATA_PACKET_MARKERS_START')
        for marker in missing_markers:
            print(marker)
        print('MISSING_PHASE9_MODULE_METADATA_PACKET_MARKERS_END')
        return 1
    required_marker_count = (len(SURVEY_REQUIRED_MARKERS) + len(MODULE_METADATA_SURVEY_EXACT_ONCE_MARKERS) + len(VALIDATE_PHASE9_REQUIRED_MARKERS) + len(MAKEFILE_REQUIRED_MARKERS) + len(PHASE9_BUILD_REQUIRED_MARKERS) + len(SURVEY_TEST_REQUIRED_MARKERS) + len(RUNTIME_LOADER_REQUIRED_MARKERS) + len(ATOMIC64_LOADER_REQUIRED_MARKERS) + len(BITMAP_LOADER_REQUIRED_MARKERS) + len(KRETPROBE_LOADER_REQUIRED_MARKERS) + len(TRACE_EVENTS_LOADER_REQUIRED_MARKERS) + (len(LOADER_PLAN_FORBIDDEN_MARKERS) * 4) + len(TESTS_README_REQUIRED_MARKERS) + 8)
    print('PHASE9_MODULE_METADATA_PACKET=pass')
    print(f'PHASE9_MODULE_METADATA_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}')
    print('PHASE9_MODULE_METADATA_PACKET_REQUIRED_MARKER_COUNT=' f'{required_marker_count}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
