#!/usr/bin/env python3
"""Guard the current Phase 6 helper-evidence packet."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

HELPER_EVIDENCE_CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
HELPER_EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PHASE6_BUILD_PATH = Path("zigux/tests/phase6_build.zig")
PHASE6_MAKEFILE_PATH = Path("zigux/Makefile")

EXPECTED_PACKET = "phase6-helper-evidence"
EXPECTED_PHASE = "Phase 6"
EXPECTED_LANE_SCOPE = "shared helper-evidence rows and machine-readable manifest only"
EXPECTED_ROADMAP_ANCHORS = ["lib/base64.c", "lib/bsearch.c", "lib/checksum.c", "lib/hexdump.c"]
REQUIRED_HELPER_PATHS = [
    Path("lib/base64.zig"),
    Path("lib/bsearch.zig"),
    Path("lib/checksum.zig"),
    Path("lib/hexdump.zig"),
]
REQUIRED_DIRECT_READBACK_COMPANIONS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/check-phase6-present-entrypoints.py",
]
EXPECTED_HELPERS = [
    {
        "key": "base64",
        "roadmap_anchor": "lib/base64.c",
        "zig_helper": "lib/base64.zig",
        "focused_helper_replay": "zigux/tests/phase6_base64.zig",
        "dedicated_slowdown_replay": "zigux/tests/phase6_base64_perf.zig",
        "fixture_surfaces": ["zigux/tests/fixtures/phase6_base64_vectors.zig"],
        "checker_surfaces": [
            "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
            "zigux/tests/phase6_base64_c_parity.zig",
            "zigux/tests/phase6_base64_c_casegen.zig",
            "zigux/tests/fixtures/phase6_base64_c_harness.c",
            "scripts/zigux/check-phase6-base64-c-parity.py",
        ],
        "slice_note": "Documentation/zigux/phase6-base64-slice.md",
        "current_review_posture": "direct-helper-readback-restored",
    },
    {
        "key": "bsearch",
        "roadmap_anchor": "lib/bsearch.c",
        "zig_helper": "lib/bsearch.zig",
        "focused_helper_replay": "zigux/tests/phase6_bsearch.zig",
        "focused_c_abi_replays": [
            "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
            "zigux/tests/phase6_bsearch_c_abi_budget.zig",
        ],
        "fixture_surfaces": ["zigux/tests/fixtures/phase6_bsearch_vectors.zig"],
        "checker_surfaces": ["scripts/zigux/check-phase6-bsearch-corpus-evidence.py"],
        "slice_note": "Documentation/zigux/phase6-bsearch-slice.md",
        "current_review_posture": "direct-helper-readback-restored",
    },
    {
        "key": "checksum",
        "roadmap_anchor": "lib/checksum.c",
        "zig_helper": "lib/checksum.zig",
        "focused_helper_replay": "zigux/tests/phase6_checksum.zig",
        "dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig",
        "fixture_surfaces": ["zigux/tests/fixtures/phase6_checksum_vectors.zig"],
        "checker_surfaces": [
            "zigux/tests/phase6_checksum_c_parity.zig",
            "zigux/tests/fixtures/phase6_checksum_c_harness.c",
            "scripts/zigux/check-phase6-checksum-c-parity.py",
        ],
        "slice_note": "Documentation/zigux/phase6-checksum-slice.md",
        "current_review_posture": "direct-helper-readback-restored",
    },
    {
        "key": "hexdump",
        "roadmap_anchor": "lib/hexdump.c",
        "zig_helper": "lib/hexdump.zig",
        "focused_helper_replay": "zigux/tests/phase6_hexdump.zig",
        "dedicated_slowdown_replay": "zigux/tests/phase6_hexdump_perf.zig",
        "perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf_matrix.zig",
        "fixture_surfaces": ["zigux/tests/fixtures/phase6_hexdump_vectors.zig"],
        "checker_surfaces": ["scripts/zigux/check-phase6-hexdump-packet.py"],
        "slice_note": "Documentation/zigux/phase6-hexdump-slice.md",
        "perf_refresh_note": "Documentation/zigux/phase6-hexdump-perf-refresh.md",
        "current_review_posture": "direct-readback-limited",
    },
]
EXPECTED_CURRENT_REPO_REALITY_GAPS = [
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "Documentation/zigux/phase6-hexdump-perf-refresh.md",
    "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
    "zigux/tests/phase6_base64_c_parity.zig",
    "zigux/tests/phase6_base64_c_casegen.zig",
    "zigux/tests/fixtures/phase6_base64_c_harness.c",
    "zigux/tests/phase6_checksum_c_parity.zig",
    "zigux/tests/fixtures/phase6_checksum_c_harness.c",
    "scripts/zigux/check-phase6-base64-c-parity.py",
    "scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
    "scripts/zigux/check-phase6-hexdump-packet.py",
]
EXPECTED_CURRENT_SHARED_REPLAY_INVENTORY = [
    "zig build phase6-base64-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-test",
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-perf",
    "zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-test",
    "zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "python3 scripts/zigux/check-phase6-hexdump-route.py",
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf",
]
REQUIRED_BUILD_SNIPPETS = [
    "const base64_perf_root_module = b.createModule(.{",
    '.root_source_file = b.path("phase6_base64_perf.zig"),',
    "const bsearch_lower_bound_c_abi_root_module = b.createModule(.{",
    '.root_source_file = b.path("phase6_bsearch_lower_bound_c_abi.zig"),',
    "const bsearch_c_abi_budget_root_module = b.createModule(.{",
    "const checksum_perf_root_module = b.createModule(.{",
    "const hexdump_perf_root_module = b.createModule(.{",
    'const base64_test_step = b.step("phase6-base64-test", "Run Phase 6 base64 helper tests");',
    'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 helper perf gate");',
    'const bsearch_test_step = b.step("phase6-bsearch-test", "Run Phase 6 bsearch helper tests");',
    'const checksum_test_step = b.step("phase6-checksum-test", "Run Phase 6 checksum helper tests");',
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
    'const hexdump_test_step = b.step("phase6-hexdump-test", "Run Phase 6 hexdump helper tests");',
    'const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");',
    'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");',
]
REQUIRED_MAKEFILE_SNIPPETS = [
    ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2 phase3-validate phase3 phase3-export-uapi-layout-test phase6-base64-test phase6-base64-perf phase6-bsearch-test phase6-checksum-test phase6-checksum-perf phase6-hexdump-review phase6-hexdump-test phase6-hexdump-perf",
    "phase6-base64-test:",
    "$(ZIG) build phase6-base64-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-base64-perf:",
    "$(ZIG) build phase6-base64-perf --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-bsearch-test:",
    "$(ZIG) build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-test:",
    "$(ZIG) build phase6-checksum-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-perf:",
    "$(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-hexdump-review:",
    "$(PYTHON) scripts/zigux/check-phase6-hexdump-route.py",
    "phase6-hexdump-test:",
    "$(ZIG) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-hexdump-perf:",
    "$(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig --summary all",
]
REQUIRED_CATALOG_SNIPPETS = [
    "- lane scope: shared helper-evidence rows and machine-readable manifest only",
    "- directly readable shared build foothold: `zigux/tests/phase6_build.zig`",
    "- directly readable shared Makefile wrapper surface: `zigux/Makefile`",
    "- returned helper-parity companion: `zigux/tests/phase6_helper_parity_manifest.json`",
    "## Current direct-readback warning",
    "- `Documentation/zigux/phase6-helper-parity-catalog.md`",
    "- `Documentation/zigux/phase6-perf-gate-survey.md`",
    "Treat those paths as last-known Phase 6 packet members that require fresh reread or re-materialization before they are presented as current shipped direct evidence again.",
    "The directly readable shared packet in this environment is therefore this helper-evidence catalog together with `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, and `scripts/zigux/check-phase6-present-entrypoints.py`.",
    "Authenticated direct readback still leaves `Documentation/zigux/phase6-perf-gate-survey.md` missing on current `master`, so the remaining shared perf-note risk is reminder-surface drift rather than an executable-route gap: the directly readable helper-evidence packet already materializes `zigux/Makefile` with the current `phase6-base64-test`, `phase6-base64-perf`, `phase6-bsearch-test`, `phase6-checksum-test`, `phase6-checksum-perf`, `phase6-hexdump-review`, `phase6-hexdump-test`, and `phase6-hexdump-perf` wrapper targets, and it also materializes the narrower helper-parity companion `zigux/tests/phase6_helper_parity_manifest.json`.",
    "the remaining roadmap-aligned measurement gap is shared survey truthfulness rather than new helper semantics: `Documentation/zigux/phase6-perf-gate-survey.md` is still missing on current `master`, so the directly readable helper-evidence packet should stay anchored to the returned `zigux/tests/phase6_helper_parity_manifest.json` and the directly readable `zigux/Makefile` Phase 6 wrapper targets while `bsearch` continues to measure bounded search cost through its C ABI budget route instead of a dedicated slowdown replay comparable to the base64, checksum, and hexdump helper-local gates.",
    "## Current shared replay inventory",
    "- `make -C zigux phase6-hexdump-perf`",
]
CATALOG_SURVEYED_HEAD_PATTERN = re.compile(r"^- surveyed head: `([^`]+)`$", re.M)
SELF_TEST_CASE_COUNT = 19
CATALOG_SCAFFOLD = """# Phase 6 Helper Evidence Catalog

This note records the current helper-evidence survey for the bounded Phase 6 leaf-helper packet on `master`.

- surveyed head: `61e026c`
- lane scope: shared helper-evidence rows and machine-readable manifest only
- shared scripts-root reminder: `scripts/zigux/README.md`
- shared tests-root reminder: `zigux/tests/README.md`
- shared docs-root reminder: `Documentation/zigux/README.md`
- directly readable shared build foothold: `zigux/tests/phase6_build.zig`
- directly readable shared Makefile wrapper surface: `zigux/Makefile`
- shared machine-readable manifest: `zigux/tests/phase6_helper_evidence_manifest.json`
- returned helper-parity companion: `zigux/tests/phase6_helper_parity_manifest.json`
- roadmap-backed helper anchors:
  - `lib/base64.c`
  - `lib/bsearch.c`
  - `lib/checksum.c`
  - `lib/hexdump.c`

## Why this catalog exists

The four Phase 6 slice notes keep the helper-local detail, but they do not keep one small shared table of the roadmap anchor, the landed Zig helper, and the current reviewable evidence row. This catalog closes that narrower review gap without widening the Phase 6 packet into new perf policy, validator, or helper-semantic work.

## Current direct-readback warning

Fresh direct GitHub contents reads on current `master` still return missing for several shared-note and helper-local packet members that older Phase 6 reminder surfaces have treated as shipped evidence, including:

- `Documentation/zigux/phase6-helper-parity-catalog.md`
- `Documentation/zigux/phase6-perf-gate-survey.md`
- `Documentation/zigux/phase6-hexdump-slice.md`
- `Documentation/zigux/phase6-hexdump-perf-refresh.md`
- `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`
- `zigux/tests/phase6_base64_c_parity.zig`
- `zigux/tests/phase6_base64_c_casegen.zig`
- `zigux/tests/fixtures/phase6_base64_c_harness.c`
- `zigux/tests/phase6_checksum_c_parity.zig`
- `zigux/tests/fixtures/phase6_checksum_c_harness.c`
- `scripts/zigux/check-phase6-base64-c-parity.py`
- `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- `scripts/zigux/check-phase6-checksum-c-parity.py`
- `scripts/zigux/check-phase6-hexdump-packet.py`

Treat those paths as last-known Phase 6 packet members that require fresh reread or re-materialization before they are presented as current shipped direct evidence again. The directly readable shared packet in this environment is therefore this helper-evidence catalog together with `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, and `scripts/zigux/check-phase6-present-entrypoints.py`.

Authenticated direct readback still leaves `Documentation/zigux/phase6-perf-gate-survey.md` missing on current `master`, so the remaining shared perf-note risk is reminder-surface drift rather than an executable-route gap: the directly readable helper-evidence packet already materializes `zigux/Makefile` with the current `phase6-base64-test`, `phase6-base64-perf`, `phase6-bsearch-test`, `phase6-checksum-test`, `phase6-checksum-perf`, `phase6-hexdump-review`, `phase6-hexdump-test`, and `phase6-hexdump-perf` wrapper targets, and it also materializes the narrower helper-parity companion `zigux/tests/phase6_helper_parity_manifest.json`.

## Current helper-evidence rows

### base64

- roadmap anchor: `lib/base64.c`
- Zig helper: `lib/base64.zig`
- focused helper replay: `zigux/tests/phase6_base64.zig`
- dedicated slowdown replay: `zigux/tests/phase6_base64_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_base64_vectors.zig`
- last-known direct C parity companions still needing fresh direct reads: `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`
- slice note: `Documentation/zigux/phase6-base64-slice.md`
- current review posture: the roadmap-backed base64 packet now has directly readable helper-local evidence through `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `Documentation/zigux/phase6-base64-slice.md`, this shared catalog, `zigux/tests/phase6_helper_evidence_manifest.json`, the returned `zigux/tests/phase6_helper_parity_manifest.json`, the restored shared build foothold, the current Makefile wrapper surface, and the directly readable scripts-root plus tests-root reminders, while the direct C parity companions still need fresh direct reads before they are presented as current shipped evidence

### bsearch

- roadmap anchor: `lib/bsearch.c`
- Zig helper: `lib/bsearch.zig`
- focused helper replay: `zigux/tests/phase6_bsearch.zig`
- focused C ABI replays: `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` and `zigux/tests/phase6_bsearch_c_abi_budget.zig`
- compact shared seed fixture companion: `zigux/tests/fixtures/phase6_bsearch_vectors.zig`
- slice note: `Documentation/zigux/phase6-bsearch-slice.md`
- last-known companion packet members still needing fresh direct reads: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`
- current review posture: direct helper-local evidence is readable again through `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `Documentation/zigux/phase6-bsearch-slice.md`, this shared catalog, `zigux/tests/phase6_helper_evidence_manifest.json`, the returned `zigux/tests/phase6_helper_parity_manifest.json`, the restored shared build foothold, the current Makefile wrapper surface, and the directly readable scripts-root plus tests-root reminders, while the dedicated corpus checker still needs fresh direct reads before it is presented as current shipped evidence

### checksum

- roadmap anchor: `lib/checksum.c`
- Zig helper: `lib/checksum.zig`
- focused helper replay: `zigux/tests/phase6_checksum.zig`
- dedicated slowdown replay: `zigux/tests/phase6_checksum_perf.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_checksum_vectors.zig`
- direct C parity packet: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`
- slice note: `Documentation/zigux/phase6-checksum-slice.md`
- current review posture: direct helper-local evidence is readable again through `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `Documentation/zigux/phase6-checksum-slice.md`, this shared catalog, `zigux/tests/phase6_helper_evidence_manifest.json`, the returned `zigux/tests/phase6_helper_parity_manifest.json`, the restored shared build foothold, the current Makefile wrapper surface, and the directly readable scripts-root plus tests-root reminders, while the direct C parity companions still need fresh direct reads before they are presented as current shipped evidence

### hexdump

- roadmap anchor: `lib/hexdump.c`
- Zig helper: `lib/hexdump.zig`
- focused helper replay: `zigux/tests/phase6_hexdump.zig`
- dedicated slowdown replay: `zigux/tests/phase6_hexdump_perf.zig`
- exact perf-matrix preflight: `zigux/tests/phase6_hexdump_perf_matrix.zig`
- committed fixture surface: `zigux/tests/fixtures/phase6_hexdump_vectors.zig`
- helper-local packet checker: `scripts/zigux/check-phase6-hexdump-packet.py`
- perf refresh note: `Documentation/zigux/phase6-hexdump-perf-refresh.md`
- slice note: `Documentation/zigux/phase6-hexdump-slice.md`
- current review posture: direct helper-local evidence is readable again through `lib/hexdump.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, this shared catalog, `zigux/tests/phase6_helper_evidence_manifest.json`, the returned `zigux/tests/phase6_helper_parity_manifest.json`, the restored shared build foothold, the current Makefile wrapper surface, and the directly readable scripts-root plus tests-root reminders, while the helper-local checker, perf refresh note, and slice note still need fresh direct reads before they are presented as current shipped evidence

## Roadmap perf-gap readback

The Phase 6 roadmap requires perf gates for math-sensitive helpers across the bounded `lib/base64.c`, `lib/bsearch.c`, `lib/checksum.c`, and `lib/hexdump.c` packet. Current direct-readback measurement coverage on surveyed head `61e026c` is therefore mixed rather than uniform:

- `base64` keeps a dedicated helper-local slowdown replay in `zigux/tests/phase6_base64_perf.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig` still centralizes six fixture-owned encode and decode cases across standard, URL-safe, and IMAP variants.
- `checksum` keeps a dedicated helper-vs-reference slowdown gate in `zigux/tests/phase6_checksum_perf.zig`, with the committed `64B` and `1501B` threshold matrix still owned by `zigux/tests/fixtures/phase6_checksum_vectors.zig`.
- `hexdump` keeps a dedicated slowdown gate in `zigux/tests/phase6_hexdump_perf.zig`, with the current fixture matrix in `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still covering four formatting cases from `16B-plain-g1` through `16B-ascii-g8`.
- `bsearch` still measures bounded search cost through `zigux/tests/phase6_bsearch_c_abi_budget.zig` and the deterministic `perf_cases` plus seeded query corpus in `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, which hold raw C ABI search and equal-range comparisons to logarithmic budgets across representative lengths instead of using a dedicated wall-clock slowdown harness.
- the remaining roadmap-aligned measurement gap is shared survey truthfulness rather than new helper semantics: `Documentation/zigux/phase6-perf-gate-survey.md` is still missing on current `master`, so the directly readable helper-evidence packet should stay anchored to the returned `zigux/tests/phase6_helper_parity_manifest.json` and the directly readable `zigux/Makefile` Phase 6 wrapper targets while `bsearch` continues to measure bounded search cost through its C ABI budget route instead of a dedicated slowdown replay comparable to the base64, checksum, and hexdump helper-local gates.

## Current shared replay inventory

- `zig build phase6-base64-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-base64-test`
- `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-base64-perf`
- `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-bsearch-test`
- `zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-checksum-test`
- `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-checksum-perf`
- `python3 scripts/zigux/check-phase6-hexdump-route.py`
- `zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-hexdump-review`
- `zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-hexdump-test`
- `zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig`
- `make -C zigux phase6-hexdump-perf`

Reopen this catalog only when one of the four roadmap anchors gains or loses a truthful helper-evidence row on `master`.
"""
BUILD_SCAFFOLD = """const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const base64_module = b.createModule(.{
        .root_source_file = b.path("../../lib/base64.zig"),
        .target = target,
        .optimize = optimize,
    });
    const base64_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_base64.zig"),
        .target = target,
        .optimize = optimize,
    });
    base64_root_module.addImport("base64", base64_module);

    const base64_perf_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_base64_perf.zig"),
        .target = target,
        .optimize = optimize,
    });
    base64_perf_root_module.addImport("base64", base64_module);

    const bsearch_module = b.createModule(.{
        .root_source_file = b.path("../../lib/bsearch.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bsearch_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_bsearch.zig"),
        .target = target,
        .optimize = optimize,
    });
    bsearch_root_module.addImport("bsearch", bsearch_module);

    const bsearch_lower_bound_c_abi_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_bsearch_lower_bound_c_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    bsearch_lower_bound_c_abi_root_module.addImport("bsearch", bsearch_module);

    const bsearch_c_abi_budget_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_bsearch_c_abi_budget.zig"),
        .target = target,
        .optimize = optimize,
    });
    bsearch_c_abi_budget_root_module.addImport("bsearch", bsearch_module);

    const checksum_module = b.createModule(.{
        .root_source_file = b.path("../../lib/checksum.zig"),
        .target = target,
        .optimize = optimize,
    });
    const checksum_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_checksum.zig"),
        .target = target,
        .optimize = optimize,
    });
    checksum_root_module.addImport("checksum", checksum_module);

    const checksum_perf_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_checksum_perf.zig"),
        .target = target,
        .optimize = optimize,
    });
    checksum_perf_root_module.addImport("checksum", checksum_module);

    const hexdump_module = b.createModule(.{
        .root_source_file = b.path("../../lib/hexdump.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hexdump_vectors_module = b.createModule(.{
        .root_source_file = b.path("fixtures/phase6_hexdump_vectors.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hexdump_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_hexdump.zig"),
        .target = target,
        .optimize = optimize,
    });
    hexdump_root_module.addImport("hexdump", hexdump_module);
    hexdump_root_module.addImport("phase6_hexdump_vectors", hexdump_vectors_module);

    const hexdump_perf_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_hexdump_perf.zig"),
        .target = target,
        .optimize = optimize,
    });
    hexdump_perf_root_module.addImport("hexdump", hexdump_module);
    hexdump_perf_root_module.addImport("phase6_hexdump_vectors", hexdump_vectors_module);
    const hexdump_perf_matrix_root_module = b.createModule(.{
        .root_source_file = b.path("phase6_hexdump_perf_matrix.zig"),
        .target = target,
        .optimize = optimize,
    });
    hexdump_perf_matrix_root_module.addImport("hexdump", hexdump_module);
    hexdump_perf_matrix_root_module.addImport("phase6_hexdump_vectors", hexdump_vectors_module);

    const base64_tests = b.addTest(.{ .name = "phase6-base64-tests", .root_module = base64_root_module });
    const run_base64_tests = b.addRunArtifact(base64_tests);
    run_base64_tests.skip_foreign_checks = true;

    const bsearch_tests = b.addTest(.{ .name = "phase6-bsearch-tests", .root_module = bsearch_root_module });
    const run_bsearch_tests = b.addRunArtifact(bsearch_tests);
    run_bsearch_tests.skip_foreign_checks = true;

    const bsearch_lower_bound_c_abi_tests = b.addTest(.{ .name = "phase6-bsearch-lower-bound-c-abi-tests", .root_module = bsearch_lower_bound_c_abi_root_module });
    const run_bsearch_lower_bound_c_abi_tests = b.addRunArtifact(bsearch_lower_bound_c_abi_tests);
    run_bsearch_lower_bound_c_abi_tests.skip_foreign_checks = true;

    const bsearch_c_abi_budget_tests = b.addTest(.{ .name = "phase6-bsearch-c-abi-budget-tests", .root_module = bsearch_c_abi_budget_root_module });
    const run_bsearch_c_abi_budget_tests = b.addRunArtifact(bsearch_c_abi_budget_tests);
    run_bsearch_c_abi_budget_tests.skip_foreign_checks = true;

    const checksum_tests = b.addTest(.{ .name = "phase6-checksum-tests", .root_module = checksum_root_module });
    const run_checksum_tests = b.addRunArtifact(checksum_tests);
    run_checksum_tests.skip_foreign_checks = true;

    const hexdump_tests = b.addTest(.{ .name = "phase6-hexdump-tests", .root_module = hexdump_root_module });
    const run_hexdump_tests = b.addRunArtifact(hexdump_tests);
    run_hexdump_tests.skip_foreign_checks = true;

    const hexdump_perf_matrix_tests = b.addTest(.{ .name = "phase6-hexdump-perf-matrix-tests", .root_module = hexdump_perf_matrix_root_module });
    const run_hexdump_perf_matrix_tests = b.addRunArtifact(hexdump_perf_matrix_tests);
    run_hexdump_perf_matrix_tests.skip_foreign_checks = true;

    const base64_perf = b.addExecutable(.{ .name = "phase6-base64-perf", .root_module = base64_perf_root_module });
    const run_base64_perf = b.addRunArtifact(base64_perf);
    run_base64_perf.skip_foreign_checks = true;

    const checksum_perf = b.addExecutable(.{ .name = "phase6-checksum-perf", .root_module = checksum_perf_root_module });
    const run_checksum_perf = b.addRunArtifact(checksum_perf);
    run_checksum_perf.skip_foreign_checks = true;

    const hexdump_perf = b.addExecutable(.{ .name = "phase6-hexdump-perf", .root_module = hexdump_perf_root_module });
    const run_hexdump_perf = b.addRunArtifact(hexdump_perf);
    run_hexdump_perf.skip_foreign_checks = true;

    const base64_test_step = b.step("phase6-base64-test", "Run Phase 6 base64 helper tests");
    base64_test_step.dependOn(&run_base64_tests.step);
    const bsearch_test_step = b.step("phase6-bsearch-test", "Run Phase 6 bsearch helper tests");
    bsearch_test_step.dependOn(&run_bsearch_tests.step);
    bsearch_test_step.dependOn(&run_bsearch_lower_bound_c_abi_tests.step);
    bsearch_test_step.dependOn(&run_bsearch_c_abi_budget_tests.step);
    const checksum_test_step = b.step("phase6-checksum-test", "Run Phase 6 checksum helper tests");
    checksum_test_step.dependOn(&run_checksum_tests.step);
    const hexdump_test_step = b.step("phase6-hexdump-test", "Run Phase 6 hexdump helper tests");
    hexdump_test_step.dependOn(&run_hexdump_tests.step);
    hexdump_test_step.dependOn(&run_hexdump_perf_matrix_tests.step);
    const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");
    hexdump_review_step.dependOn(&run_hexdump_perf_matrix_tests.step);
    const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 helper perf gate");
    base64_perf_step.dependOn(&run_base64_perf.step);
    const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");
    checksum_perf_step.dependOn(&run_checksum_perf.step);
    const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");
    hexdump_perf_step.dependOn(&run_hexdump_perf.step);
}
"""
MAKEFILE_SCAFFOLD = """PYTHON ?= python3
ZIG ?= zig
PHASE2_SCRIPT_ROOT := ../scripts/zigux
PHASE3_SCRIPT_ROOT := ../scripts/zigux
PHASE8_SCRIPT_ROOT := ../scripts/zigux
ZIGUX_ROOT := ..

.PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-validate phase2 phase3-validate phase3 phase3-export-uapi-layout-test phase6-base64-test phase6-base64-perf phase6-bsearch-test phase6-checksum-test phase6-checksum-perf phase6-hexdump-review phase6-hexdump-test phase6-hexdump-perf phase8-validate phase8-exec-cmd-test phase8-help-test phase8-help-kallsyms-test phase8-kallsyms-test phase8-libbpf-segments-test phase8-file-path-handle-bridge-test phase8-perf-buffer-poll-test phase8-test phase8 phase10-validate phase10-test phase10 phase12-smoke phase12-test phase12

phase6-base64-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-base64-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-base64-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-base64-perf --build-file zigux/tests/phase6_build.zig --summary all

phase6-bsearch-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-checksum-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-checksum-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig --summary all

phase6-hexdump-review:
	cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-hexdump-route.py

phase6-hexdump-test:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig --summary all

phase6-hexdump-perf:
	cd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig --summary all
"""
MANIFEST_SCAFFOLD = {
    "packet": "phase6-helper-evidence",
    "phase": "Phase 6",
    "surveyed_head": "61e026c",
    "lane_scope": "shared helper-evidence rows and machine-readable manifest only",
    "current_direct_readback_companions": REQUIRED_DIRECT_READBACK_COMPANIONS,
    "roadmap_anchors": EXPECTED_ROADMAP_ANCHORS,
    "helpers": EXPECTED_HELPERS,
    "current_repo_reality_gaps": EXPECTED_CURRENT_REPO_REALITY_GAPS,
    "current_shared_replay_inventory": EXPECTED_CURRENT_SHARED_REPLAY_INVENTORY,
}


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_snippets(path: Path, content: str, snippets: list[str]) -> None:
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(
                f"missing expected Phase 6 marker in {path.as_posix()}: {snippet}"
            )


def require_missing_paths(repo_root: Path, paths: list[str]) -> None:
    for relative_path in paths:
        if (repo_root / relative_path).exists():
            raise ValidationError(
                f"expected repo-reality gap path to remain absent: {relative_path}"
            )


def extract_catalog_surveyed_head(content: str) -> str:
    match = CATALOG_SURVEYED_HEAD_PATTERN.search(content)
    if match is None:
        raise ValidationError(
            f"missing expected Phase 6 marker in {HELPER_EVIDENCE_CATALOG_PATH.as_posix()}: - surveyed head: `<sha>`"
        )
    return match.group(1)


def validate(repo_root: Path) -> None:
    catalog_content = read_text(repo_root / HELPER_EVIDENCE_CATALOG_PATH)
    require_snippets(
        repo_root / HELPER_EVIDENCE_CATALOG_PATH,
        catalog_content,
        REQUIRED_CATALOG_SNIPPETS,
    )
    require_snippets(
        repo_root / PHASE6_BUILD_PATH,
        read_text(repo_root / PHASE6_BUILD_PATH),
        REQUIRED_BUILD_SNIPPETS,
    )
    require_snippets(
        repo_root / PHASE6_MAKEFILE_PATH,
        read_text(repo_root / PHASE6_MAKEFILE_PATH),
        REQUIRED_MAKEFILE_SNIPPETS,
    )
    catalog_head = extract_catalog_surveyed_head(catalog_content)
    manifest = json.loads(read_text(repo_root / HELPER_EVIDENCE_MANIFEST_PATH))
    if manifest["packet"] != EXPECTED_PACKET:
        raise ValidationError("Phase 6 helper manifest packet marker mismatch")
    if manifest["phase"] != EXPECTED_PHASE:
        raise ValidationError("Phase 6 helper manifest phase marker mismatch")
    if manifest["surveyed_head"] != catalog_head:
        raise ValidationError("surveyed-head mismatch")
    if manifest["lane_scope"] != EXPECTED_LANE_SCOPE:
        raise ValidationError("Phase 6 helper manifest lane-scope marker mismatch")
    if manifest["current_direct_readback_companions"] != REQUIRED_DIRECT_READBACK_COMPANIONS:
        raise ValidationError("Phase 6 direct-readback companions mismatch")
    if manifest["roadmap_anchors"] != EXPECTED_ROADMAP_ANCHORS:
        raise ValidationError("Phase 6 roadmap anchor packet mismatch")
    if manifest["helpers"] != EXPECTED_HELPERS:
        raise ValidationError("Phase 6 helper manifest helper packet mismatch")
    if manifest["current_repo_reality_gaps"] != EXPECTED_CURRENT_REPO_REALITY_GAPS:
        raise ValidationError("Phase 6 repo-reality gaps mismatch")
    if manifest["current_shared_replay_inventory"] != EXPECTED_CURRENT_SHARED_REPLAY_INVENTORY:
        raise ValidationError("Phase 6 shared replay inventory mismatch")
    require_missing_paths(repo_root, manifest["current_repo_reality_gaps"])
    for helper_path in REQUIRED_HELPER_PATHS:
        if not (repo_root / helper_path).is_file():
            raise ValidationError(f"missing required file: {helper_path.as_posix()}")


def scaffold_repo(root: Path) -> None:
    write(root / HELPER_EVIDENCE_CATALOG_PATH, CATALOG_SCAFFOLD)
    write(root / HELPER_EVIDENCE_MANIFEST_PATH, json.dumps(MANIFEST_SCAFFOLD, indent=2) + "\n")
    write(root / PHASE6_BUILD_PATH, BUILD_SCAFFOLD)
    write(root / PHASE6_MAKEFILE_PATH, MAKEFILE_SCAFFOLD)
    for helper_path in REQUIRED_HELPER_PATHS:
        write(root / helper_path, "// stub\n")


def expect_failure(root: Path, expected: str) -> None:
    try:
        validate(root)
    except (ValidationError, json.JSONDecodeError) as exc:
        if expected not in str(exc):
            raise AssertionError(
                f"expected {expected!r} in validation error, got {str(exc)!r}"
            ) from exc
    else:
        raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        cases_run = 0
        for snippet in (
            REQUIRED_CATALOG_SNIPPETS[2],
            REQUIRED_CATALOG_SNIPPETS[3],
            REQUIRED_CATALOG_SNIPPETS[8],
            REQUIRED_CATALOG_SNIPPETS[11],
        ):
            write(
                root / HELPER_EVIDENCE_CATALOG_PATH,
                read_text(root / HELPER_EVIDENCE_CATALOG_PATH).replace(
                    snippet + "\n", "", 1
                ),
            )
            expect_failure(root, snippet)
            cases_run += 1
            scaffold_repo(root)
        write(
            root / HELPER_EVIDENCE_CATALOG_PATH,
            read_text(root / HELPER_EVIDENCE_CATALOG_PATH).replace(
                "- surveyed head: `61e026c`\n", "", 1
            ),
        )
        expect_failure(root, "- surveyed head: `<sha>`")
        cases_run += 1
        scaffold_repo(root)
        for snippet in (
            REQUIRED_BUILD_SNIPPETS[0],
            REQUIRED_BUILD_SNIPPETS[8],
            REQUIRED_BUILD_SNIPPETS[14],
        ):
            write(
                root / PHASE6_BUILD_PATH,
                read_text(root / PHASE6_BUILD_PATH).replace(snippet + "\n", "", 1),
            )
            expect_failure(root, snippet)
            cases_run += 1
            scaffold_repo(root)
        for snippet in (
            REQUIRED_MAKEFILE_SNIPPETS[0],
            REQUIRED_MAKEFILE_SNIPPETS[2],
            REQUIRED_MAKEFILE_SNIPPETS[12],
        ):
            write(
                root / PHASE6_MAKEFILE_PATH,
                read_text(root / PHASE6_MAKEFILE_PATH).replace(snippet, "", 1),
            )
            expect_failure(root, snippet)
            cases_run += 1
            scaffold_repo(root)
        manifest = json.loads(read_text(root / HELPER_EVIDENCE_MANIFEST_PATH))
        manifest["current_direct_readback_companions"] = manifest[
            "current_direct_readback_companions"
        ][:-1]
        write(root / HELPER_EVIDENCE_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "direct-readback companions mismatch")
        cases_run += 1
        scaffold_repo(root)
        manifest = json.loads(read_text(root / HELPER_EVIDENCE_MANIFEST_PATH))
        manifest["current_repo_reality_gaps"] = manifest["current_repo_reality_gaps"][:-1]
        write(root / HELPER_EVIDENCE_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "repo-reality gaps mismatch")
        cases_run += 1
        scaffold_repo(root)
        manifest = json.loads(read_text(root / HELPER_EVIDENCE_MANIFEST_PATH))
        manifest["current_shared_replay_inventory"] = manifest[
            "current_shared_replay_inventory"
        ][:-1]
        write(root / HELPER_EVIDENCE_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "shared replay inventory mismatch")
        cases_run += 1
        scaffold_repo(root)
        manifest = json.loads(read_text(root / HELPER_EVIDENCE_MANIFEST_PATH))
        manifest["helpers"][3]["current_review_posture"] = "direct-helper-readback-restored"
        write(root / HELPER_EVIDENCE_MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")
        expect_failure(root, "helper packet mismatch")
        cases_run += 1
        scaffold_repo(root)
        write(root / EXPECTED_CURRENT_REPO_REALITY_GAPS[0], "# returned gap path\n")
        expect_failure(root, EXPECTED_CURRENT_REPO_REALITY_GAPS[0])
        cases_run += 1
        (root / EXPECTED_CURRENT_REPO_REALITY_GAPS[0]).unlink()
        scaffold_repo(root)
        write(root / HELPER_EVIDENCE_MANIFEST_PATH, "{\n")
        expect_failure(root, "Expecting property name enclosed in double quotes")
        cases_run += 1
        scaffold_repo(root)
        (root / PHASE6_MAKEFILE_PATH).unlink()
        expect_failure(root, PHASE6_MAKEFILE_PATH.as_posix())
        cases_run += 1
        scaffold_repo(root)
        (root / REQUIRED_HELPER_PATHS[0]).unlink()
        expect_failure(root, REQUIRED_HELPER_PATHS[0].as_posix())
        cases_run += 1
        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")
    print("PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST=pass")
    print(f"PHASE6_PRESENT_ENTRYPOINTS_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    try:
        validate(args.repo_root)
    except (ValidationError, json.JSONDecodeError) as exc:
        print(f"PHASE6_PRESENT_ENTRYPOINTS=fail: {exc}")
        return 1
    print("PHASE6_PRESENT_ENTRYPOINTS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
