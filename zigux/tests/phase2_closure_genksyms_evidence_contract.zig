const std = @import("std");
const testing = std.testing;

const repo_root = ".";

fn readRootFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    const joined = try std.fs.path.join(allocator, &.{ repo_root, path });
    defer allocator.free(joined);
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), joined, allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrder(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

test "phase2 closure keeps current genksyms evidence bounded and replayable" {
    const allocator = testing.allocator;
    const closure = try readRootFile(allocator, "Documentation/zigux/phase2-closure.md");
    defer allocator.free(closure);

    try expectContains(closure, "PHASE2_STATUS=parked");
    try expectContains(closure, "## Current Genksyms Evidence");
    try expectContains(closure, "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    try expectContains(closure, "scripts/zigux/check-genksyms-bridge.py");
    try expectContains(closure, "scripts/zigux/check-phase2-genksyms-selftest-alignment.py");
    try expectContains(closure, "scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py");
    try expectContains(closure, "scripts/zigux/genksyms.zig");
    try expectContains(closure, "zigux/tests/fixtures/genksyms_bridge/manifest.json");
    try expectContains(closure, "abbreviated_unexpected_long_help_argument_expected.json");
    try expectContains(closure, "PHASE2_CURRENT_GENKSYMS_BRIDGE_PACKET=");
    try expectContains(closure, "PHASE2_CURRENT_GENKSYMS_PROCESS_OUTPUT_PACKET=");
    try expectContains(closure, "make -C zigux phase2-genksyms");
    try expectOrder(closure, "## Current Genksyms Evidence", "## Current Shared Repo-Tooling Evidence");
    try expectOrder(closure, "scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py --self-test", "make -C zigux phase2-genksyms");
}

test "genksyms survey checker and manifest match the closure note packet" {
    const allocator = testing.allocator;
    const survey = try readRootFile(allocator, "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    defer allocator.free(survey);
    const checker = try readRootFile(allocator, "scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py");
    defer allocator.free(checker);
    const manifest = try readRootFile(allocator, "zigux/tests/fixtures/genksyms_bridge/manifest.json");
    defer allocator.free(manifest);

    try expectContains(survey, "wrapper bridge and CRC-side dual-implementation evidence both materialized.");
    try expectContains(survey, "Leave this survey parked unless a future reread finds another genksyms-local wording, inventory, or replay drift.");
    try expectContains(checker, "SURVEY_MARKERS = (");
    try expectContains(checker, "PHASE2_GENKSYMS_SURVEY_MARKER_COUNT");
    try expectContains(checker, "EXPECTED_SELF_TEST_CASE_COUNT = 5");
    try expectContains(manifest, "\"case_count\": 11");
    try expectContains(manifest, "\"dash_prefixed_long_option_arguments_as_data_expected.json\"");
    try expectContains(manifest, "\"dash_prefixed_short_option_arguments_as_data_expected.json\"");
    try expectContains(manifest, "\"abbreviated_unexpected_long_help_argument_expected.json\"");
    try expectContains(manifest, "\"scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig\"");
}

test "phase2 genksyms route stays visible in shared reminder surfaces" {
    const allocator = testing.allocator;
    const scripts_readme = try readRootFile(allocator, "scripts/zigux/README.md");
    defer allocator.free(scripts_readme);
    const tests_readme = try readRootFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);
    const makefile = try readRootFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);
    const workflow = try readRootFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try expectContains(scripts_readme, "Documentation/zigux/phase2-genksyms-dual-implementation-survey.md");
    try expectContains(scripts_readme, "scripts/zigux/check-phase2-genksyms-selftest-alignment.py");
    try expectContains(scripts_readme, "make -C zigux phase2-genksyms");
    try expectContains(tests_readme, "scripts/zigux/check-phase2-genksyms-selftest-alignment.py");
    try expectContains(tests_readme, "scripts/zigux/genksyms_repeated_version_before_abbrev_argument_failure_test.zig");
    try expectContains(tests_readme, "zigux/tests/fixtures/genksyms_bridge/manifest.json");
    try expectContains(makefile, "phase2-genksyms: phase2-toolchain");
    try expectContains(makefile, "check-phase2-genksyms-dual-implementation-survey.py");
    try expectContains(workflow, "Self-test current Phase 2 genksyms survey guard");
    try expectContains(workflow, "Run current Phase 2 genksyms make route");
    try expectOrder(workflow, "Check current Phase 2 genksyms survey packet", "Run current Phase 2 genksyms make route");
}
