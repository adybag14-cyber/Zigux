#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 shared helper packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    pass


MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
DOCUMENTATION_README_PATH = Path("Documentation/zigux/README.md")
SCRIPTS_README_PATH = Path("scripts/zigux/README.md")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
HELPER_EVIDENCE_CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
PERF_SURVEY_PATH = Path("Documentation/zigux/phase6-perf-gate-survey.md")
BASE64_SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")
BSEARCH_SLICE_PATH = Path("Documentation/zigux/phase6-bsearch-slice.md")
CHECKSUM_SLICE_PATH = Path("Documentation/zigux/phase6-checksum-slice.md")
HEXDUMP_SLICE_PATH = Path("Documentation/zigux/phase6-hexdump-slice.md")
HEXDUMP_PERF_REFRESH_PATH = Path("Documentation/zigux/phase6-hexdump-perf-refresh.md")
TESTS_README_PATH = Path("zigux/tests/README.md")
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
BASE64_C_CASEGEN_PATH = Path("zigux/tests/phase6_base64_c_casegen.zig")
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

HEXDUMP_HELPER_PATH = Path("lib/hexdump.zig")
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
    "review surfaces on current `master`, `zigux/Makefile` now exposes committed "
    "`phase6-base64-perf` and `phase6-checksum-perf` Linux-style target bodies, the "
    "aggregate `phase6-validate`, `phase6-perf`, and `phase6` wrappers still remain "
    "inventory-only route names without committed target bodies, and the bootstrap "
    "workflow still reruns the shared surface checkers, the base64 C parity packet, "
    "the bsearch packet, the checksum C parity packet, and the hexdump perf gate."
)

REQUIRED_SHARED_GATES = {
    DOCUMENTATION_README_PATH.as_posix(),
    SCRIPTS_README_PATH.as_posix(),
    CATALOG_PATH.as_posix(),
    HELPER_EVIDENCE_CATALOG_PATH.as_posix(),
    CHECKSUM_SLICE_PATH.as_posix(),
    PERF_SURVEY_PATH.as_posix(),
    SHARED_CHECKER_PATH.as_posix(),
    PRESENT_ENTRYPOINTS_CHECKER_PATH.as_posix(),
    TESTS_README_PATH.as_posix(),
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
    BASE64_C_CASEGEN_PATH.as_posix(),
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
    "make -C zigux phase6-base64-perf",
    "make -C zigux phase6-bsearch-test",
    "make -C zigux phase6-checksum-perf",
    "make -C zigux phase6-hexdump-test",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
}

EXPECTED_INVENTORY_ONLY_BLOCKED_ROUTES = {
    "make -C zigux phase6-base64-c-parity",
    "make -C zigux phase6-checksum-c-parity",
    "make -C zigux phase6-validate",
    "make -C zigux phase6-perf",
    "make -C zigux phase6",
}

REQUIRED_SCRIPTS_README_SNIPPETS = [
    "Phase 6 flow - `check-phase6-shared-surface.py` keeps the shared Phase 6 helper packet aligned across `Documentation/zigux/phase6-helper-parity-catalog.md`, `Documentation/zigux/phase6-perf-gate-survey.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase6_helper_parity_manifest.json`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, the directly readable base64, bsearch, checksum C-parity, and hexdump helper packet, and the current helper-local perf threshold markers before the shared helper routes run.",
    "- `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test`, `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test`, `python3 scripts/zigux/check-phase6-hexdump-packet.py --self-test`, `python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test`, and `python3 scripts/zigux/check-phase6-shared-surface.py --self-test` keep the bundled helper replay for the directly readable base64, bsearch, checksum C-parity, and hexdump packet, and `zigux/tests/phase6_base64_perf.zig` is now directly readable again beside `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, and `zigux/tests/fixtures/phase6_base64_vectors.zig`, and the direct base64 C parity packet.",
    "- `python3 scripts/zigux/check-phase6-base64-c-parity.py`, `python3 scripts/zigux/check-phase6-checksum-c-parity.py`, `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig` are directly reviewable on current `master`, so the checksum helper-owned packet should no longer be described as missing from the shared reminder surface.",
    "- `make -C zigux phase6-base64-c-parity`, `make -C zigux phase6-checksum-c-parity`, `make -C zigux phase6-validate`, `make -C zigux phase6-perf`, and `make -C zigux phase6` still remain inventory-only routes because current `zigux/Makefile` does not expose committed target bodies for those wrappers, while `make -C zigux phase6-base64-perf` and `make -C zigux phase6-checksum-perf` now remain committed helper-local Linux-style wrapper targets that match `zigux/tests/phase6_build.zig`; the directly reviewable helper-local proofs today come from `python3 scripts/zigux/check-phase6-base64-c-parity.py --self-test`, `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py --self-test`, `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, `python3 scripts/zigux/check-phase6-checksum-c-parity.py --self-test`, `python3 scripts/zigux/check-phase6-hexdump-packet.py --self-test`, `python3 scripts/zigux/check-phase6-hexdump-packet.py`, `python3 scripts/zigux/check-phase6-perf-threshold-markers.py --self-test`, `python3 scripts/zigux/check-phase6-perf-threshold-markers.py`, `make -C zigux phase6-base64-perf`, `make -C zigux phase6-bsearch-test`, `make -C zigux phase6-checksum-perf`, `make -C zigux phase6-hexdump-test`, `make -C zigux phase6-hexdump-review`, and `make -C zigux phase6-hexdump-perf`.",
]

REQUIRED_CATALOG_SNIPPETS = [
    "- direct Linux-style perf rerun route: `make -C zigux phase6-base64-perf`",
    "- current wrapper nuance: the helper-owned perf gate is directly runnable through `zigux/tests/phase6_build.zig`, and current `zigux/Makefile` now exposes a committed `phase6-base64-perf` target body; the remaining shared-route lag is the broader aggregate wrapper inventory plus the bootstrap workflow, not the helper-local Linux-style wrapper itself",
    "- direct Linux-style perf rerun route: `make -C zigux phase6-checksum-perf`",
    "- Reviewable on current `master`",
    "- `make -C zigux phase6-base64-perf`",
    "- `make -C zigux phase6-checksum-perf`",
    "- current blocked-route posture: the helper-local base64 and checksum slowdown gates are now directly readable through `lib/base64.zig`, `zigux/tests/phase6_base64_perf.zig`, `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, `zigux/tests/fixtures/phase6_checksum_vectors.zig`, and `zigux/tests/phase6_build.zig`, and `zigux/Makefile` now exposes committed `phase6-base64-perf` and `phase6-checksum-perf` target bodies, but the bootstrap workflow plus the aggregate `phase6-validate`, `phase6-perf`, and `phase6` route inventory still lag those helper-local wrappers",
]

REQUIRED_HELPER_EVIDENCE_SNIPPETS = [
    "- shared manifest: `zigux/tests/phase6_helper_parity_manifest.json`",
    "- direct C parity packet: `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, and `scripts/zigux/check-phase6-base64-c-parity.py`",
    "- direct corpus evidence checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
    "- direct C parity packet: `zigux/tests/phase6_checksum_c_parity.zig`, `zigux/tests/fixtures/phase6_checksum_c_harness.c`, and `scripts/zigux/check-phase6-checksum-c-parity.py`",
    "- helper-local packet checker: `scripts/zigux/check-phase6-hexdump-packet.py`",
    "Reopen this catalog only when one of the four roadmap anchors gains or loses a truthful helper-evidence row on `master`.",
]

REQUIRED_BASE64_SLICE_SNIPPETS = [
    "- direct focused perf route: `zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig`",
    "- current wrapper nuance: the helper-owned perf gate is directly runnable through `zigux/tests/phase6_build.zig`, and current `zigux/Makefile` now exposes a committed `phase6-base64-perf` target body; the remaining shared-route lag is the broader aggregate wrapper inventory plus the bootstrap workflow, not the helper-local Linux-style wrapper itself",
    "phase6_base64_c_casegen.zig",
]

REQUIRED_BSEARCH_SLICE_SNIPPETS = [
    "- `PHASE6_SLICE=bsearch-leaf-helper`",
    "- `bsearchEqualRangeMutable`",
    "- direct local corpus evidence checker route: `python3 scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
    "Reviewers should treat that fixture as compact shared packet support rather than as a separate standalone timing-style route.",
]

REQUIRED_CHECKSUM_SLICE_SNIPPETS = [
    "- current routed build packet now defines checksum helper and perf steps in `zigux/tests/phase6_build.zig`, while `zigux/Makefile` now exposes a committed `phase6-checksum-perf` target body and still advertises only `phase6-checksum-c-parity` as a phony route without a corresponding target body",
    "- direct Linux-style perf route: `make -C zigux phase6-checksum-perf`",
]

REQUIRED_HEXDUMP_SLICE_SNIPPETS = [
    "- `PHASE6_SLICE=hexdump-leaf-helper`",
    "- `zigux/tests/phase6_hexdump_perf_matrix.zig`",
    "- `make -C zigux phase6-hexdump-review`",
]

REQUIRED_PERF_SURVEY_SNIPPETS = [
    "* shared replay note: the current Phase 6 route inventory still names `make -C zigux phase6`, `make -C zigux phase6-base64-perf`, `make -C zigux phase6-checksum-perf`, and `make -C zigux phase6-hexdump-perf`, while current `zigux/Makefile` readback now also exposes committed target bodies for `phase6-base64-perf`, `phase6-bsearch-test`, `phase6-checksum-perf`, `phase6-hexdump-test`, `phase6-hexdump-review`, and `phase6-hexdump-perf`; the aggregate `phase6`, `phase6-validate`, and `phase6-perf` names still remain inventory-only wrapper markers in the committed file text available to this survey",
    "* base64 shared posture: `lib/base64.zig`, `zigux/tests/phase6_base64.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, and `zigux/tests/phase6_base64_perf.zig` are directly readable on current `master`, current `zigux/tests/phase6_build.zig` defines the dedicated `phase6-base64-perf` build step again, and `zigux/Makefile` now exposes a committed `phase6-base64-perf` target body; that slowdown gate is directly reviewable from the committed tree even though `.github/workflows/zigux-bootstrap.yml` still exposes Phase 6 perf coverage only through the shared checker bundle plus the hexdump perf replay",
    "* checksum exact thresholds: `zigux/tests/phase6_checksum_perf.zig` now keeps two helper-local slowdown cases, `64` at `reps = 20_000` and `1501` at `reps = 4_000`, each capped at `max_slowdown_pct = 150`, so the checksum perf packet is reviewable from committed evidence today even while the Linux-style wrapper inventory still lags that direct build route",
    "* makefile route nuance: current `zigux/Makefile` readback does expose committed target bodies for `phase6-base64-perf`, `phase6-bsearch-test`, `phase6-hexdump-test`, `phase6-hexdump-review`, `phase6-hexdump-perf`, and `phase6-checksum-perf`, so the inventory-only wrapper caveat now applies specifically to `phase6`, `phase6-validate`, and `phase6-perf`",
]

REQUIRED_TESTS_README_SNIPPETS = [
    "* `zigux/tests/phase6_base64_perf.zig`",
    "* `scripts/zigux/check-phase6-checksum-c-parity.py`",
    "* current public-tree-backed Phase 6 checksum packet: `lib/checksum.zig`, `zigux/tests/phase6_checksum.zig`, `zigux/tests/phase6_checksum_perf.zig`, and `zigux/tests/fixtures/phase6_checksum_vectors.zig`",
]

REQUIRED_BUILD_SNIPPETS = [
    'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 perf gate");',
    "base64_perf_step.dependOn(&run_base64_perf.step);",
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum perf gate");',
    "checksum_perf_step.dependOn(&run_checksum_perf.step);",
]

REQUIRED_MAKEFILE_SNIPPETS = [
    "PHONY += phase6-validate phase6-test phase6-bsearch-test phase6-base64-c-parity phase6-checksum-c-parity phase6-hexdump-test phase6-hexdump-review phase6-base64-perf phase6-checksum-perf phase6-hexdump-perf phase6-perf phase6",
    "phase6-base64-perf:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-base64-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "phase6-checksum-perf:",
    "\tcd $(ZIGUX_ROOT) && $(ZIG) build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
]

REQUIRED_WORKFLOW_SNIPPETS = [
    "- name: Self-test Phase 6 shared-surface checker",
    "- name: Run Phase 6 base64 C parity packet",
    "- name: Self-test Phase 6 checksum C parity checker",
    "- name: Check Phase 6 checksum C parity packet",
    "- name: Run Phase 6 bsearch focused packet",
    "- name: Run Phase 6 hexdump perf gate",
]

ABSENT_WORKFLOW_SNIPPETS = [
    "- name: Run Phase 6 base64 perf gate",
    "- name: Run Phase 6 checksum perf gate",
]

REQUIRED_PRESENT_ENTRYPOINTS_SNIPPETS = [
    'EXPECTED_HEXDUMP_PACKET_CHECKER = HEXDUMP_CHECKER_PATH.as_posix()',
    'EXPECTED_HEXDUMP_PERF_REFRESH = HEXDUMP_PERF_REFRESH_PATH.as_posix()',
]

SELF_TEST_CASE_COUNT = 16


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path.as_posix()}: {exc}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected Phase 6 marker in {path.as_posix()}: {snippet}")


def require_absent_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet in content:
            raise ValidationError(f"unexpected stale Phase 6 marker in {path.as_posix()}: {snippet}")


def helper_row(manifest_obj: dict[str, object], helper_id: str) -> dict[str, object]:
    helpers = manifest_obj.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError(f"missing helpers in {MANIFEST_PATH.as_posix()}")
    row = next((item for item in helpers if isinstance(item, dict) and item.get("id") == helper_id), None)
    if not isinstance(row, dict):
        raise ValidationError(f"missing {helper_id} helper row in {MANIFEST_PATH.as_posix()}")
    return row


def validate_manifest(repo_root: Path) -> None:
    manifest_obj = read_json(repo_root / MANIFEST_PATH)
    if not isinstance(manifest_obj, dict):
        raise ValidationError(f"expected object in {MANIFEST_PATH.as_posix()}")
    if manifest_obj.get("status") != "partially_blocked":
        raise ValidationError(f"unexpected Phase 6 status in {MANIFEST_PATH.as_posix()}")
    if manifest_obj.get("packet_state_summary") != EXPECTED_PACKET_STATE_SUMMARY:
        raise ValidationError(f"unexpected packet_state_summary in {MANIFEST_PATH.as_posix()}")
    if manifest_obj.get("shared_route_truthfulness_note") != EXPECTED_SHARED_ROUTE_NOTE:
        raise ValidationError(f"unexpected shared_route_truthfulness_note in {MANIFEST_PATH.as_posix()}")
    if manifest_obj.get("helper_evidence_catalog") != HELPER_EVIDENCE_CATALOG_PATH.as_posix():
        raise ValidationError(f"unexpected helper_evidence_catalog in {MANIFEST_PATH.as_posix()}")

    shared_gates = manifest_obj.get("shared_gates")
    if not isinstance(shared_gates, list) or not REQUIRED_SHARED_GATES.issubset(set(shared_gates)):
        raise ValidationError(f"missing required shared_gates entries in {MANIFEST_PATH.as_posix()}")

    present_entrypoints = manifest_obj.get("tests_root_present_entrypoints")
    if not isinstance(present_entrypoints, list) or not REQUIRED_PRESENT_ENTRYPOINTS.issubset(set(present_entrypoints)):
        raise ValidationError(f"missing required tests_root_present_entrypoints in {MANIFEST_PATH.as_posix()}")

    exact_checks = manifest_obj.get("exact_checks")
    if not isinstance(exact_checks, list) or not REQUIRED_EXACT_CHECKS.issubset(set(exact_checks)):
        raise ValidationError(f"missing required exact_checks in {MANIFEST_PATH.as_posix()}")

    blocked_routes = manifest_obj.get("inventory_only_blocked_routes")
    if set(blocked_routes or []) != EXPECTED_INVENTORY_ONLY_BLOCKED_ROUTES:
        raise ValidationError(f"unexpected inventory_only_blocked_routes in {MANIFEST_PATH.as_posix()}")

    base64 = helper_row(manifest_obj, "base64")
    if base64.get("external_parity") != BASE64_C_PARITY_CHECKER_PATH.as_posix():
        raise ValidationError(f"unexpected base64 external_parity in {MANIFEST_PATH.as_posix()}")
    if set(base64.get("tests") or []) != {
        BASE64_REPLAY_PATH.as_posix(),
        BASE64_C_PARITY_PATH.as_posix(),
        BASE64_PERF_PATH.as_posix(),
    }:
        raise ValidationError(f"unexpected base64 tests in {MANIFEST_PATH.as_posix()}")

    checksum = helper_row(manifest_obj, "checksum")
    if checksum.get("external_parity") != CHECKSUM_C_PARITY_CHECKER_PATH.as_posix():
        raise ValidationError(f"unexpected checksum external_parity in {MANIFEST_PATH.as_posix()}")
    if set(checksum.get("tests") or []) != {
        CHECKSUM_REPLAY_PATH.as_posix(),
        CHECKSUM_PERF_PATH.as_posix(),
        CHECKSUM_C_PARITY_PATH.as_posix(),
    }:
        raise ValidationError(f"unexpected checksum tests in {MANIFEST_PATH.as_posix()}")

    hexdump = helper_row(manifest_obj, "hexdump")
    if hexdump.get("packet_checker") != HEXDUMP_PACKET_CHECKER_PATH.as_posix():
        raise ValidationError(f"unexpected hexdump packet_checker in {MANIFEST_PATH.as_posix()}")
    if hexdump.get("perf_refresh_note") != HEXDUMP_PERF_REFRESH_PATH.as_posix():
        raise ValidationError(f"unexpected hexdump perf_refresh_note in {MANIFEST_PATH.as_posix()}")


def validate_paths(repo_root: Path) -> None:
    required_paths = {
        DOCUMENTATION_README_PATH,
        SCRIPTS_README_PATH,
        CATALOG_PATH,
        HELPER_EVIDENCE_CATALOG_PATH,
        PERF_SURVEY_PATH,
        BASE64_SLICE_PATH,
        BSEARCH_SLICE_PATH,
        CHECKSUM_SLICE_PATH,
        HEXDUMP_SLICE_PATH,
        TESTS_README_PATH,
        PHASE6_BUILD_PATH,
        MAKEFILE_PATH,
        WORKFLOW_PATH,
        SHARED_CHECKER_PATH,
        PRESENT_ENTRYPOINTS_CHECKER_PATH,
        BASE64_HELPER_PATH,
        BASE64_REPLAY_PATH,
        BASE64_PERF_PATH,
        BASE64_VECTORS_PATH,
        BASE64_C_PARITY_PATH,
        BASE64_C_CASEGEN_PATH,
        BASE64_C_PARITY_VECTORS_PATH,
        BASE64_C_HARNESS_PATH,
        BASE64_C_PARITY_CHECKER_PATH,
        BSEARCH_HELPER_PATH,
        BSEARCH_REPLAY_PATH,
        BSEARCH_LOWER_UPPER_PATH,
        BSEARCH_EQUALITY_PATH,
        BSEARCH_VECTORS_PATH,
        BSEARCH_CORPUS_EVIDENCE_CHECKER_PATH,
        CHECKSUM_HELPER_PATH,
        CHECKSUM_REPLAY_PATH,
        CHECKSUM_PERF_PATH,
        CHECKSUM_VECTORS_PATH,
        CHECKSUM_C_PARITY_PATH,
        CHECKSUM_C_HARNESS_PATH,
        CHECKSUM_C_PARITY_CHECKER_PATH,
        HEXDUMP_HELPER_PATH,
        HEXDUMP_REPLAY_PATH,
        HEXDUMP_PERF_PATH,
        HEXDUMP_PERF_MATRIX_PATH,
        HEXDUMP_VECTORS_PATH,
        HEXDUMP_PACKET_CHECKER_PATH,
        HEXDUMP_PERF_REFRESH_PATH,
    }
    for rel_path in sorted(path.as_posix() for path in required_paths):
        if not (repo_root / rel_path).exists():
            raise ValidationError(f"missing required Phase 6 path: {rel_path}")


def run_checks(repo_root: Path) -> None:
    validate_paths(repo_root)
    validate_manifest(repo_root)
    require_snippets(repo_root / SCRIPTS_README_PATH, REQUIRED_SCRIPTS_README_SNIPPETS)
    require_snippets(repo_root / CATALOG_PATH, REQUIRED_CATALOG_SNIPPETS)
    require_snippets(repo_root / HELPER_EVIDENCE_CATALOG_PATH, REQUIRED_HELPER_EVIDENCE_SNIPPETS)
    require_snippets(repo_root / BASE64_SLICE_PATH, REQUIRED_BASE64_SLICE_SNIPPETS)
    require_snippets(repo_root / BSEARCH_SLICE_PATH, REQUIRED_BSEARCH_SLICE_SNIPPETS)
    require_snippets(repo_root / CHECKSUM_SLICE_PATH, REQUIRED_CHECKSUM_SLICE_SNIPPETS)
    require_snippets(repo_root / HEXDUMP_SLICE_PATH, REQUIRED_HEXDUMP_SLICE_SNIPPETS)
    require_snippets(repo_root / PERF_SURVEY_PATH, REQUIRED_PERF_SURVEY_SNIPPETS)
    require_snippets(repo_root / TESTS_README_PATH, REQUIRED_TESTS_README_SNIPPETS)
    require_snippets(repo_root / PHASE6_BUILD_PATH, REQUIRED_BUILD_SNIPPETS)
    require_snippets(repo_root / MAKEFILE_PATH, REQUIRED_MAKEFILE_SNIPPETS)
    require_snippets(repo_root / WORKFLOW_PATH, REQUIRED_WORKFLOW_SNIPPETS)
    require_absent_snippets(repo_root / WORKFLOW_PATH, ABSENT_WORKFLOW_SNIPPETS)
    require_snippets(repo_root / PRESENT_ENTRYPOINTS_CHECKER_PATH, REQUIRED_PRESENT_ENTRYPOINTS_SNIPPETS)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    placeholder_files = [
        SHARED_CHECKER_PATH,
        BASE64_HELPER_PATH,
        BASE64_REPLAY_PATH,
        BASE64_PERF_PATH,
        BASE64_VECTORS_PATH,
        BASE64_C_PARITY_PATH,
        BASE64_C_CASEGEN_PATH,
        BASE64_C_PARITY_VECTORS_PATH,
        BASE64_C_HARNESS_PATH,
        BASE64_C_PARITY_CHECKER_PATH,
        BSEARCH_HELPER_PATH,
        BSEARCH_REPLAY_PATH,
        BSEARCH_LOWER_UPPER_PATH,
        BSEARCH_EQUALITY_PATH,
        BSEARCH_VECTORS_PATH,
        BSEARCH_CORPUS_EVIDENCE_CHECKER_PATH,
        CHECKSUM_HELPER_PATH,
        CHECKSUM_REPLAY_PATH,
        CHECKSUM_PERF_PATH,
        CHECKSUM_VECTORS_PATH,
        CHECKSUM_C_PARITY_PATH,
        CHECKSUM_C_HARNESS_PATH,
        CHECKSUM_C_PARITY_CHECKER_PATH,
        HEXDUMP_HELPER_PATH,
        HEXDUMP_REPLAY_PATH,
        HEXDUMP_PERF_PATH,
        HEXDUMP_PERF_MATRIX_PATH,
        HEXDUMP_VECTORS_PATH,
        HEXDUMP_PACKET_CHECKER_PATH,
    ]
    for path in placeholder_files:
        write(root / path, "placeholder\n")

    write(root / DOCUMENTATION_README_PATH, "# Zigux Documentation\n")
    write(root / HEXDUMP_PERF_REFRESH_PATH, "# Phase 6 Hexdump Perf Refresh\n")
    write(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_SCRIPTS_README_SNIPPETS) + "\n")
    write(root / CATALOG_PATH, "\n".join(REQUIRED_CATALOG_SNIPPETS) + "\n")
    write(root / HELPER_EVIDENCE_CATALOG_PATH, "\n".join(REQUIRED_HELPER_EVIDENCE_SNIPPETS) + "\n")
    write(root / BASE64_SLICE_PATH, "\n".join(REQUIRED_BASE64_SLICE_SNIPPETS) + "\n")
    write(root / BSEARCH_SLICE_PATH, "\n".join(REQUIRED_BSEARCH_SLICE_SNIPPETS) + "\n")
    write(root / CHECKSUM_SLICE_PATH, "\n".join(REQUIRED_CHECKSUM_SLICE_SNIPPETS) + "\n")
    write(root / HEXDUMP_SLICE_PATH, "\n".join(REQUIRED_HEXDUMP_SLICE_SNIPPETS) + "\n")
    write(root / PERF_SURVEY_PATH, "\n".join(REQUIRED_PERF_SURVEY_SNIPPETS) + "\n")
    write(root / TESTS_README_PATH, "\n".join(REQUIRED_TESTS_README_SNIPPETS) + "\n")
    write(root / PHASE6_BUILD_PATH, "\n".join(REQUIRED_BUILD_SNIPPETS) + "\n")
    write(root / MAKEFILE_PATH, "\n".join(REQUIRED_MAKEFILE_SNIPPETS) + "\n")
    write(root / WORKFLOW_PATH, "\n".join(REQUIRED_WORKFLOW_SNIPPETS) + "\n")
    write(root / PRESENT_ENTRYPOINTS_CHECKER_PATH, "\n".join(REQUIRED_PRESENT_ENTRYPOINTS_SNIPPETS) + "\n")

    manifest = {
        "status": "partially_blocked",
        "packet_state_summary": EXPECTED_PACKET_STATE_SUMMARY,
        "shared_route_truthfulness_note": EXPECTED_SHARED_ROUTE_NOTE,
        "shared_gates": sorted(REQUIRED_SHARED_GATES),
        "helper_evidence_catalog": HELPER_EVIDENCE_CATALOG_PATH.as_posix(),
        "tests_root_present_entrypoints": sorted(REQUIRED_PRESENT_ENTRYPOINTS),
        "exact_checks": sorted(REQUIRED_EXACT_CHECKS),
        "inventory_only_blocked_routes": sorted(EXPECTED_INVENTORY_ONLY_BLOCKED_ROUTES),
        "helpers": [
            {
                "id": "base64",
                "tests": sorted({
                    BASE64_REPLAY_PATH.as_posix(),
                    BASE64_C_PARITY_PATH.as_posix(),
                    BASE64_PERF_PATH.as_posix(),
                }),
                "external_parity": BASE64_C_PARITY_CHECKER_PATH.as_posix(),
            },
            {"id": "bsearch", "corpus_evidence_checker": BSEARCH_CORPUS_EVIDENCE_CHECKER_PATH.as_posix()},
            {
                "id": "checksum",
                "tests": sorted({
                    CHECKSUM_REPLAY_PATH.as_posix(),
                    CHECKSUM_PERF_PATH.as_posix(),
                    CHECKSUM_C_PARITY_PATH.as_posix(),
                }),
                "external_parity": CHECKSUM_C_PARITY_CHECKER_PATH.as_posix(),
            },
            {
                "id": "hexdump",
                "packet_checker": HEXDUMP_PACKET_CHECKER_PATH.as_posix(),
                "perf_refresh_note": HEXDUMP_PERF_REFRESH_PATH.as_posix(),
            },
        ],
    }
    write(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")


def assert_failure(root: Path, rel_path: Path, old: str, new: str) -> None:
    path = root / rel_path
    original = read_text(path)
    if old not in original:
        raise AssertionError(f"self-test marker not found in {rel_path.as_posix()}: {old}")
    path.write_text(original.replace(old, new, 1), encoding="utf-8")
    try:
        run_checks(root)
    except ValidationError:
        pass
    else:
        raise AssertionError(f"expected failure for {rel_path.as_posix()}")
    path.write_text(original, encoding="utf-8")


def run_self_test() -> None:
    tmpdir = Path(tempfile.mkdtemp(prefix="phase6_shared_surface_"))
    try:
        scaffold_repo(tmpdir)
        run_checks(tmpdir)
        assert_failure(tmpdir, MANIFEST_PATH, '"shared_route_truthfulness_note"', '"shared_route_truthfulness_note_missing"')
        assert_failure(tmpdir, MANIFEST_PATH, '"partially_blocked"', '"blocked"')
        assert_failure(tmpdir, MANIFEST_PATH, '"make -C zigux phase6-base64-perf"', '"make -C zigux phase6-base64-perf-missing"')
        assert_failure(tmpdir, MANIFEST_PATH, '"Documentation/zigux/README.md"', '"Documentation/zigux/README-missing.md"')
        assert_failure(tmpdir, MANIFEST_PATH, '"zigux/tests/README.md"', '"zigux/tests/README-missing.md"')
        assert_failure(tmpdir, MANIFEST_PATH, '"helper_evidence_catalog"', '"helper_evidence_catalog_missing"')
        assert_failure(tmpdir, CATALOG_PATH, "phase6-base64-perf", "phase6-base64-perf-missing")
        assert_failure(tmpdir, HELPER_EVIDENCE_CATALOG_PATH, "check-phase6-bsearch-corpus-evidence.py", "check-phase6-bsearch-evidence.py")
        assert_failure(tmpdir, BASE64_SLICE_PATH, "phase6_base64_c_casegen.zig", "phase6_base64_c_casegen_missing.zig")
        assert_failure(tmpdir, PERF_SURVEY_PATH, "phase6-base64-perf", "phase6-base64-perf-missing")
        assert_failure(tmpdir, CHECKSUM_SLICE_PATH, "phase6-checksum-perf", "phase6-checksum-perf-missing")
        assert_failure(tmpdir, MAKEFILE_PATH, "phase6-base64-perf:", "phase6-base64-perf-missing:")
        assert_failure(tmpdir, WORKFLOW_PATH, "Check Phase 6 checksum C parity packet", "Check Phase 6 checksum parity packet")
        assert_failure(tmpdir, SCRIPTS_README_PATH, "phase6-validate", "phase6-validate-missing")
        assert_failure(tmpdir, TESTS_README_PATH, "phase6_checksum_perf.zig", "phase6_checksum_perf_missing.zig")
        assert_failure(tmpdir, PRESENT_ENTRYPOINTS_CHECKER_PATH, "EXPECTED_HEXDUMP_PACKET_CHECKER", "EXPECTED_HEXDUMP_PACKET_CHECKER_MISSING")
        print("self-test passed")
        print(f"PHASE6_SHARED_SURFACE_SELF_TEST_CASE_COUNT={SELF_TEST_CASE_COUNT}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Path to the Zigux repository root")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checks")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    run_checks(Path(args.repo_root).resolve())
    print("Phase 6 shared checker matches the current base64, bsearch, checksum, and hexdump packet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
