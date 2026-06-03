const std = @import("std");
const rbtree = @import("rbtree");

const iterations_rbtree: u64 = 4000;

const TreeEntry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = rbtree.Node.init(),

    fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
        const lhs_entry: *const TreeEntry = @fieldParentPtr("node", lhs);
        const rhs_entry: *const TreeEntry = @fieldParentPtr("node", rhs);
        if (lhs_entry.key != rhs_entry.key) {
            return lhs_entry.key < rhs_entry.key;
        }
        return lhs_entry.serial < rhs_entry.serial;
    }

    fn cmp(lhs: *const rbtree.Node, rhs: *const rbtree.Node) i32 {
        const lhs_entry: *const TreeEntry = @fieldParentPtr("node", lhs);
        const rhs_entry: *const TreeEntry = @fieldParentPtr("node", rhs);
        if (lhs_entry.key < rhs_entry.key) return -1;
        if (lhs_entry.key > rhs_entry.key) return 1;
        return 0;
    }
};

fn rbtreeFindAddBench() struct { checksum: u64 } {
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        var entries = [_]TreeEntry{
            .{ .key = 10, .serial = 0 },
            .{ .key = 5, .serial = 1 },
            .{ .key = 15, .serial = 2 },
        };
        var probe = TreeEntry{ .key = 15, .serial = 3 };
        var root = rbtree.Root.init();
        for (&entries) |*entry| {
            rbtree.add(&entry.node, &root, TreeEntry.less);
        }
        const existing = rbtree.findAdd(&probe.node, &root, TreeEntry.cmp);
        const found = existing orelse unreachable;
        const entry: *const TreeEntry = @fieldParentPtr("node", found);
        checksum +%= @intCast(entry.serial);
    }
    return .{ .checksum = checksum };
}

test "phase1 rbtree findAdd replay returns the existing duplicate node" {
    var entries = [_]TreeEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var probe = TreeEntry{ .key = 15, .serial = 3 };
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, TreeEntry.less);
    }

    const existing = rbtree.findAdd(&probe.node, &root, TreeEntry.cmp) orelse return error.TestUnexpectedResult;
    const entry: *const TreeEntry = @fieldParentPtr("node", existing);
    try std.testing.expectEqual(@as(i32, 15), entry.key);
    try std.testing.expectEqual(@as(usize, 2), entry.serial);
    try std.testing.expect(rbtree.next(&entries[2].node) == null);
}

test "phase1 rbtree findAdd replay inserts missing keys once" {
    var root = rbtree.Root.init();
    var first = TreeEntry{ .key = 10, .serial = 0 };
    var duplicate = TreeEntry{ .key = 10, .serial = 1 };
    var right = TreeEntry{ .key = 20, .serial = 2 };

    try std.testing.expect(rbtree.findAdd(&first.node, &root, TreeEntry.cmp) == null);
    try std.testing.expect(rbtree.findAdd(&duplicate.node, &root, TreeEntry.cmp) == &first.node);
    try std.testing.expect(rbtree.findAdd(&right.node, &root, TreeEntry.cmp) == null);

    const root_entry: *const TreeEntry = @fieldParentPtr("node", root.node.?);
    try std.testing.expectEqual(@as(i32, 10), root_entry.key);
    try std.testing.expectEqual(@as(?*rbtree.Node, &right.node), rbtree.next(&first.node));
}

test "phase1 rbtree findAdd replay keeps the 4000-iteration checksum stable" {
    const result = rbtreeFindAddBench();
    try std.testing.expectEqual(@as(u64, 8000), result.checksum);
}
