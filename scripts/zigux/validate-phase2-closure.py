#!/usr/bin/env python3
"""Validate the current Phase 2 closure note against the shipped closure packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

WORKFLOW_REL = Path(".github/workflows/zigux-bootstrap.yml")
PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
PHASE2_BOOTSTRAP_NOTES_REL = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")
PHASE2_GENKSYMS_SURVEY_REL = Path("Documentation/zigux/phase2-genksyms-dual-implementation-survey.md")
PHASE2_VALIDATE_REL = Path("scripts/zigux/validate-phase2.py")
PHASE2_CLOSURE_VALIDATE_REL = Path("scripts/zigux/validate-phase2-closure.py")
LOCAL_ARCHIVE_WORKFLOW_CHECKER_REL = Path("scripts/zigux/check-lane05-local-first-archive-workflow.py")
LOCAL_ARCHIVE_README_CHECKER_REL = Path("scripts/zigux/check-lane05-local-archive-readme.py")
INSTALL_ZIG_ARCHIVE_VERIFICATION_CHECKER_REL = Path("scripts/zigux/check-lane05-install-zig-archive-verification.py")
STAGE_HELPER_CONTRACT_CHECKER_REL = Path("scripts/zigux/check-lane05-stage-helper-contract.py")
STAGE_HELPER_SELFTEST_CHECKER_REL = Path("scripts/zigux/check-lane05-stage-helper-selftest.py")
INSTALL_ZIG_REL = Path("scripts/zigux/install-zig.py")
STAGE_PINNED_ARCHIVE_REL = Path("scripts/zigux/stage-pinned-zig-archive.py")
TOOLCHAIN_CHECKER_REL = Path("scripts/zigux/check-zig-toolchain.py")
PINNING_CHECKER_REL = Path("scripts/zigux/check-phase2-toolchain-pinning.py")
PIN_SCOPE_CHECKER_REL = Path("scripts/zigux/check-phase2-toolchain-pin-scope.py")
KBUILD_CHECKER_REL = Path("scripts/zigux/check-phase2-kbuild-routes.py")
KCONFIG_BRIDGE_CHECKER_REL = Path("scripts/zigux/check-kconfig-bridge.py")
KCONFIG_ALIGNMENT_REL = Path("scripts/zigux/check-phase2-kconfig-selftest-alignment.py")
KCONFIG_ALLCONFIG_HELPER_PACKET_REL = Path("scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py")
GENKSYMS_ALIGNMENT_REL = Path("scripts/zigux/check-phase2-genksyms-selftest-alignment.py")
TESTS_ALIGNMENT_REL = Path("scripts/zigux/check-phase2-tests-readme-alignment.py")
CROSS_CHECKER_REL = Path("scripts/zigux/check-phase2-cross.py")
CROSS_ALIGNMENT_REL = Path("scripts/zigux/check-phase2-cross-selftest-alignment.py")
DOCS_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase2-docs-shared-reminder.py")
REQUIRED_ROUTES_CHECKER_REL = Path("scripts/zigux/check-phase2-required-make-routes.py")
TOOL_MANIFEST_CHECKER_REL = Path("scripts/zigux/check-phase2-tool-manifest.py")
ARTIFACT_MANIFEST_CHECKER_REL = Path("scripts/zigux/check-phase2-artifact-tools-manifest.py")
GENKSYMS_CHECKER_REL = Path("scripts/zigux/check-genksyms-bridge.py")
FIXDEP_GATE_REL = Path("scripts/zigux/check-phase2-fixdep-gate.py")
FIXDEP_DIFF_REL = Path("scripts/zigux/check-fixdep-diff.py")
TOOLCHAIN_POLICY_REL = Path("scripts/zigux/zig-toolchain-policy.json")
CONF_BRIDGE_REL = Path("scripts/zigux/kconfig/conf_bridge.zig")
CONFDATA_BRIDGE_REL = Path("scripts/zigux/kconfig/confdata_bridge.zig")
GENKSYMS_BRIDGE_REL = Path("scripts/zigux/genksyms.zig")
GENKSYMS_VERSION_PROOF_REL = Path("scripts/zigux/genksyms_version_before_invalid_long_option_test.zig")
GENKSYMS_AMBIGUOUS_VERSION_PROOF_REL = Path(
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig"
)
FIXDEP_BRIDGE_REL = Path("scripts/zigux/fixdep.zig")
MAKEFILE_REL = Path("zigux/Makefile")
MANIFEST_REL = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
ARTIFACT_MANIFEST_REL = Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json")
CROSS_FIXTURE_REL = Path("zigux/tests/fixtures/phase2_cross_targets.json")
FIXDEP_CASES_REL = Path("zigux/tests/fixtures/fixdep/cases.json")
CONF_MANIFEST_REL = Path("zigux/tests/fixtures/kconfig_bridge/conf_manifest.json")
CONFDATA_MANIFEST_REL = Path("zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json")
KCONFIG_CASES_REL = Path("zigux/tests/fixtures/kconfig_bridge/cases.json")
GENKSYMS_CASES_REL = Path("zigux/tests/fixtures/genksyms_bridge/cases.json")
GENKSYMS_HELP_REL = Path("zigux/tests/fixtures/genksyms_bridge/help_expected.json")
GENKSYMS_MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")
GENKSYMS_MINIMAL_REL = Path("zigux/tests/fixtures/genksyms_bridge/minimal_expected.json")
GENKSYMS_DEBUG_REL = Path("zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json")
GENKSYMS_LONG_REL = Path("zigux/tests/fixtures/genksyms_bridge/long_options_expected.json")
GENKSYMS_ABBREVIATED_REL = Path("zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json")
GENKSYMS_QUIET_REL = Path("zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json")
GENKSYMS_TERMINATOR_REL = Path("zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json")
GENKSYMS_POSITIONAL_REL = Path("zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json")
GENKSYMS_LONE_DASH_REL = Path("zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json")
GENKSYMS_DASH_PREFIXED_REL = Path(
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json"
)
GENKSYMS_DASH_PREFIXED_SHORT_REL = Path(
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json"
)
GENKSYMS_PROCESS_OUTPUT_RELS = (
    Path("zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json"),
    Path("zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json"),
)
ARCHIVE_README_REL = Path("third_party/README.md")
ARCHIVE_PAYLOAD_REL = Path("third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz")
ARCHIVE_PARTS_MANIFEST_REL = Path(
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.parts/manifest.json"
)
ARCHIVE_SUPPORT_RELS = (
    ARCHIVE_PAYLOAD_REL,
    ARCHIVE_PARTS_MANIFEST_REL,
)

REQUIRED_FILES = (
    WORKFLOW_REL,
    PHASE2_CLOSURE_REL,
    PHASE2_BOOTSTRAP_NOTES_REL,
    PHASE2_GENKSYMS_SURVEY_REL,
    PHASE2_VALIDATE_REL,
    PHASE2_CLOSURE_VALIDATE_REL,
    LOCAL_ARCHIVE_WORKFLOW_CHECKER_REL,
    LOCAL_ARCHIVE_README_CHECKER_REL,
    INSTALL_ZIG_ARCHIVE_VERIFICATION_CHECKER_REL,
    STAGE_HELPER_CONTRACT_CHECKER_REL,
    STAGE_HELPER_SELFTEST_CHECKER_REL,
    INSTALL_ZIG_REL,
    STAGE_PINNED_ARCHIVE_REL,
    TOOLCHAIN_CHECKER_REL,
    PINNING_CHECKER_REL,
    PIN_SCOPE_CHECKER_REL,
    KBUILD_CHECKER_REL,
    KCONFIG_BRIDGE_CHECKER_REL,
    KCONFIG_ALIGNMENT_REL,
    KCONFIG_ALLCONFIG_HELPER_PACKET_REL,
    GENKSYMS_ALIGNMENT_REL,
    TESTS_ALIGNMENT_REL,
    CROSS_CHECKER_REL,
    CROSS_ALIGNMENT_REL,
    DOCS_REMINDER_CHECKER_REL,
    REQUIRED_ROUTES_CHECKER_REL,
    TOOL_MANIFEST_CHECKER_REL,
    ARTIFACT_MANIFEST_CHECKER_REL,
    GENKSYMS_CHECKER_REL,
    FIXDEP_GATE_REL,
    FIXDEP_DIFF_REL,
    TOOLCHAIN_POLICY_REL,
    CONF_BRIDGE_REL,
    CONFDATA_BRIDGE_REL,
    GENKSYMS_BRIDGE_REL,
    GENKSYMS_VERSION_PROOF_REL,
    GENKSYMS_AMBIGUOUS_VERSION_PROOF_REL,
    FIXDEP_BRIDGE_REL,
    ARCHIVE_README_REL,
    MAKEFILE_REL,
    MANIFEST_REL,
    ARTIFACT_MANIFEST_REL,
    CROSS_FIXTURE_REL,
    FIXDEP_CASES_REL,
    CONF_MANIFEST_REL,
    CONFDATA_MANIFEST_REL,
    KCONFIG_CASES_REL,
    GENKSYMS_CASES_REL,
    GENKSYMS_HELP_REL,
    GENKSYMS_MANIFEST_REL,
    GENKSYMS_MINIMAL_REL,
    GENKSYMS_DEBUG_REL,
    GENKSYMS_LONG_REL,
    GENKSYMS_ABBREVIATED_REL,
    GENKSYMS_QUIET_REL,
    GENKSYMS_TERMINATOR_REL,
    GENKSYMS_POSITIONAL_REL,
    GENKSYMS_LONE_DASH_REL,
    GENKSYMS_DASH_PREFIXED_REL,
    GENKSYMS_DASH_PREFIXED_SHORT_REL,
    *GENKSYMS_PROCESS_OUTPUT_RELS,
)

REQUIRED_CLOSURE_MARKERS = (
    "`Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`",
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/check-phase2-cross.py`",
    "`scripts/zigux/check-phase2-cross-selftest-alignment.py`",
    "`third_party/README.md`",
    "`scripts/zigux/kconfig/conf_bridge.zig`",
    "`scripts/zigux/kconfig/confdata_bridge.zig`",
    "`scripts/zigux/genksyms.zig`",
    "`scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`",
    "`scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig`",
    "`scripts/zigux/fixdep.zig`",
    "`zigux/tests/fixtures/kconfig_bridge/cases.json`",
    "`zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`",
    "`zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`",
    "`zigux/tests/fixtures/phase2_tool_manifest.json`",
    "`zigux/tests/fixtures/phase2_artifact_tools_manifest.json`",
    "`zigux/tests/fixtures/phase2_cross_targets.json`",
    "`zigux/tests/fixtures/fixdep/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/cases.json`",
    "`zigux/tests/fixtures/genksyms_bridge/manifest.json`",
    "`zigux/tests/fixtures/genksyms_bridge/help_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json`",
    "`zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`",
    "`python3 scripts/zigux/check-lane05-local-archive-readme.py`",
    "`python3 scripts/zigux/install-zig.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py --self-test`",
    "`python3 scripts/zigux/check-phase2-cross.py`",
    "`python3 scripts/zigux/check-kconfig-bridge.py --self-test`",
    "`python3 scripts/zigux/check-kconfig-bridge.py`",
    "`python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test`",
    "`python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
    "`python3 scripts/zigux/check-phase2-tool-manifest.py --self-test`",
    "`python3 scripts/zigux/check-phase2-tool-manifest.py`",
    "`python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test`",
    "`python3 scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`python3 scripts/zigux/check-genksyms-bridge.py --self-test`",
    "`python3 scripts/zigux/check-genksyms-bridge.py`",
    "`python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test`",
    "`python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`",
    "`python3 scripts/zigux/check-phase2-fixdep-gate.py`",
    "`python3 scripts/zigux/check-fixdep-diff.py --self-test`",
    "`python3 scripts/zigux/check-fixdep-diff.py`",
    "`make -C zigux phase2-toolchain`",
    "`make -C zigux phase2-tools`",
    "`make -C zigux phase2-kconfig`",
    "`make -C zigux phase2-cross`",
    "`make -C zigux phase2-genksyms`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2-validate`",
    "`make -C zigux phase2`",
    "`PHASE2_CURRENT_GAP_PACKET=`",
)

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: python3 scripts/zigux/validate-phase2.py",
)

REQUIRED_MAKEFILE_LINES = (
    "phase2-toolchain:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --policy-only",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-zig-toolchain.py --archive-only --allow-missing",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pin-scope.py",
    "phase2-tools:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kbuild-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-docs-shared-reminder.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-required-make-routes.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-artifact-tools-manifest.py",
    "phase2-kconfig:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-kconfig-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-selftest-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-kconfig-allconfig-helper-packet.py",
    "phase2-cross:",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-cross-selftest-alignment.py",
    "phase2-genksyms:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
    "phase2-fixdep:",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
    "phase2: phase2-validate",
)

EXPECTED_MANIFEST_REVIEW_SURFACES = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/review-checklist.md",
    "zigux/tests/README.md",
)
EXPECTED_MANIFEST_CLOSURE_NOTES = (
    "Documentation/zigux/phase2-closure.md",
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
)
EXPECTED_MANIFEST_VALIDATORS = (
    "scripts/zigux/validate-phase2.py",
    "scripts/zigux/validate-phase2-closure.py",
)
EXPECTED_MANIFEST_CHECKERS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
)
EXPECTED_MANIFEST_BOOTSTRAP_HELPERS = (
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
)
EXPECTED_MANIFEST_ARCHIVE_SUPPORT = (
    "third_party/README.md",
)
DEFAULT_MANIFEST_ARCHIVE_SUPPORT = (
    *EXPECTED_MANIFEST_ARCHIVE_SUPPORT,
    ARCHIVE_PAYLOAD_REL.as_posix(),
)
EXPECTED_MANIFEST_BRIDGE_HELPERS = (
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
)
EXPECTED_MANIFEST_FIXTURE_ROSTER = (
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json",
)

EXPECTED_GENKSYMS_CASES = [
    {"name": "minimal", "args": [], "expected_file": "minimal_expected.json"},
    {
        "name": "debug_reference_types",
        "args": ["-d", "-r", "ref.symvers", "-T", "types.symtypes"],
        "expected_file": "debug_reference_types_expected.json",
    },
    {
        "name": "long_options",
        "args": ["--debug", "--dump", "--reference=foo.symref", "--dump-types", "types.symtypes", "--preserve"],
        "expected_file": "long_options_expected.json",
    },
    {
        "name": "abbreviated_long_options",
        "args": ["--deb", "--warn", "--qui", "--ref=foo.symref", "--dump-t", "types.symtypes", "--pres"],
        "expected_file": "abbreviated_long_options_expected.json",
    },
    {
        "name": "quiet_overrides_warning",
        "args": ["--warnings", "--quiet", "--reference", "bar.symref"],
        "expected_file": "quiet_overrides_warning_expected.json",
    },
    {
        "name": "explicit_option_terminator",
        "args": ["-d", "leftover.c", "--", "--leftover", "positional"],
        "expected_file": "explicit_option_terminator_expected.json",
    },
    {
        "name": "positional_passthrough",
        "args": ["leftover.c", "-d", "rightover.h", "-r", "foo.symref"],
        "expected_file": "positional_passthrough_expected.json",
    },
    {
        "name": "lone_dash_passthrough",
        "args": ["-", "-d"],
        "expected_file": "lone_dash_passthrough_expected.json",
    },
    {
        "name": "dash_prefixed_long_option_arguments_as_data",
        "args": ["--reference", "--debug", "--dump-types", "--types"],
        "expected_file": "dash_prefixed_long_option_arguments_as_data_expected.json",
    },
    {
        "name": "dash_prefixed_short_option_arguments_as_data",
        "args": ["-r", "-d", "-T", "--symtypes"],
        "expected_file": "dash_prefixed_short_option_arguments_as_data_expected.json",
    },
]

EXPECTED_GENKSYMS_MANIFEST = {
    "tool": "scripts/zigux/genksyms.zig",
    "status": "closed",
    "mode": "bounded wrapper-first dual-implementation bridge",
    "fixture_root": "zigux/tests/fixtures/genksyms_bridge",
    "fixture_case_source": "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "case_count": 10,
    "cases": [
        "minimal",
        "debug_reference_types",
        "long_options",
        "abbreviated_long_options",
        "quiet_overrides_warning",
        "explicit_option_terminator",
        "positional_passthrough",
        "lone_dash_passthrough",
        "dash_prefixed_long_option_arguments_as_data",
        "dash_prefixed_short_option_arguments_as_data",
    ],
    "bridge_expected_packet": [
        "minimal_expected.json",
        "debug_reference_types_expected.json",
        "long_options_expected.json",
        "abbreviated_long_options_expected.json",
        "quiet_overrides_warning_expected.json",
        "explicit_option_terminator_expected.json",
        "positional_passthrough_expected.json",
        "lone_dash_passthrough_expected.json",
        "dash_prefixed_long_option_arguments_as_data_expected.json",
        "dash_prefixed_short_option_arguments_as_data_expected.json",
    ],
    "help_packet": [
        "help_expected.json",
    ],
    "standalone_proof_packet": [
        "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
        "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    ],
    "process_output_packet": [
        "abbreviated_version_expected.json",
        "ambiguous_long_option_expected.json",
        "invalid_option_expected.json",
        "missing_long_dump_types_argument_expected.json",
        "missing_long_reference_argument_expected.json",
        "missing_reference_argument_expected.json",
        "too_many_reference_files_expected.json",
        "unsupported_long_option_expected.json",
        "unexpected_long_help_argument_expected.json",
        "abbreviated_unexpected_long_help_argument_expected.json",
    ],
    "helper_local_anchors": [
        "genksyms bridge treats pure version requests as version command",
        "genksyms bridge preserves repeated pure version invocations",
        "genksyms bridge preserves empty inline long reference argument",
        "genksyms bridge preserves empty inline abbreviated dump-types argument",
        "parseArgs reports ambiguous abbreviated long options",
        "genksyms bridge renders ambiguous long option failure like the fixture",
        "genksyms bridge renders invalid short option failure like the fixture",
        "genksyms bridge renders missing long option argument like the fixture",
        "genksyms bridge renders missing short option argument like the fixture",
        "genksyms bridge renders unexpected long option argument like the fixture",
        "genksyms bridge appends usage after getopt-style parse failures",
        "genksyms bridge leaves tool-local reference-limit failure message unchanged",
        "genksyms bridge keeps dash-prefixed long option arguments as data",
        "genksyms bridge keeps dash-prefixed short option arguments as data",
        "genksyms bridge rejects more than sixteen reference files like the C harness",
    ],
}

EXPECTED_CONF_CASE_DETAILS = [
    {"name": "oldaskconfig", "args": ["oldaskconfig", "Kconfig"], "expected": "oldaskconfig_expected.json"},
    {"name": "syncconfig", "args": ["syncconfig", "Kconfig"], "expected": "syncconfig_expected.json"},
    {"name": "oldconfig", "args": ["oldconfig", "Kconfig"], "expected": "oldconfig_expected.json"},
    {"name": "allnoconfig", "args": ["allnoconfig", "Kconfig"], "expected": "allnoconfig_expected.json"},
    {"name": "allyesconfig", "args": ["allyesconfig", "Kconfig"], "expected": "allyesconfig_expected.json"},
    {"name": "allmodconfig", "args": ["allmodconfig", "Kconfig"], "expected": "allmodconfig_expected.json"},
    {"name": "alldefconfig", "args": ["alldefconfig", "Kconfig"], "expected": "alldefconfig_expected.json"},
    {"name": "randconfig", "args": ["randconfig", "Kconfig"], "expected": "randconfig_expected.json"},
    {"name": "defconfig", "args": ["defconfig", "arch/arm64/configs/defconfig", "Kconfig"], "expected": "defconfig_expected.json"},
    {"name": "savedefconfig", "args": ["savedefconfig", "configs/minimal_defconfig", "Kconfig"], "expected": "savedefconfig_expected.json"},
    {"name": "listnewconfig", "args": ["listnewconfig", "Kconfig"], "expected": "listnewconfig_expected.json"},
    {"name": "helpnewconfig", "args": ["helpnewconfig", "Kconfig"], "expected": "helpnewconfig_expected.json"},
    {"name": "olddefconfig", "args": ["olddefconfig", "Kconfig"], "expected": "olddefconfig_expected.json"},
    {"name": "yes2modconfig", "args": ["yes2modconfig", "Kconfig"], "expected": "yes2modconfig_expected.json"},
    {"name": "mod2yesconfig", "args": ["mod2yesconfig", "Kconfig"], "expected": "mod2yesconfig_expected.json"},
    {"name": "mod2noconfig", "args": ["mod2noconfig", "Kconfig"], "expected": "mod2noconfig_expected.json"},
]

EXPECTED_CONF_MANIFEST = {
    "tool": "scripts/zigux/kconfig/conf_bridge.zig",
    "status": "closed",
    "mode": "bounded request-plan bridge",
    "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
    "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "case_count": 16,
    "cases": [
        "oldaskconfig",
        "syncconfig",
        "oldconfig",
        "allnoconfig",
        "allyesconfig",
        "allmodconfig",
        "alldefconfig",
        "randconfig",
        "defconfig",
        "savedefconfig",
        "listnewconfig",
        "helpnewconfig",
        "olddefconfig",
        "yes2modconfig",
        "mod2yesconfig",
        "mod2noconfig",
    ],
    "stdout_packet": [
        "oldaskconfig_expected.json",
        "syncconfig_expected.json",
        "oldconfig_expected.json",
        "allnoconfig_expected.json",
        "allyesconfig_expected.json",
        "allmodconfig_expected.json",
        "alldefconfig_expected.json",
        "randconfig_expected.json",
        "defconfig_expected.json",
        "savedefconfig_expected.json",
        "listnewconfig_expected.json",
        "helpnewconfig_expected.json",
        "olddefconfig_expected.json",
        "yes2modconfig_expected.json",
        "mod2yesconfig_expected.json",
        "mod2noconfig_expected.json",
    ],
    "helper_local_anchors": [
        "conf bridge emits oldaskconfig mode argument before kconfig",
        "conf bridge emits syncconfig mode argument before kconfig",
        "conf bridge emits oldconfig mode argument before kconfig",
        "conf bridge emits allnoconfig mode argument before kconfig",
        "conf bridge emits allyesconfig mode argument before kconfig",
        "conf bridge emits allmodconfig mode argument before kconfig",
        "conf bridge emits alldefconfig mode argument before kconfig",
        "conf bridge emits randconfig mode argument before kconfig",
        "conf bridge emits olddefconfig mode argument before kconfig",
        "conf bridge emits yes2modconfig mode argument before kconfig",
        "conf bridge emits mod2yesconfig mode argument before kconfig",
        "conf bridge emits mod2noconfig mode argument before kconfig",
        "conf bridge emits listnewconfig mode argument before kconfig",
        "conf bridge emits helpnewconfig mode argument before kconfig",
        "conf bridge keeps helpnewconfig mode argument even when silent is set",
        "bridge options parser rejects duplicate allconfig arguments",
        "bridge options parser rejects missing allconfig argument",
        "bridge options parser rejects duplicate env overrides",
        "bridge options parser rejects duplicate kconfig paths",
        "bridge options parser rejects helpnewconfig without a kconfig path",
        "bridge options parser rejects defconfig with missing path",
        "bridge options parser rejects savedefconfig with missing path",
        "conf bridge emits defconfig mode argument before defconfig path",
        "conf bridge emits savedefconfig mode argument before kconfig",
        "conf bridge escapes low control bytes in JSON strings",
        "mode argument validation rejects bridge option shaped defconfig payload",
        "mode argument validation accepts defconfig path that only starts with silent",
        "mode argument validation still accepts ordinary path text with equals",
        "bridge options parser accepts explicit allconfig override for allmodconfig",
        "bridge options parser accepts syncconfig nosilentupdate",
        "bridge options parser keeps empty syncconfig nosilentupdate unset",
        "bridge options parser accepts generic silent flag",
        "bridge options parser accepts silent alongside randconfig options",
        "bridge options parser rejects duplicate silent flag",
        "bridge options parser rejects duplicate randconfig probability",
        "bridge options parser rejects unexpected options for mode",
        "bridge options parser keeps empty randconfig tunables unset",
        "bridge options parser rejects duplicate mode specific options",
    ],
}

EXPECTED_CONFDATA_CASE_DETAILS = [
    {"name": "sample", "input": "sample.config", "expected": "sample_expected.json"},
    {"name": "escaped_strings", "input": "escaped_strings.config", "expected": "escaped_strings_expected.json"},
    {"name": "escaped_control_sequences", "input": "escaped_control_sequences.config", "expected": "escaped_control_sequences_expected.json"},
    {"name": "trailing_escaped_backslash", "input": "trailing_escaped_backslash.config", "expected": "trailing_escaped_backslash_expected.json"},
    {"name": "sample_crlf", "input": "sample_crlf.config", "expected": "sample_crlf_expected.json"},
    {"name": "explicit_n_tristate", "input": "explicit_n_tristate.config", "expected": "explicit_n_tristate_expected.json"},
    {"name": "final_trailing_carriage_return", "input": "final_trailing_carriage_return.config", "expected": "final_trailing_carriage_return_expected.json"},
    {"name": "final_unterminated_unset_comment", "input": "final_unterminated_unset_comment.config", "expected": "final_unterminated_unset_comment_expected.json"},
    {"name": "uppercase_tristate", "input": "uppercase_tristate.config", "expected": "uppercase_tristate_expected.json"},
    {"name": "non_config_lines", "input": "non_config_lines.config", "expected": "non_config_lines_expected.json"},
    {"name": "empty_config_symbol_names", "input": "empty_config_symbol_names.config", "expected": "empty_config_symbol_names_expected.json"},
    {"name": "malformed_unset_comment_tokens", "input": "malformed_unset_comment_tokens.config", "expected": "malformed_unset_comment_tokens_expected.json"},
    {"name": "last_state_transitions", "input": "last_state_transitions.config", "expected": "last_state_transitions_expected.json"},
    {"name": "duplicate_assignments", "input": "duplicate_assignments.config", "expected": "duplicate_assignments_expected.json"},
    {"name": "duplicate_malformed_quoted_assignment", "input": "duplicate_malformed_quoted_assignment.config", "expected": "duplicate_malformed_quoted_assignment_expected.json"},
]

EXPECTED_CONFDATA_MANIFEST = {
    "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
    "status": "closed",
    "mode": "bounded config bridge",
    "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
    "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "case_count": 15,
    "cases": [
        "sample",
        "escaped_strings",
        "escaped_control_sequences",
        "trailing_escaped_backslash",
        "sample_crlf",
        "explicit_n_tristate",
        "final_trailing_carriage_return",
        "final_unterminated_unset_comment",
        "uppercase_tristate",
        "non_config_lines",
        "empty_config_symbol_names",
        "malformed_unset_comment_tokens",
        "last_state_transitions",
        "duplicate_assignments",
        "duplicate_malformed_quoted_assignment",
    ],
    "input_packet": [
        "sample.config",
        "escaped_strings.config",
        "escaped_control_sequences.config",
        "trailing_escaped_backslash.config",
        "sample_crlf.config",
        "explicit_n_tristate.config",
        "final_trailing_carriage_return.config",
        "final_unterminated_unset_comment.config",
        "uppercase_tristate.config",
        "non_config_lines.config",
        "empty_config_symbol_names.config",
        "malformed_unset_comment_tokens.config",
        "last_state_transitions.config",
        "duplicate_assignments.config",
        "duplicate_malformed_quoted_assignment.config",
    ],
    "expected_packet": [
        "sample_expected.json",
        "escaped_strings_expected.json",
        "escaped_control_sequences_expected.json",
        "trailing_escaped_backslash_expected.json",
        "sample_crlf_expected.json",
        "explicit_n_tristate_expected.json",
        "final_trailing_carriage_return_expected.json",
        "final_unterminated_unset_comment_expected.json",
        "uppercase_tristate_expected.json",
        "non_config_lines_expected.json",
        "empty_config_symbol_names_expected.json",
        "malformed_unset_comment_tokens_expected.json",
        "last_state_transitions_expected.json",
        "duplicate_assignments_expected.json",
        "duplicate_malformed_quoted_assignment_expected.json",
    ],
    "helper_local_anchors": [
        "confdata bridge parses bounded config states",
        "confdata bridge emits bounded json output",
        "confdata bridge decodes escaped quoted strings",
        "confdata bridge strips backslashes from escaped control sequences like upstream confdata",
        "confdata bridge escapes low control bytes in json output",
        "confdata bridge accepts CRLF config lines",
        "confdata bridge preserves trailing carriage return on final unterminated value line",
        "confdata bridge ignores unterminated unset comment with trailing carriage return",
        "confdata bridge ignores suffix bytes after an embedded NUL",
        "confdata bridge preserves carriage return before an embedded NUL on newline-terminated lines",
        "confdata bridge keeps explicit n assignments as tristate values",
        "confdata bridge recognizes uppercase tristate assignments",
        "confdata bridge ignores non-CONFIG lines like upstream confdata",
        "confdata bridge ignores empty CONFIG symbol names",
        "confdata bridge ignores malformed unset comments with extra tokens",
        "confdata bridge keeps trailing escaped backslashes in quoted strings",
        "confdata bridge ignores trailing suffix bytes after a closing quote like upstream confdata",
        "confdata bridge ignores malformed quoted values like upstream confdata",
        "confdata bridge emits no entries for empty CONFIG symbol names",
        "confdata bridge keeps only the last assignment for duplicate symbols",
        "confdata bridge keeps the prior duplicate value when a later quoted assignment is malformed",
        "confdata bridge keeps only the last state across unset and set transitions",
        "confdata bridge keeps explicit empty assignments distinct from quoted empty strings",
        "confdata bridge releases appended entry ownership on index-allocation failure",
        "confdata bridge preserves duplicate unset ownership on allocation failure",
    ],
}


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def require_manifest_list(issues: list[tuple[str, str]], manifest: dict[str, object], key: str) -> list[str] | None:
    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    value = surfaces.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    return list(value)


def expect_subset(issues: list[tuple[str, str]], label: str, actual: list[str] | None, expected: tuple[str, ...]) -> None:
    if actual is None:
        return
    for marker in expected:
        if marker not in actual:
            issues.append(("MISSING_MANIFEST_SURFACE", f"{label}:{marker}"))


def collect_archive_support_issues(root: Path, archive_support: list[str] | None) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    archive_support_note = " or ".join(rel.as_posix() for rel in ARCHIVE_SUPPORT_RELS)
    if not any(resolve(root, rel).exists() for rel in ARCHIVE_SUPPORT_RELS):
        issues.append(("MISSING_REQUIRED_ARCHIVE_SUPPORT", archive_support_note))
    if archive_support is not None and not any(rel.as_posix() in archive_support for rel in ARCHIVE_SUPPORT_RELS):
        issues.append(("MISSING_MANIFEST_ARCHIVE_SUPPORT", archive_support_note))
    return issues


def collect_case_manifest_issues(
    issues: list[tuple[str, str]],
    kconfig_cases: object,
    conf_manifest: object,
    confdata_manifest: object,
    genksyms_cases: object,
    genksyms_manifest: object,
) -> None:
    if not isinstance(kconfig_cases, dict):
        issues.append(("KCONFIG_CASE_PACKET_MISMATCH", "root"))
    else:
        if kconfig_cases.get("conf_cases") != EXPECTED_CONF_CASE_DETAILS:
            issues.append(("CONF_CASE_PACKET_MISMATCH", "conf_cases"))
        if kconfig_cases.get("confdata_cases") != EXPECTED_CONFDATA_CASE_DETAILS:
            issues.append(("CONFDATA_CASE_PACKET_MISMATCH", "confdata_cases"))

    if conf_manifest != EXPECTED_CONF_MANIFEST:
        issues.append(("CONF_MANIFEST_MISMATCH", "root"))
    if confdata_manifest != EXPECTED_CONFDATA_MANIFEST:
        issues.append(("CONFDATA_MANIFEST_MISMATCH", "root"))
    if genksyms_cases != EXPECTED_GENKSYMS_CASES:
        issues.append(("GENKSYMS_CASE_PACKET_MISMATCH", "cases"))
    if genksyms_manifest != EXPECTED_GENKSYMS_MANIFEST:
        issues.append(("GENKSYMS_MANIFEST_MISMATCH", "root"))


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for rel in REQUIRED_FILES:
        if not resolve(root, rel).exists():
            issues.append(("MISSING_REQUIRED_FILE", rel.as_posix()))
    if issues:
        return issues

    workflow_text = read_text(resolve(root, WORKFLOW_REL))
    closure_text = read_text(resolve(root, PHASE2_CLOSURE_REL))
    makefile_text = read_text(resolve(root, MAKEFILE_REL))
    manifest = read_json(resolve(root, MANIFEST_REL))
    kconfig_cases = read_json(resolve(root, KCONFIG_CASES_REL))
    conf_manifest = read_json(resolve(root, CONF_MANIFEST_REL))
    confdata_manifest = read_json(resolve(root, CONFDATA_MANIFEST_REL))
    genksyms_cases = read_json(resolve(root, GENKSYMS_CASES_REL))
    genksyms_manifest = read_json(resolve(root, GENKSYMS_MANIFEST_REL))

    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    manifest_gaps = manifest.get("repo_reality_gaps")
    if manifest_gaps != []:
        issues.append(("UNEXPECTED_MANIFEST_GAPS", repr(manifest_gaps)))

    expect_subset(issues, "review_surfaces", require_manifest_list(issues, manifest, "review_surfaces"), EXPECTED_MANIFEST_REVIEW_SURFACES)
    expect_subset(issues, "closure_notes", require_manifest_list(issues, manifest, "closure_notes"), EXPECTED_MANIFEST_CLOSURE_NOTES)
    expect_subset(issues, "validators", require_manifest_list(issues, manifest, "validators"), EXPECTED_MANIFEST_VALIDATORS)
    expect_subset(issues, "checkers", require_manifest_list(issues, manifest, "checkers"), EXPECTED_MANIFEST_CHECKERS)
    expect_subset(issues, "bootstrap_helpers", require_manifest_list(issues, manifest, "bootstrap_helpers"), EXPECTED_MANIFEST_BOOTSTRAP_HELPERS)
    archive_support = require_manifest_list(issues, manifest, "archive_support")
    expect_subset(issues, "archive_support", archive_support, EXPECTED_MANIFEST_ARCHIVE_SUPPORT)
    issues.extend(collect_archive_support_issues(root, archive_support))
    expect_subset(issues, "bridge_helpers", require_manifest_list(issues, manifest, "bridge_helpers"), EXPECTED_MANIFEST_BRIDGE_HELPERS)
    expect_subset(issues, "fixture_roster", require_manifest_list(issues, manifest, "fixture_roster"), EXPECTED_MANIFEST_FIXTURE_ROSTER)

    collect_case_manifest_issues(
        issues,
        kconfig_cases,
        conf_manifest,
        confdata_manifest,
        genksyms_cases,
        genksyms_manifest,
    )

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_VALIDATION=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    archive_parts_manifest = resolve(root, ARCHIVE_PARTS_MANIFEST_REL)
    if archive_parts_manifest.exists():
        archive_parts_manifest.unlink()

    closure_lines = [
        "# Phase 2 Closure",
        "",
        "## Current Closure Packet",
        "",
        *[f"- {marker}" for marker in REQUIRED_CLOSURE_MARKERS],
        "",
    ]
    workflow_lines = ["name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES]
    makefile_lines = [
        "PYTHON ?= python3",
        "ZIG ?= zig",
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        "ZIGUX_ROOT := ..",
        "",
        *REQUIRED_MAKEFILE_LINES,
    ]
    manifest = {
        "phase": "Phase 2",
        "status": "active",
        "repo_reality_gaps": [],
        "present_surfaces": {
            "review_surfaces": list(EXPECTED_MANIFEST_REVIEW_SURFACES),
            "closure_notes": list(EXPECTED_MANIFEST_CLOSURE_NOTES),
            "validators": list(EXPECTED_MANIFEST_VALIDATORS),
            "checkers": list(EXPECTED_MANIFEST_CHECKERS),
            "bootstrap_helpers": list(EXPECTED_MANIFEST_BOOTSTRAP_HELPERS),
            "archive_support": list(DEFAULT_MANIFEST_ARCHIVE_SUPPORT),
            "bridge_helpers": list(EXPECTED_MANIFEST_BRIDGE_HELPERS),
            "fixture_roster": list(EXPECTED_MANIFEST_FIXTURE_ROSTER),
        },
    }
    kconfig_cases = {
        "conf_cases": EXPECTED_CONF_CASE_DETAILS,
        "confdata_cases": EXPECTED_CONFDATA_CASE_DETAILS,
    }

    write_text(resolve(root, PHASE2_CLOSURE_REL), "\n".join(closure_lines))
    write_text(resolve(root, WORKFLOW_REL), "\n".join(workflow_lines) + "\n")
    write_text(resolve(root, MAKEFILE_REL), "\n".join(makefile_lines) + "\n")
    write_text(resolve(root, MANIFEST_REL), json.dumps(manifest, indent=2) + "\n")
    write_text(resolve(root, KCONFIG_CASES_REL), json.dumps(kconfig_cases, indent=2) + "\n")
    write_text(resolve(root, CONF_MANIFEST_REL), json.dumps(EXPECTED_CONF_MANIFEST, indent=2) + "\n")
    write_text(resolve(root, CONFDATA_MANIFEST_REL), json.dumps(EXPECTED_CONFDATA_MANIFEST, indent=2) + "\n")
    write_text(resolve(root, GENKSYMS_CASES_REL), json.dumps(EXPECTED_GENKSYMS_CASES, indent=2) + "\n")
    write_text(resolve(root, GENKSYMS_MANIFEST_REL), json.dumps(EXPECTED_GENKSYMS_MANIFEST, indent=2) + "\n")

    for rel in REQUIRED_FILES:
        if rel in {
            PHASE2_CLOSURE_REL,
            WORKFLOW_REL,
            MAKEFILE_REL,
            MANIFEST_REL,
            KCONFIG_CASES_REL,
            CONF_MANIFEST_REL,
            CONFDATA_MANIFEST_REL,
            GENKSYMS_CASES_REL,
            GENKSYMS_MANIFEST_REL,
        }:
            continue
        if rel.suffix == ".json":
            write_text(resolve(root, rel), "{}\n")
        else:
            write_text(resolve(root, rel), "present\n")
    write_text(resolve(root, ARCHIVE_PAYLOAD_REL), "present\n")


def replace_once(text: str, marker: str, replacement: str = "") -> str:
    if marker not in text:
        raise AssertionError(f"marker not found: {marker}")
    return text.replace(marker, replacement, 1)


def replace_exact_line(text: str, marker: str, replacement: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines[index] = replacement
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validate_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_self_test_root(root)
        archive_payload_path = resolve(root, ARCHIVE_PAYLOAD_REL)
        archive_payload_path.unlink()
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["archive_support"] = [
            "third_party/README.md",
            ARCHIVE_PARTS_MANIFEST_REL.as_posix(),
        ]
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        write_text(resolve(root, ARCHIVE_PARTS_MANIFEST_REL), '{"parts": []}\n')
        assert collect_issues(root) == []
        checks_run += 1

        closure_path = resolve(root, PHASE2_CLOSURE_REL)
        closure_path.write_text(replace_once(closure_path.read_text(encoding="utf-8"), "`Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`"), encoding="utf-8")
        assert ("MISSING_CLOSURE_MARKER", "`Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        closure_path = resolve(root, PHASE2_CLOSURE_REL)
        closure_path.write_text(
            replace_once(
                closure_path.read_text(encoding="utf-8"),
                "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
            ),
            encoding="utf-8",
        )
        assert (
            "MISSING_CLOSURE_MARKER",
            "`scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py`",
        ) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        workflow_path = resolve(root, WORKFLOW_REL)
        workflow_path.write_text(replace_exact_line(workflow_path.read_text(encoding="utf-8"), "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py", "run: python3 scripts/zigux/other.py"), encoding="utf-8")
        assert ("MISSING_WORKFLOW_LINE", "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        makefile_path = resolve(root, MAKEFILE_REL)
        makefile_path.write_text(replace_exact_line(makefile_path.read_text(encoding="utf-8"), "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py", "# removed"), encoding="utf-8")
        assert ("MISSING_MAKEFILE_LINE", "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["checkers"].remove("scripts/zigux/check-lane05-install-zig-archive-verification.py")
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_SURFACE", "checkers:scripts/zigux/check-lane05-install-zig-archive-verification.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["bootstrap_helpers"].remove("scripts/zigux/stage-pinned-zig-archive.py")
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_SURFACE", "bootstrap_helpers:scripts/zigux/stage-pinned-zig-archive.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["archive_support"].remove("third_party/README.md")
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_SURFACE", "archive_support:third_party/README.md") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        archive_payload_path = resolve(root, ARCHIVE_PAYLOAD_REL)
        archive_payload_path.unlink()
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["archive_support"] = ["third_party/README.md"]
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        archive_support_note = " or ".join(rel.as_posix() for rel in ARCHIVE_SUPPORT_RELS)
        assert ("MISSING_REQUIRED_ARCHIVE_SUPPORT", archive_support_note) in issues
        assert ("MISSING_MANIFEST_ARCHIVE_SUPPORT", archive_support_note) in issues
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["bridge_helpers"].remove("scripts/zigux/genksyms_version_before_invalid_long_option_test.zig")
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_SURFACE", "bridge_helpers:scripts/zigux/genksyms_version_before_invalid_long_option_test.zig") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        manifest_path = resolve(root, MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["fixture_roster"].remove("zigux/tests/fixtures/genksyms_bridge/manifest.json")
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_SURFACE", "fixture_roster:zigux/tests/fixtures/genksyms_bridge/manifest.json") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        genksyms_manifest_path = resolve(root, GENKSYMS_MANIFEST_REL)
        payload = json.loads(genksyms_manifest_path.read_text(encoding="utf-8"))
        payload["process_output_packet"] = ["invalid_option_expected.json"]
        genksyms_manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("GENKSYMS_MANIFEST_MISMATCH", "root") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        genksyms_cases_path = resolve(root, GENKSYMS_CASES_REL)
        payload = json.loads(genksyms_cases_path.read_text(encoding="utf-8"))
        payload[0]["expected_file"] = "drifted.json"
        genksyms_cases_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("GENKSYMS_CASE_PACKET_MISMATCH", "cases") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (resolve(root, CONF_MANIFEST_REL)).write_text(
            json.dumps({**json.loads(resolve(root, CONF_MANIFEST_REL).read_text(encoding="utf-8")), "stdout_packet": ["drifted.json"]}, indent=2) + "\n",
            encoding="utf-8",
        )
        assert ("CONF_MANIFEST_MISMATCH", "root") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (resolve(root, CONFDATA_MANIFEST_REL)).write_text(
            json.dumps({**json.loads(resolve(root, CONFDATA_MANIFEST_REL).read_text(encoding="utf-8")), "helper_local_anchors": ["drifted anchor"]}, indent=2) + "\n",
            encoding="utf-8",
        )
        assert ("CONFDATA_MANIFEST_MISMATCH", "root") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        (resolve(root, PHASE2_GENKSYMS_SURVEY_REL)).unlink()
        assert ("MISSING_REQUIRED_FILE", PHASE2_GENKSYMS_SURVEY_REL.as_posix()) in collect_issues(root)
        checks_run += 1

    print("PHASE2_CLOSURE_VALIDATION_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_VALIDATION_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 2 closure note against the shipped closure packet.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_CLOSURE_VALIDATION=pass")
    print("PHASE2_CLOSURE_STATUS=parked")
    print("PHASE2_CLOSURE_PACKET=toolchain_cross_kconfig_genksyms_fixdep_closure")
    print("PHASE2_CLOSURE_REMAINING_GAPS=")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
