const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE2_VALIDATION=pass";
pub const self_test_pass_marker = "PHASE2_VALIDATION_SELF_TEST=pass";

const WORKFLOW = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
};

const MAKEFILE = [_][]const u8{
    "zigux/Makefile",
};

const TOOLCHAIN_POLICY = [_][]const u8{
    "scripts/zigux/zig-toolchain-policy.json",
};

const GENKSYMS_DUAL_IMPLEMENTATION_SURVEY = [_][]const u8{
    "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md",
};

const FIXDEP_DUAL_IMPLEMENTATION_SURVEY = [_][]const u8{
    "Documentation/zigux/phase2-fixdep-dual-implementation-survey.md",
};

const GENKSYMS_VERSION_SIDE_EFFECT_TEST = [_][]const u8{
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
};

const GENKSYMS_VERSION_SIDE_EFFECT_AMBIGUOUS_TEST = [_][]const u8{
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
};

const GENKSYMS_INLINE_SHORT_ARGUMENT_TEST = [_][]const u8{
    "scripts/zigux/genksyms_inline_short_option_argument_test.zig",
};

const GENKSYMS_REPEATED_VERSION_BEFORE_ABBREV_ARGUMENT_TEST = [_][]const u8{
    "scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig",
};

const GENKSYMS_ABBREVIATED_WARNING_QUIET_TERMINATOR_TEST = [_][]const u8{
    "scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig",
};

const GENKSYMS_MANIFEST_FIXTURE = [_][]const u8{
    "zigux/tests/fixtures/genksyms_bridge/manifest.json",
};

const GENKSYMS_PROCESS_OUTPUT_FIXTURES = [_][]const u8{
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
};

const KCONFIG_CONFDATA_REPLAY_MARKERS = [_][]const u8{
    "compile_tool(zig, CONFDATA_BRIDGE, confdata_exe)",
    "cmd = [str(confdata_exe), str(FIXTURE_DIR / str(case[\"input\"]))]",
    "actual.write_text(run(cmd, cwd=str(ROOT), capture_output=True).stdout, encoding=\"utf-8\", newline=\"\\n\")",
    "repeat.write_text(run(cmd, cwd=str(ROOT), capture_output=True).stdout, encoding=\"utf-8\", newline=\"\\n\")",
    "check_repeatable_json_output(expected, actual, repeat)",
};

const KCONFIG_BRIDGE_VALIDATOR_PATH = [_][]const u8{
    "scripts\\zigux/check_kconfig_bridge.zig",
};

const KCONFIG_CONF_EXPECTED_FIXTURES = [_][]const u8{
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
};

const KCONFIG_CONFDATA_INPUT_FIXTURES = [_][]const u8{
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
};

const KCONFIG_CONFDATA_EXPECTED_FIXTURES = [_][]const u8{
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
};

const ARCHIVE_PAYLOAD_PATH = [_][]const u8{
    "third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz",
};

const ARCHIVE_PARTS_MANIFEST_PATH = [_][]const u8{
    "third_party/zig-x86_64-linux-0.17.0-dev.877+a3ae499dc.tar.xz.parts/manifest.json",
};

const ARCHIVE_README_PATH = [_][]const u8{
    "third_party/README.md",
};

const DEFAULT_REQUIRED_MAKE_ROUTES = [_][]const u8{
    "phase2-toolchain",
    "phase2-tools",
    "phase2-kconfig",
    "phase2-cross",
    "phase2-genksyms",
    "phase2-fixdep",
    "phase2-validate",
};

const STATIC_REQUIRED_WORKFLOW_LINES = [_][]const u8{
    "run: zig run scripts\\zigux/check_zig_toolchain.zig --self-test",
    "run: zig run scripts\\zigux/check_zig_toolchain.zig --policy-only",
    "run: zig run scripts\\zigux/check_zig_toolchain.zig --archive-only --allow-missing",
    "run: zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig --self-test",
    "run: zig run scripts\\zigux/check_lane05_local_first_archive_workflow.zig",
    "run: zig run scripts\\zigux/check_lane05_local_archive_readme.zig --self-test",
    "run: zig run scripts\\zigux/check_lane05_local_archive_readme.zig",
    "run: zig run scripts\\zigux/check_lane05_install_zig_archive_verification.zig --self-test",
    "run: zig run scripts\\zigux/check_lane05_install_zig_archive_verification.zig",
    "run: zig run scripts/zigux/install_zig.zig --self-test",
    "run: zig run scripts/zigux/stage_pinned_zig_archive.zig --self-test",
    "run: zig run scripts\\zigux/check_lane05_stage_helper_contract.zig --self-test",
    "run: zig run scripts\\zigux/check_lane05_stage_helper_contract.zig",
    "run: zig run scripts\\zigux/check_lane05_stage_helper_selftest.zig --self-test",
    "run: zig run scripts\\zigux/check_lane05_stage_helper_selftest.zig",
    "run: zig run scripts\\zigux/check_phase2_fixdep_gate.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_fixdep_gate.zig",
    "run: zig run scripts\\zigux/check_fixdep_diff.zig --self-test",
    "run: zig run scripts\\zigux/check_fixdep_diff.zig",
    "run: zig test scripts/zigux/fixdep.zig",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pinning.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pinning.zig",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_toolchain_pin_scope.zig",
    "run: zig run scripts\\zigux/check_phase2_required_make_routes.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_required_make_routes.zig",
    "run: zig run scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_bootstrap_workflow_routes.zig",
    "run: zig run scripts\\zigux/check_kconfig_bridge.zig --self-test",
    "run: zig run scripts\\zigux/check_kconfig_bridge.zig",
    "run: zig test scripts/zigux/kconfig/conf_bridge.zig",
    "run: zig test scripts/zigux/kconfig/confdata_bridge.zig",
    "run: zig run scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_kconfig_selftest_alignment.zig",
    "run: zig run scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_kconfig_allconfig_helper_packet.zig",
    "run: zig run scripts\\zigux/check_phase2_kbuild_routes.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_kbuild_routes.zig",
    "run: zig run scripts\\zigux/check_phase2_tests_readme_alignment.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_tests_readme_alignment.zig",
    "run: zig run scripts\\zigux/check_phase2_cross.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_cross.zig",
    "run: zig run scripts\\zigux/check_phase2_cross_selftest_alignment.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_cross_selftest_alignment.zig",
    "run: zig run scripts\\zigux/check_phase2_docs_shared_reminder.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_docs_shared_reminder.zig",
    "run: zig run scripts\\zigux/check_phase2_tool_manifest.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_tool_manifest.zig",
    "run: zig run scripts\\zigux/check_phase2_artifact_tools_manifest.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_artifact_tools_manifest.zig",
    "run: zig run scripts\\zigux/check_genksyms_bridge.zig --self-test",
    "run: zig run scripts\\zigux/check_genksyms_bridge.zig",
    "run: zig test scripts/zigux/genksyms.zig",
    "run: zig run scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig --self-test",
    "run: zig run scripts\\zigux/check_phase2_genksyms_selftest_alignment.zig",
    "run: zig run scripts\\zigux/validate_phase2.zig",
};

const STATIC_REQUIRED_MAKEFILE_LINES = [_][]const u8{
    "phase2-toolchain:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig --policy-only",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_zig_toolchain.zig --archive-only --allow-missing",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pinning.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_toolchain_pin_scope.zig",
    "phase2-tools:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kbuild_routes.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_docs_shared_reminder.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_required_make_routes.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_bootstrap_workflow_routes.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_bootstrap_workflow_routes.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_artifact_tools_manifest.zig",
    "phase2-kconfig: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_kconfig_bridge.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_kconfig_bridge.zig --zig \"$(ZIG_REPO_ROOT)\"",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/kconfig/conf_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/kconfig/confdata_bridge.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_selftest_alignment.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_selftest_alignment.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_allconfig_helper_packet.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_kconfig_allconfig_helper_packet.zig",
    "phase2-cross:",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_cross_selftest_alignment.zig",
    "phase2-genksyms: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_genksyms_bridge.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_inline_short_option_argument_test.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_genksyms_selftest_alignment.zig --self-test",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_genksyms_selftest_alignment.zig",
    "phase2-fixdep: phase2-toolchain",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_phase2_fixdep_gate.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig --self-test",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/check_fixdep_diff.zig --zig \"$(ZIG_REPO_ROOT)\"",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/fixdep.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tests_readme_alignment.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/check_phase2_tool_manifest.zig",
    "$(ZIG) run $(PHASE2_SCRIPT_ROOT)/validate_phase2_closure.zig",
};

const ARCHIVE_SUPPORT_ALTERNATIVES = [_][]const u8{
    "ARCHIVE_PAYLOAD_PATH",
    "ARCHIVE_PARTS_MANIFEST_PATH",
};

const ARCHIVE_SUPPORT_DESCRIPTION = [_][]const u8{
    " or .join+ or documented canonical adybag14-cyber/zig fallback",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_workflow_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_workflow_path);
    const text_workflow = try guard.readUtf8File(io, allocator, text_workflow_path);
    defer allocator.free(text_workflow);
    for (WORKFLOW) |marker| try guard.requireMarker(text_workflow, marker);
    const text_makefile_path = try guard.joinPath(allocator, root, "zigux/Makefile");
    defer allocator.free(text_makefile_path);
    const text_makefile = try guard.readUtf8File(io, allocator, text_makefile_path);
    defer allocator.free(text_makefile);
    for (MAKEFILE) |marker| try guard.requireMarker(text_makefile, marker);
    const text_toolchain_policy_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_toolchain_policy_path);
    const text_toolchain_policy = try guard.readUtf8File(io, allocator, text_toolchain_policy_path);
    defer allocator.free(text_toolchain_policy);
    for (TOOLCHAIN_POLICY) |marker| try guard.requireMarker(text_toolchain_policy, marker);
    const text_genksyms_dual_implementation_survey_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_genksyms_dual_implementation_survey_path);
    const text_genksyms_dual_implementation_survey = try guard.readUtf8File(io, allocator, text_genksyms_dual_implementation_survey_path);
    defer allocator.free(text_genksyms_dual_implementation_survey);
    for (GENKSYMS_DUAL_IMPLEMENTATION_SURVEY) |marker| try guard.requireMarker(text_genksyms_dual_implementation_survey, marker);
    const text_fixdep_dual_implementation_survey_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_fixdep_dual_implementation_survey_path);
    const text_fixdep_dual_implementation_survey = try guard.readUtf8File(io, allocator, text_fixdep_dual_implementation_survey_path);
    defer allocator.free(text_fixdep_dual_implementation_survey);
    for (FIXDEP_DUAL_IMPLEMENTATION_SURVEY) |marker| try guard.requireMarker(text_fixdep_dual_implementation_survey, marker);
    const text_genksyms_version_side_effect_test_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_genksyms_version_side_effect_test_path);
    const text_genksyms_version_side_effect_test = try guard.readUtf8File(io, allocator, text_genksyms_version_side_effect_test_path);
    defer allocator.free(text_genksyms_version_side_effect_test);
    for (GENKSYMS_VERSION_SIDE_EFFECT_TEST) |marker| try guard.requireMarker(text_genksyms_version_side_effect_test, marker);
    const text_genksyms_version_side_effect_ambiguous_test_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_genksyms_version_side_effect_ambiguous_test_path);
    const text_genksyms_version_side_effect_ambiguous_test = try guard.readUtf8File(io, allocator, text_genksyms_version_side_effect_ambiguous_test_path);
    defer allocator.free(text_genksyms_version_side_effect_ambiguous_test);
    for (GENKSYMS_VERSION_SIDE_EFFECT_AMBIGUOUS_TEST) |marker| try guard.requireMarker(text_genksyms_version_side_effect_ambiguous_test, marker);
    const text_genksyms_inline_short_argument_test_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_genksyms_inline_short_argument_test_path);
    const text_genksyms_inline_short_argument_test = try guard.readUtf8File(io, allocator, text_genksyms_inline_short_argument_test_path);
    defer allocator.free(text_genksyms_inline_short_argument_test);
    for (GENKSYMS_INLINE_SHORT_ARGUMENT_TEST) |marker| try guard.requireMarker(text_genksyms_inline_short_argument_test, marker);
    const text_genksyms_repeated_version_before_abbrev_argument_test_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_genksyms_repeated_version_before_abbrev_argument_test_path);
    const text_genksyms_repeated_version_before_abbrev_argument_test = try guard.readUtf8File(io, allocator, text_genksyms_repeated_version_before_abbrev_argument_test_path);
    defer allocator.free(text_genksyms_repeated_version_before_abbrev_argument_test);
    for (GENKSYMS_REPEATED_VERSION_BEFORE_ABBREV_ARGUMENT_TEST) |marker| try guard.requireMarker(text_genksyms_repeated_version_before_abbrev_argument_test, marker);
    const text_genksyms_abbreviated_warning_quiet_terminator_test_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_genksyms_abbreviated_warning_quiet_terminator_test_path);
    const text_genksyms_abbreviated_warning_quiet_terminator_test = try guard.readUtf8File(io, allocator, text_genksyms_abbreviated_warning_quiet_terminator_test_path);
    defer allocator.free(text_genksyms_abbreviated_warning_quiet_terminator_test);
    for (GENKSYMS_ABBREVIATED_WARNING_QUIET_TERMINATOR_TEST) |marker| try guard.requireMarker(text_genksyms_abbreviated_warning_quiet_terminator_test, marker);
    const text_genksyms_manifest_fixture_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_genksyms_manifest_fixture_path);
    const text_genksyms_manifest_fixture = try guard.readUtf8File(io, allocator, text_genksyms_manifest_fixture_path);
    defer allocator.free(text_genksyms_manifest_fixture);
    for (GENKSYMS_MANIFEST_FIXTURE) |marker| try guard.requireMarker(text_genksyms_manifest_fixture, marker);
    const text_genksyms_process_output_fixtures_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_genksyms_process_output_fixtures_path);
    const text_genksyms_process_output_fixtures = try guard.readUtf8File(io, allocator, text_genksyms_process_output_fixtures_path);
    defer allocator.free(text_genksyms_process_output_fixtures);
    for (GENKSYMS_PROCESS_OUTPUT_FIXTURES) |marker| try guard.requireMarker(text_genksyms_process_output_fixtures, marker);
    const text_kconfig_confdata_replay_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_kconfig_confdata_replay_markers_path);
    const text_kconfig_confdata_replay_markers = try guard.readUtf8File(io, allocator, text_kconfig_confdata_replay_markers_path);
    defer allocator.free(text_kconfig_confdata_replay_markers);
    for (KCONFIG_CONFDATA_REPLAY_MARKERS) |marker| try guard.requireMarker(text_kconfig_confdata_replay_markers, marker);
    const text_kconfig_bridge_validator_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_kconfig_bridge_validator_path_path);
    const text_kconfig_bridge_validator_path = try guard.readUtf8File(io, allocator, text_kconfig_bridge_validator_path_path);
    defer allocator.free(text_kconfig_bridge_validator_path);
    for (KCONFIG_BRIDGE_VALIDATOR_PATH) |marker| try guard.requireMarker(text_kconfig_bridge_validator_path, marker);
    const text_kconfig_conf_expected_fixtures_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_kconfig_conf_expected_fixtures_path);
    const text_kconfig_conf_expected_fixtures = try guard.readUtf8File(io, allocator, text_kconfig_conf_expected_fixtures_path);
    defer allocator.free(text_kconfig_conf_expected_fixtures);
    for (KCONFIG_CONF_EXPECTED_FIXTURES) |marker| try guard.requireMarker(text_kconfig_conf_expected_fixtures, marker);
    const text_kconfig_confdata_input_fixtures_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_kconfig_confdata_input_fixtures_path);
    const text_kconfig_confdata_input_fixtures = try guard.readUtf8File(io, allocator, text_kconfig_confdata_input_fixtures_path);
    defer allocator.free(text_kconfig_confdata_input_fixtures);
    for (KCONFIG_CONFDATA_INPUT_FIXTURES) |marker| try guard.requireMarker(text_kconfig_confdata_input_fixtures, marker);
    const text_kconfig_confdata_expected_fixtures_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_kconfig_confdata_expected_fixtures_path);
    const text_kconfig_confdata_expected_fixtures = try guard.readUtf8File(io, allocator, text_kconfig_confdata_expected_fixtures_path);
    defer allocator.free(text_kconfig_confdata_expected_fixtures);
    for (KCONFIG_CONFDATA_EXPECTED_FIXTURES) |marker| try guard.requireMarker(text_kconfig_confdata_expected_fixtures, marker);
    const text_archive_payload_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_archive_payload_path_path);
    const text_archive_payload_path = try guard.readUtf8File(io, allocator, text_archive_payload_path_path);
    defer allocator.free(text_archive_payload_path);
    for (ARCHIVE_PAYLOAD_PATH) |marker| try guard.requireMarker(text_archive_payload_path, marker);
    const text_archive_parts_manifest_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_archive_parts_manifest_path_path);
    const text_archive_parts_manifest_path = try guard.readUtf8File(io, allocator, text_archive_parts_manifest_path_path);
    defer allocator.free(text_archive_parts_manifest_path);
    for (ARCHIVE_PARTS_MANIFEST_PATH) |marker| try guard.requireMarker(text_archive_parts_manifest_path, marker);
    const text_archive_readme_path_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_archive_readme_path_path);
    const text_archive_readme_path = try guard.readUtf8File(io, allocator, text_archive_readme_path_path);
    defer allocator.free(text_archive_readme_path);
    for (ARCHIVE_README_PATH) |marker| try guard.requireMarker(text_archive_readme_path, marker);
    const text_default_required_make_routes_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_default_required_make_routes_path);
    const text_default_required_make_routes = try guard.readUtf8File(io, allocator, text_default_required_make_routes_path);
    defer allocator.free(text_default_required_make_routes);
    for (DEFAULT_REQUIRED_MAKE_ROUTES) |marker| try guard.requireMarker(text_default_required_make_routes, marker);
    const text_static_required_workflow_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_static_required_workflow_lines_path);
    const text_static_required_workflow_lines = try guard.readUtf8File(io, allocator, text_static_required_workflow_lines_path);
    defer allocator.free(text_static_required_workflow_lines);
    for (STATIC_REQUIRED_WORKFLOW_LINES) |marker| try guard.requireExactLineCount(text_static_required_workflow_lines, marker, 1);
    const text_static_required_makefile_lines_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_static_required_makefile_lines_path);
    const text_static_required_makefile_lines = try guard.readUtf8File(io, allocator, text_static_required_makefile_lines_path);
    defer allocator.free(text_static_required_makefile_lines);
    for (STATIC_REQUIRED_MAKEFILE_LINES) |marker| try guard.requireExactLineCount(text_static_required_makefile_lines, marker, 1);
    const text_archive_support_alternatives_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_archive_support_alternatives_path);
    const text_archive_support_alternatives = try guard.readUtf8File(io, allocator, text_archive_support_alternatives_path);
    defer allocator.free(text_archive_support_alternatives);
    for (ARCHIVE_SUPPORT_ALTERNATIVES) |marker| try guard.requireMarker(text_archive_support_alternatives, marker);
    const text_archive_support_description_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_archive_support_description_path);
    const text_archive_support_description = try guard.readUtf8File(io, allocator, text_archive_support_description_path);
    defer allocator.free(text_archive_support_description);
    for (ARCHIVE_SUPPORT_DESCRIPTION) |marker| try guard.requireMarker(text_archive_support_description, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
