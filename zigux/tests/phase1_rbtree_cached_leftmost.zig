const std = @import("std");
const rbtree = @import("../../tools/lib/rbtree.zig");

const Fixture = struct {
    rbtree: struct {
        cached_leftmost_return_serials: []const i64,
    },
};

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn loadFixture(allocator: std.mem.Allocator) !std.json.Parsed(Fixture) {
    return std.json.parseFromSlice(Fixture, allocator, @embedFile("fixtures/phase1_helpers.json"), .{
        .ignore_unknown_fields = true,
    });
}

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn recordSerials(returns: []const ?*rbtree.Node, actual: []i64) void {
    for (returns, actual) |node, *serial| {
        if (node) |current| {
            const entry: *const Entry = @fieldParentPtr("node", current);
            serial.* = @as(i64, @intCast(entry.serial));
        } else {
            serial.* = -1;
        }
    }
}

test "phase 1 rbtree cached-leftmost fixture stays replayable" {
    var parsed = try loadFixture(std.testing.allocator);
    defer parsed.deinit();
    const fixture = parsed.value;

    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 12, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 5, .serial = 3 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 12, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 5, .serial = 3 },
    };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    const primary_returns = [_]?*rbtree.Node{
        rbtree.addCached(&primary_entries[0].node, &primary_root, less),
        rbtree.addCached(&primary_entries[1].node, &primary_root, less),
        rbtree.addCached(&primary_entries[2].node, &primary_root, less),
        rbtree.addCached(&primary_entries[3].node, &primary_root, less),
    };
    const alias_returns = [_]?*rbtree.Node{
        rbtree.rb_add_cached(&alias_entries[0].node, &alias_root, less),
        rbtree.rb_add_cached(&alias_entries[1].node, &alias_root, less),
        rbtree.rb_add_cached(&alias_entries[2].node, &alias_root, less),
        rbtree.rb_add_cached(&alias_entries[3].node, &alias_root, less),
    };

    var primary_serials: [4]i64 = undefined;
    var alias_serials: [4]i64 = undefined;
    recordSerials(&primary_returns, &primary_serials);
    recordSerials(&alias_returns, &alias_serials);

    try std.testing.expectEqualSlices(i64, fixture.rbtree.cached_leftmost_return_serials, &primary_serials);
    try std.testing.expectEqualSlices(i64, fixture.rbtree.cached_leftmost_return_serials, &alias_serials);
    try std.testing.expectEqual(rbtree.first(&primary_root.root), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(rbtree.first(&alias_root.root), rbtree.rb_first_cached(&alias_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &primary_entries[2].node), rbtree.firstCached(&primary_root));
    try std.testing.expectEqual(@as(?*rbtree.Node, &alias_entries[2].node), rbtree.rb_first_cached(&alias_root));
}
