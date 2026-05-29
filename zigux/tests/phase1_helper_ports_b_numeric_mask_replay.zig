const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn expectSplit(result: argv_split.ArgvSplitResult, expected: []const []const u8) !void {
    try std.testing.expectEqual(expected.len, result.argc());
    try std.testing.expectEqual(expected.len, result.argv.len);
    for (expected, 0..) |expected_arg, idx| {
        try std.testing.expectEqualStrings(expected_arg, result.argv[idx]);
    }
}

fn classMask(text: []const u8) u32 {
    var mask: u32 = 0;
    for (text) |ch| {
        if (ctype.isdigit(ch)) {
            mask |= 1 << 0;
        }
        if (ctype.isxdigit(ch)) {
            mask |= 1 << 1;
        }
        if (ctype.isalpha(ch)) {
            mask |= 1 << 2;
        }
        if (ctype.ispunct(ch)) {
            mask |= 1 << 3;
        }
        if (ctype.isspace(ch)) {
            mask |= 1 << 4;
        }
    }
    return mask;
}

test "numeric helper flow keeps split parse and byte masks aligned" {
    const first = cmdline.nextArg("payload=\"0x2d 0755K Az_9\" tail=-4K mode=fast") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("payload", first.param);
    try std.testing.expectEqualStrings("0x2d 0755K Az_9", first.value.?);

    var parts = try argv_split.argvSplit(std.testing.allocator, first.value.?);
    defer parts.deinit();
    try expectSplit(parts, &.{ "0x2d", "0755K", "Az_9" });

    const hex = cmdline.memparse(parts.argv[0]);
    try std.testing.expectEqual(@as(u64, 0x2d), hex.value);
    try std.testing.expectEqualStrings("", hex.rest);

    const octal_k = cmdline.memparse(parts.argv[1]);
    try std.testing.expectEqual(@as(u64, 0o755 << 10), octal_k.value);
    try std.testing.expectEqualStrings("", octal_k.rest);

    try std.testing.expectEqual(@as(u32, 0b0111), classMask(parts.argv[0]));
    try std.testing.expectEqual(@as(u32, 0b0111), classMask(parts.argv[1]));
    try std.testing.expectEqual(@as(u32, 0b1111), classMask(parts.argv[2]));

    const combined = classMask(parts.argv[0]) | (classMask(parts.argv[1]) << 8) | (classMask(parts.argv[2]) << 16);
    try std.testing.expectEqual(@as(u32, 10), hweight.swHweight32(combined));
    try std.testing.expectEqual(@as(u32, 3), hweight.swHweight8(classMask(parts.argv[0])));
    try std.testing.expectEqual(@as(usize, 10), hweight.hweightLong(@intCast(combined)));

    const second = cmdline.nextArg(first.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("tail", second.param);
    try std.testing.expectEqualStrings("-4K", second.value.?);
    const tail = cmdline.memparse(second.value.?);
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -4096))), tail.value);
    try std.testing.expectEqualStrings("", tail.rest);
}

test "numeric helper flow preserves rest bytes and delimiter classes" {
    const parsed = cmdline.nextArg("range=128M,done flags=quiet") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("range", parsed.param);
    try std.testing.expectEqualStrings("128M,done", parsed.value.?);
    try std.testing.expectEqualStrings("flags=quiet", parsed.remaining);

    const value = cmdline.memparse(parsed.value.?);
    try std.testing.expectEqual(@as(u64, 128 << 20), value.value);
    try std.testing.expectEqualStrings(",done", value.rest);

    var suffix_parts = try argv_split.argv_split(std.testing.allocator, value.rest[1..]);
    defer argv_split.argv_free(&suffix_parts);
    try expectSplit(suffix_parts, &.{"done"});

    try std.testing.expect(ctype.ispunct(value.rest[0]));
    try std.testing.expect(!ctype.isspace(value.rest[0]));
    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight8(classMask(value.rest[0..1])));
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight8(classMask(suffix_parts.argv[0])));
}
