const std = @import("std");
const rbtree = @import("rbtree");

const iterations_rbtree = 4_000;

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

const CachedBenchReplay = struct {
    checksum: u64,
    initial_leftmost_key: i32,
    erased_non_leftmost_returned_null: bool,
    promoted_key: i32,
    promoted_serial: usize,
    final_leftmost_key: i32,
};

fn runCachedBenchReplay() CachedBenchReplay {
    var entries = [_]TreeEntry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 15, .serial = 2 },
    };
    var cached_root = rbtree.RootCached.init();
    for (&entries) |*entry| {
        _ = rbtree.addCached(&entry.node, &cached_root, TreeEntry.less);
    }

    const initial_leftmost: *const TreeEntry = @fieldParentPtr(
        "node",
        rbtree.firstCached(&cached_root).?,
    );
    const non_leftmost_result = rbtree.eraseCached(&entries[2].node, &cached_root);
    const promoted_leftmost = rbtree.eraseCached(&entries[1].node, &cached_root) orelse unreachable;
    const promoted: *const TreeEntry = @fieldParentPtr("node", promoted_leftmost);
    const final_leftmost: *const TreeEntry = @fieldParentPtr(
        "node",
        rbtree.firstCached(&cached_root).?,
    );

    return .{
        .checksum = @intCast(promoted.serial + 1),
        .initial_leftmost_key = initial_leftmost.key,
        .erased_non_leftmost_returned_null = non_leftmost_result == null,
        .promoted_key = promoted.key,
        .promoted_serial = promoted.serial,
        .final_leftmost_key = final_leftmost.key,
    };
}

test "phase1 rbtree cached bench replay keeps eraseCached promotion explicit" {
    const replay = runCachedBenchReplay();
    try std.testing.expectEqual(@as(i32, 5), replay.initial_leftmost_key);
    try std.testing.expect(replay.erased_non_leftmost_returned_null);
    try std.testing.expectEqual(@as(i32, 10), replay.promoted_key);
    try std.testing.expectEqual(@as(usize, 0), replay.promoted_serial);
    try std.testing.expectEqual(@as(i32, 10), replay.final_leftmost_key);
    try std.testing.expectEqual(@as(u64, 1), replay.checksum);
}

test "phase1 rbtree cached bench replay matches the live bench checksum packet" {
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        checksum +%= runCachedBenchReplay().checksum;
    }

    try std.testing.expectEqual(@as(u64, 4_000), checksum);
}
