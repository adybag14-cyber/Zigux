const std = @import("std");
const argv_split = @import("argv_split");

test "phase1 argvSplit allocation-failure replay stays leak free" {
    const Harness = struct {
        fn run(allocator: std.mem.Allocator, text: []const u8) !void {
            var result = try argv_split.argvSplit(allocator, text);
            defer result.deinit();

            try std.testing.expectEqual(@as(usize, 3), result.argc());
            try std.testing.expectEqualStrings("alpha", result.argv[0]);
            try std.testing.expectEqualStrings("beta", result.argv[1]);
            try std.testing.expectEqualStrings("gamma", result.argv[2]);
        }
    };

    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        Harness.run,
        .{"alpha beta gamma"},
    );
}

test "phase1 argvSplit replay keeps duplicated storage independent of caller text" {
    var source = [_]u8{ 'a', 'l', 'p', 'h', 'a', ' ', 'b', 'e', 't', 'a' };
    var result = try argv_split.argvSplit(std.testing.allocator, source[0..]);
    defer result.deinit();

    source[0] = 'o';
    source[6] = 'z';

    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
}

test "phase1 argvSplit replay restores the blank state after deinit" {
    var result = try argv_split.argvSplit(std.testing.allocator, "alpha beta");
    try std.testing.expectEqual(@as(usize, 2), result.argc());

    result.deinit();
    try std.testing.expectEqual(@as(usize, 0), result.argc());
    try std.testing.expectEqual(@as(usize, 0), result.argv.len);

    const allocator = result.allocator;
    result = try argv_split.argvSplit(allocator, "gamma");
    defer result.deinit();

    try std.testing.expectEqual(@as(usize, 1), result.argc());
    try std.testing.expectEqualStrings("gamma", result.argv[0]);
}
