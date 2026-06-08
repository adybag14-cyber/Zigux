const std = @import("std");
const testing = std.testing;

const ClosureFamily = struct {
    helper: []const u8,
    checker_marker: []const u8,
    validator_marker: []const u8,
    manifest_marker: []const u8,
};

const direct_anchor_families = [_]ClosureFamily{
    .{
        .helper = "bitmap",
        .checker_marker = "BITMAP_REQUIRED_EXACT_CHECKSUMS",
        .validator_marker = "BITMAP_DIRECT_ANCHOR_CHECKER_REL",
        .manifest_marker = "\"tools/lib/bitmap.zig\"",
    },
    .{
        .helper = "find_bit",
        .checker_marker = "FIND_BIT_REQUIRED_EXACT_CHECKSUMS",
        .validator_marker = "FIND_BIT_BENCH_ANCHOR_CHECKER_REL",
        .manifest_marker = "\"tools/lib/find_bit.zig\"",
    },
    .{
        .helper = "rbtree",
        .checker_marker = "RBTREE_REQUIRED_EXACT_CHECKSUMS",
        .validator_marker = "RBTREE_REVIEW_CHECKER_REL",
        .manifest_marker = "\"tools/lib/rbtree.zig\"",
    },
    .{
        .helper = "string",
        .checker_marker = "STRING_REQUIRED_EXACT_CHECKSUMS",
        .validator_marker = "STRING_REVIEW_CHECKER_REL",
        .manifest_marker = "\"tools/lib/string.zig\"",
    },
};

const shared_replay_families = [_]ClosureFamily{
    .{
        .helper = "hweight",
        .checker_marker = "HWEIGHT_REQUIRED_EXACT_CHECKSUMS",
        .validator_marker = "\"tools/lib/hweight.zig\"",
        .manifest_marker = "\"tools/lib/hweight.zig\"",
    },
    .{
        .helper = "list_sort",
        .checker_marker = "LIST_SORT_REQUIRED_EXACT_CHECKSUMS",
        .validator_marker = "\"tools/lib/list_sort.zig\"",
        .manifest_marker = "\"tools/lib/list_sort.zig\"",
    },
};

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(2 * 1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectBefore(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.FirstMarkerMissing;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.SecondMarkerMissing;
    try testing.expect(first_index < second_index);
}

test "bench checksum family partitions stay tied to closure validator family anchors" {
    const allocator = testing.allocator;
    const bench_checker = try readRepoFile(allocator, "scripts/zigux/check-phase1-bench.py");
    defer allocator.free(bench_checker);
    const closure_validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(closure_validator);
    const helper_manifest = try readRepoFile(allocator, "zigux/tests/fixtures/phase1_helper_manifest.json");
    defer allocator.free(helper_manifest);

    try expectContains(closure_validator, "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS");
    try expectContains(closure_validator, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS");
    try expectContains(helper_manifest, "\"direct_anchor_followup_helpers\"");
    try expectContains(helper_manifest, "\"shared_replay_parked_helpers\"");

    for (direct_anchor_families) |family| {
        try expectContains(bench_checker, family.checker_marker);
        try expectContains(closure_validator, family.validator_marker);
        try expectContains(helper_manifest, family.manifest_marker);
    }
    for (shared_replay_families) |family| {
        try expectContains(bench_checker, family.checker_marker);
        try expectContains(closure_validator, family.validator_marker);
        try expectContains(helper_manifest, family.manifest_marker);
    }
}

test "direct-anchor bench families remain separated from shared-replay bench families" {
    const allocator = testing.allocator;
    const bench_checker = try readRepoFile(allocator, "scripts/zigux/check-phase1-bench.py");
    defer allocator.free(bench_checker);
    const closure_validator = try readRepoFile(allocator, "scripts/zigux/validate-phase1-closure.py");
    defer allocator.free(closure_validator);
    const helper_manifest = try readRepoFile(allocator, "zigux/tests/fixtures/phase1_helper_manifest.json");
    defer allocator.free(helper_manifest);

    try expectBefore(closure_validator, "EXPECTED_SHARED_REPLAY_PARKED_HELPERS", "EXPECTED_DIRECT_ANCHOR_FOLLOWUP_HELPERS");
    try expectBefore(helper_manifest, "\"shared_replay_parked_helpers\"", "\"direct_anchor_followup_helpers\"");
    try expectBefore(bench_checker, "STRING_REQUIRED_EXACT_CHECKSUMS", "HWEIGHT_REQUIRED_EXACT_CHECKSUMS");
    try expectBefore(bench_checker, "LIST_SORT_REQUIRED_EXACT_CHECKSUMS", "RBTREE_REQUIRED_EXACT_CHECKSUMS");
}

test "expectations fixture preserves exact checksum families consumed by the checker" {
    const allocator = testing.allocator;
    const bench_checker = try readRepoFile(allocator, "scripts/zigux/check-phase1-bench.py");
    defer allocator.free(bench_checker);
    const expectations = try readRepoFile(allocator, "zigux/tests/fixtures/phase1_bench_expectations.json");
    defer allocator.free(expectations);

    const expected_checksum_markers = [_][]const u8{
        "\"PHASE1_BENCH_BITMAP_WEIGHT_CHECKSUM\"",
        "\"PHASE1_BENCH_BITMAP_WINDOW_CHECKSUM\"",
        "\"PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM\"",
        "\"PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM\"",
        "\"PHASE1_BENCH_STRING_CHECKSUM\"",
        "\"PHASE1_BENCH_HWEIGHT_CHECKSUM\"",
        "\"PHASE1_BENCH_LIST_SORT_CHECKSUM\"",
        "\"PHASE1_BENCH_RBTREE_CHECKSUM\"",
        "\"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM\"",
        "\"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM\"",
        "\"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM\"",
        "\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\"",
    };

    for (expected_checksum_markers) |marker| {
        try expectContains(expectations, marker);
        const checker_marker = marker[1 .. marker.len - 1];
        try expectContains(bench_checker, checker_marker);
    }
}

test "rbtree remains the only direct-anchor family with multi-checksum expansion" {
    const allocator = testing.allocator;
    const bench_checker = try readRepoFile(allocator, "scripts/zigux/check-phase1-bench.py");
    defer allocator.free(bench_checker);

    try expectContains(bench_checker, "RBTREE_REQUIRED_ITERATIONS");
    try expectContains(bench_checker, "\"PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM\"");
    try expectContains(bench_checker, "\"PHASE1_BENCH_RBTREE_FIND_ADD_CHECKSUM\"");
    try expectContains(bench_checker, "\"PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM\"");
    try expectContains(bench_checker, "\"PHASE1_BENCH_RBTREE_CACHED_CHECKSUM\"");
    try expectBefore(bench_checker, "RBTREE_REQUIRED_EXACT_CHECKSUMS", "SOURCE_MARKER_SETS");
}
