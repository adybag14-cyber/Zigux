#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path.cwd()

MANIFEST_PATH = "zigux/tests/phase13_devres_manifest.json"
SLICE_PATH = "Documentation/zigux/phase13-devres-slice.md"
SURVEY_PATH = "Documentation/zigux/phase13-devres-survey.md"
HELPER_PATH = "lib/devres.zig"
REPLAY_PATH = "zigux/tests/phase13_devres.zig"
REVIEWABILITY_PATH = "zigux/tests/phase13_devres_reviewability.zig"
DMA_REPLAY_PATH = "zigux/tests/phase13_devres_dma_coherent.zig"

STALE_CHECKER_WARNING = (
    "older `scripts/zigux/check-phase13-devres-packet.py` wording should be treated as stale packet drift"
)
CURRENT_CHECKER_MARKER = "`scripts/zigux/check-phase13-devres-packet-alignment.py`"

IOUNMAP_SLICE_MARKERS = [
    "devm_iounmap()",
]

IOUNMAP_SURVEY_MARKERS = [
    "devm_iounmap()",
]

IOUNMAP_HELPER_MARKERS = [
    ".provides_iounmap_call_planning = true",
    "pub const ManagedIounmapPlan",
    "pub fn planManagedIounmap(",
    ".warns_on_release_miss = !release_matches",
]

IOUNMAP_REPLAY_MARKERS = [
    'test "phase13 devres plans a managed iounmap call and warns on release misses" {',
    "const miss = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4010);",
    "try std.testing.expect(miss.warns_on_release_miss);",
]

UC_WC_SLICE_MARKERS = [
    "devm_ioremap_uc()",
    "devm_ioremap_wc()",
]

UC_WC_SURVEY_MARKERS = [
    "devm_ioremap_uc()",
    "devm_ioremap_wc()",
]

UC_WC_HELPER_MARKERS = [
    ".provides_ioremap_uc_wrapper_planning = true",
    ".provides_ioremap_wc_wrapper_planning = true",
    "pub fn planManagedIoremapAcquireUc(",
    "pub fn planManagedIoremapAcquireWc(",
]

UC_WC_REPLAY_MARKERS = [
    'test "phase13 devres uncached ioremap wrapper forces the UC lifetime path" {',
    'test "phase13 devres uncached ioremap wrapper frees the release record on map failure" {',
    'test "phase13 devres write-combined ioremap wrapper forces the WC lifetime path" {',
    'test "phase13 devres write-combined ioremap wrapper frees the release record on map failure" {',
]

ARCH_TOKEN_SLICE_MARKERS = [
    "devm_arch_phys_wc_add()",
]

ARCH_TOKEN_SURVEY_MARKERS = [
    "devm_arch_phys_wc_add()",
]

ARCH_TOKEN_HELPER_MARKERS = [
    ".provides_arch_phys_wc_token_planning = true",
    "pub const ManagedPhysWcAddInput",
    "pub const ManagedPhysWcAddPlan",
    "pub fn planArchPhysWcAdd(",
]

ARCH_TOKEN_REPLAY_MARKERS = [
    'test "phase13 devres retains phys WC release tokens on successful token add" {',
    'test "phase13 devres frees phys WC release records when token add fails" {',
]

OF_IOMAP_PRETTY_NAME_HELPER_MARKERS = [
    "fail_pretty_name_allocation: bool = false",
    ".fail_pretty_name_allocation = input.fail_pretty_name_allocation,",
]

OF_IOMAP_PRETTY_NAME_REPLAY_MARKERS = [
    'test "phase13 devres propagates pretty-name allocation failure through devm_of_iomap planning" {',
    ".fail_pretty_name_allocation = true,",
    "try std.testing.expectEqual(devres.DeviceTreeIomapStage.managed_ioremap_resource, failure.stage);",
    "try std.testing.expectEqual(devres.ErrorCode.no_memory, failure.error_code);",
    "try std.testing.expectEqual(@as(?u64, 0x10), failure.reported_size);",
    "try std.testing.expectEqual(@as(?devres.ErrorStage, .pretty_name), failure.resource_stage);",
]

BOUNDARY_SURVEY_MARKERS = [
    "phase13-devres-live-mmio-mappings",
    "phase13-devres-live-device-tree-walk",
    "phase13-devres-live-arch-memtype-state",
    "phase13-devres-live-scatterlist-ownership",
    "live MMIO mappings",
    "live device-tree walking",
    "live arch memtype state transitions",
    "helper-only DMA/scatterlist boundary",
]

REVIEWABILITY_MARKERS = [
    '"P13-L01"',
    '"master-readback-2026-05-13"',
    '"phase13-make-target"',
    '"phase13-devres-arch-phys-wc-token-planner"',
    '"phase13-devres-live-arch-memtype-state"',
    '"phase13-devres-live-scatterlist-ownership"',
    "try std.testing.expectEqual(@as(usize, 9), starter_landed_count);",
    "try std.testing.expectEqual(@as(usize, 4), blocked_count);",
]

DMA_REPLAY_MARKERS = [
    '"preexisting_phase13_devres_dma_coherent_present": true',
    '"phase13-devres-live-mmio-mappings"',
    '"phase13-devres-live-arch-memtype-state"',
    '"phase13-devres-live-scatterlist-ownership"',
    '"blocked_on_live_scatterlist_state"',
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_file(root: Path, rel: str, errors: list[str]) -> Path | None:
    path = root / rel
    if not path.is_file():
        errors.append(f"missing:{rel}")
        return None
    return path


def require_markers(source: str, prefix: str, markers: list[str], errors: list[str]) -> None:
    for marker in markers:
        if marker not in source:
            errors.append(f"{prefix}:missing_marker:{marker}")


def contains_manifest_expectation(source: str, key: str, value: str) -> bool:
    literal = f'"{key}": "{value}"'
    escaped = literal.replace('"', '\\"')
    return literal in source or escaped in source


def contains_bool_expectation(source: str, key: str, value: bool) -> bool:
    literal_value = "true" if value else "false"
    literal = f'"{key}": {literal_value}'
    escaped = literal.replace('"', '\\"')
    return literal in source or escaped in source


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = require_file(root, MANIFEST_PATH, errors)
    slice_path = require_file(root, SLICE_PATH, errors)
    survey_path = require_file(root, SURVEY_PATH, errors)
    helper_path = require_file(root, HELPER_PATH, errors)
    replay_path = require_file(root, REPLAY_PATH, errors)
    reviewability_path = require_file(root, REVIEWABILITY_PATH, errors)
    dma_replay_path = require_file(root, DMA_REPLAY_PATH, errors)
    if errors:
        return errors

    manifest_text = read_text(manifest_path)
    slice_text = read_text(slice_path)
    survey_text = read_text(survey_path)
    helper_text = read_text(helper_path)
    replay_text = read_text(replay_path)
    reviewability_text = read_text(reviewability_path)
    dma_replay_text = read_text(dma_replay_path)

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        return [f"manifest:json_decode:{exc.msg}"]

    lane_key = manifest.get("lane_key")
    if lane_key != "P13-L01":
        errors.append(f"manifest:lane_key_mismatch:{lane_key}")
    else:
        if not contains_manifest_expectation(replay_text, "lane_key", lane_key):
            errors.append(f"replay:lane_key_mismatch:{lane_key}")
        if lane_key not in reviewability_text:
            errors.append(f"reviewability:lane_key_mismatch:{lane_key}")
        if f"`{lane_key}`" not in survey_text:
            errors.append(f"survey:lane_key_mismatch:{lane_key}")

    surveyed_commit = manifest.get("surveyed_commit")
    if surveyed_commit != "master-readback-2026-05-13":
        errors.append(f"manifest:surveyed_commit_mismatch:{surveyed_commit}")
    else:
        if not contains_manifest_expectation(replay_text, "surveyed_commit", surveyed_commit):
            errors.append(f"replay:surveyed_commit_mismatch:{surveyed_commit}")
        if surveyed_commit not in reviewability_text:
            errors.append(f"reviewability:surveyed_commit_mismatch:{surveyed_commit}")
        if surveyed_commit not in survey_text:
            errors.append(f"survey:surveyed_commit_mismatch:{surveyed_commit}")

    summary = manifest.get("survey_summary")
    if not isinstance(summary, dict):
        errors.append("manifest:survey_summary_missing")
    else:
        expected_bools = {
            "preexisting_phase13_build_present": False,
            "preexisting_phase13_make_target_present": True,
            "preexisting_phase13_devres_test_present": True,
            "preexisting_phase13_devres_reviewability_present": True,
            "preexisting_phase13_devres_survey_present": True,
            "preexisting_phase13_devres_dma_coherent_present": True,
        }
        for key, expected in expected_bools.items():
            if summary.get(key) is not expected:
                errors.append(f"manifest:summary_mismatch:{key}:{summary.get(key)}")
            if key.endswith("devres_dma_coherent_present") and not contains_bool_expectation(dma_replay_text, key, expected):
                errors.append(f"dma_replay:{key}_mismatch:{expected}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list) or len(gaps) != 13:
        errors.append(f"manifest:gaps_count_mismatch:{len(gaps) if isinstance(gaps, list) else 'missing'}")

    if STALE_CHECKER_WARNING not in survey_text:
        errors.append("survey:missing_stale_checker_warning")
    if CURRENT_CHECKER_MARKER not in survey_text:
        errors.append("survey:missing_current_checker_marker")

    require_markers(slice_text, "slice", IOUNMAP_SLICE_MARKERS, errors)
    require_markers(survey_text, "survey", IOUNMAP_SURVEY_MARKERS, errors)
    require_markers(helper_text, "helper", IOUNMAP_HELPER_MARKERS, errors)
    require_markers(replay_text, "replay", IOUNMAP_REPLAY_MARKERS, errors)

    require_markers(slice_text, "slice", UC_WC_SLICE_MARKERS, errors)
    require_markers(survey_text, "survey", UC_WC_SURVEY_MARKERS, errors)
    require_markers(helper_text, "helper", UC_WC_HELPER_MARKERS, errors)
    require_markers(replay_text, "replay", UC_WC_REPLAY_MARKERS, errors)

    require_markers(slice_text, "slice", ARCH_TOKEN_SLICE_MARKERS, errors)
    require_markers(survey_text, "survey", ARCH_TOKEN_SURVEY_MARKERS, errors)
    require_markers(helper_text, "helper", ARCH_TOKEN_HELPER_MARKERS, errors)
    require_markers(replay_text, "replay", ARCH_TOKEN_REPLAY_MARKERS, errors)

    require_markers(helper_text, "helper", OF_IOMAP_PRETTY_NAME_HELPER_MARKERS, errors)
    require_markers(replay_text, "replay", OF_IOMAP_PRETTY_NAME_REPLAY_MARKERS, errors)

    require_markers(survey_text, "survey", BOUNDARY_SURVEY_MARKERS, errors)
    require_markers(reviewability_text, "reviewability", REVIEWABILITY_MARKERS, errors)
    require_markers(dma_replay_text, "dma_replay", DMA_REPLAY_MARKERS, errors)

    return errors


def seed_fixture_tree(root: Path) -> None:
    write_text(
        root / MANIFEST_PATH,
        json.dumps(
            {
                "lane_key": "P13-L01",
                "phase": "Phase 13",
                "surveyed_commit": "master-readback-2026-05-13",
                "anchor": "lib/devres.c",
                "roadmap_destinations": [
                    "lib/devres.zig",
                    "zigux/tests/",
                    "Documentation/zigux/",
                ],
                "survey_summary": {
                    "preexisting_phase13_build_present": False,
                    "preexisting_phase13_make_target_present": True,
                    "preexisting_devres_zig_present": True,
                    "preexisting_phase13_devres_test_present": True,
                    "preexisting_phase13_devres_slice_present": True,
                    "preexisting_phase13_devres_reviewability_present": True,
                    "preexisting_phase13_devres_survey_present": True,
                    "preexisting_phase13_devres_dma_coherent_present": True,
                },
                "gaps": [
                    {"id": "phase13-make-target"},
                    {"id": "phase13-devres-helper-starter"},
                    {"id": "phase13-devres-slice-note"},
                    {"id": "phase13-devres-survey-note"},
                    {"id": "phase13-devres-test-gate"},
                    {"id": "phase13-devres-reviewability-gate"},
                    {"id": "phase13-devres-iounmap-planner"},
                    {"id": "phase13-devres-of-iomap-planner"},
                    {"id": "phase13-devres-arch-phys-wc-token-planner"},
                    {"id": "phase13-devres-live-mmio-mappings"},
                    {"id": "phase13-devres-live-device-tree-walk"},
                    {"id": "phase13-devres-live-arch-memtype-state"},
                    {"id": "phase13-devres-live-scatterlist-ownership"},
                ],
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / SLICE_PATH,
        "\n".join(
            [
                "devm_iounmap()",
                "devm_ioremap_uc()",
                "devm_ioremap_wc()",
                "devm_arch_phys_wc_add()",
            ]
        )
        + "\n",
    )
    write_text(
        root / SURVEY_PATH,
        "\n".join(
            [
                "# Phase 13 devres Survey",
                "`P13-L01` helper packet",
                "master-readback-2026-05-13",
                "devm_iounmap()",
                "devm_ioremap_uc()",
                "devm_ioremap_wc()",
                "devm_arch_phys_wc_add()",
                "live arch memtype state transitions",
                "phase13-devres-live-mmio-mappings",
                "phase13-devres-live-device-tree-walk",
                "phase13-devres-live-arch-memtype-state",
                "phase13-devres-live-scatterlist-ownership",
                "live MMIO mappings",
                "live device-tree walking",
                "helper-only DMA/scatterlist boundary",
                "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
                "older `scripts/zigux/check-phase13-devres-packet.py` wording should be treated as stale packet drift",
            ]
        )
        + "\n",
    )
    write_text(
        root / HELPER_PATH,
        "\n".join(
            [
                ".provides_iounmap_call_planning = true",
                "pub const ManagedIounmapPlan = struct {}",
                "pub fn planManagedIounmap(",
                ".warns_on_release_miss = !release_matches",
                ".provides_ioremap_uc_wrapper_planning = true",
                ".provides_ioremap_wc_wrapper_planning = true",
                "pub fn planManagedIoremapAcquireUc(",
                "pub fn planManagedIoremapAcquireWc(",
                ".provides_arch_phys_wc_token_planning = true",
                "pub const ManagedPhysWcAddInput = struct {}",
                "pub const ManagedPhysWcAddPlan = struct {}",
                "pub fn planArchPhysWcAdd(",
                "fail_pretty_name_allocation: bool = false",
                ".fail_pretty_name_allocation = input.fail_pretty_name_allocation,",
            ]
        )
        + "\n",
    )
    write_text(
        root / REPLAY_PATH,
        "\n".join(
            [
                'test "phase13 devres plans a managed iounmap call and warns on release misses" {',
                "const miss = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4010);",
                "try std.testing.expect(miss.warns_on_release_miss);",
                'test "phase13 devres uncached ioremap wrapper forces the UC lifetime path" {',
                'test "phase13 devres uncached ioremap wrapper frees the release record on map failure" {',
                'test "phase13 devres write-combined ioremap wrapper forces the WC lifetime path" {',
                'test "phase13 devres write-combined ioremap wrapper frees the release record on map failure" {',
                'test "phase13 devres retains phys WC release tokens on successful token add" {',
                'test "phase13 devres frees phys WC release records when token add fails" {',
                'test "phase13 devres propagates pretty-name allocation failure through devm_of_iomap planning" {',
                ".fail_pretty_name_allocation = true,",
                "try std.testing.expectEqual(devres.DeviceTreeIomapStage.managed_ioremap_resource, failure.stage);",
                "try std.testing.expectEqual(devres.ErrorCode.no_memory, failure.error_code);",
                "try std.testing.expectEqual(@as(?u64, 0x10), failure.reported_size);",
                "try std.testing.expectEqual(@as(?devres.ErrorStage, .pretty_name), failure.resource_stage);",
                '  try expectContains(manifest_text, "\\\"lane_key\\\": \\\"P13-L01\\\"");',
                '  try expectContains(manifest_text, "\\\"surveyed_commit\\\": \\\"master-readback-2026-05-13\\\"");',
            ]
        )
        + "\n",
    )
    write_text(
        root / REVIEWABILITY_PATH,
        "\n".join(
            [
                '  try std.testing.expectEqualStrings("P13-L01", manifest.lane_key);',
                '  try std.testing.expectEqualStrings("master-readback-2026-05-13", manifest.surveyed_commit);',
                '  try expectGap(manifest, "phase13-make-target", "starter_landed", "zigux/Makefile", "stable shared Phase 13 replay handle");',
                '  try expectGap(manifest, "phase13-devres-arch-phys-wc-token-planner", "starter_landed", "lib/devres.zig", "negative token results");',
                '  try expectGap(manifest, "phase13-devres-live-arch-memtype-state", "blocked_on_live_arch_memtype_state", "lib/devres.zig", "mutating real memtype state");',
                '  try expectGap(manifest, "phase13-devres-live-scatterlist-ownership", "blocked_on_live_scatterlist_state", "lib/devres.zig", "DMA/scatterlist boundary");',
                "  try std.testing.expectEqual(@as(usize, 9), starter_landed_count);",
                "  try std.testing.expectEqual(@as(usize, 4), blocked_count);",
            ]
        )
        + "\n",
    )
    write_text(
        root / DMA_REPLAY_PATH,
        "\n".join(
            [
                '"preexisting_phase13_devres_dma_coherent_present": true',
                '"phase13-devres-live-mmio-mappings"',
                '"phase13-devres-live-arch-memtype-state"',
                '"phase13-devres-live-scatterlist-ownership"',
                '"blocked_on_live_scatterlist_state"',
            ]
        )
        + "\n",
    )


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise SystemExit(f"{label}:expected={expected}:actual={actual}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_devres_alignment_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / SURVEY_PATH, "missing lane key\n")
        assert_only(
            validate(root),
            [
                "survey:lane_key_mismatch:P13-L01",
                "survey:surveyed_commit_mismatch:master-readback-2026-05-13",
                "survey:missing_stale_checker_warning",
                "survey:missing_current_checker_marker",
                "survey:missing_marker:devm_iounmap()",
                "survey:missing_marker:devm_ioremap_uc()",
                "survey:missing_marker:devm_ioremap_wc()",
                "survey:missing_marker:devm_arch_phys_wc_add()",
                "survey:missing_marker:phase13-devres-live-mmio-mappings",
                "survey:missing_marker:phase13-devres-live-device-tree-walk",
                "survey:missing_marker:phase13-devres-live-arch-memtype-state",
                "survey:missing_marker:phase13-devres-live-scatterlist-ownership",
                "survey:missing_marker:live MMIO mappings",
                "survey:missing_marker:live device-tree walking",
                "survey:missing_marker:live arch memtype state transitions",
                "survey:missing_marker:helper-only DMA/scatterlist boundary",
            ],
            "survey_missing_markers_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / SLICE_PATH, "devm_iounmap()\ndevm_arch_phys_wc_add()\n")
        assert_only(
            validate(root),
            [
                "slice:missing_marker:devm_ioremap_uc()",
                "slice:missing_marker:devm_ioremap_wc()",
            ],
            "slice_missing_uc_wc_markers_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / REVIEWABILITY_PATH, "P13-L01 only\n")
        assert_only(
            validate(root),
            [
                "reviewability:surveyed_commit_mismatch:master-readback-2026-05-13",
                'reviewability:missing_marker:"P13-L01"',
                'reviewability:missing_marker:"master-readback-2026-05-13"',
                'reviewability:missing_marker:"phase13-make-target"',
                'reviewability:missing_marker:"phase13-devres-arch-phys-wc-token-planner"',
                'reviewability:missing_marker:"phase13-devres-live-arch-memtype-state"',
                'reviewability:missing_marker:"phase13-devres-live-scatterlist-ownership"',
                "reviewability:missing_marker:try std.testing.expectEqual(@as(usize, 9), starter_landed_count);",
                "reviewability:missing_marker:try std.testing.expectEqual(@as(usize, 4), blocked_count);",
            ],
            "reviewability_missing_markers_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / HELPER_PATH, ".provides_iounmap_call_planning = true\n")
        assert_only(
            validate(root),
            [
                "helper:missing_marker:pub const ManagedIounmapPlan",
                "helper:missing_marker:pub fn planManagedIounmap(",
                "helper:missing_marker:.warns_on_release_miss = !release_matches",
                "helper:missing_marker:.provides_ioremap_uc_wrapper_planning = true",
                "helper:missing_marker:.provides_ioremap_wc_wrapper_planning = true",
                "helper:missing_marker:pub fn planManagedIoremapAcquireUc(",
                "helper:missing_marker:pub fn planManagedIoremapAcquireWc(",
                "helper:missing_marker:.provides_arch_phys_wc_token_planning = true",
                "helper:missing_marker:pub const ManagedPhysWcAddInput",
                "helper:missing_marker:pub const ManagedPhysWcAddPlan",
                "helper:missing_marker:pub fn planArchPhysWcAdd(",
                "helper:missing_marker:fail_pretty_name_allocation: bool = false",
                "helper:missing_marker:.fail_pretty_name_allocation = input.fail_pretty_name_allocation,",
            ],
            "helper_missing_markers_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / REPLAY_PATH,
            "\n".join(
                [
                    'test "phase13 devres plans a managed iounmap call and warns on release misses" {',
                    "const miss = devres.DevresHelperLab.planManagedIounmap(0x4000, 0x4010);",
                    "try std.testing.expect(miss.warns_on_release_miss);",
                    'test "phase13 devres retains phys WC release tokens on successful token add" {',
                    'test "phase13 devres frees phys WC release records when token add fails" {',
                    '  try expectContains(manifest_text, "\\\"lane_key\\\": \\\"P13-L01\\\"");',
                    '  try expectContains(manifest_text, "\\\"surveyed_commit\\\": \\\"master-readback-2026-05-13\\\"");',
                ]
            )
            + "\n",
        )
        assert_only(
            validate(root),
            [
                'replay:missing_marker:test "phase13 devres uncached ioremap wrapper forces the UC lifetime path" {',
                'replay:missing_marker:test "phase13 devres uncached ioremap wrapper frees the release record on map failure" {',
                'replay:missing_marker:test "phase13 devres write-combined ioremap wrapper forces the WC lifetime path" {',
                'replay:missing_marker:test "phase13 devres write-combined ioremap wrapper frees the release record on map failure" {',
                'replay:missing_marker:test "phase13 devres propagates pretty-name allocation failure through devm_of_iomap planning" {',
                "replay:missing_marker:.fail_pretty_name_allocation = true,",
                "replay:missing_marker:try std.testing.expectEqual(devres.DeviceTreeIomapStage.managed_ioremap_resource, failure.stage);",
                "replay:missing_marker:try std.testing.expectEqual(devres.ErrorCode.no_memory, failure.error_code);",
                "replay:missing_marker:try std.testing.expectEqual(@as(?u64, 0x10), failure.reported_size);",
                "replay:missing_marker:try std.testing.expectEqual(@as(?devres.ErrorStage, .pretty_name), failure.resource_stage);",
            ],
            "replay_missing_uc_wc_and_of_iomap_markers_failed",
        )
        case_count += 1

        seed_fixture_tree(root)
        write_text(root / DMA_REPLAY_PATH, "nothing useful\n")
        assert_only(
            validate(root),
            [
                "dma_replay:preexisting_phase13_devres_dma_coherent_present_mismatch:True",
                'dma_replay:missing_marker:"preexisting_phase13_devres_dma_coherent_present": true',
                'dma_replay:missing_marker:"phase13-devres-live-mmio-mappings"',
                'dma_replay:missing_marker:"phase13-devres-live-arch-memtype-state"',
                'dma_replay:missing_marker:"phase13-devres-live-scatterlist-ownership"',
                'dma_replay:missing_marker:"blocked_on_live_scatterlist_state"',
            ],
            "dma_replay_missing_markers_failed",
        )
        case_count += 1

    print("PHASE13_DEVRES_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_ALIGNMENT_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 13 devres survey packet stays aligned with its manifest-backed replay."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to validate.")
    parser.add_argument("--self-test", action="store_true", help="Run checker self-tests.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    errors = validate(args.root)
    if errors:
        for error in errors:
            print(error)
        return 1

    print("PHASE13_DEVRES_ALIGNMENT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
