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

const FindAddReplay = struct {
    checksum: u64,
    existing_key: i32,
    existing_serial: usize,
    inserted_order: [4]i32,
};

fn runFindAddReplay() FindAddReplay {
    var entries = [_]RbEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 5, .serial = 2 },
        .{ .key = 10, .serial = 3 },
        .{ .key = 15, .serial = 4 },
    };
    var root = rbtree.Root.init();
    var checksum: u64 = 0;

    checksum +%= @as(u64, @intFromBool(rbtree.findAdd(&entries[0].node, &root, cmpNode) == null));
    checksum +%= @as(u64, @intFromBool(rbtree.findAdd(&entries[1].node, &root, cmpNode) == null));
    checksum +%= @as(u64, @intFromBool(rbtree.findAdd(&entries[2].node, &root, cmpNode) == null));

    const existing = rbtree.findAdd(&entries[3].node, &root, cmpNode) orelse unreachable;
    const existing_entry: *const RbEntry = @fieldParentPtr("node", existing);
    checksum +%= @intCast(existing_entry.key + @as(i32, @intCast(existing_entry.serial)));

    checksum +%= @as(u64, @intFromBool(rbtree.findAdd(&entries[4].node, &root, cmpNode) == null));

    var inserted_order: [4]i32 = undefined;
    var order_index: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const RbEntry = @fieldParentPtr("node", node);
        inserted_order[order_index] = entry.key;
        order_index += 1;
    }
    std.debug.assert(order_index == inserted_order.len);

    return .{
        .checksum = checksum,
        .existing_key = existing_entry.key,
        .existing_serial = existing_entry.serial,
        .inserted_order = inserted_order,
    };
}

test "phase1 rbtree findAdd bench replay keeps duplicate-first semantics explicit" {
    const replay = runFindAddReplay();
    try std.testing.expectEqual(@as(i32, 10), replay.existing_key);
    try std.testing.expectEqual(@as(usize, 0), replay.existing_serial);
    try std.testing.expectEqual([4]i32{ 5, 10, 15, 20 }, replay.inserted_order);
    try std.testing.expectEqual(@as(u64, 14), replay.checksum);
}

test "phase1 rbtree findAdd bench replay matches the bench checksum packet" {
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        checksum +%= runFindAddReplay().checksum;
    }
    try std.testing.expectEqual(@as(u64, 56_000), checksum);
}
