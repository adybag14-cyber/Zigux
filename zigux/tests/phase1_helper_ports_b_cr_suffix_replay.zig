const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn resultHasArgv(comptime T: type) bool {
    return switch (@typeInfo(T)) {
        .@"struct" => @hasField(T, "argv"),
        else => false,
    };
}

fn typeHasDecl(comptime T: type, comptime name: []const u8) bool {
    return switch (@typeInfo(T)) {
        .@"struct", .@"enum", .@"union", .@"opaque" => @hasDecl(T, name),
        else => false,
    };
}

fn argvItems(result: anytype) []const []u8 {
    const T = @TypeOf(result);
    if (comptime resultHasArgv(T)) {
        return result.argv;
    }
    return result;
}

fn argvCount(result: anytype) usize {
    const T = @TypeOf(result);
    if (comptime (resultHasArgv(T) and typeHasDecl(T, "argc"))) {
        return result.argc();
    }
    return argvItems(result).len;
}

fn freeArgv(allocator: std.mem.Allocator, result: anytype) void {
    const Child = @typeInfo(@TypeOf(result)).pointer.child;
    if (comptime typeHasDecl(Child, "deinit")) {
        result.deinit();
    } else if (comptime resultHasArgv(Child)) {
        argv_split.argvFree(result);
    } else {
        argv_split.argvFree(allocator, result.*);
    }
}

fn hweight8(value: u32) u32 {
    if (@hasDecl(hweight, "__sw_hweight8")) {
        return hweight.__sw_hweight8(value);
    }
    return hweight.swHweight8(value);
}

fn hweight32(value: u32) u32 {
    if (@hasDecl(hweight, "__sw_hweight32")) {
        return hweight.__sw_hweight32(value);
    }
    return hweight.swHweight32(value);
}

test "carriage-return separated argv tokens keep suffix rest boundaries" {
    const input = "root=/dev/sda1\rsize=4Ktail\rdebug";
    var split = try argv_split.argvSplit(std.testing.allocator, input);
    defer freeArgv(std.testing.allocator, &split);

    const argv = argvItems(split);
    try std.testing.expectEqual(@as(usize, 3), argvCount(split));
    try std.testing.expectEqualStrings("root=/dev/sda1", argv[0]);
    try std.testing.expectEqualStrings("size=4Ktail", argv[1]);
    try std.testing.expectEqualStrings("debug", argv[2]);

    const parsed_size = cmdline.memparse(argv[1]["size=".len..]);
    try std.testing.expectEqual(@as(u64, 4 << 10), parsed_size.value);
    try std.testing.expectEqualStrings("tail", parsed_size.rest);

    try std.testing.expect(ctype.isspace('\r'));
    try std.testing.expect(ctype.iscntrl('\r'));
    try std.testing.expect(!ctype.isprint('\r'));
    try std.testing.expectEqual(@as(u32, 2), hweight8(ctype.mask('\r')));
}

test "cr-delimited command line surfaces parse options and masks independently" {
    const option_text = "quiet,trace\rdebug";
    try std.testing.expect(cmdline.parseOptionStr(option_text, "quiet"));
    try std.testing.expect(!cmdline.parseOptionStr(option_text, "debug"));

    var class_mask: u32 = 0;
    const bytes = [_]u8{ 'K', '7', '\r', ',' };
    for (bytes, 0..) |byte, idx| {
        if (ctype.isupper(byte) or ctype.isdigit(byte) or ctype.isspace(byte) or ctype.ispunct(byte)) {
            class_mask |= @as(u32, 1) << @intCast(idx);
        }
    }
    try std.testing.expectEqual(@as(u32, 4), hweight32(class_mask));

    if (@hasDecl(cmdline, "nextArg")) {
        const first = cmdline.nextArg("root=4Ktail\rdebug") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("root", first.param);
        try std.testing.expectEqualStrings("4Ktail", first.value.?);
        try std.testing.expectEqualStrings("debug", first.remaining);

        const parsed = cmdline.memparse(first.value.?);
        try std.testing.expectEqual(@as(u64, 4 << 10), parsed.value);
        try std.testing.expectEqualStrings("tail", parsed.rest);
    }
}
