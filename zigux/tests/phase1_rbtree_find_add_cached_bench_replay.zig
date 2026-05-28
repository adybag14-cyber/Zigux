const std = @import("std");
const rbtree = @import("rbtree");

const iterations_rbtree = 4_000;

const RbEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = .{},
};

fn cmpNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const RbEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const RbEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

const FindAddCachedReplay = struct {
    checksum: u64,
    initial_leftmost_key: i32,
    existing_key: i32,
    existing_serial: usize,
    final_leftmost_key: i32,
    inserted_order: [4]i32,
};

fn runFindAddCachedReplay() FindAddCachedReplay {
    var entries = [_]RbEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 10, .serial = 3 },
        .{ .key = 15, .serial = 4 },
    };
    var root = rbtree.RootCached.init();
    var checksum: u64 = 0;

    checksum +%= @as(u64, @intFromBool(rbtree.findAddCached(&entries[0].node, &root, cmpNode) == null));
    checksum +%= @as(u64, @intFromBool(rbtree.findAddCached(&entries[1].node, &root, cmpNode) == null));
    checksum +%= @as(u64, @intFromBool(rbtree.findAddCached(&entries[2].node, &root, cmpNode) == null));

    const initial_leftmost_entry: *const RbEntry = @fieldParentPtr("node", rbtree.firstCached(&root).?);
    checksum +%= @intCast(initial_leftmost_entry.key);
    checksum +%= @as(u64, @intFromBool(rbtree.first(&root.root) == rbtree.firstCached(&root)));

    const existing = rbtree.findAddCached(&entries[3].node, &root, cmpNode) orelse unreachable;
    const existing_entry: *const RbEntry = @fieldParentPtr("node", existing);
    checksum +%= @intCast(existing_entry.key + @as(i32, @intCast(existing_entry.serial)));
    checksum +%= @as(u64, @intFromBool(rbtree.first(&root.root) == rbtree.firstCached(&root)));

    checksum +%= @as(u64, @intFromBool(rbtree.findAddCached(&entries[4].node, &root, cmpNode) == null));

    const final_leftmost_entry: *const RbEntry = @fieldParentPtr("node", rbtree.firstCached(&root).?);
    checksum +%= @intCast(final_leftmost_entry.key);
    checksum +%= @as(u64, @intFromBool(rbtree.first(&root.root) == rbtree.firstCached(&root)));

    var inserted_order: [4]i32 = undefined;
    var order_index: usize = 0;
    var current = rbtree.first(&root.root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const RbEntry = @fieldParentPtr("node", node);
        inserted_order[order_index] = entry.key;
        order_index += 1;
    }
    std.debug.assert(order_index == inserted_order.len);

    return .{
        .checksum = checksum,
        .initial_leftmost_key = initial_leftmost_entry.key,
        .existing_key = existing_entry.key,
        .existing_serial = existing_entry.serial,
        .final_leftmost_key = final_leftmost_entry.key,
        .inserted_order = inserted_order,
    };
}

test "phase1 rbtree findAddCached bench replay keeps cached duplicate-first semantics explicit" {
    const replay = runFindAddCachedReplay();
    try std.testing.expectEqual(@as(i32, 5), replay.initial_leftmost_key);
    try std.testing.expectEqual(@as(i32, 10), replay.existing_key);
    try std.testing.expectEqual(@as(usize, 0), replay.existing_serial);
    try std.testing.expectEqual(@as(i32, 5), replay.final_leftmost_key);
    try std.testing.expectEqual([4]i32{ 5, 10, 15, 20 }, replay.inserted_order);
    try std.testing.expectEqual(@as(u64, 27), replay.checksum);
}

test "phase1 rbtree findAddCached bench replay matches the bench checksum packet" {
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        checksum +%= runFindAddCachedReplay().checksum;
    }
    try std.testing.expectEqual(@as(u64, 108_000), checksum);
}
