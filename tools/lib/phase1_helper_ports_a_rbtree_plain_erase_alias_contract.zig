const std = @import("std");
const rbtree = @import("rbtree.zig");

const Node = rbtree.Node;
const Root = rbtree.Root;

const Entry = struct {
    key: i32,
    node: Node = Node.init(),
};

fn less(lhs: *const Node, rhs: *const Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    return lhs_entry.key < rhs_entry.key;
}

fn plainErase(node: *Node, root: *Root) void {
    if (@hasDecl(rbtree, "rb_erase")) {
        rbtree.rb_erase(node, root);
    } else {
        rbtree.erase(node, root);
    }
}

fn plainEraseInit(node: *Node, root: *Root) void {
    if (@hasDecl(rbtree, "rb_erase_init")) {
        rbtree.rb_erase_init(node, root);
    } else {
        rbtree.eraseInit(node, root);
    }
}

fn collectKeys(root: *const Root, out: []i32) usize {
    var count: usize = 0;
    var cursor = rbtree.first(root);
    while (cursor) |node| : (cursor = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "phase1 rbtree plain erase alias contract preserves traversal parity" {
    var primary_entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 3 },
        .{ .key = 12 },
        .{ .key = 10 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 3 },
        .{ .key = 12 },
        .{ .key = 10 },
    };
    var primary_root = Root.init();
    var alias_root = Root.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, less);
        rbtree.add(&alias_entry.node, &alias_root, less);
    }

    rbtree.erase(&primary_entries[2].node, &primary_root);
    plainErase(&alias_entries[2].node, &alias_root);

    var primary_order: [3]i32 = undefined;
    var alias_order: [3]i32 = undefined;
    const primary_count = collectKeys(&primary_root, &primary_order);
    const alias_count = collectKeys(&alias_root, &alias_order);

    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(i32, primary_order[0..primary_count], alias_order[0..alias_count]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, 8, 10 }, alias_order[0..alias_count]);
}

test "phase1 rbtree plain erase init alias contract clears removed nodes" {
    var primary_entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 3 },
        .{ .key = 12 },
        .{ .key = 10 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 8 },
        .{ .key = 3 },
        .{ .key = 12 },
        .{ .key = 10 },
    };
    var primary_root = Root.init();
    var alias_root = Root.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, less);
        rbtree.add(&alias_entry.node, &alias_root, less);
    }

    rbtree.eraseInit(&primary_entries[0].node, &primary_root);
    plainEraseInit(&alias_entries[0].node, &alias_root);

    try std.testing.expect(rbtree.emptyNode(&primary_entries[0].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[0].node));

    var primary_order: [3]i32 = undefined;
    var alias_order: [3]i32 = undefined;
    const primary_count = collectKeys(&primary_root, &primary_order);
    const alias_count = collectKeys(&alias_root, &alias_order);

    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 3, 10, 12 }, alias_order[0..alias_count]);
    try std.testing.expectEqualSlices(i32, primary_order[0..primary_count], alias_order[0..alias_count]);
}
