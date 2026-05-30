const std = @import("std");
const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn classBits(token: []const u8) u32 {
    var bits: u32 = 0;
    for (token, 0..) |byte, idx| {
        if (ctype.isalpha(byte) or ctype.isdigit(byte)) {
            bits |= @as(u32, 1) << @intCast(idx);
        }
    }
    return bits;
}

fn splitArgv(split: anytype) []const []const u8 {
    const Split = @TypeOf(split);
    return if (@typeInfo(Split) == .@"struct") split.argv else split;
}

fn freeSplit(allocator: std.mem.Allocator, split: anytype) void {
    const Split = @TypeOf(split.*);
    if (@typeInfo(Split) == .@"struct") {
        split.deinit();
    } else {
        argv_split.argvFree(allocator, split.*);
    }
}

test "case folded argv tokens keep cmdline rests and hweight class counts aligned" {
    var split = try argv_split.argvSplit(std.testing.allocator, "Root=0x10Ktail alpha\x09\xC0\xE0");
    defer freeSplit(std.testing.allocator, &split);
    const argv = splitArgv(split);

    try std.testing.expectEqual(@as(usize, 3), argv.len);
    try std.testing.expectEqualStrings("Root=0x10Ktail", argv[0]);
    try std.testing.expectEqualStrings("alpha", argv[1]);
    try std.testing.expectEqualSlices(u8, &.{ 0xC0, 0xE0 }, argv[2]);

    try std.testing.expect(ctype.isupper(argv[0][0]));
    try std.testing.expectEqual(@as(u8, 'r'), ctype.tolower(argv[0][0]));
    try std.testing.expectEqual(@as(u8, 'A'), ctype.toupper(argv[1][0]));
    try std.testing.expectEqual(@as(u8, 0xE0), ctype.fastTolower(argv[2][0]));
    try std.testing.expectEqual(@as(u8, 0xC0), ctype.toupper(argv[2][1]));

    const parsed = cmdline.memparse(argv[0][5..]);
    try std.testing.expectEqual(@as(u64, 0x10 << 10), parsed.value);
    try std.testing.expectEqualStrings("tail", parsed.rest);

    const root_class_bits = classBits(argv[0]);
    try std.testing.expectEqual(@as(u32, 13), hweight.swHweight32(root_class_bits));
    try std.testing.expectEqual(@as(u32, 5), hweight.swHweight32(classBits(argv[1])));
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight32(classBits(argv[2])));
}

test "comma option scans and ctype masks produce stable bit weights" {
    const options = "quiet,debug,root,panic\x00ignored";
    try std.testing.expect(cmdline.parseOptionStr(options, "root"));
    try std.testing.expect(!cmdline.parseOptionStr(options, "ignored"));

    var printable_bits: u32 = 0;
    var graph_bits: u32 = 0;
    const sample = " A!\x7f\xA0";
    for (sample, 0..) |byte, idx| {
        const bit = @as(u32, 1) << @intCast(idx);
        if (ctype.isprint(byte)) printable_bits |= bit;
        if (ctype.isgraph(byte)) graph_bits |= bit;
    }

    try std.testing.expectEqual(@as(u32, 4), hweight.swHweight32(printable_bits));
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight32(graph_bits));
    try std.testing.expectEqual(@as(u32, 2), hweight.swHweight32(printable_bits ^ graph_bits));
}
