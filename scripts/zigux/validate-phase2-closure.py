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
PHASE2_VALIDATE_REL = Path("scripts/zigux/validate-phase2.py")
PHASE2_CLOSURE_VALIDATE_REL = Path("scripts/zigux/validate-phase2-closure.py")
INSTALL_ZIG_REL = Path("scripts/zigux/install-zig.py")
TOOLCHAIN_CHECKER_REL = Path("scripts/zigux/check-zig-toolchain.py")
PINNING_CHECKER_REL = Path("scripts/zigux/check-phase2-toolchain-pinning.py")
PIN_SCOPE_CHECKER_REL = Path("scripts/zigux/check-phase2-toolchain-pin-scope.py")
KBUILD_CHECKER_REL = Path("scripts/zigux/check-phase2-kbuild-routes.py")
KCONFIG_BRIDGE_CHECKER_REL = Path("scripts/zigux/check-kconfig-bridge.py")
KCONFIG_ALIGNMENT_REL = Path("scripts/zigux/check-phase2-kconfig-selftest-alignment.py")
TESTS_ALIGNMENT_REL = Path("scripts/zigux/check-phase2-tests-readme-alignment.py")
CROSS_CHECKER_REL = Path("scripts/zigux/check-phase2-cross.py")
CROSS_ALIGNMENT_REL = Path("scripts/zigux/check-phase2-cross-selftest-alignment.py")
DOCS_REMINDER_CHECKER_REL = Path("scripts/zigux/check-phase2-docs-shared-reminder.py")
REQUIRED_ROUTES_CHECKER_REL = Path("scripts/zigux/check-phase2-required-make-routes.py")
TOOL_MANIFEST_CHECKER_REL = Path("scripts/zigux/check-phase2-tool-manifest.py")
ARTIFACT_MANIFEST_CHECKER_REL = Path("scripts/zigux/check-phase2-artifact-tools-manifest.py")
GENKSYMS_CHECKER_REL = Path("scripts/zigux/check-genksyms-bridge.py")
GENKSYMS_SELFTEST_ALIGNMENT_REL = Path("scripts/zigux/check-phase2-genksyms-selftest-alignment.py")
FIXDEP_GATE_REL = Path("scripts/zigux/check-phase2-fixdep-gate.py")
FIXDEP_DIFF_REL = Path("scripts/zigux/check-fixdep-diff.py")
TOOLCHAIN_POLICY_REL = Path("scripts/zigux/zig-toolchain-policy.json")
CONF_BRIDGE_REL = Path("scripts/zigux/kconfig/conf_bridge.zig")
CONFDATA_BRIDGE_REL = Path("scripts/zigux/kconfig/confdata_bridge.zig")
GENKSYMS_BRIDGE_REL = Path("scripts/zigux/genksyms.zig")
GENKSYMS_VERSION_PROOF_REL = Path("scripts/zigux/genksyms_version_before_invalid_long_option_test.zig")
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
GENKSYMS_MANIFEST_REL = Path("zigux/tests/fixtures/genksyms_bridge/manifest.json")
GENKSYMS_HELP_REL = Path("zigux/tests/fixtures/genksyms_bridge/help_expected.json")
GENKSYMS_MINIMAL_REL = Path("zigux/tests/fixtures/genksyms_bridge/minimal_expected.json")
GENKSYMS_DEBUG_REL = Path("zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json")
GENKSYMS_LONG_REL = Path("zigux/tests/fixtures/genksyms_bridge/long_options_expected.json")
GENKSYMS_ABBREVIATED_REL = Path("zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json")
GENKSYMS_QUIET_REL = Path("zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json")
GENKSYMS_TERMINATOR_REL = Path("zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json")
GENKSYMS_POSITIONAL_REL = Path("zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json")
GENKSYMS_LONE_DASH_REL = Path("zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json")
GENKSYMS_ABBREVIATED_VERSION_REL = Path("zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json")
GENKSYMS_AMBIGUOUS_LONG_REL = Path("zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json")
GENKSYMS_INVALID_OPTION_REL = Path("zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json")
GENKSYMS_MISSING_LONG_DUMP_TYPES_REL = Path("zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json")
GENKSYMS_MISSING_LONG_REFERENCE_REL = Path("zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json")
GENKSYMS_MISSING_REFERENCE_REL = Path("zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json")
GENKSYMS_TOO_MANY_REFERENCE_REL = Path("zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json")
GENKSYMS_UNSUPPORTED_LONG_REL = Path("zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json")
GENKSYMS_UNEXPECTED_LONG_HELP_REL = Path("zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json")
LOCAL_ARCHIVE_WORKFLOW_CHECKER_REL = Path("scripts/zigux/check-lane05-local-first-archive-workflow.py")
LOCAL_ARCHIVE_README_CHECKER_REL = Path("scripts/zigux/check-lane05-local-archive-readme.py")
ARCHIVE_README_REL = Path("third_party/README.md")
ARCHIVE_PAYLOAD_REL = Path("third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz")

REQUIRED_FILES = (
    WORKFLOW_REL,
    PHASE2_CLOSURE_REL,
    PHASE2_BOOTSTRAP_NOTES_REL,
    PHASE2_VALIDATE_REL,
    PHASE2_CLOSURE_VALIDATE_REL,
    LOCAL_ARCHIVE_WORKFLOW_CHECKER_REL,
    LOCAL_ARCHIVE_README_CHECKER_REL,
    INSTALL_ZIG_REL,
    TOOLCHAIN_CHECKER_REL,
    PINNING_CHECKER_REL,
    PIN_SCOPE_CHECKER_REL,
    KBUILD_CHECKER_REL,
    KCONFIG_BRIDGE_CHECKER_REL,
    KCONFIG_ALIGNMENT_REL,
    TESTS_ALIGNMENT_REL,
    CROSS_CHECKER_REL,
    CROSS_ALIGNMENT_REL,
    DOCS_REMINDER_CHECKER_REL,
    REQUIRED_ROUTES_CHECKER_REL,
    TOOL_MANIFEST_CHECKER_REL,
    ARTIFACT_MANIFEST_CHECKER_REL,
    GENKSYMS_CHECKER_REL,
    GENKSYMS_SELFTEST_ALIGNMENT_REL,
    FIXDEP_GATE_REL,
    FIXDEP_DIFF_REL,
    TOOLCHAIN_POLICY_REL,
    CONF_BRIDGE_REL,
    CONFDATA_BRIDGE_REL,
    GENKSYMS_BRIDGE_REL,
    GENKSYMS_VERSION_PROOF_REL,
    FIXDEP_BRIDGE_REL,
    ARCHIVE_README_REL,
    ARCHIVE_PAYLOAD_REL,
    MAKEFILE_REL,
    MANIFEST_REL,
    ARTIFACT_MANIFEST_REL,
    CROSS_FIXTURE_REL,
    FIXDEP_CASES_REL,
    CONF_MANIFEST_REL,
    CONFDATA_MANIFEST_REL,
    KCONFIG_CASES_REL,
    GENKSYMS_CASES_REL,
    GENKSYMS_MANIFEST_REL,
    GENKSYMS_HELP_REL,
    GENKSYMS_MINIMAL_REL,
    GENKSYMS_DEBUG_REL,
    GENKSYMS_LONG_REL,
    GENKSYMS_ABBREVIATED_REL,
    GENKSYMS_QUIET_REL,
    GENKSYMS_TERMINATOR_REL,
    GENKSYMS_POSITIONAL_REL,
    GENKSYMS_LONE_DASH_REL,
    GENKSYMS_ABBREVIATED_VERSION_REL,
    GENKSYMS_AMBIGUOUS_LONG_REL,
    GENKSYMS_INVALID_OPTION_REL,
    GENKSYMS_MISSING_LONG_DUMP_TYPES_REL,
    GENKSYMS_MISSING_LONG_REFERENCE_REL,
    GENKSYMS_MISSING_REFERENCE_REL,
    GENKSYMS_TOO_MANY_REFERENCE_REL,
    GENKSYMS_UNSUPPORTED_LONG_REL,
    GENKSYMS_UNEXPECTED_LONG_HELP_REL,
)

REQUIRED_CLOSURE_MARKERS = (
    "`scripts/zigux/check-kconfig-bridge.py`",
    "`scripts/zigux/check-phase2-kconfig-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-tool-manifest.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-genksyms-bridge.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
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
    "`zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`",
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
    "The current closure-side packet keeps the fixdep governance and parity checker pair explicit through",
)

FORBIDDEN_CLOSURE_MARKERS: tuple[str, ...] = ()

REQUIRED_WORKFLOW_LINES = (
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
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

EXPECTED_MANIFEST_BOOTSTRAP_HELPERS = ("scripts/zigux/install-zig.py",)
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
EXPECTED_MANIFEST_POLICY = ("scripts/zigux/zig-toolchain-policy.json",)
EXPECTED_MANIFEST_ARCHIVE_SUPPORT = (
    "third_party/README.md",
    "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz",
)
EXPECTED_MANIFEST_CROSS_SUPPORT = (
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
)
EXPECTED_MANIFEST_ARTIFACT_SUPPORT = (
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
)
EXPECTED_MANIFEST_FIXDEP_SUPPORT = (
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "zigux/tests/fixtures/fixdep/cases.json",
)
EXPECTED_MANIFEST_FIXTURE_ROSTER = (
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/minimal_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
)
EXPECTED_MANIFEST_CHECKERS = (
    "scripts/zigux/check-zig-toolchain.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
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
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
)
EXPECTED_MANIFEST_BRIDGE_HELPERS = (
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
)
FORBIDDEN_MANIFEST_GAPS = (
    "scripts/zigux/install-zig.py",
    "scripts/zigux/check-phase2-cross.py",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "scripts/zigux/validate-phase2-closure.py",
    "scripts/zigux/check-kconfig-bridge.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
    "zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json",
    "zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/fixdep.zig",
    "zigux/tests/fixtures/fixdep/cases.json",
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
]

EXPECTED_CONF_CASE_DETAILS = [
    {"name": "oldaskconfig", "mode": "oldaskconfig", "kconfig": "Kconfig", "config": "ask/.config", "arch": "x86_64", "expected": "oldaskconfig_expected.json"},
    {"name": "syncconfig", "mode": "syncconfig", "kconfig": "Kconfig", "config": "out/.config", "arch": "riscv64", "nosilentupdate": "1", "expected": "syncconfig_expected.json"},
    {"name": "oldconfig", "mode": "oldconfig", "kconfig": "Kconfig", "config": "refresh/.config", "arch": "x86", "expected": "oldconfig_expected.json"},
    {"name": "allnoconfig", "mode": "allnoconfig", "kconfig": "Kconfig", "config": "none/.config", "arch": "arm64", "expected": "allnoconfig_expected.json"},
    {"name": "allyesconfig", "mode": "allyesconfig", "kconfig": "Kconfig", "config": "yes/.config", "arch": "arm64", "expected": "allyesconfig_expected.json"},
    {"name": "allmodconfig", "mode": "allmodconfig", "kconfig": "Kconfig", "config": "mod/.config", "arch": "arm", "allconfig": "", "expected": "allmodconfig_expected.json"},
    {"name": "alldefconfig", "mode": "alldefconfig", "kconfig": "Kconfig", "config": "build/.config", "arch": "arm64", "expected": "alldefconfig_expected.json"},
    {"name": "randconfig", "mode": "randconfig", "kconfig": "Kconfig", "config": "rand/.config", "arch": "x86_64", "allconfig": "", "seed": "0xC0FFEE", "probability": "15:25", "expected": "randconfig_expected.json"},
    {"name": "defconfig", "mode": "defconfig", "kconfig": "Kconfig", "config": "out/.config", "arch": "arm64", "mode_arg": "arch/arm64/configs/defconfig", "expected": "defconfig_expected.json"},
    {"name": "savedefconfig", "mode": "savedefconfig", "kconfig": "Kconfig", "config": ".config", "arch": "x86_64", "mode_arg": "silent=debug_defconfig", "expected": "savedefconfig_expected.json"},
    {"name": "listnewconfig", "mode": "listnewconfig", "kconfig": "Kconfig", "config": "out/list.config", "arch": "x86_64", "silent": true, "expected": "listnewconfig_expected.json"},
    {"name": "helpnewconfig", "mode": "helpnewconfig", "kconfig": "Kconfig", "config": "out/help.config", "arch": "riscv64", "silent": true, "expected": "helpnewconfig_expected.json"},
    {"name": "olddefconfig", "mode": "olddefconfig", "kconfig": "Kconfig", "config": ".config", "arch": "x86_64", "expected": "olddefconfig_expected.json"},
    {"name": "yes2modconfig", "mode": "yes2modconfig", "kconfig": "Kconfig", "config": "rewrite/.config", "arch": "x86", "expected": "yes2modconfig_expected.json"},
    {"name": "mod2yesconfig", "mode": "mod2yesconfig", "kconfig": "Kconfig", "config": "promote/.config", "arch": "x86", "expected": "mod2yesconfig_expected.json"},
    {"name": "mod2noconfig", "mode": "mod2noconfig", "kconfig": "Kconfig", "config": "demote/.config", "arch": "x86", "expected": "mod2noconfig_expected.json"},
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
    "mode_arg_cases": ["defconfig", "savedefconfig"],
    "silent_request_packet": ["listnewconfig_expected.json", "helpnewconfig_expected.json"],
    "syncconfig_env_packet": ["syncconfig_expected.json"],
    "allconfig_sentinel_packet": [
        "allnoconfig_expected.json",
        "allyesconfig_expected.json",
        "alldefconfig_expected.json",
    ],
    "allconfig_override_packet": ["allmodconfig_expected.json", "randconfig_expected.json"],
    "randconfig_env_packet": ["randconfig_expected.json"],
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
    value = manifest.get("present_surfaces")
    if not isinstance(value, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "present_surfaces"))
        return None
    entry = value.get(key)
    if not isinstance(entry, list):
        issues.append(("INVALID_MANIFEST_SHAPE", key))
        return None
    normalized: list[str] = []
    for item in entry:
        if not isinstance(item, str):
            issues.append(("INVALID_MANIFEST_SHAPE", key))
            return None
        normalized.append(item)
    return normalized

def collect_conf_packet_issues(issues: list[tuple[str, str]], kconfig_cases: object, conf_manifest: object) -> None:
    if not isinstance(kconfig_cases, dict):
        issues.append(("CONF_CASE_PACKET_MISMATCH", "conf_cases"))
        return
    if not isinstance(conf_manifest, dict):
        issues.append(("CONF_MANIFEST_MISMATCH", "root"))
        return
    conf_cases = kconfig_cases.get("conf_cases")
    if conf_cases != EXPECTED_CONF_CASE_DETAILS:
        issues.append(("CONF_CASE_PACKET_MISMATCH", "conf_cases"))
    for key, expected in EXPECTED_CONF_MANIFEST.items():
        if conf_manifest.get(key) != expected:
            issues.append(("CONF_MANIFEST_MISMATCH", key))

def collect_confdata_packet_issues(issues: list[tuple[str, str]], kconfig_cases: object, confdata_manifest: object) -> None:
    if not isinstance(kconfig_cases, dict):
        issues.append(("CONFDATA_CASE_PACKET_MISMATCH", "confdata_cases"))
        return
    if not isinstance(confdata_manifest, dict):
        issues.append(("CONFDATA_MANIFEST_MISMATCH", "root"))
        return
    confdata_cases = kconfig_cases.get("confdata_cases")
    if confdata_cases != EXPECTED_CONFDATA_CASE_DETAILS:
        issues.append(("CONFDATA_CASE_PACKET_MISMATCH", "confdata_cases"))
    for key, expected in EXPECTED_CONFDATA_MANIFEST.items():
        if confdata_manifest.get(key) != expected:
            issues.append(("CONFDATA_MANIFEST_MISMATCH", key))

def collect_genksyms_packet_issues(issues: list[tuple[str, str]], genksyms_cases: object) -> None:
    if genksyms_cases != EXPECTED_GENKSYMS_CASES:
        issues.append(("GENKSYMS_CASE_PACKET_MISMATCH", "cases"))

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
    if not isinstance(manifest, dict):
        issues.append(("INVALID_MANIFEST_SHAPE", "root"))
        return issues

    for marker in REQUIRED_CLOSURE_MARKERS:
        if marker not in closure_text:
            issues.append(("MISSING_CLOSURE_MARKER", marker))
    for marker in FORBIDDEN_CLOSURE_MARKERS:
        if marker in closure_text:
            issues.append(("FORBIDDEN_CLOSURE_MARKER", marker))

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
    if not isinstance(manifest_gaps, list):
        issues.append(("INVALID_MANIFEST_SHAPE", "repo_reality_gaps"))
        return issues
    if manifest_gaps:
        issues.append(("UNEXPECTED_MANIFEST_GAPS", ",".join(str(value) for value in manifest_gaps)))
    for marker in FORBIDDEN_MANIFEST_GAPS:
        if marker in manifest_gaps:
            issues.append(("FORBIDDEN_MANIFEST_GAP", marker))

    review_surfaces = require_manifest_list(issues, manifest, "review_surfaces")
    closure_notes = require_manifest_list(issues, manifest, "closure_notes")
    validators = require_manifest_list(issues, manifest, "validators")
    bootstrap_helpers = require_manifest_list(issues, manifest, "bootstrap_helpers")
    cross_support = require_manifest_list(issues, manifest, "cross_route_support")
    artifact_support = require_manifest_list(issues, manifest, "artifact_support")
    fixdep_support = require_manifest_list(issues, manifest, "fixdep_support")
    fixture_roster = require_manifest_list(issues, manifest, "fixture_roster")
    make_wrappers = require_manifest_list(issues, manifest, "make_wrappers")
    checkers = require_manifest_list(issues, manifest, "checkers")
    bridge_helpers = require_manifest_list(issues, manifest, "bridge_helpers")
    policy = require_manifest_list(issues, manifest, "policy")
    archive_support = require_manifest_list(issues, manifest, "archive_support")

    if review_surfaces is not None:
        for marker in EXPECTED_MANIFEST_REVIEW_SURFACES:
            if marker not in review_surfaces:
                issues.append(("MISSING_MANIFEST_SURFACE", f"review_surfaces:{marker}"))
    if closure_notes is not None:
        for marker in EXPECTED_MANIFEST_CLOSURE_NOTES:
            if marker not in closure_notes:
                issues.append(("MISSING_MANIFEST_SURFACE", f"closure_notes:{marker}"))
    if validators is not None:
        for marker in EXPECTED_MANIFEST_VALIDATORS:
            if marker not in validators:
                issues.append(("MISSING_MANIFEST_SURFACE", f"validators:{marker}"))
    if bootstrap_helpers is not None:
        for marker in EXPECTED_MANIFEST_BOOTSTRAP_HELPERS:
            if marker not in bootstrap_helpers:
                issues.append(("MISSING_MANIFEST_SURFACE", f"bootstrap_helpers:{marker}"))
    if cross_support is not None:
        for marker in EXPECTED_MANIFEST_CROSS_SUPPORT:
            if marker not in cross_support:
                issues.append(("MISSING_MANIFEST_SURFACE", f"cross_route_support:{marker}"))
    if artifact_support is not None:
        for marker in EXPECTED_MANIFEST_ARTIFACT_SUPPORT:
            if marker not in artifact_support:
                issues.append(("MISSING_MANIFEST_SURFACE", f"artifact_support:{marker}"))
    if fixdep_support is not None:
        for marker in EXPECTED_MANIFEST_FIXDEP_SUPPORT:
            if marker not in fixdep_support:
                issues.append(("MISSING_MANIFEST_SURFACE", f"fixdep_support:{marker}"))
    if fixture_roster is not None:
        for marker in EXPECTED_MANIFEST_FIXTURE_ROSTER:
            if marker not in fixture_roster:
                issues.append(("MISSING_MANIFEST_SURFACE", f"fixture_roster:{marker}"))
    if make_wrappers is not None:
        for marker in (
            "make -C zigux phase2-toolchain",
            "make -C zigux phase2-tools",
            "make -C zigux phase2-kconfig",
            "make -C zigux phase2-cross",
            "make -C zigux phase2-genksyms",
            "make -C zigux phase2-fixdep",
            "make -C zigux phase2-validate",
            "make -C zigux phase2",
        ):
            if marker not in make_wrappers:
                issues.append(("MISSING_MANIFEST_SURFACE", f"make_wrappers:{marker}"))
    if checkers is not None:
        for marker in EXPECTED_MANIFEST_CHECKERS:
            if marker not in checkers:
                issues.append(("MISSING_MANIFEST_SURFACE", f"checkers:{marker}"))
    if bridge_helpers is not None:
        for marker in EXPECTED_MANIFEST_BRIDGE_HELPERS:
            if marker not in bridge_helpers:
                issues.append(("MISSING_MANIFEST_SURFACE", f"bridge_helpers:{marker}"))
    if policy is not None:
        for marker in EXPECTED_MANIFEST_POLICY:
            if marker not in policy:
                issues.append(("MISSING_MANIFEST_SURFACE", f"policy:{marker}"))
    if archive_support is not None:
        for marker in EXPECTED_MANIFEST_ARCHIVE_SUPPORT:
            if marker not in archive_support:
                issues.append(("MISSING_MANIFEST_SURFACE", f"archive_support:{marker}"))

    collect_conf_packet_issues(issues, kconfig_cases, conf_manifest)
    collect_confdata_packet_issues(issues, kconfig_cases, confdata_manifest)
    collect_genksyms_packet_issues(issues, genksyms_cases)
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
    closure_text = """# Phase 2 Closure

## Status

- `PHASE2_STATUS=parked`
- `PHASE2_CLOSURE_RESTORE_STATE=docs_plus_manifest`
- manifest: `zigux/tests/fixtures/phase2_tool_manifest.json`

## Current Closure Packet

- `scripts/zigux/check-kconfig-bridge.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/check-phase2-tool-manifest.py`
- `scripts/zigux/check-phase2-artifact-tools-manifest.py`
- `scripts/zigux/check-lane05-local-first-archive-workflow.py`
- `scripts/zigux/check-lane05-local-archive-readme.py`
- `scripts/zigux/check-genksyms-bridge.py`
- `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
- `scripts/zigux/check-phase2-fixdep-gate.py`
- `scripts/zigux/check-fixdep-diff.py`
- `scripts/zigux/install-zig.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `third_party/README.md`
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/genksyms.zig`
- `scripts/zigux/genksyms_version_before_invalid_long_option_test.zig`
- `scripts/zigux/fixdep.zig`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
- `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_artifact_tools_manifest.json`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/tests/fixtures/fixdep/cases.json`
- `zigux/tests/fixtures/genksyms_bridge/cases.json`
- `zigux/tests/fixtures/genksyms_bridge/manifest.json`
- `zigux/tests/fixtures/genksyms_bridge/help_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/minimal_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/long_options_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json`
- `zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json`

## Current Repo-Reality Gaps

The current closure-side packet keeps the fixdep governance and parity checker pair explicit through `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, `zigux/tests/fixtures/fixdep/cases.json`, and `make -C zigux phase2-fixdep`, so same-lane follow-through should stay tied to the toolchain, cross-route, kconfig, manifest-guard, genksyms, make-wrapper, fixdep, and validator packet that the repo still ships directly.

- `PHASE2_CURRENT_GAP_PACKET=`

## Closure Validation

- `python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`
- `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test`
- `python3 scripts/zigux/check-lane05-local-first-archive-workflow.py`
- `python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test`
- `python3 scripts/zigux/check-lane05-local-archive-readme.py`
- `python3 scripts/zigux/install-zig.py --self-test`
- `python3 scripts/zigux/check-phase2-cross.py --self-test`
- `python3 scripts/zigux/check-phase2-cross.py`
- `python3 scripts/zigux/check-kconfig-bridge.py --self-test`
- `python3 scripts/zigux/check-kconfig-bridge.py`
- `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `python3 scripts/zigux/check-phase2-tool-manifest.py --self-test`
- `python3 scripts/zigux/check-phase2-tool-manifest.py`
- `python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test`
- `python3 scripts/zigux/check-phase2-artifact-tools-manifest.py`
- `python3 scripts/zigux/check-genksyms-bridge.py --self-test`
- `python3 scripts/zigux/check-genksyms-bridge.py`
- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test`
- `python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py`
- `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`
- `python3 scripts/zigux/check-phase2-fixdep-gate.py`
- `python3 scripts/zigux/check-fixdep-diff.py --self-test`
- `python3 scripts/zigux/check-fixdep-diff.py`
- `make -C zigux phase2-toolchain`
- `make -C zigux phase2-tools`
- `make -C zigux phase2-kconfig`
- `make -C zigux phase2-cross`
- `make -C zigux phase2-genksyms`
- `make -C zigux phase2-fixdep`
- `make -C zigux phase2-validate`
- `make -C zigux phase2`
"""
    workflow_lines = ["name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES]
    makefile_lines = [
        "PYTHON ?= python3",
        "ZIG ?= zig",
        "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
        "ZIGUX_ROOT := ..",
        *REQUIRED_MAKEFILE_LINES,
    ]
    manifest = {
        "phase": "Phase 2",
        "status": "active",
        "scope": "current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet",
        "workflow": ".github/workflows/zigux-bootstrap.yml",
        "present_surfaces": {
            "review_surfaces": [
                "Documentation/zigux/README.md",
                "Documentation/zigux/phase2-closure.md",
                "Documentation/zigux/review-checklist.md",
                "zigux/tests/README.md",
            ],
            "closure_notes": [
                "Documentation/zigux/phase2-closure.md",
                "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
            ],
            "validators": [
                "scripts/zigux/validate-phase2.py",
                "scripts/zigux/validate-phase2-closure.py",
            ],
            "checkers": list(EXPECTED_MANIFEST_CHECKERS),
            "bootstrap_helpers": list(EXPECTED_MANIFEST_BOOTSTRAP_HELPERS),
            "bridge_helpers": list(EXPECTED_MANIFEST_BRIDGE_HELPERS),
            "policy": list(EXPECTED_MANIFEST_POLICY),
            "archive_support": list(EXPECTED_MANIFEST_ARCHIVE_SUPPORT),
            "make_wrappers": [
                "zigux/Makefile",
                "make -C zigux phase2-toolchain",
                "make -C zigux phase2-tools",
                "make -C zigux phase2-kconfig",
                "make -C zigux phase2-cross",
                "make -C zigux phase2-genksyms",
                "make -C zigux phase2-fixdep",
                "make -C zigux phase2-validate",
                "make -C zigux phase2",
            ],
            "cross_route_support": list(EXPECTED_MANIFEST_CROSS_SUPPORT),
            "artifact_support": list(EXPECTED_MANIFEST_ARTIFACT_SUPPORT),
            "fixdep_support": list(EXPECTED_MANIFEST_FIXDEP_SUPPORT),
            "fixture_roster": list(EXPECTED_MANIFEST_FIXTURE_ROSTER),
        },
        "repo_reality_gaps": [],
        "notes": [
            "Current Phase 2 repo-tooling evidence is anchored in the shipped toolchain checker, the returned local-first archive workflow and archive README contract checkers, the shipped toolchain-pinning and pin-scope guards, the returned installer helper, direct cross-route checker, docs-shared-reminder checker, required make-route guard, kbuild routes checker, the live kconfig bridge checker and fixture roster, the dedicated genksyms selftest-alignment guard, the manifest-backed genksyms bridge checker plus its expanded expected and process-output fixture packet, the standalone invalid-long-option version-side-effect proof, the fixdep governance and parity checker pair, and the restored tranche-closure note.",
            "Keep the directly readable validator pair explicit through scripts/zigux/validate-phase2.py and scripts/zigux/validate-phase2-closure.py instead of leaving the closure-side replay packet implied only in prose.",
            "Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-fixdep, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.",
            "Keep the dedicated manifest guards and the dedicated genksyms selftest-alignment guard explicit through scripts/zigux/check-phase2-tool-manifest.py, scripts/zigux/check-phase2-artifact-tools-manifest.py, and scripts/zigux/check-phase2-genksyms-selftest-alignment.py so Phase 2 packet drift fails closed beside the other reminder checkers.",
            "Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, repo-local pinned archive payload, direct cross-route checker, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the standalone invalid-long-option version-side-effect proof, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket.",
        ],
    }
    kconfig_cases = {"conf_cases": list(EXPECTED_CONF_CASE_DETAILS), "confdata_cases": list(EXPECTED_CONFDATA_CASE_DETAILS)}

    write_text(resolve(root, WORKFLOW_REL), "\n".join(workflow_lines) + "\n")
    write_text(resolve(root, PHASE2_CLOSURE_REL), closure_text)
    write_text(resolve(root, PHASE2_BOOTSTRAP_NOTES_REL), "present\n")
    write_text(resolve(root, PHASE2_VALIDATE_REL), "present\n")
    write_text(resolve(root, PHASE2_CLOSURE_VALIDATE_REL), "present\n")
    write_text(resolve(root, LOCAL_ARCHIVE_WORKFLOW_CHECKER_REL), "present\n")
    write_text(resolve(root, LOCAL_ARCHIVE_README_CHECKER_REL), "present\n")
    write_text(resolve(root, INSTALL_ZIG_REL), "present\n")
    write_text(resolve(root, TOOLCHAIN_CHECKER_REL), "present\n")
    write_text(resolve(root, PINNING_CHECKER_REL), "present\n")
    write_text(resolve(root, PIN_SCOPE_CHECKER_REL), "present\n")
    write_text(resolve(root, KBUILD_CHECKER_REL), "present\n")
    write_text(resolve(root, KCONFIG_BRIDGE_CHECKER_REL), "present\n")
    write_text(resolve(root, KCONFIG_ALIGNMENT_REL), "present\n")
    write_text(resolve(root, TESTS_ALIGNMENT_REL), "present\n")
    write_text(resolve(root, CROSS_CHECKER_REL), "present\n")
    write_text(resolve(root, CROSS_ALIGNMENT_REL), "present\n")
    write_text(resolve(root, DOCS_REMINDER_CHECKER_REL), "present\n")
    write_text(resolve(root, REQUIRED_ROUTES_CHECKER_REL), "present\n")
    write_text(resolve(root, TOOL_MANIFEST_CHECKER_REL), "present\n")
    write_text(resolve(root, ARTIFACT_MANIFEST_CHECKER_REL), "present\n")
    write_text(resolve(root, GENKSYMS_CHECKER_REL), "present\n")
    write_text(resolve(root, GENKSYMS_SELFTEST_ALIGNMENT_REL), "present\n")
    write_text(resolve(root, FIXDEP_GATE_REL), "present\n")
    write_text(resolve(root, FIXDEP_DIFF_REL), "present\n")
    write_text(resolve(root, TOOLCHAIN_POLICY_REL), "present\n")
    write_text(resolve(root, CONF_BRIDGE_REL), "present\n")
    write_text(resolve(root, CONFDATA_BRIDGE_REL), "present\n")
    write_text(resolve(root, GENKSYMS_BRIDGE_REL), "present\n")
    write_text(resolve(root, GENKSYMS_VERSION_PROOF_REL), "present\n")
    write_text(resolve(root, FIXDEP_BRIDGE_REL), "present\n")
    write_text(resolve(root, ARCHIVE_README_REL), "present\n")
    write_text(resolve(root, ARCHIVE_PAYLOAD_REL), "present\n")
    write_text(resolve(root, MAKEFILE_REL), "\n".join(makefile_lines) + "\n")
    write_text(resolve(root, MANIFEST_REL), json.dumps(manifest, indent=2) + "\n")
    write_text(resolve(root, ARTIFACT_MANIFEST_REL), "{}\n")
    write_text(resolve(root, CROSS_FIXTURE_REL), "{}\n")
    write_text(resolve(root, FIXDEP_CASES_REL), "{}\n")
    write_text(resolve(root, CONF_MANIFEST_REL), json.dumps(EXPECTED_CONF_MANIFEST, indent=2) + "\n")
    write_text(resolve(root, CONFDATA_MANIFEST_REL), json.dumps(EXPECTED_CONFDATA_MANIFEST, indent=2) + "\n")
    write_text(resolve(root, KCONFIG_CASES_REL), json.dumps(kconfig_cases, indent=2) + "\n")
    write_text(resolve(root, GENKSYMS_CASES_REL), json.dumps(EXPECTED_GENKSYMS_CASES, indent=2) + "\n")
    write_text(resolve(root, GENKSYMS_MANIFEST_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_HELP_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_MINIMAL_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_DEBUG_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_LONG_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_ABBREVIATED_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_QUIET_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_TERMINATOR_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_POSITIONAL_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_LONE_DASH_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_ABBREVIATED_VERSION_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_AMBIGUOUS_LONG_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_INVALID_OPTION_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_MISSING_LONG_DUMP_TYPES_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_MISSING_LONG_REFERENCE_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_MISSING_REFERENCE_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_TOO_MANY_REFERENCE_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_UNSUPPORTED_LONG_REL), "{}\n")
    write_text(resolve(root, GENKSYMS_UNEXPECTED_LONG_HELP_REL), "{}\n")

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

def duplicate_exact_line(text: str, marker: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == marker:
            lines.insert(index + 1, line)
            return "\n".join(lines) + "\n"
    raise AssertionError(f"marker line not found: {marker}")

def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_validate_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        path = resolve(root, PHASE2_CLOSURE_REL)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), REQUIRED_CLOSURE_MARKERS[0]), encoding="utf-8")
        assert ("MISSING_CLOSURE_MARKER", REQUIRED_CLOSURE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, PHASE2_CLOSURE_REL)
        path.write_text(replace_once(path.read_text(encoding="utf-8"), "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`"), encoding="utf-8")
        assert ("MISSING_CLOSURE_MARKER", "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, WORKFLOW_REL)
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[0], "run: python3 scripts/zigux/other.py"), encoding="utf-8")
        assert ("MISSING_WORKFLOW_LINE", REQUIRED_WORKFLOW_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, WORKFLOW_REL)
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test", "run: python3 scripts/zigux/broken.py"), encoding="utf-8")
        assert ("MISSING_WORKFLOW_LINE", "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, WORKFLOW_REL)
        path.write_text(duplicate_exact_line(path.read_text(encoding="utf-8"), REQUIRED_WORKFLOW_LINES[0]), encoding="utf-8")
        assert ("DUPLICATE_WORKFLOW_LINE", f"{REQUIRED_WORKFLOW_LINES[0]}:count=2") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MAKEFILE_REL)
        path.write_text(replace_exact_line(path.read_text(encoding="utf-8"), REQUIRED_MAKEFILE_LINES[0], "# removed"), encoding="utf-8")
        assert ("MISSING_MAKEFILE_LINE", REQUIRED_MAKEFILE_LINES[0]) in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_REL)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["archive_support"] = []
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_SURFACE", "archive_support:third_party/README.md") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_REL)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["artifact_support"] = []
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_SURFACE", "artifact_support:scripts/zigux/check-phase2-artifact-tools-manifest.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_REL)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["fixdep_support"] = []
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_SURFACE", "fixdep_support:scripts/zigux/check-phase2-fixdep-gate.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_REL)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["bridge_helpers"] = ["scripts/zigux/genksyms.zig"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_SURFACE", "bridge_helpers:scripts/zigux/kconfig/conf_bridge.zig") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, MANIFEST_REL)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["checkers"] = [checker for checker in payload["present_surfaces"]["checkers"] if checker != "scripts/zigux/check-phase2-genksyms-selftest-alignment.py"]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("MISSING_MANIFEST_SURFACE", "checkers:scripts/zigux/check-phase2-genksyms-selftest-alignment.py") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, KCONFIG_CASES_REL)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["conf_cases"][11]["silent"] = False
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("CONF_CASE_PACKET_MISMATCH", "conf_cases") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, CONF_MANIFEST_REL)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["case_count"] = 15
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("CONF_MANIFEST_MISMATCH", "case_count") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, KCONFIG_CASES_REL)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["confdata_cases"][0]["expected"] = "broken_expected.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("CONFDATA_CASE_PACKET_MISMATCH", "confdata_cases") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, CONFDATA_MANIFEST_REL)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["case_count"] = 14
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("CONFDATA_MANIFEST_MISMATCH", "case_count") in collect_issues(root)
        checks_run += 1

        build_self_test_root(root)
        path = resolve(root, GENKSYMS_CASES_REL)
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload[0]["expected_file"] = "other.json"
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        assert ("GENKSYMS_CASE_PACKET_MISMATCH", "cases") in collect_issues(root)
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
