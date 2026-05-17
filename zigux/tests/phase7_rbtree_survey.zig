const std = @import("std");

const active_lane_key = "P7-L13";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 rbtree survey keeps the helper packet aligned with repo reality" {
    const allocator = std.testing.allocator;

    const tests_readme = try readRepoFile(allocator, "zigux/tests/README.md");
    defer allocator.free(tests_readme);

    const rbtree_slice = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-slice.md");
    defer allocator.free(rbtree_slice);

    const rbtree_test = try readRepoFile(allocator, "zigux/tests/phase7_rbtree.zig");
    defer allocator.free(rbtree_test);

    const rbtree_survey = try readRepoFile(allocator, "zigux/tests/phase7_rbtree_survey.zig");
    defer allocator.free(rbtree_survey);

    const rbtree_manifest = try readRepoFile(allocator, "zigux/tests/phase7_rbtree_manifest.json");
    defer allocator.free(rbtree_manifest);

    try std.testing.expectEqualStrings("P7-L13", active_lane_key);

    try expectContains(
        tests_readme,
        "current direct-readback Phase 7 anchor: `zigux/tests/phase7_rbtree_survey.zig`",
    );
    try expectContains(
        tests_readme,
        "repo-reality warning for the broader Phase 7 rbtree packet:",
    );

    for ([_][]const u8{
        "`Documentation/zigux/phase7-rbtree-slice.md`",
        "`scripts/zigux/check-phase7-rbtree-parity.py`",
        "`zigux/tests/phase7_rbtree.zig`",
        "`zigux/tests/phase7_rbtree_manifest.json`",
        "`zigux/tests/fixtures/phase7_rbtree.json`",
        "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`",
        "`zigux/tests/phase7_build.zig`",
    }) |needle| {
        try expectContains(tests_readme, needle);
    }

    try expectContains(
        tests_readme,
        "keep the narrower current Phase 7 reminder surface tied to the directly readable `zigux/tests/phase7_rbtree_survey.zig` anchor",
    );
    try expectContains(
        tests_readme,
        "leave `string_helpers`, `cmdline`, and `argv_split` follow-through parked until a fresh same-lane reread justifies widening beyond rbtree",
    );

    try expectContains(rbtree_slice, "`PHASE7_STATUS=parked`");
    try expectContains(rbtree_slice, "`PHASE7_SLICE=rbtree-runtime-leaf`");
    try expectContains(rbtree_slice, "`PHASE7_LANE_KEY=P7-L13`");
    try expectContains(rbtree_slice, "`lib/rbtree.zig`");
    try expectContains(rbtree_slice, "`zigux/tests/phase7_rbtree.zig`");
    try expectContains(rbtree_slice, "`zigux/tests/phase7_rbtree_survey.zig`");
    try expectContains(rbtree_slice, "`zigux/tests/phase7_rbtree_manifest.json`");
    try expectContains(rbtree_slice, "`scripts/zigux/check-phase7-rbtree-parity.py`");
    try expectContains(rbtree_slice, "`zig build test --build-file zigux/tests/phase7_build.zig --summary all`");
    try expectContains(
        rbtree_slice,
        "keep rbtree-local follow-through under `P7-L13` instead of reusing the shared sequencing lane",
    );

    try expectContains(
        rbtree_test,
        "phase 7 rbtree replaceNodeCached rewires cached leftmost ownership over dirty replacement nodes",
    );
    try expectContains(
        rbtree_test,
        "phase 7 rbtree replaceNodeCached keeps non-leftmost cached ownership stable over dirty replacement nodes",
    );
    try expectContains(
        rbtree_test,
        "phase 7 rbtree cleared detached nodes stop postorder traversal",
    );
    try expectContains(
        rbtree_test,
        "phase 7 rbtree find helpers walk duplicate-key ranges",
    );

    try expectContains(
        rbtree_survey,
        "phase 7 rbtree survey keeps the helper packet aligned with repo reality",
    );

    try expectContains(rbtree_manifest, "\"lane_key\": \"P7-L13\"");
    try expectContains(rbtree_manifest, "\"current_master_state\": \"route_present_shared_packet\"");
    try expectContains(
        rbtree_manifest,
        "\"why_now\": \"The roadmap names lib/rbtree.zig directly, and the live helper already carries the bounded duplicate-range search, linked-node ownership, cached-leftmost erase and replacement, clearNode and eraseInit reset, and postorder leaf-library surface.\"",
    );
    try expectContains(
        rbtree_manifest,
        "\"why_now\": \"A dedicated Phase 7 gate keeps the shared rbtree starter surface reviewable around duplicate-key range traversal, detached-node ownership, clearNode handoff, cached-leftmost erase state, eraseInit reset, and traversal stability without widening into subsystem policy.\"",
    );
    try expectContains(
        rbtree_manifest,
        "\"why_now\": \"A machine-checked survey gate keeps the roadmap anchor, committed parity packet, manifest record, and shared ownership-review surfaces explicit without reopening rbtree behavior growth.\"",
    );
}
