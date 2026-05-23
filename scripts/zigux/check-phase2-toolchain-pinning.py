#!/usr/bin/env python3
"""Guard the current directly readable Phase 2 toolchain pinning packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
WORKFLOW = ROOT / ".github" / "workflows" / "zigux-bootstrap.yml"
POLICY_PATH = ROOT / "scripts" / "zigux" / "zig-toolchain-policy.json"
THIRD_PARTY_README = ROOT / "third_party" / "README.md"
BOOTSTRAP_NOTES = ROOT / "Documentation" / "zigux" / "phase2-toolchain-bootstrap-notes.md"
PHASE2_CLOSURE = ROOT / "Documentation" / "zigux" / "phase2-closure.md"
REVIEW_CHECKLIST = ROOT / "Documentation" / "zigux" / "review-checklist.md"
SCRIPTS_README = ROOT / "scripts" / "zigux" / "README.md"
TESTS_README = ROOT / "zigux" / "tests" / "README.md"
TOOL_MANIFEST_PATH = ROOT / "zigux" / "tests" / "fixtures" / "phase2_tool_manifest.json"
EXPECTED_ARCHIVE_SIZES = {"x86_64-linux": 58_159_088}
ARCHIVE_README_REQUIRED_MARKER_COUNT = 10

SURFACE_PATHS = (
    ROOT / "scripts" / "zigux" / "check-zig-toolchain.py",
    ROOT / "scripts" / "zigux" / "install-zig.py",
    ROOT / "scripts" / "zigux" / "check-lane05-local-first-archive-workflow.py",
    ROOT / "scripts" / "zigux" / "check-lane05-local-archive-readme.py",
    ROOT / "scripts" / "zigux" / "check-lane05-install-zig-archive-verification.py",
    ROOT / "scripts" / "zigux" / "stage-pinned-zig-archive.py",
    ROOT / "scripts" / "zigux" / "check-lane05-stage-helper-contract.py",
    ROOT / "scripts" / "zigux" / "check-lane05-stage-helper-selftest.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pinning.py",
    ROOT / "scripts" / "zigux" / "check-phase2-toolchain-pin-scope.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kbuild-routes.py",
    ROOT / "scripts" / "zigux" / "check-kconfig-bridge.py",
    ROOT / "scripts" / "zigux" / "check-phase2-kconfig-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-genksyms-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tests-readme-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-cross-selftest-alignment.py",
    ROOT / "scripts" / "zigux" / "check-phase2-required-make-routes.py",
    ROOT / "scripts" / "zigux" / "check-phase2-docs-shared-reminder.py",
    ROOT / "scripts" / "zigux" / "check-phase2-tool-manifest.py",
    ROOT / "scripts" / "zigux" / "check-phase2-artifact-tools-manifest.py",
    ROOT / "scripts" / "zigux" / "artifact_diff.py",
    ROOT / "scripts" / "zigux" / "check-genksyms-bridge.py",
    ROOT / "scripts" / "zigux" / "check-phase2-fixdep-gate.py",
    ROOT / "scripts" / "zigux" / "check-fixdep-diff.py",
    ROOT / "scripts" / "zigux" / "validate-phase2.py",
    ROOT / "scripts" / "zigux" / "validate-phase2-closure.py",
    ROOT / "scripts" / "zigux" / "kconfig" / "conf_bridge.zig",
    ROOT / "scripts" / "zigux" / "kconfig" / "confdata_bridge.zig",
    ROOT / "scripts" / "zigux" / "genksyms.zig",
    ROOT / "scripts" / "zigux" / "genksyms_version_before_invalid_long_option_test.zig",
    ROOT / "scripts" / "zigux" / "genksyms_version_before_ambiguous_long_option_test.zig",
    ROOT / "scripts" / "zigux" / "fixdep.zig",
    THIRD_PARTY_README,
    ROOT / "zigux" / "Makefile",
    POLICY_PATH,
    BOOTSTRAP_NOTES,
    PHASE2_CLOSURE,
    REVIEW_CHECKLIST,
    SCRIPTS_README,
    TESTS_README,
    TOOL_MANIFEST_PATH,
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_artifact_tools_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "phase2_cross_targets.json",
    ROOT / "zigux" / "tests" / "fixtures" / "fixdep" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "conf_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "kconfig_bridge" / "confdata_manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "cases.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "help_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "manifest.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "minimal_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "debug_reference_types_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "long_options_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "abbreviated_long_options_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "quiet_overrides_warning_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "explicit_option_terminator_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "positional_passthrough_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "lone_dash_passthrough_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "abbreviated_version_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "ambiguous_long_option_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "invalid_option_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "missing_long_dump_types_argument_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "missing_long_reference_argument_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "missing_reference_argument_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "too_many_reference_files_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "unsupported_long_option_expected.json",
    ROOT / "zigux" / "tests" / "fixtures" / "genksyms_bridge" / "unexpected_long_help_argument_expected.json",
)

WORKFLOW_SETUP_MARKERS = (
    "- name: Setup pinned Zig toolchain",
    'policy = json.loads(Path("scripts/zigux/zig-toolchain-policy.json").read_text(encoding="utf-8"))',
    'repo_archive_path="third_party/$ZIGUX_ZIG_FILENAME"',
    'mirror_file=".zig-toolchain/community-mirrors.txt"',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$repo_archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    "if try_local_archive; then",
    'elif curl -L --fail https://ziglang.org/download/community-mirrors.txt -o "$mirror_file"; then',
    'if python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive "$archive_path" --archive-target "$ZIGUX_ZIG_TARGET"; then',
    'if python3 scripts/zigux/check-zig-toolchain.py --zig "$zig_path"; then',
    "echo 'failed to install a verified pinned Zig archive from third_party, mirrors, or ziglang.org' >&2",
)

WORKFLOW_LINES = (
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
    "run: make -C zigux phase2-fixdep",
    "run: python3 scripts/zigux/validate-phase2.py",
)

BOOTSTRAP_PRESENT_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`scripts/zigux/check-phase2-toolchain-pin-scope.py`",
    "`scripts/zigux/check-phase2-required-make-routes.py`",
    "`scripts/zigux/check-phase2-kbuild-routes.py`",
    "`scripts/zigux/check-phase2-genksyms-selftest-alignment.py`",
    "`scripts/zigux/check-phase2-artifact-tools-manifest.py`",
    "`make -C zigux phase2-fixdep`",
    "`make -C zigux phase2`",
)

BOOTSTRAP_GAP_MARKERS = (
    "No current repo-reality gaps remain inside the bounded toolchain, installer, direct cross-route, local-first archive, or returned fixdep packet on current `master`.",
    "Treat older validator-first-only Phase 2 names as separate follow-through work instead of subtracting the returned installer, local-first archive, or direct cross-route surfaces from the current packet.",
)

PHASE2_CLOSURE_MARKERS = (
    "`scripts/zigux/check-lane05-local-first-archive-workflow.py`",
    "`scripts/zigux/check-lane05-local-archive-readme.py`",
    "`scripts/zigux/check-phase2-fixdep-gate.py`",
    "`scripts/zigux/check-fixdep-diff.py`",
    "`make -C zigux phase2-fixdep`",
)

SCRIPTS_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
)

REVIEW_MARKERS = (
    "`scripts/zigux/check-phase2-toolchain-pinning.py`",
    "`python3 scripts/zigux/check-zig-toolchain.py --policy-only`",
    "`python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing`",
    "`make -C zigux phase2-fixdep`",
)

TESTS_MARKERS = SCRIPTS_MARKERS

EXPECTED_POLICY = {
    "phase": "Phase 2",
    "channel_minimum_lockstep": True,
    "archive_target_scope": ["x86_64-linux"],
    "required_make_routes": ["phase2-toolchain", "phase2-validate", "phase2-cross"],
}

EXPECTED_TOOL_MANIFEST = json.loads(
    r"""{"notes":["Current Phase 2 repo-tooling evidence is anchored in the shipped toolchain checker, the returned local-first archive workflow and archive README contract checkers, the shipped toolchain-pinning and pin-scope guards, the returned installer helper, direct cross-route checker, docs-shared-reminder checker, required make-route guard, kbuild routes checker, the live kconfig bridge checker and fixture roster, the dedicated genksyms selftest-alignment guard, the manifest-backed genksyms bridge checker plus its expanded expected and process-output fixture packet, the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, the fixdep governance and parity checker pair, and the restored tranche-closure note.","Keep the directly readable validator pair explicit through scripts/zigux/validate-phase2.py and scripts/zigux/validate-phase2-closure.py instead of leaving the closure-side replay packet implied only in prose.","Keep the shipped zigux/Makefile entrypoints explicit through the phase2-toolchain, phase2-tools, phase2-kconfig, phase2-cross, phase2-genksyms, phase2-fixdep, phase2-validate, and phase2 make wrappers instead of treating them as repo-reality gaps.","Keep the dedicated manifest guards, the primary artifact_diff helper, and the dedicated genksyms selftest-alignment guard explicit through scripts/zigux/check-phase2-tool-manifest.py, scripts/zigux/check-phase2-artifact-tools-manifest.py, scripts/zigux/artifact_diff.py, and scripts/zigux/check-phase2-genksyms-selftest-alignment.py so Phase 2 packet drift fails closed beside the other reminder checkers.","Keep the returned install-zig archive verification checker, staged pinned-archive helper, and the stage-helper contract plus selftest packet explicit beside the local-first archive workflow, archive README contract, and installer helper so the shared Phase 2 tool packet matches the live phase2-toolchain and validate-phase2 routes.","Keep the returned installer helper, local-first archive workflow checkers, third_party archive README contract, repo-local pinned archive payload, direct cross-route checker, phase2_cross_targets fixture, the manifest-backed genksyms fixture packet, its restored process-output fixture set, the standalone invalid-long-option and ambiguous-long-option version-side-effect proofs, the full fixdep C-versus-Zig parity fixture packet, and the artifact-support manifest checker plus primary artifact_diff helper explicit through the current Phase 2 tool packet instead of leaving them in the repo-reality-gap bucket."],"phase":"Phase 2","present_surfaces":{"archive_support":["third_party/README.md","third_party/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2.tar.xz"],"artifact_support":["scripts/zigux/artifact_diff.py","scripts/zigux/check-phase2-artifact-tools-manifest.py","zigux/tests/fixtures/phase2_artifact_tools_manifest.json"],"bootstrap_helpers":["scripts/zigux/install-zig.py","scripts/zigux/stage-pinned-zig-archive.py"],"bridge_helpers":["scripts/zigux/kconfig/conf_bridge.zig","scripts/zigux/kconfig/confdata_bridge.zig","scripts/zigux/genksyms.zig","scripts/zigux/genksyms_version_before_invalid_long_option_test.zig","scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig"],"checkers":["scripts/zigux/check-zig-toolchain.py","scripts/zigux/check-lane05-local-first-archive-workflow.py","scripts/zigux/check-lane05-local-archive-readme.py","scripts/zigux/check-lane05-install-zig-archive-verification.py","scripts/zigux/check-lane05-stage-helper-contract.py","scripts/zigux/check-lane05-stage-helper-selftest.py","scripts/zigux/check-kconfig-bridge.py","scripts/zigux/check-phase2-kconfig-selftest-alignment.py","scripts/zigux/check-phase2-genksyms-selftest-alignment.py","scripts/zigux/check-phase2-kbuild-routes.py","scripts/zigux/check-phase2-tests-readme-alignment.py","scripts/zigux/check-phase2-cross.py","scripts/zigux/check-phase2-cross-selftest-alignment.py","scripts/zigux/check-phase2-toolchain-pinning.py","scripts/zigux/check-phase2-toolchain-pin-scope.py","scripts/zigux/check-phase2-required-make-routes.py","scripts/zigux/check-phase2-docs-shared-reminder.py","scripts/zigux/check-phase2-tool-manifest.py","scripts/zigux/check-phase2-artifact-tools-manifest.py","scripts/zigux/check-genksyms-bridge.py","scripts/zigux/check-phase2-fixdep-gate.py","scripts/zigux/check-fixdep-diff.py"],"closure_notes":["Documentation/zigux/phase2-closure.md","Documentation/zigux/phase2-toolchain-bootstrap-notes.md"],"cross_route_support":["scripts/zigux/check-phase2-cross.py","zigux/tests/fixtures/phase2_cross_targets.json"],"fixdep_support":["scripts/basic/fixdep.c","scripts/zigux/check-phase2-fixdep-gate.py","scripts/zigux/check-fixdep-diff.py","scripts/zigux/fixdep.zig","zigux/tests/fixtures/fixdep/cases.json","zigux/tests/fixtures/fixdep/dep:colon.so","zigux/tests/fixtures/fixdep/dep\\ name.rmeta","zigux/tests/fixtures/fixdep/escaped\\ space-config.h","zigux/tests/fixtures/fixdep/sample-config.h","zigux/tests/fixtures/fixdep/sample.c","zigux/tests/fixtures/fixdep/sample.d","zigux/tests/fixtures/fixdep/sample.h","zigux/tests/fixtures/fixdep/sample.rmeta","zigux/tests/fixtures/fixdep/sample2-config.h","zigux/tests/fixtures/fixdep/sample2.c","zigux/tests/fixtures/fixdep/sample2.so","zigux/tests/fixtures/fixdep/sample_comment_continuation.d","zigux/tests/fixtures/fixdep/sample_comment_continuation_dep.so","zigux/tests/fixtures/fixdep/sample_comment_continuation_expected.txt","zigux/tests/fixtures/fixdep/sample_comment_continuation_source.c","zigux/tests/fixtures/fixdep/sample_comment_continuation_source.rmeta","zigux/tests/fixtures/fixdep/sample_comment_only.d","zigux/tests/fixtures/fixdep/sample_comment_only_expected.stderr.txt","zigux/tests/fixtures/fixdep/sample_comment_only_expected.txt","zigux/tests/fixtures/fixdep/sample_concatenated.d","zigux/tests/fixtures/fixdep/sample_concatenated_dep.h","zigux/tests/fixtures/fixdep/sample_concatenated_expected.txt","zigux/tests/fixtures/fixdep/sample_concatenated_source.c","zigux/tests/fixtures/fixdep/sample_concatenated_temp.c","zigux/tests/fixtures/fixdep/sample_concatenated_temp_dep.h","zigux/tests/fixtures/fixdep/sample_dependency_continuation.d","zigux/tests/fixtures/fixdep/sample_dependency_continuation_dep.so","zigux/tests/fixtures/fixdep/sample_dependency_continuation_expected.txt","zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.c","zigux/tests/fixtures/fixdep/sample_dependency_continuation_source.rmeta","zigux/tests/fixtures/fixdep/sample_double_backslash_comment.d","zigux/tests/fixtures/fixdep/sample_double_backslash_comment_expected.stderr.txt","zigux/tests/fixtures/fixdep/sample_double_backslash_comment_expected.txt","zigux/tests/fixtures/fixdep/sample_double_backslash_comment_source.rmeta","zigux/tests/fixtures/fixdep/sample_escaped_colon.d","zigux/tests/fixtures/fixdep/sample_escaped_colon_expected.txt","zigux/tests/fixtures/fixdep/sample_escaped_colon_source.c","zigux/tests/fixtures/fixdep/sample_escaped_colon_source.rmeta","zigux/tests/fixtures/fixdep/sample_escaped_space.d","zigux/tests/fixtures/fixdep/sample_escaped_space_expected.txt","zigux/tests/fixtures/fixdep/sample_escaped_space_source.c","zigux/tests/fixtures/fixdep/sample_escaped_space_source.rmeta","zigux/tests/fixtures/fixdep/sample_expected.txt","zigux/tests/fixtures/fixdep/sample_missing_dep.d","zigux/tests/fixtures/fixdep/sample_missing_dep_expected.stderr.txt","zigux/tests/fixtures/fixdep/sample_missing_dep_expected.txt","zigux/tests/fixtures/fixdep/sample_missing_dep_source.c","zigux/tests/fixtures/fixdep/sample_multi_target.d","zigux/tests/fixtures/fixdep/sample_multi_target_expected.txt","zigux/tests/fixtures/fixdep/sample_output_write_expected.stderr.txt","zigux/tests/fixtures/fixdep/sample_output_write_expected.txt","zigux/tests/fixtures/fixdep/shared#config.h","zigux/tests/fixtures/fixdep/shared:config.h"],"fixture_roster":["zigux/tests/fixtures/kconfig_bridge/cases.json","zigux/tests/fixtures/kconfig_bridge/conf_manifest.json","zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json","zigux/tests/fixtures/kconfig_bridge/oldaskconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/syncconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/oldconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/allnoconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/allyesconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/allmodconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/alldefconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/randconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/defconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/savedefconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/listnewconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/helpnewconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/olddefconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/yes2modconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/mod2yesconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/mod2noconfig_expected.json","zigux/tests/fixtures/kconfig_bridge/sample.config","zigux/tests/fixtures/kconfig_bridge/escaped_strings.config","zigux/tests/fixtures/kconfig_bridge/escaped_control_sequences.config","zigux/tests/fixtures/kconfig_bridge/trailing_escaped_backslash.config","zigux/tests/fixtures/kconfig_bridge/sample_crlf.config","zigux/tests/fixtures/kconfig_bridge/explicit_n_tristate.config","zigux/tests/fixtures/kconfig_bridge/final_trailing_carriage_return.config","zigux/tests/fixtures/kconfig_bridge/final_unterminated_unset_comment.config","zigux/tests/fixtures/kconfig_bridge/uppercase_tristate.config","zigux/tests/fixtures/kconfig_bridge/non_config_lines.config","zigux/tests/fixtures/kconfig_bridge/empty_config_symbol_names.config","zigux/tests/fixtures/kconfig_bridge/malformed_unset_comment_tokens.config","zigux/tests/fixtures/kconfig_bridge/last_state_transitions.config","zigux/tests/fixtures/kconfig_bridge/duplicate_assignments.config","zigux/tests/fixtures/kconfig_bridge/duplicate_malformed_quoted_assignment.config","zigux/tests/fixtures/kconfig_bridge/sample_expected.json","zigux/tests/fixtures/kconfig_bridge/escaped_strings_expected.json","zigux/tests/fixtures/kconfig_bridge/escaped_control_sequences_expected.json","zigux/tests/fixtures/kconfig_bridge/trailing_escaped_backslash_expected.json","zigux/tests/fixtures/kconfig_bridge/sample_crlf_expected.json","zigux/tests/fixtures/kconfig_bridge/explicit_n_tristate_expected.json","zigux/tests/fixtures/kconfig_bridge/final_trailing_carriage_return_expected.json","zigux/tests/fixtures/kconfig_bridge/final_unterminated_unset_comment_expected.json","zigux/tests/fixtures/kconfig_bridge/uppercase_tristate_expected.json","zigux/tests/fixtures/kconfig_bridge/non_config_lines_expected.json","zigux/tests/fixtures/kconfig_bridge/empty_config_symbol_names_expected.json","zigux/tests/fixtures/kconfig_bridge/malformed_unset_comment_tokens_expected.json","zigux/tests/fixtures/kconfig_bridge/last_state_transitions_expected.json","zigux/tests/fixtures/kconfig_bridge/duplicate_assignments_expected.json","zigux/tests/fixtures/kconfig_bridge/duplicate_malformed_quoted_assignment_expected.json","zigux/tests/fixtures/genksyms_bridge/cases.json","zigux/tests/fixtures/genksyms_bridge/help_expected.json","zigux/tests/fixtures/genksyms_bridge/manifest.json","zigux/tests/fixtures/genksyms_bridge/minimal_expected.json","zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json","zigux/tests/fixtures/genksyms_bridge/long_options_expected.json","zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json","zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json","zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json","zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json","zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json","zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json","zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json","zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json","zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json","zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json","zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json","zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json","zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json","zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json","zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json"],"make_wrappers":["zigux/Makefile","make -C zigux phase2-toolchain","make -C zigux phase2-tools","make -C zigux phase2-kconfig","make -C zigux phase2-cross","make -C zigux phase2-genksyms","make -C zigux phase2-fixdep","make -C zigux phase2-validate","make -C zigux phase2"],"policy":["scripts/zigux/zig-toolchain-policy.json"],"review_surfaces":["Documentation/zigux/README.md","Documentation/zigux/phase2-closure.md","Documentation/zigux/review-checklist.md","zigux/tests/README.md"],"validators":["scripts/zigux/validate-phase2.py","scripts/zigux/validate-phase2-closure.py"]},"repo_reality_gaps":[],"scope":"current directly readable scripts-root toolchain, local-archive, installer, direct cross-route, kbuild, kconfig, genksyms, make-wrapper, fixdep, and tranche-closure reminder packet","status":"active","workflow":".github/workflows/zigux-bootstrap.yml"}"""
)

EXPECTED_SELF_TEST_CASE_COUNT = 12


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def resolve_path(root: Path, path: Path) -> Path:
    try:
        return root / path.relative_to(ROOT)
    except ValueError:
        return root / path


def count_exact_lines(text: str, marker: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def collect_missing_markers(text: str, markers: tuple[str, ...], code: str) -> list[tuple[str, str]]:
    return [(code, marker) for marker in markers if marker not in text]


def extract_markdown_section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start == -1:
        return ""
    start = text.find("\n", start)
    if start == -1:
        return ""
    start += 1
    end = text.find("\n## ", start)
    if end == -1:
        end = len(text)
    return text[start:end]


def expected_archive_filename(target: str, channel: str) -> str:
    return f"zig-{target}-{channel}.tar.xz"


def duplicate_archive_name(expected_filename: str) -> str:
    return f"{expected_filename[:-len('.tar.xz')]} (1).tar.xz"


def archive_readme_markers(target: str, channel: str, sha256: str, expected_size: int) -> tuple[str, ...]:
    expected_filename = expected_archive_filename(target, channel)
    return (
        f"`third_party/{expected_filename}`",
        f"`python3 scripts/zigux/check-zig-toolchain.py --archive-only --archive third_party/{expected_filename} --archive-target {target}`",
        f"`{sha256}`",
        f"`{expected_size}`",
        f"`{duplicate_archive_name(expected_filename)}`",
        "repo-local pinned archive filename",
        "digest",
        "size",
        "duplicate-copy boundary",
        "archive-only",
    )


def load_policy(root: Path) -> object:
    return json.loads(read_text(resolve_path(root, POLICY_PATH)))


def load_tool_manifest(root: Path) -> object:
    return json.loads(read_text(resolve_path(root, TOOL_MANIFEST_PATH)))


def collect_policy_issues(root: Path) -> list[tuple[str, str]]:
    payload = load_policy(root)
    issues: list[tuple[str, str]] = []
    if not isinstance(payload, dict):
        return [("INVALID_POLICY_PAYLOAD", type(payload).__name__)]
    if payload.get("phase") != EXPECTED_POLICY["phase"]:
        issues.append(("POLICY_PHASE_MISMATCH", repr(payload.get("phase"))))
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(upgrade_policy, dict):
        return issues + [("INVALID_UPGRADE_POLICY", type(upgrade_policy).__name__)]
    if upgrade_policy.get("channel_minimum_lockstep") is not EXPECTED_POLICY["channel_minimum_lockstep"]:
        issues.append(("POLICY_LOCKSTEP_MISMATCH", repr(upgrade_policy.get("channel_minimum_lockstep"))))
    if upgrade_policy.get("archive_target_scope") != EXPECTED_POLICY["archive_target_scope"]:
        issues.append(("POLICY_ARCHIVE_TARGET_SCOPE_MISMATCH", repr(upgrade_policy.get("archive_target_scope"))))
    if upgrade_policy.get("required_make_routes") != EXPECTED_POLICY["required_make_routes"]:
        issues.append(("POLICY_REQUIRED_MAKE_ROUTES_MISMATCH", repr(upgrade_policy.get("required_make_routes"))))
    return issues


def collect_archive_readme_issues(root: Path) -> list[tuple[str, str]]:
    payload = load_policy(root)
    if not isinstance(payload, dict):
        return [("INVALID_ARCHIVE_README_POLICY_PAYLOAD", type(payload).__name__)]
    channel = payload.get("channel")
    archives = payload.get("archive_sha256")
    upgrade_policy = payload.get("upgrade_policy")
    if not isinstance(channel, str) or not channel.strip():
        return [("INVALID_ARCHIVE_README_CHANNEL", repr(channel))]
    if not isinstance(archives, dict) or not archives:
        return [("INVALID_ARCHIVE_README_SHA_MAP", repr(archives))]
    if not isinstance(upgrade_policy, dict):
        return [("INVALID_ARCHIVE_README_UPGRADE_POLICY", type(upgrade_policy).__name__)]
    targets = upgrade_policy.get("archive_target_scope")
    if not isinstance(targets, list) or len(targets) != 1 or not isinstance(targets[0], str):
        return [("INVALID_ARCHIVE_README_TARGET_SCOPE", repr(targets))]
    target = targets[0]
    sha256 = archives.get(target)
    if not isinstance(sha256, str) or not sha256.strip():
        return [("INVALID_ARCHIVE_README_SHA", repr(sha256))]
    expected_size = EXPECTED_ARCHIVE_SIZES.get(target)
    if expected_size is None:
        return [("UNSUPPORTED_ARCHIVE_README_TARGET", target)]
    readme_text = read_text(resolve_path(root, THIRD_PARTY_README))
    issues = collect_missing_markers(
        readme_text,
        archive_readme_markers(target, channel.strip(), sha256.strip(), expected_size),
        "MISSING_ARCHIVE_README_MARKERS",
    )
    duplicate_path = resolve_path(root, THIRD_PARTY_README).parent / duplicate_archive_name(
        expected_archive_filename(target, channel.strip())
    )
    if duplicate_path.exists():
        issues.append(("DUPLICATE_ARCHIVE_COPY", duplicate_path.name))
    return issues


def collect_tool_manifest_issues(root: Path) -> list[tuple[str, str]]:
    payload = load_tool_manifest(root)
    if payload != EXPECTED_TOOL_MANIFEST:
        return [("TOOL_MANIFEST_MISMATCH", "phase2_tool_manifest.json diverged from expected Phase 2 packet")]
    return []


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    workflow_text = read_text(resolve_path(root, WORKFLOW))
    bootstrap_notes_text = read_text(resolve_path(root, BOOTSTRAP_NOTES))
    phase2_closure_text = read_text(resolve_path(root, PHASE2_CLOSURE))
    scripts_readme_text = read_text(resolve_path(root, SCRIPTS_README))
    review_checklist_text = read_text(resolve_path(root, REVIEW_CHECKLIST))
    tests_readme_text = read_text(resolve_path(root, TESTS_README))
    bootstrap_present_text = extract_markdown_section(bootstrap_notes_text, "## Current direct packet")
    bootstrap_gap_text = extract_markdown_section(bootstrap_notes_text, "## Current repo-reality gaps")
    issues.extend(collect_missing_markers(scripts_readme_text, SCRIPTS_MARKERS, "MISSING_SCRIPTS_MARKERS"))
    issues.extend(collect_missing_markers(review_checklist_text, REVIEW_MARKERS, "MISSING_REVIEW_MARKERS"))
    issues.extend(collect_missing_markers(tests_readme_text, TESTS_MARKERS, "MISSING_TESTS_MARKERS"))
    issues.extend(collect_missing_markers(workflow_text, WORKFLOW_SETUP_MARKERS, "MISSING_WORKFLOW_SETUP_MARKERS"))
    issues.extend(collect_missing_markers(phase2_closure_text, PHASE2_CLOSURE_MARKERS, "MISSING_PHASE2_CLOSURE_MARKERS"))
    for marker in WORKFLOW_LINES:
        count = count_exact_lines(workflow_text, marker)
        if count == 0:
            issues.append(("MISSING_WORKFLOW_HOOKS", marker))
        elif count != 1:
            issues.append(("DUPLICATE_WORKFLOW_HOOKS", f"{marker}:count={count}"))
    issues.extend(collect_missing_markers(bootstrap_present_text, BOOTSTRAP_PRESENT_MARKERS, "MISSING_BOOTSTRAP_PRESENT_MARKERS"))
    issues.extend(collect_missing_markers(bootstrap_gap_text, BOOTSTRAP_GAP_MARKERS, "MISSING_BOOTSTRAP_GAP_MARKERS"))
    for path in SURFACE_PATHS:
        if not resolve_path(root, path).exists():
            issues.append(("MISSING_SURFACE_PATHS", path.relative_to(ROOT).as_posix()))
    policy_path = resolve_path(root, POLICY_PATH)
    archive_readme_path = resolve_path(root, THIRD_PARTY_README)
    policy_issues: list[tuple[str, str]] = []
    if policy_path.exists():
        policy_issues = collect_policy_issues(root)
        issues.extend(policy_issues)
    if archive_readme_path.exists() and policy_path.exists() and not policy_issues:
        issues.extend(collect_archive_readme_issues(root))
    if resolve_path(root, TOOL_MANIFEST_PATH).exists():
        issues.extend(collect_tool_manifest_issues(root))
    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_TOOLCHAIN_PINNING=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    archive_target = "x86_64-linux"
    archive_channel = "0.17.0-dev.87+9b177a7d2"
    archive_sha = "3" * 64
    write_text(resolve_path(root, WORKFLOW), "\n".join((*WORKFLOW_SETUP_MARKERS, *WORKFLOW_LINES)) + "\n")
    write_text(resolve_path(root, SCRIPTS_README), "\n".join(["# scripts", *SCRIPTS_MARKERS]) + "\n")
    write_text(resolve_path(root, REVIEW_CHECKLIST), "\n".join(["# review", *REVIEW_MARKERS]) + "\n")
    write_text(resolve_path(root, TESTS_README), "\n".join(["# tests", *TESTS_MARKERS]) + "\n")
    write_text(resolve_path(root, PHASE2_CLOSURE), "\n".join(["# Phase 2 Closure", *PHASE2_CLOSURE_MARKERS]) + "\n")
    write_text(
        resolve_path(root, BOOTSTRAP_NOTES),
        "\n".join(
            [
                "# Phase 2 Toolchain Bootstrap Notes",
                "",
                "## Current direct packet",
                "",
                *BOOTSTRAP_PRESENT_MARKERS,
                "",
                "## Current repo-reality gaps",
                "",
                *BOOTSTRAP_GAP_MARKERS,
                "",
            ]
        ),
    )
    for path in SURFACE_PATHS:
        if path == POLICY_PATH:
            write_text(
                resolve_path(root, path),
                json.dumps(
                    {
                        "phase": EXPECTED_POLICY["phase"],
                        "channel": archive_channel,
                        "minimum_version": archive_channel,
                        "archive_sha256": {archive_target: archive_sha},
                        "upgrade_policy": {
                            "channel_minimum_lockstep": EXPECTED_POLICY["channel_minimum_lockstep"],
                            "archive_target_scope": EXPECTED_POLICY["archive_target_scope"],
                            "required_make_routes": EXPECTED_POLICY["required_make_routes"],
                        },
                    },
                    indent=2,
                )
                + "\n",
            )
        elif path == TOOL_MANIFEST_PATH:
            write_text(resolve_path(root, path), json.dumps(EXPECTED_TOOL_MANIFEST, indent=2) + "\n")
        elif path == THIRD_PARTY_README:
            write_text(
                resolve_path(root, path),
                "\n".join(
                    (
                        "# third_party",
                        "",
                        *archive_readme_markers(
                            archive_target,
                            archive_channel,
                            archive_sha,
                            EXPECTED_ARCHIVE_SIZES[archive_target],
                        ),
                        "",
                    )
                ),
            )
        elif path in (BOOTSTRAP_NOTES, PHASE2_CLOSURE, SCRIPTS_README, REVIEW_CHECKLIST, TESTS_README):
            continue
        else:
            write_text(resolve_path(root, path), "present\n")


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_toolchain_pinning_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert EXPECTED_TOOL_MANIFEST["present_surfaces"]["bridge_helpers"][-1].endswith(
            "genksyms_version_before_ambiguous_long_option_test.zig"
        )
        checks_run += 1
        assert collect_issues(root) == []
        checks_run += 1
        workflow_path = resolve_path(root, WORKFLOW)
        workflow_path.write_text(workflow_path.read_text(encoding="utf-8").replace(WORKFLOW_LINES[0], ""), encoding="utf-8")
        assert any(code == "MISSING_WORKFLOW_HOOKS" for code, _ in collect_issues(root))
        checks_run += 1
        build_self_test_root(root)
        manifest_path = resolve_path(root, TOOL_MANIFEST_PATH)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["present_surfaces"]["bootstrap_helpers"] = ["scripts/zigux/install-zig.py"]
        write_text(manifest_path, json.dumps(payload, indent=2) + "\n")
        assert any(code == "TOOL_MANIFEST_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1
        build_self_test_root(root)
        policy_path = resolve_path(root, POLICY_PATH)
        policy = json.loads(policy_path.read_text(encoding="utf-8"))
        policy["upgrade_policy"]["required_make_routes"] = ["phase2-toolchain"]
        write_text(policy_path, json.dumps(policy, indent=2) + "\n")
        assert any(code == "POLICY_REQUIRED_MAKE_ROUTES_MISMATCH" for code, _ in collect_issues(root))
        checks_run += 1
        build_self_test_root(root)
        readme_path = resolve_path(root, THIRD_PARTY_README)
        readme_path.write_text(readme_path.read_text(encoding="utf-8").replace("duplicate-copy boundary", ""), encoding="utf-8")
        assert any(code == "MISSING_ARCHIVE_README_MARKERS" for code, _ in collect_issues(root))
        checks_run += 1
        build_self_test_root(root)
        duplicate_path = resolve_path(root, THIRD_PARTY_README).parent / "zig-x86_64-linux-0.17.0-dev.87+9b177a7d2 (1).tar.xz"
        write_text(duplicate_path, "duplicate\n")
        assert any(code == "DUPLICATE_ARCHIVE_COPY" for code, _ in collect_issues(root))
        checks_run += 1
        build_self_test_root(root)
        resolve_path(root, ROOT / "scripts" / "zigux" / "genksyms_version_before_ambiguous_long_option_test.zig").unlink()
        assert any(
            code == "MISSING_SURFACE_PATHS"
            and value == "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig"
            for code, value in collect_issues(root)
        )
        checks_run += 1
        build_self_test_root(root)
        notes_path = resolve_path(root, BOOTSTRAP_NOTES)
        notes_path.write_text(notes_path.read_text(encoding="utf-8").replace(BOOTSTRAP_GAP_MARKERS[0], ""), encoding="utf-8")
        assert any(code == "MISSING_BOOTSTRAP_GAP_MARKERS" for code, _ in collect_issues(root))
        checks_run += 1
        build_self_test_root(root)
        review_path = resolve_path(root, REVIEW_CHECKLIST)
        review_path.write_text(review_path.read_text(encoding="utf-8").replace(REVIEW_MARKERS[-1], ""), encoding="utf-8")
        assert any(code == "MISSING_REVIEW_MARKERS" for code, _ in collect_issues(root))
        checks_run += 1
        build_self_test_root(root)
        closure_path = resolve_path(root, PHASE2_CLOSURE)
        closure_path.write_text(closure_path.read_text(encoding="utf-8").replace(PHASE2_CLOSURE_MARKERS[-1], ""), encoding="utf-8")
        assert any(code == "MISSING_PHASE2_CLOSURE_MARKERS" for code, _ in collect_issues(root))
        checks_run += 1
        build_self_test_root(root)
        tests_path = resolve_path(root, TESTS_README)
        tests_path.write_text(tests_path.read_text(encoding="utf-8").replace(TESTS_MARKERS[0], ""), encoding="utf-8")
        assert any(code == "MISSING_TESTS_MARKERS" for code, _ in collect_issues(root))
        checks_run += 1
    assert checks_run == EXPECTED_SELF_TEST_CASE_COUNT
    print("PHASE2_TOOLCHAIN_PINNING_SELF_TEST=pass")
    print(f"PHASE2_TOOLCHAIN_PINNING_SELF_TEST_CASE_COUNT={checks_run}")
    print("PHASE2_TOOLCHAIN_PINNING_MANIFEST_SYNC=pass")
    print(
        "PHASE2_TOOLCHAIN_PINNING_SURFACE_PATH_COUNT="
        f"{len(SURFACE_PATHS)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Keep the current directly readable Phase 2 toolchain pinning packet aligned.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root)
    if issues:
        return emit_issues(issues)
    print("PHASE2_TOOLCHAIN_PINNING=pass")
    print(f"PHASE2_TOOLCHAIN_PINNING_REQUIRED_MARKER_COUNT={len(BOOTSTRAP_PRESENT_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_PINNING_GAP_MARKER_COUNT={len(BOOTSTRAP_GAP_MARKERS)}")
    print(f"PHASE2_TOOLCHAIN_PINNING_ARCHIVE_README_MARKER_COUNT={ARCHIVE_README_REQUIRED_MARKER_COUNT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
