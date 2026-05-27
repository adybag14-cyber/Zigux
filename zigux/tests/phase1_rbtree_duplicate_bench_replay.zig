const std = @import("std");
const rbtree = @import("rbtree");

const iterations_rbtree = 4_000;

const Entry = struct {
    key: i32,
    serial: usize,
    node: rbtree.Node = .{},
};

fn less(lhs: *const rbtree.Node, rhs: *const rbtree.Node) bool {
    const lhs_entry: *const Entry = @fieldParentPtr("node", lhs);
    const rhs_entry: *const Entry = @fieldParentPtr("node", rhs);
    if (lhs_entry.key != rhs_entry.key) {
        return lhs_entry.key < rhs_entry.key;
    }
    return lhs_entry.serial < rhs_entry.serial;
}

fn keyCmp(key: *const anyopaque, node: *const rbtree.Node) i32 {
    const wanted: *const i32 = @ptrCast(@alignCast(key));
    const entry: *const Entry = @fieldParentPtr("node", node);
    if (wanted.* < entry.key) return -1;
    if (wanted.* > entry.key) return 1;
    return 0;
}

const DuplicateReplay = struct {
    checksum: u64,
    found_key: i32,
    first_duplicate_serial: usize,
    next_match_serials: [3]usize,
    iterator_serials: [3]usize,
    missing_is_null: bool,
};

fn runDuplicateReplay() DuplicateReplay {
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 20, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 5, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const wanted = @as(i32, 15);
    const found = rbtree.find(&wanted, &root, keyCmp) orelse unreachable;
    const found_entry: *const Entry = @fieldParentPtr("node", found);

    const missing = @as(i32, 17);
    const missing_is_null = rbtree.find(&missing, &root, keyCmp) == null;

    const duplicate_key = @as(i32, 10);
    const first_match = rbtree.findFirst(&duplicate_key, &root, keyCmp) orelse unreachable;
    const first_match_entry: *const Entry = @fieldParentPtr("node", first_match);

    var next_match_serials = [_]usize{ 0, 0, 0 };
    var next_match_count: usize = 0;
    var cursor = first_match;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", cursor);
        next_match_serials[next_match_count] = entry.serial;
        next_match_count += 1;
        cursor = rbtree.nextMatch(&duplicate_key, cursor, keyCmp) orelse break;
    }
    std.debug.assert(next_match_count == next_match_serials.len);
    std.debug.assert(rbtree.nextMatch(&duplicate_key, cursor, keyCmp) == null);

    var iterator_serials = [_]usize{ 0, 0, 0 };
    var iterator_count: usize = 0;
    var iter = rbtree.matchIterator(&duplicate_key, &root, keyCmp);
    while (iter.next()) |node| {
        const entry: *const Entry = @fieldParentPtr("node", node);
        iterator_serials[iterator_count] = entry.serial;
        iterator_count += 1;
    }
    std.debug.assert(iterator_count == iterator_serials.len);

    var checksum: u64 = 0;
    checksum +%= @intCast(found_entry.key);
    checksum +%= @intCast(first_match_entry.serial);
    checksum +%= @as(u64, @intFromBool(missing_is_null));
    for (next_match_serials) |serial| {
        checksum +%= @intCast(serial);
    }
    for (iterator_serials) |serial| {
        checksum +%= @intCast(serial);
    }

    return .{
        .checksum = checksum,
        .found_key = found_entry.key,
        .first_duplicate_serial = first_match_entry.serial,
        .next_match_serials = next_match_serials,
        .iterator_serials = iterator_serials,
        .missing_is_null = missing_is_null,
    };
}

test "phase1 rbtree duplicate bench replay keeps duplicate-range traversal reviewable" {
    const replay = runDuplicateReplay();
    try std.testing.expectEqual(@as(i32, 15), replay.found_key);
    try std.testing.expectEqual(@as(usize, 0), replay.first_duplicate_serial);
    try std.testing.expectEqual([3]usize{ 0, 2, 4 }, replay.next_match_serials);
    try std.testing.expectEqual([3]usize{ 0, 2, 4 }, replay.iterator_serials);
    try std.testing.expect(replay.missing_is_null);
    try std.testing.expectEqual(@as(u64, 28), replay.checksum);
}

test "phase1 rbtree duplicate bench replay matches the bench checksum packet" {
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        checksum +%= runDuplicateReplay().checksum;
    }
    try std.testing.expectEqual(@as(u64, 112_000), checksum);
}
