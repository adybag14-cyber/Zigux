const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn splitArgc(result: anytype) usize {
    return switch (@typeInfo(@TypeOf(result))) {
        .@"struct" => result.argc(),
        else => result.len,
    };
}

fn splitArg(result: anytype, idx: usize) []const u8 {
    return switch (@typeInfo(@TypeOf(result))) {
        .@"struct" => result.argv[idx],
        else => result[idx],
    };
}

fn freeSplit(allocator: std.mem.Allocator, result: anytype) void {
    return switch (@typeInfo(@TypeOf(result.*))) {
        .@"struct" => result.deinit(),
        else => argv_split.argvFree(allocator, result.*),
    };
}

test "separator-heavy tokens stay verbatim across helper ports B" {
    var split = try argv_split.argvSplit(
        std.testing.allocator,
        "\r\troot=UUID=abcd-1234\x0cconsole=ttyS0,115200\nquiet",
    );
    defer freeSplit(std.testing.allocator, &split);

    try std.testing.expectEqual(@as(usize, 3), splitArgc(split));
    try std.testing.expectEqualStrings("root=UUID=abcd-1234", splitArg(split, 0));
    try std.testing.expectEqualStrings("console=ttyS0,115200", splitArg(split, 1));
    try std.testing.expectEqualStrings("quiet", splitArg(split, 2));

    try std.testing.expect(cmdline.parseOptionStr("root=UUID=abcd-1234,console,quiet", "console"));
    try std.testing.expect(cmdline.parseOptionStr("root=UUID=abcd-1234,console,quiet", "quiet"));
    try std.testing.expect(!cmdline.parseOptionStr("root=UUID=abcd-1234,console,quiet", "root"));

    const mem = cmdline.memparse("115200,8n1");
    try std.testing.expectEqual(@as(u64, 115200), mem.value);
    try std.testing.expectEqualStrings(",8n1", mem.rest);
}

test "separator classification masks have stable hweight shape" {
    try std.testing.expect(ctype.isspace('\r'));
    try std.testing.expect(ctype.isspace('\x0c'));
    try std.testing.expect(ctype.iscntrl('\r'));
    try std.testing.expect(ctype.iscntrl('\x0c'));
    try std.testing.expect(ctype.ispunct('='));
    try std.testing.expect(ctype.ispunct(','));
    try std.testing.expect(ctype.isxdigit('f'));
    try std.testing.expect(!ctype.isalnum('_'));

    const separator_mask: u8 = ctype.mask('\r') | ctype.mask('=') | ctype.mask('f');
    try std.testing.expectEqual(ctype._C | ctype._S | ctype._P | ctype._L | ctype._X, separator_mask);
    try std.testing.expectEqual(@as(u32, 5), hweight.swHweight8(separator_mask));

    const token_mask: u32 = @as(u32, ctype.mask('A')) << 8 | ctype.mask('7');
    try std.testing.expectEqual(@as(u32, 3), hweight.swHweight16(token_mask));
    try std.testing.expectEqual(@as(u32, 3), hweight.swHweight32(token_mask));
}
