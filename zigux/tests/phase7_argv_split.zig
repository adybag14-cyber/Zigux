const std = @import("std");
const argv_split = @import("argv_split");
const phase7_vectors = @import("fixtures/phase7_argv_split_vectors.zig");

fn expectFixture(fixture: phase7_vectors.ArgvSplitCase) !void {
    var argc: usize = std.math.maxInt(usize);
    var split = try argv_split.argvSplitWithArgc(std.testing.allocator, fixture.input, &argc);
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(fixture.expected.len, argv_split.countArgc(fixture.input));
    try std.testing.expectEqual(fixture.expected.len, argc);
    try std.testing.expectEqual(fixture.expected.len, split.argv.len);

    const c_argv = split.cArgv();
    for (fixture.expected, 0..) |expected, index| {
        try std.testing.expectEqualStrings(expected, split.argv[index]);
        try std.testing.expectEqualStrings(expected, std.mem.span(c_argv[index].?));
    }

    try std.testing.expectEqual(@as(?[*:0]const u8, null), c_argv[fixture.expected.len]);
}

test "phase 7 argv_split module imports cleanly" {
    _ = argv_split;
}

test "phase 7 argvSplit matches focused parity fixtures" {
    for (phase7_vectors.argv_split_cases) |fixture| {
        try expectFixture(fixture);
    }
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

test "phase 7 argvSplitWithArgc reports the split length through the optional out parameter" {
    var argc: usize = 99;
    var split = try argv_split.argvSplitWithArgc(std.testing.allocator, "console=ttyS0 root=/dev/vda rw", &argc);
    defer split.deinit(std.testing.allocator);

    try std.testing.expectEqual(@as(usize, 3), argc);
    try std.testing.expectEqual(argc, split.argv.len);
}
