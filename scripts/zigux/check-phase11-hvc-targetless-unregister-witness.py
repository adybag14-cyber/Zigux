#!/usr/bin/env python3
"""Fail-closed checker for the Phase 11 HVC targetless-unregister witness packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path


REQUIRED_COMMAND = "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig"
PHASE11_VALIDATE_COMMAND = "make -C zigux phase11-validate"
PHASE11_VALIDATE_STEP = "Validate current Phase 11 support bundle"
TARGETLESS_WITNESS_SELF_TEST_COMMAND = (
    "python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py --self-test"
)
TARGETLESS_WITNESS_COMMAND = (
    "python3 scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"
)
TARGETLESS_WITNESS_TEST_NAME = "phase11-hvc-targetless-unregister-gap"
TARGETLESS_WITNESS_REPLAY = "zigux/tests/phase11_hvc_targetless_unregister_gap.zig"
TARGETLESS_WITNESS_BUILD_REPLAY = "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig"

WORKFLOW_PATH = ".github/workflows/zigux-bootstrap.yml"
LANE_NOTE_PATH = "Documentation/zigux/phase11-driver-lane-sequencing.md"
CLEANUP_COMPANION_PATH = "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md"
VALIDATION_MATRIX_PATH = "Documentation/zigux/phase11-hvc-console-validation-matrix.md"
SURVEY_PATH = "Documentation/zigux/phase11-hvc-console-survey.md"
VERIFY_BOUNDARY_PATH = "Documentation/zigux/phase11-hvc-verify-helper-boundary.md"
DRIVER_PATH = "drivers/tty/hvc/hvc_console.zig"
CLEANUP_CHECKER_PATH = "scripts/zigux/check-phase11-hvc-cleanup-current-head.py"
VALIDATE_PHASE11_PATH = "scripts/zigux/validate-phase11.py"
MAKEFILE_PATH = "zigux/Makefile"
INVENTORY_PATH = "zigux/tests/fixtures/phase11_build_inventory.json"
WITNESS_PATH = TARGETLESS_WITNESS_REPLAY
WITNESS_BUILD_PATH = TARGETLESS_WITNESS_BUILD_REPLAY
SELF_PATH = "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"

CLEANUP_SELF_TEST_COMMAND = "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py --self-test"
CLEANUP_COMMAND = "python3 scripts/zigux/check-phase11-hvc-cleanup-current-head.py"

REQUIRED_PACKET_FILES = (
    WORKFLOW_PATH,
    LANE_NOTE_PATH,
    CLEANUP_COMPANION_PATH,
    VALIDATION_MATRIX_PATH,
    SURVEY_PATH,
    VERIFY_BOUNDARY_PATH,
    DRIVER_PATH,
    CLEANUP_CHECKER_PATH,
    SELF_PATH,
    VALIDATE_PHASE11_PATH,
    MAKEFILE_PATH,
    INVENTORY_PATH,
    WITNESS_PATH,
    WITNESS_BUILD_PATH,
)

FILE_EXPECTATIONS = {
    WORKFLOW_PATH: (
        PHASE11_VALIDATE_STEP,
        PHASE11_VALIDATE_COMMAND,
    ),
    LANE_NOTE_PATH: (
        DRIVER_PATH,
        VERIFY_BOUNDARY_PATH,
        CLEANUP_COMPANION_PATH,
        CLEANUP_CHECKER_PATH,
        SELF_PATH,
        WITNESS_PATH,
        WITNESS_BUILD_PATH,
    ),
    CLEANUP_COMPANION_PATH: (
        DRIVER_PATH,
        VERIFY_BOUNDARY_PATH,
        CLEANUP_CHECKER_PATH,
        SELF_PATH,
        WITNESS_PATH,
        WITNESS_BUILD_PATH,
        "standalone targetless-unregister witness",
        "separate failure-mode replay",
    ),
    VALIDATION_MATRIX_PATH: (
        VERIFY_BOUNDARY_PATH,
        CLEANUP_COMPANION_PATH,
        CLEANUP_CHECKER_PATH,
        "scripts/zigux/check-phase11-build-inventory.py",
        SELF_PATH,
        INVENTORY_PATH,
        WITNESS_PATH,
        WITNESS_BUILD_PATH,
        "make -C zigux phase11-validate",
        "witness shard now rereads the live starter and the boundary note together",
        "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet",
    ),
    SURVEY_PATH: (
        CLEANUP_COMPANION_PATH,
        CLEANUP_CHECKER_PATH,
        SELF_PATH,
        WITNESS_PATH,
        WITNESS_BUILD_PATH,
        "standalone targetless-unregister witness pair likewise stays",
        "without promoting itself into the shared three-entry build inventory",
    ),
    VERIFY_BOUNDARY_PATH: (
        "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge",
        "`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable",
        "`targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.",
        "the literal-fallback helpers keep both the sanitized targetless sysrq path and the non-kernel sysrq literal fallback explicit",
    ),
    DRIVER_PATH: (
        "pub const TargetlessNotifierEdgeSummary = struct {",
        "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {",
        "targetless_no_unregister_edge: bool,",
        "targetless_unregister_request_sanitized: bool,",
        "keeps_live_notifier_execution_out_of_scope: bool,",
        ".targetless_no_unregister_edge = request.notifier_registered and !request.target_present and !request.unregister_requested,",
        ".targetless_unregister_request_sanitized = request.notifier_registered and !request.target_present and request.unregister_requested,",
        ".unregister_requested = request.unregister_requested and request.target_present and request.notifier_registered,",
        'test "phase11 hvc console keeps targetless notifier no-unregister edge reviewable" {',
        "try std.testing.expect(targetless_sanitized.targetless_unregister_request_sanitized);",
        "try std.testing.expect(!targetless_sanitized.unregister_requested);",
        "try std.testing.expect(targetless_sanitized.keeps_live_notifier_execution_out_of_scope);",
        'test "phase11 hvc console keeps unregistered targeted notifier-unregister request sanitized" {',
        "try std.testing.expect(!summary.unregister_requested);",
    ),
    CLEANUP_CHECKER_PATH: (
        "check-phase11-hvc-targetless-unregister-witness.py",
        "phase11_hvc_targetless_unregister_gap_build.zig",
    ),
    VALIDATE_PHASE11_PATH: (
        CLEANUP_CHECKER_PATH,
        WITNESS_PATH,
        WITNESS_BUILD_PATH,
        "phase11-hvc-cleanup-current-head",
        '"phase11-hvc-targetless-unregister-witness-self-test",',
        '("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py", "--self-test"),',
        '"phase11-hvc-targetless-unregister-witness",',
        '("python", "scripts/zigux/check-phase11-hvc-targetless-unregister-witness.py"),',
        "phase11-hvc-targetless-unregister-gap-build",
    ),
    MAKEFILE_PATH: (
        "phase11-validate:",
        "phase11_hvc_targetless_unregister_gap_build.zig",
    ),
    WITNESS_PATH: (
        'test "phase11 hvc notifier witness records current-head targetless unregister sanitizer" {',
        f'const driver = try readRepoFile("{DRIVER_PATH}");',
        f'const boundary = try readRepoFile("{VERIFY_BOUNDARY_PATH}');