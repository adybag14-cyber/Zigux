#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ".github/workflows/zigux-bootstrap.yml"
MAKEFILE = "zigux/Makefile"
GENKSYMS_DUAL_IMPLEMENTATION_SURVEY = "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md"
FIXDEP_DUAL_IMPLEMENTATION_SURVEY = "Documentation/zigux/phase2-fixdep-dual-implementation-survey.md"
GENKSYMS_VERSION_SIDE_EFFECT_TEST = "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig"
GENKSYMS_VERSION_SIDE_EFFECT_AMBIGUOUS_TEST = "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig"
GENKSYMS_MANIFEST_FIXTURE = "zigux/tests/fixtures/genksyms_bridge/manifest.json"
GENKSYMS_PROCESS_OUTPUT_FIXTURES = (
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
KCONFIG_CONFDATA_REPLAY_MARKERS = (
    'compile_tool(zig, CONFDATA_BRIDGE, confdata_exe)',
    'cmd = [str(confdata_exe), str(FIXTURE_DIR / str(case["input"]))]',
    'actual.write_text(run(cmd, cwd=str(ROOT), capture_output=True).stdout, encoding="utf-8", newline="\\n")',
    'repeat.write_text(run(cmd, cwd=str(ROOT), capture_output=True).stdout, encoding="utf-8", newline="\\n")',
    'check_repeatable_json_output(FIXTURE_DIR / str(case["expected"]), actual, repeat)',
)
KCONFIG_BRIDGE_VALIDATOR_PATH = "scripts/zigux/check-kconfig-bridge.py"
KCONFIG_CONF_EXPECTED_FIXTURES = (
    "zigux/tests/fixtures/kconfig_bridge/oldaskconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/syncconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/oldconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/allnoconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/allyesconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/allmodconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/alldefconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/randconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/defconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/savedefconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/listnewconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/helpnewconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/olddefconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/yes2modconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/mod2yesconfig_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/mod2noconfig_expected.json",
)
KCONFIG_CONFDATA_INPUT_FIXTURES = (
    "zigux/tests/fixtures/kconfig_bridge/sample.config",
    "zigux/tests/fixtures/kconfig_bridge/escaped_strings.config",
    "zigux/tests/fixtures/kconfig_bridge/escaped_control_sequences.config",
    "zigux/tests/fixtures/kconfig_bridge/trailing_escaped_backslash.config",
    "zigux/tests/fixtures/kconfig_bridge/sample_crlf.config",
    "zigux/tests/fixtures/kconfig_bridge/explicit_n_tristate.config",
    "zigux/tests/fixtures/kconfig_bridge/final_trailing_carriage_return.config",
    "zigux/tests/fixtures/kconfig_bridge/final_unterminated_unset_comment.config",
    "zigux/tests/fixtures/kconfig_bridge/uppercase_tristate.config",
    "zigux/tests/fixtures/kconfig_bridge/non_config_lines.config",
    "zigux/tests/fixtures/kconfig_bridge/empty_config_symbol_names.config",
    "zigux/tests/fixtures/kconfig_bridge/malformed_unset_comment_tokens.config",
    "zigux/tests/fixtures/kconfig_bridge/last_state_transitions.config",
    "zigux/tests/fixtures/kconfig_bridge/duplicate_assignments.config",
    "zigux/tests/fixtures/kconfig_bridge/duplicate_malformed_quoted_assignment.config",
    "zigux/tests/fixtures/kconfig_bridge/explicit_empty_assignments.config",
)

KCONFIG_CONFDATA_EXPECTED_FIXTURES = (
    "zigux/tests/fixtures/kconfig_bridge/sample_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/escaped_strings_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/escaped_control_sequences_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/trailing_escaped_backslash_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/sample_crlf_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/explicit_n_tristate_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/final_trailing_carriage_return_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/final_unterminated_unset_comment_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/uppercase_tristate_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/non_config_lines_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/empty_config_symbol_names_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/malformed_unset_comment_tokens_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/last_state_transitions_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/duplicate_assignments_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/duplicate_malformed_quoted_assignment_expected.json",
    "zigux/tests/fixtures/kconfig_bridge/explicit_empty_assignments_expected.json",
)
FIXDEP_FIXTURE_FILES = (
    "zigux/tests/fixtures/fixdep/dep:colon.so",
    "zigux/tests/fixtures/fixdep/dep\\ name.rmeta",
    "zigux/tests/fixtures/fixdep/escaped\\ space-config.h",
    "zigux/tests/fixtures/fixdep/sample-config.h",
    "zigux/tests/fixtures/fixdep/sample.c",
    "zigux/tests/fixtures/fixdep/sample.d",
    "zigux/tests/fixtures/fixdep/sample.h",
    "zigux/tests/fixtures/fixdep/sample.rmeta",
    "zigux/tests/fixtures/fixdep/sample2-config.h",
    "zigux/tests/fixtures/fixdep/sample2.c",
    "zigux/tests/fixtures/fixdep/sample2.so",
    "zigux/tests/fixtures/fixdep/sample_comment_continuation.d",
    "zigux/tests/fixtures/fixdep/sample_comment_continuation_dep.so",
    "zigux/tests/fixtures/fixdep/sample_comment_continuation_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_comment_continuation_source.c",
    "zigux/tests/fixtures/fixdep/sample_comment_continuation_source.rmeta",
    "zigux/tests/fixtures/fixdep/sample_comment_only.d",
    "zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt",
    "zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_concatenated.d",
    "zigux/tests/fixtures/fixdep/sample_concatenated_dep.h",
    "zigux/tests/fixtures/fixdep/sample_concatenated_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_concatenated_source.c",
    "zigux/tests/fixtures/fixdep/sample_concatenated_temp.c",
    "zigux/tests/fixtures/fixdep/sample_concatenated_temp_dep.h",
    "zigux/tests/fixtures/fixdep/sample_dependency_continuation.d",
    "zigux/tests/fixtures/fixdep/sample_dependency_continuation_dep.so",
    "zigux/tests/fixtures/fixdep/sample_dependency_continuation_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.c",
    "zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.rmeta",
    "zigux/tests/fixtures/fixdep/sample_double_backslash_comment.d",
    "zigux/tests/fixtures/fixdep/sample_double_backslash_comment_expected.stderr.txt",
    "zigux/tests/fixtures/fixdep/sample_double_backslash_comment_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_double_backslash_comment_source.rmeta",
    "zigux/tests/fixtures/fixdep/sample_escaped_colon.d",
    "zigux/tests/fixtures/fixdep/sample_escaped_colon_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c",
    "zigux/tests/fixtures/fixdep/sample_escaped_colon_source.rmeta",
    "zigux/tests/fixtures/fixdep/sample_escaped_space.d",
    "zigux/tests/fixtures/fixdep/sample_escaped_space_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_escaped_space_source.c",
    "zigux/tests/fixtures/fixdep/sample_escaped_space_source.rmeta",
    "zigux/tests/fixtures/fixdep/sample_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_missing_dep.d",
    "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt",
    "zigux/tests/fixtures/fixdep/sample_missing_dep_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_missing_dep_source.c",
    "zigux/tests/fixtures/fixdep/sample_multi_target.d",
    "zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt",
    "zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt",
    "zigux/tests/fixtures/fixdep/sample_output_write_expected.txt",
    "zigux/tests/fixtures/fixdep/shared#config.h",
    "zigux/tests/fixtures/fixdep/shared:config.h",
)
ARCHIVE_PAYLOAD_PATH = "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"
ARCHIVE_PARTS_MANIFEST_PATH = "third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz.parts/manifest.json"
ARCHIVE_SUPPORT_ALTERNATIVES = (
    ARCHIVE_PAYLOAD_PATH,
    ARCHIVE_PARTS_MANIFEST_PATH,
)

REQUIRED_PATHS = (
    "Documentation/zigux/README.md",
    "Documentation/zigux/phase2-closure.md",
    GENKSYMS_DUAL_IMPLEMENTATION_SURVEY,
    FIXDEP_DUAL_IMPLEMENTATION_SURVEY,
    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/README.md",
    "scripts/zigux/check-zig-toolchain.py",
    KCONFIG_BRIDGE_VALIDATOR_PATH,
    "scripts/zigux/check-phase2-kbuild-routes.py",
    "scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "scripts/zigux/check-phase2-tests-readme-alignment.py",
    "scripts/zigux/check-phase2-cross.py",
    "scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "scripts/zigux/check-phase2-toolchain-pinning.py",
    "scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "scripts/zigux/check-phase2-required-make-routes.py",
    "scripts/zigux/check-phase2-bootstrap-workflow-routes.py",
    "scripts/zigux/check-phase2-docs-shared-reminder.py",
    "scripts/zigux/check-phase2-tool-manifest.py",
    "scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "scripts/zigux/check-genksyms-bridge.py",
    "scripts/zigux/check-phase2-fixdep-gate.py",
    "scripts/zigux/check-fixdep-diff.py",
    "scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "scripts/zigux/check-lane05-local-archive-readme.py",
    "scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/genksyms.zig",
    GENKSYMS_VERSION_SIDE_EFFECT_TEST,
    GENKSYMS_VERSION_SIDE_EFFECT_AMBIGUOUS_TEST,
    "scripts/zigux/fixdep.zig",
    "scripts/zigux/zig-toolchain-policy.json",
    "scripts/zigux/artifact_diff.py",
    "third_party/README.md",
    "zigux/tests/README.md",
    "zigux/tests/fixtures/kconfig_bridge/cases.json",
    "zigux/tests/fixtures/kconfig_bridge/conf_manifest.json",
    "zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json",
    *KCONFIG_CONF_EXPECTED_FIXTURES,
    *KCONFIG_CONFDATA_INPUT_FIXTURES,
    *KCONFIG_CONFDATA_EXPECTED_FIXTURES,
    "zigux/tests/fixtures/genksyms_bridge/cases.json",
    "zigux/tests/fixtures/genksyms_bridge/help_expected.json",
    GENKSYMS_MANIFEST_FIXTURE,
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
    *GENKSYMS_PROCESS_OUTPUT_FIXTURES,
    "zigux/tests/fixtures/phase2_tool_manifest.json",
    "zigux/tests/fixtures/phase2_artifact_tools_manifest.json",
    "zigux/tests/fixtures/phase2_cross_targets.json",
    "zigux/tests/fixtures/fixdep/cases.json",
    *FIXDEP_FIXTURE_FILES,
    "scripts/zigux/validate-phase2-closure.py",
    MAKEFILE,
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
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "run: python3 scripts/zigux/check-phase2-fixdep-gate.py",
    "run: python3 scripts/zigux/check-fixdep-diff.py --self-test",
    "run: python3 scripts/zigux/check-fixdep-diff.py",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pinning.py",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py --self-test",
    "run: python3 scripts/zigux/check-phase2-toolchain-pin-scope.py",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-required-make-routes.py",
    "run: make -C zigux phase2-toolchain",
    "run: python3 scripts/zigux/check-kconfig-bridge.py --self-test",
    "run: python3 scripts/zigux/check-kconfig-bridge.py",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kconfig-allconfig-helper-packet.py",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py --self-test",
    "run: python3 scripts/zigux/check-phase2-kbuild-routes.py",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tests-readme-alignment.py",
    "run: python3 scripts/zigux/check-phase2-cross.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross.py",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py --self-test",
    "run: python3 scripts/zigux/check-phase2-docs-shared-reminder.py",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-tool-manifest.py",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py --self-test",
    "run: python3 scripts/zigux/check-phase2-artifact-tools-manifest.py",
    "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test",
    "run: python3 scripts/zigux/check-genksyms-bridge.py",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test",
    "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py",
    "run: make -C zigux phase2-genksyms",
    "run: make -C zigux phase2-fixdep",
    "run: make -C zigux phase2-tools",
    "run: make -C zigux phase2-kconfig",
    "run: make -C zigux phase2-cross",
    "run: make -C zigux phase2-validate",
    "run: python3 scripts/zigux/validate-phase2.py",
)

DISALLOWED_WORKFLOW_LINES: tuple[str, ...] = ()

REQUIRED_PHASE2_PHONY_LINE = ".PHONY: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep phase2-validate phase2"
REQUIRED_PHASE2_PHONY_TARGETS = set(REQUIRED_PHASE2_PHONY_LINE.split(":", 1)[1].strip().split())

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
    "phase2-kconfig: phase2-toolchain",
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
    "phase2-genksyms: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/genksyms.zig",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py",
    "phase2-fixdep: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-phase2-fixdep-gate.py",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py --self-test",
    "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-fixdep-diff.py",
    "cd $(ZIGUX_ROOT) && $(ZIG) test scripts/zigux/fixdep.zig",
    "phase2-validate: phase2-toolchain phase2-tools phase2-kconfig phase2-cross phase2-genksyms phase2-fixdep",
    "phase2: phase2-validate",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tests-readme-alignment.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-tool-manifest.py",
    "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/validate-phase2-closure.py",
)


def read_text(root: Path, rel: str) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


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


def phony_targets_present(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(".PHONY:"):
            _, suffix = stripped.split(":", 1)
            targets.update(token for token in suffix.strip().split() if token)
    return targets


def collect_archive_support_issues(root: Path) -> list[tuple[str, str]]:
    if any((root / rel).exists() for rel in ARCHIVE_SUPPORT_ALTERNATIVES):
        return []
    return [(
        "MISSING_REQUIRED_ARCHIVE_SUPPORT",
        " or ".join(ARCHIVE_SUPPORT_ALTERNATIVES),
    )]


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(root, WORKFLOW)
    makefile_text = read_text(root, MAKEFILE)

    for marker in REQUIRED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_LINE", f"{marker}:count={count}"))

    for marker in DISALLOWED_WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count != 0:
            issues.append(("UNEXPECTED_WORKFLOW_LINE", f"{marker}:count={count}"))

    if not REQUIRED_PHASE2_PHONY_TARGETS.issubset(phony_targets_present(makefile_text)):
        issues.append(("MISSING_MAKEFILE_LINE", REQUIRED_PHASE2_PHONY_LINE))

    for marker in REQUIRED_MAKEFILE_LINES:
        count = count_exact_lines(makefile_text, marker)
        if count == 0:
            issues.append(("MISSING_MAKEFILE_LINE", marker))
        elif count != 1:
            issues.append(("DUPLICATE_MAKEFILE_LINE", f"{marker}:count={count}"))

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            issues.append(("MISSING_REQUIRED_PATH", rel))

    kconfig_bridge_text = read_text(root, KCONFIG_BRIDGE_VALIDATOR_PATH)
    for marker in KCONFIG_CONFDATA_REPLAY_MARKERS:
        count = count_exact_lines(kconfig_bridge_text, marker)
        if count == 0:
            issues.append(("MISSING_KCONFIG_CONFDATA_REPLAY_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_KCONFIG_CONFDATA_REPLAY_MARKER", f"{marker}:count={count}"))

    issues.extend(collect_archive_support_issues(root))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_VALIDATION=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_self_test_root(root: Path) -> None:
    for child in root.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    write_text(root, WORKFLOW, "\n".join(("name: zigux-bootstrap", *REQUIRED_WORKFLOW_LINES)) + "\n")
    write_text(
        root,
        MAKEFILE,
        "\n".join(
            (
                "PYTHON ?= python3",
                "ZIG ?= zig",
                "PHASE2_SCRIPT_ROOT := ../scripts/zigux",
                "ZIGUX_ROOT := ..",
                "",
                REQUIRED_PHASE2_PHONY_LINE,
                *REQUIRED_MAKEFILE_LINES,
            )
        ) + "\n",
    )
    for rel in REQUIRED_PATHS:
        if rel != MAKEFILE:
            write_text(root, rel, "present\n")
    write_text(
        root,
        KCONFIG_BRIDGE_VALIDATOR_PATH,
        "\n".join(KCONFIG_CONFDATA_REPLAY_MARKERS) + "\n",
    )
    write_text(root, ARCHIVE_PAYLOAD_PATH, "archive\n")


def expect_issue(root: Path, expected: tuple[str, str]) -> None:
    issues = collect_issues(root)
    assert expected in issues, (expected, issues)


def expect_required_file_abort(root: Path, rel: str) -> None:
    try:
        collect_issues(root)
    except SystemExit as exc:
        assert f"required file missing: {root / rel}" in str(exc)
    else:
        raise AssertionError(f"missing file did not abort: {rel}")


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(REQUIRED_WORKFLOW_LINES)
        + len(REQUIRED_WORKFLOW_LINES)
        + len(DISALLOWED_WORKFLOW_LINES)
        + 1
        + len(REQUIRED_MAKEFILE_LINES)
        + len(REQUIRED_MAKEFILE_LINES)
        + len([rel for rel in REQUIRED_PATHS[:-1] if rel != KCONFIG_BRIDGE_VALIDATOR_PATH])
        + len(KCONFIG_CONFDATA_REPLAY_MARKERS)
        + len(KCONFIG_CONFDATA_REPLAY_MARKERS)
        + 3
        + 2
    )
    checks = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_validate_") as tmp_dir:
        root = Path(tmp_dir)

        build_self_test_root(root)
        assert collect_issues(root) == []
        checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            write_text(root, WORKFLOW, replace_exact_line(read_text(root, WORKFLOW), marker, "run: python3 scripts/zigux/other.py"))
            expect_issue(root, ("MISSING_WORKFLOW_LINE", marker))
            checks += 1

        for marker in REQUIRED_WORKFLOW_LINES:
            build_self_test_root(root)
            write_text(root, WORKFLOW, duplicate_exact_line(read_text(root, WORKFLOW), marker))
            expect_issue(root, ("DUPLICATE_WORKFLOW_LINE", f"{marker}:count=2"))
            checks += 1

        for marker in DISALLOWED_WORKFLOW_LINES:
            build_self_test_root(root)
            write_text(root, WORKFLOW, read_text(root, WORKFLOW) + marker + "\n")
            expect_issue(root, ("UNEXPECTED_WORKFLOW_LINE", f"{marker}:count=1"))
            checks += 1

        build_self_test_root(root)
        write_text(root, MAKEFILE, replace_exact_line(read_text(root, MAKEFILE), REQUIRED_PHASE2_PHONY_LINE, "# removed"))
        expect_issue(root, ("MISSING_MAKEFILE_LINE", REQUIRED_PHASE2_PHONY_LINE))
        checks += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            write_text(root, MAKEFILE, replace_exact_line(read_text(root, MAKEFILE), marker, "# removed"))
            expect_issue(root, ("MISSING_MAKEFILE_LINE", marker))
            checks += 1

        for marker in REQUIRED_MAKEFILE_LINES:
            build_self_test_root(root)
            write_text(root, MAKEFILE, duplicate_exact_line(read_text(root, MAKEFILE), marker))
            expect_issue(root, ("DUPLICATE_MAKEFILE_LINE", f"{marker}:count=2"))
            checks += 1

        for rel in REQUIRED_PATHS[:-1]:
            if rel == KCONFIG_BRIDGE_VALIDATOR_PATH:
                continue
            build_self_test_root(root)
            (root / rel).unlink()
            expect_issue(root, ("MISSING_REQUIRED_PATH", rel))
            checks += 1

        for marker in KCONFIG_CONFDATA_REPLAY_MARKERS:
            build_self_test_root(root)
            write_text(
                root,
                KCONFIG_BRIDGE_VALIDATOR_PATH,
                replace_exact_line(read_text(root, KCONFIG_BRIDGE_VALIDATOR_PATH), marker, "# removed"),
            )
            expect_issue(root, ("MISSING_KCONFIG_CONFDATA_REPLAY_MARKER", marker))
            checks += 1

        for marker in KCONFIG_CONFDATA_REPLAY_MARKERS:
            build_self_test_root(root)
            write_text(
                root,
                KCONFIG_BRIDGE_VALIDATOR_PATH,
                duplicate_exact_line(read_text(root, KCONFIG_BRIDGE_VALIDATOR_PATH), marker),
            )
            expect_issue(root, ("DUPLICATE_KCONFIG_CONFDATA_REPLAY_MARKER", f"{marker}:count=2"))
            checks += 1

        for rel in (WORKFLOW, MAKEFILE, KCONFIG_BRIDGE_VALIDATOR_PATH):
            build_self_test_root(root)
            (root / rel).unlink()
            expect_required_file_abort(root, rel)
            checks += 1

        build_self_test_root(root)
        (root / ARCHIVE_PAYLOAD_PATH).unlink()
        write_text(root, ARCHIVE_PARTS_MANIFEST_PATH, "present\n")
        assert collect_issues(root) == []
        checks += 1

        build_self_test_root(root)
        (root / ARCHIVE_PAYLOAD_PATH).unlink()
        expect_issue(
            root,
            ("MISSING_REQUIRED_ARCHIVE_SUPPORT", " or ".join(ARCHIVE_SUPPORT_ALTERNATIVES)),
        )
        checks += 1

    assert checks == expected_case_count
    print("PHASE2_VALIDATION_SELF_TEST=pass")
    print(f"PHASE2_VALIDATION_SELF_TEST_CASE_COUNT={checks}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the current Phase 2 toolchain, kbuild, kconfig, genksyms, and fixdep packet.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_VALIDATION=pass")
    print(f"PHASE2_VALIDATION_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}")
    print(f"PHASE2_VALIDATION_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS) + 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())