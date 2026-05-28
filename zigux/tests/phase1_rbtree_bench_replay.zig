const std = @import("std");
const rbtree = @import("rbtree");

const iterations_rbtree = 4_000;
const expected_checksum_per_iteration: u64 = 6;
const expected_checksum: u64 = expected_checksum_per_iteration * iterations_rbtree;

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
};

fn seedEntries() [3]TreeEntry {
    return .{
        .{ .key = 2, .serial = 0 },
        .{ .key = 1, .serial = 1 },
        .{ .key = 3, .serial = 2 },
    };
}

fn runRbtreeBenchReplay() u64 {
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        var entries = seedEntries();
        var root = rbtree.Root.init();
        for (&entries) |*entry| {
            rbtree.add(&entry.node, &root, TreeEntry.less);
        }

        var node = rbtree.first(&root);
        while (node) |current| : (node = rbtree.next(current)) {
            const entry: *const TreeEntry = @fieldParentPtr("node", current);
            checksum +%= @intCast(entry.key);
        }
    }
    return checksum;
}

test "phase1 rbtree bench replay keeps the in-order witness explicit" {
    var entries = seedEntries();
    var root = rbtree.Root.init();
    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, TreeEntry.less);
    }

    var ordered_keys = [_]i32{ 0, 0, 0 };
    var count: usize = 0;
    var node = rbtree.first(&root);
    while (node) |current| : (node = rbtree.next(current)) {
        const entry: *const TreeEntry = @fieldParentPtr("node", current);
        ordered_keys[count] = entry.key;
        count += 1;
    }

    try std.testing.expectEqual(@as(usize, 3), count);
    try std.testing.expectEqual([3]i32{ 1, 2, 3 }, ordered_keys);
}

test "phase1 rbtree bench replay keeps the exact 4000-iteration checksum" {
    try std.testing.expectEqual(expected_checksum, runRbtreeBenchReplay());
}
