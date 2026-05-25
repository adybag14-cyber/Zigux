#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 direct perf-threshold packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    """Raised when an expected Phase 6 perf marker is missing."""


BASE64_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_base64_vectors.zig")
BASE64_PERF_PATH = Path("zigux/tests/phase6_base64_perf.zig")
BASE64_SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")
BSEARCH_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_bsearch_vectors.zig")
BSEARCH_PERF_PATH = Path("zigux/tests/phase6_bsearch_perf.zig")
CHECKSUM_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")
CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
HEXDUMP_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")
HEXDUMP_PERF_PATH = Path("zigux/tests/phase6_hexdump_perf.zig")
PHASE6_PERF_SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
PHASE6_BUILD_PATH = Path("zigux/tests/phase6_build.zig")
PHASE6_HELPER_EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PHASE6_HELPER_PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")

REQUIRED_SNIPPETS = {
    BASE64_VECTORS_PATH: [
        '.{ .label = "STD_PAD", .payload = perf_payload, .padding = true, .variant_name = "std", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "STD_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "std", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "URLSAFE_PAD", .payload = perf_payload, .padding = true, .variant_name = "urlsafe", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "URLSAFE_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "urlsafe", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "IMAP_PAD", .payload = perf_payload, .padding = true, .variant_name = "imap", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "IMAP_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "imap", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        "try std.testing.expectEqual(expected.len, perf_cases.len);",
        "try std.testing.expect(saw_std_pad);",
        "try std.testing.expect(saw_std_no_pad);",
        "try std.testing.expect(saw_urlsafe_pad);",
        "try std.testing.expect(saw_urlsafe_no_pad);",
        "try std.testing.expect(saw_imap_pad);",
        "try std.testing.expect(saw_imap_no_pad);",
    ],
    BASE64_PERF_PATH: [
        "for (fixtures.perf_cases, 0..) |case, idx| {",
        "for (fixtures.perf_cases[idx + 1 ..]) |other| {",
        "if (encode_slowdown > case.max_encode_slowdown_pct) {",
        "if (decode_slowdown > case.max_decode_slowdown_pct) {",
    ],
    BASE64_SLICE_PATH: [
        "- exact helper-local perf replay packet: ordered labels `STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, `URLSAFE_NO_PAD`, `IMAP_PAD`, and `IMAP_NO_PAD`, each with `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`, owned once in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by the helper-local perf gate",
    ],
    PHASE6_HELPER_EVIDENCE_MANIFEST_PATH: [
        '      "key": "base64",',
        '      "dedicated_slowdown_replay": "zigux/tests/phase6_base64_perf.zig",',
        '        "scripts/zigux/check-phase6-base64-corpus-determinism.py"',
        '      "current_perf_evidence": {',
        '          "STD_PAD",',
        '          "STD_NO_PAD",',
        '          "URLSAFE_PAD",',
        '          "URLSAFE_NO_PAD",',
        '          "IMAP_PAD",',
        '          "IMAP_NO_PAD"',
        '        "iterations": 12000,',
        '        "max_encode_slowdown_pct": 150,',
        '        "max_decode_slowdown_pct": 325,',
        '          "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",',
        '          "make -C zigux phase6-base64-perf",',
        '      "key": "bsearch",',
        '      "dedicated_slowdown_replay": "zigux/tests/phase6_bsearch_perf.zig",',
        '          "len15",',
        '          "len64",',
        '          "len1024"',
        '        "query_count": 16,',
        '        "budget_formula": "std.math.log2_int_ceil(len) + 1",',
        '          "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",',
        '          "make -C zigux phase6-bsearch-perf",',
        '      "key": "checksum",',
        '      "dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig",',
        '            "label": "64B",',
        '            "iterations": 200000,',
        '            "max_slowdown_pct": 150',
        '            "label": "1501B",',
        '            "iterations": 12000,',
        '          "IPV4_20B",',
        '          "IPV4_20B_UPDATED",',
        '          "IPV4_24B",',
        '          "IPV4_60B"',
        '          "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",',
        '          "make -C zigux phase6-checksum-perf-matrix-test",',
        '          "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",',
        '          "make -C zigux phase6-checksum-perf",',
        '      "key": "hexdump",',
        '      "dedicated_slowdown_replay": "zigux/tests/phase6_hexdump_perf.zig",',
        '      "perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf_matrix.zig",',
        '            "label": "16B-plain-g1",',
        '            "reps": 40000,',
        '            "max_slowdown_pct": 175',
        '            "label": "32B-ascii-g2",',
        '            "reps": 10000,',
        '            "label": "16B-ascii-g4",',
        '            "reps": 20000,',
        '            "label": "16B-ascii-g8",',
        '            "max_slowdown_pct": 600',
        '          "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",',
        '          "make -C zigux phase6-hexdump-perf",',
    ],
    PHASE6_HELPER_PARITY_MANIFEST_PATH: [
        '      "key": "base64",',
        '      "dedicated_slowdown_replay": "zigux/tests/phase6_base64_perf.zig",',
        '      "slice_note": "Documentation/zigux/phase6-base64-slice.md",',
        '      "current_perf_evidence": {',
        '          "STD_PAD",',
        '          "STD_NO_PAD",',
        '          "URLSAFE_PAD",',
        '          "URLSAFE_NO_PAD",',
        '          "IMAP_PAD",',
        '          "IMAP_NO_PAD"',
        '        "iterations": 12000,',
        '        "max_encode_slowdown_pct": 150,',
        '        "max_decode_slowdown_pct": 325,',
        '          "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",',
        '          "make -C zigux phase6-base64-perf",',
        '      "key": "bsearch",',
        '      "dedicated_slowdown_replay": "zigux/tests/phase6_bsearch_perf.zig",',
        '        "budget_model": "comparison_budget",',
        '          "len15",',
        '          "len64",',
        '          "len1024"',
        '        "query_count": 16,',
        '        "bound_budget_formula": "len == 0 ? 0 : std.math.log2_int_floor(len) + 1",',
        '          "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",',
        '          "make -C zigux phase6-bsearch-perf",',
        '      "key": "checksum",',
        '      "dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig",',
        '            "label": "64B",',
        '            "iterations": 200000,',
        '            "max_slowdown_pct": 150',
        '            "label": "1501B",',
        '            "iterations": 12000,',
        '          "IPV4_20B",',
        '          "IPV4_20B_UPDATED",',
        '          "IPV4_24B",',
        '          "IPV4_60B"',
        '          "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",',
        '          "make -C zigux phase6-checksum-perf-matrix-test",',
        '          "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",',
        '          "make -C zigux phase6-checksum-perf",',
        '      "key": "hexdump",',
        '      "dedicated_slowdown_replay": "zigux/tests/phase6_hexdump_perf.zig",',
        '      "perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf_matrix.zig",',
        '            "label": "16B-plain-g1",',
        '            "reps": 40000,',
        '            "max_slowdown_pct": 175',
        '            "label": "32B-ascii-g2",',
        '            "reps": 10000,',
        '            "label": "16B-ascii-g4",',
        '            "reps": 20000,',
        '            "label": "16B-ascii-g8",',
        '            "max_slowdown_pct": 600',
        '          "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",',
        '          "make -C zigux phase6-hexdump-perf",',
    ],
... truncated ...