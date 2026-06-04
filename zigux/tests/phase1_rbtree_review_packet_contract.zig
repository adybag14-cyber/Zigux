const std = @import("std");

const checker_path = "scripts/zigux/check-phase1-rbtree-review-packet.py";

const required_once_markers = [_][]const u8{
    "Guard the Phase 1 rbtree review packet against helper, fixture, smoke, and lane drift.",
    "EXPECTED_SOURCE_SYMBOLS = [",
    "pub fn insertColorCached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "pub fn rb_insert_color_cached(node: *Node, root: *RootCached, leftmost: bool) void {",
    "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn rb_add_cached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
    "pub fn findAddCached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "pub fn rb_find_add_cached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
    "pub fn eraseInitCached(node: *Node, root: *RootCached) void {",
    "pub fn rb_erase_init_cached(node: *Node, root: *RootCached) void {",
    "pub fn firstCached(root: *const RootCached) ?*Node {",
    "pub fn rb_first_cached(root: *const RootCached) ?*Node {",
    "pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {",
    "pub fn rb_replace_node_cached(victim: *Node, new: *Node, root: *RootCached) void {",
    "pub fn nextMatch(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {",
    "pub fn rb_next_match(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {",
    "pub fn matchIterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {",
    "pub fn rb_match_iterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {",
    "EXPECTED_HELPER_TEST_ANCHORS = [",
    "EXPECTED_PARITY_FIXTURE_KEYS = [",
    "EXPECTED_SMOKE_MARKERS = [",
    "var cached_leftmost_return_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);",
    "var cached_root_transition_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, 0, 4, 2 }, &cached_root_transition_serials);",
    "manifest:duplicate_json_key",
    "fixture:duplicate_json_key",
    "PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias",
    "PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials",
};

const required_present_markers = [_][]const u8{
    "test \"rbtree ordered Linux-style aliases mirror traversal and replacement helpers\"",
    "test \"rbtree low-level Linux-style aliases mirror node-state helpers\"",
    "test \"rbtree findAdd keeps the first duplicate and inserts new keys\"",
    "test \"rbtree nextMatch walks the duplicate range in order\"",
    "test \"rbtree matchIterator walks the duplicate range in order\"",
    "test \"rbtree addCached returns the inserted node only when it becomes leftmost\"",
    "test \"rbtree findAddCached keeps cached leftmost stable while inserting misses\"",
    "test \"rbtree cached-root Linux-style aliases mirror the primary helpers\"",
    "test \"rbtree eraseInitCached clears singleton cached roots before reseed\"",
    "\"find_found_key\"",
    "\"find_missing\"",
    "\"find_first_serial\"",
    "\"next_match_serials\"",
    "\"match_iterator_serials\"",
    "\"next_match_terminal_null\"",
    "\"cached_leftmost_return_serials\"",
    "\"cached_root_transition_serials\"",
    "collect_duplicate_json_key_paths",
    "run_self_test()",
    "try std.testing.expect(@hasDecl(rbtree, \"find\"));",
    "try std.testing.expect(@hasDecl(rbtree, \"matchIterator\"));",
};

const required_order = [_][]const u8{
    "EXPECTED_SOURCE_SYMBOLS = [",
    "EXPECTED_HELPER_TEST_ANCHORS = [",
    "EXPECTED_LANE_LINES = [",
    "EXPECTED_PARITY_FIXTURE_KEYS = [",
    "EXPECTED_MANIFEST_PACKET = {",
    "EXPECTED_FIXTURE_VALUES = {",
    "EXPECTED_SMOKE_MARKERS = [",
    "def collect_failures(root: Path) -> list[str]:",
    "def run_self_test() -> int:",
};

fn readChecker(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(std.testing.io, checker_path, allocator, .limited(512 * 1024));
}

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

test "phase1 rbtree review checker keeps the expected packet roster" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    inline for (required_once_markers) |marker| {
        try std.testing.expectEqual(@as(usize, 1), countNeedle(checker, marker));
    }
    inline for (required_present_markers) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, checker, marker) != null);
    }
}

test "phase1 rbtree review checker keeps packet sections ordered" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    var previous_end: usize = 0;
    inline for (required_order) |marker| {
        const found = std.mem.indexOfPos(u8, checker, previous_end, marker) orelse return error.TestUnexpectedResult;
        previous_end = found + marker.len;
    }
}

test "phase1 rbtree review checker self-test guards representative drift modes" {
    const checker = try readChecker(std.testing.allocator);
    defer std.testing.allocator.free(checker);

    const drift_cases = [_][]const u8{
        "source_symbol_",
        "helper_anchor_",
        "smoke_marker_",
        "lane_marker_",
        "manifest_duplicate_review_packet_summary",
        "fixture_duplicate_cached_leftmost_return_serials",
        "manifest_missing_file",
        "fixture_missing_file",
        "smoke_missing_file",
        "lane_missing_file",
        "closure_missing_file",
        "manifest_invalid_json",
        "fixture_invalid_json",
    };
    inline for (drift_cases) |marker| {
        try std.testing.expect(std.mem.indexOf(u8, checker, marker) != null);
    }

    try std.testing.expect(std.mem.indexOf(u8, checker, "self-test:ok") != null);
    try std.testing.expect(std.mem.indexOf(u8, checker, "phase1-rbtree-review-packet:ok") != null);
}
