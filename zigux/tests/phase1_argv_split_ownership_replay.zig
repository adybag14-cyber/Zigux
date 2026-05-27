const std = @import("std");
const argv_split = @import("argv_split");

test "phase1 argvSplit collapses extended whitespace into stable owned tokens" {
    var split = try argv_split.argvSplit(std.testing.allocator, "\ralpha\x0bbeta\x0cgamma\r\n\tdelta");
    defer split.deinit();

    try std.testing.expectEqual(@as(usize, 4), split.argc());
    try std.testing.expectEqualStrings("alpha", split.argv[0]);
    try std.testing.expectEqualStrings("beta", split.argv[1]);
    try std.testing.expectEqualStrings("gamma", split.argv[2]);
    try std.testing.expectEqualStrings("delta", split.argv[3]);
}

test "phase1 argvSplit keeps sibling result ownership separate and reusable after argvFree" {
    var first = try argv_split.argvSplit(std.testing.allocator, "alpha beta");
    var second = try argv_split.argvSplit(std.testing.allocator, "gamma delta");
    defer second.deinit();

    try std.testing.expect(first.argv[0].ptr != second.argv[0].ptr);
    first.argv[0][0] = 'A';
    try std.testing.expectEqualStrings("Alpha", first.argv[0]);
    try std.testing.expectEqualStrings("gamma", second.argv[0]);

    argv_split.argv_free(&first);
    try std.testing.expectEqual(@as(usize, 0), first.argc());
    try std.testing.expectEqual(@as(usize, 0), first.argv.len);

    first = try argv_split.argvSplit(std.testing.allocator, "epsilon");
    defer first.deinit();
    try std.testing.expectEqual(@as(usize, 1), first.argc());
    try std.testing.expectEqualStrings("epsilon", first.argv[0]);
    try std.testing.expectEqualStrings("gamma", second.argv[0]);
    try std.testing.expectEqualStrings("delta", second.argv[1]);
}
