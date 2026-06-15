const std = @import("std");

const argv_split = @import("./argv_split.zig");
const cmdline = @import("./cmdline.zig");
const ctype = @import("./ctype.zig");
const hweight = @import("./hweight.zig");

fn argvItems(result: anytype) [][]u8 {
    const result_ptr = @typeInfo(@TypeOf(result)).pointer;
    const result_info = @typeInfo(result_ptr.child);
    return switch (result_info) {
        .@"struct" => result.argv,
        .pointer => result.*,
        else => @compileError("unsupported argvSplit result shape"),
    };
}

fn freeArgv(allocator: std.mem.Allocator, result: anytype) void {
    const result_ptr = @typeInfo(@TypeOf(result)).pointer;
    const result_info = @typeInfo(result_ptr.child);
    switch (result_info) {
        .@"struct" => result.deinit(),
        .pointer => argv_split.argvFree(allocator, result.*),
        else => @compileError("unsupported argvSplit result shape"),
    }
}

fn hweight8(value: u32) u32 {
    return if (@hasDecl(hweight, "hweight8"))
        hweight.hweight8(value)
    else
        hweight.swHweight8(value);
}

test "slash path payloads stay intact across argv and cmdline helpers" {
    var split = try argv_split.argvSplit(
        std.testing.allocator,
        "root=/dev/sda1//boot init=/sbin/init loglevel=4",
    );
    defer freeArgv(std.testing.allocator, &split);

    const argv = argvItems(&split);
    try std.testing.expectEqual(@as(usize, 3), argv.len);
    try std.testing.expectEqualStrings("root=/dev/sda1//boot", argv[0]);
    try std.testing.expectEqualStrings("init=/sbin/init", argv[1]);
    try std.testing.expectEqualStrings("loglevel=4", argv[2]);

    const parsed_size = cmdline.memparse("0x2f/rest");
    try std.testing.expectEqual(@as(u64, 0x2f), parsed_size.value);
    try std.testing.expectEqualStrings("/rest", parsed_size.rest);

    try std.testing.expect(cmdline.parseOptionStr("ro,/dev/sda1//boot,noexec", "/dev/sda1//boot"));
    try std.testing.expect(!cmdline.parse_option_str("root=/dev/sda1//boot,ro", "/dev/sda1//boot"));
    try std.testing.expect(!cmdline.parseOptionStr("root=/dev/sda1//boot,ro", "root"));

    if (@hasDecl(cmdline, "nextArg")) {
        const arg = cmdline.nextArg("root=/dev/sda1//boot quiet") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("root", arg.param);
        try std.testing.expectEqualStrings("/dev/sda1//boot", arg.value.?);
        try std.testing.expectEqualStrings("quiet", arg.remaining);
    }
}

test "slash bytes keep punctuation classification and stable hweight counts" {
    try std.testing.expect(ctype.ispunct('/'));
    try std.testing.expect(ctype.isgraph('/'));
    try std.testing.expect(ctype.isprint('/'));
    try std.testing.expect(!ctype.isspace('/'));
    try std.testing.expect(!ctype.isalnum('/'));
    try std.testing.expect(!ctype.isxdigit('/'));
    try std.testing.expectEqual(ctype._P, ctype.mask('/') & ctype._P);

    const slash_byte: u32 = '/';
    const slash_pair: u32 = slash_byte | (slash_byte << 8);
    const slash_quad: u32 = slash_pair | (slash_pair << 16);

    try std.testing.expectEqual(@as(u32, 5), hweight.swHweight8(slash_byte));
    try std.testing.expectEqual(@as(u32, 5), hweight8(slash_byte));
    try std.testing.expectEqual(@as(u32, 10), hweight.swHweight16(slash_pair));
    try std.testing.expectEqual(@as(u32, 20), hweight.swHweight32(slash_quad));
}
