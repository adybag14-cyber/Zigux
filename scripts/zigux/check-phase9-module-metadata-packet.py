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
PHASE9_BUILD_PATH = "zigux/tests/phase9_build.zig"
LOADER_GAP_SURVEY_PATH = "Documentation/zigux/phase9-runtime-loader-gap-survey.md"
RUNTIME_LOADER_PATH = "zigux/kernel/runtime_loader.zig"
TESTS_README_PATH = "zigux/tests/README.md"

REQUIRED_FILES = [
    SURVEY_PATH,
    MANIFEST_PATH,
    SURVEY_TEST_PATH,
    PHASE9_BUILD_PATH,
    LOADER_GAP_SURVEY_PATH,
    RUNTIME_LOADER_PATH,
    TESTS_README_PATH,
]

SURVEY_REQUIRED_MARKERS = [
    "`PHASE9_SLICE=runtime-module-metadata-depmod-bridge-survey`",
    "`PHASE9_SURVEYED_COMMIT=",
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
]

PHASE9_BUILD_REQUIRED_MARKERS = [
    "runtime_module_metadata_survey.zig",
    "phase9-runtime-module-metadata-survey-tests",
]

SURVEY_TEST_REQUIRED_MARKERS = [
    'test "runtime module metadata manifest keeps the dedicated descriptor and depmod-gap packet explicit" {',
    'test "runtime module metadata survey note keeps descriptor fields, shared loader metadata, and depmod gaps explicit" {',
    'test "runtime module metadata survey proves the live starter descriptors and shared loader metadata surface directly" {',
    '"Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md"',
    '"zigux/tests/runtime_module_metadata_manifest.json"',
    '"Documentation/zigux/phase9-runtime-loader-gap-survey.md"',
    '"zigux/kernel/runtime_loader.zig"',
    '"samples/zigux/runtime_trace_events.zig"',
    '"MODULE_INFO()"',
    '"MODULE_ALIAS()"',
    '"scripts/depmod.sh"',
    '"RuntimeLoadRequest"',
    '"runtime_trace_events_loader.zig"',
]

LOADER_GAP_SURVEY_REQUIRED_MARKERS = [
    "samples/zigux/runtime_trace_events_loader.zig",
    "sample-only blocked runtime pilot",
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


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def collect_missing_files(root: Path) -> list[str]:
    return [rel_path for rel_path in REQUIRED_FILES if not (root / rel_path).exists()]


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
            "runtime_loader_plan_count": 3,
            "runtime_sample_only_blocked_count": 1,
            "shared_metadata_field_count": 9,
            "depmod_gap_count": 8,
            "shared_runtime_loader_present": True,
            "runtime_trace_events_loader_present": False,
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
    ]:
        failures.append("manifest:runtime_loader_plans_drift")

    sample_only_blocked = manifest.get("runtime_sample_only_blocked")
    if not isinstance(sample_only_blocked, list) or len(sample_only_blocked) != 1:
        failures.append("manifest:runtime_sample_only_blocked_drift")
    elif sample_only_blocked[0].get("blocked_loader_path") != "samples/zigux/runtime_trace_events_loader.zig":
        failures.append("manifest:blocked_loader_path_drift")

    delivery_evidence = manifest.get("delivery_evidence_catalog")
    if not isinstance(delivery_evidence, list):
        failures.append("manifest:delivery_evidence_catalog_missing")
    else:
        expected_pairs = {
            ("runtime-module-metadata-survey-note", SURVEY_PATH),
            ("runtime-module-metadata-manifest", MANIFEST_PATH),
            ("runtime-module-metadata-survey-gate", SURVEY_TEST_PATH),
            ("runtime-loader-gap-note", LOADER_GAP_SURVEY_PATH),
            ("shared-runtime-loader-contract", RUNTIME_LOADER_PATH),
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
            LOADER_GAP_SURVEY_PATH,
            RUNTIME_LOADER_PATH,
        }
        actual_surfaces = {
            entry.get("surface")
            for entry in ownership_map
            if isinstance(entry, dict)
        }
        if actual_surfaces != required_surfaces:
            failures.append("manifest:ownership_map_drift")

    review_prompts = manifest.get("review_prompts")
    if not isinstance(review_prompts, list) or len(review_prompts) != 3:
        failures.append("manifest:review_prompts_drift")

    return failures


def validate(root: Path) -> tuple[list[str], list[str]]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return missing_files, []

    survey_text = read_text(root, SURVEY_PATH)
    survey_test_text = read_text(root, SURVEY_TEST_PATH)
    phase9_build_text = read_text(root, PHASE9_BUILD_PATH)
    loader_gap_survey_text = read_text(root, LOADER_GAP_SURVEY_PATH)
    runtime_loader_text = read_text(root, RUNTIME_LOADER_PATH)
    tests_readme_text = read_text(root, TESTS_README_PATH)

    failures: list[str] = []

    for marker in SURVEY_REQUIRED_MARKERS:
        if marker not in survey_text:
            failures.append(f"survey:{marker}")
    for marker in PHASE9_BUILD_REQUIRED_MARKERS:
        if marker not in phase9_build_text:
            failures.append(f"phase9_build:{marker}")
    for marker in SURVEY_TEST_REQUIRED_MARKERS:
        if marker not in survey_test_text:
            failures.append(f"survey_test:{marker}")
    for marker in LOADER_GAP_SURVEY_REQUIRED_MARKERS:
        if marker not in loader_gap_survey_text:
            failures.append(f"loader_gap_survey:{marker}")
    for marker in RUNTIME_LOADER_REQUIRED_MARKERS:
        if marker not in runtime_loader_text:
            failures.append(f"runtime_loader:{marker}")
    for marker in TESTS_README_REQUIRED_MARKERS:
        if marker not in tests_readme_text:
            failures.append(f"tests_readme:{marker}")

    failures.extend(validate_manifest_packet(root))
    return [], failures


def write_fixture_tree(root: Path) -> None:
    (root / "Documentation/zigux").mkdir(parents=True, exist_ok=True)
    (root / "zigux/tests").mkdir(parents=True, exist_ok=True)
    (root / "zigux/kernel").mkdir(parents=True, exist_ok=True)

    commit = "5a2398b1223d2c1e39c84c500f684244f4182eff"
    manifest = {
        "lane_key": "P9-L07",
        "phase": "Phase 9",
        "surveyed_commit": commit,
        "survey_summary": {
            "runtime_descriptor_count": 4,
            "runtime_loader_lane_count": 3,
            "runtime_loader_plan_count": 3,
            "runtime_sample_only_blocked_count": 1,
            "shared_metadata_field_count": 9,
            "depmod_gap_count": 8,
            "shared_runtime_loader_present": True,
            "runtime_trace_events_loader_present": False,
        },
        "runtime_loader_plans": [
            "samples/zigux/runtime_atomic64_loader.zig",
            "samples/zigux/runtime_bitmap_loader.zig",
            "samples/zigux/runtime_kretprobe_loader.zig",
        ],
        "runtime_sample_only_blocked": [
            {
                "sample_path": "samples/zigux/runtime_trace_events.zig",
                "blocked_loader_path": "samples/zigux/runtime_trace_events_loader.zig",
            }
        ],
        "depmod_gap_surfaces": EXPECTED_DEPMOD_GAP_SURFACES,
        "delivery_evidence_catalog": [
            {"id": "runtime-module-metadata-survey-note", "path": SURVEY_PATH},
            {"id": "runtime-module-metadata-manifest", "path": MANIFEST_PATH},
            {"id": "runtime-module-metadata-survey-gate", "path": SURVEY_TEST_PATH},
            {"id": "runtime-loader-gap-note", "path": LOADER_GAP_SURVEY_PATH},
            {"id": "shared-runtime-loader-contract", "path": RUNTIME_LOADER_PATH},
        ],
        "ownership_map": [
            {"surface": SURVEY_PATH},
            {"surface": MANIFEST_PATH},
            {"surface": SURVEY_TEST_PATH},
            {"surface": LOADER_GAP_SURVEY_PATH},
            {"surface": RUNTIME_LOADER_PATH},
        ],
        "review_prompts": ["a", "b", "c"],
    }

    (root / SURVEY_PATH).write_text(
        "\n".join(
            [
                "# Phase 9 Module Metadata and Depmod Bridge Survey",
                "",
                "- `PHASE9_SLICE=runtime-module-metadata-depmod-bridge-survey`",
                f"- `PHASE9_SURVEYED_COMMIT={commit}`",
                "ModuleDescriptor keeps requires_runtime_substrate and provides_selftest_hook explicit.",
                "RuntimeLoadRequest keeps module_name, command_name, entry_symbol, exit_symbol, handoff_stage, and allocator_handoff explicit.",
                "The packet names samples/zigux/runtime_trace_events_loader.zig plus MODULE_INFO(), MODULE_ALIAS(), .modinfo, modules.alias, modules.order, modules.builtin, Module.symvers, and scripts/depmod.sh directly.",
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
                "",
                "5. run the shared convenience target",
                "- `make -C zigux phase9-validate`",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (root / MANIFEST_PATH).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (root / SURVEY_TEST_PATH).write_text(
        "\n".join(
            [
                'test "runtime module metadata manifest keeps the dedicated descriptor and depmod-gap packet explicit" {',
                'test "runtime module metadata survey note keeps descriptor fields, shared loader metadata, and depmod gaps explicit" {',
                'test "runtime module metadata survey proves the live starter descriptors and shared loader metadata surface directly" {',
                f'"{SURVEY_PATH}"',
                f'"{MANIFEST_PATH}"',
                f'"{LOADER_GAP_SURVEY_PATH}"',
                f'"{RUNTIME_LOADER_PATH}"',
                '"samples/zigux/runtime_trace_events.zig"',
                '"MODULE_INFO()"',
                '"MODULE_ALIAS()"',
                '"scripts/depmod.sh"',
                '"RuntimeLoadRequest"',
                '"runtime_trace_events_loader.zig"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / PHASE9_BUILD_PATH).write_text(
        "\n".join(
            [
                "runtime_module_metadata_survey.zig",
                "phase9-runtime-module-metadata-survey-tests",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / LOADER_GAP_SURVEY_PATH).write_text(
        "samples/zigux/runtime_trace_events_loader.zig\nsample-only blocked runtime pilot\n",
        encoding="utf-8",
    )
    (root / RUNTIME_LOADER_PATH).write_text(
        "\n".join(
            [
                "pub const RuntimeLoadRequest = struct {",
                "    module_name: []const u8,",
                "    command_name: ?[]const u8,",
                "    entry_symbol: []const u8,",
                "    exit_symbol: []const u8,",
                "    handoff_stage: u8,",
                "    allocator_handoff: u8,",
                "};",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / TESTS_README_PATH).write_text(
        "\n".join(
            [
                "# zigux/tests",
                "",
                "- keep the current Phase 9 runtime bundle reviewable through `zigux/tests/phase9_build.zig`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_module_metadata_survey.zig`, `zigux/tests/runtime_module_metadata_manifest.json`, `scripts/zigux/validate-phase9.py`, `make -C zigux phase9-validate`, and the focused `make -C zigux phase9-trace-events-survey` replay instead of widening into ad hoc runtime-slice checks",
                "- keep the dedicated Phase 9 module-metadata packet explicit beside the loader-gap packet: `Documentation/zigux/phase9-module-metadata-depmod-bridge-survey.md`, `zigux/tests/runtime_module_metadata_manifest.json`, and `zigux/tests/runtime_module_metadata_survey.zig` should continue to record the starter-descriptor surface and absent depmod-facing metadata without implying `.modinfo`, `MODULE_ALIAS()`, or `scripts/depmod.sh` parity",
                "",
            ]
        ),
        encoding="utf-8",
    )


def expect_missing_marker(label: str, root: Path, expected_marker: str) -> None:
    missing_files, missing_markers = validate(root)
    if missing_files:
        raise SystemExit(
            f"phase9-module-metadata-selftest:{label}:unexpected_missing_files:{','.join(missing_files)}"
        )
    if expected_marker not in missing_markers:
        actual = ",".join(missing_markers) if missing_markers else "none"
        raise SystemExit(
            f"phase9-module-metadata-selftest:{label}:expected_missing_marker:{expected_marker}:actual:{actual}"
        )


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase9_module_metadata_") as tmp_dir:
        tmp_root = Path(tmp_dir)
        write_fixture_tree(tmp_root)

        missing_files, missing_markers = validate(tmp_root)
        if missing_files or missing_markers:
            raise SystemExit(
                "phase9-module-metadata-selftest:baseline_failed:"
                f"files={','.join(missing_files) if missing_files else 'none'}:"
                f"markers={','.join(missing_markers) if missing_markers else 'none'}"
            )

        survey_path = tmp_root / SURVEY_PATH
        original_survey = survey_path.read_text(encoding="utf-8")
        survey_path.write_text(
            original_survey.replace("MODULE_ALIAS()", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker("survey_depmod_surface", tmp_root, "survey:MODULE_ALIAS()")
        survey_path.write_text(original_survey, encoding="utf-8")

        manifest_path = tmp_root / MANIFEST_PATH
        original_manifest = manifest_path.read_text(encoding="utf-8")
        manifest = json.loads(original_manifest)
        manifest["survey_summary"]["depmod_gap_count"] = 7
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_missing_marker("manifest_depmod_count", tmp_root, "manifest:summary_depmod_gap_count_drift")
        manifest_path.write_text(original_manifest, encoding="utf-8")

        survey_test_path = tmp_root / SURVEY_TEST_PATH
        original_survey_test = survey_test_path.read_text(encoding="utf-8")
        survey_test_path.write_text(
            original_survey_test.replace('"runtime_trace_events_loader.zig"', "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_test_trace_events_loader_boundary",
            tmp_root,
            'survey_test:"runtime_trace_events_loader.zig"',
        )
        survey_test_path.write_text(original_survey_test, encoding="utf-8")

        phase9_build_path = tmp_root / PHASE9_BUILD_PATH
        original_phase9_build = phase9_build_path.read_text(encoding="utf-8")
        phase9_build_path.write_text(
            original_phase9_build.replace("phase9-runtime-module-metadata-survey-tests", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "phase9_build_module_metadata_step",
            tmp_root,
            "phase9_build:phase9-runtime-module-metadata-survey-tests",
        )
        phase9_build_path.write_text(original_phase9_build, encoding="utf-8")

        loader_gap_path = tmp_root / LOADER_GAP_SURVEY_PATH
        original_loader_gap = loader_gap_path.read_text(encoding="utf-8")
        loader_gap_path.write_text(
            original_loader_gap.replace("sample-only blocked runtime pilot", "", 1),
            encoding="utf-8",
        )
        expect_missing_marker(
            "loader_gap_sample_only_boundary",
            tmp_root,
            "loader_gap_survey:sample-only blocked runtime pilot",
        )
        loader_gap_path.write_text(original_loader_gap, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_checker_self_test_gate",
            tmp_root,
            "survey:- `python3 scripts/zigux/check-phase9-module-metadata-packet.py --self-test`",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        survey_path.write_text(
            original_survey.replace(
                "- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`\n",
                "",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "survey_checker_live_gate",
            tmp_root,
            "survey:- `python3 scripts/zigux/check-phase9-module-metadata-packet.py`",
        )
        survey_path.write_text(original_survey, encoding="utf-8")

        tests_readme_path = tmp_root / TESTS_README_PATH
        original_tests_readme = tests_readme_path.read_text(encoding="utf-8")
        tests_readme_path.write_text(
            original_tests_readme.replace(
                "keep the dedicated Phase 9 module-metadata packet explicit beside the loader-gap packet",
                "keep the dedicated Phase 9 packet explicit beside the loader-gap packet",
                1,
            ),
            encoding="utf-8",
        )
        expect_missing_marker(
            "tests_readme_packet_summary",
            tmp_root,
            "tests_readme:keep the dedicated Phase 9 module-metadata packet explicit beside the loader-gap packet",
        )

    print("PHASE9_MODULE_METADATA_PACKET_SELF_TEST=pass")
    print("PHASE9_MODULE_METADATA_PACKET_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the dedicated Phase 9 runtime module-metadata packet."
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
        help="Run the built-in module-metadata packet self-test.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing_files, missing_markers = validate(args.root)
    if missing_files:
        print("PHASE9_MODULE_METADATA_PACKET=fail")
        print("MISSING_PHASE9_MODULE_METADATA_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE9_MODULE_METADATA_PACKET_FILES_END")
        return 1
    if missing_markers:
        print("PHASE9_MODULE_METADATA_PACKET=fail")
        print("MISSING_PHASE9_MODULE_METADATA_PACKET_MARKERS_START")
        for marker in missing_markers:
            print(marker)
        print("MISSING_PHASE9_MODULE_METADATA_PACKET_MARKERS_END")
        return 1

    required_marker_count = (
        len(SURVEY_REQUIRED_MARKERS)
        + len(PHASE9_BUILD_REQUIRED_MARKERS)
        + len(SURVEY_TEST_REQUIRED_MARKERS)
        + len(LOADER_GAP_SURVEY_REQUIRED_MARKERS)
        + len(RUNTIME_LOADER_REQUIRED_MARKERS)
        + len(TESTS_README_REQUIRED_MARKERS)
        + 10
    )
    print("PHASE9_MODULE_METADATA_PACKET=pass")
    print(f"PHASE9_MODULE_METADATA_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE9_MODULE_METADATA_PACKET_REQUIRED_MARKER_COUNT="
        f"{required_marker_count}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
