const std = @import("std");
const argv_split = @import("argv_split");

const ArgvFixture = struct {
    input: []const u8,
    expected: []const []const u8,
};

const whitespace_expected = [_][]const u8{
    "init=/init",
    "console=ttyS0",
    "panic=-1",
};

const blank_expected = [_][]const u8{};

const nul_expected = [_][]const u8{
    "root=/dev/vda",
    "rw",
};

const quote_expected = [_][]const u8{
    "root=\"/dev/sda",
    "1\"",
    "single",
};

fn expectFixture(fixture: ArgvFixture) !void {
    var split = try argv_split.argvSplit(std.testing.allocator, fixture.input);
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(fixture.expected.len, argv_split.countArgc(fixture.input));
    try std.testing.expectEqual(fixture.expected.len, split.argv.len);

    for (fixture.expected, 0..) |expected, index| {
        try std.testing.expectEqualStrings(expected, split.argv[index]);
    }
}

test "phase 7 argv_split module imports cleanly" {
    _ = argv_split;
}

test "phase 7 argvSplit matches focused parity fixtures" {
    try expectFixture(.{
        .input = " init=/init   console=ttyS0\tpanic=-1 ",
        .expected = &whitespace_expected,
    });
    try expectFixture(.{
        .input = " \t\n",
        .expected = &blank_expected,
    });
    try expectFixture(.{
        .input = "root=/dev/vda rw\x00ignored debug",
        .expected = &nul_expected,
    });
    try expectFixture(.{
        .input = "root=\"/dev/sda 1\" single",
        .expected = &quote_expected,
    });
}

test "phase 7 argvSplit token buffer does not alias the source text" {
    var source = [_]u8{ 'r', 'o', 'o', 't', '=', '/', 'd', 'e', 'v', '/', 'v', 'd', 'a', ' ', 'r', 'w' };
    var split = try argv_split.argvSplit(std.testing.allocator, &source);
    defer split.deinit(std.testing.allocator);

    source[0] = 'X';
    source[5] = 'Y';

    try std.testing.expectEqualStrings("root=/dev/vda", split.argv[0]);
    try std.testing.expectEqualStrings("rw", split.argv[1]);
}
