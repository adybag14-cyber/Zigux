const std = @import("std");

const argv_split = @import("argv_split");
const cmdline = @import("cmdline");
const ctype = @import("ctype");
const hweight = @import("hweight");

fn argvItems(result: anytype) [][]u8 {
    const Result = @TypeOf(result.*);
    if (@hasField(Result, "argv")) {
        return result.argv;
    }
    return result.*;
}

fn argvLen(result: anytype) usize {
    const Result = @TypeOf(result.*);
    if (@hasField(Result, "argv")) {
        return result.argc();
    }
    return result.len;
}

fn freeArgv(allocator: std.mem.Allocator, result: anytype) void {
    const Result = @TypeOf(result.*);
    if (@hasField(Result, "argv")) {
        result.deinit();
    } else {
        argv_split.argvFree(allocator, result.*);
    }
}

test "nul byte fences stay distinct across argv_split cmdline ctype and hweight" {
    var args = try argv_split.argvSplit(
        std.testing.allocator,
        "flag alpha\x00beta tail",
    );
    defer freeArgv(std.testing.allocator, &args);

    const argv = argvItems(&args);
    try std.testing.expectEqual(@as(usize, 3), argvLen(&args));
    try std.testing.expectEqualStrings("flag", argv[0]);
    try std.testing.expectEqualStrings("alpha\x00beta", argv[1]);
    try std.testing.expectEqualStrings("tail", argv[2]);

    const nul_idx = std.mem.indexOfScalar(u8, argv[1], 0) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(@as(usize, 5), nul_idx);
    try std.testing.expect(ctype.iscntrl(argv[1][nul_idx]));
    try std.testing.expect(!ctype.isprint(argv[1][nul_idx]));
    try std.testing.expect(!ctype.isgraph(argv[1][nul_idx]));
    try std.testing.expectEqual(@as(u32, 0), hweight.swHweight8(argv[1][nul_idx]));

    try std.testing.expect(cmdline.parseOptionStr("alpha\x00beta,tail", "alpha"));
    try std.testing.expect(!cmdline.parseOptionStr("alpha\x00beta,tail", "beta"));
    try std.testing.expect(!cmdline.parseOptionStr("alpha\x00beta,tail", "tail"));
}

test "control-byte parser rest and bit counts stay stable" {
    const parsed = cmdline.memparse("0\x00tail");
    try std.testing.expectEqual(@as(u64, 0), parsed.value);
    try std.testing.expectEqualStrings("\x00tail", parsed.rest);

    var zero_count: u32 = 0;
    var printable_count: u32 = 0;
    for (parsed.rest) |ch| {
        if (ch == 0) {
            zero_count += 1;
            try std.testing.expect(ctype.iscntrl(ch));
            try std.testing.expectEqual(@as(u32, 0), hweight.swHweight8(ch));
        } else {
            try std.testing.expect(ctype.isprint(ch));
            printable_count += 1;
        }
    }

    try std.testing.expectEqual(@as(u32, 1), zero_count);
    try std.testing.expectEqual(@as(u32, 4), printable_count);
    try std.testing.expectEqual(@as(u32, 3), hweight.swHweight8('a'));
    try std.testing.expectEqual(@as(u32, 0), hweight.swHweight16(@as(u32, zero_count - 1)));
}
