const std = @import("std");
const rbtree = @import("rbtree");

const iterations_rbtree = 4_000;

const RbEntry = struct {
    key: i32,
    node: rbtree.Node = .{},
};

fn less(a: *const rbtree.Node, b: *const rbtree.Node) bool {
    const lhs: *const RbEntry = @fieldParentPtr("node", a);
    const rhs: *const RbEntry = @fieldParentPtr("node", b);
    return lhs.key < rhs.key;
}

const CachedReplay = struct {
    checksum: u64,
    initial_leftmost_key: i32,
    erase_non_leftmost_returned_leftmost: bool,
    promoted_leftmost_key: i32,
    replacement_leftmost_key: i32,
    inserted_leftmost_key: i32,
    add_cached_leftmost_keys: [3]i32,
};

fn runCachedReplay() CachedReplay {
    var cached_entries = [_]RbEntry{
        .{ .key = 10 },
        .{ .key = 5 },
        .{ .key = 20 },
        .{ .key = 15 },
    };
    var cached_replacement = RbEntry{ .key = 10 };
    var new_leftmost = RbEntry{ .key = 3 };
    var cached_root = rbtree.RootCached.init();
    var add_cached_leftmost_keys = [_]i32{ -1, -1, -1 };
    var add_cached_leftmost_count: usize = 0;

    for (&cached_entries) |*entry| {
        if (rbtree.addCached(&entry.node, &cached_root, less)) |leftmost| {
            const leftmost_entry: *const RbEntry = @fieldParentPtr("node", leftmost);
            add_cached_leftmost_keys[add_cached_leftmost_count] = leftmost_entry.key;
            add_cached_leftmost_count += 1;
        }
    }

    const initial_leftmost_entry: *const RbEntry = @fieldParentPtr(
        "node",
        rbtree.firstCached(&cached_root).?,
    );
    const erase_non_leftmost_returned_leftmost =
        rbtree.eraseCached(&cached_entries[2].node, &cached_root) == null;
    const still_leftmost_entry: *const RbEntry = @fieldParentPtr(
        "node",
        rbtree.firstCached(&cached_root).?,
    );
    std.debug.assert(still_leftmost_entry.key == initial_leftmost_entry.key);

    const promoted_leftmost = rbtree.eraseCached(&cached_entries[1].node, &cached_root) orelse unreachable;
    const promoted_leftmost_entry: *const RbEntry = @fieldParentPtr("node", promoted_leftmost);

    rbtree.replaceNodeCached(&cached_entries[0].node, &cached_replacement.node, &cached_root);
    const replacement_leftmost_entry: *const RbEntry = @fieldParentPtr(
        "node",
        rbtree.firstCached(&cached_root).?,
    );

    if (rbtree.addCached(&new_leftmost.node, &cached_root, less)) |leftmost| {
        const leftmost_entry: *const RbEntry = @fieldParentPtr("node", leftmost);
        add_cached_leftmost_keys[add_cached_leftmost_count] = leftmost_entry.key;
        add_cached_leftmost_count += 1;
    }
    const inserted_leftmost_entry: *const RbEntry = @fieldParentPtr(
        "node",
        rbtree.firstCached(&cached_root).?,
    );

    var checksum: u64 = 0;
    checksum +%= @as(u64, @intFromBool(rbtree.first(&cached_root.root) == rbtree.firstCached(&cached_root)));
    checksum +%= @intCast(initial_leftmost_entry.key);
    checksum +%= @as(u64, @intFromBool(erase_non_leftmost_returned_leftmost));
    checksum +%= @intCast(still_leftmost_entry.key);
    checksum +%= @intCast(promoted_leftmost_entry.key);
    checksum +%= @as(u64, @intFromBool(rbtree.first(&cached_root.root) == rbtree.firstCached(&cached_root)));
    checksum +%= @intCast(replacement_leftmost_entry.key);
    checksum +%= @intCast(inserted_leftmost_entry.key);
    checksum +%= @as(u64, @intFromBool(rbtree.first(&cached_root.root) == rbtree.firstCached(&cached_root)));

    return .{
        .checksum = checksum,
        .initial_leftmost_key = initial_leftmost_entry.key,
        .erase_non_leftmost_returned_leftmost = erase_non_leftmost_returned_leftmost,
        .promoted_leftmost_key = promoted_leftmost_entry.key,
        .replacement_leftmost_key = replacement_leftmost_entry.key,
        .inserted_leftmost_key = inserted_leftmost_entry.key,
        .add_cached_leftmost_keys = add_cached_leftmost_keys,
    };
}

test "phase1 rbtree cached bench replay keeps leftmost-return semantics explicit" {
    const replay = runCachedReplay();
    try std.testing.expectEqual(@as(i32, 5), replay.initial_leftmost_key);
    try std.testing.expect(replay.erase_non_leftmost_returned_leftmost);
    try std.testing.expectEqual(@as(i32, 10), replay.promoted_leftmost_key);
    try std.testing.expectEqual(@as(i32, 10), replay.replacement_leftmost_key);
    try std.testing.expectEqual(@as(i32, 3), replay.inserted_leftmost_key);
    try std.testing.expectEqual([3]i32{ 10, 5, 3 }, replay.add_cached_leftmost_keys);
    try std.testing.expectEqual(@as(u64, 37), replay.checksum);
}

test "phase1 rbtree cached bench replay matches the bench checksum packet" {
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        checksum +%= runCachedReplay().checksum;
    }
    try std.testing.expectEqual(@as(u64, 148_000), checksum);
}
