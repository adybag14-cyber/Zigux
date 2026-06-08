const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectLineOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

const bridge_fixture_packet =
    "PHASE2_CURRENT_GENKSYMS_BRIDGE_PACKET=zigux/tests/fixtures/genksyms_bridge/minimal_expected.json,zigux/tests/fixtures/genksyms_bridge/debug_reference_types_expected.json,zigux/tests/fixtures/genksyms_bridge/inline_short_option_arguments_expected.json,zigux/tests/fixtures/genksyms_bridge/long_options_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_long_options_expected.json,zigux/tests/fixtures/genksyms_bridge/quiet_overrides_warning_expected.json,zigux/tests/fixtures/genksyms_bridge/explicit_option_terminator_expected.json,zigux/tests/fixtures/genksyms_bridge/positional_passthrough_expected.json,zigux/tests/fixtures/genksyms_bridge/lone_dash_passthrough_expected.json,zigux/tests/fixtures/genksyms_bridge/dash_prefixed_long_option_arguments_as_data_expected.json,zigux/tests/fixtures/genksyms_bridge/dash_prefixed_short_option_arguments_as_data_expected.json";

const process_output_packet =
    "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=zigux/tests/fixtures/genksyms_bridge/abbreviated_version_expected.json,zigux/tests/fixtures/genksyms_bridge/ambiguous_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/invalid_option_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_dump_types_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_long_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/missing_reference_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/too_many_reference_files_expected.json,zigux/tests/fixtures/genksyms_bridge/unsupported_long_option_expected.json,zigux/tests/fixtures/genksyms_bridge/unexpected_long_help_argument_expected.json,zigux/tests/fixtures/genksyms_bridge/abbreviated_unexpected_long_help_argument_expected.json";

const standalone_proofs = [_][]const u8{
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
    "scripts/zigux/genksyms_inline_short_option_argument_test.zig",
    "scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig",
    "scripts/zigux/genksyms_abbreviated_warning_quiet_terminator_test.zig",
};

const bridge_expected_files = [_][]const u8{
    "minimal_expected.json",
    "debug_reference_types_expected.json",
    "inline_short_option_arguments_expected.json",
    "long_options_expected.json",
    "abbreviated_long_options_expected.json",
    "quiet_overrides_warning_expected.json",
    "explicit_option_terminator_expected.json",
    "positional_passthrough_expected.json",
    "lone_dash_passthrough_expected.json",
    "dash_prefixed_long_option_arguments_as_data_expected.json",
    "dash_prefixed_short_option_arguments_as_data_expected.json",
};

const process_output_files = [_][]const u8{
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
};

test "phase 2 genksyms survey records the wrapper and CRC-side evidence packet" {
    const survey = try readRepoFile("Documentation/zigux/phase2-genksyms-dual-implementation-survey.md", 64 * 1024);
    defer std.testing.allocator.free(survey);

    try expectContains(survey, "# Phase 2 genksyms dual-implementation survey");
    try expectContains(survey, "Lane: `P2-L07`");
    try expectContains(survey, "scripts/genksyms/genksyms.c");
    try expectContains(survey, "scripts/zigux/genksyms.zig");
    try expectContains(survey, "selected dual implementations");
    try expectContains(survey, "wrapper-first");
    try expectContains(survey, "scripts/zigux/genksyms_crc.zig");
    try expectContains(survey, "scripts/zigux/check-genksyms-crc-diff.py");
    try expectContains(survey, "scripts/zigux/check-genksyms-bridge.py");
    try expectContains(survey, "scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py");
    try expectContains(survey, "wrapper bridge and CRC-side dual-implementation evidence both materialized.");
    try expectContains(survey, "Leave this survey parked unless a future reread finds another genksyms-local wording, inventory, or replay drift.");

    for (standalone_proofs) |path| {
        try expectContains(survey, path);
    }
    for (bridge_expected_files) |file| {
        try expectContains(survey, file);
    }
    for (process_output_files) |file| {
        try expectContains(survey, file);
    }
}

test "phase 2 closure and tool manifest keep the genksyms survey packet aligned" {
    const closure = try readRepoFile("Documentation/zigux/phase2-closure.md", 128 * 1024);
    defer std.testing.allocator.free(closure);

    const manifest = try readRepoFile("zigux/tests/fixtures/phase2_tool_manifest.json", 128 * 1024);
    defer std.testing.allocator.free(manifest);

    const genksyms_manifest = try readRepoFile("zigux/tests/fixtures/genksyms_bridge/manifest.json", 32 * 1024);
    defer std.testing.allocator.free(genksyms_manifest);

    try expectContains(closure, "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    try expectContains(closure, "scripts/zigux/check-genksyms-bridge.py");
    try expectContains(closure, "scripts/zigux/check-phase2-genksyms-selftest-alignment.py");
    try expectContains(closure, "scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py");
    try expectContains(closure, bridge_fixture_packet);
    try expectContains(closure, process_output_packet);
    try expectContains(closure, "PHASE2_SHARED_MAKE_ROUTES=make -C zigux phase2-toolchain,make -C zigux phase2-tools,make -C zigux phase2-kconfig,make -C zigux phase2-cross,make -C zigux phase2-genksyms,make -C zigux phase2-fixdep,make -C zigux phase2-validate,make -C zigux phase2");
    try expectContains(closure, "PHASE2_CLOSURE_VALIDATORS=python3 scripts/zigux/validate-phase2.py,python3 scripts/zigux/validate-phase2-closure.py");

    try expectContains(manifest, "scripts/zigux/check-phase2-genksyms-selftest-alignment.py");
    try expectContains(manifest, "scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py");
    try expectContains(manifest, "scripts/zigux/check-genksyms-bridge.py");
    try expectContains(manifest, "make -C zigux phase2-genksyms");
    try expectContains(manifest, "repo_reality_gaps");
    try expectContains(manifest, "\"repo_reality_gaps\": []");

    try expectContains(genksyms_manifest, "\"case_count\": 11");
    try expectContains(genksyms_manifest, "\"mode\": \"bounded wrapper-first dual-implementation bridge\"");
    try expectContains(genksyms_manifest, "\"process_output_packet\"");
    for (standalone_proofs) |path| {
        try expectContains(manifest, path);
        try expectContains(genksyms_manifest, path);
    }
    for (process_output_files) |file| {
        try expectContains(manifest, file);
        try expectContains(genksyms_manifest, file);
    }
}

test "phase 2 reminder and replay surfaces expose the genksyms survey route" {
    const scripts_readme = try readRepoFile("scripts/zigux/README.md", 128 * 1024);
    defer std.testing.allocator.free(scripts_readme);

    const tests_readme = try readRepoFile("zigux/tests/README.md", 128 * 1024);
    defer std.testing.allocator.free(tests_readme);

    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml", 256 * 1024);
    defer std.testing.allocator.free(workflow);

    const makefile = try readRepoFile("zigux/Makefile", 128 * 1024);
    defer std.testing.allocator.free(makefile);

    try expectContains(scripts_readme, "scripts/zigux/check-genksyms-bridge.py");
    try expectContains(scripts_readme, "make -C zigux phase2-genksyms");
    try expectContains(scripts_readme, "returned make wrappers");

    try expectContains(tests_readme, "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    try expectContains(tests_readme, "scripts/zigux/check-phase2-genksyms-selftest-alignment.py");
    try expectContains(tests_readme, "scripts/zigux/check-genksyms-bridge.py");
    try expectContains(tests_readme, "zigux/tests/fixtures/genksyms_bridge/manifest.json");
    try expectContains(tests_readme, "make -C zigux phase2-genksyms");

    try expectLineOnce(workflow, "run: python3 scripts/zigux/check-genksyms-bridge.py --self-test");
    try expectLineOnce(workflow, "run: python3 scripts/zigux/check-genksyms-bridge.py");
    try expectLineOnce(workflow, "run: zig test scripts/zigux/genksyms.zig");
    try expectLineOnce(workflow, "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py --self-test");
    try expectLineOnce(workflow, "run: python3 scripts/zigux/check-phase2-genksyms-selftest-alignment.py");
    try expectLineOnce(workflow, "run: python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py --self-test");
    try expectLineOnce(workflow, "run: python3 scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py");
    try expectLineOnce(workflow, "run: make -C zigux phase2-genksyms");

    try expectLineOnce(makefile, "phase2-genksyms: phase2-toolchain");
    try expectLineOnce(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py --self-test");
    try expectLineOnce(makefile, "cd $(ZIGUX_ROOT) && $(PYTHON) scripts/zigux/check-genksyms-bridge.py");
    try expectLineOnce(makefile, "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) test scripts/zigux/genksyms.zig");
    try expectLineOnce(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py --self-test");
    try expectLineOnce(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-selftest-alignment.py");
    try expectLineOnce(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-dual-implementation-survey.py --self-test");
    try expectLineOnce(makefile, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-genksyms-dual-implementation-survey.py");
}
