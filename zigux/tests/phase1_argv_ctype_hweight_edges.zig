const std = @import("std");
const argv_split = @import("argv_split");
const ctype = @import("ctype");
const hweight = @import("hweight");

const LegacyArgvSplitResult = struct {
    allocator: std.mem.Allocator,
    argv: [][]u8,

    fn argc(self: @This()) usize {
        return self.argv.len;
    }

    fn deinit(self: *@This()) void {
        argv_split.argvFree(self.allocator, self.argv);
        self.* = .{
            .allocator = self.allocator,
            .argv = &.{},
        };
    }
};

const ArgvSplitHandle = if (@hasDecl(argv_split, "ArgvSplitResult"))
    argv_split.ArgvSplitResult
else
    LegacyArgvSplitResult;

fn splitArgs(allocator: std.mem.Allocator, text: []const u8) !ArgvSplitHandle {
    if (@hasDecl(argv_split, "ArgvSplitResult")) {
        return try argv_split.argvSplit(allocator, text);
    }

    return .{
        .allocator = allocator,
        .argv = try argv_split.argvSplit(allocator, text),
    };
}

test "standalone argv split replay keeps mixed whitespace tokenization aligned" {
    var split = try splitArgs(std.testing.allocator, "\tzigux  phase1\nhelpers\r\nalpha");
    defer split.deinit();

    try std.testing.expectEqual(@as(usize, 4), split.argc());
    try std.testing.expectEqualStrings("zigux", split.argv[0]);
    try std.testing.expectEqualStrings("phase1", split.argv[1]);
    try std.testing.expectEqualStrings("helpers", split.argv[2]);
    try std.testing.expectEqualStrings("alpha", split.argv[3]);

    var blank = try splitArgs(std.testing.allocator, " \n\t\r ");
    defer blank.deinit();
    try std.testing.expectEqual(@as(usize, 0), blank.argc());
}

test "standalone ctype replay keeps latin-pair and ascii edges aligned" {
    try std.testing.expect(ctype.isupper(0xC0));
    try std.testing.expect(ctype.islower(0xE0));
    try std.testing.expectEqual(@as(u8, 0xE0), ctype.tolower(0xC0));
    try std.testing.expectEqual(@as(u8, 0xC0), ctype.toupper(0xE0));
    try std.testing.expectEqual(@as(u8, 0xF8), ctype.fastTolower(0xD8));
    try std.testing.expectEqual(@as(u8, '!'), ctype.fastTolower('!'));
    try std.testing.expect(!ctype.isascii(0x80));
    try std.testing.expectEqual(@as(u8, 0x7F), ctype.toascii(0xFF));
    try std.testing.expect(ctype.isxdigit('F'));
    try std.testing.expect(!ctype.isodigit('8'));
}

test "standalone hweight replay keeps width boundaries and aliases aligned" {
    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight8(0xF0));
    try std.testing.expectEqual(@as(u32, 8), hweight.swHweight16(0xF0F0));
    try std.testing.expectEqual(@as(u32, 16), hweight.swHweight32(0xF0F0_F0F0));
    try std.testing.expectEqual(@as(u64, 33), hweight.swHweight64(0xFFFF_FFFF_0000_0001));
    try std.testing.expectEqual(@bitSizeOf(usize), hweight.hweightLong(std.math.maxInt(usize)));

    if (@hasDecl(hweight, "__sw_hweight64")) {
        try std.testing.expectEqual(
            hweight.swHweight64(0xFFFF_FFFF_0000_0001),
            hweight.__sw_hweight64(0xFFFF_FFFF_0000_0001),
        );
    }
    if (@hasDecl(hweight, "hweight_long")) {
        try std.testing.expectEqual(
            hweight.hweightLong(std.math.maxInt(usize)),
            hweight.hweight_long(std.math.maxInt(usize)),
        );
    }
}
