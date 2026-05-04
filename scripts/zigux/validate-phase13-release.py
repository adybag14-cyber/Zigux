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

FILES = [
    "scripts/zigux/validate-phase13-release.py",
    "scripts/zigux/check-phase13-libfs-packet.py",
    "scripts/zigux/check-phase13-devres-packet.py",
    "scripts/zigux/check-phase13-devres-inventory-contract.py",
    "scripts/zigux/check-phase13-release-replay-exact-counts.py",
    "scripts/zigux/check-phase13-notifier-packet.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase13-libfs-slice.md",
    "Documentation/zigux/phase13-libfs-survey.md",
    "Documentation/zigux/phase13-devres-slice.md",
    "Documentation/zigux/phase13-devres-survey.md",
    "Documentation/zigux/phase13-landlock-ruleset-slice.md",
    "Documentation/zigux/phase13-landlock-ruleset-survey.md",
    "Documentation/zigux/phase13-landlock-syscalls-slice.md",
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
    "Documentation/zigux/phase13-notifier-list-survey.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_libfs.zig",
    "zigux/tests/phase13_libfs_manifest.json",
    "zigux/tests/phase13_devres.zig",
    "zigux/tests/phase13_devres_manifest.json",
    "zigux/tests/phase13_landlock_ruleset.zig",
    "zigux/tests/phase13_landlock_ruleset_reviewability.zig",
    "zigux/tests/phase13_landlock_ruleset_fops_sync.zig",
    "zigux/tests/phase13_landlock_ruleset_manifest.json",
    "zigux/tests/phase13_landlock_syscalls.zig",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/tests/phase13_notifier_list_manifest.json",
    "zigux/tests/phase13_libfs_reviewability.zig",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "zigux/tests/phase13_devres_iounmap_reviewability.zig",
    "zigux/tests/phase13_devres_iomap_reviewability.zig",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13_devres_wrapper_reviewability.zig",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
    "zigux/tests/phase13_notifier_list_reviewability.zig",
    "zigux/bindings/notifier_abi.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
]

MAKE_MARKERS = [
    "PHONY += phase13-validate phase13-test phase13",
    "phase13-validate:",
    "scripts/zigux/validate-phase13-release.py",
    "phase13-test:",
    "$(ZIG) build test --build-file zigux/tests/phase13_build.zig --summary all",
    "phase13: phase13-validate phase13-test",
]

MAKE_EXACT_COUNT_MARKERS = {
    "phase13-validate:": 1,
    "scripts/zigux/check-phase13-libfs-packet.py --self-test": 1,
    "scripts/zigux/check-phase13-libfs-packet.py\n": 1,
    "scripts/zigux/check-phase13-devres-packet.py --self-test": 1,
    "scripts/zigux/check-phase13-devres-packet.py\n": 1,
    "scripts/zigux/check-phase13-release-replay-exact-counts.py --self-test": 1,
    "scripts/zigux/check-phase13-release-replay-exact-counts.py\n": 1,
    "scripts/zigux/check-phase13-notifier-packet.py --self-test": 1,
    "scripts/zigux/check-phase13-notifier-packet.py\n": 1,
    "scripts/zigux/validate-phase13-release.py": 1,
    "phase13-test:": 1,
    "$(ZIG) build test --build-file zigux/tests/phase13_build.zig --summary all": 1,
    "phase13: phase13-validate phase13-test": 1,
}

WORKFLOW_MARKERS = [
    "Validate Phase 13 release-discipline packet",
    "make -C zigux phase13-validate",
    "Run Phase 13 shared helper tests",
    "zig build test --build-file zigux/tests/phase13_build.zig --summary all",
]

WORKFLOW_EXACT_COUNT_MARKERS = {
    "- name: Validate Phase 13 release-discipline packet": 1,
    "run: make -C zigux phase13-validate": 1,
    "- name: Run Phase 13 shared helper tests": 1,
    "run: zig build test --build-file zigux/tests/phase13_build.zig --summary all": 1,
}

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
    "PHASE13_SHARED_REPLAY_STEP_COUNT=15",
    "PHASE13_RELEASE_CLOSED=no",
    "The current release packet also carries one active Phase 13 boundary reminder on `master`:",
    "`python3 scripts/zigux/validate-phase13-release.py`, `make -C zigux phase13-validate`, `zig build test --build-file zigux/tests/phase13_build.zig --summary all`, and `make -C zigux phase13` are the published validator-first and shared replay path for the current packet",
    "the shared release packet also keeps the dedicated `scripts/zigux/check-phase13-devres-packet.py` guard visible as part of that published review path, so the stricter helper-first `devres` boundary contract is not left implicit in `zigux/Makefile` alone",
    "the shared release packet now also keeps the dedicated `phase13-devres-iounmap-reviewability-tests` gate visible through `zigux/tests/phase13_devres_iounmap_reviewability.zig` so the helper-advertised `devm_iounmap()` planning surface does not look smaller than the actual shared replay on current `master`",
    "the shared release packet now also keeps the dedicated `phase13-devres-iomap-reviewability-tests` gate visible through `zigux/tests/phase13_devres_iomap_reviewability.zig` so the helper-advertised `devm_of_iomap()` planning surface does not look smaller than the actual shared replay on current `master`",
    "the shared release packet now also keeps the dedicated `phase13-devres-wrapper-reviewability-tests` gate visible through `zigux/tests/phase13_devres_wrapper_reviewability.zig` so the direct plain, uncached, write-combined, and non-posted managed `devres` ioremap wrapper family does not look smaller than the actual shared replay on current `master`",
    "the shared release packet now also keeps the dedicated `phase13-landlock-ruleset-fops-sync-tests` gate visible through `zigux/tests/phase13_landlock_ruleset_fops_sync.zig` so the ruleset-fd creation and explicit fops planning surface does not look smaller than the actual shared replay on current `master`",
    "the earlier `expected statement, found 'EOF'` note for `zigux/tests/phase13_landlock_ruleset.zig` is now historical: the current checked-in ruleset test file is syntactically complete, its dedicated ruleset helper replay still passes against `security/landlock/ruleset.zig`, and the broader shared replay has already been rerun successfully on `master`",
    "the remaining live ruleset blocker is the same one already recorded by the manifest-backed survey packet: `rb_replace_node()`, live object ownership transfer, hierarchy lifetime, and workqueue-backed teardown are still outside the current helper-only lane",
    "The current manifest lane ownership carried by the release packet is:",
    "`fs/libfs.c` through `zigux/tests/phase13_libfs_manifest.json` lane `P13-L04`",
    "`lib/devres.c` through `zigux/tests/phase13_devres_manifest.json` lane `P13-L10`",
    "`security/landlock/ruleset.c` through `zigux/tests/phase13_landlock_ruleset_manifest.json` lane `P13-L12`",
    "`security/landlock/syscalls.c` through `zigux/tests/phase13_landlock_syscalls_manifest.json` lane `P13-L16`",
    "adjacent notifier-list reviewability evidence through `zigux/tests/phase13_notifier_list_manifest.json` lane `P13-L19`",
    "Shared helper sequencing on top of those manifest-owner keys is now:",
    "`fs/libfs.c`: keep `P13-L01` narrowed to libfs survey-local or traceability-local drift now that `generic_check_addressable()` is already landed, and keep `P13-L03` verification-only unless a real packet-alignment failure or focused libfs replay regression appears",
    "`lib/devres.c`: keep helper expansion parked behind `P13-L06` until a concrete exported-helper gap appears, and keep `P13-L07` verification-only unless a focused devres replay fails or a helper-local regression surfaces",
    "`security/landlock/ruleset.c`: keep the remaining helper-only boundary work, if any, under `P13-L12` and do not reopen it from shared release notes unless the manifest-backed packet or shared replay drifts",
    "`security/landlock/syscalls.c`: keep `P13-L16` narrowed to packet drift or tiny validation-only cleanup and do not widen it from the shared release packet into new syscall helper scope",
    "shared release-discipline or docs-root follow-up should stay note-local and should not consume helper-local work already assigned to those narrower same-family lanes",
    "the adjacent notifier-list packet now stays visible as roadmap-adjacent release evidence, and its shared replay surface includes the landed read-only generic notifier foothold through `zigux/bindings/notifier_abi.zig`, the dedicated exported C header `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig`",
    "lib/devres.c`: helper slice landed, dedicated tests present, roadmap traceability present, manifest-backed survey present, and helper-first MMIO or resource planners keep live DMA-backed mappings and scatterlist ownership explicitly blocked",
    "the shared replay now also keeps the adjacent helper-first coherent DMA alloc/free bookkeeping replay visible through `phase13-devres-dma-coherent-tests` without turning the blocked devres DMA/scatterlist boundary into a live DMA-backed mapping claim",
    "the shared replay now also keeps the dedicated `phase13-devres-iounmap-reviewability-tests` gate visible through `zigux/tests/phase13_devres_iounmap_reviewability.zig` so the helper-advertised `devm_iounmap()` planning surface does not look smaller than the actual shared replay on current `master`",
    "the shared replay now also keeps the dedicated `phase13-devres-wrapper-reviewability-tests` gate visible through `zigux/tests/phase13_devres_wrapper_reviewability.zig` so the direct plain, uncached, write-combined, and non-posted managed `devres` ioremap wrapper family does not look smaller than the actual shared replay on current `master`",
    "the shared replay now also keeps the dedicated Landlock ruleset reviewability gate visible through `phase13-landlock-ruleset-reviewability-tests` so the manifest-backed ruleset helper packet does not look smaller than the actual published replay on current `master`",
    "the shared replay now also keeps the dedicated `phase13-landlock-ruleset-fops-sync-tests` gate visible through `zigux/tests/phase13_landlock_ruleset_fops_sync.zig` so the ruleset-fd creation and explicit fops planning surface does not look smaller than the actual shared replay on current `master`",
    "the shared replay now also keeps the dedicated Landlock syscall reviewability gate visible through `phase13-landlock-syscalls-reviewability-tests` so the manifest-backed syscall helper packet does not look smaller than the actual published replay on current `master`",
    "phase13_notifier_list_reviewability.zig",
    "zig build test --build-file zigux/tests/phase13_build.zig --summary all",
]

RELEASE_EXACT_COUNT_MARKERS = {
    "`python3 scripts/zigux/validate-phase13-release.py`, `make -C zigux phase13-validate`, `zig build test --build-file zigux/tests/phase13_build.zig --summary all`, and `make -C zigux phase13` are the published validator-first and shared replay path for the current packet": 1,
    "the shared release packet also keeps the dedicated `scripts/zigux/check-phase13-devres-packet.py` guard visible as part of that published review path, so the stricter helper-first `devres` boundary contract is not left implicit in `zigux/Makefile` alone": 1,
    "the shared release packet now also keeps the dedicated `phase13-devres-iounmap-reviewability-tests` gate visible through `zigux/tests/phase13_devres_iounmap_reviewability.zig` so the helper-advertised `devm_iounmap()` planning surface does not look smaller than the actual shared replay on current `master`": 1,
    "the shared release packet now also keeps the dedicated `phase13-devres-iomap-reviewability-tests` gate visible through `zigux/tests/phase13_devres_iomap_reviewability.zig` so the helper-advertised `devm_of_iomap()` planning surface does not look smaller than the actual shared replay on current `master`": 1,
    "the shared release packet now also keeps the dedicated `phase13-devres-wrapper-reviewability-tests` gate visible through `zigux/tests/phase13_devres_wrapper_reviewability.zig` so the direct plain, uncached, write-combined, and non-posted managed `devres` ioremap wrapper family does not look smaller than the actual shared replay on current `master`": 1,
    "the shared release packet now also keeps the dedicated `phase13-landlock-ruleset-fops-sync-tests` gate visible through `zigux/tests/phase13_landlock_ruleset_fops_sync.zig` so the ruleset-fd creation and explicit fops planning surface does not look smaller than the actual shared replay on current `master`": 1,
    "the earlier `expected statement, found 'EOF'` note for `zigux/tests/phase13_landlock_ruleset.zig` is now historical: the current checked-in ruleset test file is syntactically complete, its dedicated ruleset helper replay still passes against `security/landlock/ruleset.zig`, and the broader shared replay has already been rerun successfully on `master`": 1,
    "the remaining live ruleset blocker is the same one already recorded by the manifest-backed survey packet: `rb_replace_node()`, live object ownership transfer, hierarchy lifetime, and workqueue-backed teardown are still outside the current helper-only lane": 1,
    "the adjacent notifier-list packet now stays visible as roadmap-adjacent release evidence, and its shared replay surface includes the landed read-only generic notifier foothold through `zigux/bindings/notifier_abi.zig`, the dedicated exported C header `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig`": 1,
    "the shared replay now also keeps the adjacent helper-first coherent DMA alloc/free bookkeeping replay visible through `phase13-devres-dma-coherent-tests` without turning the blocked devres DMA/scatterlist boundary into a live DMA-backed mapping claim": 1,
    "the shared replay now also keeps the dedicated `phase13-devres-iounmap-reviewability-tests` gate visible through `zigux/tests/phase13_devres_iounmap_reviewability.zig` so the helper-advertised `devm_iounmap()` planning surface does not look smaller than the actual shared replay on current `master`": 1,
    "the shared replay now also keeps the dedicated `phase13-devres-wrapper-reviewability-tests` gate visible through `zigux/tests/phase13_devres_wrapper_reviewability.zig` so the direct plain, uncached, write-combined, and non-posted managed `devres` ioremap wrapper family does not look smaller than the actual shared replay on current `master`": 1,
    "the shared replay now also keeps the dedicated Landlock ruleset reviewability gate visible through `phase13-landlock-ruleset-reviewability-tests` so the manifest-backed ruleset helper packet does not look smaller than the actual published replay on current `master`": 1,
    "the shared replay now also keeps the dedicated `phase13-landlock-ruleset-fops-sync-tests` gate visible through `zigux/tests/phase13_landlock_ruleset_fops_sync.zig` so the ruleset-fd creation and explicit fops planning surface does not look smaller than the actual shared replay on current `master`": 1,
    "the shared replay now also keeps the dedicated Landlock syscall reviewability gate visible through `phase13-landlock-syscalls-reviewability-tests` so the manifest-backed syscall helper packet does not look smaller than the actual published replay on current `master`": 1,
}

TRACEABILITY_MARKERS = [
    "Shared tranche entrypoints already present on `master`:",
    "`zigux/tests/phase13_build.zig`",
    "`zigux/Makefile` via `make -C zigux phase13`",
    "`lib/devres.c` is represented by real helper code, real tests, a manifest-backed survey packet, and explicit blocked DMA/scatterlist boundary evidence",
    "the same shared packet also keeps `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, `zigux/helpers/notifier_chain_view.zig`, `zigux/tests/phase13_notifier_list_reviewability.zig`, and `Documentation/zigux/phase13-notifier-list-survey.md` visible as roadmap-adjacent release-facing evidence without changing the roadmap's four-anchor count",
    "reviewability gate: `zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
]

DOCS_ROOT_MARKERS = [
    "Phase 13 notes",
    "`Documentation/zigux/phase13-roadmap-traceability.md` now maps the four shared-helper roadmap anchors `fs/libfs.c`, `lib/devres.c`, `security/landlock/ruleset.c`, and `security/landlock/syscalls.c` to the live Zigux evidence so the current Phase 13 packet is visible from the docs root.",
    "`Documentation/zigux/phase13-release-notes-survey.md` records the active Phase 13 release-discipline packet, including the validator-first entrypoints, the four manifest-backed roadmap anchors, and the current helper-first non-goals, so release-facing review does not depend on the traceability note alone.",
    "`Documentation/zigux/README.md` now also keeps the dedicated `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_iounmap_reviewability.zig`, `zigux/tests/phase13_devres_iomap_reviewability.zig`, `zigux/tests/phase13_landlock_ruleset_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig` gates, the adjacent notifier-list manifest `zigux/tests/phase13_notifier_list_manifest.json`, and the roadmap-adjacent notifier evidence (`zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig`) visible from the docs root, so the top-level Phase 13 summary does not undercount the actual thirteen-step shared replay on current `master`.",
    "`Documentation/zigux/phase13-libfs-survey.md`, `Documentation/zigux/phase13-devres-survey.md`, `Documentation/zigux/phase13-landlock-ruleset-survey.md`, and `Documentation/zigux/phase13-landlock-syscalls-survey.md` plus the four `zigux/tests/phase13_*_manifest.json` files now keep the current helper-first boundaries explicit instead of implying broader runtime parity.",
    "`make -C zigux phase13-validate` is the current validator-first entrypoint for the shared Phase 13 release-discipline packet.",
    "`zigux/tests/phase13_build.zig` and `make -C zigux phase13` remain the published shared replay path; the earlier `phase13_landlock_ruleset.zig` EOF blocker note is now historical, the shared replay has already been rerun successfully on current `master`, and the remaining live `P13-L12` blocker is the manifest-backed helper boundary around `rb_replace_node()`, live object ownership transfer, hierarchy lifetime, and workqueue-backed teardown.",
]

DOCS_ROOT_EXACT_COUNT_MARKERS = {
    "`Documentation/zigux/README.md` now also keeps the dedicated `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_iounmap_reviewability.zig`, `zigux/tests/phase13_devres_iomap_reviewability.zig`, `zigux/tests/phase13_landlock_ruleset_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig` gates, the adjacent notifier-list manifest `zigux/tests/phase13_notifier_list_manifest.json`, and the roadmap-adjacent notifier evidence (`zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `include/zigux/notifier_abi.h`, and `zigux/helpers/notifier_chain_view.zig`) visible from the docs root, so the top-level Phase 13 summary does not undercount the actual thirteen-step shared replay on current `master`.": 1,
}

SCRIPT_README_MARKERS = [
    "Phase 13 flow",
    "`check-phase13-libfs-packet.py`, `check-phase13-devres-packet.py`, `check-phase13-notifier-packet.py`, and `validate-phase13-release.py` keep `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/Makefile`, and `zigux/tests/phase13_build.zig` aligned as one shared release-discipline packet, with the four roadmap-anchor manifests `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, the adjacent `zigux/tests/phase13_notifier_list_manifest.json`, the dedicated `scripts/zigux/check-phase13-devres-packet.py` guard, the `phase13-landlock-syscalls-reviewability-tests` gate under `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and the adjacent notifier evidence under `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, and `zigux/helpers/notifier_chain_view.zig` kept explicit instead of leaving the Phase 13 review path split across isolated docs or build wiring.",
    "`check-phase13-devres-packet.py` keeps the helper-first `devres` packet and its blocked DMA/scatterlist boundary visible in that same shared Phase 13 release flow instead of leaving the live devres guard implicit in the Makefile wiring and packet-local survey assets.",
    "`make -C zigux phase13-validate` runs that dedicated release validator before the broader shared replay.",
    "`make -C zigux phase13` routes through the validator before the shared replay, so the local convenience path matches the release-facing review contract.",
    "`Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_reviewability.zig` keep the helper-first `devres` packet explicit about adjacent coherent-DMA bookkeeping while live DMA-backed mappings and scatterlist ownership stay blocked rather than implied.",
]

SCRIPTS_README_EXACT_COUNT_MARKERS = {
    "`check-phase13-libfs-packet.py`, `check-phase13-devres-packet.py`, `check-phase13-notifier-packet.py`, and `validate-phase13-release.py` keep `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/Makefile`, and `zigux/tests/phase13_build.zig` aligned as one shared release-discipline packet, with the four roadmap-anchor manifests `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`, the adjacent `zigux/tests/phase13_notifier_list_manifest.json`, the dedicated `scripts/zigux/check-phase13-devres-packet.py` guard, the `phase13-landlock-syscalls-reviewability-tests` gate under `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and the adjacent notifier evidence under `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, and `zigux/helpers/notifier_chain_view.zig` kept explicit instead of leaving the Phase 13 review path split across isolated docs or build wiring.": 1,
}

REVIEW_CHECKLIST_MARKERS = [
    "Phase 13 release-discipline packet",
    "if the change touches the shared Phase 13 release-discipline packet, do `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, and `zigux/tests/phase13_build.zig` still agree",
    "if the change touches the shared Phase 13 release-discipline packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase13-release.py`, and `Documentation/zigux/phase13-release-notes-survey.md` still keep the docs-root Phase 13 reviewability sentence explicit around `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig` so the top-level Phase 13 summary does not undercount the ten-step shared replay?",
    "if the change touches the shared Phase 13 release-discipline packet, do `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_reviewability.zig` still keep the scripts-root devres inventory sentence and its adjacent coherent-DMA plus reviewability evidence explicit so reviewer guidance does not drift behind the stricter shared validator contract?",
    "does `make -C zigux phase13` routes through `make -C zigux phase13-validate` before the shared replay",
    "and that the shared replay still names the same ten steps?",
    "if the shared replay is currently blocked on `master`, does `Documentation/zigux/phase13-release-notes-survey.md` still name the exact blocker, the owning lane, and the fact that `phase13-validate` is green while `phase13-test` is not?",
    "if the change touches the shared Phase 13 release-discipline packet, do `zigux/tests/phase13_libfs_manifest.json`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_libfs_reviewability.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_notifier_list_reviewability.zig` still back the same four manifest-backed roadmap anchors plus the adjacent notifier-list reviewability packet",
    "while keeping live DMA-backed mappings and scatterlist ownership blocked rather than implied?",
    "if the change touches the shared Phase 13 release-discipline packet, do `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, and `Documentation/zigux/phase13-notifier-list-survey.md` still keep the adjacent notifier packet explicit as roadmap-adjacent release evidence rather than a fifth roadmap anchor?",
]

REVIEW_CHECKLIST_EXACT_COUNT_MARKERS = {
    "if the change touches the shared Phase 13 release-discipline packet, do `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase13-release.py`, `zigux/Makefile`, and `zigux/tests/phase13_build.zig` still agree": 1,
    "if the change touches the shared Phase 13 release-discipline packet, do `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase13-release.py`, and `Documentation/zigux/phase13-release-notes-survey.md` still keep the docs-root Phase 13 reviewability sentence explicit around `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig` so the top-level Phase 13 summary does not undercount the ten-step shared replay?": 1,
    "if the change touches the shared Phase 13 release-discipline packet, do `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase13-devres-survey.md`, `zigux/tests/phase13_devres_manifest.json`, `zigux/tests/phase13_devres_dma_coherent.zig`, and `zigux/tests/phase13_devres_reviewability.zig` still keep the scripts-root devres inventory sentence and its adjacent coherent-DMA plus reviewability evidence explicit so reviewer guidance does not drift behind the stricter shared validator contract?": 1,
}

DEVRES_SURVEY_MARKERS = [
    "# Phase 13 devres helper DMA/scatterlist boundary survey",
    "helper-first iomap or resource planners plus explicit DMA/scatterlist blockers pinned to the current repo state",
    "the shipped `DevresHelperLab` descriptor now says explicitly that the helper-only surface still avoids live DMA-backed mappings and scatterlist ownership",
    "live DMA-backed helpers such as `dmam_alloc_coherent()`, `dmam_free_coherent()`, `dma_map_resource()`, `dma_unmap_resource()`, or `dma_map_sgtable()` ownership and execution",
    "live scatter-gather ownership such as `struct scatterlist`, `sg_table`, `sg_*` iteration, merge, or detach-time cleanup behavior",
]

DEVRES_REVIEWABILITY_MARKERS = [
    'test "phase13 devres manifest records the current helper boundary and explicit dma/scatterlist blockers"',
    "try std.testing.expect(!descriptor.touches_live_dma);",
    "try std.testing.expect(!descriptor.touches_live_scatterlist);",
    "try std.testing.expectEqual(@as(usize, 1), blocked_dma_count);",
    "try std.testing.expectEqual(@as(usize, 1), blocked_scatterlist_count);",
    "try std.testing.expect(saw_dma_blocker);",
    "try std.testing.expect(saw_scatterlist_blocker);",
]

DEVRES_MANIFEST_GAP_EXPECTATIONS = [
    ("phase13-devres-live-dma-mappings", "blocked_on_dma_state"),
    ("phase13-devres-live-scatterlist-ownership", "blocked_on_scatterlist_state"),
]

BUILD_NAME_MARKERS = [
    "phase13-libfs-tests",
    "phase13-devres-tests",
    "phase13-devres-dma-coherent-tests",
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

RELEASE_EVIDENCE_CORE_PATHS = [
    "scripts/zigux/validate-phase13-release.py",
    "scripts/zigux/check-phase13-devres-packet.py",
    "scripts/zigux/README.md",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/README.md",
    "Documentation/zigux/review-checklist.md",
    ".github/workflows/zigux-bootstrap.yml",
    "zigux/Makefile",
    "zigux/tests/phase13_build.zig",
    "zigux/tests/phase13_devres_dma_coherent.zig",
    "zigux/tests/phase13_devres_iounmap_reviewability.zig",
    "zigux/tests/phase13_devres_iomap_reviewability.zig",
    "zigux/tests/phase13_devres_wrapper_reviewability.zig",
    "zigux/tests/phase13_landlock_ruleset_reviewability.zig",
    "zigux/tests/phase13_landlock_ruleset_fops_sync.zig",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
    "zigux/bindings/notifier_abi.zig",
    "include/zigux/notifier_abi.h",
    "zigux/helpers/notifier_chain_view.zig",
]

def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

def load_json(path: str) -> dict[str, object]:
    return json.loads(text(path))

def section_text(source: str, start_marker: str, end_marker: str) -> str | None:
    start = source.find(start_marker)
    if start == -1:
        return None
    start += len(start_marker)
    end = source.find(end_marker, start)
    if end == -1:
        return None
    return source[start:end]

def require_exact_count(missing: list[str], label: str, source: str, marker: str, expected_count: int) -> None:
    actual_count = source.count(marker)
    if actual_count != expected_count:
        missing.append(f"{label}:exact_count:{marker}:{actual_count}!={expected_count}")

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
    source_by_name = {
        "docs_root": text("Documentation/zigux/README.md"),
        "scripts_readme": text("scripts/zigux/README.md"),
        "make": text("zigux/Makefile"),
        "workflow": text(".github/workflows/zigux-bootstrap.yml"),
        "release": text("Documentation/zigux/phase13-release-notes-survey.md"),
        "traceability": text("Documentation/zigux/phase13-roadmap-traceability.md"),
        "review_checklist": text("Documentation/zigux/review-checklist.md"),
    }

    for name, markers in [
        ("docs_root", DOCS_ROOT_MARKERS),
        ("scripts_readme", SCRIPT_README_MARKERS),
        ("make", MAKE_MARKERS),
        ("workflow", WORKFLOW_MARKERS),
        ("release", RELEASE_MARKERS),
        ("traceability", TRACEABILITY_MARKERS),
        ("review_checklist", REVIEW_CHECKLIST_MARKERS),
    ]:
        source = source_by_name[name]
        for marker in markers:
            if marker not in source:
                missing.append(f"{name}:{marker}")

    for marker, expected_count in MAKE_EXACT_COUNT_MARKERS.items():
        require_exact_count(missing, "make", source_by_name["make"], marker, expected_count)
    for marker, expected_count in WORKFLOW_EXACT_COUNT_MARKERS.items():
        require_exact_count(missing, "workflow", source_by_name["workflow"], marker, expected_count)
    for marker, expected_count in RELEASE_EXACT_COUNT_MARKERS.items():
        require_exact_count(missing, "release", source_by_name["release"], marker, expected_count)
    for marker, expected_count in DOCS_ROOT_EXACT_COUNT_MARKERS.items():
        require_exact_count(missing, "docs_root", source_by_name["docs_root"], marker, expected_count)
    for marker, expected_count in SCRIPTS_README_EXACT_COUNT_MARKERS.items():
        require_exact_count(missing, "scripts_readme", source_by_name["scripts_readme"], marker, expected_count)
    for marker, expected_count in REVIEW_CHECKLIST_EXACT_COUNT_MARKERS.items():
        require_exact_count(missing, "review_checklist", source_by_name["review_checklist"], marker, expected_count)

    release_text = source_by_name["release"]
    product_boundary = section_text(
        release_text,
        "product boundary:\n",
        "\n## Why this record exists",
    )
    if product_boundary is None:
        missing.append("release:product_boundary_section")
    else:
        for rel in [
            "scripts/zigux/validate-phase13-release.py",
            "scripts/zigux/check-phase13-devres-packet.py",
            "scripts/zigux/README.md",
            "Documentation/zigux/phase13-release-notes-survey.md",
            "Documentation/zigux/phase13-roadmap-traceability.md",
            "Documentation/zigux/README.md",
            "Documentation/zigux/review-checklist.md",
            ".github/workflows/zigux-bootstrap.yml",
            "zigux/tests/phase13_build.zig",
            "zigux/Makefile",
            "Documentation/zigux/phase13-libfs-slice.md",
            "Documentation/zigux/phase13-libfs-survey.md",
            "Documentation/zigux/phase13-devres-slice.md",
            "Documentation/zigux/phase13-devres-survey.md",
            "Documentation/zigux/phase13-landlock-ruleset-slice.md",
            "Documentation/zigux/phase13-landlock-ruleset-survey.md",
            "Documentation/zigux/phase13-landlock-syscalls-slice.md",
            "Documentation/zigux/phase13-landlock-syscalls-survey.md",
            "Documentation/zigux/phase13-notifier-list-survey.md",
            "zigux/tests/phase13_libfs_manifest.json",
            "zigux/tests/phase13_devres_manifest.json",
            "zigux/tests/phase13_landlock_ruleset_manifest.json",
            "zigux/tests/phase13_landlock_syscalls_manifest.json",
            "zigux/tests/phase13_notifier_list_manifest.json",
            "zigux/tests/phase13_libfs_reviewability.zig",
            "zigux/tests/phase13_devres.zig",
            "zigux/tests/phase13_devres_dma_coherent.zig",
            "zigux/tests/phase13_devres_iounmap_reviewability.zig",
            "zigux/tests/phase13_devres_iomap_reviewability.zig",
            "zigux/tests/phase13_devres_reviewability.zig",
            "zigux/tests/phase13_devres_wrapper_reviewability.zig",
            "zigux/tests/phase13_landlock_ruleset_reviewability.zig",
            "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
            "zigux/tests/phase13_landlock_ruleset_fops_sync.zig",
            "zigux/tests/phase13_notifier_list_reviewability.zig",
            "zigux/bindings/notifier_abi.zig",
            "include/zigux/notifier_abi.h",
            "zigux/helpers/notifier_chain_view.zig",
        ]:
            if rel not in product_boundary:
                missing.append(f"release:product_boundary_path:{rel}")

    for rel in [
        "scripts/zigux/validate-phase13-release.py",
        "scripts/zigux/check-phase13-devres-packet.py",
        "scripts/zigux/README.md",
        "Documentation/zigux/phase13-release-notes-survey.md",
        "Documentation/zigux/phase13-roadmap-traceability.md",
        "Documentation/zigux/README.md",
        "Documentation/zigux/review-checklist.md",
        "zigux/tests/phase13_build.zig",
        "zigux/Makefile",
        "Documentation/zigux/phase13-libfs-survey.md",
        "Documentation/zigux/phase13-devres-survey.md",
        "Documentation/zigux/phase13-landlock-ruleset-survey.md",
        "Documentation/zigux/phase13-landlock-syscalls-survey.md",
        "Documentation/zigux/phase13-notifier-list-survey.md",
        "zigux/tests/phase13_libfs_manifest.json",
        "zigux/tests/phase13_devres_manifest.json",
        "zigux/tests/phase13_devres_dma_coherent.zig",
        "zigux/tests/phase13_devres_iounmap_reviewability.zig",
        "zigux/tests/phase13_devres_iomap_reviewability.zig",
        "zigux/tests/phase13_devres_wrapper_reviewability.zig",
        "zigux/tests/phase13_landlock_ruleset_manifest.json",
        "zigux/tests/phase13_landlock_ruleset_reviewability.zig",
        "zigux/tests/phase13_landlock_ruleset_fops_sync.zig",
        "zigux/tests/phase13_landlock_syscalls_manifest.json",
        "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
        "zigux/tests/phase13_notifier_list_manifest.json",
        "zigux/tests/phase13_devres_reviewability.zig",
        "zigux/tests/phase13_notifier_list_reviewability.zig",
        "zigux/bindings/notifier_abi.zig",
        "include/zigux/notifier_abi.h",
        "zigux/helpers/notifier_chain_view.zig",
    ]:
        if rel not in release_text:
            missing.append(f"release:evidence_path:{rel}")

    release_evidence = section_text(
        release_text,
        "The current bounded release-evidence set is:\n",
        "\n## Gates",
    )
    if release_evidence is None:
        missing.append("release:evidence_set_section")
    else:
        for rel in RELEASE_EVIDENCE_CORE_PATHS:
            if rel not in release_evidence:
                missing.append(f"release:evidence_set_path:{rel}")

    build_text = text("zigux/tests/phase13_build.zig")
    build_names = BUILD_TEST_NAME_RE.findall(build_text)
    if build_names != BUILD_NAME_MARKERS:
        missing.append("build:test_names")
    for build_name in BUILD_NAME_MARKERS:
        if build_name not in release_text:
            missing.append(f"release:shared_replay_step:{build_name}")
    depend_steps = BUILD_DEPEND_STEP_RE.findall(build_text)
    if len(depend_steps) != 15:
        missing.append(f"build:depend_step_count={len(depend_steps)}")

    for manifest_path, lane_key, anchor in [
        ("zigux/tests/phase13_libfs_manifest.json", "P13-L04", "fs/libfs.c"),
        ("zigux/tests/phase13_devres_manifest.json", "P13-L10", "lib/devres.c"),
        ("zigux/tests/phase13_landlock_ruleset_manifest.json", "P13-L12", "security/landlock/ruleset.c"),
        ("zigux/tests/phase13_landlock_syscalls_manifest.json", "P13-L16", "security/landlock/syscalls.c"),
    ]:
        manifest = load_json(manifest_path)
        if manifest.get("phase") != "Phase 13":
            missing.append(f"{manifest_path}:phase")
        if manifest.get("lane_key") != lane_key:
            missing.append(f"{manifest_path}:lane_key")
        if manifest.get("anchor") != anchor:
            missing.append(f"{manifest_path}:anchor")
        summary = manifest.get("survey_summary")
        if not isinstance(summary, dict):
            missing.append(f"{manifest_path}:survey_summary")
            continue
        if summary.get("preexisting_phase13_build_present") is not True:
            missing.append(f"{manifest_path}:build_present")
        if summary.get("preexisting_phase13_make_target_present") is not True:
            missing.append(f"{manifest_path}:make_present")

    ruleset_manifest = load_json("zigux/tests/phase13_landlock_ruleset_manifest.json")
    ruleset_summary = ruleset_manifest.get("survey_summary")
    if not isinstance(ruleset_summary, dict):
        missing.append("zigux/tests/phase13_landlock_ruleset_manifest.json:survey_summary")
    else:
        if ruleset_summary.get("preexisting_phase13_build_present") is not True:
            missing.append("zigux/tests/phase13_landlock_ruleset_manifest.json:build_present")

    syscalls_manifest = load_json("zigux/tests/phase13_landlock_syscalls_manifest.json")
    syscalls_summary = syscalls_manifest.get("survey_summary")
    if not isinstance(syscalls_summary, dict):
        missing.append("zigux/tests/phase13_landlock_syscalls_manifest.json:survey_summary")
    else:
        if syscalls_summary.get("preexisting_phase13_landlock_syscalls_reviewability_present") is not True:
            missing.append("zigux/tests/phase13_landlock_syscalls_manifest.json:reviewability_present")

    devres_manifest = load_json("zigux/tests/phase13_devres_manifest.json")
    for blocked in ["blocked_on_dma_state", "blocked_on_scatterlist_state"]:
        if not any(gap.get("status") == blocked for gap in devres_manifest.get("gaps", []) if isinstance(gap, dict)):
            missing.append(f"zigux/tests/phase13_devres_manifest.json:{blocked}")
    for gap_id, status in DEVRES_MANIFEST_GAP_EXPECTATIONS:
        if not any(isinstance(gap, dict) and gap.get("id") == gap_id and gap.get("status") == status for gap in devres_manifest.get("gaps", [])):
            missing.append(f"zigux/tests/phase13_devres_manifest.json:{gap_id}:{status}")

    devres_surveyed_commit = devres_manifest.get("surveyed_commit")
    if not isinstance(devres_surveyed_commit, str) or SURVEYED_COMMIT_RE.fullmatch(devres_surveyed_commit) is None:
        missing.append("zigux/tests/phase13_devres_manifest.json:surveyed_commit")
    else:
        devres_survey_text = text("Documentation/zigux/phase13-devres-survey.md")
        devres_traceability_text = text("Documentation/zigux/phase13-roadmap-traceability.md")
        if f"- `PHASE13_SURVEYED_COMMIT={devres_surveyed_commit}`" not in devres_survey_text:
            missing.append("Documentation/zigux/phase13-devres-survey.md:surveyed_commit")
        if f"- manifest `surveyed_commit`: `{devres_surveyed_commit}`" not in devres_traceability_text:
            missing.append("Documentation/zigux/phase13-roadmap-traceability.md:devres_surveyed_commit")
        for marker in DEVRES_SURVEY_MARKERS:
            if marker not in devres_survey_text:
                missing.append(f"Documentation/zigux/phase13-devres-survey.md:{marker}")

    devres_reviewability_text = text("zigux/tests/phase13_devres_reviewability.zig")
    for marker in DEVRES_REVIEWABILITY_MARKERS:
        if marker not in devres_reviewability_text:
            missing.append(f"zigux/tests/phase13_devres_reviewability.zig:{marker}")

    notifier_manifest = load_json("zigux/tests/phase13_notifier_list_manifest.json")
    if notifier_manifest.get("phase") != "Phase 13":
        missing.append("zigux/tests/phase13_notifier_list_manifest.json:phase")
    if notifier_manifest.get("lane_key") != "P13-L19":
        missing.append("zigux/tests/phase13_notifier_list_manifest.json:lane_key")
    notifier_summary = notifier_manifest.get("survey_summary")
    if not isinstance(notifier_summary, dict):
        missing.append("zigux/tests/phase13_notifier_list_manifest.json:survey_summary")
    else:
        if notifier_summary.get("preexisting_phase13_build_present") is not True:
            missing.append("zigux/tests/phase13_notifier_list_manifest.json:build_present")
        if notifier_summary.get("landed_generic_notifier_abi_present") is not True:
            missing.append("zigux/tests/phase13_notifier_list_manifest.json:notifier_abi_present")
        if notifier_summary.get("landed_generic_notifier_build_surface_present") is not True:
            missing.append("zigux/tests/phase13_notifier_list_manifest.json:notifier_build_surface_present")
        if notifier_summary.get("landed_generic_notifier_helper_present") is not True:
            missing.append("zigux/tests/phase13_notifier_list_manifest.json:notifier_helper_present")
        if notifier_summary.get("landed_generic_notifier_c_header_surface_present") is not True:
            missing.append("zigux/tests/phase13_notifier_list_manifest.json:notifier_c_header_present")

    if missing:
        print("PHASE13_RELEASE_VALIDATION=fail")
        print("PHASE13_RELEASE_VALIDATION_MISSING_START")
        for item in missing:
            print(item)
        print("PHASE13_RELEASE_VALIDATION_MISSING_END")
        return 1

    print("PHASE13_RELEASE_VALIDATION=pass")
    print(f"PHASE13_RELEASE_REQUIRED_FILE_COUNT={len(FILES)}")
    print("PHASE13_RELEASE_REQUIRED_MARKER_COUNT=" f"{len(MAKE_MARKERS) + len(MAKE_EXACT_COUNT_MARKERS) + len(WORKFLOW_MARKERS) + len(WORKFLOW_EXACT_COUNT_MARKERS) + len(RELEASE_MARKERS) + len(RELEASE_EXACT_COUNT_MARKERS) + len(TRACEABILITY_MARKERS) + len(DOCS_ROOT_MARKERS) + len(DOCS_ROOT_EXACT_COUNT_MARKERS) + len(SCRIPT_README_MARKERS) + len(SCRIPTS_README_EXACT_COUNT_MARKERS) + len(REVIEW_CHECKLIST_MARKERS) + len(REVIEW_CHECKLIST_EXACT_COUNT_MARKERS) + len(DEVRES_SURVEY_MARKERS) + len(DEVRES_REVIEWABILITY_MARKERS)}")
    print(f"PHASE13_RELEASE_BUILD_TEST_COUNT={len(build_names)}")
    print(f"PHASE13_RELEASE_BUILD_DEPEND_STEP_COUNT={len(depend_steps)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
