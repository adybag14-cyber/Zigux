#!/usr/bin/env python3
"""Guard the current Phase 13 devres DMA/scatterlist boundary validation gap."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = Path("zigux/tests/phase13_devres_manifest.json")
SURVEY_PATH = Path("Documentation/zigux/phase13-devres-survey.md")
ALIGNMENT_CHECKER_PATH = Path("scripts/zigux/check-phase13-devres-packet-alignment.py")
REVIEWABILITY_PATH = Path("zigux/tests/phase13_devres_reviewability.zig")
DMA_REPLAY_PATH = Path("zigux/tests/phase13_devres_dma_coherent.zig")

EXPECTED_LANE = "P13-L01"
EXPECTED_COMMIT = "master-readback-2026-05-14"
DMA_GAP_ID = "phase13-devres-live-dma-mappings"
SCATTERLIST_GAP_ID = "phase13-devres-live-scatterlist-ownership"

ALIGNMENT_GAP_MARKERS = [
    "EXPECTED_GAP_COUNT = 17",
    "EXPECTED_BLOCKED_COUNT = 6",
    '"phase13-devres-live-scatterlist-ownership": "blocked_on_live_scatterlist_state"',
]

ALIGNMENT_ABSENT_MARKERS = [
    DMA_GAP_ID,
    "blocked_on_live_dma_state",
]

REVIEWABILITY_GAP_MARKERS = [
    'try std.testing.expectEqual(@as(usize, 17), manifest.gaps.len);',
    'try std.testing.expectEqual(@as(usize, 6), blocked_count);',
    'try expectGap(manifest, "phase13-devres-live-arch-memtype-state", "blocked_on_live_arch_memtype_state", "lib/devres.zig", "mutating real memtype state");',
]

REVIEWABILITY_ABSENT_MARKERS = [
    DMA_GAP_ID,
    "blocked_on_live_dma_state",
]

SURVEY_MARKERS = [
    EXPECTED_COMMIT,
    "helper-only DMA/scatterlist boundary",
    "live DMA-backed helpers or DMA mapping ownership",
    "live scatterlist ownership or `sg_table` lifecycle control",
]

DMA_REPLAY_MARKERS = [
    '"phase13-devres-live-scatterlist-ownership"',
    '"blocked_on_live_scatterlist_state"',
    "adjacent coherent-DMA evidence shard",
    "helper-only DMA/scatterlist boundary",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def require_markers(errors: list[str], scope: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            errors.append(f"{scope}:missing_marker:{marker}")


def require_absent_markers(errors: list[str], scope: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker in text:
            errors.append(f"{scope}:gap_closed_or_changed:{marker}")


def validate(root: Path) -> list[str]:
    errors: list[str] = []

    manifest_path = root / MANIFEST_PATH
    survey_path = root / SURVEY_PATH
    alignment_path = root / ALIGNMENT_CHECKER_PATH
    reviewability_path = root / REVIEWABILITY_PATH
    dma_replay_path = root / DMA_REPLAY_PATH

    for path in [manifest_path, survey_path, alignment_path, reviewability_path, dma_replay_path]:
        if not path.exists():
            errors.append(f"missing:{path.as_posix()}")

    if errors:
        return errors

    manifest = json.loads(read_text(manifest_path))
    if manifest.get("lane_key") != EXPECTED_LANE:
        errors.append(f"manifest:lane_mismatch:{manifest.get('lane_key')}")
    if manifest.get("surveyed_commit") != EXPECTED_COMMIT:
        errors.append(f"manifest:commit_mismatch:{manifest.get('surveyed_commit')}")

    gaps = {gap["id"]: gap for gap in manifest.get("gaps", [])}
    dma_gap = gaps.get(DMA_GAP_ID)
    if dma_gap is None:
        errors.append(f"manifest:missing_gap:{DMA_GAP_ID}")
    elif dma_gap.get("status") != "blocked_on_live_dma_state":
        errors.append(f"manifest:gap_status_mismatch:{DMA_GAP_ID}:{dma_gap.get('status')}")

    scatterlist_gap = gaps.get(SCATTERLIST_GAP_ID)
    if scatterlist_gap is None:
        errors.append(f"manifest:missing_gap:{SCATTERLIST_GAP_ID}")
    elif scatterlist_gap.get("status") != "blocked_on_live_scatterlist_state":
        errors.append(
            f"manifest:gap_status_mismatch:{SCATTERLIST_GAP_ID}:{scatterlist_gap.get('status')}"
        )

    blocked_dma_count = sum(1 for gap in gaps.values() if gap.get("status") == "blocked_on_live_dma_state")
    if blocked_dma_count != 1:
        errors.append(f"manifest:blocked_on_live_dma_state_count_mismatch:{blocked_dma_count}")

    require_markers(errors, "survey", read_text(survey_path), SURVEY_MARKERS)
    require_markers(errors, "alignment", read_text(alignment_path), ALIGNMENT_GAP_MARKERS)
    require_absent_markers(errors, "alignment", read_text(alignment_path), ALIGNMENT_ABSENT_MARKERS)
    require_markers(errors, "reviewability", read_text(reviewability_path), REVIEWABILITY_GAP_MARKERS)
    require_absent_markers(errors, "reviewability", read_text(reviewability_path), REVIEWABILITY_ABSENT_MARKERS)
    require_markers(errors, "dma_replay", read_text(dma_replay_path), DMA_REPLAY_MARKERS)

    return errors


def seed_fixture_tree(root: Path) -> None:
    manifest = {
        "lane_key": EXPECTED_LANE,
        "phase": "Phase 13",
        "surveyed_commit": EXPECTED_COMMIT,
        "anchor": "lib/devres.c",
        "roadmap_destinations": ["lib/devres.zig", "zigux/tests/", "Documentation/zigux/"],
        "survey_summary": {
            "preexisting_phase13_build_present": False,
            "preexisting_phase13_make_target_present": True,
            "preexisting_devres_zig_present": True,
            "preexisting_phase13_devres_test_present": True,
            "preexisting_phase13_devres_slice_present": True,
            "preexisting_phase13_devres_reviewability_present": True,
            "preexisting_phase13_devres_boundary_evidence_present": True,
            "preexisting_phase13_devres_survey_present": True,
            "preexisting_phase13_devres_dma_coherent_present": True,
        },
        "gaps": [
            {"id": "phase13-make-target", "status": "starter_landed"},
            {"id": "phase13-devres-helper-starter", "status": "starter_landed"},
            {"id": "phase13-devres-slice-note", "status": "starter_landed"},
            {"id": "phase13-devres-survey-note", "status": "starter_landed"},
            {"id": "phase13-devres-test-gate", "status": "starter_landed"},
            {"id": "phase13-devres-reviewability-gate", "status": "starter_landed"},
            {"id": "phase13-devres-boundary-evidence-gate", "status": "starter_landed"},
            {"id": "phase13-devres-iounmap-planner", "status": "starter_landed"},
            {"id": "phase13-devres-of-iomap-planner", "status": "starter_landed"},
            {"id": "phase13-devres-arch-io-wc-memtype-planner", "status": "starter_landed"},
            {"id": "phase13-devres-arch-phys-wc-token-planner", "status": "starter_landed"},
            {"id": "phase13-devres-live-mmio-mappings", "status": "blocked_on_live_mmio_state"},
            {"id": "phase13-devres-live-region-reservation", "status": "blocked_on_live_mmio_state"},
            {"id": "phase13-devres-live-release-region-mutation", "status": "blocked_on_live_mmio_state"},
            {"id": "phase13-devres-live-device-tree-walk", "status": "blocked_on_live_device_tree_state"},
            {"id": "phase13-devres-live-arch-memtype-state", "status": "blocked_on_live_arch_memtype_state"},
            {"id": DMA_GAP_ID, "status": "blocked_on_live_dma_state"},
            {"id": SCATTERLIST_GAP_ID, "status": "blocked_on_live_scatterlist_state"},
        ],
    }
    write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
    write_text(
        root / SURVEY_PATH,
        "\n".join(
            [
                f"surveyed commit: {EXPECTED_COMMIT}",
                "helper-only DMA/scatterlist boundary",
                "live DMA-backed helpers or DMA mapping ownership",
                "live scatterlist ownership or `sg_table` lifecycle control",
            ]
        )
        + "\n",
    )
    write_text(
        root / ALIGNMENT_CHECKER_PATH,
        "\n".join(ALIGNMENT_GAP_MARKERS) + "\n" + "# still missing live dma drift markers\n",
    )
    write_text(
        root / REVIEWABILITY_PATH,
        "\n".join(REVIEWABILITY_GAP_MARKERS) + "\n" + "// still missing live dma drift markers\n",
    )
    write_text(root / DMA_REPLAY_PATH, "\n".join(DMA_REPLAY_MARKERS) + "\n")


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_dma_boundary_gap_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")
        case_count += 1

        seed_fixture_tree(root)
        write_text(
            root / ALIGNMENT_CHECKER_PATH,
            "\n".join(ALIGNMENT_GAP_MARKERS + [DMA_GAP_ID, "blocked_on_live_dma_state"]) + "\n",
        )
        assert_only(
            validate(root),
            [
                f"alignment:gap_closed_or_changed:{DMA_GAP_ID}",
                "alignment:gap_closed_or_changed:blocked_on_live_dma_state",
            ],
            "alignment_gap_closed_failed",
        )

