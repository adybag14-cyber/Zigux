const std = @import("std");

const source_path = "scripts/zigux/check-phase1-rbtree-review-packet.py";

fn readSource(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        source_path,
        allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(source: []const u8, marker: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, source, marker) != null);
}

fn expectContainsInOrder(source: []const u8, markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOf(u8, source[cursor..], marker) orelse return error.MarkerOutOfOrder;
        cursor += found + marker.len;
    }
}

test "rbtree review checker keeps required file roster and duplicate tracking" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const required_paths = [_][]const u8{
        "HELPER_REL = Path(\"tools/lib/rbtree.zig\")",
        "MANIFEST_REL = Path(\"zigux/tests/fixtures/phase1_helper_manifest.json\")",
        "FIXTURE_REL = Path(\"zigux/tests/fixtures/phase1_helpers.json\")",
        "SMOKE_REL = Path(\"zigux/tests/phase1_host_tools_smoke.zig\")",
        "LANE_NOTE_REL = Path(\"Documentation/zigux/phase1-host-helper-lane-sequencing.md\")",
        "CLOSURE_NOTE_REL = Path(\"Documentation/zigux/phase1-closure.md\")",
    };
    for (required_paths) |marker| {
        try expectContains(source, marker);
    }

    try expectContainsInOrder(source, &.{
        "class DuplicateTrackingDict(dict[str, object]):",
        "self.duplicate_keys: list[str] = []",
        "if key in self and key not in self.duplicate_keys:",
        "self.duplicate_keys.append(key)",
    });
}

test "rbtree review checker pins cached helper symbols and test anchors" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const helper_symbols = [_][]const u8{
        "pub fn insertColorCached(node: *Node, root: *RootCached, leftmost: bool) void {",
        "pub fn rb_insert_color_cached(node: *Node, root: *RootCached, leftmost: bool) void {",
        "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
        "pub fn rb_add_cached(node: *Node, root: *RootCached, less: LessFn) ?*Node {",
        "pub fn findAddCached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
        "pub fn rb_find_add_cached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {",
        "pub fn eraseCached(node: *Node, root: *RootCached) ?*Node {",
        "pub fn rb_erase_cached(node: *Node, root: *RootCached) ?*Node {",
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
    };
    for (helper_symbols) |marker| {
        try expectContains(source, marker);
    }

    const helper_test_anchors = [_][]const u8{
        "rbtree ordered Linux-style aliases mirror traversal and replacement helpers",
        "rbtree low-level Linux-style aliases mirror node-state helpers",
        "rbtree findAdd keeps the first duplicate and inserts new keys",
        "rbtree nextMatch walks the duplicate range in order",
        "rbtree matchIterator walks the duplicate range in order",
        "rbtree addCached returns the inserted node only when it becomes leftmost",
        "rbtree findAddCached keeps cached leftmost stable while inserting misses",
        "rbtree cached root keeps the leftmost pointer in sync",
        "rbtree cached-root Linux-style aliases mirror the primary helpers",
        "rbtree eraseInitCached clears singleton cached roots before reseed",
    };
    for (helper_test_anchors) |marker| {
        try expectContains(source, marker);
    }
}

test "rbtree review checker keeps manifest fixture smoke and note packets visible" {
    const source = try readSource(std.testing.allocator);
    defer std.testing.allocator.free(source);

    const packet_markers = [_][]const u8{
        "EXPECTED_LANE_PARAGRAPH",
        "EXPECTED_CLOSURE_PARAGRAPH",
        "EXPECTED_PARITY_FIXTURE_KEYS",
        "EXPECTED_DUPLICATE_SEARCH_ANCHORS",
        "EXPECTED_MANIFEST_PACKET",
        "cached_leftmost_return_serials",
        "cached_root_transition_serials",
        "ordered_alias_anchor",
        "low_level_alias_anchor",
        "cached_root_alias_anchor",
        "review_packet_summary",
        "next_safe_step_note",
        "EXPECTED_FIXTURE_VALUES",
        "EXPECTED_SMOKE_MARKERS",
    };
    for (packet_markers) |marker| {
        try expectContains(source, marker);
    }

    try expectContainsInOrder(source, &.{
        "\"empty_root\"",
        "\"insert_order\"",
        "\"reverse_order\"",
        "\"replace_order\"",
        "\"erase_init_order\"",
        "\"postorder_count\"",
        "\"find_found_key\"",
        "\"find_first_serial\"",
        "\"next_match_serials\"",
        "\"match_iterator_serials\"",
        "\"next_match_terminal_null\"",
    });
}
