#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Documentation/zigux/freeze-map.md",
    "scripts/zigux/validate-phase9.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
    "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
    "Documentation/zigux/phase9-runtime-atomic64-survey.md",
    "Documentation/zigux/phase9-runtime-atomic64-module-slice.md",
    "Documentation/zigux/phase9-runtime-bitmap-survey.md",
    "Documentation/zigux/phase9-runtime-bitmap-module-slice.md",
    "Documentation/zigux/phase9-runtime-kretprobe-survey.md",
    "Documentation/zigux/phase9-runtime-trace-events-survey.md",
    "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
    "zigux/Makefile",
    "zigux/tests/README.md",
    "zigux/tests/phase9_build.zig",
    "zigux/tests/runtime_atomic64_manifest.json",
    "zigux/tests/runtime_atomic64_survey.zig",
    "zigux/tests/runtime_atomic64_module.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/runtime_bitmap_manifest.json",
    "zigux/tests/runtime_bitmap_survey.zig",
    "zigux/tests/runtime_bitmap_module.zig",
    "zigux/tests/runtime_bitmap_diff.zig",
    "Documentation/zigux/phase9-runtime-kretprobe-module-slice.md",
    "zigux/tests/runtime_kretprobe_manifest.json",
    "zigux/tests/runtime_kretprobe_survey.zig",
    "zigux/tests/runtime_kretprobe_module.zig",
    "zigux/tests/runtime_kretprobe_diff.zig",
    "zigux/tests/runtime_loader_gap_manifest.json",
    "zigux/tests/runtime_loader_gap_survey.zig",
    "zigux/tests/runtime_module_metadata_manifest.json",
    "zigux/tests/runtime_module_metadata_survey.zig",
    "zigux/tests/runtime_trace_events_manifest.json",
    "zigux/tests/runtime_trace_events_survey.zig",
    "zigux/tests/runtime_trace_events_module.zig",
    "zigux/tests/runtime_trace_events_diff.zig",
    "samples/zigux/runtime_atomic64.zig",
    "samples/zigux/runtime_atomic64_loader.zig",
    "samples/zigux/runtime_bitmap.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_kretprobe.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
    "samples/zigux/runtime_trace_events.zig",
    "zigux/kernel/runtime_loader.zig",
    "zigux/helpers/allocator_policy.zig",
    "scripts/zigux/check-phase9-module-metadata-packet.py",
    ".github/workflows/zigux-bootstrap.yml",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


def extract_markdown_surveyed_commit(text: str, label: str) -> tuple[str | None, str | None]:
    match = re.search(r"`PHASE9_SURVEYED_COMMIT=([0-9a-f]{40})`", text)
    if not match:
        return None, f"{label}:missing_or_invalid_surveyed_commit_marker"
    return match.group(1), None


def validate_doc_manifest_surveyed_commit_consistency(
    family: str,
    manifest_text: str,
    survey_text: str,
    module_slice_text: str,
    survey_label: str,
    module_label: str,
) -> list[str]:
    missing_markers: list[str] = []
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        return [f"{family}_consistency:manifest_json_decode_failed"]

    manifest_commit = manifest.get("surveyed_commit")
    if not isinstance(manifest_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", manifest_commit):
        missing_markers.append(f"{family}_consistency:manifest_invalid_surveyed_commit")
        return missing_markers

    survey_commit, survey_error = extract_markdown_surveyed_commit(
        survey_text,
        survey_label,
    )
    if survey_error:
        missing_markers.append(survey_error)
    elif survey_commit != manifest_commit:
        missing_markers.append(f"{family}_consistency:survey_doc_commit_mismatch")

    module_commit, module_error = extract_markdown_surveyed_commit(
        module_slice_text,
        module_label,
    )
    if module_error:
        missing_markers.append(module_error)
    elif module_commit != manifest_commit:
        missing_markers.append(f"{family}_consistency:module_slice_commit_mismatch")

    return missing_markers


def validate_atomic64_surveyed_commit_consistency(
    manifest_text: str,
    survey_text: str,
    module_slice_text: str,
) -> list[str]:
    return validate_doc_manifest_surveyed_commit_consistency(
        "atomic64",
        manifest_text,
        survey_text,
        module_slice_text,
        "atomic64_survey",
        "atomic64_module_slice",
    )


def validate_bitmap_surveyed_commit_consistency(
    manifest_text: str,
    survey_text: str,
    module_slice_text: str,
) -> list[str]:
    return validate_doc_manifest_surveyed_commit_consistency(
        "bitmap",
        manifest_text,
        survey_text,
        module_slice_text,
        "bitmap_survey",
        "bitmap_module_slice",
    )


def validate_module_metadata_manifest_surveyed_commit_consistency(
    manifest_text: str,
    survey_text: str,
) -> list[str]:
    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        return ["module_metadata_consistency:manifest_json_decode_failed"]

    manifest_commit = manifest.get("surveyed_commit")
    if not isinstance(manifest_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", manifest_commit):
        return ["module_metadata_consistency:manifest_invalid_surveyed_commit"]

    survey_commit, survey_error = extract_markdown_surveyed_commit(
        survey_text,
        "module_metadata_survey",
    )
    if survey_error:
        return [survey_error]
    if survey_commit != manifest_commit:
        return ["module_metadata_consistency:survey_doc_commit_mismatch"]
    return []

required_make_markers = [
    "PHONY += phase9-validate phase9-test phase9",
    "phase9-validate:",
    "scripts/zigux/validate-phase9.py --self-test",
    "scripts/zigux/validate-phase9.py",
    "phase9-test:",
    "zigux/tests/phase9_build.zig",
    "phase9: phase9-validate phase9-test",
]

required_workflow_markers = [
    "Self-test Phase 9 runtime validator",
    "python3 scripts/zigux/validate-phase9.py --self-test",
    "Validate Phase 9 runtime gates",
    "make -C zigux phase9-validate",
    "Run Phase 9 runtime helper tests",
    "zigux/tests/phase9_build.zig",
]

required_script_readme_markers = [
    "validate-phase9.py",
    "validate-phase9.py --self-test",
    "Phase 9 flow",
    "make -C zigux phase9-validate",
    "phase9_build.zig",
    "phase9-runtime-loader-gap-survey.md",
    "review-checklist.md",
    "manifest-backed catalog and ownership map",
    "selftest-hook markers",
    "bounded lifecycle-parity posture",
]

required_tests_readme_markers = [
    "zigux/tests/phase9_build.zig",
    "zigux/tests/runtime_loader_gap_survey.zig",
    "zigux/tests/runtime_loader_gap_manifest.json",
    "scripts/zigux/validate-phase9.py",
    "manifest-backed catalog and ownership map",
    "make -C zigux phase9-validate",
    "selftest-hook markers",
    "bounded lifecycle-parity posture",
    "Documentation/zigux/freeze-map.md",
    "`kernel/trace/ring_buffer.c`",
    "Study / Boundary Only",
]

required_doc_readme_markers = [
    "Phase 9 notes",
    "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
    "Documentation/zigux/review-checklist.md",
    "the `Documentation/zigux/phase9-runtime-trace-events-{survey,module-slice}.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` bundle now keeps the `Documentation/zigux/freeze-map.md` boundary explicit",
    "python3 scripts/zigux/validate-phase9.py --self-test",
    "python3 scripts/zigux/validate-phase9.py",
    "make -C zigux phase9-validate",
    "zigux/tests/phase9_build.zig",
    "manifest-backed catalog and ownership map",
    "selftest-hook markers",
    "bounded lifecycle-parity posture",
    "existing atomic64, bitmap, or kretprobe loader plans",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "rust/exports.c",
    "zigux/kernel/export_shim.zig",
    "Phase 2 or Phase 3 non-owner references",
    "Phase 9 runtime evidence",
]

required_freeze_map_markers = [
    "## Study / Boundary Only",
    "`kernel/trace/ring_buffer.c`",
    "Architecture Council decision",
]

required_review_checklist_markers = [
    "if the change is a Phase 9 runtime slice, do the module or sample note, the manifest-backed survey or loader-gap survey, and the shared `phase9_build.zig` entrypoint still agree on the same Linux anchor, bounded blocker posture, and replay scope?",
    "if the change is a Phase 9 runtime slice, do the shipped sample, manifest-backed survey, and shared `phase9_build.zig` evidence still keep the roadmap's selftest-hook markers and bounded lifecycle-parity posture explicit instead of implying a loadable module path that the runtime substrate does not support yet?",
    "if the change touches the shared Phase 9 runtime-loader evidence packet, does `zigux/tests/runtime_loader_gap_manifest.json` still keep the manifest-backed catalog and ownership map aligned with the survey note, review checklist, shared request contract, sample-side loader plans, and shared `phase9_build.zig` entrypoint in one reviewable ownership packet?",
    "if the change touches the shared Phase 9 runtime-loader evidence packet, do `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `rust/exports.c`, and `zigux/kernel/export_shim.zig` still stay explicit as Phase 2 or Phase 3 non-owner references instead of being silently counted as Phase 9 runtime evidence?",
    "if the change touches the shared Phase 9 runtime-loader evidence packet and its adjacent scheduler-facing boundary, does `Documentation/zigux/freeze-map.md` still stay in that same reviewable ownership packet so the study-only `kernel/workqueue.c` status and Architecture Council reopen rule remain explicit beside the survey note, review checklist, shared request contract, sample-side loader plans, and shared `phase9_build.zig` entrypoint?",
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
    "samples/zigux/runtime_atomic64_loader.zig",
    "Delivery ownership map",
    "manifest-backed catalog",
    "three sample-side loader plans",
    "atomic64 loader-plan projection",
    "bitmap loader-plan projection",
    "kretprobe loader-plan projection",
    "Phase 8",
    "Phase 9",
    "command or environment control surface",
    "shared `command_name` field",
    "tools/lib/subcmd/exec-cmd.zig",
    "tools/lib/subcmd/help.zig",
    "ExtractArgv0Result.command_name",
    "Config.exec_path_env",
    "PERF_EXEC_PATH",
    "PATH",
    "LINES",
    "COLUMNS",
    "argv policy",
    "environment-derived activation cues",
    "allocator-handoff contract",
    "pre-execution",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "rust/exports.c",
    "zigux/kernel/export_shim.zig",
    "boundary references instead of Phase 9 runtime evidence",
]

required_phase9_build_markers = [
    "runtime_loader_gap_survey.zig",
    "phase9-runtime-atomic64-sample-tests",
    "phase9-runtime-atomic64-module-tests",
    "phase9-runtime-atomic64-diff-tests",
    "phase9-runtime-atomic64-loader-tests",
    "phase9-runtime-atomic64-survey-tests",
    "phase9-runtime-bitmap-sample-tests",
    "phase9-runtime-bitmap-module-tests",
    "phase9-runtime-bitmap-diff-tests",
    "phase9-runtime-loader-gap-survey-tests",
    "phase9-runtime-bitmap-survey-tests",
    "phase9-runtime-loader-tests",
    "phase9-runtime-bitmap-loader-tests",
    "phase9-runtime-kretprobe-sample-tests",
    "phase9-runtime-kretprobe-module-tests",
    "phase9-runtime-kretprobe-diff-tests",
    "phase9-runtime-kretprobe-loader-tests",
    "phase9-runtime-kretprobe-survey-tests",
    "phase9-runtime-module-metadata-survey-tests",
    "phase9-runtime-trace-events-module-tests",
    "phase9-runtime-trace-events-sample-tests",
    "phase9-runtime-trace-events-diff-tests",
    "phase9-runtime-trace-events-survey-tests",
]

forbidden_phase9_build_markers = [
    "runtime_trace_events_loader",
    "phase9-runtime-trace-events-loader-tests",
]

required_loader_gap_survey_test_markers = [
    "runtime loader gap survey manifest keeps the roadmap boundary and shared request surface explicit",
    "runtime loader gap survey doc keeps the mixed roadmap phases and remaining control-surface gap explicit",
    "runtime loader gap survey keeps the review checklist runtime guardrails explicit",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/runtime_loader_gap_manifest.json",
    'try std.testing.expectEqualStrings("tools/lib/subcmd/exec-cmd.zig", manifest.phase8_command_environment_surfaces[0]);',
    'try std.testing.expectEqualStrings("tools/lib/subcmd/help.zig", manifest.phase8_command_environment_surfaces[1]);',
    'try std.testing.expectEqualStrings("tools/lib/subcmd/exec-cmd.zig", manifest.phase8_control_surface_markers.exec_cmd_surface);',
    'try std.testing.expectEqualStrings("tools/lib/subcmd/help.zig", manifest.phase8_control_surface_markers.help_surface);',
    'try std.testing.expectEqualStrings("ExtractArgv0Result.command_name", manifest.phase8_control_surface_markers.command_name_field);',
    'try std.testing.expectEqualStrings("Config.exec_path_env", manifest.phase8_control_surface_markers.exec_path_env_field);',
    'try std.testing.expectEqualStrings("shared command_name field", manifest.phase8_control_surface_markers.shared_runtime_loader_field);',
    'try std.testing.expectEqualStrings("PERF_EXEC_PATH", manifest.phase8_control_surface_markers.exec_env_names[0]);',
    'try std.testing.expectEqualStrings("PATH", manifest.phase8_control_surface_markers.exec_env_names[1]);',
    'try std.testing.expectEqualStrings("LINES", manifest.phase8_control_surface_markers.terminal_env_names[0]);',
    'try std.testing.expectEqualStrings("COLUMNS", manifest.phase8_control_surface_markers.terminal_env_names[1]);',
    'std.mem.indexOf(u8, survey_note, "three sample-side loader plans")',
    'std.mem.indexOf(u8, survey_note, "atomic64 loader-plan projection")',
    'std.mem.indexOf(u8, survey_note, "ExtractArgv0Result.command_name")',
    'std.mem.indexOf(u8, survey_note, "Config.exec_path_env")',
    'std.mem.indexOf(u8, survey_note, "PERF_EXEC_PATH")',
    'std.mem.indexOf(u8, survey_note, "PATH")',
    'std.mem.indexOf(u8, survey_note, "LINES")',
    'std.mem.indexOf(u8, survey_note, "COLUMNS")',
    'try std.testing.expectEqual(@as(usize, 4), manifest.non_owner_surfaces.len);',
    'try std.testing.expectEqualStrings("scripts/zigux/kconfig/conf_bridge.zig", manifest.non_owner_surfaces[0].surface);',
    'try std.testing.expectEqualStrings("scripts/zigux/kconfig/confdata_bridge.zig", manifest.non_owner_surfaces[1].surface);',
    'try std.testing.expectEqualStrings("rust/exports.c", manifest.non_owner_surfaces[2].surface);',
    'try std.testing.expectEqualStrings("zigux/kernel/export_shim.zig", manifest.non_owner_surfaces[3].surface);',
    'std.mem.indexOf(u8, survey_note, "scripts/zigux/kconfig/conf_bridge.zig")',
    'std.mem.indexOf(u8, survey_note, "scripts/zigux/kconfig/confdata_bridge.zig")',
    'std.mem.indexOf(u8, survey_note, "rust/exports.c")',
    'std.mem.indexOf(u8, survey_note, "zigux/kernel/export_shim.zig")',
    'std.mem.indexOf(u8, review_checklist, "scripts/zigux/kconfig/conf_bridge.zig")',
    'std.mem.indexOf(u8, review_checklist, "zigux/kernel/export_shim.zig")',
    'const absent_command_env_surface = [_][]const u8{',
    'try expectContainsNone(atomic64_loader, &absent_command_env_surface);',
    'try expectContainsNone(bitmap_loader, &absent_command_env_surface);',
    'try expectContainsNone(kretprobe_loader, &absent_command_env_surface);',
    'try expectContainsNone(runtime_loader_file, &absent_command_env_surface);',
    'try expectContainsNone(runtime_loader_file, &.{',
]

required_loader_gap_manifest_markers = [
    '"cross_phase_non_owner_surface_count": 4',
    '"non_owner_surfaces": [',
    '"surface": "scripts/zigux/kconfig/conf_bridge.zig"',
    '"surface": "scripts/zigux/kconfig/confdata_bridge.zig"',
    '"surface": "rust/exports.c"',
    '"surface": "zigux/kernel/export_shim.zig"',
    '"owning_phase": "Phase 2"',
    '"owning_phase": "Phase 3"',
    '"boundary_kind": "config_surface_bridge"',
    '"boundary_kind": "export_boundary"',
    '"why_non_owner": "The live Kconfig config-surface bridge stays in the Phase 2 config-surface bridge packet and is recorded here only as a boundary reference instead of Phase 9 runtime evidence."',
    '"why_non_owner": "The Zig export shim stays in the Phase 3 export-boundary packet and is recorded here only as a boundary reference instead of Phase 9 runtime evidence."',
    '"roadmap_command_environment_phase": "Phase 8"',
    '"phase8_command_environment_surface_count": 2',
    '"shared_command_environment_control_present": false',
    '"phase8_command_environment_surfaces": [',
    '"phase8_control_surface_markers": {',
    '"tools/lib/subcmd/exec-cmd.zig"',
    '"tools/lib/subcmd/help.zig"',
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
    '"shared_runtime_loader_field": "shared command_name field"',
    '"command_name_field": "ExtractArgv0Result.command_name"',
    '"exec_path_env_field": "Config.exec_path_env"',
    '"exec_env_names": [',
    '"PERF_EXEC_PATH"',
    '"PATH"',
    '"terminal_env_names": [',
    '"LINES"',
    '"COLUMNS"',
]

required_module_metadata_survey_markers = [
    "manifest-backed delivery catalog and ownership map",
    "`PHASE9_SURVEYED_COMMIT=",
    "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md",
    "zigux/tests/runtime_module_metadata_manifest.json",
    "zigux/tests/runtime_module_metadata_survey.zig",
    "scripts/zigux/check-phase9-module-metadata-packet.py",
    "RuntimeLoadRequest",
    "MODULE_INFO()",
    "scripts/depmod.sh",
    "phase9-module-metadata-survey",
]

required_module_metadata_manifest_markers = [
    '"lane_key": "P9-L07"',
    '"phase": "Phase 9"',
    '"surveyed_commit": "',
    '"path": "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md"',
    '"path": "zigux/tests/runtime_module_metadata_manifest.json"',
    '"path": "zigux/tests/runtime_module_metadata_survey.zig"',
    '"path": "scripts/zigux/check-phase9-module-metadata-packet.py"',
    '"path": "zigux/tests/phase9_build.zig"',
    '"path": "zigux/tests/README.md"',
    '"path": "zigux/kernel/runtime_loader.zig"',
    '"path": "samples/zigux/runtime_trace_events_loader.zig"',
]

required_module_metadata_survey_test_markers = [
    'test "runtime module metadata survey keeps the shared phase9 validator route explicit" {',
    '"Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md"',
    '"zigux/tests/runtime_module_metadata_manifest.json"',
    '"zigux/tests/runtime_module_metadata_survey.zig"',
    '"scripts/zigux/check-phase9-module-metadata-packet.py"',
    '"scripts/zigux/validate-phase9.py"',
    '"phase9-runtime-module-metadata-survey-tests"',
]

required_atomic64_survey_markers = [
    "manifest-backed delivery catalog and ownership map",
    "`PHASE9_SURVEYED_COMMIT=",
    "the current survey packet is pinned to `master` commit `",
    "Delivery ownership map",
    "zigux/tests/runtime_atomic64_manifest.json",
    "zigux/tests/runtime_atomic64_survey.zig",
    "zigux/tests/runtime_atomic64_module.zig",
    "zigux/tests/runtime_atomic64_diff.zig",
    "zigux/tests/phase9_build.zig",
    "samples/zigux/runtime_atomic64_loader.zig",
    "zigux/kernel/runtime_loader.zig",
    "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
    "blocked shared command-name, argv-policy, and environment-derived activation-control posture",
    "shared Phase 9 replay entrypoint",
]

required_atomic64_module_slice_markers = [
    "a direct post-selftest mutation replay proof that `selftest_complete` still permits bounded counter replay and keeps `RuntimeAtomic64Summary` explicit until exit",
    "the bounded guard-return trio from `lib/atomic64_test.c`: `add_unless`, `inc_not_zero`, and `dec_if_positive`",
    "a narrow differential gate under `zigux/tests/runtime_atomic64_diff.zig` for bounded add, sub, bitwise, swap, compare-swap, and guard-return expectations drawn from `lib/atomic64_test.c`",
    "a landed sample-side loader scaffold under `samples/zigux/runtime_atomic64_loader.zig` plus a shared runtime-loader request binding under `zigux/kernel/runtime_loader.zig`",
    "keep future work narrowly aimed at the remaining runtime substrate handoff or lifecycle-parity blocker",
]

required_atomic64_manifest_markers = [
    '"surveyed_commit": "',
    '"delivery_evidence_catalog": [',
    '"id": "runtime-atomic64-manifest"',
    '"path": "zigux/tests/runtime_atomic64_manifest.json"',
    '"id": "phase9-atomic64-build-gate"',
    '"path": "zigux/tests/phase9_build.zig"',
    '"id": "runtime-atomic64-loader-scaffold"',
    '"path": "samples/zigux/runtime_atomic64_loader.zig"',
    '"id": "runtime-loader-gap-note"',
    '"path": "Documentation/zigux/phase9-runtime-loader-gap-survey.md"',
    '"ownership_map": [',
    '"surface": "zigux/tests/runtime_atomic64_diff.zig"',
    '"surface": "samples/zigux/runtime_atomic64.zig"',
    '"surface": "Documentation/zigux/phase9-runtime-loader-gap-survey.md"',
]

required_atomic64_survey_test_markers = [
    'const DeliveryEvidence = struct {',
    'const OwnershipEntry = struct {',
    'fn expectSurveyedCommitMarker(document: []const u8, commit: []const u8) !void {',
    'fn expectPinnedCommitSentence(document: []const u8, commit: []const u8) !void {',
    'manifest.delivery_evidence_catalog.len',
    'manifest.ownership_map.len',
    'std.mem.eql(u8, entry.id, "runtime-atomic64-manifest")',
    'std.mem.eql(u8, entry.id, "phase9-atomic64-build-gate")',
    'std.mem.eql(u8, entry.id, "runtime-loader-gap-note")',
    'std.mem.eql(u8, entry.surface, "zigux/tests/runtime_atomic64_diff.zig")',
    'std.mem.eql(u8, entry.surface, "samples/zigux/runtime_atomic64.zig")',
    'std.mem.indexOf(u8, entry.role, "ownership map")',
    'std.mem.indexOf(u8, entry.owns, "argv-policy")',
    'expectSurveyedCommitMarker(survey_doc, manifest.surveyed_commit);',
    'expectPinnedCommitSentence(survey_doc, manifest.surveyed_commit);',
    'expectSurveyedCommitMarker(module_slice, manifest.surveyed_commit);',
]

required_bitmap_survey_markers = [
    "selftest-hook metadata",
    "phase9-runtime-bitmap-sample-tests",
    "phase9-runtime-bitmap-loader-tests",
    "command-name, argv-policy, and environment-derived activation handling",
    "the direct sample leg replays sparse `nthSetBit()` iteration across bits `10`, `20`, `30`, `40`, `50`, `60`, `80`, and `123`",
]

required_bitmap_module_slice_markers = [
    "adjacent loader scaffold plus shared loader-request binding",
    "zigux/kernel/runtime_loader.zig",
    "direct post-selftest mutation replay proof",
    "direct `phase9-runtime-bitmap-sample-tests` and `phase9-runtime-bitmap-loader-tests` legs",
    "shared runtime-loader request binding in `zigux/kernel/runtime_loader.zig`",
    "bounded two-word runtime bitmap backing store",
    "bounded parse-and-print replay",
]

required_bitmap_manifest_markers = [
    '"id": "runtime-bitmap-survey-gate"',
    '"zigux_destination": "zigux/tests/runtime_bitmap_survey.zig"',
    '"id": "runtime-bitmap-loader-scaffold"',
    '"zigux_destination": "samples/zigux/runtime_bitmap_loader.zig"',
    '"id": "runtime-bitmap-live-loader-binding"',
    '"zigux_destination": "zigux/kernel/runtime_loader.zig"',
    '"id": "runtime-bitmap-shared-phase9-build-gate"',
    '"zigux_destination": "zigux/tests/phase9_build.zig"',
    '"surface": "zigux/tests/runtime_bitmap_survey.zig"',
    '"surface": "samples/zigux/runtime_bitmap.zig"',
    '"surface": "samples/zigux/runtime_bitmap_loader.zig"',
    '"surface": "zigux/kernel/runtime_loader.zig"',
]

required_bitmap_survey_test_markers = [
    'test "runtime bitmap manifest keeps the direct sample, loader, and shared build packet aligned" {',
    'test "runtime bitmap survey note keeps the lifecycle and loader bridge explicit" {',
    'test "runtime bitmap sample and loader packet keep the runtime descriptor and bounded bitmap replay explicit" {',
    'test "runtime bitmap module gate keeps post-selftest replay and loader bridge expectations explicit" {',
    '"zigux/tests/runtime_bitmap_manifest.json"',
    '"Documentation/zigux/phase9-runtime-bitmap-survey.md"',
    '"Documentation/zigux/phase9-runtime-bitmap-module-slice.md"',
    '"samples/zigux/runtime_bitmap.zig"',
    '"samples/zigux/runtime_bitmap_loader.zig"',
    '"zigux/kernel/runtime_loader.zig"',
    '"phase9-runtime-bitmap-loader-tests"',
    '"phase9-runtime-bitmap-survey-tests"',
    '"bounded two-word runtime bitmap backing store"',
    '"nthSetBit()"',
]

KRETPROBE_LANE_KEY = "P9-L15"
KRETPROBE_SURVEYED_COMMIT = "9ab58640ce44fd53534dd49e29fcce6e274dc3d0"
TRACE_EVENTS_SURVEYED_COMMIT = "e7b3b515704dd521630df0b0f62396d033e38e02"
BITMAP_SURVEYED_COMMIT = "456151afa8a38a088e3cc582187b35fe5c7b0445"

required_kretprobe_survey_markers = [
    "manifest-backed delivery catalog and ownership map",
    "`PHASE9_SURVEYED_COMMIT=",
    "the current survey packet is pinned to `master` commit `",
    "Phase 5 sample packet",
    "Phase 9 runtime pilot",
    "runtime_kretprobe",
    "bounded lifecycle parity",
    "loader scaffold",
    "phase9-runtime-kretprobe-loader-tests",
]

required_kretprobe_manifest_markers = [
    '"surveyed_commit": "',
    '"delivery_evidence_catalog": [',
    '"id": "runtime-kretprobe-manifest"',
    '"path": "zigux/tests/runtime_kretprobe_manifest.json"',
    '"id": "runtime-kretprobe-survey-gate"',
    '"path": "zigux/tests/runtime_kretprobe_survey.zig"',
    '"id": "runtime-kretprobe-module-gate"',
    '"path": "zigux/tests/runtime_kretprobe_module.zig"',
    '"id": "runtime-kretprobe-diff-gate"',
    '"path": "zigux/tests/runtime_kretprobe_diff.zig"',
    '"id": "runtime-kretprobe-loader-scaffold"',
    '"path": "samples/zigux/runtime_kretprobe_loader.zig"',
]

required_kretprobe_survey_test_markers = [
    'test "runtime kretprobe manifest keeps the direct sample, runtime module, loader scaffold, and shared build packet aligned" {',
    'test "runtime kretprobe survey note keeps the roadmap and loader handoff posture explicit" {',
    'test "runtime kretprobe sample and runtime module packet keep the bounded lifecycle and replay surface explicit" {',
    'test "runtime kretprobe loader packet keeps the runtime substrate bridge and blocker posture explicit" {',
    '"zigux/tests/runtime_kretprobe_manifest.json"',
    '"Documentation/zigux/phase9-runtime-kretprobe-survey.md"',
    '"Documentation/zigux/phase9-runtime-kretprobe-module-slice.md"',
    '"samples/zigux/runtime_kretprobe.zig"',
    '"samples/zigux/runtime_kretprobe_loader.zig"',
    '"zigux/kernel/runtime_loader.zig"',
    '"phase9-runtime-kretprobe-loader-tests"',
    '"phase9-runtime-kretprobe-survey-tests"',
    '"register_kretprobe"',
    '"pre-execution"',
]

required_kretprobe_module_slice_markers = [
    "loader-side scaffold under `samples/zigux/runtime_kretprobe_loader.zig`",
    "shared runtime-loader request binding under `zigux/kernel/runtime_loader.zig`",
    "direct post-selftest mutation replay proof",
    "fixed `maxactive`",
    "`nmissed` replay",
]

required_trace_events_survey_markers = [
    "manifest-backed delivery catalog and ownership map",
    "`PHASE9_SURVEYED_COMMIT=",
    "the current survey packet is pinned to `master` commit `",
    "blocked loader scaffold",
    "`kernel/trace/ring_buffer.c`",
    "Study / Boundary Only",
    "Architecture Council decision",
    "phase9-runtime-trace-events-module-tests",
    "phase9-runtime-trace-events-survey-tests",
]

required_trace_events_module_slice_markers = [
    "direct module-facing replay under `zigux/tests/runtime_trace_events_module.zig`",
    "direct diff gate under `zigux/tests/runtime_trace_events_diff.zig`",
    "blocked loader scaffold under `samples/zigux/runtime_trace_events_loader.zig`",
    "study-only `kernel/trace/ring_buffer.c` boundary",
    "keep future work narrowly aimed at the remaining runtime substrate handoff or lifecycle-parity blocker",
]

required_trace_events_manifest_markers = [
    '"surveyed_commit": "',
    '"delivery_evidence_catalog": [',
    '"id": "runtime-trace-events-manifest"',
    '"path": "zigux/tests/runtime_trace_events_manifest.json"',
    '"id": "runtime-trace-events-survey-gate"',
    '"path": "zigux/tests/runtime_trace_events_survey.zig"',
    '"id": "runtime-trace-events-module-gate"',
    '"path": "zigux/tests/runtime_trace_events_module.zig"',
    '"id": "runtime-trace-events-diff-gate"',
    '"path": "zigux/tests/runtime_trace_events_diff.zig"',
    '"id": "freeze-map-note"',
    '"path": "Documentation/zigux/freeze-map.md"',
]

required_trace_events_survey_test_markers = [
    'test "runtime trace-events manifest keeps the direct sample, module, diff, and freeze-map packet aligned" {',
    'test "runtime trace-events survey note keeps the trace-core boundary and shared build packet explicit" {',
    'test "runtime trace-events sample and module packet keep the bounded lifecycle and callback replay explicit" {',
    'test "runtime trace-events diff packet keeps the post-selftest drift gate explicit" {',
    '"zigux/tests/runtime_trace_events_manifest.json"',
    '"Documentation/zigux/phase9-runtime-trace-events-survey.md"',
    '"Documentation/zigux/phase9-runtime-trace-events-module-slice.md"',
    '"samples/zigux/runtime_trace_events.zig"',
    '"zigux/tests/runtime_trace_events_module.zig"',
    '"zigux/tests/runtime_trace_events_diff.zig"',
    '"phase9-runtime-trace-events-module-tests"',
    '"phase9-runtime-trace-events-survey-tests"',
    '"kernel/trace/ring_buffer.c"',
    '"Architecture Council decision"',
]

required_trace_events_sample_markers = [
    'pub const ModuleDescriptor = struct',
    '.name = "runtime_trace_events"',
    '.anchor = "samples/trace_events/trace-events-sample.c"',
    '.requires_runtime_substrate = true',
    '.provides_selftest_hook = true',
    'pub const ModuleStage = enum',
    'pub const RuntimeTraceEventsSummary = struct',
    'pub fn runSelftest(self: *RuntimeTraceEventsSample) !RuntimeTraceEventsSummary',
    'pub fn emitMainIteration(self: *RuntimeTraceEventsSample, count: i32) !usize',
    'pub fn emitFunctionIteration(self: *RuntimeTraceEventsSample, count: i32) !usize',
]

required_trace_events_module_markers = [
    'test "runtime trace-events sample advertises the bounded pilot-module contract" {',
    'test "runtime trace-events sample keeps gated main-thread replay and lifecycle state honest" {',
    'test "runtime trace-events sample keeps replay-summary continuity explicit after selftest completion" {',
    'test "runtime trace-events sample keeps registration balance and failed-exit rollback explicit" {',
    'test "runtime trace-events module gate keeps selftest-ready failed-exit rollback explicit" {',
    'try std.testing.expectEqual(@as(usize, 1), initialized_summary.init_runs);',
    'try std.testing.expectEqual(@as(usize, 1), selftest_summary.selftest_runs);',
    'try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);',
    'test "runtime trace-events sample keeps registration balance explicit" {',
]


def required_marker_count() -> int:
    return (
        len(required_make_markers)
        + len(required_workflow_markers)
        + len(required_script_readme_markers)
        + len(required_tests_readme_markers)
        + len(required_doc_readme_markers)
        + len(required_freeze_map_markers)
        + len(required_review_checklist_markers)
        + len(required_loader_gap_survey_markers)
        + len(required_phase9_build_markers)
        + len(forbidden_phase9_build_markers)
        + len(required_loader_gap_survey_test_markers)
        + len(required_loader_gap_manifest_markers)
        + len(required_module_metadata_survey_markers)
        + len(required_module_metadata_manifest_markers)
        + len(required_module_metadata_survey_test_markers)
        + 1
        + len(required_atomic64_survey_markers)
        + len(required_atomic64_module_slice_markers)
        + len(required_atomic64_manifest_markers)
        + len(required_atomic64_survey_test_markers)
        + len(required_bitmap_survey_markers)
        + len(required_bitmap_module_slice_markers)
        + len(required_bitmap_manifest_markers)
        + len(required_bitmap_survey_test_markers)
        + len(required_kretprobe_survey_markers)
        + len(required_kretprobe_manifest_markers)
        + len(required_kretprobe_survey_test_markers)
        + 2
        + len(required_trace_events_survey_markers)
        + len(required_trace_events_module_slice_markers)
        + len(required_trace_events_manifest_markers)
        + len(required_trace_events_survey_test_markers)
        + len(required_trace_events_sample_markers)
        + len(required_trace_events_module_markers)
    )


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []

    makefile = read_text(root, "zigux/Makefile")
    workflow = read_text(root, ".github/workflows/zigux-bootstrap.yml")
    freeze_map = read_text(root, "Documentation/zigux/freeze-map.md")
    script_readme = read_text(root, "scripts/zigux/README.md")
    tests_readme = read_text(root, "zigux/tests/README.md")
    doc_readme = read_text(root, "Documentation/zigux/README.md")
    review_checklist = read_text(root, "Documentation/zigux/review-checklist.md")
    loader_gap_survey = read_text(root, "Documentation/zigux/phase9-runtime-loader-gap-survey.md")
    module_metadata_survey = read_text(root, "Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md")
    module_metadata_manifest = read_text(root, "zigux/tests/runtime_module_metadata_manifest.json")
    module_metadata_survey_test = read_text(root, "zigux/tests/runtime_module_metadata_survey.zig")
    atomic64_survey = read_text(root, "Documentation/zigux/phase9-runtime-atomic64-survey.md")
    atomic64_module_slice = read_text(root, "Documentation/zigux/phase9-runtime-atomic64-module-slice.md")
    bitmap_survey = read_text(root, "Documentation/zigux/phase9-runtime-bitmap-survey.md")
    bitmap_module_slice = read_text(root, "Documentation/zigux/phase9-runtime-bitmap-module-slice.md")
    kretprobe_survey = read_text(root, "Documentation/zigux/phase9-runtime-kretprobe-survey.md")
    bitmap_manifest = read_text(root, "zigux/tests/runtime_bitmap_manifest.json")
    bitmap_survey_test = read_text(root, "zigux/tests/runtime_bitmap_survey.zig")
    kretprobe_module_slice = read_text(root, "Documentation/zigux/phase9-runtime-kretprobe-module-slice.md")
    kretprobe_manifest = read_text(root, "zigux/tests/runtime_kretprobe_manifest.json")
    kretprobe_survey_test = read_text(root, "zigux/tests/runtime_kretprobe_survey.zig")
    trace_events_survey = read_text(root, "Documentation/zigux/phase9-runtime-trace-events-survey.md")
    trace_events_module_slice = read_text(root, "Documentation/zigux/phase9-runtime-trace-events-module-slice.md")
    phase9_build = read_text(root, "zigux/tests/phase9_build.zig")
    atomic64_manifest = read_text(root, "zigux/tests/runtime_atomic64_manifest.json")
    atomic64_survey_test = read_text(root, "zigux/tests/runtime_atomic64_survey.zig")
    loader_gap_survey_test = read_text(root, "zigux/tests/runtime_loader_gap_survey.zig")
    loader_gap_manifest = read_text(root, "zigux/tests/runtime_loader_gap_manifest.json")
    trace_events_manifest = read_text(root, "zigux/tests/runtime_trace_events_manifest.json")
    trace_events_survey_test = read_text(root, "zigux/tests/runtime_trace_events_survey.zig")
    trace_events_sample = read_text(root, "samples/zigux/runtime_trace_events.zig")
    trace_events_module = read_text(root, "zigux/tests/runtime_trace_events_module.zig")

    missing_markers: list[str] = []

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
    for marker in forbidden_phase9_build_markers:
        if marker in phase9_build:
            missing_markers.append(f"phase9_build_forbidden:{marker}")
    for marker in required_loader_gap_survey_test_markers:
        if marker not in loader_gap_survey_test:
            missing_markers.append(f"loader_gap_survey_test:{marker}")
    for marker in required_loader_gap_manifest_markers:
        if marker not in loader_gap_manifest:
            missing_markers.append(f"loader_gap_manifest:{marker}")
    for marker in required_module_metadata_survey_markers:
        if marker not in module_metadata_survey:
            missing_markers.append(f"module_metadata_survey:{marker}")
    for marker in required_module_metadata_manifest_markers:
        if marker not in module_metadata_manifest:
            missing_markers.append(f"module_metadata_manifest:{marker}")
    for marker in required_module_metadata_survey_test_markers:
        if marker not in module_metadata_survey_test:
            missing_markers.append(f"module_metadata_survey_test:{marker}")
    missing_markers.extend(
        validate_module_metadata_manifest_surveyed_commit_consistency(
            module_metadata_manifest,
            module_metadata_survey,
        )
    )
    for marker in required_atomic64_survey_markers:
        if marker not in atomic64_survey:
            missing_markers.append(f"atomic64_survey:{marker}")
    for marker in required_atomic64_module_slice_markers:
        if marker not in atomic64_module_slice:
            missing_markers.append(f"atomic64_module_slice:{marker}")
    for marker in required_atomic64_manifest_markers:
        if marker not in atomic64_manifest:
            missing_markers.append(f"atomic64_manifest:{marker}")
    for marker in required_atomic64_survey_test_markers:
        if marker not in atomic64_survey_test:
            missing_markers.append(f"atomic64_survey_test:{marker}")
    missing_markers.extend(
        validate_atomic64_surveyed_commit_consistency(
            atomic64_manifest,
            atomic64_survey,
            atomic64_module_slice,
        )
    )
    for marker in required_bitmap_survey_markers:
        if marker not in bitmap_survey:
            missing_markers.append(f"bitmap_survey:{marker}")
    for marker in required_bitmap_module_slice_markers:
        if marker not in bitmap_module_slice:
            missing_markers.append(f"bitmap_module_slice:{marker}")
    for marker in required_bitmap_manifest_markers:
        if marker not in bitmap_manifest:
            missing_markers.append(f"bitmap_manifest:{marker}")
    for marker in required_bitmap_survey_test_markers:
        if marker not in bitmap_survey_test:
            missing_markers.append(f"bitmap_survey_test:{marker}")
    missing_markers.extend(
        validate_bitmap_surveyed_commit_consistency(
            bitmap_manifest,
            bitmap_survey,
            bitmap_module_slice,
        )
    )
    for marker in required_kretprobe_survey_markers:
        if marker not in kretprobe_survey:
            missing_markers.append(f"kretprobe_survey:{marker}")
    for marker in required_kretprobe_manifest_markers:
        if marker not in kretprobe_manifest:
            missing_markers.append(f"kretprobe_manifest:{marker}")
    for marker in required_kretprobe_survey_test_markers:
        if marker not in kretprobe_survey_test:
            missing_markers.append(f"kretprobe_survey_test:{marker}")
    for marker in required_kretprobe_module_slice_markers:
        if marker not in kretprobe_module_slice:
            missing_markers.append(f"kretprobe_module_slice:{marker}")
    missing_markers.extend(
        validate_doc_manifest_surveyed_commit_consistency(
            "kretprobe",
            kretprobe_manifest,
            kretprobe_survey,
            kretprobe_module_slice,
            "kretprobe_survey",
            "kretprobe_module_slice",
        )
    )
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
    for marker in required_trace_events_sample_markers:
        if marker not in trace_events_sample:
            missing_markers.append(f"trace_events_sample:{marker}")
    for marker in required_trace_events_module_markers:
        if marker not in trace_events_module:
            missing_markers.append(f"trace_events_module:{marker}")
    missing_markers.extend(
        validate_doc_manifest_surveyed_commit_consistency(
            "trace_events",
            trace_events_manifest,
            trace_events_survey,
            trace_events_module_slice,
            "trace_events_survey",
            "trace_events_module_slice",
        )
    )
    return [], missing_markers


def clone_fixture_root(destination_root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        source = ROOT / rel_path
        target = destination_root / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase9-self-test:{label}:unexpected_missing_files:{','.join(missing_files)}"
        )
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase9-self-test:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_selftest_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        clone_fixture_root(tmp_root)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase9-self-test:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        makefile_path = tmp_root / "zigux/Makefile"
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/validate-phase9.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_self_test_hook",
            tmp_root,
            "make:scripts/zigux/validate-phase9.py --self-test",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        module_metadata_survey_test_path = tmp_root / "zigux/tests/runtime_module_metadata_survey.zig"
        original_module_metadata_survey_test = module_metadata_survey_test_path.read_text(encoding="utf-8")
        module_metadata_survey_test_path.write_text(
            original_module_metadata_survey_test.replace(
                '"scripts/zigux/validate-phase9.py"',
                '"scripts/zigux/phase9-validator.py"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "module_metadata_survey_test_shared_validator_route",
            tmp_root,
            'module_metadata_survey_test:"scripts/zigux/validate-phase9.py"',
        )
        module_metadata_survey_test_path.write_text(original_module_metadata_survey_test, encoding="utf-8")

        module_metadata_manifest_path = tmp_root / "zigux/tests/runtime_module_metadata_manifest.json"
        original_module_metadata_manifest = module_metadata_manifest_path.read_text(encoding="utf-8")
        module_metadata_manifest_path.write_text(
            original_module_metadata_manifest.replace(
                '"surveyed_commit": "949994db4046ec70abf044d1b2ea874fde9bc4a6"',
                '"surveyed_commit": "0000000000000000000000000000000000000000"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "module_metadata_manifest_surveyed_commit_consistency",
            tmp_root,
            "module_metadata_consistency:survey_doc_commit_mismatch",
        )
        module_metadata_manifest_path.write_text(original_module_metadata_manifest, encoding="utf-8")

        trace_events_survey_path = tmp_root / "Documentation/zigux/phase9-runtime-trace-events-survey.md"
        original_trace_events_survey = trace_events_survey_path.read_text(encoding="utf-8")
        trace_events_survey_path.write_text(
            original_trace_events_survey.replace(
                f"`PHASE9_SURVEYED_COMMIT={TRACE_EVENTS_SURVEYED_COMMIT}`",
                "`PHASE9_SURVEYED_COMMIT=`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "trace_events_surveyed_commit_pin",
            tmp_root,
            f"trace_events_survey:`PHASE9_SURVEYED_COMMIT={TRACE_EVENTS_SURVEYED_COMMIT}`",
        )
        trace_events_survey_path.write_text(original_trace_events_survey, encoding="utf-8")

        trace_events_sample_path = tmp_root / "samples/zigux/runtime_trace_events.zig"
        original_trace_events_sample = trace_events_sample_path.read_text(encoding="utf-8")
        trace_events_sample_path.write_text(
            original_trace_events_sample.replace(
                "        self.selftest_runs += 1;\n",
                "",
                1,
            ),
            encoding="utf-8")
        expect_missing_marker(
            "trace_events_sample_selftest_counter",
            tmp_root,
            "trace_events_sample:self.selftest_runs += 1;",
        )
        trace_events_sample_path.write_text(original_trace_events_sample, encoding="utf-8")

        trace_events_module_path = tmp_root / "zigux/tests/runtime_trace_events_module.zig"
        original_trace_events_module = trace_events_module_path.read_text(encoding="utf-8")
        trace_events_module_path.write_text(
            original_trace_events_module.replace(
                '    try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "trace_events_module_exit_counter_assert",
            tmp_root,
            "trace_events_module:try std.testing.expectEqual(@as(usize, 1), exited_summary.exit_runs);",
        )
        trace_events_module_path.write_text(original_trace_events_module, encoding="utf-8")

        kretprobe_survey_test_path = tmp_root / "zigux/tests/runtime_kretprobe_survey.zig"
        original_kretprobe_survey_test = kretprobe_survey_test_path.read_text(encoding="utf-8")
        kretprobe_survey_test_path.write_text(
            original_kretprobe_survey_test.replace(
                '            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "pre-execution") != null);\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "kretprobe_loader_rollback_surface",
            tmp_root,
            'kretprobe_survey_test:std.mem.indexOf(u8, gap.why_now, "pre-execution")',
        )
        kretprobe_survey_test_path.write_text(original_kretprobe_survey_test, encoding="utf-8")

        kretprobe_module_slice_path = tmp_root / "Documentation/zigux/phase9-runtime-kretprobe-module-slice.md"
        original_kretprobe_module_slice = kretprobe_module_slice_path.read_text(encoding="utf-8")
        kretprobe_module_slice_path.write_text(
            original_kretprobe_module_slice.replace(
                f"`PHASE9_SURVEYED_COMMIT={KRETPROBE_SURVEYED_COMMIT}`",
                "`PHASE9_SURVEYED_COMMIT=`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "kretprobe_module_slice_surveyed_commit_pin",
            tmp_root,
            f"kretprobe_module_slice:`PHASE9_SURVEYED_COMMIT={KRETPROBE_SURVEYED_COMMIT}`",
        )
        kretprobe_module_slice_path.write_text(original_kretprobe_module_slice, encoding="utf-8")

        kretprobe_manifest_path = tmp_root / "zigux/tests/runtime_kretprobe_manifest.json"
        original_kretprobe_manifest = kretprobe_manifest_path.read_text(encoding="utf-8")
        kretprobe_manifest_path.write_text(
            original_kretprobe_manifest.replace(
                f'"surveyed_commit": "{KRETPROBE_SURVEYED_COMMIT}"',
                '"surveyed_commit": "0000000000000000000000000000000000000000"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "kretprobe_manifest_surveyed_commit_consistency",
            tmp_root,
            "kretprobe_consistency:survey_doc_commit_mismatch",
        )
        kretprobe_manifest_path.write_text(original_kretprobe_manifest, encoding="utf-8")

        bitmap_manifest_path = tmp_root / "zigux/tests/runtime_bitmap_manifest.json"
        original_bitmap_manifest = bitmap_manifest_path.read_text(encoding="utf-8")
        bitmap_manifest_path.write_text(
            original_bitmap_manifest.replace(
                f'"surveyed_commit": "{BITMAP_SURVEYED_COMMIT}"',
                '"surveyed_commit": "2222222222222222222222222222222222222222"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "bitmap_manifest_surveyed_commit_consistency",
            tmp_root,
            "bitmap_consistency:survey_doc_commit_mismatch",
        )
        bitmap_manifest_path.write_text(original_bitmap_manifest, encoding="utf-8")

        bitmap_module_slice_path = tmp_root / "Documentation/zigux/phase9-runtime-bitmap-module-slice.md"
        original_bitmap_module_slice = bitmap_module_slice_path.read_text(encoding="utf-8")
        bitmap_module_slice_path.write_text(
            original_bitmap_module_slice.replace(
                f"`PHASE9_SURVEYED_COMMIT={BITMAP_SURVEYED_COMMIT}`",
                "`PHASE9_SURVEYED_COMMIT=`",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "bitmap_module_slice_surveyed_commit_pin",
            tmp_root,
            "bitmap_module_slice:missing_or_invalid_surveyed_commit_marker",
        )
        bitmap_module_slice_path.write_text(original_bitmap_module_slice, encoding="utf-8")

        loader_gap_survey_test_path = tmp_root / "zigux/tests/runtime_loader_gap_survey.zig"
        original_loader_gap_survey_test = loader_gap_survey_test_path.read_text(encoding="utf-8")
        loader_gap_survey_test_path.write_text(
            original_loader_gap_survey_test.replace(
                '    try expectContainsNone(runtime_loader_file, &absent_command_env_surface);\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "loader_gap_absent_command_env_guard",
            tmp_root,
            "loader_gap_survey_test:try expectContainsNone(runtime_loader_file, &absent_command_env_surface);",
        )
        loader_gap_survey_test_path.write_text(original_loader_gap_survey_test, encoding="utf-8")

        review_checklist_path = tmp_root / "Documentation/zigux/review-checklist.md"
        original_review_checklist = review_checklist_path.read_text(encoding="utf-8")
        review_checklist_path.write_text(
            original_review_checklist.replace(
                "if the change touches the shared Phase 9 runtime-loader evidence packet, do `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `rust/exports.c`, and `zigux/kernel/export_shim.zig` still stay explicit as Phase 2 or Phase 3 non-owner references instead of being silently counted as Phase 9 runtime evidence?\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "loader_gap_review_checklist_non_owner_boundary",
            tmp_root,
            "review_checklist:if the change touches the shared Phase 9 runtime-loader evidence packet, do `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, `rust/exports.c`, and `zigux/kernel/export_shim.zig` still stay explicit as Phase 2 or Phase 3 non-owner references instead of being silently counted as Phase 9 runtime evidence?",
        )
        review_checklist_path.write_text(original_review_checklist, encoding="utf-8")

        trace_events_manifest_path = tmp_root / "zigux/tests/runtime_trace_events_manifest.json"
        original_trace_events_manifest = trace_events_manifest_path.read_text(encoding="utf-8")
        trace_events_manifest_path.write_text(
            original_trace_events_manifest.replace(
                f'"surveyed_commit": "{TRACE_EVENTS_SURVEYED_COMMIT}"',
                '"surveyed_commit": "1111111111111111111111111111111111111111"',
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "trace_events_manifest_surveyed_commit_consistency",
            tmp_root,
            "trace_events_consistency:survey_doc_commit_mismatch",
        )
        trace_events_manifest_path.write_text(original_trace_events_manifest, encoding="utf-8")

    print("PHASE9_VALIDATOR_SELF_TEST=pass")
    print("PHASE9_VALIDATOR_SELF_TEST_CASE_COUNT=15")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the shared Phase 9 runtime pilot review packet."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in validator drift checks against a temporary Phase 9 fixture tree.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(ROOT)
    if missing_files:
        print("PHASE9_VALIDATION=fail")
        print("MISSING_PHASE9_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE9_FILES_END")
        return 1
    if missing_markers:
        print("PHASE9_VALIDATION=fail")
        print("MISSING_PHASE9_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE9_MARKERS_END")
        return 1

    print("PHASE9_VALIDATION=pass")
    print(f"PHASE9_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE9_REQUIRED_MARKER_COUNT={required_marker_count()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
