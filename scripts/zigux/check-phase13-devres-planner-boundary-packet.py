#!/usr/bin/env python3
"""Guard the live Phase 13 devres planner-and-survey boundary packet."""

from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path


SURVEY = "Documentation/zigux/phase13-devres-survey.md"
SLICE = "Documentation/zigux/phase13-devres-slice.md"
DMAM_NOTE = "Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md"
SCATTERLIST_NOTE = "Documentation/zigux/phase13-devres-scatterlist-planner.md"
DMAM_MANIFEST = "zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json"
SCATTERLIST_MANIFEST = "zigux/tests/phase13_devres_scatterlist_planner_manifest.json"
DMA_REPLAY = "zigux/tests/phase13_devres_dma_coherent.zig"

REQUIRED_MARKERS = {
    SURVEY: [
        "# Phase 13 devres DMA, scatterlist, and MMIO Boundary Survey",
        "the shipped DMA and scatterlist boundary evidence, plus the still-missing MMIO and iomap safety gaps that remain open against the Phase 13 roadmap.",
        "`Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`",
        "`zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json`",
        "`Documentation/zigux/phase13-devres-scatterlist-planner.md`",
        "`zigux/tests/phase13_devres_scatterlist_planner_manifest.json`",
        "`zigux/tests/phase13_devres_dma_coherent.zig`",
        "`lib/devres_scatterlist.zig`",
        "`zigux/tests/phase13_devres_scatterlist.zig`",
        "current `master` does not ship `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_manifest.json`, or `scripts/zigux/check-phase13-devres-packet-alignment.py`.",
        "blocked `phase13-devres-live-dmam-alloc-side-effects`",
        "blocked `phase13-devres-live-scatterlist-ownership`",
        "blocked `phase13-devres-live-sg-table-lifecycle`",
        "blocked `phase13-devres-generic-dma-map-family`",
        "blocked `phase13-devres-missing-devm-ioremap-np-surface`",
        "blocked `phase13-devres-broader-direct-helper-packet`",
    ],
    SLICE: [
        "`zigux/tests/phase13_devres_dma_coherent.zig` plus `Documentation/zigux/phase13-devres-dmam-alloc-coherent-planner.md`, `lib/devres_scatterlist.zig`, and `zigux/tests/phase13_devres_scatterlist.zig` keep the current packet helper-first and planning-only",
        "`scripts/zigux/check-phase13-devres-packet-alignment.py`",
        "the older direct devres replay, reviewability gate, manifest-backed packet, and packet-alignment checker remain repo-reality gaps",
        "the broader direct helper packet stays an explicit repo-reality gap",
    ],
    DMAM_NOTE: [
        "lands one pure `dmam_alloc_coherent()` planning surface in `lib/devres.zig`",
        "routes `planManagedDmamAllocCoherent(...)` through `planManagedReleaseRecordLifetime(...)`",
        "routes `planManagedDmamFreeCoherent(...)` through one private `planReleaseCall(...)` helper",
        "retains detach-time cleanup ownership on success",
        "failed allocation frees the release record",
        "`zigux/tests/phase13_devres_dma_coherent.zig` remains adjacent boundary evidence only",
        "does not claim live DMA allocation side effects",
        "dma_map_sgtable()",
        "struct scatterlist",
        "sg_table",
    ],
    SCATTERLIST_NOTE: [
        "lands one pure scatterlist lifetime planning surface in `lib/devres_scatterlist.zig`",
        "routes `planManagedScatterlistMap(...)` through one helper-local release-record outcome",
        "retains detach-time unmap ownership on success",
        "failed mapping frees the release record",
        "routes `planManagedScatterlistUnmap(...)` through exact original-entry and mapped-entry matching",
        "exposes `scatterlistReleaseMatches(...)` as the helper-first exact-match check",
        "`zigux/tests/phase13_devres_dma_coherent.zig` remains adjacent boundary evidence only",
        "sg_alloc_table()",
        "dma_map_sgtable()",
        "sg_table",
    ],
    DMAM_MANIFEST: [
        '"lane_key": "P13-L08"',
        '"packet": "phase13-devres-dmam-alloc-coherent-planner"',
        '"status": "starter_landed"',
        '"detach_cleanup_owner": "zigux/tests/phase13_devres_dmam_alloc_coherent_planner.zig"',
        '"id": "phase13-devres-live-dmam-alloc-side-effects"',
        '"status": "blocked_on_dma_state"',
        '"id": "phase13-devres-live-scatterlist-ownership"',
        '"status": "blocked_on_scatterlist_state"',
    ],
    SCATTERLIST_MANIFEST: [
        '"lane_key": "P13-L08"',
        '"packet": "phase13-devres-scatterlist-planner"',
        '"status": "starter_landed"',
        '"release_match_owner": "zigux/tests/phase13_devres_scatterlist.zig"',
        '"id": "phase13-devres-live-scatterlist-ownership"',
        '"status": "blocked_on_scatterlist_state"',
        '"id": "phase13-devres-live-sg-table-lifecycle"',
        '"status": "blocked_on_sg_table_lifecycle"',
        '"id": "phase13-devres-generic-dma-map-family"',
        '"status": "blocked_on_dma_mapping_state"',
    ],
    DMA_REPLAY: [
        'test "phase13 devres dma coherent replay records blocked dma and scatterlist boundaries"',
        'test "phase13 devres dma coherent replay proves lib/devres stays planning-only at the boundary"',
        'test "phase13 devres dma coherent replay keeps missing checker surfaces framed as gaps"',
        'test "phase13 devres dma coherent replay anchors the survey-side scatterlist boundary"',
        'test "phase13 devres dma coherent replay keeps scatterlist helper evidence helper-first"',
    ],
}

FORBIDDEN_MARKERS = {
    SURVEY: [
        "current `master` now ships `zigux/tests/phase13_devres.zig`",
        "current `master` now ships `zigux/tests/phase13_devres_reviewability.zig`",
        "current `master` now ships `zigux/tests/phase13_devres_manifest.json`",
        "current `master` now ships `scripts/zigux/check-phase13-devres-packet-alignment.py`",
    ],
    SLICE: [
        "the older direct devres replay, reviewability gate, manifest-backed packet, and packet-alignment checker now ship on current `master`",
    ],
}


def read_text(root: Path, relpath: str) -> str:
    path = root / relpath
    if not path.exists():
        raise SystemExit(f"required file missing: {relpath}")
    return path.read_text(encoding="utf-8")


def write_text(root: Path, relpath: str, content: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []
    for relpath, markers in REQUIRED_MARKERS.items():
        try:
            text = read_text(root, relpath)
        except SystemExit as exc:
            issues.append(str(exc))
            continue

        for marker in markers:
            if marker not in text:
                issues.append(f"missing_marker:{relpath}:{marker}")

    for relpath, markers in FORBIDDEN_MARKERS.items():
        try:
            text = read_text(root, relpath)
        except SystemExit:
            continue

        for marker in markers:
            if marker in text:
                issues.append(f"forbidden_marker:{relpath}:{marker}")

    return issues


def emit_issues(issues: list[str]) -> int:
    print("PHASE13_DEVRES_PLANNER_BOUNDARY_PACKET=fail")
    print("PHASE13_DEVRES_PLANNER_BOUNDARY_PACKET_ISSUES_START")
    for issue in issues:
        print(issue)
    print("PHASE13_DEVRES_PLANNER_BOUNDARY_PACKET_ISSUES_END")
    return 1


def populate_sample_root(root: Path) -> None:
    for relpath, markers in REQUIRED_MARKERS.items():
        write_text(root, relpath, "\n".join(markers) + "\n")


def run_self_test() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="phase13-devres-planner-boundary-"))
    checks_run = 0
    try:
        populate_sample_root(tempdir)
        assert collect_issues(tempdir) == []
        checks_run += 1

        survey_path = tempdir / SURVEY
        survey_path.write_text(
            survey_path.read_text(encoding="utf-8").replace(
                "blocked `phase13-devres-live-sg-table-lifecycle`\n", "", 1
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "missing_marker:Documentation/zigux/phase13-devres-survey.md:blocked `phase13-devres-live-sg-table-lifecycle`"
            in issues
        )
        populate_sample_root(tempdir)
        checks_run += 1

        manifest_path = tempdir / DMAM_MANIFEST
        manifest_path.write_text(
            manifest_path.read_text(encoding="utf-8").replace(
                '"status": "blocked_on_dma_state"\n', "", 1
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            'missing_marker:zigux/tests/phase13_devres_dmam_alloc_coherent_planner_manifest.json:"status": "blocked_on_dma_state"'
            in issues
        )
        populate_sample_root(tempdir)
        checks_run += 1

        replay_path = tempdir / DMA_REPLAY
        replay_path.write_text(
            replay_path.read_text(encoding="utf-8").replace(
                'test "phase13 devres dma coherent replay anchors the survey-side scatterlist boundary"\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            'missing_marker:zigux/tests/phase13_devres_dma_coherent.zig:test "phase13 devres dma coherent replay anchors the survey-side scatterlist boundary"'
            in issues
        )
        populate_sample_root(tempdir)
        checks_run += 1

        slice_path = tempdir / SLICE
        slice_path.write_text(
            slice_path.read_text(encoding="utf-8")
            + "the older direct devres replay, reviewability gate, manifest-backed packet, and packet-alignment checker now ship on current `master`\n",
            encoding="utf-8",
        )
        issues = collect_issues(tempdir)
        assert (
            "forbidden_marker:Documentation/zigux/phase13-devres-slice.md:the older direct devres replay, reviewability gate, manifest-backed packet, and packet-alignment checker now ship on current `master`"
            in issues
        )
        checks_run += 1
    finally:
        shutil.rmtree(tempdir)

    print("PHASE13_DEVRES_PLANNER_BOUNDARY_PACKET_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_PLANNER_BOUNDARY_PACKET_SELF_TEST_CASES={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the live Phase 13 devres planner-and-survey packet aligned."
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--write-sample-root", type=Path)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        if args.write_sample_root.exists():
            shutil.rmtree(args.write_sample_root)
        args.write_sample_root.mkdir(parents=True, exist_ok=True)
        populate_sample_root(args.write_sample_root)
        print(
            "PHASE13_DEVRES_PLANNER_BOUNDARY_PACKET_SAMPLE_ROOT="
            f"{args.write_sample_root}"
        )
        return 0

    issues = collect_issues(args.repo_root)
    if issues:
        return emit_issues(issues)

    print("PHASE13_DEVRES_PLANNER_BOUNDARY_PACKET=pass")
    print(f"PHASE13_DEVRES_PLANNER_BOUNDARY_PACKET_FILE_COUNT={len(REQUIRED_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
