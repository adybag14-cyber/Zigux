#!/usr/bin/env python3
"""Fail-closed Phase 6 shared-surface checks for the current leaf-helper packet."""

from __future__ import annotations

import argparse
import ast
import json
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
BASE64_C_PARITY_SCRIPT_PATH = Path("scripts/zigux/check-phase6-base64-c-parity.py")
HEXDUMP_PACKET_SCRIPT_PATH = Path("scripts/zigux/check-phase6-hexdump-packet.py")
HEXDUMP_PERF_MATRIX_PATH = Path("zigux/tests/phase6_hexdump_perf_matrix.zig")
CHECKSUM_C_PARITY_SCRIPT_PATH = Path("scripts/zigux/check-phase6-checksum-c-parity.py")
BSEARCH_CORPUS_EVIDENCE_SCRIPT_PATH = Path("scripts/zigux/check-phase6-bsearch-corpus-evidence.py")
PERF_THRESHOLD_SCRIPT_PATH = Path("scripts/zigux/check-phase6-perf-threshold-markers.py")
CATALOG_SURVEYED_HEAD_PREFIX = "- surveyed head: `"


REQUIRED_SNIPPETS = {
    "Documentation/zigux/phase6-helper-parity-catalog.md": [
        "# Phase 6 Helper Parity Catalog",
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_PACKET=base64-bsearch-checksum-hexdump`",
        "- surveyed head: `",
        "- dedicated perf replay: `zigux/tests/phase6_base64_perf.zig`",
        "- focused lower- and upper-bound C ABI replay: `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`",
        "- focused direct C ABI equality-budget replay: `zigux/tests/phase6_bsearch_c_abi_budget.zig`",
        "- fixtures: `zigux/tests/fixtures/phase6_bsearch_vectors.zig` for the bounded deterministic query-seeding and case-size corpus shared by the focused bsearch replays",
        "- exact corpus evidence: `zigux/tests/phase6_bsearch.zig` still anchors 15-element ascending and descending equality replays with five representative hit-or-miss probes each across typed and raw lookup paths, while `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` and `zigux/tests/phase6_bsearch_c_abi_budget.zig` still sweep dynamic lengths `0...32` plus packed-record `member_size` ranges under the same `std.math.log2_int_ceil(len) + 1` comparison budget",
        "- current review posture: functional parity plus bounded comparison-budget evidence inside the focused replay, alongside the dedicated corpus-evidence checker, the bounds-focused C ABI companion, and the dedicated direct C ABI equality-budget replay that keep the typed and raw lower-bound, upper-bound, and equality comparator contract reviewable without widening into a separate timing-style perf target in the shipped packet today",
        "- `make -C zigux phase6-hexdump-test`",
        "- `make -C zigux phase6-validate`",
        "- `make -C zigux phase6`",
        "- `make -C zigux phase6-base64-perf`",
        "- `make -C zigux phase6-checksum-perf`",
        "- `make -C zigux phase6-hexdump-perf`",
        "- `make -C zigux phase6-perf`",
    ],
    "Documentation/zigux/phase6-leaf-helper-lane-sequencing.md": [
        "# Phase 6 Leaf-Helper Lane Sequencing",
        "### `P6-L09` bsearch packet",
        "- `lib/bsearch.zig`",
        "- `zigux/tests/phase6_bsearch.zig`",
        "- `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`",
        "- `zigux/tests/phase6_bsearch_c_abi_budget.zig`",
        "- `Documentation/zigux/phase6-bsearch-slice.md`",
    ],
    "Documentation/zigux/phase6-base64-slice.md": [
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_SLICE=base64-leaf-helper`",
        "- `zigux/tests/phase6_base64_c_parity.zig`",
        "- `zigux/tests/fixtures/phase6_base64_c_harness.c`",
        "- `scripts/zigux/check-phase6-base64-c-parity.py`",
        "- a direct 24-case C-vs-Zig spot check covering representative std, URL-safe, and IMAP encode parity, decoded-byte parity, returned encoded-size parity through `chars`, returned decoded-size parity through `bytes`, and malformed-tail rejection through `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
    ],
    "Documentation/zigux/phase6-bsearch-slice.md": [
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_SLICE=bsearch-leaf-helper`",
        "- lane state: helper slice landed; parked unless a new `bsearch.c` parity, comparison-budget, lower- or upper-bound companion, or packet-alignment drift appears",
        "- `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`",
        "- `zigux/tests/phase6_bsearch_c_abi_budget.zig`",
        "- direct local rerun route: `zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig`",
        "- `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test`",
        "The current packet intentionally keeps its representative sorted inputs, deterministic query seeding, and case-size corpus inline in the focused `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, and `zigux/tests/phase6_bsearch_c_abi_budget.zig` replays so the helper bundle stays small and directly reviewable.",
        "The same packet still keeps its bounded comparison-budget evidence instead of a dedicated `phase6_bsearch_perf` route, and the dedicated bsearch-only rerun routes keep that packet reviewable without dragging the rest of the shared Phase 6 helper bundle into every follow-up.",
    ],
    "Documentation/zigux/phase6-checksum-slice.md": [
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_SLICE=checksum-leaf-helper`",
        "- fixture-backed carry-discipline and imported KUnit random-prefix replays for all-ones prefixes and no-spurious-carry seeded cases",
        "- IPv4 and IPv6 pseudo-header accumulation parity between the dedicated helper paths and manual `partial` plus `blockAdd` composition",
        "- incremental checksum replacement parity for payload word updates, 16-bit IPv4 header field replacement, diff-based checksum repair, and 32-bit IPv4 address replacement",
        "- `make -C zigux phase6-checksum-perf`",
    ],
    "Documentation/zigux/phase6-hexdump-slice.md": [
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_SLICE=hexdump-leaf-helper`",
        "- `zigux/tests/phase6_hexdump_perf_matrix.zig`",
        "- the non-truncating helper path now uses a direct full-buffer formatter so the grouped ASCII perf replays do not pay the truncating writer's per-byte bounds checks",
        "- a dedicated hexdump-only build step now reruns the focused helper replay while the helper-local perf gate keeps its threshold matrix preflight beside the ReleaseSafe slowdown replay",
        "- `make -C zigux phase6-hexdump-test`",
        "- `make -C zigux phase6-hexdump-perf`",
    ],
    "Documentation/zigux/phase6-perf-gate-survey.md": [
        "- `PHASE6_PERF_SURVEY_STATUS=active`",
        "- `PHASE6_PERF_PACKET=base64-bsearch-checksum-hexdump`",
        "- shared replay note: the shared `make -C zigux phase6` route still stops at `phase6-validate` plus `phase6-test`; dedicated perf replays remain helper-local through `make -C zigux phase6-base64-perf`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf`",
        "- aggregated route note: `make -C zigux phase6-perf` now exists as a narrow convenience wrapper for `phase6-base64-perf`, `phase6-checksum-perf`, and `phase6-hexdump-perf`, while the shared `make -C zigux phase6` route still excludes every helper-local slowdown gate",
        "- bsearch shared posture: the live executable measurement evidence remains the algorithmic comparison-budget replays inside `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, and `zigux/tests/phase6_bsearch_c_abi_budget.zig`, not a separate wall-clock perf harness",
        "- bsearch exact evidence: the current 15-element equality replay in `zigux/tests/phase6_bsearch.zig` still requires `counted_compare_calls <= 4` across five representative typed lookups and `counted_raw_compare_calls <= 4` across five representative raw lookups, while `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig` keeps the same expected `std.math.log2_int_ceil(len) + 1` insertion-point budget explicit for typed and raw lower-bound replays across ascending, descending, and packed-record ranges, and `zigux/tests/phase6_bsearch_c_abi_budget.zig` keeps that same equality budget explicit for typed and raw runtime-selected C ABI comparator replays across ascending, descending, and packed-record ranges without widening into standalone nanosecond thresholds",
        "- bsearch review-surface posture: `Documentation/zigux/phase6-bsearch-slice.md`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/phase6_build.zig`, and `zigux/Makefile` now agree that the shipped bsearch packet uses inline sorted inputs plus the bundled comparison-budget replays rather than a separate fixture module or standalone `phase6_bsearch_perf` route",
        "- the current bundled make routes now replay the three dedicated helper-local perf gates through `make -C zigux phase6-perf`, while the shared `make -C zigux phase6` route still stops at the shared checker plus bundled helper tests",
        "- the convenience `make -C zigux phase6-perf` route now truthfully summarizes that shared perf posture on `master` by aggregating the base64, checksum, and hexdump slowdown gates while leaving `bsearch` on its bounded comparison-budget evidence path",
    ],
    "Documentation/zigux/README.md": [
        "- `Documentation/zigux/phase6-base64-slice.md`",
        "- `Documentation/zigux/phase6-bsearch-slice.md`",
        "- `Documentation/zigux/phase6-checksum-slice.md`",
        "- `Documentation/zigux/phase6-hexdump-slice.md`",
        "make -C zigux phase6-perf",
        "the aggregate helper-local perf replay",
    ],
    "Documentation/zigux/review-checklist.md": [
        "Documentation/zigux/phase6-bsearch-slice.md",
        "scripts/zigux/check-phase6-shared-surface.py",
        "zigux/tests/phase6_bsearch.zig",
        "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
        "zigux/tests/phase6_bsearch_c_abi_budget.zig",
        "make -C zigux phase6-validate",
        "make -C zigux phase6",
        "make -C zigux phase6-perf",
        "while `bsearch` stays on its bounded comparison-budget evidence path",
    ],
    "scripts/zigux/README.md": [
        "- `check-phase6-shared-surface.py`",
        "- `check-phase6-hexdump-packet.py`",
        "- the current shared Phase 6 review surface on `master` is the four slice notes (`Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, and `Documentation/zigux/phase6-hexdump-slice.md`) plus `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
        "- `make -C zigux phase6-validate` keeps the shared Phase 6 surface checker wired through the Zigux convenience target.",
        "- `zig build test --build-file zigux/tests/phase6_build.zig` is the bundled helper replay for the current `base64`, `bsearch`, `checksum`, and `hexdump` packet.",
        "- `make -C zigux phase6-hexdump-review` keeps the dedicated hexdump packet checker, focused helper replay, and helper-local perf gate aligned on the same Linux-style wrapper route.",
    ],
    "scripts/zigux/check-phase6-base64-c-parity.py": [
        "EXPECTED_SORTED_LINES = sorted(",
        "print(f\"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}\")",
    ],
    "scripts/zigux/check-phase6-bsearch-corpus-evidence.py": [
        '"""Fail-closed exact evidence checks for the Phase 6 bsearch corpus packet."""',
        'MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")',
        'BSEARCH_PATH = Path("zigux/tests/phase6_bsearch.zig")',
        '"python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test",',
        '"python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py",',
    ],
    "scripts/zigux/check-phase6-hexdump-packet.py": [
        '"""Fail-closed checker for the bounded Phase 6 hexdump review packet."""',
        '"packet_checker": "scripts/zigux/check-phase6-hexdump-packet.py"',
        '"linux_review_route": "make -C zigux phase6-hexdump-review"',
        'print("PHASE6_HEXDUMP_PACKET_SELF_TEST=pass")',
    ],
    "scripts/zigux/check-phase6-perf-threshold-markers.py": [
        '"""Fail-closed checks for the current Phase 6 exact perf-threshold packet."""',
        'SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")',
        'BASE64_PERF_PATH = Path("zigux/tests/phase6_base64_perf.zig")',
        'CHECKSUM_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")',
        'HEXDUMP_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")',
    ],
    HEXDUMP_PERF_MATRIX_PATH.as_posix(): [
        'const fixtures = @import("phase6_hexdump_vectors");',
        '.label = "16B-plain-g1"',
        '.label = "32B-ascii-g2"',
        '.label = "16B-ascii-g4"',
        '.label = "16B-ascii-g8"',
        'return error.HexdumpPerfMatrixMismatch;',
        'test "phase 6 hexdump perf matrix preflight stays aligned with the documented packet" {',
    ],
    "zigux/tests/README.md": [
        "  * `zigux/tests/phase6_base64_perf.zig`",
        "  * `zigux/tests/phase6_checksum_perf.zig`",
        "  * `zigux/tests/phase6_hexdump_perf.zig`",
        "  * `zigux/tests/fixtures/phase6_bsearch_vectors.zig`",
        "  * keep the shared Phase 6 leaf-helper packet wired through `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, including `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `zigux/tests/phase6_checksum.zig`, and `zigux/tests/phase6_hexdump.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase6-validate`, and `make -C zigux phase6`, so the landed `base64`, `bsearch`, `checksum`, and `hexdump` bundle stays reviewable through one bounded helper gate, and keep `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/phase6_hexdump_perf.zig` explicit in the tests root so the shipped dedicated base64, checksum, and hexdump perf routes stay visible alongside the shared packet without implying that `make -C zigux phase6-perf` or `make -C zigux phase6` replays every helper-local slowdown gate",
        "  * keep `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, `zigux/tests/fixtures/phase6_hexdump_vectors.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig` explicit in the tests root too so the committed fixture-backed bsearch, checksum, hexdump, and base64 evidence stays reviewable from the same shared catalog instead of living only inside helper-local imports and slice prose",
    ],
    "zigux/tests/phase6_helper_parity_manifest.json": [
        "\"phase\": \"Phase 6\",",
        "\"tranche\": \"leaf-helper-parity\",",
        "\"surveyed_commit\": \"",
        "\"id\": \"base64\"",
        "\"zigux/tests/phase6_base64_c_parity.zig\"",
        "\"zigux/tests/fixtures/phase6_base64_c_harness.c\"",
        "\"scripts/zigux/check-phase6-base64-c-parity.py\"",
        "\"id\": \"bsearch\"",
        "\"zigux/tests/phase6_bsearch_lower_bound_c_abi.zig\"",
        "\"zigux/tests/phase6_bsearch_c_abi_budget.zig\"",
        "\"Documentation/zigux/phase6-helper-parity-catalog.md\",",
        "\"Documentation/zigux/phase6-perf-gate-survey.md\",",
        "\"Documentation/zigux/phase6-leaf-helper-lane-sequencing.md\",",
        "\"scripts/zigux/check-phase6-shared-surface.py\",",
        "\"zigux/tests/phase6_hexdump_perf_matrix.zig\"",
        "\"relative_slowdown_helpers\": [",
        "\"comparison_budget_helpers\": [",
        "\"fixture_posture\": {",
        "\"inline_corpus_governance\": {",
        "\"policy\": \"keep representative sorted slices, duplicate-bearing lower- and upper-bound insertion probes, direct c abi equality probes, and packed-record member_size cases inline in the focused bsearch replays instead of a separate Phase 6 fixture module\"",
        "\"lower_bound_budget_formula\": \"std.math.log2_int_ceil(len) + 1\"",
        "\"equality_budget_formula\": \"std.math.log2_int_ceil(len) + 1\"",
        "\"python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test\",",
        "\"python3 scripts/zigux/check-phase6-base64-c-parity.py\",",
        "\"make -C zigux phase6-base64-c-parity\",",
        "\"make -C zigux phase6-validate\",",
        "\"make -C zigux phase6\",",
        "\"make -C zigux phase6-bsearch-test\",",
        "\"python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test\",",
        "\"python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py\",",
        "\"make -C zigux phase6-checksum-c-parity\",",
        "\"make -C zigux phase6-hexdump-test\",",
        "\"make -C zigux phase6-perf\",",
        "\"make -C zigux phase6-base64-perf\",",
        "\"make -C zigux phase6-checksum-perf\",",
        "\"make -C zigux phase6-hexdump-perf\",",
        "\"python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test\",",
        "\"python3 scripts/zigux/check-phase6-checksum-c-parity.py\",",
        "\"python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test\"",
        "\"python3 scripts/zigux/check-phase6-perf-threshold-markers.py\"",
        "\"comparison_budget_max_compare_calls\": 4",
        "\"c_parity_cases\": 24",
        "\"generated_fixture_artifacts_committed\": false",
    ],
    "zigux/tests/phase6_build.zig": [
        'const test_step = b.step("test", "Run Phase 6 leaf helper tests");',
        '.root_source_file = b.path("phase6_bsearch_lower_bound_c_abi.zig"),',
        '.root_source_file = b.path("phase6_bsearch_c_abi_budget.zig"),',
        '.name = "phase6-base64-tests"',
        '.name = "phase6-bsearch-tests"',
        '.name = "phase6-bsearch-lower-bound-c-abi-tests"',
        '.name = "phase6-bsearch-c-abi-budget-tests"',
        'const bsearch_test_step = b.step("phase6-bsearch-test", "Run Phase 6 bsearch helper tests");',
        'bsearch_test_step.dependOn(&run_bsearch_tests.step);',
        'bsearch_test_step.dependOn(&run_bsearch_lower_bound_c_abi_tests.step);',
        'bsearch_test_step.dependOn(&run_bsearch_c_abi_budget_tests.step);',
        'test_step.dependOn(&run_bsearch_lower_bound_c_abi_tests.step);',
        'test_step.dependOn(&run_bsearch_c_abi_budget_tests.step);',
        'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 perf gate");',
        'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
        'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump perf gate");',
    ],
    "zigux/tests/phase6_bsearch.zig": [
        'test "phase 6 bsearch keeps representative lookup work inside a binary-search budget"',
        'test "phase 6 bsearch keeps descending lookup work inside a binary-search budget"',
        'test "phase 6 bsearch raw lookup keeps representative work inside a binary-search budget"',
        'test "phase 6 bsearch bounded typed and raw equality probes stay inside a binary-search budget"',
    ],
    "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig": [
        'test "phase 6 bsearch lower-bound helpers accept runtime-selected c abi comparator pointers"',
        'test "phase 6 bsearch lower-bound c abi helpers short-circuit empty input and keep singleton insertion edges bounded"',
        'test "phase 6 bsearch lower-bound c abi helpers match bounded insertion points across ascending and descending ranges"',
        'test "phase 6 bsearch lower-bound c abi record member_size replay stays inside a binary-search budget"',
    ],
    "zigux/tests/phase6_bsearch_c_abi_budget.zig": [
        'test "phase 6 bsearch direct c abi equality helpers stay inside a binary-search budget"',
    ],
    "zigux/Makefile": [
        "PHONY += phase6-validate phase6-test phase6-bsearch-test phase6-base64-c-parity phase6-checksum-c-parity phase6-hexdump-test phase6-hexdump-review phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6-perf phase6",
        "phase6-validate:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py",
        "phase6-test:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase6_build.zig",
        "phase6-bsearch-test:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig",
        "phase6-hexdump-review:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-hexdump-packet.py",
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
        "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "phase6-base64-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-base64-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "phase6-perf: phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf",
        "phase6-checksum-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "phase6-hexdump-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "phase6: phase6-validate phase6-test",
    ],
    ".github/workflows/zigux-bootstrap.yml": [
        "- name: Self-test Phase 6 shared-surface checker\n        run: python3 scripts/zigux/check-phase6-shared-surface.py --self-test",
        "- name: Check Phase 6 shared surface\n        run: python3 scripts/zigux/check-phase6-shared-surface.py",
        "- name: Run Phase 6 leaf helper tests\n        run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
        "- name: Run Phase 6 base64 perf gate\n        run: zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
        "- name: Run Phase 6 checksum perf gate\n        run: zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
        "- name: Run Phase 6 hexdump perf gate\n        run: zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
    ],
}

EXACT_OCCURRENCE_MARKERS = {
    "zigux/tests/phase6_bsearch.zig": [
        ("try std.testing.expect(counted_compare_calls <= 4);", 10),
        ("try std.testing.expect(counted_raw_compare_calls <= 4);", 10),
    ],
    "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig": [
        ("try std.testing.expect(typed_c_compare_calls <= 1);", 8),
        ("try std.testing.expect(raw_c_compare_calls <= 1);", 12),
        ("try std.testing.expect(typed_c_compare_calls <= budget);", 4),
        ("try std.testing.expect(raw_c_compare_calls <= budget);", 6),
    ],
    "zigux/tests/phase6_bsearch_c_abi_budget.zig": [
        ("try std.testing.expect(typed_c_compare_calls <= budget);", 2),
        ("try std.testing.expect(raw_c_compare_calls <= budget);", 3),
    ],
}

REMOVED_PATHS = [
    "scripts/zigux/validate-phase6.py",
    "zigux/tests/phase6_hexdump_c_parity.zig",
    "zigux/tests/fixtures/phase6_hexdump_c_harness.c",
    "scripts/zigux/check-phase6-hexdump-c-parity.py",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc


def validate_surveyed_head_alignment(repo_root: Path) -> None:
    manifest_rel = MANIFEST_PATH.as_posix()
    catalog_rel = CATALOG_PATH.as_posix()
    manifest_data = read_json(repo_root / manifest_rel)
    if not isinstance(manifest_data, dict):
        raise ValidationError(f"expected object in {manifest_rel}")
    surveyed_commit = manifest_data.get("surveyed_commit")
    if not isinstance(surveyed_commit, str) or not surveyed_commit:
        raise ValidationError(f"missing surveyed_commit in {manifest_rel}")
    catalog_content = read_text(repo_root / catalog_rel)
    expected_marker = f"{CATALOG_SURVEYED_HEAD_PREFIX}{surveyed_commit}`"
    occurrences = catalog_content.count(expected_marker)
    if occurrences != 1:
        raise ValidationError(f"expected exactly one surveyed-head marker in {catalog_rel}, found {occurrences}: {expected_marker}")


def extract_sorted_literal_list(script_text: str, rel_path: str, variable_name: str) -> list[object]:
    try:
        tree = ast.parse(script_text, filename=rel_path)
    except SyntaxError as exc:
        raise ValidationError(f"invalid Python in {rel_path}: {exc}") from exc
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == variable_name:
                value = node.value
                if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == "sorted" and len(value.args) == 1:
                    try:
                        literal = ast.literal_eval(value.args[0])
                    except (ValueError, SyntaxError) as exc:
                        raise ValidationError(f"{rel_path} keeps non-literal {variable_name}; expected a literal list") from exc
                    if not isinstance(literal, list):
                        raise ValidationError(f"{rel_path} keeps non-list {variable_name}; expected a literal list")
                    return literal
                raise ValidationError(f"{rel_path} keeps unsupported {variable_name} shape; expected sorted([...])")
    raise ValidationError(f"missing {variable_name} in {rel_path}")


def validate_parity_alignment(repo_root: Path, helper: str, script_path: Path, case_key: str, marker: str) -> None:
    manifest_rel = MANIFEST_PATH.as_posix()
    manifest_data = read_json(repo_root / manifest_rel)
    if not isinstance(manifest_data, dict):
        raise ValidationError(f"expected object in {manifest_rel}")
    determinism = manifest_data.get("determinism_evidence")
    if not isinstance(determinism, dict):
        raise ValidationError(f"missing determinism_evidence in {manifest_rel}")
    helper_data = determinism.get(helper)
    if not isinstance(helper_data, dict):
        raise ValidationError(f"missing determinism_evidence.{helper} in {manifest_rel}")
    case_count = helper_data.get(case_key)
    if not isinstance(case_count, int) or case_count <= 0:
        raise ValidationError(f"missing positive {helper} {case_key} in {manifest_rel}")
    script_rel = script_path.as_posix()
    script_text = read_text(repo_root / script_rel)
    if marker not in script_text:
        raise ValidationError(f"missing expected Phase 6 marker in {script_rel}: {marker}")
    expected_sorted_lines = extract_sorted_literal_list(script_text, script_rel, "EXPECTED_SORTED_LINES")
    expected_case_count = len(expected_sorted_lines)
    if case_count != expected_case_count:
        raise ValidationError(f"Phase 6 {helper} direct C parity case count drifted between {manifest_rel} ({case_count}) and {script_rel} ({expected_case_count})")


def run_checks(repo_root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        content = read_text(repo_root / rel_path)
        for snippet in snippets:
            if snippet not in content:
                raise ValidationError(f"missing expected Phase 6 marker in {rel_path}: {snippet}")
    validate_surveyed_head_alignment(repo_root)
    validate_parity_alignment(repo_root, "base64", BASE64_C_PARITY_SCRIPT_PATH, "c_parity_cases", 'PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}')
    validate_parity_alignment(repo_root, "checksum", CHECKSUM_C_PARITY_SCRIPT_PATH, "c_parity_cases", 'PHASE6_CHECKSUM_C_PARITY_CASES={len(c_lines)}')
    for rel_path, markers in EXACT_OCCURRENCE_MARKERS.items():
        content = read_text(repo_root / rel_path)
        for marker, expected in markers:
            occurrences = content.count(marker)
            if occurrences != expected:
                raise ValidationError(f"expected {expected} occurrences of Phase 6 marker in {rel_path}, found {occurrences}: {marker}")
    for rel_path in REMOVED_PATHS:
        if (repo_root / rel_path).exists():
            raise ValidationError(f"removed Phase 6 shared-surface file unexpectedly present: {rel_path}")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        if rel_path == MANIFEST_PATH.as_posix():
            manifest = {
                "phase": "Phase 6",
                "tranche": "leaf-helper-parity",
                "surveyed_commit": "277b3ab",
                "helpers": [
                    {"id": "base64", "helper": "lib/base64.zig", "tests": ["zigux/tests/phase6_base64.zig", "zigux/tests/phase6_base64_c_parity.zig", "zigux/tests/phase6_base64_perf.zig"], "fixtures": ["zigux/tests/fixtures/phase6_base64_vectors.zig", "zigux/tests/fixtures/phase6_base64_c_harness.c"], "slice_note": "Documentation/zigux/phase6-base64-slice.md", "external_parity": "scripts/zigux/check-phase6-base64-c-parity.py"},
                    {"id": "bsearch", "helper": "lib/bsearch.zig", "tests": ["zigux/tests/phase6_bsearch.zig", "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig", "zigux/tests/phase6_bsearch_c_abi_budget.zig"], "slice_note": "Documentation/zigux/phase6-bsearch-slice.md"},
                    {"id": "checksum", "helper": "lib/checksum.zig", "tests": ["zigux/tests/phase6_checksum.zig", "zigux/tests/phase6_checksum_perf.zig", "zigux/tests/phase6_checksum_c_parity.zig"], "fixtures": ["zigux/tests/fixtures/phase6_checksum_vectors.zig", "zigux/tests/fixtures/phase6_checksum_c_harness.c"], "slice_note": "Documentation/zigux/phase6-checksum-slice.md", "external_parity": "scripts/zigux/check-phase6-checksum-c-parity.py"},
                    {"id": "hexdump", "helper": "lib/hexdump.zig", "tests": ["zigux/tests/phase6_hexdump.zig", "zigux/tests/phase6_hexdump_perf.zig", "zigux/tests/phase6_hexdump_perf_matrix.zig"], "fixtures": ["zigux/tests/fixtures/phase6_hexdump_vectors.zig"], "slice_note": "Documentation/zigux/phase6-hexdump-slice.md", "packet_checker": "scripts/zigux/check-phase6-hexdump-packet.py", "linux_review_route": "make -C zigux phase6-hexdump-review"},
                ],
                "shared_gates": ["Documentation/zigux/phase6-helper-parity-catalog.md", "Documentation/zigux/phase6-perf-gate-survey.md", "Documentation/zigux/phase6-leaf-helper-lane-sequencing.md", "scripts/zigux/check-phase6-shared-surface.py", "zigux/Makefile"],
                "perf_posture": {"relative_slowdown_helpers": ["base64", "checksum", "hexdump"], "comparison_budget_helpers": ["bsearch"], "timing_sanity_only_helpers": []},
                "fixture_posture": {
                    "inline_corpus_governance": {
                        "bsearch": {
                            "focused_replay": "zigux/tests/phase6_bsearch.zig",
                            "lower_bound_c_abi_replay": "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
                            "upper_bound_c_abi_replay": "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
                            "equality_c_abi_replay": "zigux/tests/phase6_bsearch_c_abi_budget.zig",
                            "policy": "keep representative sorted slices, duplicate-bearing lower- and upper-bound insertion probes, direct c abi equality probes, and packed-record member_size cases inline in the focused bsearch replays instead of a separate Phase 6 fixture module",
                        }
                    }
                },
                "perf_thresholds": {"bsearch": {"lower_bound_budget_formula": "std.math.log2_int_ceil(len) + 1", "equality_budget_formula": "std.math.log2_int_ceil(len) + 1", "comparison_budget_max_compare_calls": 4}},
                "exact_checks": [
                    "python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test",
                    "python3 scripts/zigux/check-phase6-base64-c-parity.py",
                    "make -C zigux phase6-base64-c-parity",
                    "make -C zigux phase6-validate",
                    "make -C zigux phase6",
                    "make -C zigux phase6-bsearch-test",
                    "python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test",
                    "python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
                    "make -C zigux phase6-checksum-c-parity",
                    "make -C zigux phase6-hexdump-test",
                    "make -C zigux phase6-perf",
                    "make -C zigux phase6-base64-perf",
                    "make -C zigux phase6-checksum-perf",
                    "make -C zigux phase6-hexdump-perf",
                    "make -C zigux phase6-hexdump-review",
                    "python3 scripts/zigux/check-phase6-hexdump-packet.py --self-test",
                    "python3 scripts/zigux/check-phase6-hexdump-packet.py",
                    "python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test",
                    "python3 scripts/zigux/check-phase6-checksum-c-parity.py",
                    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test",
                    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py",
                ],
                "checksum_parity_replay": "python3 scripts/zigux/check-phase6-checksum-c-parity.py",
                "determinism_evidence": {
                    "base64": {"c_parity_cases": 24},
                    "bsearch": {"comparison_budget_max_compare_calls": 4},
                    "checksum": {"c_parity_cases": 41},
                    "generated_fixture_artifacts_committed": False,
                },
            }
            write(root / rel_path, json.dumps(manifest, indent=2) + "\n")
            continue
        if rel_path == CATALOG_PATH.as_posix():
            lines = list(dict.fromkeys(snippets))
            lines = ["- surveyed head: `277b3ab`" if line == "- surveyed head: `" else line for line in lines]
            write(root / rel_path, "\n".join(lines) + "\n")
            continue
        if rel_path == BASE64_C_PARITY_SCRIPT_PATH.as_posix():
            lines = ["EXPECTED_SORTED_LINES = sorted(", "    [", *[f'        \"case-{index:02d}\",' for index in range(1, 25)], "    ]", ")", 'print(f\"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}\")', ""]
            write(root / rel_path, "\n".join(lines))
            continue
        if rel_path == CHECKSUM_C_PARITY_SCRIPT_PATH.as_posix():
            lines = ["EXPECTED_SORTED_LINES = sorted(", "    [", *[f'        \"case-{index:02d}\",' for index in range(1, 42)], "    ]", ")", 'print(f\"PHASE6_CHECKSUM_C_PARITY_CASES={len(c_lines)}\")', ""]
            write(root / rel_path, "\n".join(lines))
            continue
        if rel_path == BSEARCH_CORPUS_EVIDENCE_SCRIPT_PATH.as_posix() or rel_path == PERF_THRESHOLD_SCRIPT_PATH.as_posix() or rel_path == HEXDUMP_PACKET_SCRIPT_PATH.as_posix():
            lines = list(dict.fromkeys(snippets))
            write(root / rel_path, "\n".join(lines) + "\n")
            continue
        lines = list(dict.fromkeys(snippets))
        for marker, expected in EXACT_OCCURRENCE_MARKERS.get(rel_path, []):
            lines.extend([marker] * expected)
        write(root / rel_path, "\n".join(lines) + "\n")
    checksum_script = root / CHECKSUM_C_PARITY_SCRIPT_PATH
    if not checksum_script.exists():
        lines = ["EXPECTED_SORTED_LINES = sorted(", "    [", *[f'        \"case-{index:02d}\",' for index in range(1, 42)], "    ]", ")", 'print(f\"PHASE6_CHECKSUM_C_PARITY_CASES={len(c_lines)}\")', ""]
        write(checksum_script, "\n".join(lines))


def assert_failure(root: Path, rel_path: str, old: str, new: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    try:
        run_checks(root)
    except ValidationError as exc:
        if rel_path not in str(exc):
            raise AssertionError(f"unexpected failure for {rel_path}: {exc}") from exc
    else:
        raise AssertionError(f"expected failure for {rel_path}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        run_checks(root)
        removed_path = root / REMOVED_PATHS[0]
        write(removed_path, "stale\n")
        try:
            run_checks(root)
        except ValidationError as exc:
            if REMOVED_PATHS[0] not in str(exc):
                raise AssertionError(f"unexpected removed-path failure: {exc}") from exc
        else:
            raise AssertionError("expected removed-path failure")
        removed_path.unlink()
        assert_failure(root, "Documentation/zigux/phase6-helper-parity-catalog.md", "- surveyed head: `277b3ab`", "- surveyed head: `deadbeef`")
        assert_failure(root, "zigux/tests/phase6_helper_parity_manifest.json", '"surveyed_commit": "277b3ab",', '"surveyed_commit": "",')
        assert_failure(root, "zigux/tests/phase6_helper_parity_manifest.json", 'check-phase6-bsearch-corpus-evidence.py --self-test', 'check-phase6-bsearch-corpus-proof.py --self-test')
        assert_failure(root, "zigux/tests/phase6_helper_parity_manifest.json", 'check-phase6-perf-threshold-markers.py --self-test', 'check-phase6-perf-threshold-proof.py --self-test')
        assert_failure(root, "zigux/tests/phase6_helper_parity_manifest.json", '"zigux/tests/phase6_hexdump_perf_matrix.zig"', '"zigux/tests/phase6_hexdump_matrix.zig"')
        assert_failure(root, "scripts/zigux/check-phase6-base64-c-parity.py", 'print(f\"PHASE6_BASE64_C_PARITY_CASES={len(c_lines)}\")', 'print(f\"PHASE6_BASE64_C_PARITY_COUNT={len(c_lines)}\")')
        assert_failure(root, "scripts/zigux/check-phase6-bsearch-corpus-evidence.py", 'BSEARCH_PATH = Path("zigux/tests/phase6_bsearch.zig")', 'BSEARCH_PATH = Path("zigux/tests/phase6_bsearch_probe.zig")')
        assert_failure(root, "scripts/zigux/check-phase6-checksum-c-parity.py", 'print(f\"PHASE6_CHECKSUM_C_PARITY_CASES={len(c_lines)}\")', 'print(f\"PHASE6_CHECKSUM_C_PARITY_COUNT={len(c_lines)}\")')
        assert_failure(root, "scripts/zigux/check-phase6-hexdump-packet.py", '"linux_review_route": "make -C zigux phase6-hexdump-review"', '"linux_review_route": "make -C zigux phase6-hexdump-test"')
        assert_failure(root, "scripts/zigux/check-phase6-perf-threshold-markers.py", 'SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")', 'SURVEY_PATH = Path("Documentation/zigux/phase6-perf-threshold-survey.md")')
        assert_failure(root, "Documentation/zigux/phase6-bsearch-slice.md", "deterministic query seeding, and case-size corpus inline", "deterministic query seeding only")
        assert_failure(root, "Documentation/zigux/phase6-helper-parity-catalog.md", "- current review posture: functional parity plus bounded comparison-budget evidence inside the focused replay, alongside the dedicated corpus-evidence checker, the bounds-focused C ABI companion, and the dedicated direct C ABI equality-budget replay that keep the typed and raw lower-bound, upper-bound, and equality comparator contract reviewable without widening into a separate timing-style perf target in the shipped packet today", "- current review posture: drifted")
        assert_failure(root, "Documentation/zigux/phase6-perf-gate-survey.md", "- bsearch review-surface posture: `Documentation/zigux/phase6-bsearch-slice.md`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/phase6_build.zig`, and `zigux/Makefile` now agree that the shipped bsearch packet uses inline sorted inputs plus the bundled comparison-budget replays rather than a separate fixture module or standalone `phase6_bsearch_perf` route", "- bsearch review-surface posture: drifted")
        assert_failure(root, "Documentation/zigux/phase6-hexdump-slice.md", "- `zigux/tests/phase6_hexdump_perf_matrix.zig`", "- `zigux/tests/phase6_hexdump_perf_gate.zig`")
        assert_failure(root, "Documentation/zigux/phase6-hexdump-slice.md", "- a dedicated hexdump-only build step now reruns the focused helper replay while the helper-local perf gate keeps its threshold matrix preflight beside the ReleaseSafe slowdown replay", "- a dedicated hexdump-only build step now reruns the focused helper replay")
        assert_failure(root, "scripts/zigux/README.md", '`make -C zigux phase6-hexdump-review` keeps the dedicated hexdump packet checker, focused helper replay, and helper-local perf gate aligned on the same Linux-style wrapper route.', '`make -C zigux phase6-hexdump-test` keeps the focused hexdump replay explicit.')
        assert_failure(root, "zigux/tests/phase6_hexdump_perf_matrix.zig", 'test "phase 6 hexdump perf matrix preflight stays aligned with the documented packet" {', 'test "phase 6 hexdump perf matrix drifted" {')
        assert_failure(root, "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig", "try std.testing.expect(raw_c_compare_calls <= budget);", "try std.testing.expect(raw_c_compare_calls <= budget + 1);")
        assert_failure(root, "zigux/tests/phase6_bsearch_c_abi_budget.zig", "try std.testing.expect(raw_c_compare_calls <= budget);", "try std.testing.expect(raw_c_compare_calls <= budget + 1);")
        assert_failure(root, "zigux/tests/phase6_build.zig", '.name = "phase6-bsearch-c-abi-budget-tests"', '.name = "phase6-bsearch-c-abi-tests"')
        assert_failure(root, "zigux/Makefile", 'phase6-hexdump-review:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-hexdump-packet.py', 'phase6-hexdump-review:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-hexdump-review.py')
    print("self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    run_checks(Path(args.repo_root).resolve())
    print("Phase 6 shared surface looks aligned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
