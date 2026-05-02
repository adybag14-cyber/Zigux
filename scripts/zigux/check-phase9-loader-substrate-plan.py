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
    "Documentation/zigux/phase9-runtime-loader-gap-survey.md",
    "Documentation/zigux/phase9-runtime-loader-substrate-plan.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/Makefile",
    "zigux/tests/runtime_loader_gap_manifest.json",
]

SURVEY_PATH = "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
SUBSTRATE_PLAN_PATH = "Documentation/zigux/phase9-runtime-loader-substrate-plan.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
MAKEFILE_PATH = "zigux/Makefile"
MANIFEST_PATH = "zigux/tests/runtime_loader_gap_manifest.json"

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

MAKEFILE_REQUIRED_MARKERS = [
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py --self-test\n",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase9-loader-substrate-plan.py\n",
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
    makefile_text = read_text(root, MAKEFILE_PATH)

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
    for marker in MAKEFILE_REQUIRED_MARKERS:
        if marker not in makefile_text:
            missing_markers.append(f"makefile:{marker}")

    missing_markers.extend(validate_manifest_alignment(root))
    return [], missing_markers


def write_fixture_tree(root: Path) -> None:
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
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
                    }
                ],
                "ownership_map": [
                    {
                        "surface": SUBSTRATE_PLAN_PATH,
                        "owns": "shared loader-stage vocabulary plus the without-substrate fallback",
                    }
                ],
                "gaps": [
                    {
                        "id": "runtime-loader-substrate-plan",
                        "zigux_destination": SUBSTRATE_PLAN_PATH,
                        "why_now": "This keeps waiting_on_runtime_substrate and released_without_substrate explicit in one shared review surface.",
                    }
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

    print("PHASE9_LOADER_SUBSTRATE_PLAN_SELF_TEST=pass")
    print("PHASE9_LOADER_SUBSTRATE_PLAN_SELF_TEST_CASE_COUNT=10")
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
        f"{len(SURVEY_REQUIRED_MARKERS) + len(SUBSTRATE_PLAN_REQUIRED_MARKERS) + len(REVIEW_CHECKLIST_REQUIRED_MARKERS) + len(MAKEFILE_REQUIRED_MARKERS) + 13}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
