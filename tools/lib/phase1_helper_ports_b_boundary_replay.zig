const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn expectArg(result: argv_split.ArgvSplitResult, idx: usize, expected: []const u8) !void {
    try std.testing.expect(idx < result.argv.len);
    try std.testing.expectEqualStrings(expected, result.argv[idx]);
}

test "helper ports B preserve whitespace token and classifier boundaries" {
    const form_feed: u8 = 0x0c;
    var text = [_]u8{
        ' ', 'a', 'l', 'p', 'h', 'a', form_feed, 'b', 'e', 't', 'a',  '\r',
        'g', 'a', 'm', 'm', 'a', 0,   't',       'a', 'i', 'l', '\t',
    };

    var split = try argv_split.argv_split(std.testing.allocator, text[0..]);
    defer argv_split.argv_free(&split);

    try std.testing.expectEqual(@as(usize, 3), split.argc());
    try expectArg(split, 0, "alpha");
    try expectArg(split, 1, "beta");
    try std.testing.expectEqualSlices(u8, text[12..22], split.argv[2]);
    try std.testing.expectEqual(@as(u8, 0), split.argv[2][5]);

    try std.testing.expect(ctype.isspace(form_feed));
    try std.testing.expect(ctype.isspace('\r'));
    try std.testing.expect(ctype.isspace('\t'));
    try std.testing.expect(!ctype.isspace(0));
    try std.testing.expect(ctype.isalpha(split.argv[0][0]));
    try std.testing.expectEqual(@as(u32, 3), hweight.__sw_hweight8(0b1010_0100));
}

test "cmdline quote parsing feeds memparse and hweight without changing rest cursors" {
    const first = cmdline.next_arg("  \"mode=fast boot\" size=0x10K mask=0xf0f0 tail") orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mode", first.param);
    try std.testing.expectEqualStrings("fast boot", first.value.?);
    try std.testing.expectEqualStrings("size=0x10K mask=0xf0f0 tail", first.remaining);

    const size_arg = cmdline.nextArg(first.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("size", size_arg.param);
    const size = cmdline.memparse(size_arg.value.?);
    try std.testing.expectEqual(@as(u64, 0x10 << 10), size.value);
    try std.testing.expectEqualStrings("", size.rest);

    const mask_arg = cmdline.nextArg(size_arg.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("mask", mask_arg.param);
    const mask = cmdline.memparse(mask_arg.value.?);
    try std.testing.expectEqual(@as(u64, 0xf0f0), mask.value);
    try std.testing.expectEqualStrings("", mask.rest);
    try std.testing.expectEqual(@as(u32, 8), hweight.__sw_hweight16(@intCast(mask.value)));

    const tail_arg = cmdline.nextArg(mask_arg.remaining) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqualStrings("tail", tail_arg.param);
    try std.testing.expect(tail_arg.value == null);
    try std.testing.expectEqualStrings("", tail_arg.remaining);
}

test "ctype transforms and narrow hweight helpers keep high bytes out of low lanes" {
    try std.testing.expect(ctype.isupper('Q'));
    try std.testing.expect(ctype.islower(ctype.fastTolower('Q')));
    try std.testing.expectEqual(@as(u8, 'q'), ctype.tolower('Q'));
    try std.testing.expectEqual(@as(u8, 'Q'), ctype.toupper('q'));

    const high_noise: u32 = 0xffff_0081;
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight8(high_noise));
    try std.testing.expectEqual(@as(u32, 2), hweight.__sw_hweight8(high_noise));
    try std.testing.expectEqual(@as(u32, 6), hweight.swHweight16(0x80f1));

    const long_mask: usize = if (@sizeOf(usize) == 4) 0x8000_0001 else 0x8000_0000_0000_0001;
    try std.testing.expectEqual(@as(usize, 2), hweight.hweight_long(long_mask));
}
