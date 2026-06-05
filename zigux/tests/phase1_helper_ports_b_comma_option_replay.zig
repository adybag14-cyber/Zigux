const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn hasDecl(comptime Container: type, comptime name: []const u8) bool {
    return switch (@typeInfo(Container)) {
        .@"struct", .@"enum", .@"union", .@"opaque" => @hasDecl(Container, name),
        else => false,
    };
}

fn hasField(comptime Container: type, comptime name: []const u8) bool {
    return switch (@typeInfo(Container)) {
        .@"struct", .@"union" => @hasField(Container, name),
        else => false,
    };
}

fn splitArgv(result: anytype) [][]u8 {
    const Result = @TypeOf(result);
    if (comptime hasField(Result, "argv")) {
        return result.argv;
    }

    return result;
}

fn splitArgc(result: anytype) usize {
    const Result = @TypeOf(result);
    if (comptime hasDecl(Result, "argc")) {
        return result.argc();
    }

    return splitArgv(result).len;
}

fn freeSplit(allocator: std.mem.Allocator, result: anytype) void {
    const Result = @typeInfo(@TypeOf(result)).pointer.child;
    if (comptime hasDecl(Result, "deinit")) {
        result.deinit();
    } else {
        argv_split.argvFree(allocator, result.*);
    }
}

fn punctuationMask(token: []const u8) u32 {
    var mask: u32 = 0;
    for (token, 0..) |ch, idx| {
        if (ctype.ispunct(ch)) {
            mask |= @as(u32, 1) << @intCast(idx);
        }
    }
    return mask;
}

test "helper ports B preserve comma option tokens and punctuation masks" {
    var parsed = try argv_split.argvSplit(std.testing.allocator, " quiet,debug=1,,panic=5 0x2K,mask ");
    defer freeSplit(std.testing.allocator, &parsed);

    const argv = splitArgv(parsed);
    try std.testing.expectEqual(@as(usize, 2), splitArgc(parsed));
    try std.testing.expectEqualStrings("quiet,debug=1,,panic=5", argv[0]);
    try std.testing.expectEqualStrings("0x2K,mask", argv[1]);

    try std.testing.expect(cmdline.parseOptionStr(argv[0], "quiet"));
    try std.testing.expect(cmdline.parse_option_str(argv[0], ""));
    try std.testing.expect(!cmdline.parseOptionStr(argv[0], "debug"));
    try std.testing.expect(!cmdline.parseOptionStr(argv[0], "panic"));
    try std.testing.expect(!cmdline.parseOptionStr(argv[0], "mask"));

    const parsed_size = cmdline.memparse(argv[1]);
    try std.testing.expectEqual(@as(u64, 2 << 10), parsed_size.value);
    try std.testing.expectEqualStrings(",mask", parsed_size.rest);

    const option_mask = punctuationMask(argv[0]);
    try std.testing.expectEqual(@as(u32, 0x10_6820), option_mask);
    try std.testing.expectEqual(@as(u32, 5), hweight.swHweight32(option_mask));
    if (@hasDecl(hweight, "__sw_hweight32")) {
        try std.testing.expectEqual(@as(u32, 5), hweight.__sw_hweight32(option_mask));
    }

    try std.testing.expect(ctype.ispunct(','));
    try std.testing.expect(ctype.ispunct('='));
    try std.testing.expect(!ctype.isspace(','));
    try std.testing.expect(!ctype.isalnum('='));
}
