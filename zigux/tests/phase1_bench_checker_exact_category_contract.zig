const std = @import("std");

const ExactCategory = struct {
    expectation_reason: []const u8,
    output_reason: []const u8,
    set_name: []const u8,
    checksum_keys: []const []const u8,
};

const exact_categories = [_]ExactCategory{
    .{
        .expectation_reason = "expectations_checksums_bitmap_exact_required",
        .output_reason = "missing_bitmap_exact_checksums",
        .set_name = "BITMAP_REQUIRED_EXACT_CHECKSUMS",
        .checksum_keys = &.{
            "PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM",
            "PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM",
        },
    },
    .{
        .expectation_reason = "expectations_checksums_find_bit_exact_required",
        .output_reason = "missing_find_bit_exact_checksums",
        .set_name = "FIND_BIT_REQUIRED_EXACT_CHECKSUMS",
        .checksum_keys = &.{
            "PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM",
            "PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM",
        },
    },
    .{
        .expectation_reason = "expectations_checksums_string_exact_required",
        .output_reason = "missing_string_exact_checksums",
        .set_name = "STRING_REQUIRED_EXACT_CHECKSUMS",
        .checksum_keys = &.{"PHASE1_BENCH_STRING_CHECKSUM"},
    },
    .{
        .expectation_reason = "expectations_checksums_hweight_exact_required",
        .output_reason = "missing_hweight_exact_checksums",
        .set_name = "HWEIGHT_REQUIRED_EXACT_CHECKSUMS",
        .checksum_keys = &.{"PHASE1_BENCH_HWEIGHT_CHECKSUM"},
    },
    .{
        .expectation_reason = "expectations_checksums_list_sort_exact_required",
        .output_reason = "missing_list_sort_exact_checksums",
        .set_name = "LIST_SORT_REQUIRED_EXACT_CHECKSUMS",
        .checksum_keys = &.{"PHASE1_BENCH_LIST_SORT_CHECKSUM"},
    },
    .{
        .expectation_reason = "expectations_checksums_rbtree_exact_required",
        .output_reason = "missing_rbtree_exact_checksums",
        .set_name = "RBTREE_REQUIRED_EXACT_CHECKSUMS",
        .checksum_keys = &.{
            "PHASE1_BENCH_RBTREE_CHECKSUM",
            "PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM",
            "PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM",
            "PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM",
            "PHASE1_BENCH_RBTREE_CACHED_CHECKSUM",
        },
    },
};

fn readCheckerSource(allocator: std.mem.Allocator) ![]u8 {
    const paths = [_][]const u8{
        "scripts/zigux/check-phase1-bench.py",
        "../../scripts/zigux/check-phase1-bench.py",
    };
    var last_error: anyerror = error.FileNotFound;
    for (paths) |path| {
        return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(512 * 1024)) catch |err| {
            last_error = err;
            continue;
        };
    }
    return last_error;
}

fn expectContains(source: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, needle) != null);
}

fn expectOrderedAfter(source: []const u8, previous: *usize, needle: []const u8) !void {
    const relative = std.mem.indexOf(u8, source[previous.*..], needle) orelse return error.MissingOrderedMarker;
    previous.* += relative + needle.len;
}

test "phase1 bench checker keeps exact checksum category sets explicit" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "REQUIRED_EXACT_CHECKSUMS = set(EXPECTED_CHECKSUMS)");
    for (exact_categories) |category| {
        try expectContains(source, category.set_name);
        for (category.checksum_keys) |checksum_key| {
            try expectContains(source, checksum_key);
        }
    }
}

test "phase1 bench checker maps expectation exact categories before generic missing checksums" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "exact_requirements = (");
    var position: usize = 0;
    for (exact_categories) |category| {
        try expectOrderedAfter(source, &position, category.expectation_reason);
        try expectOrderedAfter(source, &position, category.set_name);
    }
    try expectOrderedAfter(source, &position, "expectations_missing_exact_checksums");
    try expectOrderedAfter(source, &position, "expectations_unexpected_exact_checksums");
}

test "phase1 bench checker returns helper specific missing-output exact checksum reasons" {
    const source = try readCheckerSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    try expectContains(source, "exact_categories = (");
    const output_order = [_]usize{ 5, 0, 1, 2, 3, 4 };
    var position: usize = 0;
    for (output_order) |category_index| {
        const category = exact_categories[category_index];
        try expectOrderedAfter(source, &position, category.output_reason);
        try expectOrderedAfter(source, &position, category.set_name);
    }
}
