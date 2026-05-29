const std = @import("std");

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

test "phase 1 closure keeps rbtree direct review parked and helper-local" {
    const closure = try readRepoFile("Documentation/zigux/phase1-closure.md", 96 * 1024);
    defer std.testing.allocator.free(closure);

    try expectContains(closure, "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route");
    try expectContains(closure, "keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof");
    try expectContains(closure, "the dedicated manifest-backed `low_level_alias_anchor`");
    try expectContains(closure, "the dedicated manifest-backed `cached_root_alias_anchor`");
    try expectContains(closure, "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors");
    try expectContains(closure, "the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness");
    try expectContains(closure, "do not batch a second cached-root widening into the same reopen step");
}

test "phase 1 closure keeps rbtree shared transition evidence distinct" {
    const closure = try readRepoFile("Documentation/zigux/phase1-closure.md", 96 * 1024);
    defer std.testing.allocator.free(closure);

    try expectContains(closure, "Current `master` also keeps the companion `cached_root_transition_serials` witness shared instead of helper-local only");
    try expectContains(closure, "`zigux/tests/fixtures/phase1_helpers.json` still records the exact cached-root erase, replacement, and detach transition packet");
    try expectContains(closure, "`zigux/tests/phase1_host_tools_smoke.zig` already rechecks the same `[0, 0, 4, 2]` sequence");
    try expectContains(closure, "Treat that transition packet as landed shared closure evidence for future cached-root rereads");
    try expectContains(closure, "still leaving the remaining insert-miss, leftmost-sync, alias, singleton-erase, replacement, detach, and reseed anchors helper-local");
}

test "phase 1 manifest keeps the rbtree direct anchors named" {
    const manifest = try readRepoFile("zigux/tests/fixtures/phase1_helper_manifest.json", 160 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectContains(manifest, "\"tools/lib/rbtree.zig\"");
    try expectContains(manifest, "test \\\"rbtree ordered Linux-style aliases mirror traversal and replacement helpers\\\"");
    try expectContains(manifest, "test \\\"rbtree low-level Linux-style aliases mirror node-state helpers\\\"");
    try expectContains(manifest, "test \\\"rbtree addCached returns the inserted node only when it becomes leftmost\\\"");
    try expectContains(manifest, "test \\\"rbtree cached-root Linux-style aliases mirror the primary helpers\\\"");
    try expectContains(manifest, "test \\\"rbtree eraseInitCached clears singleton cached roots before reseed\\\"");
    try expectContains(manifest, "\"low_level_alias_anchor\"");
    try expectContains(manifest, "\"cached_root_alias_anchor\"");
    try expectContains(manifest, "\"duplicate_search_anchors\"");
    try expectContains(manifest, "\"cached_root_followup_anchors\"");
    try expectContains(manifest, "\"cached_root_direct_review_summary\"");
}

test "phase 1 fixture and smoke route keep rbtree shared witnesses visible" {
    const fixture = try readRepoFile("zigux/tests/fixtures/phase1_helpers.json", 96 * 1024);
    defer std.testing.allocator.free(fixture);
    const smoke = try readRepoFile("zigux/tests/phase1_host_tools_smoke.zig", 96 * 1024);
    defer std.testing.allocator.free(smoke);

    try expectContains(fixture, "\"find_first_serial\":0");
    try expectContains(fixture, "\"next_match_serials\":[0,2,4]");
    try expectContains(fixture, "\"match_iterator_serials\":[0,2,4]");
    try expectContains(fixture, "\"cached_leftmost_return_serials\":[0,-1,2,-1]");
    try expectContains(fixture, "\"cached_root_transition_serials\":[0,0,4,2]");

    try expectContains(smoke, "const rbtree = @import(\"rbtree\");");
    try expectContains(smoke, "try std.testing.expect(@hasDecl(rbtree, \"matchIterator\"));");
    try expectContains(smoke, "const second_duplicate = rbtree.nextMatch(&duplicate_key, first_duplicate, RbtreeSmokeEntry.cmp) orelse return error.TestUnexpectedResult;");
    try expectContains(smoke, "var cached_leftmost_return_serials: [4]i32 = undefined;");
    try expectContains(smoke, "try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);");
    try expectContains(smoke, "var cached_root_transition_serials: [4]i32 = undefined;");
    try expectContains(smoke, "try std.testing.expectEqualSlices(i32, &.{ 0, 0, 4, 2 }, &cached_root_transition_serials);");
}

test "tools lib rbtree keeps the direct review anchors executable" {
    const helper = try readRepoFile("tools/lib/rbtree.zig", 192 * 1024);
    defer std.testing.allocator.free(helper);

    try expectContains(helper, "pub fn insertColorCached(node: *Node, root: *RootCached, leftmost: bool) void {");
    try expectContains(helper, "pub fn rb_insert_color_cached(node: *Node, root: *RootCached, leftmost: bool) void {");
    try expectContains(helper, "pub fn addCached(node: *Node, root: *RootCached, less: LessFn) ?*Node {");
    try expectContains(helper, "pub fn rb_add_cached(node: *Node, root: *RootCached, less: LessFn) ?*Node {");
    try expectContains(helper, "pub fn findAddCached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {");
    try expectContains(helper, "pub fn rb_find_add_cached(node: *Node, root: *RootCached, cmp: CmpNodeFn) ?*Node {");
    try expectContains(helper, "pub fn replaceNodeCached(victim: *Node, new: *Node, root: *RootCached) void {");
    try expectContains(helper, "pub fn rb_replace_node_cached(victim: *Node, new: *Node, root: *RootCached) void {");
    try expectContains(helper, "pub fn nextMatch(key: *const anyopaque, node: *const Node, cmp: CmpKeyFn) ?*Node {");
    try expectContains(helper, "pub fn matchIterator(key: *const anyopaque, root: *const Root, cmp: CmpKeyFn) MatchIterator {");
}

test "rbtree direct review contract rejects stale narrow cached-root wording" {
    const manifest = try readRepoFile("zigux/tests/fixtures/phase1_helper_manifest.json", 160 * 1024);
    defer std.testing.allocator.free(manifest);

    try expectNotContains(manifest, "cached-root leftmost-return, insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors until master ships a dedicated cached-root leftmost-return fixture key");
    try expectNotContains(manifest, "\"cached_leftmost_return_serials\" witness now stays helper-local only");
}
