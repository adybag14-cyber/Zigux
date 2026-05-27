const std = @import("std");
const rbtree = @import("rbtree");

const iterations_rbtree = 4_000;

const RbEntry = struct {
    key: i32,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const RbEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const RbEntry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

const PostorderReplay = struct {
    checksum: u64,
    inorder_keys: [5]i32,
    postorder_keys: [3]i32,
    replacement_cleared: bool,
};

fn runPostorderReplay() PostorderReplay {
    var entries = [_]RbEntry{
        .{ .key = 10 },
        .{ .key = 20 },
        .{ .key = 5 },
        .{ .key = 15 },
        .{ .key = 25 },
    };
    var replacement = RbEntry{ .key = 10 };
    var root = rbtree.Root.init();
    var checksum: u64 = 0;

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    var inorder_keys: [5]i32 = undefined;
    var inorder_count: usize = 0;
    var current = rbtree.first(&root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const RbEntry = @fieldParentPtr("node", node);
        inorder_keys[inorder_count] = entry.key;
        inorder_count += 1;
        checksum +%= @intCast(entry.key + 31);
    }
    std.debug.assert(inorder_count == inorder_keys.len);

    rbtree.erase(&entries[1].node, &root);
    rbtree.replaceNode(&entries[0].node, &replacement.node, &root);
    rbtree.eraseInit(&replacement.node, &root);
    const replacement_cleared = rbtree.emptyNode(&replacement.node);
    checksum +%= @as(u64, @intFromBool(replacement_cleared));

    var postorder_keys: [3]i32 = undefined;
    var postorder_count: usize = 0;
    current = rbtree.firstPostorder(&root);
    while (current) |node| : (current = rbtree.nextPostorder(node)) {
        const entry: *const RbEntry = @fieldParentPtr("node", node);
        postorder_keys[postorder_count] = entry.key;
        postorder_count += 1;
        checksum +%= @intCast(entry.key + 17);
    }
    std.debug.assert(postorder_count == postorder_keys.len);

    return .{
        .checksum = checksum,
        .inorder_keys = inorder_keys,
        .postorder_keys = postorder_keys,
        .replacement_cleared = replacement_cleared,
    };
}

test "phase1 rbtree postorder bench replay keeps the postorder-safe witness explicit" {
    const replay = runPostorderReplay();
    try std.testing.expectEqual([5]i32{ 5, 10, 15, 20, 25 }, replay.inorder_keys);
    try std.testing.expect(replay.replacement_cleared);
    try std.testing.expectEqual([3]i32{ 5, 25, 15 }, replay.postorder_keys);
    try std.testing.expectEqual(@as(u64, 327), replay.checksum);
}

test "phase1 rbtree postorder bench replay matches the bench checksum packet" {
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        checksum +%= runPostorderReplay().checksum;
    }
    try std.testing.expectEqual(@as(u64, 1_308_000), checksum);
}
