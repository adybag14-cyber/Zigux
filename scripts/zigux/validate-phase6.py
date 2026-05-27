#!/usr/bin/env python3
"""Validate the current Phase 6 shared helper-evidence packet."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

HELPER_EVIDENCE_CATALOG = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
HELPER_PARITY_CATALOG = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
RUNTIME_COMMAND_ENVIRONMENT_GAP_SURVEY = Path("Documentation/zigux/phase6-runtime-command-environment-gap-survey.md")
RUNTIME_TASK_POLL_EVENT_LOOP_GAP_SURVEY = Path(
    "Documentation/zigux/phase6-runtime-task-poll-event-loop-gap-survey.md"
)
HELPER_EVIDENCE_MANIFEST = Path("zigux/tests/phase6_helper_evidence_manifest.json")
HELPER_PARITY_MANIFEST = Path("zigux/tests/phase6_helper_parity_manifest.json")
PHASE6_BUILD = Path("zigux/tests/phase6_build.zig")
MAKEFILE = Path("zigux/Makefile")
WORKFLOW = Path(".github/workflows/zigux-bootstrap.yml")
SHARED_SURFACE_CHECKER = Path("scripts/zigux/check-phase6-shared-surface.py")
PRESENT_ENTRYPOINTS_CHECKER = Path("scripts/zigux/check-phase6-present-entrypoints.py")
BASE64_CORPUS_CHECKER = Path("scripts/zigux/check-phase6-base64-corpus-determinism.py")
BASE64_C_PARITY_CHECKER = Path("scripts/zigux/check-phase6-base64-c-parity.py")
BSEARCH_CORPUS_CHECKER = Path("scripts/zigux/check-phase6-bsearch-corpus-evidence.py")
BSEARCH_C_PARITY_CHECKER = Path("scripts/zigux/check-phase6-bsearch-c-parity.py")
BASE64_BSEARCH_PERF_MARKERS_CHECKER = Path(
    "scripts/zigux/check-phase6-base64-bsearch-perf-markers.py"
)
CHECKSUM_CORPUS_CHECKER = Path("scripts/zigux/check-phase6-checksum-corpus-evidence.py")
CHECKSUM_C_PARITY_CHECKER = Path("scripts/zigux/check-phase6-checksum-c-parity.py")
CHECKSUM_HEXDUMP_PERF_MARKERS_CHECKER = Path(
    "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py"
)
HEXDUMP_PACKET_CHECKER = Path("scripts/zigux/check-phase6-hexdump-packet.py")
HEXDUMP_ROUTE_CHECKER = Path("scripts/zigux/check-phase6-hexdump-route.py")
PERF_THRESHOLD_CHECKER = Path("scripts/zigux/check-phase6-perf-threshold-markers.py")
RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET_CHECKER = Path(
    "scripts/zigux/check-phase6-runtime-task-poll-event-loop-shared-packet.py"
)

CHECKER_INVOCATIONS = [
    (SHARED_SURFACE_CHECKER, "--repo-root"),
    (PRESENT_ENTRYPOINTS_CHECKER, "--repo-root"),
    (BASE64_CORPUS_CHECKER, "--repo-root"),
    (BASE64_C_PARITY_CHECKER, None),
    (BSEARCH_CORPUS_CHECKER, "--repo-root"),
    (BSEARCH_C_PARITY_CHECKER, None),
    (BASE64_BSEARCH_PERF_MARKERS_CHECKER, "--repo-root"),
    (CHECKSUM_CORPUS_CHECKER, "--repo-root"),
    (CHECKSUM_C_PARITY_CHECKER, None),
    (CHECKSUM_HEXDUMP_PERF_MARKERS_CHECKER, "--repo-root"),
    (HEXDUMP_PACKET_CHECKER, "--repo-root"),
    (HEXDUMP_ROUTE_CHECKER, "--root"),
    (PERF_THRESHOLD_CHECKER, "--repo-root"),
    (RUNTIME_TASK_POLL_EVENT_LOOP_SHARED_PACKET_CHECKER, "--root"),
]

REQUIRED_FILES = [
    HELPER_EVIDENCE_CATALOG,
    HELPER_PARITY_CATALOG,
    RUNTIME_COMMAND_ENVIRONMENT_GAP_SURVEY,
    RUNTIME_TASK_POLL_EVENT_LOOP_GAP_SURVEY,
    HELPER_EVIDENCE_MANIFEST,
    HELPER_PARITY_MANIFEST,
    PHASE6_BUILD,
    MAKEFILE,
    WORKFLOW,
    *[checker for checker, _ in CHECKER_INVOCATIONS],
]

EXPECTED_HELPER_EVIDENCE_PACKET = "phase6-helper-evidence"
EXPECTED_HELPER_PARITY_PACKET = "phase6-helper-parity"
EXPECTED_PHASE = "Phase 6"
EXPECTED_SURVEYED_HEAD = "current-master-readback-2026-05-22"
EXPECTED_EVIDENCE_LANE_SCOPE = "shared helper-evidence rows and machine-readable manifest only"
EXPECTED_PARITY_LANE_SCOPE = "shared helper-parity rows and machine-readable manifest only"
EXPECTED_CURRENT_DIRECT_READBACK_COMPANIONS = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-hexdump-slice.md",
    "Documentation/zigux/phase6-hexdump-perf-refresh.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "Documentation/zigux/phase6-runtime-command-environment-gap-survey.md",
    "Documentation/zigux/README.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/check-phase6-present-entrypoints.py",
    "scripts/zigux/check-phase6-base64-bsearch-perf-markers.py",
    "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "scripts/zigux/check-phase6-perf-threshold-markers.py",
    "scripts/zigux/check-phase6-hexdump-packet.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
]
EXPECTED_SHARED_DIRECT_EVIDENCE = [
    "Documentation/zigux/phase6-helper-evidence-catalog.md",
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "Documentation/zigux/phase6-perf-gate-survey.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
    "zigux/Makefile",
    "zigux/tests/phase6_build.zig",
    "zigux/tests/phase6_helper_evidence_manifest.json",
    "zigux/tests/phase6_helper_parity_manifest.json",
    "scripts/zigux/check-phase6-shared-surface.py",
    "scripts/zigux/check-phase6-present-entrypoints.py",
    "scripts/zigux/check-phase6-base64-bsearch-perf-markers.py",
    "scripts/zigux/validate-phase6.py",
    "scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "scripts/zigux/check-phase6-perf-threshold-markers.py",
    "scripts/zigux/check-phase6-hexdump-packet.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
]
EXPECTED_ROADMAP_ANCHORS = ["lib/base64.c", "lib/bsearch.c", "lib/checksum.c", "lib/hexdump.c"]
EXPECTED_SHARED_PERF_WRAPPER = "make -C zigux phase6-perf"
EXPECTED_SHARED_PERF_WRAPPER_KEYS = ["base64", "bsearch", "checksum", "hexdump"]
EXPECTED_SHARED_PUBLIC_COMPANIONS = []
EXPECTED_BASE64_DIRECT_GAPS: list[str] = []
EXPECTED_EVIDENCE_CURRENT_GAPS = EXPECTED_BASE64_DIRECT_GAPS
EXPECTED_PARITY_FOLLOW_THROUGH_GAPS = []
EXPECTED_SHARED_REPLAY_INVENTORY = [
    "zig build phase6-base64-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-test",
    "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-base64-perf",
    "python3 scripts/zigux/check-phase6-base64-c-parity.py",
    "zig build phase6-bsearch-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-test",
    "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-bsearch-perf",
    "python3 scripts/zigux/check-phase6-bsearch-c-parity.py",
    "python3 scripts/zigux/check-phase6-base64-bsearch-perf-markers.py",
    "zig build phase6-checksum-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-test",
    "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf-matrix-test",
    "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-checksum-perf",
    "python3 scripts/zigux/check-phase6-checksum-c-parity.py",
    "python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py",
    "python3 scripts/zigux/check-phase6-perf-threshold-markers.py",
    "python3 scripts/zigux/check-phase6-hexdump-packet.py",
    "python3 scripts/zigux/check-phase6-hexdump-route.py",
    "zig build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-review",
    "zig build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-perf-matrix-test",
    "zig build phase6-hexdump-test --build-file zigux/tests/phase6_build.zig",
    "make -C zigux phase6-hexdump-test",
    "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe",
    "make -C zigux phase6-hexdump-perf",
    "make -C zigux phase6-perf",
]

REQUIRED_MAKEFILE_SNIPPETS = [
    "phase6-validate:",
    "$(PYTHON) scripts/zigux/validate-phase6.py",
    "phase6-base64-perf:",
    "phase6-bsearch-perf:",
    "$(ZIG) build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-perf-matrix-test:",
    "$(ZIG) build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
    "phase6-checksum-perf:",
    "phase6-hexdump-review:",
    "phase6-perf: phase6-base64-perf phase6-bsearch-perf phase6-checksum-perf phase6-hexdump-review phase6-hexdump-perf-matrix-test phase6-hexdump-perf",
]

REQUIRED_BUILD_SNIPPETS = [
    'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 helper perf gate");',
    'const bsearch_perf_root_module = b.createModule(.{',
    'const bsearch_perf_step = b.step("phase6-bsearch-perf", "Run Phase 6 bsearch helper perf gate");',
    "const checksum_perf_matrix_test_step = b.step(",
    'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
    'const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");',
]

REQUIRED_WORKFLOW_SNIPPETS = [
    "- name: Run current Phase 6 shared perf route",
    "run: make -C zigux phase6-perf",
]

REQUIRED_CATALOG_SNIPPETS = [
    "- dedicated slowdown replay: `zigux/tests/phase6_bsearch_perf.zig`",
    "## Roadmap perf-gap readback",
    "## Current shared replay inventory",
    "- `python3 scripts/zigux/check-phase6-base64-c-parity.py`",
    "- `make -C zigux phase6-bsearch-perf`",
    "- `python3 scripts/zigux/check-phase6-base64-bsearch-perf-markers.py`",
    "- `make -C zigux phase6-checksum-perf-matrix-test`",
    "- `python3 scripts/zigux/check-phase6-checksum-c-parity.py`",
    "- `python3 scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`",
    "- `python3 scripts/zigux/check-phase6-perf-threshold-markers.py`",
    "A targeted authenticated current-master reread on 2026-05-27 also directly recovered `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` and `zigux/tests/phase6_base64_c_casegen.zig`, so the Phase 6 base64 packet no longer carries a known direct-readback generator gap.",
]

REQUIRED_PARITY_CATALOG_SNIPPETS = [
    "- direct helper-evidence companion: `Documentation/zigux/phase6-helper-evidence-catalog.md`",
    "- helper-evidence row: `zigux/tests/phase6_base64_perf.zig`, `zigux/tests/phase6_base64_c_parity.zig`, `zigux/tests/fixtures/phase6_base64_vectors.zig`, `zigux/tests/fixtures/phase6_base64_c_harness.c`, `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig`, `zigux/tests/phase6_base64_c_casegen.zig`, `scripts/zigux/check-phase6-base64-corpus-determinism.py`, `scripts/zigux/check-phase6-base64-c-parity.py`, `Documentation/zigux/phase6-base64-slice.md`, `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, and `zigux/tests/phase6_helper_parity_manifest.json`",
    "- current posture: direct helper readback is restored for the helper, focused replay, perf replay, fixture surface, dedicated corpus checker, direct C parity runner, direct C parity harness, direct C parity vectors companion, direct C parity casegen companion, direct C parity checker, and slice note. A targeted authenticated current-master reread on 2026-05-27 directly recovered `zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig` and `zigux/tests/phase6_base64_c_casegen.zig`, so the base64 row no longer carries a known generator-side direct-readback gap.",
    "- current posture: direct helper readback is restored for the helper, focused replay, fixture-owned perf packet, direct C parity runner, direct C parity harness, direct C parity checker, and slice note, so the checksum row now ships the same external parity review hook as the other portability-sensitive Phase 6 helpers without reopening hexdump work",
    "scripts/zigux/check-phase6-perf-threshold-markers.py",
    "Treat this file as the broader parity companion for the current helper-evidence packet rather than as a substitute for the directly readable shared packet in `Documentation/zigux/phase6-helper-evidence-catalog.md`, `zigux/tests/phase6_helper_evidence_manifest.json`, `zigux/tests/phase6_helper_parity_manifest.json`, `scripts/zigux/check-phase6-shared-surface.py`, `scripts/zigux/check-phase6-present-entrypoints.py`, `scripts/zigux/check-phase6-base64-bsearch-perf-markers.py`, `scripts/zigux/validate-phase6.py`, `scripts/zigux/check-phase6-checksum-hexdump-perf-markers.py`, `scripts/zigux/check-phase6-perf-threshold-markers.py`, `scripts/zigux/check-phase6-hexdump-packet.py`, `scripts/zigux/check-phase6-hexdump-route.py`, `zigux/tests/phase6_build.zig`, `zigux/Makefile`, and `Documentation/zigux/phase6-perf-gate-survey.md`.",
    "broader reminder surfaces can keep the shared survey plus the base64-bsearch, checksum-hexdump, and perf-threshold guard surfaces inside the directly readable shared packet instead of treating any of those guards as fallback-only evidence.",
]

REQUIRED_PARITY_COVERAGE_NOTE_SNIPPETS = [
    "Documentation/zigux/phase6-helper-parity-catalog.md",
    "scripts/zigux/check-phase6-base64-c-parity.py",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
    "A targeted authenticated current-master reread on 2026-05-27 also directly recovered zigux/tests/fixtures/phase6_base64_c_parity_vectors.zig and zigux/tests/phase6_base64_c_casegen.zig, so the base64 helper row no longer carries a known generator-side direct-readback gap.",
]

REQUIRED_PARITY_PERF_NOTE_SNIPPETS = [
    "zigux/tests/phase6_bsearch_perf.zig",
    "zigux/tests/phase6_hexdump_perf_matrix.zig",
]

EXPECTED_BSEARCH_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
    "scripts/zigux/check-phase6-bsearch-c-parity.py",
]

EXPECTED_CHECKSUM_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-checksum-corpus-evidence.py",
    "scripts/zigux/check-phase6-checksum-c-parity.py",
]

EXPECTED_HEXDUMP_CHECKER_SURFACES = [
    "scripts/zigux/check-phase6-hexdump-packet.py",
    "scripts/zigux/check-phase6-hexdump-route.py",
]

SELF_TEST_CASE_COUNT = 33


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def read_json(path: Path) -> dict[str, object]:
    return json.loads(read_text(path))


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"missing expected Phase 6 marker in {path.as_posix()}: {snippet}")


def require_text_snippets(name: str, content: object, snippets: list[str]) -> None:
    if not isinstance(content, str):
        raise ValidationError(f"{name} missing")
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(f"{name} drifted: {snippet}")


def extract_shared_perf_wrapper_keys(helper_parity_manifest: dict[str, object]) -> list[str]:
    helpers = helper_parity_manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError("phase6 helper parity helpers missing")

    keys: list[str] = []
    for helper in helpers:
        if not isinstance(helper, dict):
            continue
        current_perf_evidence = helper.get("current_perf_evidence")
        if not isinstance(current_perf_evidence, dict):
            continue
        routes = current_perf_evidence.get("linux_style_rerun_routes")
        if isinstance(routes, list) and EXPECTED_SHARED_PERF_WRAPPER in routes:
            key = helper.get("key")
            if isinstance(key, str):
                keys.append(key)
    return keys


def run_checker(root: Path, checker: Path, flag: str | None) -> None:
    cmd = [sys.executable, str(root / checker)]
    if flag is not None:
        cmd.extend([flag, str(root)])
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise ValidationError(f"{checker.as_posix()} failed: {detail}")
