const std = @import("std");
const argv_split = @import("argv_split");

test "argvSplit snapshots token bytes away from later source mutations" {
    var input = [_]u8{ ' ', 'a', 'l', 'p', 'h', 'a', ' ', 'b', 'e', 't', 'a', ' ', 'g', 'a', 'm', 'm', 'a', ' ' };

    var result = try argv_split.argvSplit(std.testing.allocator, input[0..]);
    defer result.deinit();

    input[1] = 'x';
    input[7] = 'y';
    input[12] = 'z';

    try std.testing.expectEqual(@as(usize, 3), result.argc());
    try std.testing.expectEqualStrings("alpha", result.argv[0]);
    try std.testing.expectEqualStrings("beta", result.argv[1]);
    try std.testing.expectEqualStrings("gamma", result.argv[2]);
}

test "argv_split aliases preserve lifecycle and partial-allocation cleanup" {
    var alias_result = try argv_split.argv_split(std.testing.allocator, "left middle right");
    defer argv_split.argv_free(&alias_result);

    try std.testing.expectEqual(@as(usize, 3), alias_result.argc());
    try std.testing.expectEqualStrings("left", alias_result.argv[0]);
    try std.testing.expectEqualStrings("middle", alias_result.argv[1]);
    try std.testing.expectEqualStrings("right", alias_result.argv[2]);

    const Harness = struct {
        fn run(allocator: std.mem.Allocator, text: []const u8) !void {
            var result = try argv_split.argv_split(allocator, text);
            defer argv_split.argv_free(&result);
        }
    };

    try std.testing.checkAllAllocationFailures(
        std.testing.allocator,
        Harness.run,
        .{"left middle right tail"},
    );
}
