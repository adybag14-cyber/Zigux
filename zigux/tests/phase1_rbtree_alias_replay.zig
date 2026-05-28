const std = @import("std");
const rbtree = @import("rbtree");

const ReplayEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const ReplayEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const ReplayEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn cmpNode(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
    const lhs_entry: *const ReplayEntry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const ReplayEntry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key < rhs_entry.key) return -1;
    if (lhs_entry.key > rhs_entry.key) return 1;
    return 0;
}

fn cmpKey(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const ReplayEntry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

fn identity(node: ?*rbtree.Node) ?struct { i32, usize } {
    const current = node orelse return null;
    const entry: *const ReplayEntry = @fieldParentPtr("node", current);
    return .{ entry.key, entry.serial };
}

fn firstKey(root: *const rbtree.RootCached) ?i32 {
    const node = rbtree.firstCached(root) orelse return null;
    const entry: *const ReplayEntry = @fieldParentPtr("node", node);
    return entry.key;
}

test "phase1 rbtree replay keeps cached Linux-style aliases aligned" {
    var primary_first = ReplayEntry{ .key = 10, .serial = 0 };
    var alias_first = ReplayEntry{ .key = 10, .serial = 0 };
    var primary_second = ReplayEntry{ .key = 5, .serial = 1 };
    var alias_second = ReplayEntry{ .key = 5, .serial = 1 };
    var primary_third = ReplayEntry{ .key = 15, .serial = 2 };
    var alias_third = ReplayEntry{ .key = 15, .serial = 2 };
    var primary_duplicate = ReplayEntry{ .key = 10, .serial = 3 };
    var alias_duplicate = ReplayEntry{ .key = 10, .serial = 3 };
    var primary_replacement = ReplayEntry{ .key = 10, .serial = 4 };
    var alias_replacement = ReplayEntry{ .key = 10, .serial = 4 };
    var primary_root = rbtree.RootCached.init();
    var alias_root = rbtree.RootCached.init();

    try std.testing.expectEqual(identity(rbtree.addCached(&primary_first.node, &primary_root, less)), identity(rbtree.rb_add_cached(&alias_first.node, &alias_root, less)));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    try std.testing.expectEqual(identity(rbtree.findAddCached(&primary_second.node, &primary_root, cmpNode)), identity(rbtree.rb_find_add_cached(&alias_second.node, &alias_root, cmpNode)));
    try std.testing.expectEqual(identity(rbtree.findAddCached(&primary_third.node, &primary_root, cmpNode)), identity(rbtree.rb_find_add_cached(&alias_third.node, &alias_root, cmpNode)));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    const primary_existing = rbtree.findAddCached(&primary_duplicate.node, &primary_root, cmpNode) orelse return error.TestUnexpectedResult;
    const alias_existing = rbtree.rb_find_add_cached(&alias_duplicate.node, &alias_root, cmpNode) orelse return error.TestUnexpectedResult;
    try std.testing.expectEqual(identity(primary_existing), identity(alias_existing));

    try std.testing.expectEqual(identity(rbtree.eraseCached(&primary_second.node, &primary_root)), identity(rbtree.rb_erase_cached(&alias_second.node, &alias_root)));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    rbtree.replaceNodeCached(&primary_first.node, &primary_replacement.node, &primary_root);
    rbtree.rb_replace_node_cached(&alias_first.node, &alias_replacement.node, &alias_root);
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    try std.testing.expectEqual(identity(rbtree.eraseCached(&primary_third.node, &primary_root)), identity(rbtree.rb_erase_cached(&alias_third.node, &alias_root)));
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    rbtree.eraseInitCached(&primary_replacement.node, &primary_root);
    rbtree.rb_erase_init_cached(&alias_replacement.node, &alias_root);
    try std.testing.expectEqual(firstKey(&primary_root), firstKey(&alias_root));

    var manual_root = rbtree.RootCached.init();
    var manual_entry = ReplayEntry{ .key = 1, .serial = 0 };
    rbtree.linkNode(&manual_entry.node, null, &manual_root.root.node);
    rbtree.insertColorCached(&manual_entry.node, &manual_root, true);

    var manual_alias_root = rbtree.RootCached.init();
    var manual_alias_entry = ReplayEntry{ .key = 1, .serial = 0 };
    rbtree.linkNode(&manual_alias_entry.node, null, &manual_alias_root.root.node);
    rbtree.rb_insert_color_cached(&manual_alias_entry.node, &manual_alias_root, true);

    try std.testing.expectEqual(firstKey(&manual_root), firstKey(&manual_alias_root));
}
