const std = @import("std");

const BenchPacket = struct {
    name: []const u8,
    iterations_label: []const u8,
    checksum_label: []const u8,
};

const bench_packets = [_]BenchPacket{
    .{
        .name = "bitmap-weight",
        .iterations_label = "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
        .checksum_label = "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
    },
    .{
        .name = "bitmap-window",
        .iterations_label = "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS",
        .checksum_label = "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
    },
    .{
        .name = "find-next-bit",
        .iterations_label = "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS",
        .checksum_label = "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
    },
    .{
        .name = "find-bit-edge",
        .iterations_label = "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS",
        .checksum_label = "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
    },
    .{
        .name = "string",
        .iterations_label = "PHASE1_BENCH_STRING_ITERATIONS",
        .checksum_label = "PHASE1_BENCH_STRING_CHECKSUM",
    },
    .{
        .name = "hweight",
        .iterations_label = "PHASE1_BENCH_HWEIGHT_ITERATIONS",
        .checksum_label = "PHASE1_BENCH_HWEIGHT_CHECKSUM",
    },
    .{
        .name = "list-sort",
        .iterations_label = "PHASE1_BENCH_LIST_SORT_ITERATIONS",
        .checksum_label = "PHASE1_BENCH_LIST_SORT_CHECKSUM",
    },
    .{
        .name = "rbtree",
        .iterations_label = "PHASE1_BENCH_RBTREE_ITERATIONS",
        .checksum_label = "PHASE1_BENCH_RBTREE_CHECKSUM",
    },
    .{
        .name = "rbtree-postorder-safe",
        .iterations_label = "PHASE1_BENCH_RBTREE_ITERATIONS",
        .checksum_label = "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
    },
    .{
        .name = "rbtree-find-add",
        .iterations_label = "PHASE1_BENCH_RBTREE_ITERATIONS",
        .checksum_label = "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
    },
    .{
        .name = "rbtree-duplicate",
        .iterations_label = "PHASE1_BENCH_RBTREE_ITERATIONS",
        .checksum_label = "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
    },
    .{
        .name = "rbtree-cached",
        .iterations_label = "PHASE1_BENCH_RBTREE_ITERATIONS",
        .checksum_label = "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
    },
};

const unique_iteration_labels = [_][]const u8{
    "PHASE1_BENCH_BITMAP_WEIGHT_ITERATIONS",
    "PHASE1_BENCH_BITMAP_WINDOW_ITERATIONS",
    "PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS",
    "PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS",
    "PHASE1_BENCH_STRING_ITERATIONS",
    "PHASE1_BENCH_HWEIGHT_ITERATIONS",
    "PHASE1_BENCH_LIST_SORT_ITERATIONS",
    "PHASE1_BENCH_RBTREE_ITERATIONS",
};

fn countLabel(labels: []const []const u8, wanted: []const u8) usize {
    var count: usize = 0;
    for (labels) |label| {
        if (std.mem.eql(u8, label, wanted)) {
            count += 1;
        }
    }
    return count;
}

test "phase1 bench output contract covers every helper packet" {
    try std.testing.expectEqual(@as(usize, 12), bench_packets.len);
    try std.testing.expectEqualStrings("bitmap-weight", bench_packets[0].name);
    try std.testing.expectEqualStrings("rbtree-cached", bench_packets[bench_packets.len - 1].name);

    var rbtree_packet_count: usize = 0;
    for (bench_packets) |packet| {
        try std.testing.expect(std.mem.startsWith(u8, packet.iterations_label, "PHASE1_BENCH_"));
        try std.testing.expect(std.mem.endsWith(u8, packet.iterations_label, "_ITERATIONS"));
        try std.testing.expect(std.mem.startsWith(u8, packet.checksum_label, "PHASE1_BENCH_"));
        try std.testing.expect(std.mem.endsWith(u8, packet.checksum_label, "_CHECKSUM"));

        if (std.mem.eql(u8, packet.iterations_label, "PHASE1_BENCH_RBTREE_ITERATIONS")) {
            rbtree_packet_count += 1;
        }
    }

    try std.testing.expectEqual(@as(usize, 5), rbtree_packet_count);
}

test "phase1 bench output contract keeps labels unique where required" {
    var checksum_labels: [bench_packets.len][]const u8 = undefined;
    for (bench_packets, 0..) |packet, index| {
        checksum_labels[index] = packet.checksum_label;
    }

    for (checksum_labels, 0..) |label, index| {
        try std.testing.expectEqual(@as(usize, 1), countLabel(checksum_labels[0 .. index + 1], label));
    }

    for (unique_iteration_labels) |label| {
        var seen = false;
        for (bench_packets) |packet| {
            seen = seen or std.mem.eql(u8, packet.iterations_label, label);
        }
        try std.testing.expect(seen);
    }
}
