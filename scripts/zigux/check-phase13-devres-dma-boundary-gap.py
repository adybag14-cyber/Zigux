#!/usr/bin/env python3
"""Guard the current Phase 13 devres DMA/scatterlist validation drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path("zigux/tests/phase13_devres_manifest.json")
SURVEY = Path("Documentation/zigux/phase13-devres-survey.md")
ALIGNMENT = Path("scripts/zigux/check-phase13-devres-packet-alignment.py")
REVIEWABILITY = Path("zigux/tests/phase13_devres_reviewability.zig")
DMA_REPLAY = Path("zigux/tests/phase13_devres_dma_coherent.zig")

EXPECTED_COMMIT = "master-readback-2026-05-14"
EXPECTED_LANE = "P13-L01"
DMA_GAP = "phase13-devres-live-dma-mappings"
SG_GAP = "phase13-devres-live-scatterlist-ownership"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = root / MANIFEST
    survey_path = root / SURVEY
    alignment_path = root / ALIGNMENT
    reviewability_path = root / REVIEWABILITY
    dma_replay_path = root / DMA_REPLAY

    for path in [manifest_path, survey_path, alignment_path, reviewability_path, dma_replay_path]:
        if not path.exists():
            errors.append(f"missing:{path.as_posix()}")
    if errors:
        return errors

    manifest = json.loads(read(manifest_path))
    if manifest.get("lane_key") != EXPECTED_LANE:
        errors.append(f"manifest:lane_mismatch:{manifest.get('lane_key')}")
    if manifest.get("surveyed_commit") != EXPECTED_COMMIT:
        errors.append(f"manifest:commit_mismatch:{manifest.get('surveyed_commit')}")

    gaps = {gap["id"]: gap for gap in manifest.get("gaps", [])}
    for gap_id, expected_status in [
        (DMA_GAP, "blocked_on_live_dma_state"),
        (SG_GAP, "blocked_on_live_scatterlist_state"),
    ]:
        gap = gaps.get(gap_id)
        if gap is None:
            errors.append(f"manifest:missing_gap:{gap_id}")
            continue
        if gap.get("status") != expected_status:
            errors.append(f"manifest:gap_status_mismatch:{gap_id}:{gap.get('status')}")

    if sum(1 for gap in gaps.values() if gap.get("status") == "blocked_on_live_dma_state") != 1:
        errors.append("manifest:blocked_on_live_dma_state_count_mismatch")

    survey = read(survey_path)
    for marker in [
        EXPECTED_COMMIT,
        "helper-only DMA/scatterlist boundary",
        "live DMA-backed helpers or DMA mapping ownership",
        "live scatterlist ownership or `sg_table` lifecycle control",
    ]:
        if marker not in survey:
            errors.append(f"survey:missing_marker:{marker}")

    dma_replay = read(dma_replay_path)
    for marker in [
        '"phase13-devres-live-scatterlist-ownership"',
        '"blocked_on_live_scatterlist_state"',
        "adjacent coherent-DMA evidence shard",
        "helper-only DMA/scatterlist boundary",
    ]:
        if marker not in dma_replay:
            errors.append(f"dma_replay:missing_marker:{marker}")

    alignment = read(alignment_path)
    for marker in [
        "EXPECTED_GAP_COUNT = 17",
        "EXPECTED_BLOCKED_COUNT = 6",
        '"phase13-devres-live-scatterlist-ownership": "blocked_on_live_scatterlist_state"',
    ]:
        if marker not in alignment:
            errors.append(f"alignment:missing_marker:{marker}")
    for marker in [DMA_GAP, "blocked_on_live_dma_state"]:
        if marker in alignment:
            errors.append(f"alignment:gap_closed_or_changed:{marker}")

    reviewability = read(reviewability_path)
    for marker in [
        'try std.testing.expectEqual(@as(usize, 17), manifest.gaps.len);',
        'try std.testing.expectEqual(@as(usize, 6), blocked_count);',
        'try expectGap(manifest, "phase13-devres-live-arch-memtype-state", "blocked_on_live_arch_memtype_state", "lib/devres.zig", "mutating real memtype state");',
    ]:
        if marker not in reviewability:
            errors.append(f"reviewability:missing_marker:{marker}")
    for marker in [DMA_GAP, "blocked_on_live_dma_state"]:
        if marker in reviewability:
            errors.append(f"reviewability:gap_closed_or_changed:{marker}")

    return errors


def seed_fixture_tree(root: Path) -> None:
    manifest = {
        "lane_key": EXPECTED_LANE,
        "surveyed_commit": EXPECTED_COMMIT,
        "gaps": [
            {"id": "phase13-devres-helper-starter", "status": "starter_landed"},
            {"id": DMA_GAP, "status": "blocked_on_live_dma_state"},
            {"id": SG_GAP, "status": "blocked_on_live_scatterlist_state"},
        ],
    }
    write(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")
    write(
        root / SURVEY,
        "\n".join(
            [
                EXPECTED_COMMIT,
                "helper-only DMA/scatterlist boundary",
                "live DMA-backed helpers or DMA mapping ownership",
                "live scatterlist ownership or `sg_table` lifecycle control",
            ]
        )
        + "\n",
    )
    write(
        root / DMA_REPLAY,
        "\n".join(
            [
                '"phase13-devres-live-scatterlist-ownership"',
                '"blocked_on_live_scatterlist_state"',
                "adjacent coherent-DMA evidence shard",
                "helper-only DMA/scatterlist boundary",
            ]
        )
        + "\n",
    )
    write(
        root / ALIGNMENT,
        "\n".join(
            [
                "EXPECTED_GAP_COUNT = 17",
                "EXPECTED_BLOCKED_COUNT = 6",
                '"phase13-devres-live-scatterlist-ownership": "blocked_on_live_scatterlist_state"',
            ]
        )
        + "\n",
    )
    write(
        root / REVIEWABILITY,
        "\n".join(
            [
                'try std.testing.expectEqual(@as(usize, 17), manifest.gaps.len);',
                'try std.testing.expectEqual(@as(usize, 6), blocked_count);',
                'try expectGap(manifest, "phase13-devres-live-arch-memtype-state", "blocked_on_live_arch_memtype_state", "lib/devres.zig", "mutating real memtype state");',
            ]
        )
        + "\n",
    )


def assert_only(actual: list[str], expected: list[str], label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase13_dma_boundary_gap_") as temp_dir:
        root = Path(temp_dir)

        seed_fixture_tree(root)
        assert_only(validate(root), [], "baseline_failed")

        seed_fixture_tree(root)
        write(root / ALIGNMENT, read(root / ALIGNMENT) + DMA_GAP + "\nblocked_on_live_dma_state\n")
        assert_only(
            validate(root),
            [
                f"alignment:gap_closed_or_changed:{DMA_GAP}",
                "alignment:gap_closed_or_changed:blocked_on_live_dma_state",
            ],
            "alignment_gap_closed_failed",
        )

        seed_fixture_tree(root)
        manifest = json.loads(read(root / MANIFEST))
        manifest["gaps"] = [gap for gap in manifest["gaps"] if gap["id"] != DMA_GAP]
        write(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")
        assert_only(
            validate(root),
            [
                f"manifest:missing_gap:{DMA_GAP}",
                "manifest:blocked_on_live_dma_state_count_mismatch",
            ],
            "manifest_missing_gap_failed",
        )

    print("PHASE13_DEVRES_DMA_BOUNDARY_GAP_SELF_TEST=pass")
    print("PHASE13_DEVRES_DMA_BOUNDARY_GAP_SELF_TEST_CASES=3")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Phase 13 devres DMA/scatterlist validation drift stays explicit."
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

    print("PHASE13_DEVRES_DMA_BOUNDARY_GAP=present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
