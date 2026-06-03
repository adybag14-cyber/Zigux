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
};

fn cachedBenchIterationChecksum() u64 {
    var entries = [_]TreeEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var cached_root = rbtree.RootCached.init();

    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &cached_root, TreeEntry.less);
    }

    tryNonLeftmostEraseStaysSilent(&entries, &cached_root);

    const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root) orelse unreachable;
    const promoted: *const TreeEntry = @fieldParentPtr("node", promoted_leftmost);

    return @intCast(promoted.serial + 1);
}

fn tryNonLeftmostEraseStaysSilent(entries: []TreeEntry, cached_root: *rbtree.RootCached) void {
    if (rbtree.eraseCached(&entries[2].node, cached_root) != null) {
        unreachable;
    }
}

fn cachedBenchChecksum() u64 {
    var checksum: u64 = 0;
    var idx: u64 = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        checksum +%= cachedBenchIterationChecksum();
    }
    return checksum;
}

test "rbtree cached bench promotes the next leftmost node" {
    try std.testing.expectEqual(@as(u64, 1), cachedBenchIterationChecksum());
}

test "rbtree cached bench checksum matches the current Phase 1 packet" {
    try std.testing.expectEqual(@as(u64, 4000), cachedBenchChecksum());
}
