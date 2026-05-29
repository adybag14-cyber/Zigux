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

test "quoted suffix tokens stay byte-stable across helper ports B" {
    var split = try argv_split.argvSplit(
        std.testing.allocator,
        "root=\"/dev/sda1\" size=64K ro panic=-1",
    );
    defer freeSplit(std.testing.allocator, &split);

    try std.testing.expectEqual(@as(usize, 4), splitArgc(split));
    try std.testing.expectEqualStrings("root=\"/dev/sda1\"", splitArg(split, 0));
    try std.testing.expectEqualStrings("size=64K", splitArg(split, 1));
    try std.testing.expectEqualStrings("ro", splitArg(split, 2));
    try std.testing.expectEqualStrings("panic=-1", splitArg(split, 3));

    try std.testing.expect(cmdline.parseOptionStr("ro,quiet,panic=-1", "ro"));
    try std.testing.expect(cmdline.parseOptionStr("root=\"/dev/sda1\",size=64K", "size=64K"));
    try std.testing.expect(!cmdline.parseOptionStr("root=\"/dev/sda1\",size=64K", "root"));

    const size = cmdline.memparse("64K:ro");
    try std.testing.expectEqual(@as(u64, 64 << 10), size.value);
    try std.testing.expectEqualStrings(":ro", size.rest);
}

test "quote and suffix class masks keep their hweight contract" {
    try std.testing.expect(ctype.ispunct('"'));
    try std.testing.expect(ctype.ispunct('/'));
    try std.testing.expect(ctype.ispunct(':'));
    try std.testing.expect(ctype.isupper('K'));
    try std.testing.expect(ctype.isdigit('4'));
    try std.testing.expect(ctype.isxdigit('f'));

    const quoted_path_mask: u8 = ctype.mask('"') | ctype.mask('/') | ctype.mask(':') | ctype.mask('K');
    try std.testing.expectEqual(ctype._P | ctype._U, quoted_path_mask);
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight8(quoted_path_mask));

    const suffix_digit_mask: u32 = @as(u32, ctype.mask('6')) << 8 | ctype.mask('4') | ctype.mask('f');
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight16(suffix_digit_mask));
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight32(suffix_digit_mask));
}
