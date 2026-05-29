const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

test "helper ports B preserve signed suffix tokens across split and parse" {
    var split = try argv_split.argvSplit(
        std.testing.allocator,
        "mem=-0x2K mask=0xf0 bank=+010M flag",
    );
    defer split.deinit();

    try std.testing.expectEqual(@as(usize, 4), split.argc());
    try std.testing.expectEqualStrings("mem=-0x2K", split.argv[0]);
    try std.testing.expectEqualStrings("mask=0xf0", split.argv[1]);
    try std.testing.expectEqualStrings("bank=+010M", split.argv[2]);
    try std.testing.expectEqualStrings("flag", split.argv[3]);

    const mem_value = cmdline.memparse(split.argv[0][4..]);
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -2048))), mem_value.value);
    try std.testing.expectEqualStrings("", mem_value.rest);

    const mask_value = cmdline.memparse(split.argv[1][5..]);
    try std.testing.expectEqual(@as(u64, 0xf0), mask_value.value);
    try std.testing.expectEqualStrings("", mask_value.rest);
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight8(@intCast(mask_value.value)));

    const bank_value = cmdline.memparse(split.argv[2][5..]);
    try std.testing.expectEqual(@as(u64, 8 << 20), bank_value.value);
    try std.testing.expectEqualStrings("", bank_value.rest);
    try std.testing.expectEqual(@as(u32, 1), hweight.swHweight32(@intCast(bank_value.value)));
}

test "helper ports B keep delimiter option and byte-mask boundaries explicit" {
    try std.testing.expect(cmdline.parse_option_str("mem,mask,bank,flag", "mask"));
    try std.testing.expect(!cmdline.parse_option_str("mem,mask\x00bank,flag", "bank"));
    try std.testing.expect(cmdline.parse_option_str("mem,,flag", ""));
    try std.testing.expect(!cmdline.parse_option_str("mem,flag,", ""));

    const punctuation = [_]u8{ '-', '+', '=', ',' };
    for (punctuation) |ch| {
        try std.testing.expect(ctype.ispunct(ch));
        try std.testing.expect(!ctype.isalnum(ch));
    }

    const suffixes = [_]u8{ 'K', 'M', 'g' };
    for (suffixes) |ch| {
        try std.testing.expect(ctype.isalpha(ch));
        try std.testing.expect(!ctype.isxdigit(ch));
    }

    const hex_bytes = [_]u8{ '0', '9', 'a', 'F' };
    for (hex_bytes) |ch| {
        try std.testing.expect(ctype.isxdigit(ch));
    }

    const delimiter_mask: u32 = @as(u32, 1) << 0 | @as(u32, 1) << 1 | @as(u32, 1) << 4 | @as(u32, 1) << 7;
    try std.testing.expectEqual(@as(u32, punctuation.len), hweight.swHweight8(delimiter_mask));
}

test "helper ports B width helpers agree on split-owned values" {
    var split = try argv_split.argv_split(std.testing.allocator, "0xff 0x0101 0x10001");
    defer argv_split.argv_free(&split);

    try std.testing.expectEqual(@as(usize, 3), split.argc());

    const byte = cmdline.memparse(split.argv[0]);
    const word = cmdline.memparse(split.argv[1]);
    const dword = cmdline.memparse(split.argv[2]);

    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight8(@intCast(byte.value)));
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight16(@intCast(word.value)));
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight32(@intCast(dword.value)));
    try std.testing.expectEqual(@as(usize, 2), hweight.hweightLong(@intCast(dword.value)));
}
