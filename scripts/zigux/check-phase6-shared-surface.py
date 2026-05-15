#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 catalog-backed shared packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
PERF_SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
BASE64_SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")
BSEARCH_SLICE_PATH = Path("Documentation/zigux/phase6-bsearch-slice.md")
CHECKSUM_SLICE_PATH = Path("Documentation/zigux/phase6-checksum-slice.md")
HEXDUMP_SLICE_PATH = Path("Documentation/zigux/phase6-hexdump-slice.md")
HEXDUMP_PERF_REFRESH_PATH = Path("Documentation/zigux/phase6-hexdump-perf-refresh.md")
PHASE6_BUILD_PATH = Path("zigux/tests/phase6_build.zig")
MAKEFILE_PATH = Path("zigux/Makefile")
WORKFLOW_PATH = Path(".github/workflows/zigux-bootstrap.yml")
SHARED_CHECKER_PATH = Path("scripts/zigux/check-phase6-shared-surface.py")
PRESENT_ENTRYPOINTS_CHECKER_PATH = Path("scripts/zigux/check-phase6-present-entrypoints.py")
BASE64_HELPER_PATH = Path("lib/base64.zig")
BASE64_REPLAY_PATH = Path("zigux/tests/phase6_base64.zig")
BASE64_PERF_PATH = Path("zigux/tests/phase6_base64_perf.zig")
BASE64_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_base64_vectors.zig")
BASE64_C_PARITY_PATH = Path("zigux/tests/phase6_base64_c_parity.zig")
BASE64_C_PARITY_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig")
BASE64_C_HARNESS_PATH = Path("zigux/tests/fixtures/phase6_base64_c_harness.c")
BASE64_C_PARITY_CHECKER_PATH = Path("scripts/zigux/check-phase6-base64-c-parity.py")
BSEARCH_HELPER_PATH = Path("lib/bsearch.zig")
BSEARCH_REPLAY_PATH = Path("zigux/tests/phase6_bsearch.zig")
BSEARCH_LOWER_UPPER_PATH = Path("zigux/tests/phase6_bsearch_lower_bound_c_abi.zig")
BSEARCH_EQUALITY_PATH = Path("zigux/tests/phase6_bsearch_c_abi_budget.zig")
BSEARCH_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_bsearch_vectors.zig")
BSEARCH_CORPUS_EVIDENCE_CHECKER_PATH = Path("scripts/zigux/check-phase6-bsearch-corpus-evidence.py")
CHECKSUM_HELPER_PATH = Path("lib/checksum.zig")
CHECKSUM_REPLAY_PATH = Path("zigux/tests/phase6_checksum.zig")
CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
CHECKSUM_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")
CHECKSUM_C_PARITY_PATH = Path("zigux/tests/phase6_checksum_c_parity.zig")
CHECKSUM_C_HARNESS_PATH = Path("zigux/tests/fixtures/phase6_checksum_c_harness.c")
CHECKSUM_C_PARITY_CHECKER_PATH = Path("scripts/zigux/check-phase6-checksum-c-parity.py")
HEXDUMP_REPLAY_PATH = Path("zigux/tests/phase6_hexdump.zig")
HEXDUMP_PERF_PATH = Path("zigux/tests/phase6_hexdump_perf.zig")
HEXDUMP_PERF_MATRIX_PATH = Path("zigux/tests/phase6_hexdump_perf_matrix.zig")
HEXDUMP_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")
HEXDUMP_PACKET_CHECKER_PATH = Path("scripts/zigux/check-phase6-hexdump-packet.py")

EXPECTED_PACKET_STATE_SUMMARY = {
    "base64": "parked_reviewable",
    "bsearch": "parked_reviewable",
    "checksum": "parked_reviewable",
    "hexdump": "parked_reviewable",
}

EXPECTED_SHARED_ROUTE_NOTE = (
    "base64, bsearch, checksum, and hexdump now keep committed helper-local or direct "
    "review surfaces on current `master`, while the Linux-style `zigux/Makefile` "
    "inventory still advertises `phase6-base64-perf`, `phase6-perf`, and `phase6` as "
    "wrapper names without committed target bodies, `phase6-checksum-perf` now reruns "
    "through a committed Linux-style target body, and the bootstrap workflow still "
    "reruns only the shared surface checkers, the base64 C parity packet, the bsearch "
    "packet, and the hexdump perf gate."
)

REQUIRED_SHARED_GATES = {
    SCRIPTS_README_PATH.as_posix(),
    CATALOG_PATH.as_posix(),
    CHECKSUM_SLICE_PATH.as_posix(),
    PERF_SURVEY_PATH.as_posix(),
    SHARED_CHECKER_PATH.as_posix(),
    PRESENT_ENTRYPOINTS_CHECKER_PATH.as_posix(),
    PHASE6_BUILD_PATH.as_posix(),
    MAKEFILE_PATH.as_posix(),
    WORKFLOW_PATH.as_posix(),
}

REQUIRED_PRESENT_ENTRYPOINTS = {
    CATALOG_PATH.as_posix(),
    PERF_SURVEY_PATH.as_posix(),
    HEXDUMP_PERF_REFRESH_PATH.as_posix(),
    PHASE6_BUILD_PATH.as_posix(),
    MANIFEST_PATH.as_posix(),
    BASE64_REPLAY_PATH.as_posix(),
    BASE64_C_PARITY_PATH.as_posix(),
    BASE64_PERF_PATH.as_posix(),
    BASE64_VECTORS_PATH.as_posix(),
    BASE64_C_PARITY_VECTORS_PATH.as_posix(),
    BASE64_C_HARNESS_PATH.as_posix(),
    BASE64_C_PARITY_CHECKER_PATH.as_posix(),
    BSEARCH_REPLAY_PATH.as_posix(),
    BSEARCH_LOWER_UPPER_PATH.as_posix(),
    BSEARCH_EQUALITY_PATH.as_posix(),
    BSEARCH_VECTORS_PATH.as_posix(),
    BSEARCH_CORPUS_EVIDENCE_CHECKER_PATH.as_posix(),
    CHECKSUM_HELPER_PATH.as_posix(),
    CHECKSUM_REPLAY_PATH.as_posix(),
    CHECKSUM_PERF_PATH.as_posix(),
    CHECKSUM_VECTORS_PATH.as_posix(),
    CHECKSUM_C_PARITY_PATH.as_posix(),
    CHECKSUM_C_HARNESS_PATH.as_posix(),
    CHECKSUM_C_PARITY_CHECKER_PATH.as_posix(),
    HEXDUMP_REPLAY_PATH.as_posix(),
    HEXDUMP_PERF_PATH.as_posix(),
    HEXDUMP_PERF_MATRIX_PATH.as_posix(),
    HEXDUMP_VECTORS_PATH.as_posix(),
    HEXDUMP_PACKET_CHECKER_PATH.as_posix(),
    PRESENT_ENTRYPOINTS_CHECKER_PATH.as_posix(),
}

REQUIRED_EXACT_CHECKS = {
    "python3 scripts/zigux/check-phase6-base64-c-parity.py",
    "python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test",
    "python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
    "python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test",
    "python3 scripts/zigux/check-phase6-checksum-c-parity.py",
    "python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test",
    "python3 scripts/zigux/check-phase6-hexdump-packet.py",
    "python3 scripts/zigux/check-phase6-hexdump-packet.py --self-test",
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py",
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test",
    "python3 scripts/zigux/check-phase6-present-entrypoints.py",
    "python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test",
    "make -C zigux phase6-bsearch-test",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-hexdump-test",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
}

EXPECTED_INVENTORY_ONLY_BLOCKED_ROUTES = {
    "make -C zigux phase6-base64-c-parity",
    "make -C zigux phase6-base64-perf",
    "make -C zigux phase6-checksum-c-parity",
    "make -C zigux phase6-validate",
    "make -C zigux phase6-perf",
    "make -C zigux phase6",
}

REQUIRED_CATALOG_SNIPPETS = [
    "- still-present direct C parity scaffolding: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
    "- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records `24` direct C parity cases and preserves the dedicated slowdown packet as six case labels, `STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, `URLSAFE_NO_PAD`, `IMAP_PAD`, and `IMAP_NO_PAD`, each at `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`",
    "### bsearch",
    "- direct local corpus evidence checker: `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
    "- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records a 15-element representative inline corpus, `10` typed and `10` raw lookup budget checks capped at `4` comparator calls, plus lower- and upper-bound as well as direct C ABI equality sweeps across dynamic lengths `0...32` and packed-record `member_size` ranges under the same `std.math.log2_int_ceil(len) + 1` budget",
    "- slice note: `Documentation/zigux/phase6-checksum-slice.md`",
    "- focused helper replay on current `master`: `zigux/tests/phase6_checksum.zig`",
    "- dedicated helper-local perf replay on current `master`: `zigux/tests/phase6_checksum_perf.zig`",
    "- focused checksum fixture companion on current `master`: `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
    "- direct Linux-style perf rerun route: `make -C zigux phase6-checksum-perf`",
    "- current review posture: the checksum helper-owned packet is directly readable on current `master`, while the broader shared route inventory stays partially blocked only because the aggregate wrappers and bootstrap workflow still lag the restored checksum perf wrapper",
    "### hexdump",
    "- direct local packet checker: `python3 scripts/zigux/check-phase6-hexdump-packet.py`",
    "- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records a four-case slowdown packet, `16B-plain-g1`, `32B-ascii-g2`, `16B-ascii-g4`, and `16B-ascii-g8`, with helper-local caps of `175`, `550`, `550`, and `600`",
    "- `make -C zigux phase6-checksum-perf`",
    "- current blocked-route posture: the helper-local checksum replay and slowdown gate are now directly readable through `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, and `zigux/tests/phase6_build.zig`, and `zigux/Makefile` now exposes a committed `phase6-checksum-perf` target body, but the bootstrap workflow plus the aggregate `phase6-validate`, `phase6-perf`, and `phase6` route inventory still lag that restored checksum wrapper",
    "- current shared-lane posture: the broader `phase6-base64-perf`, `phase6-validate`, `phase6-perf`, and `phase6` wrappers remain part of the shared route inventory, but the directly readable base64 and checksum build steps in `zigux/tests/phase6_build.zig` plus the committed `phase6-checksum-perf` Linux-style route now carry the current helper-local perf gates while the remaining wrapper surfaces continue to lag",
]

REQUIRED_BASE64_SLICE_SNIPPETS = [
    "- current `master` still keeps the direct C parity packet: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
    "- present direct C parity packet: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
    "- direct local C parity checker route: `python3 scripts/zigux/check-phase6-base64-c-parity.py`",
    "- built-in parity-script self-test route: `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test`",
]

REQUIRED_BSEARCH_SLICE_SNIPPETS = [
    "- `PHASE6_SLICE=bsearch-leaf-helper`",
    "- `searchIndex`",
    "- `search`",
    "- `searchMutable`",
    "- `lowerBoundIndex`",
    "- `upperBoundIndex`",
    "- `IndexRange`",
    "- `equalRangeIndex`",
    "- `equalRange`",
    "- `equalRangeMutable`",
    "- `bsearchIndex`",
    "- `bsearch`",
    "- `bsearchMutable`",
    "- `bsearchLowerBoundIndex`",
    "- `bsearchUpperBoundIndex`",
    "- `bsearchEqualRangeIndex`",
    "- `bsearchEqualRange`",
    "- `bsearchEqualRangeMutable`",
    "- `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`",
    "- `zigux/tests/phase6_bsearch_c_abi_budget.zig`",
    "- direct local corpus evidence checker route: `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
    "- direct local corpus evidence checker self-test: `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test`",
    "The shared `zigux/tests/fixtures/phase6_bsearch_vectors.zig` companion remains helper-local support inside that packet today: `phase6_bsearch.zig` still imports it for representative ascending and descending raw-array reuse, and the bounds-focused plus direct C ABI budget replays still reuse its dynamic-length and packed-record seed corpus.",
    "Reviewers should treat that fixture as compact shared packet support rather than as a separate standalone timing-style route.",
    "the exported `IndexRange` result type keeps duplicate-span length, emptiness, typed slice, and raw byte views explicit through `len`, `isEmpty`, `sliceConst`, `sliceMutable`, `bytes`, and `bytesMutable`, while the direct `equalRange`, `equalRangeMutable`, `bsearchEqualRange`, and `bsearchEqualRangeMutable` wrappers hand those typed slice and raw byte views back without forcing callers to peel `IndexRange` apart by hand or widening Phase 6 into a separate fixture or routing packet.",
]

REQUIRED_CHECKSUM_SLICE_SNIPPETS = [
    "- `PHASE6_STATUS=parked_reviewable`",
    "- current `master` keeps `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
    "- current routed build packet now defines checksum helper and perf steps in `zigux/tests/phase6_build.zig`, while `zigux/Makefile` now exposes a committed `phase6-checksum-perf` target body and still advertises only `phase6-checksum-c-parity` as a phony route without a corresponding target body",
    "- direct focused perf route: `zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig`",
    "- direct Linux-style perf route: `make -C zigux phase6-checksum-perf`",
    "- route nuance note: the checksum helper-owned replay, slowdown gate, and Linux-style perf wrapper are readable from the committed helper packet again, but the aggregate `zigux/Makefile` and workflow surfaces still need their own route-truthfulness follow-up before reviewers should treat the broader `phase6-validate`, `phase6-perf`, and `phase6` wrappers as equivalent packet summaries",
    "- current review posture: parked reviewable; the checksum roadmap anchor now keeps the helper-owned replay, slowdown gate, direct C parity scaffolding, aligned IPv4 fast-path helper proof, and Linux-style perf wrapper readable on current `master`, while the remaining gap has narrowed to aggregate shared-route inventory truthfulness rather than a missing checksum helper packet",
]

REQUIRED_HEXDUMP_SLICE_SNIPPETS = [
    "- `PHASE6_STATUS=parked_reviewable`",
    "- `PHASE6_SLICE=hexdump-leaf-helper`",
    "- `zigux/tests/phase6_hexdump.zig`",
    "- `zigux/tests/phase6_hexdump_perf.zig`",
    "- `zigux/tests/phase6_hexdump_perf_matrix.zig`",
    "- `zigux/tests/fixtures/phase6_hexdump_vectors.zig`",
    "- `scripts/zigux/check-phase6-hexdump-packet.py`",
    "- `make -C zigux phase6-hexdump-test`",
    "- `make -C zigux phase6-hexdump-perf`",
    "- `make -C zigux phase6-hexdump-review`",
    "- exact manifest-backed evidence: `zigux/tests/phase6_helper_parity_manifest.json` still records a four-case slowdown packet, `16B-plain-g1`, `32B-ascii-g2`, `16B-ascii-g4`, and `16B-ascii-g8`, with helper-local caps of `175`, `550`, `550`, and `600`",
]

REQUIRED_PERF_SURVEY_SNIPPETS = [
    "- bsearch shared posture: the live executable measurement evidence remains the algorithmic comparison-budget replays inside `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, and `zigux/tests/phase6_bsearch_c_abi_budget.zig`, not a separate wall-clock perf harness",
    "- bsearch review-surface posture: `Documentation/zigux/phase6-bsearch-slice.md`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `zigux/tests/phase6_build.zig`, and `zigux/Makefile` now agree that the shipped bsearch packet uses inline equality probes plus a compact shared seed fixture companion for representative arrays, dynamic lengths, and packed-record corpus reuse, without widening into a separate timing route",
    "* checksum exact thresholds: `zigux/tests/phase6_checksum_perf.zig` now keeps two helper-local slowdown cases, `64` at `reps = 20_000` and `1501` at `reps = 4_000`, each capped at `max_slowdown_pct = 150`, so the checksum perf packet is reviewable from committed evidence today even while the Linux-style wrapper inventory still lags that direct build route",
    "* hexdump shared posture: a dedicated slowdown gate remains wired through `zigux/tests/phase6_hexdump_perf.zig`, `zigux/tests/phase6_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and the committed `phase6-hexdump-perf` plus `phase6-hexdump-review` target bodies in `zigux/Makefile`",
    "* hexdump exact thresholds: `zigux/tests/fixtures/phase6_hexdump_vectors.zig` still pins `16B-plain-g1` at `reps = 40_000` with `max_slowdown_pct = 175`, `32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`, `16B-ascii-g4` at `reps = 20_000` with `max_slowdown_pct = 550`, and `16B-ascii-g8` at `reps = 20_000` with `max_slowdown_pct = 600`",
]

REQUIRED_BUILD_SNIPPETS = [
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
    "checksum_perf_step.dependOn(&run_checksum_perf.step);",
    'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump perf gate");',
    "hexdump_perf_step.dependOn(&run_hexdump_perf_matrix_tests.step);",
    "hexdump_perf_step.dependOn(&run_hexdump_perf.step);",
]

REQUIRED_MAKEFILE_SNIPPETS = [
    "PHONY += phase6-validate phase6-test phase6-bsearch-test phase6-base64-c-parity phase6-checksum-c-parity phase6-hexdump-test phase6-hexdump-review phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6-perf phase6",
    "phase6-checksum-perf:",
    '\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig',
]

REQUIRED_WORKFLOW_SNIPPETS = [
    "- name: Self-test Phase 6 shared-surface checker",
    "- name: Check Phase 6 shared surface",
    "- name: Self-test Phase 6 checksum C parity checker",
    "- name: Run Phase 6 bsearch focused packet",
    "- name: Run Phase 6 hexdump perf gate",
]

ABSENT_WORKFLOW_SNIPPETS = [
    "- name: Run Phase 6 checksum perf gate",
]

REQUIRED_PRESENT_ENTRYPOINTS_SNIPPETS = [
    'EXPECTED_HEXDUMP_PACKET_CHECKER = HEXDUMP_CHECKER_PATH.as_posix()',
    'EXPECTED_HEXDUMP_PERF_REFRESH = HEXDUMP_PERF_REFRESH_PATH.as_posix()',
    'raise ValidationError(f"missing hexdump helper row in {MANIFEST_PATH.as_posix()}")',
]

REQUIRED_SCRIPTS_README_SNIPPETS = [
    "- Phase 6 flow - the current shared Phase 6 review surface on `master` is `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, `Documentation/zigux/phase6-leaf-helper-lane-sequencing.md`, `scripts/zigux/README.md`, `scripts/zigux/check-phase6-shared-surface.py`, `zigux/tests/README.md`, `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`.",
    "- `check-phase6-shared-surface.py`, `check-phase6-base64-c-parity.py`, `check-phase6-bsearch-corpus-evidence.py`, `check-phase6-checksum-c-parity.py`, `check-phase6-hexdump-packet.py`, and `check-phase6-perf-threshold-markers.py` are the shipped scripts-root Phase 6 checkers on current `master`.",
    "- `python3 scripts/zigux/check-phase6-shared-surface.py --self-test` and `python3 scripts/zigux/check-phase6-shared-surface.py` keep the manifest-backed shared packet honest, while `make -C zigux phase6-validate`, `make -C zigux phase6-perf`, and `make -C zigux phase6` should still be read as inventory-only convenience routes because current `zigux/Makefile` exposes those wrapper names without committed target bodies.",
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


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected Phase 6 marker in {path}: {snippet}")


def require_absent_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet in content:
            raise ValidationError(f"unexpected stale Phase 6 marker in {path}: {snippet}")


def helper_row(manifest: dict[str, object], helper_id: str) -> dict[str, object]:
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"missing helpers in {MANIFEST_PATH}")
    rows = [item for item in helpers if isinstance(item, dict) and item.get("id") == helper_id]
    if len(rows) != 1:
        raise ValidationError(f"expected one {helper_id} helper row in {MANIFEST_PATH}")
    return rows[0]


def require_helper_packet(
    manifest: dict[str, object],
    helper_id: str,
    expected_tests: set[str],
    expected_fixtures: set[str],
    expected_fields: dict[str, str] | None = None,
) -> None:
    row = helper_row(manifest, helper_id)
    if set(row.get("tests") or []) != expected_tests:
        raise ValidationError(f"unexpected {helper_id} tests list in {MANIFEST_PATH}")
    if set(row.get("fixtures") or []) != expected_fixtures:
        raise ValidationError(f"unexpected {helper_id} fixtures list in {MANIFEST_PATH}")
    for key, value in (expected_fields or {}).items():
        if row.get(key) != value:
            raise ValidationError(f"unexpected {helper_id} {key} in {MANIFEST_PATH}")


def validate_manifest(repo_root: Path) -> None:
    manifest = read_json(repo_root / MANIFEST_PATH)
    if not isinstance(manifest, dict):
        raise ValidationError(f"expected object in {MANIFEST_PATH}")

    if manifest.get("status") != "partially_blocked":
        raise ValidationError(f"unexpected Phase 6 status in {MANIFEST_PATH}")
    if manifest.get("packet_state_summary") != EXPECTED_PACKET_STATE_SUMMARY:
        raise ValidationError(f"unexpected packet_state_summary in {MANIFEST_PATH}")
    if manifest.get("shared_route_truthfulness_note") != EXPECTED_SHARED_ROUTE_NOTE:
        raise ValidationError(f"unexpected shared_route_truthfulness_note in {MANIFEST_PATH}")

    shared_gates = manifest.get("shared_gates")
    if not isinstance(shared_gates, list):
        raise ValidationError(f"missing shared_gates in {MANIFEST_PATH}")
    if not REQUIRED_SHARED_GATES.issubset(set(shared_gates)):
        raise ValidationError(f"missing required shared_gates entries in {MANIFEST_PATH}")

    present_entrypoints = manifest.get("tests_root_present_entrypoints")
    if not isinstance(present_entrypoints, list):
        raise ValidationError(f"missing tests_root_present_entrypoints in {MANIFEST_PATH}")
    if not REQUIRED_PRESENT_ENTRYPOINTS.issubset(set(present_entrypoints)):
        raise ValidationError(f"missing restored Phase 6 entrypoints in {MANIFEST_PATH}")

    public_tree_gaps = manifest.get("tests_root_public_tree_gaps")
    if public_tree_gaps != []:
        raise ValidationError(f"unexpected tests_root_public_tree_gaps in {MANIFEST_PATH}")

    exact_checks = manifest.get("exact_checks")
    if not isinstance(exact_checks, list):
        raise ValidationError(f"missing exact_checks in {MANIFEST_PATH}")
    if not REQUIRED_EXACT_CHECKS.issubset(set(exact_checks)):
        raise ValidationError(f"missing exact_checks for the Phase 6 packet in {MANIFEST_PATH}")

    blocked_routes = manifest.get("inventory_only_blocked_routes")
    if not isinstance(blocked_routes, list):
        raise ValidationError(f"missing inventory_only_blocked_routes in {MANIFEST_PATH}")
    if set(blocked_routes) != EXPECTED_INVENTORY_ONLY_BLOCKED_ROUTES:
        raise ValidationError(f"unexpected inventory_only_blocked_routes in {MANIFEST_PATH}")

    require_helper_packet(
        manifest,
        "base64",
        {
            "zigux/tests/phase6_base64.zig",
            "zigux/tests/phase6_base64_c_parity.zig",
            "zigux/tests/phase6_base64_perf.zig",
        },
        {
            "zigux/tests/fixtures/phase6_base64_vectors.zig",
            "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
            "zigux/tests/fixtures/phase6_base64_c_harness.c",
        },
        {"external_parity": "scripts/zigux/check-phase6-base64-c-parity.py"},
    )
    require_helper_packet(
        manifest,
        "bsearch",
        {
            "zigux/tests/phase6_bsearch.zig",
            "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
            "zigux/tests/phase6_bsearch_c_abi_budget.zig",
        },
        {
            "zigux/tests/fixtures/phase6_bsearch_vectors.zig",
        },
        {"corpus_evidence_checker": "scripts/zigux/check-phase6-bsearch-corpus-evidence.py"},
    )
    require_helper_packet(
        manifest,
        "checksum",
        {
            "zigux/tests/phase6_checksum.zig",
            "zigux/tests/phase6_checksum_perf.zig",
            "zigux/tests/phase6_checksum_c_parity.zig",
        },
        {
            "zigux/tests/fixtures/phase6_checksum_vectors.zig",
            "zigux/tests/fixtures/phase6_checksum_c_harness.c",
        },
        {"external_parity": "scripts/zigux/check-phase6-checksum-c-parity.py"},
    )
    require_helper_packet(
        manifest,
        "hexdump",
        {
            "zigux/tests/phase6_hexdump.zig",
            "zigux/tests/phase6_hexdump_perf.zig",
            "zigux/tests/phase6_hexdump_perf_matrix.zig",
        },
        {
            "zigux/tests/fixtures/phase6_hexdump_vectors.zig",
        },
        {
            "perf_refresh_note": "Documentation/zigux/phase6-hexdump-perf-refresh.md",
            "packet_checker": "scripts/zigux/check-phase6-hexdump-packet.py",
            "linux_review_route": "make -C zigux phase6-hexdump-review",
        },
    )


def validate_paths(repo_root: Path) -> None:
    required = {
        SCRIPTS_README_PATH.as_posix(),
        CATALOG_PATH.as_posix(),
        PERF_SURVEY_PATH.as_posix(),
        BASE64_SLICE_PATH.as_posix(),
        BSEARCH_SLICE_PATH.as_posix(),
        CHECKSUM_SLICE_PATH.as_posix(),
        HEXDUMP_SLICE_PATH.as_posix(),
        HEXDUMP_PERF_REFRESH_PATH.as_posix(),
        PHASE6_BUILD_PATH.as_posix(),
        MAKEFILE_PATH.as_posix(),
        WORKFLOW_PATH.as_posix(),
        SHARED_CHECKER_PATH.as_posix(),
        PRESENT_ENTRYPOINTS_CHECKER_PATH.as_posix(),
        BASE64_HELPER_PATH.as_posix(),
        BASE64_REPLAY_PATH.as_posix(),
        BASE64_PERF_PATH.as_posix(),
        BASE64_VECTORS_PATH.as_posix(),
        BASE64_C_PARITY_PATH.as_posix(),
        BASE64_C_PARITY_VECTORS_PATH.as_posix(),
        BASE64_C_HARNESS_PATH.as_posix(),
        BASE64_C_PARITY_CHECKER_PATH.as_posix(),
        BSEARCH_HELPER_PATH.as_posix(),
        BSEARCH_REPLAY_PATH.as_posix(),
        BSEARCH_LOWER_UPPER_PATH.as_posix(),
        BSEARCH_EQUALITY_PATH.as_posix(),
        BSEARCH_VECTORS_PATH.as_posix(),
        BSEARCH_CORPUS_EVIDENCE_CHECKER_PATH.as_posix(),
        CHECKSUM_HELPER_PATH.as_posix(),
        CHECKSUM_REPLAY_PATH.as_posix(),
        CHECKSUM_PERF_PATH.as_posix(),
        CHECKSUM_VECTORS_PATH.as_posix(),
        CHECKSUM_C_PARITY_PATH.as_posix(),
        CHECKSUM_C_HARNESS_PATH.as_posix(),
        CHECKSUM_C_PARITY_CHECKER_PATH.as_posix(),
        HEXDUMP_REPLAY_PATH.as_posix(),
        HEXDUMP_PERF_PATH.as_posix(),
        HEXDUMP_PERF_MATRIX_PATH.as_posix(),
        HEXDUMP_VECTORS_PATH.as_posix(),
        HEXDUMP_PACKET_CHECKER_PATH.as_posix(),
    }
    for rel_path in sorted(required):
        if not (repo_root / rel_path).exists():
            raise ValidationError(f"missing required Phase 6 path: {rel_path}")


def run_checks(repo_root: Path) -> None:
    validate_paths(repo_root)
    validate_manifest(repo_root)
    require_snippets(repo_root / SCRIPTS_README_PATH, REQUIRED_SCRIPTS_README_SNIPPETS)
    require_snippets(repo_root / CATALOG_PATH, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(repo_root / BASE64_SLICE_PATH, REQUIRED_BASE64_SLICE_SNIPPETS)
    require_snippets(repo_root / BSEARCH_SLICE_PATH, REQUIRED_BSEARCH_SLICE_SNIPPETS)
    require_snippets(repo_root / CHECKSUM_SLICE_PATH, REQUIRED_CHECKSUM_SLICE_SNIPPETS)
    require_snippets(repo_root / HEXDUMP_SLICE_PATH, REQUIRED_HEXDUMP_SLICE_SNIPPETS)
    require_snippets(repo_root / PERF_SURVEY_PATH, REQUIRED_PERF_SURVEY_SNIPPETS)
    require_snippets(repo_root / PHASE6_BUILD_PATH, REQUIRED_BUILD_SNIPPETS)
    require_snippets(repo_root / MAKEFILE_PATH, REQUIRED_MAKEFILE_SNIPPETS)
    require_snippets(repo_root / WORKFLOW_PATH, REQUIRED_WORKFLOW_SNIPPETS)
    require_absent_snippets(repo_root / WORKFLOW_PATH, ABSENT_WORKFLOW_SNIPPETS)
    require_snippets(repo_root / PRESENT_ENTRYPOINTS_CHECKER_PATH, REQUIRED_PRESENT_ENTRYPOINTS_SNIPPETS)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    for rel_path in REQUIRED_PRESENT_ENTRYPOINTS | REQUIRED_SHARED_GATES:
        write(root / rel_path, "placeholder\n")

    for rel_path in {
        BASE64_HELPER_PATH.as_posix(),
        BASE64_REPLAY_PATH.as_posix(),
        BASE64_PERF_PATH.as_posix(),
        BASE64_VECTORS_PATH.as_posix(),
        BASE64_C_PARITY_PATH.as_posix(),
        BASE64_C_PARITY_VECTORS_PATH.as_posix(),
        BASE64_C_HARNESS_PATH.as_posix(),
        BASE64_C_PARITY_CHECKER_PATH.as_posix(),
        BSEARCH_HELPER_PATH.as_posix(),
        BSEARCH_REPLAY_PATH.as_posix(),
        BSEARCH_LOWER_UPPER_PATH.as_posix(),
        BSEARCH_EQUALITY_PATH.as_posix(),
        BSEARCH_VECTORS_PATH.as_posix(),
        BSEARCH_CORPUS_EVIDENCE_CHECKER_PATH.as_posix(),
        CHECKSUM_HELPER_PATH.as_posix(),
        CHECKSUM_REPLAY_PATH.as_posix(),
        CHECKSUM_PERF_PATH.as_posix(),
        CHECKSUM_VECTORS_PATH.as_posix(),
        CHECKSUM_C_PARITY_PATH.as_posix(),
        CHECKSUM_C_HARNESS_PATH.as_posix(),
        CHECKSUM_C_PARITY_CHECKER_PATH.as_posix(),
        HEXDUMP_REPLAY_PATH.as_posix(),
        HEXDUMP_PERF_PATH.as_posix(),
        HEXDUMP_PERF_MATRIX_PATH.as_posix(),
        HEXDUMP_VECTORS_PATH.as_posix(),
        HEXDUMP_PACKET_CHECKER_PATH.as_posix(),
    }:
        write(root / rel_path, "fixture\n")

    write(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_SCRIPTS_README_SNIPPETS + [""]))
    write(root / CATALOG_PATH, "\n".join(REQUIRED_CATALOG_SNIPPETS + ["- surveyed head: `test-head`", ""]))
    write(root / BASE64_SLICE_PATH, "\n".join(REQUIRED_BASE64_SLICE_SNIPPETS + [""]))
    write(root / BSEARCH_SLICE_PATH, "\n".join(REQUIRED_BSEARCH_SLICE_SNIPPETS + [""]))
    write(root / CHECKSUM_SLICE_PATH, "\n".join(REQUIRED_CHECKSUM_SLICE_SNIPPETS + [""]))
    write(root / HEXDUMP_SLICE_PATH, "\n".join(REQUIRED_HEXDUMP_SLICE_SNIPPETS + [""]))
    write(root / PERF_SURVEY_PATH, "\n".join(REQUIRED_PERF_SURVEY_SNIPPETS + [""]))
    write(root / PHASE6_BUILD_PATH, "\n".join(REQUIRED_BUILD_SNIPPETS + [""]))
    write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_SNIPPETS + [""]))
    write(root / WORKFLOW_PATH, "\n".join(REQUIRED_WORKFLOW_SNIPPETS + [""]))
    write(root / PRESENT_ENTRYPOINTS_CHECKER_PATH, "\n".join(REQUIRED_PRESENT_ENTRYPOINTS_SNIPPETS + [""]))

    manifest = {
        "phase": "Phase 6",
        "tranche": "leaf-helper-parity",
        "status": "partially_blocked",
        "packet_state_summary": dict(EXPECTED_PACKET_STATE_SUMMARY),
        "shared_route_truthfulness_note": EXPECTED_SHARED_ROUTE_NOTE,
        "surveyed_commit": "test-head",
        "helpers": [
            {
                "id": "base64",
                "tests": sorted(
                    [
                        "zigux/tests/phase6_base64.zig",
                        "zigux/tests/phase6_base64_c_parity.zig",
                        "zigux/tests/phase6_base64_perf.zig",
                    ]
                ),
                "fixtures": sorted(
                    [
                        "zigux/tests/fixtures/phase6_base64_vectors.zig",
                        "zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig",
                        "zigux/tests/fixtures/phase6_base64_c_harness.c",
                    ]
                ),
                "external_parity": "scripts/zigux/check-phase6-base64-c-parity.py",
            },
            {
                "id": "bsearch",
                "tests": sorted(
                    [
                        "zigux/tests/phase6_bsearch.zig",
                        "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
                        "zigux/tests/phase6_bsearch_c_abi_budget.zig",
                    ]
                ),
                "fixtures": sorted(
                    [
                        "zigux/tests/fixtures/phase6_bsearch_vectors.zig",
                    ]
                ),
                "corpus_evidence_checker": "scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
            },
            {
                "id": "checksum",
                "tests": sorted(
                    [
                        "zigux/tests/phase6_checksum.zig",
                        "zigux/tests/phase6_checksum_perf.zig",
                        "zigux/tests/phase6_checksum_c_parity.zig",
                    ]
                ),
                "fixtures": sorted(
                    [
                        "zigux/tests/fixtures/phase6_checksum_vectors.zig",
                        "zigux/tests/fixtures/phase6_checksum_c_harness.c",
                    ]
                ),
                "external_parity": "scripts/zigux/check-phase6-checksum-c-parity.py",
            },
            {
                "id": "hexdump",
                "tests": sorted(
                    [
                        "zigux/tests/phase6_hexdump.zig",
                        "zigux/tests/phase6_hexdump_perf.zig",
                        "zigux/tests/phase6_hexdump_perf_matrix.zig",
                    ]
                ),
                "fixtures": ["zigux/tests/fixtures/phase6_hexdump_vectors.zig"],
                "perf_refresh_note": "Documentation/zigux/phase6-hexdump-perf-refresh.md",
                "packet_checker": "scripts/zigux/check-phase6-hexdump-packet.py",
                "linux_review_route": "make -C zigux phase6-hexdump-review",
            },
        ],
        "shared_gates": sorted(REQUIRED_SHARED_GATES),
        "tests_root_present_entrypoints": sorted(REQUIRED_PRESENT_ENTRYPOINTS),
        "tests_root_public_tree_gaps": [],
        "exact_checks": sorted(REQUIRED_EXACT_CHECKS),
        "inventory_only_blocked_routes": sorted(EXPECTED_INVENTORY_ONLY_BLOCKED_ROUTES),
    }
    write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")


def assert_failure(root: Path, rel_path: Path, old: str, new: str) -> None:
    path = root / rel_path
    original = path.read_text(encoding="utf-8")
    if old not in original:
        raise AssertionError(f"self-test marker not found in {rel_path}: {old}")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    try:
        run_checks(root)
    except ValidationError as exc:
        if rel_path.as_posix() not in str(exc):
            raise AssertionError(f"unexpected failure for {rel_path}: {exc}") from exc
    else:
        raise AssertionError(f"expected failure for {rel_path}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        run_checks(root)
        assert_failure(
            root,
            MANIFEST_PATH,
            '"scripts/zigux/README.md"',
            '"scripts/zigux/README-missing.md"',
        )
        assert_failure(
            root,
            SCRIPTS_README_PATH,
            "`check-phase6-perf-threshold-markers.py`",
            "`check-phase6-perf-threshold-drift.py`",
        )
        assert_failure(
            root,
            MANIFEST_PATH,
            '"bsearch": "parked_reviewable"',
            '"bsearch": "blocked_helper_packet_missing"',
        )
        assert_failure(
            root,
            MANIFEST_PATH,
            '"scripts/zigux/check-phase6-bsearch-corpus-evidence.py"',
            '"scripts/zigux/check-phase6-bsearch-proof.py"',
        )
        assert_failure(
            root,
            MANIFEST_PATH,
            '"zigux/tests/phase6_bsearch_c_abi_budget.zig"',
            '"zigux/tests/phase6_bsearch_c_abi_budget_missing.zig"',
        )
        assert_failure(
            root,
            BSEARCH_SLICE_PATH,
            "- `bsearchEqualRangeMutable`",
            "- `bsearchEqualRangeMutableDrift`",
        )
        assert_failure(
            root,
            PERF_SURVEY_PATH,
            "without widening into a separate timing route",
            "while widening into a separate timing route",
        )
        assert_failure(
            root,
            MANIFEST_PATH,
            '"hexdump": "parked_reviewable"',
            '"hexdump": "blocked_helper_packet_missing"',
        )
        assert_failure(
            root,
            MANIFEST_PATH,
            '"scripts/zigux/check-phase6-hexdump-packet.py"',
            '"scripts/zigux/check-phase6-hexdump-review.py"',
        )
        assert_failure(
            root,
            MANIFEST_PATH,
            '"python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test"',
            '"python3 scripts/zigux/check-phase6-present-entrypoints.py --self-test-missing"',
        )
        assert_failure(
            root,
            HEXDUMP_SLICE_PATH,
            "- `zigux/tests/phase6_hexdump_perf_matrix.zig`",
            "- `zigux/tests/phase6_hexdump_perf_matrix_missing.zig`",
        )
        assert_failure(
            root,
            PERF_SURVEY_PATH,
            "`32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 550`",
            "`32B-ascii-g2` at `reps = 10_000` with `max_slowdown_pct = 425`",
        )
        assert_failure(
            root,
            PRESENT_ENTRYPOINTS_CHECKER_PATH,
            'EXPECTED_HEXDUMP_PACKET_CHECKER = HEXDUMP_CHECKER_PATH.as_posix()',
            'EXPECTED_HEXDUMP_PACKET_CHECKER = "scripts/zigux/check-phase6-hexdump-review.py"',
        )
        assert_failure(
            root,
            MAKEFILE_PATH,
            "phase6-checksum-perf:",
            "phase6-checksum-perf-missing:",
        )
        assert_failure(
            root,
            WORKFLOW_PATH,
            "- name: Run Phase 6 hexdump perf gate",
            "- name: Run Phase 6 checksum perf gate",
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
    print("Phase 6 shared checker matches the current bsearch, checksum, hexdump, and shared packet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())