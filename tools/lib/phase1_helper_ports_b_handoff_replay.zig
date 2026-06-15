const std = @import("std");

const argv_split = @import("argv_split.zig");
const cmdline = @import("cmdline.zig");
const ctype = @import("ctype.zig");
const hweight = @import("hweight.zig");

fn argvItems(result: anytype) [][]u8 {
    return switch (@typeInfo(@TypeOf(result))) {
        .@"struct" => result.argv,
        .pointer => |pointer| switch (pointer.size) {
            .slice => result,
            else => @compileError("unsupported argvSplit result pointer shape"),
        },
        else => @compileError("unsupported argvSplit result shape"),
    };
}

fn freeArgv(allocator: std.mem.Allocator, result: anytype) void {
    const items = argvItems(result);
    for (items) |arg| {
        allocator.free(arg);
    }
    allocator.free(items);
}

test "phase1 helper ports B hand command tokens between split parse classify and hweight" {
    const parsed = try argv_split.argvSplit(
        std.testing.allocator,
        "  size=0x20K flags=quiet,debug mask=0xf0f0f00f class=Az_9  ",
    );
    defer freeArgv(std.testing.allocator, parsed);

    const argv = argvItems(parsed);
    try std.testing.expectEqual(@as(usize, 4), argv.len);
    try std.testing.expectEqualStrings("size=0x20K", argv[0]);
    try std.testing.expectEqualStrings("flags=quiet,debug", argv[1]);
    try std.testing.expectEqualStrings("mask=0xf0f0f00f", argv[2]);
    try std.testing.expectEqualStrings("class=Az_9", argv[3]);

    const size_token = cmdline.memparse(argv[0]["size=".len..]);
    try std.testing.expectEqual(@as(u64, 0x20 << 10), size_token.value);
    try std.testing.expectEqualStrings("", size_token.rest);

    const flags = argv[1]["flags=".len..];
    try std.testing.expect(cmdline.parseOptionStr(flags, "quiet"));
    try std.testing.expect(cmdline.parse_option_str(flags, "debug"));
    try std.testing.expect(!cmdline.parseOptionStr(flags, "trace"));

    const mask_token = cmdline.memparse(argv[2]["mask=".len..]);
    try std.testing.expectEqual(@as(u64, 0xf0f0f00f), mask_token.value);
    try std.testing.expectEqualStrings("", mask_token.rest);
    try std.testing.expectEqual(@as(u32, 16), hweight.swHweight32(@intCast(mask_token.value)));
    try std.testing.expectEqual(@as(usize, 16), hweight.hweightLong(@intCast(mask_token.value)));

    const class = argv[3]["class=".len..];
    try std.testing.expect(ctype.isupper(class[0]));
    try std.testing.expect(ctype.islower(class[1]));
    try std.testing.expect(ctype.ispunct(class[2]));
    try std.testing.expect(ctype.isdigit(class[3]));
    try std.testing.expectEqual(@as(u8, 'a'), ctype.tolower(class[0]));
    try std.testing.expectEqual(@as(u8, 'Z'), ctype.toupper(class[1]));
}
