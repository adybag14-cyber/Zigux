#!/usr/bin/env python3
"""Fail-closed Phase 6 shared-surface checks for the current leaf-helper packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


REQUIRED_SNIPPETS = {
    "Documentation/zigux/README.md": [
        "- `Documentation/zigux/phase6-base64-slice.md`",
        "- `Documentation/zigux/phase6-bsearch-slice.md`",
        "- `Documentation/zigux/phase6-checksum-slice.md`",
        "- `Documentation/zigux/phase6-hexdump-slice.md`",
        "- `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, and `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/phase6_hexdump_perf.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `make -C zigux phase6-validate`, and `make -C zigux phase6`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf` now keep the current base64, bsearch, checksum, and hexdump helper bundle reviewable",
        "- the current bounded Phase 6 decision is no longer whether one more tiny external fixture is still worth carrying; the live leaf-helper lane is the bundled `base64`, `bsearch`, `checksum`, and `hexdump` packet already kept reviewable through `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, and `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/phase6_hexdump_perf.zig`, `make -C zigux phase6`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf`, so future follow-up here should reopen only for a concrete parity gap or another similarly small helper-first step inside that same packet.",
    ],
    "scripts/zigux/README.md": [
        "- `check-phase6-shared-surface.py`",
        "- the current shared Phase 6 review surface on `master` is the four slice notes (`Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, and `Documentation/zigux/phase6-hexdump-slice.md`) plus `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
        "- `make -C zigux phase6-validate` keeps the shared Phase 6 surface checker wired through the Zigux convenience target.",
        "- `zig build test --build-file zigux/tests/phase6_build.zig` is the bundled helper replay for the current `base64`, `bsearch`, `checksum`, and `hexdump` packet.",
        "- there is no separate shared `validate-phase6.py` or broader external portability checker packet beyond `check-phase6-shared-surface.py` on `master`; the shipped dedicated perf replays are `make -C zigux phase6-base64-perf`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf`, while `make -C zigux phase6-perf` remains the narrow aggregate route for the checksum and hexdump perf packet rather than a bundle-wide Phase 6 perf closure",
    ],
    "Documentation/zigux/review-checklist.md": [
        "  * if the change touches the shared Phase 6 leaf-helper packet, do `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-bsearch-slice.md`, `Documentation/zigux/phase6-checksum-slice.md`, `Documentation/zigux/phase6-hexdump-slice.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_hexdump_perf.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase6-validate`, `make -C zigux phase6`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf` still agree on the same bundled `base64`, `bsearch`, `checksum`, and `hexdump` helper packet without implying a removed shared `validate-phase6.py`, a broader external parity checker beyond `check-phase6-shared-surface.py`, or an aggregated `phase6-perf` route?",
    ],
    "zigux/tests/README.md": [
        "  * `zigux/tests/phase6_base64_perf.zig`",
        "  * `zigux/tests/fixtures/phase6_base64_vectors.zig`",
        "  * `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
        "  * `zigux/tests/fixtures/phase6_hexdump_vectors.zig`",
        "  * `zigux/tests/phase6_checksum_perf.zig`",
        "  * `zigux/tests/phase6_hexdump_perf.zig`",
        "  * keep the shared Phase 6 leaf-helper packet wired through `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/phase6_build.zig`, including `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_checksum.zig`, and `zigux/tests/phase6_hexdump.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase6-validate`, and `make -C zigux phase6`, so the landed `base64`, `bsearch`, `checksum`, and `hexdump` bundle stays reviewable through one bounded helper gate, and keep `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/phase6_hexdump_perf.zig` explicit in the tests root so the shipped dedicated base64, checksum, and hexdump perf routes stay visible alongside the shared packet without implying that `make -C zigux phase6-perf` or `make -C zigux phase6` replays every helper-local slowdown gate",
    ],
    "Documentation/zigux/phase6-helper-parity-catalog.md": [
        "# Phase 6 Helper Parity Catalog",
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_PACKET=base64-bsearch-checksum-hexdump`",
        "- shared packet manifest: `zigux/tests/phase6_helper_parity_manifest.json`",
        "- dedicated perf replay: `zigux/tests/phase6_base64_perf.zig`",
        "- current review posture: functional parity plus bounded comparison-budget evidence inside the focused replay; there is no separate timing-style perf target in the shipped packet today",
        "- current review posture: helper parity plus the shipped dedicated slowdown gate exposed through `make -C zigux phase6-checksum-perf`",
        "- current review posture: helper parity plus the shipped formatter-sensitive slowdown gate exposed through `make -C zigux phase6-hexdump-perf`",
        "- `make -C zigux phase6-validate`",
        "- `make -C zigux phase6`",
        "- `make -C zigux phase6-base64-perf`",
        "- `make -C zigux phase6-checksum-perf`",
        "- `make -C zigux phase6-hexdump-perf`",
        "- `make -C zigux phase6-perf`",
    ],
    "zigux/tests/phase6_helper_parity_manifest.json": [
        "\"phase\": \"Phase 6\",",
        "\"tranche\": \"leaf-helper-parity\",",
        "\"surveyed_commit\": \"\",",
        "\"id\": \"base64\"",
        "\"id\": \"bsearch\"",
        "\"id\": \"checksum\"",
        "\"id\": \"hexdump\"",
        "\"Documentation/zigux/phase6-helper-parity-catalog.md\",",
        "\"Documentation/zigux/phase6-perf-gate-survey.md\",",
        "\"scripts/zigux/check-phase6-shared-surface.py\",",
        "\"make -C zigux phase6-validate\",",
        "\"make -C zigux phase6\",",
        "\"make -C zigux phase6-perf\",",
        "\"make -C zigux phase6-base64-perf\",",
        "\"make -C zigux phase6-checksum-perf\",",
        "\"make -C zigux phase6-hexdump-perf\",",
        "\"generated_fixture_artifacts_committed\": false",
    ],
    "Documentation/zigux/phase6-base64-slice.md": [
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_SLICE=base64-leaf-helper`",
        "- lane state: helper, fixture, and dedicated perf slice landed; parked unless a new helper-local parity or slowdown issue appears",
        "- `Variant.imap`",
        "- fixture-backed decode-length parity through `bytes` across the full committed valid std, URL-safe, and IMAP decode corpus",
        "- invalid-input rejection through both `bytes` and `decode` for malformed, embedded-NUL, and variant-mismatched decode inputs",
        "- exhaustive canonical tail acceptance for padded and unpadded std, URL-safe, and IMAP decode paths",
    ],
    "Documentation/zigux/phase6-bsearch-slice.md": [
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_SLICE=bsearch-leaf-helper`",
        "- lane state: helper slice landed; parked unless a new `bsearch.c` parity, comparison-budget, or packet-alignment drift appears",
        "- `searchIndex`",
        "- `search`",
        "- `searchMutable`",
        "- `bsearchIndex`",
        "- `bsearch`",
        "- `bsearchMutable`",
        "- mutable typed and raw lookup write-through parity",
        "- runtime-selected raw C ABI comparator pointer parity, including descending-order lookup, pointer-return duplicate hits, mutable write-through, and null misses",
        "The current packet intentionally keeps its representative sorted inputs inline in `zigux/tests/phase6_bsearch.zig` instead of a separate fixture module so the helper bundle stays small and directly reviewable.",
    ],
    "Documentation/zigux/phase6-checksum-slice.md": [
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_SLICE=checksum-leaf-helper`",
        "- lane state: helper, fixture, perf, and direct C parity slice landed; parked unless a new `checksum.c` parity issue appears",
        "- `zigux/tests/phase6_checksum_c_parity.zig`",
        "- `zigux/tests/fixtures/phase6_checksum_c_harness.c`",
        "- `scripts/zigux/check-phase6-checksum-c-parity.py`",
        "- `python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test`",
        "- `ZIG=zig python3 scripts/zigux/check-phase6-checksum-c-parity.py`",
        "- `replaceByDiff`",
        "- `compute`",
        "- fixture-backed checksum vectors for empty, even, odd, and carry-heavy inputs",
        "- incremental partial-sum chaining across even and odd fragment boundaries",
        "- non-zero seeded `partial` accumulation parity across odd, carry-heavy, and pre-folded seed inputs",
        "- a tiny KUnit-inspired carry-discipline matrix covering all-ones and no-spurious-carry seeded cases",
        "- pseudo-header accumulation parity between `tcpUdpNofold` and manual `partial` plus `blockAdd`",
        "- incremental checksum replacement parity for payload word updates, 16-bit IPv4 header field replacement, diff-based checksum repair, and 32-bit IPv4 address replacement",
        "- a direct 30-case C-vs-Zig replay for compute, seeded partial, composition, IPv4 and IPv6 pseudo-header, direct `negate`, direct `from32to16` and `fold`, and incremental replacement behavior",
        "- helper-local perf smoke on patterned 64-byte and 1501-byte payloads keeps `checksum.compute` within a 150% slowdown ceiling versus the bounded reference loop",
    ],
    "Documentation/zigux/phase6-hexdump-slice.md": [
        "- `PHASE6_STATUS=parked`",
        "- `PHASE6_SLICE=hexdump-leaf-helper`",
        "- lane state: helper, fixture, and dedicated perf gate slice landed; parked unless a new `hexdump.c` parity or perf-threshold issue appears",
        "- `hexDumpToBuffer`",
        "- serialized required-length vectors for `hexDumpLineLength` and zero-buffer `hexDumpToBuffer`",
        "- a dedicated perf replay that benchmarks the existing four-case perf fixture packet against the committed `fixtures.prepareExpectedLine(...)` reference path",
        "- `16B-plain-g1`",
        "- `32B-ascii-g2`",
        "- `16B-ascii-g4`",
        "- `16B-ascii-g8`",
    ],
    "Documentation/zigux/phase6-perf-gate-survey.md": [
        "- `PHASE6_PERF_SURVEY_STATUS=active`",
        "- `PHASE6_PERF_PACKET=base64-bsearch-checksum-hexdump`",
        "- shared replay note: the shared `make -C zigux phase6` route still stops at `phase6-validate` plus `phase6-test`; dedicated perf replays remain helper-local through `make -C zigux phase6-base64-perf`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf`",
        "- aggregated route note: `make -C zigux phase6-perf` now exists as a narrow convenience wrapper for `phase6-checksum-perf` plus `phase6-hexdump-perf`; it still excludes base64 even though `.github/workflows/zigux-bootstrap.yml` reruns `phase6-base64-perf` directly in CI",
        "- base64 shared posture: `zigux/tests/phase6_base64_perf.zig` still emits dedicated encode and decode slowdown markers for four fixture-backed replay cases, `zigux/tests/phase6_build.zig` still defines `phase6-base64-perf`, `zigux/Makefile` still exposes `make -C zigux phase6-base64-perf`, and `.github/workflows/zigux-bootstrap.yml` now reruns that base64 perf gate as its own direct CI step, while the shared `phase6` target and aggregate `phase6-perf` route still do not",
        "- base64 exact thresholds: `zigux/tests/fixtures/phase6_base64_vectors.zig` still pins four perf cases (`STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, and `URLSAFE_NO_PAD`) at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`",
        "- bsearch shared posture: the live executable measurement evidence remains the algorithmic comparison-budget replay inside `zigux/tests/phase6_bsearch.zig`, not a separate wall-clock perf harness",
        "- bsearch exact evidence: the current 15-element typed and raw replay packet still requires `counted_compare_calls <= 4` across five representative typed lookups and `counted_raw_compare_calls <= 4` across five representative raw lookups, which keeps the packet aligned with the expected `std.math.log2_int_ceil(len) + 1` search budget without widening into standalone nanosecond thresholds",
        "- bsearch review-surface posture: `Documentation/zigux/phase6-bsearch-slice.md`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_build.zig`, and `zigux/Makefile` now agree that the shipped bsearch packet uses inline sorted inputs plus the bundled comparison-budget replay rather than a separate fixture module or standalone `phase6_bsearch_perf` route",
        "- checksum shared posture: a dedicated slowdown gate remains wired through `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`",
        "- hexdump shared posture: a dedicated slowdown gate remains wired through `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`",
        "- the bundled `phase6` and aggregate `phase6-perf` make routes still replay only the shared helper tests plus the checksum and hexdump dedicated perf gates, while `.github/workflows/zigux-bootstrap.yml` separately reruns the base64 perf gate as its own direct CI step",
    ],
    "zigux/tests/phase6_build.zig": [
        'const test_step = b.step("test", "Run Phase 6 leaf helper tests");',
        '.name = "phase6-base64-tests"',
        '.name = "phase6-base64-perf"',
        '.name = "phase6-bsearch-tests"',
        '.name = "phase6-checksum-tests"',
        '.name = "phase6-hexdump-tests"',
        '.name = "phase6-checksum-perf"',
        '.name = "phase6-hexdump-perf"',
        'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 perf gate");',
        'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
        'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump perf gate");',
    ],
    "zigux/tests/phase6_base64.zig": [
        'const fixtures = @import("fixtures/phase6_base64_vectors.zig");',
        "for (fixtures.standard_cases) |case| {",
        "for (fixtures.variant_cases) |case| {",
        "for (fixtures.standard_decode_cases) |case| {",
        "for (fixtures.invalid_decode_cases) |case| {",
        "for (fixtures.variant_decode_cases) |case| {",
        'test "phase 6 base64 variant decode parity keeps bytes and decode aligned with kernel mappings"',
    ],
    "zigux/tests/phase6_base64_perf.zig": [
        'const fixtures = @import("fixtures/phase6_base64_vectors.zig");',
        'fn runHelperEncodeBench(case: fixtures.PerfCase, variant: base64.Variant) !BenchResult {',
        'for (fixtures.perf_cases) |case| {',
        'const variant = fixtureVariant(case.variant_name);',
        'try stdout_writer.interface.print("PHASE6_BASE64_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
        'try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_ENCODE_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_encode_slowdown_pct });',
        'try stdout_writer.interface.print("PHASE6_BASE64_PERF_{s}_DECODE_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_decode_slowdown_pct });',
    ],
    "zigux/tests/fixtures/phase6_base64_vectors.zig": [
        "pub const standard_cases = [_]EncodeCase{",
        "pub const variant_cases = [_]VariantCase{",
        ' .{ .expected = "APv,f4A=", .variant_name = "imap", .padding = true },',
        "pub const invalid_decode_cases = [_]InvalidDecodeCase{",
        "pub const variant_decode_cases = [_]DecodeCase{",
        "pub const perf_cases = [_]PerfCase{",
        '.label = "URLSAFE_NO_PAD"',
    ],
    "zigux/tests/phase6_bsearch.zig": [
        'test "phase 6 bsearch mutable typed lookup supports write-through"',
        'test "phase 6 bsearch treats duplicate keys as found-or-null without claiming stable selection"',
        'test "phase 6 bsearch accepts runtime-selected raw c abi comparator pointers"',
        'test "phase 6 bsearch mutable raw c abi lookup supports write-through"',
        'test "phase 6 bsearch keeps representative lookup work inside a binary-search budget"',
        'test "phase 6 bsearch keeps descending lookup work inside a binary-search budget"',
        'test "phase 6 bsearch raw lookup keeps representative work inside a binary-search budget"',
        'test "phase 6 bsearch bounded typed and raw equality probes stay inside a binary-search budget"',
    ],
    "zigux/tests/phase6_checksum.zig": [
        'const fixtures = @import("fixtures/phase6_checksum_vectors.zig");',
        'test "partial sums compose across the fixture split matrix"',
        'test "fixture-backed negate cases keep the public checksum helper reviewable"',
        'test "pseudo header accumulation matches the fixture-backed reference checksum"',
        'test "incremental checksum replacement helpers match direct recomputation"',
    ],
    "zigux/tests/phase6_checksum_perf.zig": [
        'const fixtures = @import("fixtures/phase6_checksum_vectors.zig");',
        'try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
        'try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}_SLOWDOWN_PCT={d}\\n", .{ case.label, slowdown_pct });',
        'try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct });',
        'try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF_{s}_CHECKSUM={d}\\n", .{ case.label, helper_result.checksum_accumulator });',
        'try stdout_writer.interface.print("PHASE6_CHECKSUM_PERF={s}\\n", .{if (failed) "fail" else "pass"});',
    ],
    "zigux/tests/fixtures/phase6_checksum_vectors.zig": [
        "pub const compute_cases = [_]ComputeCase{",
        ' .name = "carry-heavy payload"',
        "pub const composition_cases = [_]CompositionCase{",
        ' .name = "odd split"',
        "pub const negate_cases = [_]NegateCase{",
        ' .name = "mixed payload preserves ones complement carry"',
        "pub const perf_cases = [_]PerfCase{",
        ' .label = "64B"',
        ' .label = "1501B"',
    ],
    "zigux/tests/phase6_hexdump.zig": [
        'test "phase 6 hexdump serialized linux-derived vectors stay in sync"',
        'test "phase 6 hexdump serialized overflow vectors stay in sync"',
        'test "phase 6 hexdump serialized required-length vectors stay in sync"',
        'test "phase 6 hexdump perf fixture packet stays in sync"',
        'test "phase 6 hexdump covers normalization and empty-buffer edge cases"',
    ],
    "zigux/tests/phase6_hexdump_perf.zig": [
        'const fixtures = @import("phase6_hexdump_vectors");',
        'for (fixtures.perf_cases) |case| {',
        'const expected = fixtures.prepareExpectedLine(',
        'try std.testing.expectEqual(fixtures.expectedLength(case.len, case.rowsize, case.groupsize, case.ascii), required);',
        'try std.testing.expectEqualSlices(u8, expected, std.mem.sliceTo(helper_line[0..], 0));',
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_SLOWDOWN_PCT={d}\\n", .{ case.label, slowdown_pct });',
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct });',
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF={s}\\n", .{if (failed) "fail" else "pass"});',
    ],
    "zigux/tests/fixtures/phase6_hexdump_vectors.zig": [
        "pub const perf_cases = [_]PerfCase{",
        '.label = "16B-plain-g1"',
        '.label = "32B-ascii-g2"',
        '.label = "16B-ascii-g4"',
        '.label = "16B-ascii-g8"',
        ".max_slowdown_pct = 175,",
        ".max_slowdown_pct = 550,",
        ".max_slowdown_pct = 600,",
    ],
    "zigux/Makefile": [
        "PHONY += phase6-validate phase6-test phase6-perf phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6",
        "phase6-validate:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py",
        "phase6-test:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase6_build.zig",
        "phase6-base64-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-base64-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "phase6-perf: phase6-checksum-perf phase6-hexdump-perf",
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

EXACT_COUNT_MARKERS = {
    "Documentation/zigux/phase6-helper-parity-catalog.md": [
        "### base64",
        "### bsearch",
        "### checksum",
        "### hexdump",
    ],
    "zigux/tests/phase6_helper_parity_manifest.json": [
        "\"id\": \"base64\"",
        "\"id\": \"bsearch\"",
        "\"id\": \"checksum\"",
        "\"id\": \"hexdump\"",
        "\"timing_sanity_only_helpers\": []",
        "\"generated_fixture_artifacts_committed\": false",
    ],
    "zigux/Makefile": [
        "PHONY += phase6-validate phase6-test phase6-perf phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6",
        "phase6-validate:\n\tcd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase6-shared-surface.py",
        "phase6-test:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build test --build-file zigux/tests/phase6_build.zig",
        "phase6-base64-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-base64-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        "phase6-perf: phase6-checksum-perf phase6-hexdump-perf",
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
    "zigux/tests/fixtures/phase6_base64_vectors.zig": [
        (".max_encode_slowdown_pct = 150,", 4),
        (".max_decode_slowdown_pct = 325,", 4),
    ],
    "zigux/tests/fixtures/phase6_checksum_vectors.zig": [
        (".max_slowdown_pct = 150,", 2),
    ],
    "zigux/tests/phase6_bsearch.zig": [
        ("try std.testing.expect(counted_compare_calls <= 4);", 10),
        ("try std.testing.expect(counted_raw_compare_calls <= 4);", 10),
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


def run_checks(repo_root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        content = read_text(repo_root / rel_path)
        for snippet in snippets:
            if snippet not in content:
                raise ValidationError(
                    f"missing expected Phase 6 marker in {rel_path}: {snippet}"
                )

    for rel_path, markers in EXACT_COUNT_MARKERS.items():
        content = read_text(repo_root / rel_path)
        for marker in markers:
            occurrences = content.count(marker)
            if occurrences != 1:
                raise ValidationError(
                    f"expected exactly one Phase 6 marker in {rel_path}, found {occurrences}: {marker}"
                )

    for rel_path, markers in EXACT_OCCURRENCE_MARKERS.items():
        content = read_text(repo_root / rel_path)
        for marker, expected in markers:
            occurrences = content.count(marker)
            if occurrences != expected:
                raise ValidationError(
                    f"expected {expected} occurrences of Phase 6 marker in {rel_path}, found {occurrences}: {marker}"
                )

    for rel_path in REMOVED_PATHS:
        if (repo_root / rel_path).exists():
            raise ValidationError(
                f"removed Phase 6 shared-surface file unexpectedly present: {rel_path}"
            )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        lines = list(dict.fromkeys(snippets + EXACT_COUNT_MARKERS.get(rel_path, [])))
        for marker, expected in EXACT_OCCURRENCE_MARKERS.get(rel_path, []):
            lines.extend([marker] * expected)
        write(root / rel_path, "\n".join(lines) + "\n")


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

        assert_failure(
            root,
            "Documentation/zigux/phase6-helper-parity-catalog.md",
            "- `PHASE6_PACKET=base64-bsearch-checksum-hexdump`",
            "- `PHASE6_PACKET=base64-checksum-hexdump`",
        )
        assert_failure(
            root,
            "Documentation/zigux/phase6-helper-parity-catalog.md",
            "### checksum",
            "### sumcheck",
        )
        assert_failure(
            root,
            "zigux/tests/phase6_helper_parity_manifest.json",
            "\"tranche\": \"leaf-helper-parity\",",
            "\"tranche\": \"leaf-helper\",",
        )
        assert_failure(
            root,
            "zigux/tests/phase6_helper_parity_manifest.json",
            "\"make -C zigux phase6-perf\",",
            "\"make -C zigux phase6-bsearch-perf\",",
        )
        assert_failure(
            root,
            "Documentation/zigux/phase6-base64-slice.md",
            "helper, fixture, and dedicated perf slice landed",
            "helper and fixture slice landed",
        )
        assert_failure(
            root,
            "Documentation/zigux/phase6-bsearch-slice.md",
            "lane state: helper slice landed; parked unless a new `bsearch.c` parity, comparison-budget, or packet-alignment drift appears",
            "lane state: helper slice landed; parked unless a new `bsearch.c` parity issue appears",
        )
        assert_failure(
            root,
            "Documentation/zigux/phase6-checksum-slice.md",
            "`scripts/zigux/check-phase6-checksum-c-parity.py`",
            "`scripts/zigux/check-phase6-checksum-parity.py`",
        )
        assert_failure(
            root,
            "Documentation/zigux/phase6-checksum-slice.md",
            "incremental partial-sum chaining across even and odd fragment boundaries",
            "partial sums compose across the fixture split matrix",
        )
        assert_failure(
            root,
            "Documentation/zigux/phase6-hexdump-slice.md",
            "lane state: helper, fixture, and dedicated perf gate slice landed; parked unless a new `hexdump.c` parity or perf-threshold issue appears",
            "lane state: helper, fixture, dedicated perf gate, and external parity slices landed; parked unless a new `hexdump.c` parity issue appears",
        )
        assert_failure(
            root,
            "zigux/tests/phase6_base64_perf.zig",
            'const fixtures = @import("fixtures/phase6_base64_vectors.zig");',
            'const fixtures = @import("fixtures/phase6_base64_inline_perf.zig");',
        )
        assert_failure(
            root,
            "zigux/tests/phase6_base64_perf.zig",
            'for (fixtures.perf_cases) |case| {',
            'for (inline_perf_cases) |case| {',
        )
        assert_failure(
            root,
            "zigux/tests/phase6_hexdump_perf.zig",
            'const fixtures = @import("phase6_hexdump_vectors");',
            'const fixtures = @import("phase6_hexdump_inline_cases");',
        )
        assert_failure(
            root,
            "zigux/tests/phase6_hexdump_perf.zig",
            'for (fixtures.perf_cases) |case| {',
            'for (inline_perf_cases) |case| {',
        )
        assert_failure(
            root,
            "Documentation/zigux/phase6-perf-gate-survey.md",
            "`zigux/tests/phase6_build.zig` still defines `phase6-base64-perf`, `zigux/Makefile` still exposes `make -C zigux phase6-base64-perf`, and `.github/workflows/zigux-bootstrap.yml` now reruns that base64 perf gate as its own direct CI step, while the shared `phase6` target and aggregate `phase6-perf` route still do not",
            "`zigux/tests/phase6_build.zig` still defines `phase6-base64-perf`, but no shared replay surface reruns that base64 perf gate anywhere on current `master`",
        )
        assert_failure(
            root,
            ".github/workflows/zigux-bootstrap.yml",
            "- name: Run Phase 6 base64 perf gate\n        run: zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
            "- name: Run Phase 6 base64 bench\n        run: zig build phase6-base64-bench --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
        )
        assert_failure(
            root,
            "Documentation/zigux/phase6-perf-gate-survey.md",
            "`make -C zigux phase6-perf` now exists as a narrow convenience wrapper for `phase6-checksum-perf` plus `phase6-hexdump-perf`; it still excludes base64 even though `.github/workflows/zigux-bootstrap.yml` reruns `phase6-base64-perf` directly in CI",
            "`make -C zigux phase6-perf` now exists as a narrow convenience wrapper for every dedicated helper-local perf gate on current `master`",
        )
        assert_failure(
            root,
            "Documentation/zigux/phase6-perf-gate-survey.md",
            "the bundled `phase6` and aggregate `phase6-perf` make routes still replay only the shared helper tests plus the checksum and hexdump dedicated perf gates, while `.github/workflows/zigux-bootstrap.yml` separately reruns the base64 perf gate as its own direct CI step",
            "the bundled `phase6` and aggregate `phase6-perf` routes now replay every dedicated Phase 6 perf gate directly",
        )
        assert_failure(
            root,
            "Documentation/zigux/phase6-perf-gate-survey.md",
            "the live executable measurement evidence remains the algorithmic comparison-budget replay inside `zigux/tests/phase6_bsearch.zig`, not a separate wall-clock perf harness",
            "the live executable measurement evidence remains a standalone `phase6_bsearch_perf` route",
        )
        assert_failure(
            root,
            "Documentation/zigux/phase6-perf-gate-survey.md",
            "counted_compare_calls <= 4",
            "counted_compare_calls <= 5",
        )
        assert_failure(
            root,
            "Documentation/zigux/phase6-perf-gate-survey.md",
            "max_decode_slowdown_pct = 325",
            "max_decode_slowdown_pct = 150",
        )
        assert_failure(
            root,
            "scripts/zigux/README.md",
            "while `make -C zigux phase6-perf` remains the narrow aggregate route for the checksum and hexdump perf packet rather than a bundle-wide Phase 6 perf closure",
            "and there is still no `make -C zigux phase6-perf` route on `master`",
        )
        assert_failure(
            root,
            "zigux/tests/phase6_build.zig",
            '.name = "phase6-base64-perf"',
            '.name = "phase6-base64-bench"',
        )
        assert_failure(
            root,
            "zigux/tests/README.md",
            "  * `zigux/tests/phase6_base64_perf.zig`",
            "  * `zigux/tests/phase6_base64_bench.zig`",
        )
        assert_failure(
            root,
            "zigux/tests/phase6_bsearch.zig",
            "try std.testing.expect(counted_raw_compare_calls <= 4);",
            "try std.testing.expect(counted_raw_compare_calls <= 5);",
        )
        assert_failure(
            root,
            "zigux/Makefile",
            "phase6-base64-perf:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-base64-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
            "phase6-base64-bench:\n\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-base64-bench --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
        )
        assert_failure(
            root,
            "zigux/Makefile",
            "phase6-perf: phase6-checksum-perf phase6-hexdump-perf",
            "phase6-perf: phase6-checksum-perf",
        )
        assert_failure(
            root,
            "zigux/tests/README.md",
            "  * `zigux/tests/phase6_checksum_perf.zig`",
            "  * `zigux/tests/phase6_checksum_bench.zig`",
        )
        assert_failure(
            root,
            "zigux/tests/fixtures/phase6_base64_vectors.zig",
            ".max_decode_slowdown_pct = 325,",
            ".max_decode_slowdown_pct = 150,",
        )
        assert_failure(
            root,
            "zigux/tests/fixtures/phase6_checksum_vectors.zig",
            ".max_slowdown_pct = 150,",
            ".max_slowdown_pct = 175,",
        )

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
