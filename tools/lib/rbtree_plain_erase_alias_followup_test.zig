const std = @import("std");
const rbtree = @import("rbtree.zig");

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn erasePlainAlias(node: *rbtree.Node, root: *rbtree.Root) void {
    if (@hasDecl(rbtree, "rb_erase")) {
        rbtree.rb_erase(node, root);
    } else {
        rbtree.erase(node, root);
    }
}

fn eraseInitPlainAlias(node: *rbtree.Node, root: *rbtree.Root) void {
    if (@hasDecl(rbtree, "rb_erase_init")) {
        rbtree.rb_erase_init(node, root);
    } else {
        rbtree.eraseInit(node, root);
    }
}

fn readOrder(root: *const rbtree.Root, out: []i32) usize {
    var count: usize = 0;
    var current = rbtree.first(root);
    while (current) |node| : (current = rbtree.next(node)) {
        const entry: *const Entry = @fieldParentPtr("node", node);
        out[count] = entry.key;
        count += 1;
    }
    return count;
}

test "plain erase alias follow-up mirrors primary erase surfaces" {
    var primary_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 4, .serial = 1 },
        .{ .key = 16, .serial = 2 },
        .{ .key = 12, .serial = 3 },
        .{ .key = 20, .serial = 4 },
    };
    var alias_entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 4, .serial = 1 },
        .{ .key = 16, .serial = 2 },
        .{ .key = 12, .serial = 3 },
        .{ .key = 20, .serial = 4 },
    };
    var primary_root = rbtree.Root.init();
    var alias_root = rbtree.Root.init();

    for (&primary_entries, &alias_entries) |*primary_entry, *alias_entry| {
        rbtree.add(&primary_entry.node, &primary_root, less);
        rbtree.add(&alias_entry.node, &alias_root, less);
    }

    rbtree.erase(&primary_entries[2].node, &primary_root);
    erasePlainAlias(&alias_entries[2].node, &alias_root);
    rbtree.eraseInit(&primary_entries[1].node, &primary_root);
    eraseInitPlainAlias(&alias_entries[1].node, &alias_root);

    try std.testing.expect(rbtree.emptyNode(&primary_entries[1].node));
    try std.testing.expect(rbtree.emptyNode(&alias_entries[1].node));

    var primary_order: [5]i32 = undefined;
    var alias_order: [5]i32 = undefined;
    const primary_count = readOrder(&primary_root, &primary_order);
    const alias_count = readOrder(&alias_root, &alias_order);

    try std.testing.expectEqual(primary_count, alias_count);
    try std.testing.expectEqualSlices(i32, primary_order[0..primary_count], alias_order[0..alias_count]);
    try std.testing.expectEqualSlices(i32, &[_]i32{ 10, 12, 20 }, alias_order[0..alias_count]);
}
