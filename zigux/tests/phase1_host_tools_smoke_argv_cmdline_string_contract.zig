const std = @import("std");
const options = @import("phase1_host_tools_smoke_argv_cmdline_string_options");

const smoke_source = options.smoke_source;
const tests_build = options.tests_build;

const helper_imports = [_][]const u8{
    "const argv_split = @import(\"argv_split\");",
    "const cmdline = @import(\"cmdline\");",
    "const string = @import(\"string\");",
};

const build_imports = [_][]const u8{
    "const argv_split_module = b.createModule(.{",
    ".root_source_file = b.path(\"../../tools/lib/argv_split.zig\"),",
    "const cmdline_module = b.createModule(.{",
    ".root_source_file = b.path(\"../../tools/lib/cmdline.zig\"),",
    "const string_module = b.createModule(.{",
    ".root_source_file = b.path(\"../../tools/lib/string.zig\"),",
    "string_module.addImport(\"cmdline\", cmdline_module);",
    "root_module.addImport(\"argv_split\", argv_split_module);",
    "root_module.addImport(\"cmdline\", cmdline_module);",
    "root_module.addImport(\"string\", string_module);",
};

const argv_markers = [_][]const u8{
    "var split = try argv_split.argv_split(std.testing.allocator, \"  zigux   host\\ttools  \ ");",
    "defer argv_split.argv_free(&split);",
    "try std.testing.expectEqual(@as(usize, 3), split.argc());",
    "try std.testing.expectEqualStrings(\"zigux\", split.argv[0]);",
    "try std.testing.expectEqualStrings(\"host\", split.argv[1]);",
    "try std.testing.expectEqualStrings(\"tools\", split.argv[2]);",
};

const cmdline_markers = [_][]const u8{
    "const parsed = cmdline.memparse(\"64K tail\");",
    "const signed = cmdline.memparse(\"-2K tail\");",
    "const saturated = cmdline.memparse(\"+9223372036854775808\");",
    "const hexadecimal = cmdline.memparse(\"0x20M\");",
    "const octal = cmdline.memparse(\"010K\");",
    "const invalid = cmdline.memparse(\"xyz\");",
    "try std.testing.expect(cmdline.parseOptionStr(\"rootwait,quiet\", \"quiet\"));",
    "try std.testing.expect(cmdline.parseOptionStr(\"rootwait,,quiet\", \"\"));",
    "const keyed = cmdline.nextArg(\"console=ttyS0,115200 root=\\\"/dev/sda1 quiet\\\" panic=-1\") orelse return error.TestUnexpectedResult;",
    "const quoted = cmdline.nextArg(\"\\\"mode=fast path\\\" tail\") orelse return error.TestUnexpectedResult;",
    "const unterminated = cmdline.nextArg(\"mode=\\\"fast boot\") orelse return error.TestUnexpectedResult;",
};

const string_markers = [_][]const u8{
    "var padded: [6]u8 = @splat(0xaa);",
    "try std.testing.expectEqual(@as(isize, 2), string.strscpyPad(&padded, \"hi\"));",
    "try std.testing.expectEqual(@as(usize, 5), string.strlcat(appended[0..], \"all\"));",
    "try std.testing.expectEqual(@as(usize, 6), string.strlcat(truncated_append[0..], \"cdef\"));",
    "try std.testing.expectEqual(@as(?usize, 1), string.sysfsMatchString(&sysfs, \"auto\"));",
    "try std.testing.expect(string.sysfs_streq(\"auto\\n\", \"auto\"));",
    "try std.testing.expectEqual(@as(?usize, 1), string.matchString(&lookup, \"manual\"));",
    "try std.testing.expectEqual(@as(?usize, 3), string.match_string(&lookup, &lookup_cstr));",
    "try std.testing.expectEqual(@as(?usize, 1), string.strnchr(&counted, counted.len, 'b'));",
    "try std.testing.expectEqual(@as(?usize, null), string.strnchr(&counted, counted.len, 'c'));",
    "try std.testing.expectEqual(@as(usize, 2), string.strnchrNul(&counted, counted.len, 'z'));",
    "try std.testing.expectEqual(@as(usize, 1), string.strnchrnul(&counted, counted.len, 'b'));",
    "try std.testing.expectEqual(@as(usize, 4), string.strspn(\"abba!\", \"ab\"));",
    "try std.testing.expectEqual(@as(usize, 1), string.strchrNul(&terminator_clamped, 'z'));",
    "try std.testing.expectEqual(@as(usize, 2), string.strchrnul(\"abcz\", 'c'));",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOf(u8, haystack[cursor..], needle) orelse return error.MissingMarker;
        cursor += found + needle.len;
    }
}

fn expectUnique(haystack: []const u8, needle: []const u8) !void {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingMarker;
    try std.testing.expect(std.mem.indexOf(u8, haystack[first + needle.len ..], needle) == null);
}

test "phase1 host-tools smoke imports argv cmdline and string helpers" {
    for (helper_imports) |marker| {
        try expectContains(smoke_source, marker);
    }
    for (build_imports) |marker| {
        try expectContains(tests_build, marker);
    }

    try expectOrdered(tests_build, &.{
        "const argv_split_module = b.createModule(.{",
        "const cmdline_module = b.createModule(.{",
        "const string_module = b.createModule(.{",
        "string_module.addImport(\"cmdline\", cmdline_module);",
        "root_module.addImport(\"argv_split\", argv_split_module);",
        "root_module.addImport(\"cmdline\", cmdline_module);",
        "root_module.addImport(\"string\", string_module);",
    });
}

test "phase1 host-tools smoke keeps argv and cmdline coverage markers" {
    try expectOrdered(smoke_source, &argv_markers);
    try expectOrdered(smoke_source, &cmdline_markers);

    for (argv_markers ++ cmdline_markers) |marker| {
        try expectUnique(smoke_source, marker);
    }
}

test "phase1 host-tools smoke keeps string edge coverage markers" {
    try expectOrdered(smoke_source, &string_markers);

    for (string_markers) |marker| {
        try expectUnique(smoke_source, marker);
    }
}
