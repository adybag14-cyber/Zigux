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

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) return;
    }
    try std.testing.expect(false);
}

fn expectSliceNotContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |item| {
        if (std.mem.eql(u8, item, needle)) {
            try std.testing.expect(false);
        }
    }
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 rbtree survey keeps the rematerialized direct-helper packet honest" {
    const allocator = std.testing.allocator;

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_rbtree_manifest.json");
    defer allocator.free(manifest_json);

    const direct_anchor_note = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-direct-anchor-note.md");
    defer allocator.free(direct_anchor_note);

    const helper = try readRepoFile(allocator, "tools/lib/rbtree.zig");
    defer allocator.free(helper);

    const parsed = try std.json.parseFromSlice(RbtreeManifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P7-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.anchor);
    try std.testing.expectEqualStrings("direct_helper_note_survey_manifest_only", manifest.current_direct_readback_state);
    try std.testing.expectEqualStrings("lib/rbtree.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.verified_on_utc.len != 0);

    try expectSliceContains(manifest.visible_paths, "Documentation/zigux/phase7-rbtree-direct-anchor-note.md");
    try expectSliceContains(manifest.visible_paths, "tools/lib/rbtree.zig");
    try expectSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree_survey.zig");
    try expectSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree_manifest.json");
    try expectSliceNotContains(manifest.visible_paths, "Documentation/zigux/phase7-rbtree-slice.md");
    try expectSliceNotContains(manifest.visible_paths, "lib/rbtree.zig");
    try expectSliceNotContains(manifest.visible_paths, "zigux/tests/phase7_rbtree.zig");

    try expectContains(helper, "pub const Node = struct {");
    try expectContains(helper, "pub const RootCached = struct {");
    try expectContains(helper, "pub fn clearNode");
    try expectContains(helper, "pub fn linkNode");
    try expectContains(helper, "pub fn add");
    try expectContains(helper, "pub fn findAdd");
    try expectContains(helper, "pub fn rb_find_add_cached");

    try expectSliceContains(manifest.readable_non_owner_paths, "zigux/Makefile");
    try expectSliceContains(manifest.readable_non_owner_paths, ".github/workflows/zigux-bootstrap.yml");
    try expectSliceNotContains(manifest.readable_non_owner_paths, "tools/lib/rbtree.zig");

    try expectSliceContains(manifest.missing_paths, "Documentation/zigux/phase7-rbtree-slice.md");
    try expectSliceContains(manifest.missing_paths, "lib/rbtree.zig");
    try expectSliceContains(manifest.missing_paths, "zigux/tests/phase7_rbtree.zig");
    try expectSliceContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_rbtree.json");
    try expectSliceContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    try expectSliceContains(manifest.missing_paths, "scripts/zigux/check-phase7-rbtree-parity.py");
    try expectSliceContains(manifest.missing_paths, "zigux/tests/phase7_build.zig");
    try expectSliceContains(manifest.missing_paths, "scripts/zigux/validate-phase7.py");
    try expectSliceNotContains(manifest.missing_paths, "tools/lib/rbtree.zig");

    try expectSliceContains(manifest.absent_makefile_markers, "phase7-validate:");
    try expectSliceContains(manifest.absent_makefile_markers, "phase7-rbtree-test:");
    try expectSliceContains(manifest.absent_makefile_markers, "phase7-rbtree-survey:");
    try expectSliceContains(manifest.absent_makefile_markers, "phase7-test:");
    try expectSliceContains(manifest.absent_makefile_markers, "phase7:");

    try expectSliceContains(manifest.absent_workflow_markers, "Validate Phase 7 runtime helper gates");
    try expectSliceContains(manifest.absent_workflow_markers, "Run Phase 7 runtime helper tests");
    try expectSliceContains(manifest.absent_workflow_markers, "make -C zigux phase7-validate");
    try expectSliceContains(manifest.absent_workflow_markers, "make -C zigux phase7-test");

    try expectSliceContains(manifest.ownership_focus, "the currently readable same-lane rbtree packet includes the direct helper at `tools/lib/rbtree.zig` plus the direct-anchor note, survey, and manifest, so same-lane truthfulness must keep that returned tool-root helper explicit while still not presenting the dedicated slice, dedicated test, fixture pair, parity checker, shared build file, or shared validator as returned on current master");
    try expectSliceContains(manifest.ownership_focus, "path truthfulness must keep the currently returned helper rooted at `tools/lib/rbtree.zig` explicit while the roadmap destination `lib/rbtree.zig` still remains a repo-reality gap on current master");
    try expectSliceContains(manifest.ownership_focus, "cross-helper truthfulness must keep the landed string_helpers packet explicit while keeping the cmdline, argv_split, and rbtree packets distinct instead of collapsing them into one shared reminder claim");
    try expectSliceContains(manifest.ownership_focus, "build-graph truthfulness must keep the split non-owner evidence explicit: `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` are readable, while the dedicated rbtree slice, dedicated replay, fixture pair, shared build file, and shared validator still do not directly materialize on current master");
    try expectContains(manifest.next_bounded_step, "direct-helper-plus-anchor-note");
    try expectContains(manifest.next_bounded_step, "Documentation/zigux/phase7-rbtree-slice.md");
    try expectContains(manifest.next_bounded_step, "zigux/tests/phase7_rbtree.zig");

    try expectContains(direct_anchor_note, "Current direct-readback Phase 7 rbtree helper packet partially rematerializes on current `master` through `tools/lib/rbtree.zig`");
    try expectContains(direct_anchor_note, "the directly readable same-lane truthfulness packet is limited to:");
    try expectContains(direct_anchor_note, "`Documentation/zigux/phase7-rbtree-direct-anchor-note.md`");
    try expectContains(direct_anchor_note, "`tools/lib/rbtree.zig`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_rbtree_survey.zig`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_rbtree_manifest.json`");
    try expectContains(direct_anchor_note, "Fresh authenticated GitHub reread in this slot directly returned:");
    try expectContains(direct_anchor_note, "Fresh authenticated GitHub reread in this slot still returned 404 for these dedicated companion or roadmap-path surfaces:");
    try expectContains(direct_anchor_note, "`Documentation/zigux/phase7-rbtree-slice.md`");
    try expectContains(direct_anchor_note, "`lib/rbtree.zig`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_rbtree.zig`");
    try expectContains(direct_anchor_note, "`zigux/tests/fixtures/phase7_rbtree.json`");
    try expectContains(direct_anchor_note, "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`");
    try expectContains(direct_anchor_note, "`scripts/zigux/check-phase7-rbtree-parity.py`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_build.zig`");
    try expectContains(direct_anchor_note, "`scripts/zigux/validate-phase7.py`");
    try expectContains(direct_anchor_note, "`zigux/Makefile` still lacks dedicated `phase7-*` wrapper markers");
    try expectContains(direct_anchor_note, "`.github/workflows/zigux-bootstrap.yml` still lacks dedicated Phase 7 runtime-helper steps");
    try expectContains(direct_anchor_note, "Keep the current Phase 7 rbtree reminder surface tied to the returned tool-root helper plus the still-missing dedicated companion packet rather than claiming a fully returned helper-local review packet.");
    try expectContains(direct_anchor_note, "`string_helpers` remains the Phase 7 fully landed sibling packet");
    try expectContains(direct_anchor_note, "`cmdline` and `argv_split` keep their own helper-local packet ownership");
    try expectContains(direct_anchor_note, "Do not widen this note into make-wrapper or workflow-recovery claims until a fresh same-lane reread proves one concrete dedicated rbtree companion surface such as `Documentation/zigux/phase7-rbtree-slice.md` or `zigux/tests/phase7_rbtree.zig` has rematerialized on current `master`.");
    try expectNotContains(direct_anchor_note, "does not publicly materialize on current `master`");
    try expectNotContains(direct_anchor_note, "missing-helper truthfulness rather than a returned-packet claim");
}
