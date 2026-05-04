#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
BUILD_TEST_NAME_RE = re.compile(r'\.name = "(phase13-[^"]+)"')
BUILD_DEPEND_STEP_RE = re.compile(r"test_step\.dependOn\(&([A-Za-z0-9_]+)\.step\);")
SURVEYED_COMMIT_RE = re.compile(r"[0-9a-f]{40}")

SHARED_REPLAY_STEPS = [
    "phase13-libfs-tests",
    "phase13-devres-tests",
    "phase13-devres-dma-coherent-tests",
    "phase13-devres-scatterlist-tests",
    "phase13-devres-iounmap-reviewability-tests",
    "phase13-devres-iomap-reviewability-tests",
    "phase13-landlock-ruleset-tests",
    "phase13-landlock-ruleset-reviewability-tests",
    "phase13-landlock-syscalls-tests",
    "phase13-landlock-syscalls-reviewability-tests",
    "phase13-landlock-ruleset-fops-sync-tests",
    "phase13-libfs-reviewability-tests",
    "phase13-devres-reviewability-tests",
    "phase13-devres-wrapper-reviewability-tests",
    "phase13-notifier-list-reviewability-tests",
    "phase13-notifier-chain-view-tests",
]

FILES = [
    "scripts/zigux/validate-phase13-release.py",
    "scripts/zigux/check-phase13-libfs-packet.py",
    "scripts/zigux/check-phase13-devres-packet.py",
    "scripts/zigux/check-phase13-devres-inventory-contract.py",
    "scripts/zigux/check-phase13-notifier-packet.py",
    "scripts/zigux/check-phase13-release-replay-exact-counts.py",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-devres-survey.md",
    "Documentation/zigux/phase13-devres-scatterlist-slice.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_libfs_manifest.json",
    "zigux/tests/phase13_devres_manifest.json",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/tests/phase13_libfs.zig",
    "zigux/tests/phase13_libfs_reviewability.zig",
    "zigux/tests/phase13_devres.zig",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "zigux/tests/phase13_devres_scatterlist.zig",
    "zigux/tests/phase13_devres_iounmap_reviewability.zig",
    "zigux/tests/phase13_devres_iomap_reviewability.zig",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13_devres_wrapper_reviewability.zig",
    "zigux/tests/phase13_landlock_ruleset.zig",
    "zigux/tests/phase13_landlock_ruleset_reviewability.zig",
    "zigux/tests/phase13_landlock_ruleset_fops_sync.zig",
    "zigux/tests/phase13_landlock_syscalls.zig",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
    "zigux/tests/phase13_notifier_list_reviewability.zig",
    "zigux/bindings/notifier_abi.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
]

MAKE_MARKERS = [
    "PHONY += phase13-validate phase13-test phase13",
    "phase13-validate:",
    "scripts/zigux/check-phase13-release-replay-exact-counts.py --self-test",
    "scripts/zigux/check-phase13-release-replay-exact-counts.py",
    "scripts/zigux/validate-phase13-release.py",
    "phase13-test:",
    "$(ZIG) build test --build-file zigux/tests/phase13_build.zig --summary all",
    "phase13: phase13-validate phase13-test",
]

WORKFLOW_MARKERS = [
    "Validate Phase 13 release-discipline packet",
    "make -C zigux phase13-validate",
    "Run Phase 13 shared helper tests",
    "zig build test --build-file zigux/tests/phase13_build.zig --summary all",
]

RELEASE_MARKERS = [
    "PHASE13_STATUS=active",
    "PHASE13_TRANCHE=shared-helper-bundle",
    "PHASE13_RELEASE_SURVEY=present",
    "PHASE13_RELEASE_VALIDATOR=present",
    "PHASE13_ROADMAP_ANCHOR_COUNT=4",
    "PHASE13_MANIFEST_BACKED_SURVEY_COUNT=4",
    "PHASE13_ACTIVE_ASYMMETRIC_ANCHOR_COUNT=0",
    "PHASE13_VALIDATE_SCRIPT=python3 scripts/zigux/validate-phase13-release.py",
    "PHASE13_VALIDATE_ENTRYPOINT=make -C zigux phase13-validate",
    "PHASE13_SHARED_BUILD_PRESENT=yes",
    "PHASE13_SHARED_MAKE_TARGET_PRESENT=yes",
    "PHASE13_SHARED_REPLAY_STEP_COUNT=16",
    "PHASE13_RELEASE_CLOSED=no",
    "zigux/tests/phase13_devres_scatterlist.zig",
    "Documentation/zigux/phase13-devres-scatterlist-slice.md",
    "phase13-devres-scatterlist-tests",
    "helper-first scatterlist bookkeeping replay visible",
]

TRACEABILITY_MARKERS = [
    "adjacent scatterlist helper: `lib/devres_scatterlist.zig`",
    "adjacent scatterlist replay: `zigux/tests/phase13_devres_scatterlist.zig`",
    "adjacent scatterlist slice note: `Documentation/zigux/phase13-devres-scatterlist-slice.md`",
    "the same manifest-backed packet now also records the already-landed helper-first scatterlist bookkeeping slice",
]

DEVRES_SURVEY_MARKERS = [
    "# Phase 13 devres helper DMA/scatterlist boundary survey",
    "helper-first iomap or resource planners plus explicit DMA/scatterlist blockers pinned to the current repo state",
    "the manifest-backed devres packet now names that same scatterlist slice in `zigux/tests/phase13_devres_manifest.json` and `zigux/tests/phase13_build.zig`",
    "live DMA-backed helpers such as `dmam_alloc_coherent()`, `dmam_free_coherent()`, `dma_map_resource()`, `dma_unmap_resource()`, or `dma_map_sgtable()` ownership and execution",
    "live scatter-gather ownership such as `struct scatterlist`, `sg_table`, `sg_*` iteration, merge, or detach-time cleanup behavior",
]

DEVRES_MANIFEST_GAP_EXPECTATIONS = [
    ("phase13-devres-live-dma-mappings", "blocked_on_dma_state"),
    ("phase13-devres-live-scatterlist-ownership", "blocked_on_scatterlist_state"),
]


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str) -> dict[str, object]:
    return json.loads(text(path))


def require_marker(missing: list[str], label: str, source: str, marker: str) -> None:
    if marker not in source:
        missing.append(f"{label}:{marker}")


def main() -> int:
    missing_files = [path for path in FILES if not (ROOT / path).exists()]
    if missing_files:
        print("PHASE13_RELEASE_VALIDATION=fail")
        print("MISSING_PHASE13_RELEASE_FILES_START")
        for path in missing_files:
            print(path)
        print("MISSING_PHASE13_RELEASE_FILES_END")
        return 1

    missing: list[str] = []

    make_text = text("zigux/Makefile")
    workflow_text = text(".github/workflows/zigux-bootstrap.yml")
    release_text = text("Documentation/zigux/phase13-release-notes-survey.md")
    traceability_text = text("Documentation/zigux/phase13-roadmap-traceability.md")
    devres_survey_text = text("Documentation/zigux/phase13-devres-survey.md")
    build_text = text("zigux/tests/phase13_build.zig")

    for marker in MAKE_MARKERS:
        require_marker(missing, "make", make_text, marker)
    for marker in WORKFLOW_MARKERS:
        require_marker(missing, "workflow", workflow_text, marker)
    for marker in RELEASE_MARKERS:
        require_marker(missing, "release", release_text, marker)
    for marker in TRACEABILITY_MARKERS:
        require_marker(missing, "traceability", traceability_text, marker)
    for marker in DEVRES_SURVEY_MARKERS:
        require_marker(missing, "devres_survey", devres_survey_text, marker)

    build_names = BUILD_TEST_NAME_RE.findall(build_text)
    if build_names != SHARED_REPLAY_STEPS:
        missing.append("build:test_name_sequence")
    depend_steps = BUILD_DEPEND_STEP_RE.findall(build_text)
    if len(depend_steps) != len(SHARED_REPLAY_STEPS):
        missing.append(f"build:depend_step_count={len(depend_steps)}")

    for step in SHARED_REPLAY_STEPS:
        require_marker(missing, "release_step", release_text, f"- `{step}`")

    devres_manifest = load_json("zigux/tests/phase13_devres_manifest.json")
    if devres_manifest.get("phase") != "Phase 13":
        missing.append("devres_manifest:phase")
    if devres_manifest.get("lane_key") != "P13-L10":
        missing.append("devres_manifest:lane_key")
    if devres_manifest.get("anchor") != "lib/devres.c":
        missing.append("devres_manifest:anchor")

    summary = devres_manifest.get("survey_summary")
    if not isinstance(summary, dict):
        missing.append("devres_manifest:survey_summary")
    else:
        for key in [
            "preexisting_phase13_build_present",
            "preexisting_phase13_make_target_present",
            "preexisting_devres_scatterlist_zig_present",
            "preexisting_phase13_devres_scatterlist_test_present",
            "preexisting_phase13_devres_scatterlist_slice_present",
            "preexisting_phase13_devres_dma_coherent_test_present",
            "preexisting_phase13_devres_iounmap_reviewability_present",
            "preexisting_phase13_devres_iomap_reviewability_present",
        ]:
            if summary.get(key) is not True:
                missing.append(f"devres_manifest:{key}")

    gaps = devres_manifest.get("gaps", [])
    for gap_id, status in DEVRES_MANIFEST_GAP_EXPECTATIONS:
        if not any(isinstance(gap, dict) and gap.get("id") == gap_id and gap.get("status") == status for gap in gaps):
            missing.append(f"devres_manifest:{gap_id}:{status}")

    devres_surveyed_commit = devres_manifest.get("surveyed_commit")
    if not isinstance(devres_surveyed_commit, str) or SURVEYED_COMMIT_RE.fullmatch(devres_surveyed_commit) is None:
        missing.append("devres_manifest:surveyed_commit")
    else:
        require_marker(missing, "devres_survey", devres_survey_text, f"- `PHASE13_SURVEYED_COMMIT={devres_surveyed_commit}`")
        require_marker(missing, "traceability", traceability_text, f"- manifest `surveyed_commit`: `{devres_surveyed_commit}`")

    libfs_manifest = load_json("zigux/tests/phase13_libfs_manifest.json")
    ruleset_manifest = load_json("zigux/tests/phase13_landlock_ruleset_manifest.json")
    syscalls_manifest = load_json("zigux/tests/phase13_landlock_syscalls_manifest.json")
    notifier_manifest = load_json("zigux/tests/phase13_notifier_list_manifest.json")

    expected_manifest_heads = [
        (libfs_manifest, "P13-L04", "fs/libfs.c", "phase13_libfs_manifest.json"),
        (ruleset_manifest, "P13-L12", "security/landlock/ruleset.c", "phase13_landlock_ruleset_manifest.json"),
        (syscalls_manifest, "P13-L16", "security/landlock/syscalls.c", "phase13_landlock_syscalls_manifest.json"),
        (notifier_manifest, "P13-L19", None, "phase13_notifier_list_manifest.json"),
    ]
    for manifest, lane_key, anchor, label in expected_manifest_heads:
        if manifest.get("phase") != "Phase 13":
            missing.append(f"{label}:phase")
        if manifest.get("lane_key") != lane_key:
            missing.append(f"{label}:lane_key")
        if anchor is not None and manifest.get("anchor") != anchor:
            missing.append(f"{label}:anchor")

    notifier_summary = notifier_manifest.get("survey_summary")
    if not isinstance(notifier_summary, dict):
        missing.append("phase13_notifier_list_manifest.json:survey_summary")
    else:
        for key in [
            "landed_generic_notifier_abi_present",
            "landed_generic_notifier_build_surface_present",
            "landed_generic_notifier_helper_present",
            "landed_generic_notifier_c_header_surface_present",
        ]:
            if notifier_summary.get(key) is not True:
                missing.append(f"phase13_notifier_list_manifest.json:{key}")

    if missing:
        print("PHASE13_RELEASE_VALIDATION=fail")
        print("PHASE13_RELEASE_VALIDATION_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE13_RELEASE_VALIDATION_MISSING_END")
        return 1

    print("PHASE13_RELEASE_VALIDATION=pass")
    print(f"PHASE13_RELEASE_REQUIRED_FILE_COUNT={len(FILES)}")
    print(f"PHASE13_RELEASE_BUILD_TEST_COUNT={len(build_names)}")
    print(f"PHASE13_RELEASE_BUILD_DEPEND_STEP_COUNT={len(depend_steps)}")
    print(f"PHASE13_RELEASE_SHARED_REPLAY_STEP_COUNT={len(SHARED_REPLAY_STEPS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())