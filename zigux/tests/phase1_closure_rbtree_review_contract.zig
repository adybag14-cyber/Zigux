const std = @import("std");

const RbtreeManifestAnchor = struct {
    helper_test_anchors: []const []const u8,
    parity_fixture_keys: []const []const u8,
    cached_leftmost_fixture_keys: []const []const u8,
    cached_root_transition_fixture_keys: []const []const u8,
    shared_replay_summary: []const u8,
    cached_root_transition_shared_replay_summary: []const u8,
    cached_root_direct_review_summary: []const u8,
    ordered_alias_anchor: []const u8,
    low_level_alias_anchor: []const u8,
    duplicate_search_anchors: []const []const u8,
    cached_root_followup_anchors: []const []const u8,
    cached_root_alias_anchor: []const u8,
    review_packet_summary: []const u8,
    next_safe_step_note: []const u8,
};

const ReviewAnchors = struct {
    @"tools/lib/rbtree.zig": RbtreeManifestAnchor,
};

const HelperManifest = struct {
    phase: []const u8,
    status: []const u8,
    helper_count: usize,
    helpers: []const []const u8,
    review_anchors: ReviewAnchors,
};

const RbtreeFixture = struct {
    empty_root: bool,
    insert_order: []const i32,
    reverse_order: []const i32,
    replace_order: []const i32,
    erase_init_order: []const i32,
    postorder_count: usize,
    erase_init_node_empty: bool,
    cleared_node_empty: bool,
    find_found_key: i32,
    find_missing: bool,
    find_first_serial: i32,
    next_match_serials: []const i32,
    match_iterator_serials: []const i32,
    cached_leftmost_return_serials: []const i32,
    cached_root_transition_serials: []const i32,
    next_match_terminal_null: bool,
};

const Phase1Fixture = struct {
    rbtree: RbtreeFixture,
};

const helper_test_anchors = [_][]const u8{
    "test \"rbtree ordered Linux-style aliases mirror traversal and replacement helpers\"",
    "test \"rbtree low-level Linux-style aliases mirror node-state helpers\"",
    "test \"rbtree findAdd keeps the first duplicate and inserts new keys\"",
    "test \"rbtree nextMatch walks the duplicate range in order\"",
    "test \"rbtree matchIterator walks the duplicate range in order\"",
    "test \"rbtree addCached returns the inserted node only when it becomes leftmost\"",
    "test \"rbtree findAddCached keeps cached leftmost stable while inserting misses\"",
    "test \"rbtree cached root keeps the leftmost pointer in sync\"",
    "test \"rbtree cached-root Linux-style aliases mirror the primary helpers\"",
    "test \"rbtree replaceNodeCached keeps non-leftmost leftmost unchanged\"",
    "test \"rbtree eraseCached returns null for a singleton cached tree\"",
    "test \"rbtree eraseInitCached detaches nodes while keeping cached leftmost aligned\"",
    "test \"rbtree eraseInitCached clears singleton cached roots before reseed\"",
};

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

const smoke_markers = [_][]const u8{
    "const rbtree = @import(\"rbtree\");",
    "try std.testing.expect(@hasDecl(rbtree, \"find\"));",
    "try std.testing.expect(@hasDecl(rbtree, \"matchIterator\"));",
    "const found_duplicate = rbtree.find(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;",
    "const first_duplicate = rbtree.findFirst(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;",
    "const second_duplicate = rbtree.nextMatch(&duplicate_key, first_duplicate, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;",
    "try std.testing.expect(rbtree.nextMatch(&duplicate_key, third_duplicate, RbtreeSmokeEntry.cmp) == null);",
    "var iter = rbtree.matchIterator(&duplicate_key, &tree_root, RbtreeSmokeEntry.cmp);",
    "var cached_leftmost_return_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);",
    "var cached_root_transition_serials: [4]i32 = undefined;",
    "try std.testing.expectEqualSlices(i32, &.{ 0, 0, 4, 2 }, &cached_root_transition_serials);",
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectAll(text: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try expectContains(text, marker);
    }
}

fn expectListContains(list: []const []const u8, needle: []const u8) !void {
    for (list) |item| {
        if (std.mem.eql(u8, item, needle)) return;
    }
    return error.TestUnexpectedResult;
}

fn expectSliceEqual(comptime T: type, expected: []const T, actual: []const T) !void {
    try std.testing.expectEqualSlices(T, expected, actual);
}

test "phase1 rbtree closure packet keeps docs and checker ownership aligned" {
    const closure = try readRepoFile("Documentation/zigux/phase1-closure.md", 48 * 1024);
    defer std.testing.allocator.free(closure);
    const lane_note = try readRepoFile("Documentation/zigux/phase1-host-helper-lane-sequencing.md", 64 * 1024);
    defer std.testing.allocator.free(lane_note);
    const checker = try readRepoFile("scripts/zigux/check-phase1-rbtree-review-packet.py", 64 * 1024);
    defer std.testing.allocator.free(checker);

    try expectContains(closure, "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route:");
    try expectContains(closure, "helper-local ordered Linux-style alias proof");
    try expectContains(closure, "dedicated manifest-backed `low_level_alias_anchor`");
    try expectContains(closure, "dedicated manifest-backed `cached_root_alias_anchor`");
    try expectContains(closure, "exact `cached_leftmost_return_serials` witness");
    try expectContains(closure, "Current `master` also keeps the companion `cached_root_transition_serials` witness shared instead of helper-local only:");
    try expectContains(closure, "`zigux/tests/fixtures/phase1_helpers.json` still records the exact cached-root erase, replacement, and detach transition packet");
    try expectContains(closure, "Treat that transition packet as landed shared closure evidence for future cached-root rereads");

    try expectContains(lane_note, "`PHASE1_RBTREE_DIRECT_OWNER=rbtree keeps ordered Linux-style alias, low-level Linux-style alias, cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed anchors helper-local");
    try expectContains(lane_note, "`PHASE1_RBTREE_NEXT_SAFE_STEP=rbtree reopens only to keep the already-landed cached_leftmost_return_serials shared replay aligned");
    try expectContains(lane_note, "The dedicated `low_level_alias_anchor` and `cached_root_alias_anchor` entries");

    try expectContains(checker, "Guard the Phase 1 rbtree review packet against helper, fixture, smoke, and lane drift.");
    try expectContains(checker, "EXPECTED_CLOSURE_PARAGRAPH");
    try expectContains(checker, "EXPECTED_MANIFEST_PACKET");
    try expectContains(checker, "cached_root_transition_shared_replay_summary");
    try expectContains(checker, "manifest_duplicate_review_packet_summary");
    try expectContains(checker, "fixture_duplicate_cached_leftmost_return_serials");
}

test "phase1 rbtree helper source and smoke route keep cached-root anchors visible" {
    const helper = try readRepoFile("tools/lib/rbtree.zig", 96 * 1024);
    defer std.testing.allocator.free(helper);
    const smoke = try readRepoFile("zigux/tests/phase1_host_tools_smoke.zig", 80 * 1024);
    defer std.testing.allocator.free(smoke);

    try expectAll(helper, &helper_symbols);
    try expectAll(helper, &helper_test_anchors);
    try expectAll(smoke, &smoke_markers);
}

test "phase1 rbtree manifest and fixture keep shared replay split exact" {
    const manifest_json = try readRepoFile("zigux/tests/fixtures/phase1_helper_manifest.json", 128 * 1024);
    defer std.testing.allocator.free(manifest_json);
    const manifest = try std.json.parseFromSlice(HelperManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer manifest.deinit();

    try std.testing.expectEqualStrings("Phase 1", manifest.value.phase);
    try std.testing.expectEqualStrings("closed", manifest.value.status);
    try std.testing.expectEqual(@as(usize, 13), manifest.value.helper_count);
    try expectListContains(manifest.value.helpers, "tools/lib/rbtree.zig");

    const packet = manifest.value.review_anchors.@"tools/lib/rbtree.zig";
    try expectAllList(packet.helper_test_anchors, &helper_test_anchors);
    try expectSliceEqual(u8, "test \"rbtree ordered Linux-style aliases mirror traversal and replacement helpers\"", packet.ordered_alias_anchor);
    try expectSliceEqual(u8, "test \"rbtree low-level Linux-style aliases mirror node-state helpers\"", packet.low_level_alias_anchor);
    try expectSliceEqual(u8, "test \"rbtree cached-root Linux-style aliases mirror the primary helpers\"", packet.cached_root_alias_anchor);
    try expectListContains(packet.parity_fixture_keys, "next_match_terminal_null");
    try expectListContains(packet.cached_leftmost_fixture_keys, "cached_leftmost_return_serials");
    try expectListContains(packet.cached_root_transition_fixture_keys, "cached_root_transition_serials");
    try expectContains(packet.shared_replay_summary, "exact cached-leftmost-return witnesses for rbtree");
    try expectContains(packet.cached_root_transition_shared_replay_summary, "exact `cached_root_transition_serials` cached-root erase, replacement, and detach sequence");
    try expectContains(packet.cached_root_direct_review_summary, "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors");
    try expectContains(packet.review_packet_summary, "direct helper-local anchors continue to own cached-root insert-miss");
    try expectContains(packet.next_safe_step_note, "until another committed cached-root field lands");

    const fixture_json = try readRepoFile("zigux/tests/fixtures/phase1_helpers.json", 64 * 1024);
    defer std.testing.allocator.free(fixture_json);
    const fixture = try std.json.parseFromSlice(Phase1Fixture, std.testing.allocator, fixture_json, .{
        .ignore_unknown_fields = true,
    });
    defer fixture.deinit();

    const rbtree = fixture.value.rbtree;
    try std.testing.expect(rbtree.empty_root);
    try expectSliceEqual(i32, &.{ 5, 10, 15, 20, 25 }, rbtree.insert_order);
    try expectSliceEqual(i32, &.{ 25, 20, 15, 10, 5 }, rbtree.reverse_order);
    try expectSliceEqual(i32, &.{ 5, 10, 15, 25 }, rbtree.replace_order);
    try expectSliceEqual(i32, &.{ 5, 15, 25 }, rbtree.erase_init_order);
    try std.testing.expectEqual(@as(usize, 3), rbtree.postorder_count);
    try std.testing.expect(rbtree.erase_init_node_empty);
    try std.testing.expect(rbtree.cleared_node_empty);
    try std.testing.expectEqual(@as(i32, 10), rbtree.find_found_key);
    try std.testing.expect(rbtree.find_missing);
    try std.testing.expectEqual(@as(i32, 0), rbtree.find_first_serial);
    try expectSliceEqual(i32, &.{ 0, 2, 6 }, rbtree.next_match_serials);
    try expectSliceEqual(i32, &.{ 0, 2, 6 }, rbtree.match_iterator_serials);
    try expectSliceEqual(i32, &.{ 0, -1, 2, -1 }, rbtree.cached_leftmost_return_serials);
    try expectSliceEqual(i32, &.{ 0, 0, 4, 2 }, rbtree.cached_root_transition_serials);
    try std.testing.expect(rbtree.next_match_terminal_null);
}

fn expectAllList(actual: []const []const u8, expected: []const []const u8) !void {
    for (expected) |item| {
        try expectListContains(actual, item);
    }
}
