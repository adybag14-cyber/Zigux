const std = @import("std");

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(2 * 1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

test "lane11 fixdep dual packet keeps C Zig and checker anchors together" {
    const allocator = std.testing.allocator;
    const c_fixdep = try readRepoFile(allocator, "scripts/basic/fixdep.c");
    defer allocator.free(c_fixdep);
    const zig_fixdep = try readRepoFile(allocator, "scripts/zigux/fixdep.zig");
    defer allocator.free(zig_fixdep);
    const diff_checker = try readRepoFile(allocator, "scripts/zigux/check-fixdep-diff.py");
    defer allocator.free(diff_checker);
    const gate_checker = try readRepoFile(allocator, "scripts/zigux/check-phase2-fixdep-gate.py");
    defer allocator.free(gate_checker);

    try expectContains(c_fixdep, "parse_dep_file");
    try expectContains(c_fixdep, "parse_config_file");
    try expectContains(c_fixdep, "CONFIG_");

    try expectContains(zig_fixdep, "pub fn runFixdep");
    try expectContains(zig_fixdep, "fn parseDepFile");
    try expectContains(zig_fixdep, "fn parseConfigFile");
    try expectContains(zig_fixdep, "fn isNoParseFile");
    try expectContains(zig_fixdep, "bytesBeforeFirstNull");
    try expectContains(zig_fixdep, "include/generated/autoconf.h");

    try expectContains(diff_checker, "EXPECTED_CASES");
    try expectContains(diff_checker, "EXPECTED_ZIG_FIXDEP");
    try expectContains(diff_checker, "fixdep.zig");
    try expectContains(diff_checker, "FIXDEP_DIFF=pass");
    try expectContains(diff_checker, "FIXDEP_DETERMINISM=pass");

    try expectContains(gate_checker, "check-fixdep-diff.py");
    try expectContains(gate_checker, "PHASE2_FIXDEP_GATE_SELF_TEST=pass");
    try expectContains(gate_checker, "scripts/basic/fixdep.c");
    try expectContains(gate_checker, "scripts/zigux/fixdep.zig");
}

test "lane11 fixdep fixture roster preserves the 13 case dual replay surface" {
    const allocator = std.testing.allocator;
    const cases_json = try readRepoFile(allocator, "zigux/tests/fixtures/fixdep/cases.json");
    defer allocator.free(cases_json);

    const expected_names = [_][]const u8{
        "\"name\": \"sample\"",
        "\"name\": \"sample_multi_target\"",
        "\"name\": \"sample_escaped_space\"",
        "\"name\": \"sample_escaped_colon\"",
        "\"name\": \"sample_concatenated\"",
        "\"name\": \"sample_dependency_continuation\"",
        "\"name\": \"sample_comment_continuation\"",
        "\"name\": \"sample_double_backslash_comment\"",
        "\"name\": \"sample_comment_only\"",
        "\"name\": \"sample_comment_only_stdout_full\"",
        "\"name\": \"sample_missing_dep\"",
        "\"name\": \"sample_missing_dep_stdout_full\"",
        "\"name\": \"sample_output_write\"",
    };

    try std.testing.expectEqual(@as(usize, expected_names.len), countNeedle(cases_json, "\"name\":"));
    for (expected_names) |name| {
        try expectContains(cases_json, name);
    }

    try expectContains(cases_json, "\"expected_exit_code\": 0");
    try expectContains(cases_json, "\"expected_exit_code\": 1");
    try expectContains(cases_json, "\"expected_exit_code\": 2");
    try std.testing.expectEqual(@as(usize, 3), countNeedle(cases_json, "\"stdout_mode\": \"dev_full\""));
}
