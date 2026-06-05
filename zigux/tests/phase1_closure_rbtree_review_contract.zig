const std = @import("std");

const closure_path = "Documentation/zigux/phase1-closure.md";
const manifest_path = "zigux/tests/fixtures/phase1_helper_manifest.json";
const helper_path = "tools/lib/rbtree.zig";
const smoke_path = "zigux/tests/phase1_host_tools_smoke.zig";

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(2 * 1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectInOrder(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.TestExpectedEqual;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.TestExpectedEqual;
    try std.testing.expect(first_index < second_index);
}

test "phase1 rbtree closure note keeps helper-local review ownership explicit" {
    const allocator = std.testing.allocator;
    const closure = try readRepoFile(allocator, closure_path);
    defer allocator.free(closure);

    try expectContains(closure, "`PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py exact-checks helper-local rbtree anchors plus the committed duplicate-search and cached-leftmost replay packet across the helper, closure note, lane note, manifest, fixture, and shared smoke route`");
    try expectContains(closure, "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route");
    try expectContains(closure, "keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof");
    try expectContains(closure, "dedicated manifest-backed `low_level_alias_anchor`");
    try expectContains(closure, "dedicated manifest-backed `cached_root_alias_anchor`");
    try expectContains(closure, "cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors");
    try expectContains(closure, "exact `cached_leftmost_return_serials` witness");
    try expectContains(closure, "companion `cached_root_transition_serials` witness shared instead of helper-local only");
    try expectContains(closure, "same `[0, 0, 4, 2]` sequence");

    try expectInOrder(
        closure,
        "`PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
        "`PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
    );
    try expectInOrder(
        closure,
        "A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route",
        "A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route",
    );
    try expectNotContains(closure, "`PHASE1_RBTREE_REVIEW_GUARD=drifted");
}

test "phase1 rbtree manifest keeps direct anchors and shared replay fields aligned" {
    const allocator = std.testing.allocator;
    const manifest = try readRepoFile(allocator, manifest_path);
    defer allocator.free(manifest);

    try expectContains(manifest, "\"tools/lib/rbtree.zig\"");
    try expectContains(manifest, "\"phase1_helper_replay_anchor\": \"test \\\"phase1 host-tools smoke exercises live helper behavior\\\"\"");
    try expectContains(manifest, "\"shared_replay_summary\": \"the committed Phase 1 fixture still carries traversal, detached-node, duplicate-search, and exact cached-leftmost-return witnesses for rbtree");
    try expectContains(manifest, "\"cached_root_transition_shared_replay_summary\": \"the committed Phase 1 fixture and the shared host-tools smoke route also keep the exact `cached_root_transition_serials` cached-root erase, replacement, and detach sequence aligned on current master\"");
    try expectContains(manifest, "\"cached_root_direct_review_summary\": \"cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior remain owned by direct helper-local anchors");
    try expectContains(manifest, "\"ordered_alias_anchor\": \"test \\\"rbtree ordered Linux-style aliases mirror traversal and replacement helpers\\\"\"");
    try expectContains(manifest, "\"low_level_alias_anchor\": \"test \\\"rbtree low-level Linux-style aliases mirror node-state helpers\\\"\"");
    try expectContains(manifest, "\"cached_root_alias_anchor\": \"test \\\"rbtree cached-root Linux-style aliases mirror the primary helpers\\\"\"");
    try expectContains(manifest, "\"cached_leftmost_fixture_keys\"");
    try expectContains(manifest, "\"cached_leftmost_return_serials\"");
    try expectContains(manifest, "\"cached_root_transition_fixture_keys\"");
    try expectContains(manifest, "\"cached_root_transition_serials\"");
    try expectContains(manifest, "\"duplicate_search_replay_keys\"");
    try expectContains(manifest, "\"find_found_key\"");
    try expectContains(manifest, "\"next_match_serials\"");
    try expectContains(manifest, "\"match_iterator_serials\"");
    try expectContains(manifest, "\"next_match_terminal_null\"");
    try expectContains(manifest, "\"the ordered Linux-style alias proof, dedicated `low_level_alias_anchor`, and the remaining cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, and reseed behavior stay owned by direct helper-local anchors until another committed cached-root field lands.\"");

    try expectInOrder(
        manifest,
        "\"cached_leftmost_fixture_keys\"",
        "\"cached_root_transition_fixture_keys\"",
    );
    try expectInOrder(
        manifest,
        "\"duplicate_search_replay_keys\"",
        "\"cached_root_followup_anchors\"",
    );
}

test "phase1 rbtree helper and shared smoke route keep closure witnesses live" {
    const allocator = std.testing.allocator;
    const helper = try readRepoFile(allocator, helper_path);
    defer allocator.free(helper);
    const smoke = try readRepoFile(allocator, smoke_path);
    defer allocator.free(smoke);

    const helper_anchors = [_][]const u8{
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
    for (helper_anchors) |anchor| {
        try expectContains(helper, anchor);
    }

    try expectContains(smoke, "test \"phase1 host-tools smoke exercises live helper behavior\"");
    try expectContains(smoke, "var cached_leftmost_return_serials: [4]i32 = undefined;");
    try expectContains(smoke, "try std.testing.expectEqualSlices(i32, &.{ 0, -1, 2, -1 }, &cached_leftmost_return_serials);");
    try expectContains(smoke, "var cached_root_transition_serials: [4]i32 = undefined;");
    try expectContains(smoke, "try std.testing.expectEqualSlices(i32, &.{ 0, 0, 4, 2 }, &cached_root_transition_serials);");
    try expectContains(smoke, "try std.testing.expect(rbtree.emptyNode(&cached_replacement.node));");
    try expectInOrder(smoke, "cached_leftmost_return_serials[0]", "cached_root_transition_serials[0]");
}
