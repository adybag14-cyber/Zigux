const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

test "ports B keep ASCII control separators out of parsed tokens" {
    var parsed = try argv_split.argvSplit(
        std.testing.allocator,
        "\tmem=0x10K\nmode=fast\rflags=debug\x0bpanic=-1\x0croot=/dev/zigux",
    );
    defer parsed.deinit();

    try std.testing.expectEqual(@as(usize, 5), parsed.argc());
    try std.testing.expectEqualStrings("mem=0x10K", parsed.argv[0]);
    try std.testing.expectEqualStrings("mode=fast", parsed.argv[1]);
    try std.testing.expectEqualStrings("flags=debug", parsed.argv[2]);
    try std.testing.expectEqualStrings("panic=-1", parsed.argv[3]);
    try std.testing.expectEqualStrings("root=/dev/zigux", parsed.argv[4]);

    const mem = cmdline.memparse(parsed.argv[0]["mem=".len..]);
    try std.testing.expectEqual(@as(u64, 0x10 << 10), mem.value);
    try std.testing.expectEqualStrings("", mem.rest);

    const panic = cmdline.memparse(parsed.argv[3]["panic=".len..]);
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -1))), panic.value);
    try std.testing.expectEqualStrings("", panic.rest);

    try std.testing.expect(cmdline.parseOptionStr("quiet,debug,fast", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug\x00fast", "fast"));
}

test "ports B derive stable masks from printable and control bytes" {
    const control_bytes = [_]u8{ 0, '\t', '\n', '\x0b', '\x0c', '\r', 0x7f };
    var control_mask: u32 = 0;
    for (control_bytes) |byte| {
        try std.testing.expect(ctype.iscntrl(byte) or ctype.isspace(byte));
        try std.testing.expect(!ctype.isgraph(byte));
        control_mask |= @as(u32, 1) << @intCast(byte & 0x1f);
    }

    const expected_control_mask: u32 =
        (@as(u32, 1) << 0) |
        (@as(u32, 1) << 9) |
        (@as(u32, 1) << 10) |
        (@as(u32, 1) << 11) |
        (@as(u32, 1) << 12) |
        (@as(u32, 1) << 13) |
        (@as(u32, 1) << 31);
    try std.testing.expectEqual(expected_control_mask, control_mask);
    try std.testing.expectEqual(@as(u32, control_bytes.len), hweight.swHweight32(control_mask));

    const printable = "AZaz09,_-";
    var printable_mask: u32 = 0;
    for (printable) |byte| {
        try std.testing.expect(ctype.isprint(byte));
        try std.testing.expect(ctype.isgraph(byte));
        try std.testing.expect(!ctype.isspace(byte));
        printable_mask |= @as(u32, 1) << @intCast(byte & 0x1f);
    }

    try std.testing.expectEqual(@as(u32, 7), hweight.swHweight32(printable_mask));
}

test "ports B preserve delimiter ownership across split and option parsing" {
    var parsed = try argv_split.argv_split(
        std.testing.allocator,
        "debug,trace token=0xff rest=08G",
    );
    defer argv_split.argv_free(&parsed);

    try std.testing.expectEqual(@as(usize, 3), parsed.argc());
    try std.testing.expect(cmdline.parse_option_str(parsed.argv[0], "debug"));
    try std.testing.expect(cmdline.parse_option_str(parsed.argv[0], "trace"));
    try std.testing.expect(!cmdline.parse_option_str(parsed.argv[0], "token"));

    const token = cmdline.memparse(parsed.argv[1]["token=".len..]);
    try std.testing.expectEqual(@as(u64, 0xff), token.value);
    try std.testing.expectEqualStrings("", token.rest);

    const rest = cmdline.memparse(parsed.argv[2]["rest=".len..]);
    try std.testing.expectEqual(@as(u64, 0), rest.value);
    try std.testing.expectEqualStrings("8G", rest.rest);

    try std.testing.expect(ctype.isxdigit('f'));
    try std.testing.expect(!ctype.isxdigit('G'));
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight16(0x00ff));
}
