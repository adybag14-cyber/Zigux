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

test "semicolon bridge keeps command fields intact across argv and cmdline helpers" {
    var split = try argv_split.argvSplit(
        std.testing.allocator,
        "root=/dev/sda1;rw limit=0x3b;tail flags=boot;fast,irq;shared class=A;z;9 mask=0x3b3b",
    );
    defer freeArgv(std.testing.allocator, &split);

    const argv = argvItems(&split);
    try std.testing.expectEqual(@as(usize, 5), argv.len);
    try std.testing.expectEqualStrings("root=/dev/sda1;rw", argv[0]);
    try std.testing.expectEqualStrings("limit=0x3b;tail", argv[1]);
    try std.testing.expectEqualStrings("flags=boot;fast,irq;shared", argv[2]);
    try std.testing.expectEqualStrings("class=A;z;9", argv[3]);
    try std.testing.expectEqualStrings("mask=0x3b3b", argv[4]);

    if (@hasDecl(cmdline, "nextArg")) {
        const first = cmdline.nextArg("root=/dev/sda1;rw limit=0x3b;tail") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("root", first.param);
        try std.testing.expectEqualStrings("/dev/sda1;rw", first.value.?);
        try std.testing.expectEqualStrings("limit=0x3b;tail", first.remaining);
    }

    const limit = cmdline.memparse(argv[1]["limit=".len..]);
    try std.testing.expectEqual(@as(u64, 0x3b), limit.value);
    try std.testing.expectEqualStrings(";tail", limit.rest);

    const flags = argv[2]["flags=".len..];
    try std.testing.expect(cmdline.parseOptionStr(flags, "boot;fast"));
    try std.testing.expect(cmdline.parse_option_str(flags, "irq;shared"));
    try std.testing.expect(!cmdline.parseOptionStr(flags, "boot"));
    try std.testing.expect(!cmdline.parseOptionStr(flags, "shared"));
}

test "semicolon byte classification and hweight counts stay stable" {
    const class = "A;z;9";
    try std.testing.expect(ctype.isupper(class[0]));
    try std.testing.expect(ctype.ispunct(class[1]));
    try std.testing.expect(ctype.islower(class[2]));
    try std.testing.expect(ctype.ispunct(class[3]));
    try std.testing.expect(ctype.isdigit(class[4]));
    try std.testing.expect(ctype.isgraph(';'));
    try std.testing.expect(ctype.isprint(';'));
    try std.testing.expect(!ctype.isspace(';'));
    try std.testing.expect(!ctype.isalnum(';'));
    try std.testing.expectEqual(@as(u8, 'a'), ctype.tolower(class[0]));
    try std.testing.expectEqual(@as(u8, 'Z'), ctype.toupper(class[2]));
    try std.testing.expectEqual(@as(u8, ';'), ctype.tolower(';'));
    try std.testing.expectEqual(@as(u8, ';'), ctype.toupper(';'));

    const semicolon_byte: u32 = ';';
    const semicolon_pair: u32 = semicolon_byte | (semicolon_byte << 8);
    const semicolon_quad: u32 = semicolon_pair | (semicolon_pair << 16);
    const parsed_mask = cmdline.memparse("0x3b3b");

    try std.testing.expectEqual(@as(u64, 0x3b3b), parsed_mask.value);
    try std.testing.expectEqualStrings("", parsed_mask.rest);
    try std.testing.expectEqual(@as(u32, 5), hweight.swHweight8(semicolon_byte));
    try std.testing.expectEqual(@as(u32, 10), hweight.swHweight16(semicolon_pair));
    try std.testing.expectEqual(@as(u32, 20), hweight.swHweight32(semicolon_quad));
    try std.testing.expectEqual(@as(u32, 10), hweight.swHweight16(@intCast(parsed_mask.value)));
    try std.testing.expectEqual(@as(usize, 10), hweight.hweightLong(@intCast(parsed_mask.value)));

    if (@hasDecl(hweight, "hweight_long")) {
        try std.testing.expectEqual(
            hweight.hweightLong(@intCast(parsed_mask.value)),
            hweight.hweight_long(@intCast(parsed_mask.value)),
        );
    }
}
