const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn splitArgv(allocator: std.mem.Allocator, text: []const u8) !struct {
    argv: [][]u8,
    cleanup: *const fn (std.mem.Allocator, [][]u8) void,
} {
    const Result = @TypeOf(try argv_split.argvSplit(allocator, text));
    if (Result == [][]u8) {
        return .{
            .argv = try argv_split.argvSplit(allocator, text),
            .cleanup = struct {
                fn cleanup(inner_allocator: std.mem.Allocator, argv: [][]u8) void {
                    argv_split.argvFree(inner_allocator, argv);
                }
            }.cleanup,
        };
    }

    const result = try argv_split.argvSplit(allocator, text);
    return .{
        .argv = result.argv,
        .cleanup = struct {
            fn cleanup(inner_allocator: std.mem.Allocator, argv: [][]u8) void {
                var owned = argv_split.ArgvSplitResult{
                    .allocator = inner_allocator,
                    .argv = argv,
                };
                argv_split.argvFree(&owned);
            }
        }.cleanup,
    };
}

test "helper ports B keep whitespace and comma delimiters narrow" {
    const text = "\talpha\n\x0bbeta\x0cgamma\r delta";
    const split = try splitArgv(std.testing.allocator, text);
    defer split.cleanup(std.testing.allocator, split.argv);

    try std.testing.expectEqual(@as(usize, 4), split.argv.len);
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("beta", split.argv[1]);
    try std.testing.expectEqualStrings("gamma", split.argv[2]);
    try std.testing.expectEqualStrings("delta", split.argv[3]);

    try std.testing.expect(cmdline.parseOptionStr("quiet,,debug\x00panic", ""));
    try std.testing.expect(cmdline.parse_option_str("quiet,,debug\x00panic", "debug"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,,debug\x00panic", "panic"));
    try std.testing.expect(!cmdline.parseOptionStr("quiet,debug=1", "debug"));
}

test "helper ports B preserve numeric tails and character masks" {
    const unsigned = cmdline.memparse("0755K,rest");
    try std.testing.expectEqual(@as(u64, 0o755 << 10), unsigned.value);
    try std.testing.expectEqualStrings(",rest", unsigned.rest);

    const signed = cmdline.memparse("-0x10M tail");
    try std.testing.expectEqual(@as(u64, @bitCast(@as(i64, -(0x10 << 20)))), signed.value);
    try std.testing.expectEqualStrings(" tail", signed.rest);

    try std.testing.expect(ctype.isascii(0x7f));
    try std.testing.expect(!ctype.isascii(0x80));
    try std.testing.expect(ctype.isspace('\x0b'));
    try std.testing.expect(ctype.isspace('\x0c'));
    try std.testing.expect(ctype.isgraph('~'));
    try std.testing.expect(!ctype.isgraph(' '));
    try std.testing.expectEqual(@as(u8, 0x00), ctype.toascii(0x80));
    try std.testing.expectEqual(@as(u8, 0x7f), ctype.toascii(0xff));
}

test "helper ports B hweight low-lane masks ignore high payload bits" {
    try std.testing.expectEqual(@as(u32, 0), hweight.swHweight8(0xffff_ff00));
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight8(0xffff_ffff));
    try std.testing.expectEqual(@as(u32, 0), hweight.swHweight16(0xffff_0000));
    try std.testing.expectEqual(@as(u32, 16), hweight.swHweight16(0xffff_ffff));
    try std.testing.expectEqual(@as(u32, 32), hweight.swHweight32(0xffff_ffff));
    try std.testing.expectEqual(@as(u64, 64), hweight.swHweight64(0xffff_ffff_ffff_ffff));

    if (@hasDecl(hweight, "__sw_hweight8")) {
        try std.testing.expectEqual(hweight.swHweight8(0xff), hweight.__sw_hweight8(0xff));
        try std.testing.expectEqual(hweight.swHweight16(0xffff), hweight.__sw_hweight16(0xffff));
        try std.testing.expectEqual(hweight.swHweight32(0xffff_ffff), hweight.__sw_hweight32(0xffff_ffff));
        try std.testing.expectEqual(hweight.swHweight64(0xffff_ffff_ffff_ffff), hweight.__sw_hweight64(0xffff_ffff_ffff_ffff));
    }
}
