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

const DuplicateMutationReplay = struct {
    checksum: u64,
    after_erase_serials: [2]usize,
    after_replace_serials: [2]usize,
};

fn runDuplicateMutationReplay() DuplicateMutationReplay {
    var entries = [_]Entry{
        .{ .key = 10, .serial = 0 },
        .{ .key = 5, .serial = 1 },
        .{ .key = 10, .serial = 2 },
        .{ .key = 20, .serial = 3 },
        .{ .key = 10, .serial = 4 },
        .{ .key = 15, .serial = 5 },
    };
    var replacement = Entry{ .key = 10, .serial = 6 };
    var root = rbtree.Root.init();

    for (&entries) |*entry| {
        rbtree.add(&entry.node, &root, less);
    }

    const wanted = @as(i32, 10);

    rbtree.erase(&entries[2].node, &root);
    var after_erase = rbtree.findFirst(&wanted, &root, keyCmp) orelse unreachable;
    var after_erase_serials = [_]usize{ 0, 0 };
    var erase_index: usize = 0;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", after_erase);
        after_erase_serials[erase_index] = entry.serial;
        erase_index += 1;
        after_erase = rbtree.nextMatch(&wanted, after_erase, keyCmp) orelse break;
    }
    std.debug.assert(erase_index == after_erase_serials.len);

    rbtree.replaceNode(&entries[4].node, &replacement.node, &root);
    var after_replace = rbtree.findFirst(&wanted, &root, keyCmp) orelse unreachable;
    var after_replace_serials = [_]usize{ 0, 0 };
    var replace_index: usize = 0;
    while (true) {
        const entry: *const Entry = @fieldParentPtr("node", after_replace);
        after_replace_serials[replace_index] = entry.serial;
        replace_index += 1;
        after_replace = rbtree.nextMatch(&wanted, after_replace, keyCmp) orelse break;
    }
    std.debug.assert(replace_index == after_replace_serials.len);

    var checksum: u64 = 0;
    for (after_erase_serials) |serial| {
        checksum +%= serial + 97;
    }
    for (after_replace_serials) |serial| {
        checksum +%= serial + 107;
    }

    return .{
        .checksum = checksum,
        .after_erase_serials = after_erase_serials,
        .after_replace_serials = after_replace_serials,
    };
}

test "phase1 rbtree duplicate mutation bench replay keeps erase and replace ranges explicit" {
    const replay = runDuplicateMutationReplay();
    try std.testing.expectEqual([2]usize{ 0, 4 }, replay.after_erase_serials);
    try std.testing.expectEqual([2]usize{ 0, 6 }, replay.after_replace_serials);
    try std.testing.expectEqual(@as(u64, 418), replay.checksum);
}

test "phase1 rbtree duplicate mutation bench replay matches the bench checksum packet" {
    var checksum: u64 = 0;
    var idx: usize = 0;
    while (idx < iterations_rbtree) : (idx += 1) {
        checksum +%= runDuplicateMutationReplay().checksum;
    }
    try std.testing.expectEqual(@as(u64, 1_672_000), checksum);
}
