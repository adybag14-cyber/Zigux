const std = @import("std");

const RbtreeManifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    verified_on_utc: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    current_direct_readback_state: []const u8,
    visible_paths: []const []const u8,
    readable_non_owner_paths: []const []const u8,
    missing_paths: []const []const u8,
    absent_makefile_markers: []const []const u8,
    absent_workflow_markers: []const []const u8,
    ownership_focus: []const []const u8,
    next_bounded_step: []const u8,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectStringSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) return;
    }
    try std.testing.expect(false);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 rbtree survey keeps the restored packet truthful to current readback" {
    const allocator = std.testing.allocator;

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_rbtree_manifest.json");
    defer allocator.free(manifest_json);

    const direct_anchor_note = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-direct-anchor-note.md");
    defer allocator.free(direct_anchor_note);

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-slice.md");
    defer allocator.free(slice_note);

    const parsed = try std.json.parseFromSlice(RbtreeManifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P7-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.anchor);
    try std.testing.expectEqualStrings(
        "public_fallback_packet_with_shared_build_and_validator",
        manifest.current_direct_readback_state,
    );
    try std.testing.expectEqualStrings("lib/rbtree.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.verified_on_utc.len != 0);
    try std.testing.expectEqual(@as(usize, 0), manifest.missing_paths.len);

    try expectStringSliceContains(manifest.visible_paths, "Documentation/zigux/phase7-rbtree-slice.md");
    try expectStringSliceContains(manifest.visible_paths, "lib/rbtree.zig");
    try expectStringSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree.zig");
    try expectStringSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree_survey.zig");
    try expectStringSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree_manifest.json");
    try expectStringSliceContains(manifest.visible_paths, "zigux/tests/fixtures/phase7_rbtree.json");
    try expectStringSliceContains(manifest.visible_paths, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    try expectStringSliceContains(manifest.visible_paths, "scripts/zigux/check-phase7-rbtree-parity.py");
    try expectStringSliceContains(manifest.visible_paths, "zigux/tests/phase7_build.zig");
    try expectStringSliceContains(manifest.visible_paths, "scripts/zigux/validate-phase7.py");

    try expectStringSliceContains(manifest.readable_non_owner_paths, "zigux/Makefile");
    try expectStringSliceContains(manifest.readable_non_owner_paths, ".github/workflows/zigux-bootstrap.yml");

    try expectStringSliceContains(manifest.absent_makefile_markers, "phase7-validate:");
    try expectStringSliceContains(manifest.absent_makefile_markers, "phase7-rbtree-test:");
    try expectStringSliceContains(manifest.absent_makefile_markers, "phase7-rbtree-survey:");
    try expectStringSliceContains(manifest.absent_makefile_markers, "phase7-test:");
    try expectStringSliceContains(manifest.absent_makefile_markers, "phase7:");

    try expectStringSliceContains(manifest.absent_workflow_markers, "Validate Phase 7 runtime helper gates");
    try expectStringSliceContains(manifest.absent_workflow_markers, "Run Phase 7 runtime helper tests");
    try expectStringSliceContains(manifest.absent_workflow_markers, "make -C zigux phase7-validate");
    try expectStringSliceContains(manifest.absent_workflow_markers, "make -C zigux phase7-test");

    try expectStringSliceContains(manifest.ownership_focus, "the current public-fallback-visible rbtree packet now includes the slice note, helper, dedicated test, survey, manifest, fixture pair, parity checker, shared build file, and shared validator, so same-lane truthfulness must stop presenting those returned surfaces as missing on current master");
    try expectStringSliceContains(manifest.ownership_focus, "same-lane follow-through can now use the restored helper-local rbtree packet or the returned shared build-and-validator evidence, but it still must not claim that the Phase 7 make-wrapper routes or workflow steps have returned on current master");
    try expectStringSliceContains(manifest.ownership_focus, "cross-helper truthfulness must keep the landed string_helpers packet explicit while keeping the cmdline, argv_split, and rbtree packets distinct instead of collapsing them into one shared reminder claim");
    try expectStringSliceContains(manifest.ownership_focus, "build-graph truthfulness must keep the split non-owner evidence explicit: `zigux/tests/phase7_build.zig` and `scripts/zigux/validate-phase7.py` are directly readable again, while `zigux/Makefile` still lacks dedicated `phase7-*` wrapper routes and `.github/workflows/zigux-bootstrap.yml` still lacks dedicated Phase 7 runtime-helper steps");
    try expectContains(manifest.next_bounded_step, "restored rbtree helper-test-fixture-checker-build-validator packet");

    try expectContains(slice_note, "`PHASE7_LANE_KEY=P7-L13`");
    try expectContains(slice_note, "keep this helper slice parked unless a fresh ownership, parity, or review-surface gap appears inside the existing helper, shared-test, survey, manifest, parity-checker, or shared review packet");
    try expectContains(slice_note, "the broader shared `phase7_build.zig` route is also back to a directly readable shared reminder instead of the older missing-sibling blocker wording");
    try expectContains(slice_note, "`python3 scripts/zigux/check-phase7-rbtree-parity.py` remains the dedicated parity readback route");
    try expectContains(slice_note, "this slice does not carry an open parity-fixture follow-up");
    try expectNotContains(slice_note, "Repo-reality warning for the still-missing Phase 7 rbtree companions:");

    try expectContains(direct_anchor_note, "Current direct-readback Phase 7 rbtree packet is publicly visible again through:");
    try expectContains(direct_anchor_note, "`Documentation/zigux/phase7-rbtree-slice.md`");
    try expectContains(direct_anchor_note, "`lib/rbtree.zig`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_rbtree.zig`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_rbtree_survey.zig`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_rbtree_manifest.json`");
    try expectContains(direct_anchor_note, "`zigux/tests/fixtures/phase7_rbtree.json`");
    try expectContains(direct_anchor_note, "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`");
    try expectContains(direct_anchor_note, "`scripts/zigux/check-phase7-rbtree-parity.py`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_build.zig`");
    try expectContains(direct_anchor_note, "`scripts/zigux/validate-phase7.py`");
    try expectContains(direct_anchor_note, "Fresh public GitHub fallback reread in this slot confirmed the slice note, helper, dedicated test, survey, manifest, fixture pair, parity checker, shared build file, and shared validator are visible again on current `master`.");
    try expectContains(direct_anchor_note, "Repo-reality warning for the still-missing Phase 7 shared wrapper routes:");
    try expectContains(direct_anchor_note, "`zigux/Makefile` still lacks dedicated `phase7-*` wrapper markers");
    try expectContains(direct_anchor_note, "`.github/workflows/zigux-bootstrap.yml` still lacks dedicated Phase 7 runtime-helper steps");
    try expectContains(direct_anchor_note, "`string_helpers` remains the Phase 7 fully checker-backed sibling packet");
    try expectContains(direct_anchor_note, "`cmdline` and `argv_split` keep their own helper-local packet ownership");
    try expectContains(direct_anchor_note, "Do not widen this note into make-wrapper or workflow-recovery claims until a fresh same-lane reread proves those shared non-owner routes returned on current `master`.");

    try expectNotContains(direct_anchor_note, "Repo-reality warning for the still-missing Phase 7 rbtree companions:");
    try expectNotContains(manifest_json, "\"missing_paths\": [\n    \"zigux/tests/fixtures/phase7_rbtree.json\"");
}
