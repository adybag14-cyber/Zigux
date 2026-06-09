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

test "pipe-delimited fields stay intact across argv split and cmdline parsing" {
    var split = try argv_split.argvSplit(
        std.testing.allocator,
        "pipe=a|b|c addr=0x7c|0x20 flags=left|right,debug|pipe class=A|z|5 mask=0x7c7c",
    );
    defer freeArgv(std.testing.allocator, &split);

    const argv = argvItems(&split);
    try std.testing.expectEqual(@as(usize, 5), argv.len);
    try std.testing.expectEqualStrings("pipe=a|b|c", argv[0]);
    try std.testing.expectEqualStrings("addr=0x7c|0x20", argv[1]);
    try std.testing.expectEqualStrings("flags=left|right,debug|pipe", argv[2]);
    try std.testing.expectEqualStrings("class=A|z|5", argv[3]);
    try std.testing.expectEqualStrings("mask=0x7c7c", argv[4]);

    if (@hasDecl(cmdline, "nextArg")) {
        const first = cmdline.nextArg("pipe=a|b|c addr=0x7c|0x20") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("pipe", first.param);
        try std.testing.expectEqualStrings("a|b|c", first.value.?);
        try std.testing.expectEqualStrings("addr=0x7c|0x20", first.remaining);
    }

    const addr_first = cmdline.memparse(argv[1]["addr=".len..]);
    try std.testing.expectEqual(@as(u64, 0x7c), addr_first.value);
    try std.testing.expectEqualStrings("|0x20", addr_first.rest);

    const addr_second = cmdline.memparse(addr_first.rest[1..]);
    try std.testing.expectEqual(@as(u64, 0x20), addr_second.value);
    try std.testing.expectEqualStrings("", addr_second.rest);

    const flags = argv[2]["flags=".len..];
    try std.testing.expect(cmdline.parseOptionStr(flags, "left|right"));
    try std.testing.expect(cmdline.parseOptionStr(flags, "debug|pipe"));
    try std.testing.expect(!cmdline.parseOptionStr(flags, "left"));
    try std.testing.expect(!cmdline.parseOptionStr(flags, "pipe"));
}

test "pipe bytes keep ctype punctuation shape and stable hweight counts" {
    const class = "A|z|5";
    try std.testing.expect(ctype.isupper(class[0]));
    try std.testing.expect(ctype.ispunct(class[1]));
    try std.testing.expect(ctype.islower(class[2]));
    try std.testing.expect(ctype.ispunct(class[3]));
    try std.testing.expect(ctype.isdigit(class[4]));
    try std.testing.expect(ctype.isgraph('|'));
    try std.testing.expect(ctype.isprint('|'));
    try std.testing.expect(!ctype.isspace('|'));
    try std.testing.expect(!ctype.isalnum('|'));
    try std.testing.expectEqual(@as(u8, 'a'), ctype.tolower(class[0]));
    try std.testing.expectEqual(@as(u8, 'Z'), ctype.toupper(class[2]));

    const pipe_byte: u32 = '|';
    const pipe_pair: u32 = pipe_byte | (pipe_byte << 8);
    const pipe_quad: u32 = pipe_pair | (pipe_pair << 16);
    const parsed_mask = cmdline.memparse("0x7c7c");

    try std.testing.expectEqual(@as(u64, 0x7c7c), parsed_mask.value);
    try std.testing.expectEqualStrings("", parsed_mask.rest);
    try std.testing.expectEqual(@as(u32, 5), hweight.swHweight8(pipe_byte));
    try std.testing.expectEqual(@as(u32, 10), hweight.swHweight16(pipe_pair));
    try std.testing.expectEqual(@as(u32, 20), hweight.swHweight32(pipe_quad));
    try std.testing.expectEqual(@as(u32, 10), hweight.swHweight16(@intCast(parsed_mask.value)));
    try std.testing.expectEqual(@as(usize, 10), hweight.hweightLong(@intCast(parsed_mask.value)));
}
