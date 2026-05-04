#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


SURVEYED_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

REQUIRED_FILES = [
    "lib/devres.zig",
    "lib/devres_dma_coherent.zig",
    "lib/devres_scatterlist.zig",
    "zigux/tests/phase13_devres.zig",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "zigux/tests/phase13_devres_scatterlist.zig",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13_devres_wrapper_reviewability.zig",
    "zigux/tests/phase13_devres_iounmap_reviewability.zig",
    "zigux/tests/phase13_devres_iomap_reviewability.zig",
    "zigux/tests/phase13_devres_manifest.json",
    "zigux/tests/phase13_build.zig",
    "Documentation/zigux/phase13-devres-slice.md",
    "Documentation/zigux/phase13-devres-scatterlist-slice.md",
    "Documentation/zigux/phase13-devres-survey.md",
    "scripts/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
]

DEVRES_MARKERS = [
    "provides_ioremap_resource_plain_wrapper_planning: bool,",
    "provides_arch_phys_wc_token_planning: bool,",
    "provides_arch_io_wc_memtype_planning: bool,",
    "touches_live_dma: bool,",
    "touches_live_scatterlist: bool,",
    "pub fn planManagedIoremapResourcePlain(",
    "pub fn planArchPhysWcAdd(",
    "pub fn planArchIoReserveMemtypeWc(",
]

DMA_COHERENT_MARKERS = [
    "provides_dma_coherent_lifetime_planning: bool,",
    "touches_live_dma: bool,",
    "touches_live_scatterlist: bool,",
    "pub fn planManagedDmaCoherentAlloc(",
    "pub fn planManagedDmaCoherentFree(",
]

SCATTERLIST_MARKERS = [
    "provides_scatterlist_lifetime_planning: bool,",
    "touches_live_dma: bool,",
    "touches_live_scatterlist: bool,",
    "pub fn planManagedScatterlistMap(",
    "pub fn planManagedScatterlistUnmap(",
]

DEVRES_TEST_MARKERS = [
    'test "phase13 devres plans a plain managed ioremap resource wrapper"',
    'test "phase13 devres propagates plain managed resource wrapper failures"',
    'test "phase13 devres plans devm_of_iomap around translated resources and optional size reporting"',
    "planManagedIoremapResourcePlain(",
]

DMA_COHERENT_TEST_MARKERS = [
    'test "phase13 devres descriptor records helper-first dma coherent planning"',
    "planManagedDmaCoherentAlloc(",
    "planManagedDmaCoherentFree(",
]

SCATTERLIST_TEST_MARKERS = [
    'test "phase13 devres descriptor records helper-first scatterlist planning"',
    'test "phase13 devres retains the release record when helper-first scatterlist planning succeeds"',
    'test "phase13 devres scatterlist release matching stays exact across original and mapped counts"',
    "planManagedScatterlistMap(",
    "planManagedScatterlistUnmap(",
]

WRAPPER_REVIEWABILITY_MARKERS = [
    'test "phase13 devres direct ioremap wrapper family stays explicit and individually covered"',
    'try expectContains(devres_source, "pub fn planManagedIoremapAcquirePlain(");',
    'try expectContains(devres_source, "pub fn planManagedIoremapAcquireUc(");',
    'try expectContains(devres_source, "pub fn planManagedIoremapAcquireWc(");',
    'try expectContains(devres_source, "pub fn planManagedIoremapAcquireNp(");',
    'try expectContains(phase13_build, "phase13_devres_wrapper_reviewability.zig");',
    'try expectContains(phase13_build, "phase13-devres-wrapper-reviewability-tests");',
]

IOUNMAP_REVIEWABILITY_MARKERS = [
    'test "phase13 devres iounmap descriptor keeps the planner explicit"',
    'test "phase13 devres iounmap planner stays pointer-exact and warns on release misses"',
    ".provides_iounmap_call_planning = true",
    "pub fn planManagedIounmap(",
]

IOMAP_REVIEWABILITY_MARKERS = [
    'test "phase13 devres of_iomap descriptor keeps the planner explicit"',
    'test "phase13 devres of_iomap planner keeps translated size explicit on success"',
    'test "phase13 devres of_iomap planner rejects address-translation misses before managed remap"',
    'test "phase13 devres of_iomap planner preserves translated size on downstream remap failure"',
    'try expectContains(devres_source, ".provides_of_iomap_planning = true");',
    'try expectContains(devres_source, "pub fn planDeviceTreeIomap(");',
]

REVIEWABILITY_MARKERS = [
    'test "phase13 devres manifest records the current helper boundary and explicit dma/scatterlist blockers"',
    'try std.testing.expect(!descriptor.touches_live_dma);',
    'try std.testing.expect(!descriptor.touches_live_scatterlist);',
    'try std.testing.expectEqual(@as(usize, 1), blocked_live_mmio_count);',
    'try std.testing.expectEqual(@as(usize, 1), blocked_dma_count);',
    'try std.testing.expectEqual(@as(usize, 1), blocked_scatterlist_count);',
    'try std.testing.expect(saw_live_mmio_blocker);',
    'try std.testing.expect(saw_dma_blocker);',
    'try std.testing.expect(saw_scatterlist_blocker);',
]

SURVEY_MARKERS = [
    "# Phase 13 devres helper DMA/scatterlist boundary survey",
    "- `PHASE13_STATUS=active`",
    "- `PHASE13_SLICE=devres-helper-dma-scatterlist-boundary-reviewability`",
    "helper-first iomap or resource planners plus explicit DMA/scatterlist blockers pinned to the current repo state",
    "- `zigux/tests/phase13_devres_wrapper_reviewability.zig`",
    "- `lib/devres_scatterlist.zig`",
    "- `zigux/tests/phase13_devres_scatterlist.zig`",
    "- `Documentation/zigux/phase13-devres-scatterlist-slice.md`",
    "`zigux/tests/phase13_devres_wrapper_reviewability.zig` now source-scans `lib/devres.zig` for the direct plain, UC, WC, and NP managed ioremap wrapper entrypoints",
    "`zigux/tests/phase13_devres_iounmap_reviewability.zig` now source-scans `lib/devres.zig` for the explicit `provides_iounmap_call_planning` marker and replays exact-match plus release-miss `devm_iounmap()` planning so the pointer-exact detach surface stays reviewable inside the broader devres packet instead of living only in the helper lab or survey prose",
    "the direct plain, UC, WC, and NP managed ioremap wrapper family plus its dedicated survey-visible reviewability gate",
    "live MMIO side effects such as `devres_alloc_node()` ownership, `devres_add()` installation, `devm_request_mem_region()` side effects, and direct `ioremap()` or `iounmap()` execution against real hardware state",
    "live DMA-backed helpers such as `dmam_alloc_coherent()`, `dmam_free_coherent()`, `dma_map_resource()`, `dma_unmap_resource()`, or `dma_map_sgtable()` ownership and execution",
    "live scatter-gather ownership such as `struct scatterlist`, `sg_table`, `sg_*` iteration, merge, or detach-time cleanup behavior",
    "the manifest-backed devres packet now names that same scatterlist slice in `zigux/tests/phase13_devres_manifest.json` and `zigux/tests/phase13_build.zig` so the already-landed helper-first DMA/scatterlist bookkeeping evidence is checked with the rest of the devres packet instead of living only in an adjacent slice note",
]

SURVEY_EXACT_COUNT_MARKERS = {
    "live MMIO side effects such as `devres_alloc_node()` ownership, `devres_add()` installation, `devm_request_mem_region()` side effects, and direct `ioremap()` or `iounmap()` execution against real hardware state": 1,
    "live DMA-backed helpers such as `dmam_alloc_coherent()`, `dmam_free_coherent()`, `dma_map_resource()`, `dma_unmap_resource()`, or `dma_map_sgtable()` ownership and execution": 1,
    "live scatter-gather ownership such as `struct scatterlist`, `sg_table`, `sg_*` iteration, merge, or detach-time cleanup behavior": 1,
}

SLICE_MARKERS = [
    "pure helper-first foothold anchored to `lib/devres.c`",
    "adds one adjacent helper-first coherent DMA lifetime planner in `lib/devres_dma_coherent.zig`",
    "does not expose `dma_map_*`, `dma_unmap_*`, `dma_map_sgtable()`, `struct scatterlist`, `sg_table`, or `sg_*` traversal behavior at all",
    "without widening into live mappings, generic devres groups, or cross-subsystem device-resource state",
]

SCATTERLIST_SLICE_MARKERS = [
    "# Phase 13 devres scatterlist helper slice",
    "`DevresScatterlistHelper.descriptor()` names the same `lib/devres.c` anchor while keeping `touches_live_dma = false` and `touches_live_scatterlist = false`",
    "`planManagedScatterlistMap()` models a helper-first retained-record decision around original segment count, mapped segment count, and detach-time unmap readiness",
    "`planManagedScatterlistUnmap()` keeps the release match exact across original and mapped segment counts so the detach bookkeeping surface stays reviewable",
    "no live `dma_map_sgtable()` or `dma_unmap_sgtable()` execution",
]

BUILD_MARKERS = [
    "../../lib/devres_dma_coherent.zig",
    "../../lib/devres_scatterlist.zig",
    "phase13_devres_dma_coherent.zig",
    "phase13_devres_scatterlist.zig",
    "phase13_devres_wrapper_reviewability.zig",
    "phase13_devres_iounmap_reviewability.zig",
    "phase13_devres_iomap_reviewability.zig",
    "phase13-devres-tests",
    "phase13-devres-dma-coherent-tests",
    "phase13-devres-scatterlist-tests",
    "phase13-devres-wrapper-reviewability-tests",
    "phase13-devres-iounmap-reviewability-tests",
    "phase13-devres-iomap-reviewability-tests",
    "phase13-devres-reviewability-tests",
]

SCRIPTS_README_MARKERS = [
    "that shared Phase 13 release packet keeps `Documentation/zigux/phase13-notifier-list-survey.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, the four roadmap-anchor manifests plus `zigux/tests/phase13_notifier_list_manifest.json`, the direct libfs, devres, coherent-DMA, scatterlist, Landlock ruleset, and Landlock syscalls helper replays, the `iounmap`, `iomap`, wrapper, ruleset-fops-sync, and syscall reviewability gates, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig` visible from the scripts root so the contributor packet names the same validator-first evidence bundle as the tests-root and docs-root guides.",
]

SCRIPTS_README_EXACT_COUNT_MARKERS = {
    "that shared Phase 13 release packet keeps `Documentation/zigux/phase13-notifier-list-survey.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, the four roadmap-anchor manifests plus `zigux/tests/phase13_notifier_list_manifest.json`, the direct libfs, devres, coherent-DMA, scatterlist, Landlock ruleset, and Landlock syscalls helper replays, the `iounmap`, `iomap`, wrapper, ruleset-fops-sync, and syscall reviewability gates, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig` visible from the scripts root so the contributor packet names the same validator-first evidence bundle as the tests-root and docs-root guides.": 1,
}

REVIEW_CHECKLIST_MARKERS = [
    "if the change touches the shared Phase 13 release-discipline packet, do `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_reviewability.zig` still keep the scripts-root devres inventory sentence and its adjacent coherent-DMA, scatterlist, plus reviewability evidence explicit so reviewer guidance does not drift behind the stricter shared validator contract?",
]

REVIEW_CHECKLIST_EXACT_COUNT_MARKERS = {
    "if the change touches the shared Phase 13 release-discipline packet, do `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-devres-scatterlist-slice.md`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_devres_dma_coherent.zig`, `zigux/tests/phase13_devres_scatterlist.zig`, and `zigux/tests/phase13_devres_reviewability.zig` still keep the scripts-root devres inventory sentence and its adjacent coherent-DMA, scatterlist, plus reviewability evidence explicit so reviewer guidance does not drift behind the stricter shared validator contract?": 1,
}

EXPECTED_GAP_STATUS = {
    "phase13-devres-iounmap-reviewability-gate": "starter_landed",
    "phase13-devres-live-mmio-side-effects": "blocked_on_live_mmio_state",
    "phase13-devres-live-dma-mappings": "blocked_on_dma_state",
    "phase13-devres-live-scatterlist-ownership": "blocked_on_scatterlist_state",
    "phase13-devres-managed-resource-planner": "starter_landed",
    "phase13-devres-devicetree-iomap-planner": "starter_landed",
    "phase13-devres-arch-phys-wc-token-planner": "starter_landed",
    "phase13-devres-arch-io-memtype-planner": "starter_landed",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _require_markers(missing: list[str], label: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            missing.append(f"{label}:{marker}")


def _require_exact_counts(
    missing: list[str],
    label: str,
    text: str,
    markers: dict[str, int],
) -> None:
    for marker, expected_count in markers.items():
        actual_count = text.count(marker)
        if actual_count != expected_count:
            missing.append(
                f"{label}:exact_count:{marker}:{actual_count}!={expected_count}"
            )


def _check_repo(root: Path) -> list[str]:
    missing: list[str] = []
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            missing.append(f"missing_file:{rel}")

    if missing:
        return missing

    devres_text = _read(root / "lib/devres.zig")
    dma_coherent_text = _read(root / "lib/devres_dma_coherent.zig")
    scatterlist_text = _read(root / "lib/devres_scatterlist.zig")
    devres_tests_text = _read(root / "zigux/tests/phase13_devres.zig")
    dma_coherent_tests_text = _read(root / "zigux/tests/phase13_devres_dma_coherent.zig")
    scatterlist_tests_text = _read(root / "zigux/tests/phase13_devres_scatterlist.zig")
    reviewability_text = _read(root / "zigux/tests/phase13_devres_reviewability.zig")
    wrapper_reviewability_text = _read(root / "zigux/tests/phase13_devres_wrapper_reviewability.zig")
    iounmap_reviewability_text = _read(root / "zigux/tests/phase13_devres_iounmap_reviewability.zig")
    iomap_reviewability_text = _read(root / "zigux/tests/phase13_devres_iomap_reviewability.zig")
    manifest_text = _read(root / "zigux/tests/phase13_devres_manifest.json")
    build_text = _read(root / "zigux/tests/phase13_build.zig")
    survey_text = _read(root / "Documentation/zigux/phase13-devres-survey.md")
    slice_text = _read(root / "Documentation/zigux/phase13-devres-slice.md")
    scatterlist_slice_text = _read(root / "Documentation/zigux/phase13-devres-scatterlist-slice.md")
    scripts_readme_text = _read(root / "scripts/zigux/README.md")
    review_checklist_text = _read(root / "Documentation/zigux/review-checklist.md")

    _require_markers(missing, "devres", devres_text, DEVRES_MARKERS)
    _require_markers(missing, "devres_dma_coherent", dma_coherent_text, DMA_COHERENT_MARKERS)
    _require_markers(missing, "devres_scatterlist", scatterlist_text, SCATTERLIST_MARKERS)
    _require_markers(missing, "devres_tests", devres_tests_text, DEVRES_TEST_MARKERS)
    _require_markers(missing, "devres_dma_coherent_tests", dma_coherent_tests_text, DMA_COHERENT_TEST_MARKERS)
    _require_markers(missing, "devres_scatterlist_tests", scatterlist_tests_text, SCATTERLIST_TEST_MARKERS)
    _require_markers(missing, "wrapper_reviewability", wrapper_reviewability_text, WRAPPER_REVIEWABILITY_MARKERS)
    _require_markers(missing, "iounmap_reviewability", iounmap_reviewability_text, IOUNMAP_REVIEWABILITY_MARKERS)
    _require_markers(missing, "iomap_reviewability", iomap_reviewability_text, IOMAP_REVIEWABILITY_MARKERS)
    _require_markers(missing, "reviewability", reviewability_text, REVIEWABILITY_MARKERS)
    _require_markers(missing, "survey", survey_text, SURVEY_MARKERS)
    _require_exact_counts(missing, "survey", survey_text, SURVEY_EXACT_COUNT_MARKERS)
    _require_markers(missing, "slice", slice_text, SLICE_MARKERS)
    _require_markers(missing, "scatterlist_slice", scatterlist_slice_text, SCATTERLIST_SLICE_MARKERS)
    _require_markers(missing, "build", build_text, BUILD_MARKERS)
    _require_markers(missing, "scripts_readme", scripts_readme_text, SCRIPTS_README_MARKERS)
    _require_exact_counts(
        missing,
        "scripts_readme",
        scripts_readme_text,
        SCRIPTS_README_EXACT_COUNT_MARKERS,
    )
    _require_markers(
        missing,
        "review_checklist",
        review_checklist_text,
        REVIEW_CHECKLIST_MARKERS,
    )
    _require_exact_counts(
        missing,
        "review_checklist",
        review_checklist_text,
        REVIEW_CHECKLIST_EXACT_COUNT_MARKERS,
    )

    manifest = json.loads(manifest_text)
    if manifest.get("lane_key") != "P13-L10":
        missing.append("manifest:lane_key")
    if manifest.get("phase") != "Phase 13":
        missing.append("manifest:phase")
    if manifest.get("anchor") != "lib/devres.c":
        missing.append("manifest:anchor")

    surveyed_commit = manifest.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not SURVEYED_COMMIT_RE.fullmatch(surveyed_commit):
        missing.append("manifest:surveyed_commit")
    else:
        if f"- `PHASE13_SURVEYED_COMMIT={surveyed_commit}`" not in survey_text:
            missing.append("survey:surveyed_commit")
        if f'try std.testing.expectEqualStrings("{surveyed_commit}", manifest.surveyed_commit);' not in reviewability_text:
            missing.append("reviewability:surveyed_commit")

    survey_summary = manifest.get("survey_summary")
    if not isinstance(survey_summary, dict):
        missing.append("manifest:survey_summary")
    else:
        for key in (
            "preexisting_phase13_build_present",
            "preexisting_phase13_make_target_present",
            "preexisting_devres_zig_present",
            "preexisting_phase13_devres_test_present",
            "preexisting_phase13_devres_slice_present",
            "preexisting_phase13_devres_reviewability_present",
            "preexisting_phase13_devres_wrapper_reviewability_present",
            "preexisting_phase13_devres_iounmap_reviewability_present",
            "preexisting_phase13_devres_iomap_reviewability_present",
            "preexisting_phase13_devres_survey_present",
            "preexisting_devres_dma_coherent_zig_present",
            "preexisting_phase13_devres_dma_coherent_test_present",
            "preexisting_devres_scatterlist_zig_present",
            "preexisting_phase13_devres_scatterlist_test_present",
            "preexisting_phase13_devres_scatterlist_slice_present",
        ):
            if survey_summary.get(key) is not True:
                missing.append(f"manifest:{key}")

    gaps = manifest.get("gaps")
    if not isinstance(gaps, list):
        missing.append("manifest:gaps")
        return missing

    gap_lookup = {
        gap.get("id"): gap.get("status")
        for gap in gaps
        if isinstance(gap, dict) and isinstance(gap.get("id"), str)
    }
    for gap_id, expected_status in EXPECTED_GAP_STATUS.items():
        if gap_lookup.get(gap_id) != expected_status:
            missing.append(f"manifest:{gap_id}:{expected_status}")

    return missing


def _run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for rel in ("lib", "zigux/tests", "Documentation/zigux", "scripts/zigux"):
            (root / rel).mkdir(parents=True, exist_ok=True)

        case_count = 0
        surveyed_commit = "aa01b37be5500e6a1e4f959c9fe07f0e39d39bfb"
        (root / "lib/devres.zig").write_text("\n".join(DEVRES_MARKERS) + "\n", encoding="utf-8")
        (root / "lib/devres_dma_coherent.zig").write_text("\n".join(DMA_COHERENT_MARKERS) + "\n", encoding="utf-8")
        (root / "lib/devres_scatterlist.zig").write_text("\n".join(SCATTERLIST_MARKERS) + "\n", encoding="utf-8")
        (root / "zigux/tests/phase13_devres.zig").write_text("\n".join(DEVRES_TEST_MARKERS) + "\n", encoding="utf-8")
        (root / "zigux/tests/phase13_devres_dma_coherent.zig").write_text("\n".join(DMA_COHERENT_TEST_MARKERS) + "\n", encoding="utf-8")
        (root / "zigux/tests/phase13_devres_scatterlist.zig").write_text("\n".join(SCATTERLIST_TEST_MARKERS) + "\n", encoding="utf-8")
        (root / "zigux/tests/phase13_devres_wrapper_reviewability.zig").write_text(
            "\n".join(WRAPPER_REVIEWABILITY_MARKERS) + "\n",
            encoding="utf-8",
        )
        (root / "zigux/tests/phase13_devres_reviewability.zig").write_text(
            "\n".join(
                [
                    f'try std.testing.expectEqualStrings("{surveyed_commit}", manifest.surveyed_commit);',
                    *REVIEWABILITY_MARKERS,
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (root / "zigux/tests/phase13_devres_iounmap_reviewability.zig").write_text(
            "\n".join(IOUNMAP_REVIEWABILITY_MARKERS) + "\n",
            encoding="utf-8",
        )
        (root / "zigux/tests/phase13_devres_iomap_reviewability.zig").write_text(
            "\n".join(IOMAP_REVIEWABILITY_MARKERS) + "\n",
            encoding="utf-8",
        )
        (root / "Documentation/zigux/phase13-devres-survey.md").write_text(
            f"- `PHASE13_SURVEYED_COMMIT={surveyed_commit}`\n" + "\n".join(SURVEY_MARKERS) + "\n",
            encoding="utf-8",
        )
        (root / "Documentation/zigux/phase13-devres-slice.md").write_text(
            "\n".join(SLICE_MARKERS) + "\n",
            encoding="utf-8",
        )
        (root / "Documentation/zigux/phase13-devres-scatterlist-slice.md").write_text(
            "\n".join(SCATTERLIST_SLICE_MARKERS) + "\n",
            encoding="utf-8",
        )
        (root / "zigux/tests/phase13_build.zig").write_text("\n".join(BUILD_MARKERS) + "\n", encoding="utf-8")
        (root / "scripts/zigux/README.md").write_text(
            "\n".join(SCRIPTS_README_MARKERS) + "\n",
            encoding="utf-8",
        )
        (root / "Documentation/zigux/review-checklist.md").write_text(
            "\n".join(REVIEW_CHECKLIST_MARKERS) + "\n",
            encoding="utf-8",
        )
        manifest = {
            "lane_key": "P13-L10",
            "phase": "Phase 13",
            "surveyed_commit": surveyed_commit,
            "anchor": "lib/devres.c",
            "survey_summary": {
                "preexisting_phase13_build_present": True,
                "preexisting_phase13_make_target_present": True,
                "preexisting_devres_zig_present": True,
                "preexisting_phase13_devres_test_present": True,
                "preexisting_phase13_devres_slice_present": True,
                "preexisting_phase13_devres_reviewability_present": True,
                "preexisting_phase13_devres_wrapper_reviewability_present": True,
                "preexisting_phase13_devres_iounmap_reviewability_present": True,
                "preexisting_phase13_devres_iomap_reviewability_present": True,
                "preexisting_phase13_devres_survey_present": True,
                "preexisting_devres_dma_coherent_zig_present": True,
                "preexisting_phase13_devres_dma_coherent_test_present": True,
                "preexisting_devres_scatterlist_zig_present": True,
                "preexisting_phase13_devres_scatterlist_test_present": True,
                "preexisting_phase13_devres_scatterlist_slice_present": True,
            },
            "gaps": [
                {"id": gap_id, "status": status}
                for gap_id, status in EXPECTED_GAP_STATUS.items()
            ],
        }
        (root / "zigux/tests/phase13_devres_manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )

        missing = _check_repo(root)
        if missing:
            print("PHASE13_DEVRES_PACKET_SELF_TEST=fail")
            for item in missing:
                print(item)
            return 1
        case_count += 1

        duplicate_marker = next(iter(SURVEY_EXACT_COUNT_MARKERS))
        survey_path = root / "Documentation/zigux/phase13-devres-survey.md"
        survey_path.write_text(
            _read(survey_path) + duplicate_marker + "\n",
            encoding="utf-8",
        )
        missing = _check_repo(root)
        expected_missing = (
            f"survey:exact_count:{duplicate_marker}:2!=1"
        )
        if expected_missing not in missing:
            print("PHASE13_DEVRES_PACKET_SELF_TEST=fail")
            print("missing exact-count failure for duplicate survey blocker marker")
            for item in missing:
                print(item)
            return 1
        case_count += 1
        survey_path.write_text(
            f"- `PHASE13_SURVEYED_COMMIT={surveyed_commit}`\n" + "\n".join(SURVEY_MARKERS) + "\n",
            encoding="utf-8",
        )

        scripts_readme_path = root / "scripts/zigux/README.md"
        original_scripts_readme = _read(scripts_readme_path)
        scripts_readme_path.write_text(
            original_scripts_readme + SCRIPTS_README_MARKERS[0] + "\n",
            encoding="utf-8",
        )
        missing = _check_repo(root)
        expected_missing = (
            "scripts_readme:exact_count:"
            + SCRIPTS_README_MARKERS[0]
            + ":2!=1"
        )
        if expected_missing not in missing:
            print("PHASE13_DEVRES_PACKET_SELF_TEST=fail")
            print("missing exact-count failure for duplicate scripts-readme devres marker")
            for item in missing:
                print(item)
            return 1
        case_count += 1
        scripts_readme_path.write_text(original_scripts_readme, encoding="utf-8")

        review_checklist_path = root / "Documentation/zigux/review-checklist.md"
        original_review_checklist = _read(review_checklist_path)
        review_checklist_path.write_text("", encoding="utf-8")
        missing = _check_repo(root)
        expected_missing = "review_checklist:" + REVIEW_CHECKLIST_MARKERS[0]
        if expected_missing not in missing:
            print("PHASE13_DEVRES_PACKET_SELF_TEST=fail")
            print("missing required review-checklist devres marker did not fail")
            for item in missing:
                print(item)
            return 1
        case_count += 1
        review_checklist_path.write_text(original_review_checklist, encoding="utf-8")

        wrapper_reviewability_path = root / "zigux/tests/phase13_devres_wrapper_reviewability.zig"
        wrapper_reviewability_path.write_text("", encoding="utf-8")
        missing = _check_repo(root)
        expected_missing = (
            "wrapper_reviewability:"
            + WRAPPER_REVIEWABILITY_MARKERS[0]
        )
        if expected_missing not in missing:
            print("PHASE13_DEVRES_PACKET_SELF_TEST=fail")
            print("missing wrapper reviewability marker did not fail")
            for item in missing:
                print(item)
            return 1
        case_count += 1
        wrapper_reviewability_path.write_text(
            "\n".join(WRAPPER_REVIEWABILITY_MARKERS) + "\n",
            encoding="utf-8",
        )

    print("PHASE13_DEVRES_PACKET_SELF_TEST=pass")
    print(f"PHASE13_DEVRES_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    if args.self_test:
        return _run_self_test()

    missing = _check_repo(Path(args.root).resolve())
    if missing:
        print("PHASE13_DEVRES_PACKET=fail")
        print("PHASE13_DEVRES_PACKET_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE13_DEVRES_PACKET_MISSING_END")
        return 1

    print("PHASE13_DEVRES_PACKET=pass")
    print(f"PHASE13_DEVRES_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE13_DEVRES_MARKER_COUNT="
        f"{len(DEVRES_MARKERS) + len(DMA_COHERENT_MARKERS) + len(SCATTERLIST_MARKERS) + len(DEVRES_TEST_MARKERS) + len(DMA_COHERENT_TEST_MARKERS) + len(SCATTERLIST_TEST_MARKERS) + len(WRAPPER_REVIEWABILITY_MARKERS) + len(IOUNMAP_REVIEWABILITY_MARKERS) + len(IOMAP_REVIEWABILITY_MARKERS) + len(REVIEWABILITY_MARKERS) + len(SURVEY_MARKERS) + len(SURVEY_EXACT_COUNT_MARKERS) + len(SLICE_MARKERS) + len(SCATTERLIST_SLICE_MARKERS) + len(BUILD_MARKERS) + len(SCRIPTS_README_MARKERS) + len(SCRIPTS_README_EXACT_COUNT_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(REVIEW_CHECKLIST_EXACT_COUNT_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
