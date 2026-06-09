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

test "colon chains stay intact across argv split and cmdline parsing" {
    var split = try argv_split.argvSplit(
        std.testing.allocator,
        "pci=0000:00:1f.2 mem=0x10:0x20 flags=boot:fast,irq:shared class=A:z:9 mask=0x3a3a",
    );
    defer freeArgv(std.testing.allocator, &split);

    const argv = argvItems(&split);
    try std.testing.expectEqual(@as(usize, 5), argv.len);
    try std.testing.expectEqualStrings("pci=0000:00:1f.2", argv[0]);
    try std.testing.expectEqualStrings("mem=0x10:0x20", argv[1]);
    try std.testing.expectEqualStrings("flags=boot:fast,irq:shared", argv[2]);
    try std.testing.expectEqualStrings("class=A:z:9", argv[3]);
    try std.testing.expectEqualStrings("mask=0x3a3a", argv[4]);

    if (@hasDecl(cmdline, "nextArg")) {
        const first = cmdline.nextArg("pci=0000:00:1f.2 mem=0x10:0x20") orelse return error.TestUnexpectedResult;
        try std.testing.expectEqualStrings("pci", first.param);
        try std.testing.expectEqualStrings("0000:00:1f.2", first.value.?);
        try std.testing.expectEqualStrings("mem=0x10:0x20", first.remaining);
    }

    const mem_first = cmdline.memparse(argv[1]["mem=".len..]);
    try std.testing.expectEqual(@as(u64, 0x10), mem_first.value);
    try std.testing.expectEqualStrings(":0x20", mem_first.rest);

    const mem_second = cmdline.memparse(mem_first.rest[1..]);
    try std.testing.expectEqual(@as(u64, 0x20), mem_second.value);
    try std.testing.expectEqualStrings("", mem_second.rest);

    const flags = argv[2]["flags=".len..];
    try std.testing.expect(cmdline.parseOptionStr(flags, "boot:fast"));
    try std.testing.expect(cmdline.parseOptionStr(flags, "irq:shared"));
    try std.testing.expect(!cmdline.parseOptionStr(flags, "boot"));
    try std.testing.expect(!cmdline.parseOptionStr(flags, "shared"));
}

test "colon bytes keep ctype punctuation shape and stable hweight counts" {
    const class = "A:z:9";
    try std.testing.expect(ctype.isupper(class[0]));
    try std.testing.expect(ctype.ispunct(class[1]));
    try std.testing.expect(ctype.islower(class[2]));
    try std.testing.expect(ctype.ispunct(class[3]));
    try std.testing.expect(ctype.isdigit(class[4]));
    try std.testing.expect(ctype.isgraph(':'));
    try std.testing.expect(ctype.isprint(':'));
    try std.testing.expect(!ctype.isspace(':'));
    try std.testing.expect(!ctype.isalnum(':'));
    try std.testing.expectEqual(@as(u8, 'a'), ctype.tolower(class[0]));
    try std.testing.expectEqual(@as(u8, 'Z'), ctype.toupper(class[2]));

    const colon_byte: u32 = ':';
    const colon_pair: u32 = colon_byte | (colon_byte << 8);
    const colon_quad: u32 = colon_pair | (colon_pair << 16);
    const parsed_mask = cmdline.memparse("0x3a3a");

    try std.testing.expectEqual(@as(u64, 0x3a3a), parsed_mask.value);
    try std.testing.expectEqualStrings("", parsed_mask.rest);
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight8(colon_byte));
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight16(colon_pair));
    try std.testing.expectEqual(@as(u32, 16), hweight.swHweight32(colon_quad));
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight16(@intCast(parsed_mask.value)));
    try std.testing.expectEqual(@as(usize, 8), hweight.hweightLong(@intCast(parsed_mask.value)));
}
