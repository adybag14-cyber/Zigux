#!/usr/bin/env python3
"""Fail-close the current Phase 3 scripts-root tooling inventory."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

SCRIPTS_README_PATH = Path("scripts/zigux/README.md")

RUNNER_FILE = Path("scripts/zigux/run-phase3-checks.py")
SHARED_TESTS_ROUTES_FILE = Path("scripts/zigux/check-phase3-shared-tests-routes.py")
ABI_MANIFEST_REPLAY_ROUTES_FILE = Path(
    "scripts/zigux/check-phase3-abi-manifest-replay-routes.py"
)
BINDING_FILE = Path("zigux/bindings/dev_t.zig")
NOTIFIER_BINDING_FILE = Path("zigux/bindings/notifier_abi.zig")
NARROW_UNSAFE_FILE = Path("zigux/unsafe/narrow.zig")
UAPI_FILE = Path("zigux/uapi/dev_t.zig")
LOW_LEVEL_WRAPPER_SURVEY_VALIDATOR_FILE = Path(
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py"
)
LOW_LEVEL_WRAPPER_REPLAY_FILE = Path("zigux/tests/phase3_low_level_wrappers.zig")
LOW_LEVEL_WRAPPER_BUILD_FILE = Path("zigux/tests/phase3_low_level_wrappers_build.zig")
EXPORT_UAPI_LAYOUT_REPLAY_FILE = Path("zigux/tests/phase3_export_uapi_layout.zig")
EXPORT_UAPI_LAYOUT_BUILD_FILE = Path("zigux/tests/phase3_export_uapi_layout_build.zig")
EXPORT_UAPI_C_HEADER_SMOKE_CHECK_FILE = Path(
    "scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"
)
EXPORT_UAPI_C_HEADER_SMOKE_REPLAY_FILE = Path(
    "zigux/tests/phase3_export_uapi_c_header_smoke.c"
)
WORKFLOW_FILE = Path(".github/workflows/zigux-bootstrap.yml")
POLICY_STARTER_BUILD_FILE = Path("zigux/tests/phase3_policy_starter_packet_build.zig")
POLICY_DUMP_REPLAY_FILE = Path("zigux/tests/phase3_policy_dump.zig")
POLICY_DUMP_BUILD_FILE = Path("zigux/tests/phase3_policy_dump_build.zig")
XARRAY_SLOT_HELPER_FILE = Path("zigux/helpers/xarray_slot_view.zig")
XARRAY_SLOT_STARTER_FILE = Path("zigux/tests/phase3_xarray_slot_starter_packet.zig")
XARRAY_SLOT_STARTER_BUILD_FILE = Path(
    "zigux/tests/phase3_xarray_slot_starter_packet_build.zig"
)
XARRAY_SLOT_CHECK_FILE = Path("scripts/zigux/check-phase3-xarray-slot-starter-packet.py")
SHARED_TESTS_BUILD_FILE = Path("zigux/tests/build.zig")
SHARED_VALIDATOR_FILE = Path("scripts/zigux/validate-phase3.py")
ABI_CHECK_FILE = Path("scripts/zigux/check-phase3-abi.py")
ABI_SUPPORT_PACKET_FILE = Path("scripts/zigux/check-phase3-abi-support-packet.py")
ABI_REPLAY_FILE = Path("zigux/tests/phase3_abi.zig")
ABI_DUMP_REPLAY_FILE = Path("zigux/tests/phase3_abi_dump_current.zig")
CATALOG_TOOL_FILE = Path("scripts/zigux/phase3_catalog.py")
CATALOG_SELFTEST_CHECK_FILE = Path("scripts/zigux/check-phase3-catalog-selftest.py")
GENERATED_WRAPPER_FILE = Path("scripts/zigux/generate-phase3-check-wrappers.py")
WRAPPER_TEMPLATE_CHECK_FILE = Path("scripts/zigux/check-phase3-wrapper-templates.py")
FIXTURE_MANIFEST_FILE = Path("zigux/tests/fixtures/phase3_abi_manifest.json")
HEADER_FAMILY_VALIDATOR_FILE = Path(
    "scripts/zigux/validate-phase3-abi-header-family-survey.py"
)
HEADER_FAMILY_NOTE_FILE = Path(
    "Documentation/zigux/phase3-abi-header-family-survey.md"
)
HEADER_FAMILY_NEXT_STEP_NOTE_FILE = Path(
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md"
)
HEADER_GOVERNANCE_VALIDATOR_FILE = Path(
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py"
)
EXPORT_UAPI_SURVEY_NOTE_FILE = Path(
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md"
)
EXPORT_UAPI_SURVEY_VALIDATOR_FILE = Path(
    "scripts/zigux/validate-phase3-export-uapi-survey.py"
)
POLICY_DUMP_CHECK_FILE = Path("scripts/zigux/check-phase3-policy-dump.py")
POLICY_UNSAFE_SURVEY_VALIDATOR_FILE = Path(
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py"
)
XARRAY_SLOT_NOTE_FILE = Path("Documentation/zigux/phase3-xarray-slot-slice.md")
POLICY_UNSAFE_SURVEY_NOTE_FILE = Path(
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
)

RUNNER_MARKER = "scripts/zigux/run-phase3-checks.py"
SHARED_TESTS_ROUTES_MARKER = "scripts/zigux/check-phase3-shared-tests-routes.py"
ABI_MANIFEST_REPLAY_ROUTES_MARKER = (
    "scripts/zigux/check-phase3-abi-manifest-replay-routes.py"
)
ABI_MANIFEST_REPLAY_ROUTES_SELFTEST_MARKER = (
    "python3 scripts/zigux/check-phase3-abi-manifest-replay-routes.py --self-test"
)
HEADER_MARKER = "include/linux/zigux.h"
UAPI_MARKER = "zigux/uapi/dev_t.zig"
NOTIFIER_BINDING_MARKER = "zigux/bindings/notifier_abi.zig"
VALIDATOR_SUPPORT_NOTE_MARKER = "Documentation/zigux/phase3-validator-support-surface.md"
SELFTEST_SURFACE_MARKER = "scripts/zigux/check-phase3-selftest-surface.py"
XARRAY_SLOT_NOTE_MARKER = "Documentation/zigux/phase3-xarray-slot-slice.md"
POLICY_UNSAFE_SURVEY_NOTE_MARKER = (
    "Documentation/zigux/phase3-policy-unsafe-boundary-survey.md"
)
XARRAY_SLOT_CHECK_MARKER = "scripts/zigux/check-phase3-xarray-slot-starter-packet.py"
POLICY_DUMP_CHECK_MARKER = "scripts/zigux/check-phase3-policy-dump.py"
POLICY_UNSAFE_SURVEY_VALIDATOR_MARKER = (
    "scripts/zigux/validate-phase3-policy-unsafe-survey.py"
)
MMIO_HELPER_MARKER = "zigux/helpers/mmio.zig"
LOW_LEVEL_WRAPPER_SURVEY_VALIDATOR_MARKER = (
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py"
)
LOW_LEVEL_WRAPPER_SURVEY_SELFTEST_MARKER = (
    "python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test"
)
LOW_LEVEL_WRAPPER_REPLAY_MARKER = "zigux/tests/phase3_low_level_wrappers.zig"
LOW_LEVEL_WRAPPER_BUILD_MARKER = "zigux/tests/phase3_low_level_wrappers_build.zig"
EXPORT_UAPI_LAYOUT_REPLAY_MARKER = "zigux/tests/phase3_export_uapi_layout.zig"
EXPORT_UAPI_LAYOUT_BUILD_MARKER = "zigux/tests/phase3_export_uapi_layout_build.zig"
EXPORT_UAPI_LAYOUT_BUILD_ROUTE_MARKER = (
    "zig build phase3-export-uapi-layout-test --build-file "
    "zigux/tests/phase3_export_uapi_layout_build.zig"
)
EXPORT_UAPI_C_HEADER_SMOKE_CHECK_MARKER = (
    "scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"
)
EXPORT_UAPI_C_HEADER_SMOKE_ROUTE_MARKER = (
    "python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py"
)
EXPORT_UAPI_C_HEADER_SMOKE_REPLAY_MARKER = (
    "zigux/tests/phase3_export_uapi_c_header_smoke.c"
)
WORKFLOW_MARKER = ".github/workflows/zigux-bootstrap.yml"
EXPORT_UAPI_SURVEY_NOTE_MARKER = "Documentation/zigux/phase3-export-uapi-boundary-survey.md"
EXPORT_UAPI_SURVEY_VALIDATOR_MARKER = "scripts/zigux/validate-phase3-export-uapi-survey.py"
HEADER_GOVERNANCE_VALIDATOR_MARKER = (
    "scripts/zigux/validate-phase3-linux-zigux-header-governance.py"
)
HEADER_GOVERNANCE_VALIDATOR_SELFTEST_MARKER = (
    "python3 scripts/zigux/validate-phase3-linux-zigux-header-governance.py --self-test"
)
CATALOG_SELFTEST_GAP_MARKER = "scripts/zigux/check-phase3-catalog-selftest.py"
CATALOG_TOOL_MARKER = "scripts/zigux/phase3_catalog.py"
WRAPPER_GENERATION_GAP_MARKER = "scripts/zigux/generate-phase3-check-wrappers.py"
WRAPPER_TEMPLATE_CHECK_MARKER = "scripts/zigux/check-phase3-wrapper-templates.py"
WRAPPER_TEMPLATE_CHECK_SELFTEST_MARKER = (
    "python3 scripts/zigux/check-phase3-wrapper-templates.py --self-test"
)
SHARED_VALIDATOR_MARKER = "scripts/zigux/validate-phase3.py"
ABI_CHECK_MARKER = "scripts/zigux/check-phase3-abi.py"
ABI_SUPPORT_PACKET_MARKER = "scripts/zigux/check-phase3-abi-support-packet.py"
FIXTURE_MANIFEST_MARKER = "zigux/tests/fixtures/phase3_abi_manifest.json"
XARRAY_SLOT_HELPER_MARKER = "zigux/helpers/xarray_slot_view.zig"
XARRAY_SLOT_STARTER_MARKER = "zigux/tests/phase3_xarray_slot_starter_packet.zig"
XARRAY_SLOT_STARTER_BUILD_MARKER = "zigux/tests/phase3_xarray_slot_starter_packet_build.zig"
SHARED_TESTS_BUILD_MARKER = "zigux/tests/build.zig"
XARRAY_SLOT_BUILD_ROUTE_MARKER = (
    "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig"
)
POLICY_DUMP_REPLAY_MARKER = "zigux/tests/phase3_policy_dump.zig"
POLICY_DUMP_BUILD_MARKER = "zigux/tests/phase3_policy_dump_build.zig"
POLICY_DUMP_BUILD_ROUTE_MARKER = (
    "zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig"
)
HEADER_FAMILY_VALIDATOR_GAP_MARKER = (
    "scripts/zigux/validate-phase3-abi-header-family-survey.py"
)
HEADER_FAMILY_NOTE_GAP_MARKER = (
    "Documentation/zigux/phase3-abi-header-family-survey.md"
)
HEADER_FAMILY_NEXT_STEP_GAP_MARKER = (
    "Documentation/zigux/phase3-abi-h-boundary-next-step.md"
)
HEADER_FAMILY_RETURNED_SURFACES_MARKER = (
    "`scripts/zigux/validate-phase3-abi-header-family-survey.py` and "
    "`Documentation/zigux/phase3-abi-header-family-survey.md` are directly readable on current "
    "`master`, so keep the bounded header-family survey follow-through explicit beside the "
    "export/UAPI layout replay and shared ABI inventory instead of leaving those two surfaces "
    "in repo-reality-gap wording"
)
HEADER_FAMILY_NEXT_STEP_REMINDER_MARKER = (
    "`Documentation/zigux/phase3-abi-h-boundary-next-step.md` is directly readable on current "
    "`master`, so keep that focused abi.h next-step follow-through explicit beside the bounded "
    "header-family survey, the shared ABI inventory, and the export/UAPI layout replay instead "
    "of leaving it in repo-reality-gap wording"
)

REQUIRED_FILES = (
    Path("Documentation/zigux/phase3-abi-slice.md"),
    Path("Documentation/zigux/phase3-errptr-xarray-slice.md"),
    XARRAY_SLOT_NOTE_FILE,
    Path("Documentation/zigux/phase3-policy-slice.md"),
    POLICY_UNSAFE_SURVEY_NOTE_FILE,
    Path("Documentation/zigux/phase3-validator-support-surface.md"),
    Path("Documentation/zigux/phase3-boundary-lane-sequencing.md"),
    Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
    EXPORT_UAPI_SURVEY_NOTE_FILE,
    Path("include/linux/zigux.h"),
    Path("include/zigux/dev_t.h"),
    Path("include/zigux/abi.h"),
    Path("scripts/zigux/check-phase3-selftest-surface.py"),
    SHARED_TESTS_ROUTES_FILE,
    ABI_MANIFEST_REPLAY_ROUTES_FILE,
    Path("scripts/zigux/validate-phase3-validator-support-surface.py"),
    Path("scripts/zigux/validate_phase3_selftest.py"),
    RUNNER_FILE,
    SHARED_VALIDATOR_FILE,
    ABI_CHECK_FILE,
    ABI_SUPPORT_PACKET_FILE,
    CATALOG_TOOL_FILE,
    CATALOG_SELFTEST_CHECK_FILE,
    GENERATED_WRAPPER_FILE,
    WRAPPER_TEMPLATE_CHECK_FILE,
    FIXTURE_MANIFEST_FILE,
    HEADER_FAMILY_VALIDATOR_FILE,
    HEADER_FAMILY_NOTE_FILE,
    HEADER_FAMILY_NEXT_STEP_NOTE_FILE,
    HEADER_GOVERNANCE_VALIDATOR_FILE,
    Path("scripts/zigux/check-phase3-dev-t-starter-packet.py"),
    Path("scripts/zigux/check-phase3-errptr-xarray-starter-packet.py"),
    XARRAY_SLOT_CHECK_FILE,
    Path("scripts/zigux/check-phase3-policy-starter-packet.py"),
    POLICY_DUMP_CHECK_FILE,
    LOW_LEVEL_WRAPPER_SURVEY_VALIDATOR_FILE,
    EXPORT_UAPI_SURVEY_VALIDATOR_FILE,
    EXPORT_UAPI_C_HEADER_SMOKE_CHECK_FILE,
    POLICY_UNSAFE_SURVEY_VALIDATOR_FILE,
    BINDING_FILE,
    Path("zigux/bindings/version.zig"),
    Path("zigux/bindings/abi.zig"),
    NOTIFIER_BINDING_FILE,
    Path("zigux/helpers/err_ptr.zig"),
    Path("zigux/helpers/xa_value.zig"),
    XARRAY_SLOT_HELPER_FILE,
    Path("zigux/helpers/panic_policy.zig"),
    Path("zigux/helpers/allocator_policy.zig"),
    Path("zigux/helpers/unsafe_policy.zig"),
    Path("zigux/helpers/atomic.zig"),
    Path("zigux/helpers/barrier.zig"),
    Path("zigux/helpers/mmio.zig"),
    NARROW_UNSAFE_FILE,
    Path("zigux/kernel/export_shim.zig"),
    UAPI_FILE,
    Path("zigux/uapi/version.zig"),
    Path("zigux/tests/phase3_dev_t_starter_packet.zig"),
    Path("zigux/tests/phase3_dev_t_starter_packet_build.zig"),
    Path("zigux/tests/phase3_errptr_xarray_starter_packet.zig"),
    Path("zigux/tests/phase3_errptr_xarray_starter_packet_build.zig"),
    XARRAY_SLOT_STARTER_FILE,
    XARRAY_SLOT_STARTER_BUILD_FILE,
    SHARED_TESTS_BUILD_FILE,
    ABI_REPLAY_FILE,
    ABI_DUMP_REPLAY_FILE,
    Path("zigux/tests/phase3_policy_starter_packet.zig"),
    POLICY_STARTER_BUILD_FILE,
    POLICY_DUMP_REPLAY_FILE,
    POLICY_DUMP_BUILD_FILE,
    LOW_LEVEL_WRAPPER_REPLAY_FILE,
    LOW_LEVEL_WRAPPER_BUILD_FILE,
    EXPORT_UAPI_LAYOUT_REPLAY_FILE,
    EXPORT_UAPI_LAYOUT_BUILD_FILE,
    EXPORT_UAPI_C_HEADER_SMOKE_REPLAY_FILE,
    WORKFLOW_FILE,
)

REQUIRED_MARKERS = (
    "Documentation/zigux/phase3-abi-slice.md",
    "Documentation/zigux/phase3-errptr-xarray-slice.md",
    XARRAY_SLOT_NOTE_MARKER,
    "Documentation/zigux/phase3-policy-slice.md",
    POLICY_UNSAFE_SURVEY_NOTE_MARKER,
    "Documentation/zigux/phase3-validator-support-surface.md",
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py --self-test",
    "python3 scripts/zigux/check-phase3-readme-tooling-inventory.py",
    "scripts/zigux/check-phase3-selftest-surface.py",
    ABI_MANIFEST_REPLAY_ROUTES_SELFTEST_MARKER,
    ABI_MANIFEST_REPLAY_ROUTES_MARKER,
    "scripts/zigux/check-phase3-shared-tests-routes.py",
    "scripts/zigux/validate-phase3-validator-support-surface.py",
    "scripts/zigux/validate-phase3-export-uapi-survey.py",
    EXPORT_UAPI_C_HEADER_SMOKE_CHECK_MARKER,
    EXPORT_UAPI_C_HEADER_SMOKE_ROUTE_MARKER,
    EXPORT_UAPI_C_HEADER_SMOKE_REPLAY_MARKER,
    POLICY_UNSAFE_SURVEY_VALIDATOR_MARKER,
    HEADER_GOVERNANCE_VALIDATOR_SELFTEST_MARKER,
    HEADER_GOVERNANCE_VALIDATOR_MARKER,
    "scripts/zigux/validate_phase3_selftest.py",
    "scripts/zigux/run-phase3-checks.py",
    "scripts/zigux/validate-phase3.py",
    ABI_CHECK_MARKER,
    ABI_SUPPORT_PACKET_MARKER,
    "scripts/zigux/phase3_catalog.py",
    "scripts/zigux/check-phase3-catalog-selftest.py",
    WRAPPER_TEMPLATE_CHECK_SELFTEST_MARKER,
    WRAPPER_TEMPLATE_CHECK_MARKER,
    "scripts/zigux/check-phase3-dev-t-starter-packet.py",
    "scripts/zigux/check-phase3-errptr-xarray-starter-packet.py",
    XARRAY_SLOT_CHECK_MARKER,
    "scripts/zigux/check-phase3-policy-starter-packet.py",
    POLICY_DUMP_CHECK_MARKER,
    "scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "Documentation/zigux/phase3-boundary-lane-sequencing.md",
    "Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md",
    "Documentation/zigux/phase3-export-uapi-boundary-survey.md",
    "include/linux/zigux.h",
    "include/zigux/dev_t.h",
    "include/zigux/abi.h",
    "zigux/helpers/err_ptr.zig",
    "zigux/helpers/xa_value.zig",
    "zigux/helpers/xarray_slot_view.zig",
    "zigux/helpers/panic_policy.zig",
    "zigux/helpers/allocator_policy.zig",
    "zigux/helpers/unsafe_policy.zig",
    "zigux/helpers/atomic.zig",
    "zigux/helpers/barrier.zig",
    "zigux/helpers/mmio.zig",
    "zigux/kernel/export_shim.zig",
    "zigux/bindings/dev_t.zig",
    "zigux/bindings/version.zig",
    "zigux/bindings/abi.zig",
    "zigux/bindings/notifier_abi.zig",
    "zigux/unsafe/narrow.zig",
    "zigux/uapi/dev_t.zig",
    "zigux/uapi/version.zig",
    "zigux/tests/fixtures/phase3_abi_manifest.json",
    "zigux/tests/phase3_dev_t_starter_packet.zig",
    "zigux/tests/phase3_dev_t_starter_packet_build.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet.zig",
    "zigux/tests/phase3_errptr_xarray_starter_packet_build.zig",
    "zigux/tests/phase3_xarray_slot_starter_packet.zig",
    XARRAY_SLOT_STARTER_BUILD_MARKER,
    "zigux/tests/build.zig",
    "zig build phase3-xarray-slot-starter-packet --build-file zigux/tests/build.zig",
    "zigux/tests/phase3_policy_starter_packet.zig",
    "zigux/tests/phase3_policy_starter_packet_build.zig",
    POLICY_DUMP_REPLAY_MARKER,
    POLICY_DUMP_BUILD_MARKER,
    POLICY_DUMP_BUILD_ROUTE_MARKER,
    "zigux/tests/phase3_low_level_wrappers.zig",
    "zigux/tests/phase3_low_level_wrappers_build.zig",
    "zigux/tests/phase3_export_uapi_layout.zig",
    "zigux/tests/phase3_export_uapi_layout_build.zig",
    "zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    ".github/workflows/zigux-bootstrap.yml",
    LOW_LEVEL_WRAPPER_SURVEY_SELFTEST_MARKER,
    CATALOG_SELFTEST_GAP_MARKER,
    WRAPPER_GENERATION_GAP_MARKER,
    WRAPPER_TEMPLATE_CHECK_MARKER,
    SHARED_VALIDATOR_MARKER,
    FIXTURE_MANIFEST_MARKER,
    HEADER_FAMILY_VALIDATOR_GAP_MARKER,
    HEADER_FAMILY_NOTE_GAP_MARKER,
    HEADER_FAMILY_NEXT_STEP_GAP_MARKER,
    HEADER_FAMILY_RETURNED_SURFACES_MARKER,
    HEADER_FAMILY_NEXT_STEP_REMINDER_MARKER,
)

README_MARKER_CASES = (
    (RUNNER_MARKER, "expected missing runner README marker was not reported"),
    (
        SHARED_TESTS_ROUTES_MARKER,
        "expected missing shared-tests-routes README marker was not reported",
    ),
    (
        ABI_MANIFEST_REPLAY_ROUTES_SELFTEST_MARKER,
        "expected missing manifest-replay self-test README marker was not reported",
    ),
    (
        ABI_MANIFEST_REPLAY_ROUTES_MARKER,
        "expected missing manifest-replay README marker was not reported",
    ),
    (HEADER_MARKER, "expected missing header README marker was not reported"),
    (UAPI_MARKER, "expected missing UAPI README marker was not reported"),
    (
        NOTIFIER_BINDING_MARKER,
        "expected missing notifier-binding README marker was not reported",
    ),
    (
        VALIDATOR_SUPPORT_NOTE_MARKER,
        "expected missing validator-support note README marker was not reported",
    ),
    (
        SELFTEST_SURFACE_MARKER,
        "expected missing selftest-surface README marker was not reported",
    ),
    (
        XARRAY_SLOT_NOTE_MARKER,
        "expected missing xarray-slot note README marker was not reported",
    ),
    (
        POLICY_UNSAFE_SURVEY_NOTE_MARKER,
        "expected missing policy-unsafe survey note README marker was not reported",
    ),
    (
        XARRAY_SLOT_CHECK_MARKER,
        "expected missing xarray-slot checker README marker was not reported",
    ),
    (
        POLICY_DUMP_CHECK_MARKER,
        "expected missing policy-dump checker README marker was not reported",
    ),
    (
        POLICY_UNSAFE_SURVEY_VALIDATOR_MARKER,
        "expected missing policy-unsafe validator README marker was not reported",
    ),
    (
        HEADER_GOVERNANCE_VALIDATOR_SELFTEST_MARKER,
        "expected missing header-governance self-test README marker was not reported",
    ),
    (
        HEADER_GOVERNANCE_VALIDATOR_MARKER,
        "expected missing header-governance validator README marker was not reported",
    ),
    (
        EXPORT_UAPI_C_HEADER_SMOKE_CHECK_MARKER,
        "expected missing export-uapi c-header smoke checker README marker was not reported",
    ),
    (
        EXPORT_UAPI_C_HEADER_SMOKE_ROUTE_MARKER,
        "expected missing export-uapi c-header smoke route README marker was not reported",
    ),
    (
        EXPORT_UAPI_C_HEADER_SMOKE_REPLAY_MARKER,
        "expected missing export-uapi c-header smoke replay README marker was not reported",
    ),
    (MMIO_HELPER_MARKER, "expected missing MMIO helper README marker was not reported"),
    (
        LOW_LEVEL_WRAPPER_SURVEY_VALIDATOR_MARKER,
        "expected missing low-level-wrapper survey validator README marker was not reported",
    ),
    (
        LOW_LEVEL_WRAPPER_SURVEY_SELFTEST_MARKER,
        "expected missing low-level-wrapper survey self-test README marker was not reported",
    ),
    (
        LOW_LEVEL_WRAPPER_REPLAY_MARKER,
        "expected missing low-level-wrapper replay README marker was not reported",
    ),
    (
        LOW_LEVEL_WRAPPER_BUILD_MARKER,
        "expected missing low-level-wrapper build README marker was not reported",
    ),
    (
        EXPORT_UAPI_LAYOUT_REPLAY_MARKER,
        "expected missing export-uapi-layout replay README marker was not reported",
    ),
    (
        EXPORT_UAPI_LAYOUT_BUILD_MARKER,
        "expected missing export-uapi-layout build README marker was not reported",
    ),
    (
        EXPORT_UAPI_LAYOUT_BUILD_ROUTE_MARKER,
        "expected missing export-uapi-layout build-route README marker was not reported",
    ),
    (WORKFLOW_MARKER, "expected missing workflow README marker was not reported"),
    (
        EXPORT_UAPI_SURVEY_NOTE_MARKER,
        "expected missing export-uapi survey note README marker was not reported",
    ),
    (
        EXPORT_UAPI_SURVEY_VALIDATOR_MARKER,
        "expected missing export-uapi survey validator README marker was not reported",
    ),
    (
        CATALOG_SELFTEST_GAP_MARKER,
        "expected missing catalog-selftest guard README marker was not reported",
    ),
    (CATALOG_TOOL_MARKER, "expected missing catalog tool README marker was not reported"),
    (
        WRAPPER_GENERATION_GAP_MARKER,
        "expected missing wrapper-generation gap README marker was not reported",
    ),
    (
        WRAPPER_TEMPLATE_CHECK_SELFTEST_MARKER,
        "expected missing wrapper-template self-test README marker was not reported",
    ),
    (
        WRAPPER_TEMPLATE_CHECK_MARKER,
        "expected missing wrapper-template checker README marker was not reported",
    ),
    (
        SHARED_VALIDATOR_MARKER,
        "expected missing shared validator README marker was not reported",
    ),
    (
        ABI_CHECK_MARKER,
        "expected missing shared ABI checker README marker was not reported",
    ),
    (
        ABI_SUPPORT_PACKET_MARKER,
        "expected missing shared ABI support-packet README marker was not reported",
    ),
    (
        FIXTURE_MANIFEST_MARKER,
        "expected missing fixture-manifest README marker was not reported",
    ),
    (
        XARRAY_SLOT_HELPER_MARKER,
        "expected missing xarray-slot helper README marker was not reported",
    ),
    (
        XARRAY_SLOT_STARTER_MARKER,
        "expected missing xarray-slot starter README marker was not reported",
    ),
    (
        XARRAY_SLOT_STARTER_BUILD_MARKER,
        "expected missing xarray-slot starter build README marker was not reported",
    ),
    (
        SHARED_TESTS_BUILD_MARKER,
        "expected missing shared tests build README marker was not reported",
    ),
    (
        XARRAY_SLOT_BUILD_ROUTE_MARKER,
        "expected missing xarray-slot build-route README marker was not reported",
    ),
    (
        POLICY_DUMP_REPLAY_MARKER,
        "expected missing policy-dump replay README marker was not reported",
    ),
    (
        POLICY_DUMP_BUILD_MARKER,
        "expected missing policy-dump build README marker was not reported",
    ),
    (
        POLICY_DUMP_BUILD_ROUTE_MARKER,
        "expected missing policy-dump build-route README marker was not reported",
    ),
    (
        HEADER_FAMILY_VALIDATOR_GAP_MARKER,
        "expected missing header-family validator gap README marker was not reported",
    ),
    (
        HEADER_FAMILY_NOTE_GAP_MARKER,
        "expected missing header-family note gap README marker was not reported",
    ),
    (
        HEADER_FAMILY_NEXT_STEP_GAP_MARKER,
        "expected missing header-family next-step gap README marker was not reported",
    ),
    (
        HEADER_FAMILY_RETURNED_SURFACES_MARKER,
        "expected missing header-family returned-surfaces README marker was not reported",
    ),
    (
        HEADER_FAMILY_NEXT_STEP_REMINDER_MARKER,
        "expected missing header-family next-step reminder README marker was not reported",
    ),
)

FILE_CASES = (
    (RUNNER_FILE, "expected missing runner file was not reported"),
    (
        SHARED_TESTS_ROUTES_FILE,
        "expected missing shared-tests-routes file was not reported",
    ),
    (
        ABI_MANIFEST_REPLAY_ROUTES_FILE,
        "expected missing manifest-replay-routes file was not reported",
    ),
    (BINDING_FILE, "expected missing binding file was not reported"),
    (
        NOTIFIER_BINDING_FILE,
        "expected missing notifier-binding file was not reported",
    ),
    (NARROW_UNSAFE_FILE, "expected missing narrow-unsafe file was not reported"),
    (UAPI_FILE, "expected missing UAPI file was not reported"),
    (CATALOG_TOOL_FILE, "expected missing catalog tool file was not reported"),
    (
        CATALOG_SELFTEST_CHECK_FILE,
        "expected missing catalog-selftest guard file was not reported",
    ),
    (
        GENERATED_WRAPPER_FILE,
        "expected missing generated-wrapper file was not reported",
    ),
    (
        WRAPPER_TEMPLATE_CHECK_FILE,
        "expected missing wrapper-template checker file was not reported",
    ),
    (FIXTURE_MANIFEST_FILE, "expected missing fixture manifest file was not reported"),
    (
        HEADER_FAMILY_VALIDATOR_FILE,
        "expected missing header-family validator file was not reported",
    ),
    (
        HEADER_FAMILY_NOTE_FILE,
        "expected missing header-family survey note was not reported",
    ),
    (
        HEADER_FAMILY_NEXT_STEP_NOTE_FILE,
        "expected missing header-family next-step note was not reported",
    ),
    (
        HEADER_GOVERNANCE_VALIDATOR_FILE,
        "expected missing header-governance validator file was not reported",
    ),
    (
        LOW_LEVEL_WRAPPER_SURVEY_VALIDATOR_FILE,
        "expected missing low-level-wrapper survey validator file was not reported",
    ),
    (
        LOW_LEVEL_WRAPPER_REPLAY_FILE,
        "expected missing low-level-wrapper replay file was not reported",
    ),
    (
        LOW_LEVEL_WRAPPER_BUILD_FILE,
        "expected missing low-level-wrapper build file was not reported",
    ),
    (
        EXPORT_UAPI_LAYOUT_REPLAY_FILE,
        "expected missing export-uapi-layout replay file was not reported",
    ),
    (
        EXPORT_UAPI_LAYOUT_BUILD_FILE,
        "expected missing export-uapi-layout build file was not reported",
    ),
    (
        EXPORT_UAPI_C_HEADER_SMOKE_CHECK_FILE,
        "expected missing export-uapi c-header smoke checker file was not reported",
    ),
    (
        EXPORT_UAPI_C_HEADER_SMOKE_REPLAY_FILE,
        "expected missing export-uapi c-header smoke replay file was not reported",
    ),
    (WORKFLOW_FILE, "expected missing workflow file was not reported"),
    (
        EXPORT_UAPI_SURVEY_NOTE_FILE,
        "expected missing export-uapi survey note file was not reported",
    ),
    (
        EXPORT_UAPI_SURVEY_VALIDATOR_FILE,
        "expected missing export-uapi survey validator file was not reported",
    ),
    (
        POLICY_STARTER_BUILD_FILE,
        "expected missing starter build file was not reported",
    ),
    (POLICY_DUMP_REPLAY_FILE, "expected missing policy-dump replay file was not reported"),
    (POLICY_DUMP_BUILD_FILE, "expected missing policy-dump build file was not reported"),
    (
        XARRAY_SLOT_HELPER_FILE,
        "expected missing xarray-slot helper file was not reported",
    ),
    (
        XARRAY_SLOT_STARTER_FILE,
        "expected missing xarray-slot starter file was not reported",
    ),
    (
        XARRAY_SLOT_STARTER_BUILD_FILE,
        "expected missing xarray-slot starter build file was not reported",
    ),
    (
        XARRAY_SLOT_CHECK_FILE,
        "expected missing xarray-slot checker file was not reported",
    ),
    (
        SHARED_TESTS_BUILD_FILE,
        "expected missing shared tests build file was not reported",
    ),
    (ABI_REPLAY_FILE, "expected missing shared ABI replay file was not reported"),
    (ABI_DUMP_REPLAY_FILE, "expected missing shared ABI dump replay file was not reported"),
    (SHARED_VALIDATOR_FILE, "expected missing shared validator file was not reported"),
    (ABI_CHECK_FILE, "expected missing shared ABI checker file was not reported"),
    (ABI_SUPPORT_PACKET_FILE, "expected missing shared ABI support-packet file was not reported"),
    (
        Path("Documentation/zigux/phase3-policy-slice.md"),
        "expected missing policy-slice file was not reported",
    ),
    (
        XARRAY_SLOT_NOTE_FILE,
        "expected missing xarray-slot note file was not reported",
    ),
    (
        POLICY_UNSAFE_SURVEY_NOTE_FILE,
        "expected missing policy-unsafe survey note was not reported",
    ),
    (
        Path("Documentation/zigux/phase3-low-level-wrapper-boundary-survey.md"),
        "expected missing low-level-wrapper survey note was not reported",
    ),
    (Path("include/zigux/abi.h"), "expected missing ABI header file was not reported"),
    (
        POLICY_DUMP_CHECK_FILE,
        "expected missing policy-dump checker file was not reported",
    ),
    (
        POLICY_UNSAFE_SURVEY_VALIDATOR_FILE,
        "expected missing policy-unsafe survey validator file was not reported",
    ),
    (
        Path("zigux/helpers/unsafe_policy.zig"),
        "expected missing unsafe-policy helper file was not reported",
    ),
    (
        Path("zigux/helpers/atomic.zig"),
        "expected missing atomic helper file was not reported",
    ),
    (
        Path("zigux/helpers/barrier.zig"),
        "expected missing barrier helper file was not reported",
    ),
    (
        Path("zigux/helpers/mmio.zig"),
        "expected missing MMIO helper file was not reported",
    ),
    (
        Path("zigux/kernel/export_shim.zig"),
        "expected missing export-shim file was not reported",
    ),
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_repo(repo_root: Path) -> list[str]:
    issues: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).is_file():
            issues.append(f"missing repo file: {rel_path.as_posix()}")

    readme_path = repo_root / SCRIPTS_README_PATH
    try:
        readme_text = _read(readme_path)
    except FileNotFoundError:
        return issues + [f"missing repo file: {SCRIPTS_README_PATH.as_posix()}"]

    for marker in REQUIRED_MARKERS:
        if marker not in readme_text:
            issues.append(f"missing scripts README marker: {marker}")
    return issues


def _populate_repo(root: Path) -> None:
    for rel_path in REQUIRED_FILES:
        _write(root / rel_path, rel_path.as_posix() + "\n")
    _write(root / SCRIPTS_README_PATH, "\n".join(REQUIRED_MARKERS) + "\n")


def _expect_missing_marker(root: Path, marker: str, message: str) -> int:
    readme = root / SCRIPTS_README_PATH
    readme.write_text(_read(readme).replace(marker, ""), encoding="utf-8")
    issues = validate_repo(root)
    expected = f"missing scripts README marker: {marker}"
    if expected not in issues:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def _expect_missing_file(root: Path, rel_path: Path, message: str) -> int:
    (root / rel_path).unlink()
    issues = validate_repo(root)
    expected = f"missing repo file: {rel_path.as_posix()}"
    if expected not in issues:
        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
        print(message)
        return 1
    return 0


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="zigux_phase3_readme_tooling_inventory_") as temp_dir:
        root = Path(temp_dir)
        _populate_repo(root)

        issues = validate_repo(root)
        if issues:
            print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=fail")
            print("\n".join(issues))
            return 1

        for marker, message in README_MARKER_CASES:
            _populate_repo(root)
            if _expect_missing_marker(root, marker, message) != 0:
                return 1

        for rel_path, message in FILE_CASES:
            _populate_repo(root)
            if _expect_missing_file(root, rel_path, message) != 0:
                return 1

        print("PHASE3_README_TOOLING_INVENTORY_SELF_TEST=pass")
        print(
            "PHASE3_README_TOOLING_INVENTORY_SELF_TEST_CASE_COUNT="
            f"{1 + len(README_MARKER_CASES) + len(FILE_CASES)}"
        )
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 3 scripts-root tooling inventory."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root that contains scripts/zigux/README.md",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_repo(args.repo_root)
    if issues:
        print("PHASE3_README_TOOLING_INVENTORY=fail")
        print("\n".join(issues))
        return 1

    print(f"validated {args.repo_root / SCRIPTS_README_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
