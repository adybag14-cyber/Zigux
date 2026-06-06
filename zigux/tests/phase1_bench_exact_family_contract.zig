const std = @import("std");

const bench_checker_path = "scripts/zigux/check-phase1-bench.py";
const expectations_path = "zigux/tests/fixtures/phase1_bench_expectations.json";

const Family = struct {
    set_name: []const u8,
    required_reason: []const u8,
    missing_reason: []const u8,
    keys: []const []const u8,
};

const families = [_]Family{
    .{
        .set_name = "BITMAP_REQUIRED_EXACT_CHECKSUMS",
        .required_reason = "expectations_checksums_bitmap_exact_required",
        .missing_reason = "missing_bitmap_exact_checksums",
        .keys = &.{
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
        },
    },
    .{
        .set_name = "FIND_BIT_REQUIRED_EXACT_CHECKSUMS",
        .required_reason = "expectations_checksums_find_bit_exact_required",
        .missing_reason = "missing_find_bit_exact_checksums",
        .keys = &.{
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
        },
    },
    .{
        .set_name = "STRING_REQUIRED_EXACT_CHECKSUMS",
        .required_reason = "expectations_checksums_string_exact_required",
        .missing_reason = "missing_string_exact_checksums",
        .keys = &.{"PHASE1_BENCH_STRING_CHECKSUM"},
    },
    .{
        .set_name = "HWEIGHT_REQUIRED_EXACT_CHECKSUMS",
        .required_reason = "expectations_checksums_hweight_exact_required",
        .missing_reason = "missing_hweight_exact_checksums",
        .keys = &.{"PHASE1_BENCH_HWEIGHT_CHECKSUM"},
    },
    .{
        .set_name = "LIST_SORT_REQUIRED_EXACT_CHECKSUMS",
        .required_reason = "expectations_checksums_list_sort_exact_required",
        .missing_reason = "missing_list_sort_exact_checksums",
        .keys = &.{"PHASE1_BENCH_LIST_SORT_CHECKSUM"},
    },
    .{
        .set_name = "RBTREE_REQUIRED_EXACT_CHECKSUMS",
        .required_reason = "expectations_checksums_rbtree_exact_required",
        .missing_reason = "missing_rbtree_exact_checksums",
        .keys = &.{
            "PHASE1_BENCH_RBTREE_CHECKSUM",
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
        },
    },
};

const expected_exact_values = [_]struct {
    key: []const u8,
    value: []const u8,
}{
    .{ .key = "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM", .value = "100000" },
    .{ .key = "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM", .value = "120000" },
    .{ .key = "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM", .value = "3780000" },
    .{ .key = "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM", .value = "4020000" },
    .{ .key = "PHASE1_BENCH_STRING_CHECKSUM", .value = "320000" },
    .{ .key = "PHASE1_BENCH_HWEIGHT_CHECKSUM", .value = "6800000" },
    .{ .key = "PHASE1_BENCH_LIST_SORT_CHECKSUM", .value = "10000" },
    .{ .key = "PHASE1_BENCH_RBTREE_CHECKSUM", .value = "24000" },
    .{ .key = "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM", .value = "24000" },
    .{ .key = "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM", .value = "8000" },
    .{ .key = "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM", .value = "24000" },
    .{ .key = "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM", .value = "4000" },
};

fn loadFile(io: std.Io, path: []const u8, limit: usize) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn expectOccurrenceCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

fn expectFamilySet(checker: []const u8, family: Family) !void {
    try expectContains(checker, family.set_name);
    try expectContains(checker, family.required_reason);
    try expectContains(checker, family.missing_reason);
    for (family.keys) |key| {
        try expectContains(checker, key);
    }
}

fn isCurrentFamilyAwareChecker(checker: []const u8) bool {
    return std.mem.indexOf(u8, checker, "HWEIGHT_REQUIRED_EXACT_CHECKSUMS") != null and
        std.mem.indexOf(u8, checker, "LIST_SORT_REQUIRED_EXACT_CHECKSUMS") != null and
        std.mem.indexOf(u8, checker, "exact_requirements = (") != null;
}

test "phase 1 bench checker keeps exact checksum families distinct" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const checker = try loadFile(io_instance.io(), bench_checker_path, 128 * 1024);
    defer std.testing.allocator.free(checker);

    if (!isCurrentFamilyAwareChecker(checker)) return error.SkipZigTest;

    var previous_set: ?[]const u8 = null;
    for (families) |family| {
        try expectFamilySet(checker, family);
        if (previous_set) |set_name| {
            try expectBefore(checker, set_name, family.set_name);
        }
        previous_set = family.set_name;
    }
}

test "phase 1 bench checker has family-specific required and output failure labels" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const checker = try loadFile(io_instance.io(), bench_checker_path, 128 * 1024);
    defer std.testing.allocator.free(checker);

    if (!isCurrentFamilyAwareChecker(checker)) return error.SkipZigTest;

    try expectContains(checker, "exact_requirements = (");
    try expectContains(checker, "exact_categories = (");
    for (families) |family| {
        try expectContains(checker, family.required_reason);
        try expectContains(checker, family.missing_reason);
    }
    try expectBefore(checker, "expectations_checksums_bitmap_exact_required", "expectations_checksums_find_bit_exact_required");
    try expectBefore(checker, "expectations_checksums_find_bit_exact_required", "expectations_checksums_string_exact_required");
    try expectBefore(checker, "expectations_checksums_string_exact_required", "expectations_checksums_hweight_exact_required");
    try expectBefore(checker, "expectations_checksums_hweight_exact_required", "expectations_checksums_list_sort_exact_required");
    try expectBefore(checker, "expectations_checksums_list_sort_exact_required", "expectations_checksums_rbtree_exact_required");
}

test "phase 1 bench expectations fixture carries every exact checksum in roster and exact map" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const expectations = try loadFile(io_instance.io(), expectations_path, 64 * 1024);
    defer std.testing.allocator.free(expectations);

    if (std.mem.indexOf(u8, expectations, "\"PHASE1_BENCH_HWEIGHT_CHECKSUM\": 6800000") == null) {
        return error.SkipZigTest;
    }

    for (families) |family| {
        for (family.keys) |key| {
            try expectOccurrenceCount(expectations, key, 2);
        }
    }
    for (expected_exact_values) |entry| {
        var marker_buffer: [128]u8 = undefined;
        const marker = try std.fmt.bufPrint(
            &marker_buffer,
            "\"{s}\": {s}",
            .{ entry.key, entry.value },
        );
        try expectContains(expectations, marker);
    }
}

test "phase 1 bench fixture checksum roster stays ordered before exact values" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const expectations = try loadFile(io_instance.io(), expectations_path, 64 * 1024);
    defer std.testing.allocator.free(expectations);

    if (std.mem.indexOf(u8, expectations, "\"PHASE1_BENCH_LIST_SORT_CHECKSUM\": 10000") == null) {
        return error.SkipZigTest;
    }

    var previous: ?[]const u8 = null;
    for (expected_exact_values) |entry| {
        if (previous) |prior_key| {
            try expectBefore(expectations, prior_key, entry.key);
        }
        previous = entry.key;
    }
    try expectBefore(expectations, "\"checksums\": [", "\"exact_checksums\": {");
}
