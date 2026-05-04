#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import tempfile


_SELF_PATH = Path(__file__).resolve()
ROOT = _SELF_PATH.parents[2] if len(_SELF_PATH.parents) > 2 else _SELF_PATH.parent

SURVEY_PATH = "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
SUBSTRATE_PLAN_PATH = "Documentation/zigux/phase9-runtime-loader-substrate-plan.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
SAMPLES_README_PATH = "samples/zigux/README.md"
MAKEFILE_PATH = "zigux/Makefile"
MANIFEST_PATH = "zigux/tests/runtime_loader_gap_manifest.json"
RUNTIME_LOADER_PATH = "zigux/kernel/runtime_loader.zig"
ALLOCATOR_POLICY_PATH = "zigux/helpers/allocator_policy.zig"
ATOMIC64_LOADER_PATH = "samples/zigux/runtime_atomic64_loader.zig"
BITMAP_LOADER_PATH = "samples/zigux/runtime_bitmap_loader.zig"
KRETPROBE_LOADER_PATH = "samples/zigux/runtime_kretprobe_loader.zig"
TRACE_EVENTS_LOADER_PATH = "samples/zigux/runtime_trace_events_loader.zig"

REQUIRED_FILES = [
    SURVEY_PATH,
    SUBSTRATE_PLAN_PATH,
    REVIEW_CHECKLIST_PATH,
    SAMPLES_README_PATH,
    MAKEFILE_PATH,
    MANIFEST_PATH,
    RUNTIME_LOADER_PATH,
    ALLOCATOR_POLICY_PATH,
    ATOMIC64_LOADER_PATH,
    BITMAP_LOADER_PATH,
    KRETPROBE_LOADER_PATH,
    TRACE_EVENTS_LOADER_PATH,
]

SURVEY_REQUIRED_MARKERS = [
    "Documentation/zigux/phase9-runtime-loader-substrate-plan.md",
    "shared loader-stage vocabulary",
    "The shared substrate plan is part of the same delivery packet now.",
    "- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test`",
    "- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py`",
]

SUBSTRATE_PLAN_REQUIRED_MARKERS = [
    "`PHASE9_SLICE=shared-runtime-loader-substrate-plan`",
    "PHASE9_SURVEYED_COMMIT=",
    "zigux/kernel/runtime_loader.zig",
    "samples/zigux/runtime_atomic64_loader.zig",
    "samples/zigux/runtime_bitmap_loader.zig",
    "samples/zigux/runtime_kretprobe_loader.zig",
    "zigux/helpers/allocator_policy.zig",
    "waiting_on_runtime_substrate",
    "released_without_substrate",
    "shared loader-stage vocabulary",
    "shared `command_name` handoff field",
    "samples/zigux/runtime_trace_events.zig",
    "`kernel/trace/ring_buffer.c`",
    "Study / Boundary Only",
]

REVIEW_CHECKLIST_REQUIRED_MARKERS = [
    "if the change touches the shared Phase 9 runtime-loader evidence packet, does `Documentation/zigux/phase9-runtime-loader-substrate-plan.md` still stay aligned with `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/kernel/runtime_loader.zig`, and the atomic64, bitmap, and kretprobe loader plans so the shared loader-stage vocabulary plus the without-substrate fallback remain reviewable in one place?",
]

SAMPLES_README_REQUIRED_MARKERS = [
    "Later runtime starters, loader-side follow-ons, and blocked pilots",
    "- `samples/zigux/runtime_bitmap.zig`",
    "- `samples/zigux/runtime_bitmap_loader.zig`",
    "- `samples/zigux/runtime_trace_events.zig`",
    "- `samples/zigux/runtime_trace_events.zig` is still a sample-only blocked Phase 9 pilot on current `master`; the bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold is shipped now, but keep it separate from the loader-backed follow-ons above because the runtime-substrate handoff still stays blocked",
    "- the current Phase 9 loader-side packet now depends on the shared `zigux/kernel/runtime_loader.zig` `RuntimeLoadRequest` boundary for `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_kretprobe_loader.zig`; keep `samples/zigux/runtime_trace_events_loader.zig` explicit as an adjacent scaffold until the trace-events blocker can truthfully adopt that same shared request path",
    "- the runtime bitmap packet rooted in `lib/test_bitmap.c` now includes `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and the focused `samples/zigux/runtime_bitmap_top_bit_contract.zig` plus `samples/zigux/runtime_bitmap_top_bit_build.zig` companion replay; keep that family cataloged here as later Phase 9 follow-on work rather than treating it as a fifth approved Phase 5 reference idiom",
    "- keep the bitmap runtime pilot visibly separate from the approved Phase 5 idiom set: `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and `samples/zigux/runtime_bitmap_top_bit_build.zig` belong with the Phase 9 runtime bitmap survey packet, not the four roadmap-approved Phase 5 anchor samples",
    "- keep `samples/zigux/runtime_trace_events.zig` explicit as a sample-only blocked Phase 9 pilot even though `samples/zigux/runtime_trace_events_loader.zig` is now shipped as a bounded scaffold, so the shared sample-root packet does not imply a cleared runtime-substrate handoff or a fully loader-backed runtime follow-on",
    "- when this loader-side catalog changes, keep `python3 scripts/zigux/check-phase9-loader-substrate-plan.py` in the same review packet so the sample-root runtime inventory stays aligned with `Documentation/zigux/phase9-runtime-loader-substrate-plan.md`, `zigux/tests/runtime_loader_gap_manifest.json`, and `zigux/tests/runtime_trace_events_manifest.json`",
]

MAKEFILE_REQUIRED_MARKERS = [
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py --self-test\n",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py\n",
]

TRACE_EVENTS_LOADER_REQUIRED_MARKERS = [
    "pub const RuntimeTraceEventsLoadPlan = struct",
    "command_name: ?[]const u8",
    "pub fn withCommandName",
    "pub fn prepareWithCommandName",
    "pub fn requestRuntimeLoad",
    "pub fn releasePlanWithoutSubstrate",
    "\"foo_bar_reg\"",
    "\"foo_bar_unreg\"",
]

TRACE_EVENTS_LOADER_REQUIRED_CONTROL_SURFACE_MARKERS = [
    "\"perf-runtime-trace-events\"",
    "error.InvalidCommandName",
]

TRACE_EVENTS_LOADER_FORBIDDEN_MARKERS = [
    "requestSharedRuntimeLoad",
    "releaseSharedRuntimeLoadWithoutSubstrate",
    "RuntimeLoadRequest",
    "toSharedRequest(",
]

TRACE_EVENTS_LOADER_FORBIDDEN_CONTROL_SURFACE_MARKERS = [
    "ExtractArgv0Result.command_name",
    "Config.exec_path_env",
    "\"PERF_EXEC_PATH\"",
    "env.get(\"PATH\")",
    "env_lines",
    "env_columns",
    "argv_policy",
    "activation_env",
]

EXPECTED_LIFECYCLE_BOUNDARY_SUMMARY = {
    "staged_init_exit_symbols_are_review_only": True,
    "kretprobe_registration_labels_are_metadata_only": True,
    "live_initcall_or_registration_path_present": False,
}

EXPECTED_FORBIDDEN_LIVE_CALLS = [
    "module_init()",
    "module_exit()",
    "register_kretprobe()",
    "unregister_kretprobe()",
]

EXPECTED_MODULE_METADATA_DEPMOD_BOUNDARIES = [
    {
        "surface": ".modinfo",
        "boundary_kind": "module_metadata",
        "status": "blocked_on_depmod_bridge",
        "why_non_owner_fragment": "blocked boundary",
    },
    {
        "surface": "MODULE_ALIAS()",
        "boundary_kind": "module_alias",
        "status": "blocked_on_depmod_bridge",
        "why_non_owner_fragment": "blocked boundary",
    },
    {
        "surface": "modules.alias",
        "boundary_kind": "depmod_output",
        "status": "blocked_on_depmod_bridge",
        "why_non_owner_fragment": "blocked boundary",
    },
    {
        "surface": "scripts/depmod.sh",
        "boundary_kind": "depmod_bridge",
        "status": "blocked_on_depmod_bridge",
        "why_non_owner_fragment": "blocked boundary",
    },
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


def validate_manifest_alignment(root: Path) -> list[str]:
    manifest_text = read_text(root, MANIFEST_PATH)
    survey_text = read_text(root, SURVEY_PATH)
    substrate_plan_text = read_text(root, SUBSTRATE_PLAN_PATH)

    missing_markers: list[str] = []

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError:
        return ["manifest:json_decode_failed"]

    manifest_commit = manifest.get("surveyed_commit")
    if not isinstance(manifest_commit, str) or not re.fullmatch(r"[0-9a-f]{40}", manifest_commit):
        return ["manifest:invalid_surveyed_commit"]

    survey_commit, survey_error = extract_markdown_surveyed_commit(survey_text, "survey")
    if survey_error:
        missing_markers.append(survey_error)
    elif survey_commit != manifest_commit:
        missing_markers.append("survey:surveyed_commit_mismatch")

    substrate_plan_commit, substrate_plan_error = extract_markdown_surveyed_commit(
        substrate_plan_text,
        "substrate_plan",
    )
    if substrate_plan_error:
        missing_markers.append(substrate_plan_error)
    elif substrate_plan_commit != manifest_commit:
        missing_markers.append("substrate_plan:surveyed_commit_mismatch")

    delivery_evidence = manifest.get("delivery_evidence_catalog")
    if not isinstance(delivery_evidence, list):
        missing_markers.append("manifest:delivery_evidence_catalog_missing")
    else:
        if not any(
            isinstance(entry, dict)
            and entry.get("id") == "runtime-loader-substrate-plan"
            and entry.get("path") == SUBSTRATE_PLAN_PATH
            for entry in delivery_evidence
        ):
            missing_markers.append("manifest:runtime-loader-substrate-plan_delivery_evidence_missing")
        if not any(
            isinstance(entry, dict)
            and entry.get("id") == "trace-events-loader-blocked-scaffold"
            and entry.get("path") == TRACE_EVENTS_LOADER_PATH
            for entry in delivery_evidence
        ):
            missing_markers.append("manifest:trace-events-loader-blocked-scaffold_delivery_evidence_missing")

    ownership_map = manifest.get("ownership_map")
    if not isinstance(ownership_map, list):
        missing_markers.append("manifest:ownership_map_missing")
    else:
        if not any(
            isinstance(entry, dict)
            and entry.get("surface") == SUBSTRATE_PLAN_PATH
            and isinstance(entry.get("owns"), str)
            and "shared loader-stage vocabulary" in entry["owns"]
            for entry in ownership_map
        ):
            missing_markers.append("manifest:runtime-loader-substrate-plan_ownership_missing")
        if not any(
            isinstance(entry, dict)
            and entry.get("surface") == TRACE_EVENTS_LOADER_PATH
            and isinstance(entry.get("owns"), str)
            and "trace-events loader-plan scaffold" in entry["owns"]
            and "without-substrate fallback" in entry["owns"]
            for entry in ownership_map
        ):
            missing_markers.append("manifest:trace-events-loader-blocked-scaffold_ownership_missing")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        missing_markers.append("manifest:gaps_missing")
    else:
        if not any(
            isinstance(entry, dict)
            and entry.get("id") == "runtime-loader-substrate-plan"
            and entry.get("zigux_destination") == SUBSTRATE_PLAN_PATH
            and isinstance(entry.get("why_now"), str)
            and "waiting_on_runtime_substrate" in entry["why_now"]
            and "released_without_substrate" in entry["why_now"]
            for entry in gaps
        ):
            missing_markers.append("manifest:runtime-loader-substrate-plan_gap_missing")
        if not any(
            isinstance(entry, dict)
            and entry.get("id") == "runtime-loader-trace-events-sample-only-boundary"
            and entry.get("zigux_destination") == TRACE_EVENTS_LOADER_PATH
            and isinstance(entry.get("why_now"), str)
            and "sample-only" in entry["why_now"]
            and "kernel/trace/ring_buffer.c" in entry["why_now"]
            for entry in gaps
        ):
            missing_markers.append("manifest:trace-events-loader-blocked-scaffold_gap_missing")

    control_surface_markers = manifest.get("phase8_control_surface_markers")
    if not isinstance(control_surface_markers, dict):
        missing_markers.append("manifest:phase8_control_surface_markers_missing")
    else:
        if control_surface_markers.get("shared_runtime_loader_field") != "shared command_name field":
            missing_markers.append("manifest:shared_runtime_loader_field_drift")
        if control_surface_markers.get("command_name_field") != "ExtractArgv0Result.command_name":
            missing_markers.append("manifest:command_name_field_drift")

    lifecycle_boundary_summary = manifest.get("lifecycle_boundary_summary")
    if not isinstance(lifecycle_boundary_summary, dict):
        missing_markers.append("manifest:lifecycle_boundary_summary_missing")
    else:
        for field, expected in EXPECTED_LIFECYCLE_BOUNDARY_SUMMARY.items():
            if lifecycle_boundary_summary.get(field) != expected:
                missing_markers.append(f"manifest:lifecycle_boundary_summary:{field}")
        if lifecycle_boundary_summary.get("forbidden_live_calls") != EXPECTED_FORBIDDEN_LIVE_CALLS:
            missing_markers.append("manifest:lifecycle_boundary_summary:forbidden_live_calls")

    module_metadata_depmod_boundaries = manifest.get("module_metadata_depmod_boundaries")
    if not isinstance(module_metadata_depmod_boundaries, list):
        missing_markers.append("manifest:module_metadata_depmod_boundaries_missing")
    else:
        if len(module_metadata_depmod_boundaries) != len(EXPECTED_MODULE_METADATA_DEPMOD_BOUNDARIES):
            missing_markers.append("manifest:module_metadata_depmod_boundaries:count")
        for index, expected in enumerate(EXPECTED_MODULE_METADATA_DEPMOD_BOUNDARIES):
            if index >= len(module_metadata_depmod_boundaries):
                missing_markers.append(
                    f"manifest:module_metadata_depmod_boundaries:{expected['surface']}:missing"
                )
                continue
            actual = module_metadata_depmod_boundaries[index]
            if actual.get("surface") != expected["surface"]:
                missing_markers.append(
                    f"manifest:module_metadata_depmod_boundaries:{expected['surface']}:surface"
                )
            if actual.get("boundary_kind") != expected["boundary_kind"]:
                missing_markers.append(
                    f"manifest:module_metadata_depmod_boundaries:{expected['surface']}:boundary_kind"
                )
            if actual.get("status") != expected["status"]:
                missing_markers.append(
                    f"manifest:module_metadata_depmod_boundaries:{expected['surface']}:status"
                )
            why_non_owner = actual.get("why_non_owner")
            if not isinstance(why_non_owner, str) or expected["why_non_owner_fragment"] not in why_non_owner:
                missing_markers.append(
                    f"manifest:module_metadata_depmod_boundaries:{expected['surface']}:why_non_owner"
                )

    return missing_markers


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []

    survey_text = read_text(root, SURVEY_PATH)
    substrate_plan_text = read_text(root, SUBSTRATE_PLAN_PATH)
    review_checklist_text = read_text(root, REVIEW_CHECKLIST_PATH)
    samples_readme_text = read_text(root, SAMPLES_README_PATH)
    makefile_text = read_text(root, MAKEFILE_PATH)
    trace_events_loader_text = read_text(root, TRACE_EVENTS_LOADER_PATH)

    missing_markers: list[str] = []

    for marker in SURVEY_REQUIRED_MARKERS:
        if marker not in survey_text:
            missing_markers.append(f"survey:{marker}")
    for marker in SUBSTRATE_PLAN_REQUIRED_MARKERS:
        if marker not in substrate_plan_text:
            missing_markers.append(f"substrate_plan:{marker}")
    for marker in REVIEW_CHECKLIST_REQUIRED_MARKERS:
        if marker not in review_checklist_text:
            missing_markers.append(f"review_checklist:{marker}")
    for marker in SAMPLES_README_REQUIRED_MARKERS:
        if marker not in samples_readme_text:
            missing_markers.append(f"samples_readme:{marker}")
    for marker in MAKEFILE_REQUIRED_MARKERS:
        if marker not in makefile_text:
            missing_markers.append(f"makefile:{marker}")
    for marker in TRACE_EVENTS_LOADER_REQUIRED_MARKERS:
        if marker not in trace_events_loader_text:
            missing_markers.append(f"trace_events_loader:{marker}")
    for marker in TRACE_EVENTS_LOADER_REQUIRED_CONTROL_SURFACE_MARKERS:
        if marker not in trace_events_loader_text:
            missing_markers.append(f"trace_events_loader_control_surface:{marker}")
    for marker in TRACE_EVENTS_LOADER_FORBIDDEN_MARKERS:
        if marker in trace_events_loader_text:
            missing_markers.append(f"trace_events_loader_forbidden:{marker}")
    for marker in TRACE_EVENTS_LOADER_FORBIDDEN_CONTROL_SURFACE_MARKERS:
        if marker in trace_events_loader_text:
            missing_markers.append(f"trace_events_loader_control_surface_forbidden:{marker}")

    missing_markers.extend(validate_manifest_alignment(root))
    return [], missing_markers


def write_fixture_tree(root: Path) -> None:
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "samples/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
    (root / "zigux/kernel").mkdir(parents=True, exist_ok=True)
    (root / "zigux/helpers").mkdir(parents=True, exist_ok=True)
    (root / "zigux").mkdir(parents=True, exist_ok=True)

    commit = "179066fc0b38700d1f1103de528b99cb63bef850"

    (root / SURVEY_PATH).write_text(
        "\n".join(
            [
                "# Phase 9 Runtime Loader Gap Survey",
                "",
                f"- `PHASE9_SURVEYED_COMMIT={commit}`",
                "The shared substrate plan is part of the same delivery packet now.",
                "`Documentation/zigux/phase9-runtime-loader-substrate-plan.md` keeps the shared loader-stage vocabulary explicit.",
                "",
                "## Gates",
                "",
                "- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test`",
                "- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py`",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / SUBSTRATE_PLAN_PATH).write_text(
        "\n".join(
            [
                "# Phase 9 Shared Runtime Loader Substrate Plan",
                "",
                "- `PHASE9_SLICE=shared-runtime-loader-substrate-plan`",
                f"- `PHASE9_SURVEYED_COMMIT={commit}`",
                "This note keeps the shared loader-stage vocabulary explicit.",
                "It covers zigux/kernel/runtime_loader.zig, samples/zigux/runtime_atomic64_loader.zig, samples/zigux/runtime_bitmap_loader.zig, and samples/zigux/runtime_kretprobe_loader.zig.",
                "It keeps zigux/helpers/allocator_policy.zig visible, with waiting_on_runtime_substrate and released_without_substrate as the shared handoff states.",
                "The shared `command_name` handoff field stays reviewable here.",
                "samples/zigux/runtime_trace_events.zig remains blocked while `kernel/trace/ring_buffer.c` stays Study / Boundary Only.",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / REVIEW_CHECKLIST_PATH).write_text(
        REVIEW_CHECKLIST_REQUIRED_MARKERS[0] + "\n",
        encoding="utf-8",
    )
    (root / SAMPLES_README_PATH).write_text(
        "\n".join(
            [
                "# Zigux Samples",
                "",
                "Later runtime starters, loader-side follow-ons, and blocked pilots",
                "- `samples/zigux/runtime_bitmap.zig`",
                "- `samples/zigux/runtime_bitmap_loader.zig`",
                "- `samples/zigux/runtime_trace_events.zig`",
                "- `samples/zigux/runtime_trace_events.zig` is still a sample-only blocked Phase 9 pilot on current `master`; the bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold is shipped now, but keep it separate from the loader-backed follow-ons above because the runtime-substrate handoff still stays blocked",
                "- the current Phase 9 loader-side packet now depends on the shared `zigux/kernel/runtime_loader.zig` `RuntimeLoadRequest` boundary for `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_kretprobe_loader.zig`; keep `samples/zigux/runtime_trace_events_loader.zig` explicit as an adjacent scaffold until the trace-events blocker can truthfully adopt that same shared request path",
                "- the runtime bitmap packet rooted in `lib/test_bitmap.c` now includes `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and the focused `samples/zigux/runtime_bitmap_top_bit_contract.zig` plus `samples/zigux/runtime_bitmap_top_bit_build.zig` companion replay; keep that family cataloged here as later Phase 9 follow-on work rather than treating it as a fifth approved Phase 5 reference idiom",
                "- keep the bitmap runtime pilot visibly separate from the approved Phase 5 idiom set: `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and `samples/zigux/runtime_bitmap_top_bit_build.zig` belong with the Phase 9 runtime bitmap survey packet, not the four roadmap-approved Phase 5 anchor samples",
                "- keep `samples/zigux/runtime_trace_events.zig` explicit as a sample-only blocked Phase 9 pilot even though `samples/zigux/runtime_trace_events_loader.zig` is now shipped as a bounded scaffold, so the shared sample-root packet does not imply a cleared runtime-substrate handoff or a fully loader-backed runtime follow-on",
                "- when this loader-side catalog changes, keep `python3 scripts/zigux/check-phase9-loader-substrate-plan.py` in the same review packet so the sample-root runtime inventory stays aligned with `Documentation/zigux/phase9-runtime-loader-substrate-plan.md`, `zigux/tests/runtime_loader_gap_manifest.json`, and `zigux/tests/runtime_trace_events_manifest.json`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / MAKEFILE_PATH).write_text(
        "\n".join(
            [
                "phase9-validate:",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py --self-test",
                "\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / MANIFEST_PATH).write_text(
        json.dumps(
            {
                "surveyed_commit": commit,
                "delivery_evidence_catalog": [
                    {
                        "id": "runtime-loader-substrate-plan",
                        "path": SUBSTRATE_PLAN_PATH,
                    },
                    {
                        "id": "trace-events-loader-blocked-scaffold",
                        "path": TRACE_EVENTS_LOADER_PATH,
                    },
                ],
                "ownership_map": [
                    {
                        "surface": SUBSTRATE_PLAN_PATH,
                        "owns": "shared loader-stage vocabulary plus the without-substrate fallback",
                    },
                    {
                        "surface": TRACE_EVENTS_LOADER_PATH,
                        "owns": "trace-events loader-plan scaffold plus the without-substrate fallback under the sample-only blocked boundary",
                    },
                ],
                "gaps": [
                    {
                        "id": "runtime-loader-substrate-plan",
                        "zigux_destination": SUBSTRATE_PLAN_PATH,
                        "why_now": "This keeps waiting_on_runtime_substrate and released_without_substrate explicit in one shared review surface.",
                    },
                    {
                        "id": "runtime-loader-trace-events-sample-only-boundary",
                        "zigux_destination": TRACE_EVENTS_LOADER_PATH,
                        "why_now": "This keeps the sample-only trace-events boundary explicit beside kernel/trace/ring_buffer.c while the runtime-substrate handoff stays blocked.",
                    },
                ],
                "phase8_control_surface_markers": {
                    "shared_runtime_loader_field": "shared command_name field",
                    "command_name_field": "ExtractArgv0Result.command_name",
                },
                "lifecycle_boundary_summary": {
                    **EXPECTED_LIFECYCLE_BOUNDARY_SUMMARY,
                    "forbidden_live_calls": EXPECTED_FORBIDDEN_LIVE_CALLS,
                },
                "module_metadata_depmod_boundaries": [
                    {
                        "surface": boundary["surface"],
                        "boundary_kind": boundary["boundary_kind"],
                        "status": boundary["status"],
                        "why_non_owner": f"{boundary['surface']} stays a blocked boundary until a real depmod bridge exists.",
                    }
                    for boundary in EXPECTED_MODULE_METADATA_DEPMOD_BOUNDARIES
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / RUNTIME_LOADER_PATH).write_text(
        "pub const runtime_loader_placeholder = true;\n",
        encoding="utf-8",
    )
    (root / ALLOCATOR_POLICY_PATH).writeText(
        "pub const allocator_policy_placeholder = true;\n",
        encoding="utf-8",
    )
    (root / ATOMIC64_LOADER_PATH).write_text(
        "pub const runtime_atomic64_loader_placeholder = true;\n",
        encoding="utf-8",
    )
    (root / BITMAP_LOADER_PATH).write_text(
        "pub const runtime_bitmap_loader_placeholder = true;\n",
        encoding="utf-8",
    )
    (root / KRETPROBE_LOADER_PATH).write_text(
        "pub const runtime_kretprobe_loader_placeholder = true;\n",
        encoding="utf-8",
    )
    (root / TRACE_EVENTS_LOADER_PATH).write_text(
        "\n".join(
            [
                "pub const RuntimeTraceEventsLoadPlan = struct {",
                "    command_name: ?[]const u8,",
                "};",
                "pub fn withCommandName() void {}",
                "pub fn prepareWithCommandName() void {}",
                "pub fn requestRuntimeLoad() void {}",
                "pub fn releasePlanWithoutSubstrate() void {}",
                'const review_only_command_name = "perf-runtime-trace-events";',
                "const invalid_command_name = error.InvalidCommandName;",
                'const register_api = "foo_bar_reg";',
                'const unregister_api = "foo_bar_unreg";',
                "",
            ]
        ),
        encoding="utf-8",
    )


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase9-loader-substrate-plan-selftest:{label}:unexpected_missing_files:{','.join(missing_files)}"
        )
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase9-loader-substrate-plan-selftest:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def expect_missing_file(label: str, root: Path, expected_file: str) -> None:
    missing_files, missing_markers = validate(root)
    if expected_file not in missing_files:
        actual = ",".join(missing_files) if missing_files else "none"
        raise SystemExit(
            f"phase9-loader-substrate-plan-selftest:{label}:expected_missing_file:{expected_file}:actual:{actual}"
        )
    if missing_markers:
        raise SystemExit(
            f"phase9-loader-substrate-plan-selftest:{label}:unexpected_missing_markers:{','.join(missing_markers)}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_loader_substrate_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase9-loader-substrate-plan-selftest:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        trace_events_loader_path = tmp_root / TRACE_EVENTS_LOADER_PATH
        original_trace_events_loader = trace_events_loader_path.read_text(encoding="utf-8")
        trace_events_loader_path.unlink()
        expect_missing_file(
            "trace_events_loader_required_file",
            tmp_root,
            TRACE_EVENTS_LOADER_PATH,
        )
        trace_events_loader_path.write_text(original_trace_events_loader, encoding="utf-8")

        makefile_path = tmp_root / MAKEFILE_PATH
        original_makefile = makefile_path.read_text(encoding="utf-8")
        makefile_path.write_text(
            original_makefile.replace(
                "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py --self-test\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "makefile_self_test_hook",
            tmp_root,
            "makefile:cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py --self-test\n",
        )
        makefile_path.write_text(original_makefile, encoding="utf-8")

        survey_path = tmp_root / SURVEY_PATH
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace(
                "Documentation/zigux/phase9-runtime-loader-substrate-plan.md",
                "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_substrate_plan_reference",
            tmp_root,
            "survey:Documentation/zigux/phase9-runtime-loader-substrate-plan.md",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        review_checklist_path = tmp_root / REVIEW_CHECKLIST_PATH
        original_review_checklist = review_checklist_path.read_text(encoding="utf-8")
        review_checklist_path.write_text("", encoding="utf-8")
        expect_missing_marker(
            "review_checklist_alignment",
            tmp_root,
            f"review_checklist:{REVIEW_CHECKLIST_REQUIRED_MARKERS[0]}",
        )
        review_checklist_path.write_text(original_review_checklist, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_self_test_gate",
            tmp_root,
            "survey:- `python3 scripts/zigux/check-phase9-loader-substrate-plan.py --self-test`",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        samples_readme_path = tmp_root / SAMPLES_README_PATH
        original_samples_readme = samples_readme_path.read_text(encoding="utf-8")
        samples_readme_path.write_text(
            original_samples_readme.replace(
                "- `samples/zigux/runtime_trace_events.zig` is still a sample-only blocked Phase 9 pilot on current `master`; the bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold is shipped now, but keep it separate from the loader-backed follow-ons above because the runtime-substrate handoff still stays blocked",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "samples_readme_blocked_trace_events_loader_boundary",
            tmp_root,
            "samples_readme:- `samples/zigux/runtime_trace_events.zig` is still a sample-only blocked Phase 9 pilot on current `master`; the bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold is shipped now, but keep it separate from the loader-backed follow-ons above because the runtime-substrate handoff still stays blocked",
        )
        samples_readme_path.write_text(original_samples_readme, encoding="utf-8")

        samples_readme_path.write_text(
            original_samples_readme.replace(
                "- the current Phase 9 loader-side packet now depends on the shared `zigux/kernel/runtime_loader.zig` `RuntimeLoadRequest` boundary for `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_kretprobe_loader.zig`; keep `samples/zigux/runtime_trace_events_loader.zig` explicit as an adjacent scaffold until the trace-events blocker can truthfully adopt that same shared request path",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "samples_readme_shared_runtime_loader_boundary",
            tmp_root,
            "samples_readme:- the current Phase 9 loader-side packet now depends on the shared `zigux/kernel/runtime_loader.zig` `RuntimeLoadRequest` boundary for `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_kretprobe_loader.zig`; keep `samples/zigux/runtime_trace_events_loader.zig` explicit as an adjacent scaffold until the trace-events blocker can truthfully adopt that same shared request path",
        )
        samples_readme_path.write_text(original_samples_readme, encoding="utf-8")

        samples_readme_path.write_text(
            original_samples_readme.replace(
                "- the runtime bitmap packet rooted in `lib/test_bitmap.c` now includes `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and the focused `samples/zigux/runtime_bitmap_top_bit_contract.zig` plus `samples/zigux/runtime_bitmap_top_bit_build.zig` companion replay; keep that family cataloged here as later Phase 9 follow-on work rather than treating it as a fifth approved Phase 5 reference idiom",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "samples_readme_runtime_bitmap_packet_boundary",
            tmp_root,
            "samples_readme:- the runtime bitmap packet rooted in `lib/test_bitmap.c` now includes `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and the focused `samples/zigux/runtime_bitmap_top_bit_contract.zig` plus `samples/zigux/runtime_bitmap_top_bit_build.zig` companion replay; keep that family cataloged here as later Phase 9 follow-on work rather than treating it as a fifth approved Phase 5 reference idiom",
        )
        samples_readme_path.write_text(original_samples_readme, encoding="utf-8")

        samples_readme_path.write_text(
            original_samples_readme.replace(
                "- when this loader-side catalog changes, keep `python3 scripts/zigux/check-phase9-loader-substrate-plan.py` in the same review packet so the sample-root runtime inventory stays aligned with `Documentation/zigux/phase9-runtime-loader-substrate-plan.md`, `zigux/tests/runtime_loader_gap_manifest.json`, and `zigux/tests/runtime_trace_events_manifest.json`",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "samples_readme_loader_checker_trace_events_manifest_alignment",
            tmp_root,
            "samples_readme:- when this loader-side catalog changes, keep `python3 scripts/zigux/check-phase9-loader-substrate-plan.py` in the same review packet so the sample-root runtime inventory stays aligned with `Documentation/zigux/phase9-runtime-loader-substrate-plan.md`, `zigux/tests/runtime_loader_gap_manifest.json`, and `zigux/tests/runtime_trace_events_manifest.json`",
        )
        samples_readme_path.write_text(original_samples_readme, encoding="utf-8")

        manifest_path = tmp_root / MANIFEST_PATH
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest = json.loads(original_manifest)
        manifest["delivery_evidence_catalog"][0]["id"] = "runtime-loader-gap-note"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_delivery_evidence",
            tmp_root,
            "manifest:runtime-loader-substrate-plan_delivery_evidence_missing",
        )
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest = json.loads(original_manifest)
        manifest["delivery_evidence_catalog"][1]["id"] = "runtime-trace-events-loader"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_trace_events_delivery_evidence",
            tmp_root,
            "manifest:trace-events-loader-blocked-scaffold_delivery_evidence_missing",
        )
        manifest_path.write_text(original_manifest, encoding="utf-8")

        substrate_plan_path = tmp_root / SUBSTRATE_PLAN_PATH
        original_substrate_plan = substrate_plan_path.read_text(encoding="utf-8")
        substrate_plan_path.write_text(
            original_substrate_plan.replace(
                "179066fc0b38700d1f1103de528b99cb63bef850",
                "0000000000000000000000000000000000000000",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "substrate_plan_commit_alignment",
            tmp_root,
            "substrate_plan:surveyed_commit_mismatch",
        )
        substrate_plan_path.write_text(original_substrate_plan, encoding="utf-8")

        manifest = json.loads(original_manifest)
        manifest["phase8_control_surface_markers"]["shared_runtime_loader_field"] = "shared loader field"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_shared_runtime_loader_field",
            tmp_root,
            "manifest:shared_runtime_loader_field_drift",
        )
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest = json.loads(original_manifest)
        manifest["phase8_control_surface_markers"]["command_name_field"] = "argv0"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_command_name_field",
            tmp_root,
            "manifest:command_name_field_drift",
        )
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest = json.loads(original_manifest)
        manifest["lifecycle_boundary_summary"]["live_initcall_or_registration_path_present"] = True
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_lifecycle_boundary_summary",
            tmp_root,
            "manifest:lifecycle_boundary_summary:live_initcall_or_registration_path_present",
        )
        manifest_path.write_text(original_manifest, encoding="utf-8")

        manifest = json.loads(original_manifest)
        manifest["module_metadata_depmod_boundaries"][1]["status"] = "starter_landed"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker(
            "manifest_module_metadata_depmod_boundary_status",
            tmp_root,
            "manifest:module_metadata_depmod_boundaries:MODULE_ALIAS():status",
        )
        manifest_path.write_text(original_manifest, encoding="utf-8")

        trace_events_loader_path.write_text(
            original_trace_events_loader.replace(
                "pub fn withCommandName() void {}",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "trace_events_loader_required_marker",
            tmp_root,
            "trace_events_loader:pub fn withCommandName",
        )
        trace_events_loader_path.write_text(original_trace_events_loader, encoding="utf-8")

        trace_events_loader_path.write_text(
            original_trace_events_loader.replace(
                'const review_only_command_name = "perf-runtime-trace-events";',
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "trace_events_loader_review_only_command_name",
            tmp_root,
            'trace_events_loader_control_surface:"perf-runtime-trace-events"',
        )
        trace_events_loader_path.write_text(original_trace_events_loader, encoding="utf-8")

        trace_events_loader_path.write_text(
            original_trace_events_loader + "\npub fn requestSharedRuntimeLoad() void {}\n",
            encoding="utf-8",
        )
        expect_missing_marker(
            "trace_events_loader_forbidden_shared_request",
            tmp_root,
            "trace_events_loader_forbidden:requestSharedRuntimeLoad",
        )
        trace_events_loader_path.write_text(original_trace_events_loader, encoding="utf-8")

        trace_events_loader_path.write_text(
            original_trace_events_loader + '\nconst env_hint = "PERF_EXEC_PATH";\n',
            encoding="utf-8",
        )
        expect_missing_marker(
            "trace_events_loader_forbidden_phase8_env_marker",
            tmp_root,
            'trace_events_loader_control_surface_forbidden:"PERF_EXEC_PATH"',
        )
        trace_events_loader_path.write_text(original_trace_events_loader, encoding="utf-8")

    print("PHASE9_LOADER_SUBSTRATE_PLAN_SELF_TEST=pass")
    print("PHASE9_LOADER_SUBSTRATE_PLAN_SELF_TEST_CASE_COUNT=20")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the dedicated Phase 9 runtime-loader substrate-plan packet."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root to validate. Defaults to the current directory.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in substrate-plan fixture drift checks.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(args.root)
    if missing_files:
        print("PHASE9_LOADER_SUBSTRATE_PLAN=fail")
        print("MISSING_PHASE9_LOADER_SUBSTRATE_PLAN_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE9_LOADER_SUBSTRATE_PLAN_FILES_END")
        return 1
    if missing_markers:
        print("PHASE9_LOADER_SUBSTRATE_PLAN=fail")
        print("MISSING_PHASE9_LOADER_SUBSTRATE_PLAN_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE9_LOADER_SUBSTRATE_PLAN_MARKERS_END")
        return 1

    print("PHASE9_LOADER_SUBSTRATE_PLAN=pass")
    print(
        "PHASE9_LOADER_SUBSTRATE_PLAN_MARKER_COUNT="
        f"{len(SURVEY_REQUIRED_MARKERS) + len(SUBSTRATE_PLAN_REQUIRED_MARKERS) + len(REVIEW_CHECKLIST_REQUIRED_MARKERS) + len(SAMPLES_README_REQUIRED_MARKERS) + len(MAKEFILE_REQUIRED_MARKERS) + len(TRACE_EVENTS_LOADER_REQUIRED_MARKERS) + len(TRACE_EVENTS_LOADER_REQUIRED_CONTROL_SURFACE_MARKERS) + len(TRACE_EVENTS_LOADER_FORBIDDEN_MARKERS) + len(TRACE_EVENTS_LOADER_FORBIDDEN_CONTROL_SURFACE_MARKERS) + 16}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
