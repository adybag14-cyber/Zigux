const std = @import("std");
const contract_options = @import("contract_options");

const smoke_source = contract_options.smoke_source;
const tests_build_source = contract_options.tests_build_source;

fn expectContains(haystack: []const u8, needle: []const u8) !usize {
    const found = std.mem.indexOf(u8, haystack, needle) orelse {
        std.debug.print("missing marker: {s}\n", .{needle});
        return error.MissingMarker;
    };
    return found;
}

fn expectOrdered(before: usize, after: usize) !void {
    try std.testing.expect(before < after);
}

fn expectAbsent(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle)) |_| {
        std.debug.print("unexpected stale marker: {s}\n", .{needle});
        return error.UnexpectedMarker;
    }
}

test "host-tools smoke keeps string imports and build wiring explicit" {
    const smoke_import = try expectContains(smoke_source, "const string = @import(\"string\");");
    const behavior_test = try expectContains(smoke_source, "test \"phase1 host-tools smoke exercises live helper behavior\"");
    try expectOrdered(smoke_import, behavior_test);

    const string_module = try expectContains(tests_build_source, "const string_module = b.createModule(.{");
    const string_path = try expectContains(tests_build_source, ".root_source_file = b.path(\"../../tools/lib/string.zig\"),");
    const cmdline_dependency = try expectContains(tests_build_source, "string_module.addImport(\"cmdline\", cmdline_module);");
    const root_import = try expectContains(tests_build_source, "root_module.addImport(\"string\", string_module);");

    try expectOrdered(string_module, string_path);
    try expectOrdered(string_path, cmdline_dependency);
    try expectOrdered(cmdline_dependency, root_import);
    _ = try expectContains(tests_build_source, ".name = \"phase1-host-tools-smoke\",");

    try expectAbsent(tests_build_source, "root_module.addImport(\"string\", cmdline_module);");
    try expectAbsent(tests_build_source, "../../tools/lib/string_phase1_strlcat_test.zig\"),\n        .target = target,\n        .optimize = optimize,\n    });\n    root_module.addImport(\"string\"");
}

test "host-tools smoke keeps string copy and append anchors together" {
    const pad_anchor = try expectContains(smoke_source, "try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, \"hi\"));");
    const pad_bytes = try expectContains(smoke_source, "try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 0, 0, 0, 0 }, &padded);");
    const append_anchor = try expectContains(smoke_source, "try std.testing.expectEqual(@as(usize, 5), string.strlcat(appended[0..], \"all\"));");
    const append_bytes = try expectContains(smoke_source, "try std.testing.expectEqualSlices(u8, &[_]u8{ 'h', 'i', 'a', 'l', 'l', 0 }, appended[0..]);");
    const truncated_anchor = try expectContains(smoke_source, "try std.testing.expectEqual(@as(usize, 6), string.strlcat(truncated_append[0..], \"cdef\"));");
    const truncated_bytes = try expectContains(smoke_source, "try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', 'c', 0 }, truncated_append[0..]);");

    try expectOrdered(pad_anchor, pad_bytes);
    try expectOrdered(pad_bytes, append_anchor);
    try expectOrdered(append_anchor, append_bytes);
    try expectOrdered(append_bytes, truncated_anchor);
    try expectOrdered(truncated_anchor, truncated_bytes);
}

test "host-tools smoke keeps string match and search boundary anchors ordered" {
    const sysfs_table = try expectContains(smoke_source, "const sysfs = [_][]const u8{ \"disabled\", \"auto\\n\", \"manual\" };");
    const sysfs_match = try expectContains(smoke_source, "try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs, \"auto\"));");
    const sysfs_streq = try expectContains(smoke_source, "try std.testing.expect(string.sysfs_streq(\"auto\\n\", \"auto\"));");
    const lookup_table = try expectContains(smoke_source, "const lookup = [_][]const u8{ \"disabled\", \"manual\", \"manual\", \"auto\" };");
    const match_string = try expectContains(smoke_source, "try std.testing.expectEqual(@as(?usize, 3), string.match_string(&lookup, &lookup_cstr));");
    const counted = try expectContains(smoke_source, "const counted = [_]u8{ 'a', 'b', 0, 'c', 'd' };");
    const strnchr_nul = try expectContains(smoke_source, "try std.testing.expectEqual(@as(usize, 2), string.strnchrNul(&counted, counted.len, 'z'));");
    const strspn = try expectContains(smoke_source, "try std.testing.expectEqual(@as(usize, 4), string.strspn(\"abba!\", \"ab\"));");
    const terminator = try expectContains(smoke_source, "const terminator_clamped = [_]u8{ 'a', 0, 'b', 'c' };");
    const strchrnul = try expectContains(smoke_source, "try std.testing.expectEqual(@as(usize, 2), string.strchrnul(\"abcz\", 'c'));");

    try expectOrdered(sysfs_table, sysfs_match);
    try expectOrdered(sysfs_match, sysfs_streq);
    try expectOrdered(sysfs_streq, lookup_table);
    try expectOrdered(lookup_table, match_string);
    try expectOrdered(match_string, counted);
    try expectOrdered(counted, strnchr_nul);
    try expectOrdered(strnchr_nul, strspn);
    try expectOrdered(strspn, terminator);
    try expectOrdered(terminator, strchrnul);

    try expectAbsent(smoke_source, "string.strnchr(&counted, counted.len, 'c'));\n    try std.testing.expectEqual(@as(?usize, 2)");
}
