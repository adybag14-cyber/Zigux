const std = @import("std");
const list_sort = @import("list_sort");

const iterations_list_sort = 1_000;
const expected_checksum_per_iteration: u64 = 690;
const expected_checksum: u64 = expected_checksum_per_iteration * iterations_list_sort;

const Entry = struct {
    key: i32,
    ordinal: usize,
    node: list_sort.ListHead = .{},
};

const cmp = struct {
    fn compare(_: ?*anyopaque, a: *const list_sort.ListHead, b: *const list_sort.ListHead) i32 {
        const lhs: *const Entry = @fieldParentPtr("node", a);
        const rhs: *const Entry = @fieldParentPtr("node", b);
        if (lhs.key < rhs.key) return -1;
        if (lhs.key > rhs.key) return 1;
        return 0;
    }
}.compare;

fn seedEntries() [128]Entry {
    var entries: [128]Entry = undefined;
    for (&entries, 0..) |*entry, idx| {
        entry.* = .{
            .key = @intCast((127 - idx) % 11),
            .ordinal = idx,
        };
    }
    return entries;
}

fn runListSortBench() !u64 {
    var checksum: u64 = 0;
    var iter: usize = 0;
    while (iter < iterations_list_sort) : (iter += 1) {
        var head: list_sort.ListHead = .{};
        head.init();
        var entries = seedEntries();
        for (&entries) |*entry| {
            list_sort.listAddTail(&entry.node, &head);
        }

        list_sort.listSort(null, &head, cmp);

        var current = head.next;
        while (current != &head) : (current = current.?.next) {
            const entry: *const Entry = @fieldParentPtr("node", current.?);
            checksum +%= @intCast(entry.key + @as(i32, @intCast(entry.ordinal & 1)));
            try std.testing.expect(current.?.next.?.prev == current.?);
            try std.testing.expect(current.?.prev.?.next == current.?);
        }
    }

    return checksum;
}

test "phase1 list_sort bench replay preserves stable key order" {
    var head: list_sort.ListHead = .{};
    head.init();
    var entries = seedEntries();
    for (&entries) |*entry| {
        list_sort.listAddTail(&entry.node, &head);
    }

    list_sort.listSort(null, &head, cmp);

    var last_key: ?i32 = null;
    var previous_duplicate_ordinal: ?usize = null;
    var item_count: usize = 0;
    var per_iteration_checksum: u64 = 0;
    var current = head.next;
    while (current != &head) : (current = current.?.next) {
        const entry: *const Entry = @fieldParentPtr("node", current.?);
        if (last_key) |key| {
            try std.testing.expect(key <= entry.key);
            if (key == entry.key) {
                try std.testing.expect(previous_duplicate_ordinal.? < entry.ordinal);
            } else {
                previous_duplicate_ordinal = null;
            }
        }
        last_key = entry.key;
        previous_duplicate_ordinal = entry.ordinal;
        per_iteration_checksum +%= @intCast(entry.key + @as(i32, @intCast(entry.ordinal & 1)));
        try std.testing.expect(current.?.next.?.prev == current.?);
        try std.testing.expect(current.?.prev.?.next == current.?);
        item_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 128), item_count);
    try std.testing.expectEqual(expected_checksum_per_iteration, per_iteration_checksum);
}

test "phase1 list_sort bench replay keeps the exact 1000-iteration checksum" {
    try std.testing.expectEqual(expected_checksum, try runListSortBench());
}
