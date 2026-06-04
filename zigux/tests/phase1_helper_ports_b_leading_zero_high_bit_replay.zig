const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn splitHasStructResult(comptime Split: type) bool {
    return switch (@typeInfo(Split)) {
        .@"struct" => @hasField(Split, "argv"),
        else => false,
    };
}

fn splitArgc(split: anytype) usize {
    const Split = @TypeOf(split);
    if (comptime splitHasStructResult(Split)) {
        return split.argc();
    }
    return split.len;
}

fn splitArg(split: anytype, index: usize) []const u8 {
    const Split = @TypeOf(split);
    if (comptime splitHasStructResult(Split)) {
        return split.argv[index];
    }
    return split[index];
}

fn freeSplit(allocator: std.mem.Allocator, split: anytype) void {
    const Ptr = @TypeOf(split);
    const Split = @typeInfo(Ptr).pointer.child;
    if (comptime splitHasStructResult(Split)) {
        split.deinit();
    } else {
        argv_split.argvFree(allocator, split.*);
    }
}

test "helper ports B keep leading-zero and high-bit boundaries aligned" {
    const allocator = std.testing.allocator;
    var split = try argv_split.argvSplit(allocator, "  0 08 0x10 0Xf 0xff\x80tail \x80solo  ");
    defer freeSplit(allocator, &split);

    try std.testing.expectEqual(@as(usize, 6), splitArgc(split));
    try std.testing.expectEqualStrings("0", splitArg(split, 0));
    try std.testing.expectEqualStrings("08", splitArg(split, 1));
    try std.testing.expectEqualStrings("0x10", splitArg(split, 2));
    try std.testing.expectEqualStrings("0Xf", splitArg(split, 3));
    try std.testing.expectEqualStrings("0xff\x80tail", splitArg(split, 4));
    try std.testing.expectEqualStrings("\x80solo", splitArg(split, 5));

    const zero = cmdline.memparse(splitArg(split, 0));
    try std.testing.expectEqual(@as(u64, 0), zero.value);
    try std.testing.expectEqualStrings("", zero.rest);

    const octal_boundary = cmdline.memparse(splitArg(split, 1));
    try std.testing.expectEqual(@as(u64, 0), octal_boundary.value);
    try std.testing.expectEqualStrings("8", octal_boundary.rest);

    const hex_lower = cmdline.memparse(splitArg(split, 2));
    try std.testing.expectEqual(@as(u64, 16), hex_lower.value);
    try std.testing.expectEqualStrings("", hex_lower.rest);

    const hex_upper = cmdline.memparse(splitArg(split, 3));
    try std.testing.expectEqual(@as(u64, 15), hex_upper.value);
    try std.testing.expectEqualStrings("", hex_upper.rest);

    const high_tail = cmdline.memparse(splitArg(split, 4));
    try std.testing.expectEqual(@as(u64, 255), high_tail.value);
    try std.testing.expectEqualStrings("\x80tail", high_tail.rest);
    try std.testing.expect(!ctype.isascii(high_tail.rest[0]));
    try std.testing.expect(!ctype.isprint(high_tail.rest[0]));
    try std.testing.expectEqual(@as(u8, 0), ctype.mask(high_tail.rest[0]));

    try std.testing.expect(!ctype.isascii(splitArg(split, 5)[0]));
    try std.testing.expectEqual(@as(u8, 0), ctype.toascii(splitArg(split, 5)[0]));
}

test "helper ports B count the same leading-zero token windows" {
    const windows = [_][]const u8{
        "0",
        "08",
        "0x10",
        "0Xf",
        "0xff\x80tail",
        "\x80solo",
    };

    var combined_low_lane: u32 = 0;
    var combined_ascii_mask: u64 = 0;
    for (windows, 0..) |window, index| {
        const parsed = cmdline.memparse(window);
        if (parsed.rest.len == 0) {
            combined_low_lane |= @as(u32, 1) << @intCast(index);
        }
        if (ctype.isascii(window[0])) {
            combined_ascii_mask |= @as(u64, 1) << @intCast(index * 8);
        }
    }

    try std.testing.expectEqual(@as(u32, 3), hweight.swHweight8(combined_low_lane));
    try std.testing.expectEqual(@as(u32, 3), hweight.swHweight16(combined_low_lane));
    try std.testing.expectEqual(@as(u32, 3), hweight.swHweight32(combined_low_lane));
    try std.testing.expectEqual(@as(u64, 5), hweight.swHweight64(combined_ascii_mask));
    try std.testing.expectEqual(@as(usize, 3), hweight.hweightLong(combined_low_lane));
}
