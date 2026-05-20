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

    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-slice.md");
    defer allocator.free(slice_note);

    const direct_anchor_note = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-direct-anchor-note.md");
    defer allocator.free(direct_anchor_note);

    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-rbtree-parity.py");
    defer allocator.free(checker);

    const helper = try readRepoFile(allocator, "tools/lib/rbtree.zig");
    defer allocator.free(helper);

    const helper_companion = try readRepoFile(allocator, "zigux/tests/phase7_rbtree.zig");
    defer allocator.free(helper_companion);

    const parsed = try std.json.parseFromSlice(RbtreeManifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P7-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.anchor);
    try std.testing.expectEqualStrings("direct_helper_slice_checker_test_note_survey_manifest", manifest.current_direct_readback_state);
    try std.testing.expectEqualStrings("lib/rbtree.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.verified_on_utc.len != 0);

    try expectContains(checker, "PHASE7_RBTREE_PARITY=pass");
    try expectContains(checker, "PHASE7_RBTREE_PARITY_REQUIRED_FILE_COUNT=");
    try expectContains(checker, "PHASE7_RBTREE_PARITY_SELF_TEST=pass");
    try expectContains(checker, "\\\"Documentation/zigux/phase7-rbtree-slice.md\\\",");
    try expectContains(checker, "\\\"tools/lib/rbtree.zig\\\",");
    try expectContains(checker, "\\\"zigux/tests/phase7_rbtree.zig\\\",");
    try expectContains(checker, "\\\"zigux/tests/phase7_rbtree_survey.zig\\\",");
    try expectContains(checker, "\\\"zigux/tests/phase7_rbtree_manifest.json\\\",");

    try expectContains(slice_note, "`PHASE7_STATUS=helper_local_slice_note_test_survey_manifest_checker_anchor`");
    try expectContains(slice_note, "`PHASE7_LANE_KEY=P7-L13`");
    try expectContains(slice_note, "`tools/lib/rbtree.zig`");
    try expectContains(slice_note, "`Documentation/zigux/phase7-rbtree-direct-anchor-note.md`");
    try expectContains(slice_note, "`scripts/zigux/check-phase7-rbtree-parity.py`");
    try expectContains(slice_note, "`lib/rbtree.zig`");
    try expectContains(slice_note, "`zigux/tests/fixtures/phase7_rbtree.json`");
    try expectContains(slice_note, "same-lane truthfulness keeps the returned slice note, direct-anchor note, parity checker, replay, survey, and manifest explicit");
    try expectContains(slice_note, "Keep `scripts/zigux/validate-phase7.py` explicit as directly readable shared-validator evidence rather than helper-local ownership.");

    try expectSliceContains(manifest.visible_paths, "Documentation/zigux/phase7-rbtree-slice.md");
    try expectSliceContains(manifest.visible_paths, "Documentation/zigux/phase7-rbtree-direct-anchor-note.md");
    try expectSliceContains(manifest.visible_paths, "scripts/zigux/check-phase7-rbtree-parity.py");
    try expectSliceContains(manifest.visible_paths, "tools/lib/rbtree.zig");
    try expectSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree.zig");
    try expectSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree_survey.zig");
    try expectSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree_manifest.json");

    try expectContains(helper, "pub const Node = struct {");
    try expectContains(helper, "pub const RootCached = struct {");
    try expectContains(helper, "pub fn clearNode");
    try expectContains(helper, "pub fn linkNode");
    try expectContains(helper, "pub fn add");
    try expectContains(helper, "pub fn findAdd");
    try expectContains(helper, "pub fn rb_find_add_cached");

    try expectContains(helper_companion, "const rbtree = @import(\"../../tools/lib/rbtree.zig\");");
    try expectContains(helper_companion, "phase 7 rbtree companion replays ordered traversal and duplicate-range helpers");
    try expectContains(helper_companion, "phase 7 rbtree companion replays cached-leftmost promotion and erase-init ownership boundaries");
    try expectContains(helper_companion, "rbtree.matchIterator");
    try expectContains(helper_companion, "rbtree.eraseInitCached");
    try expectContains(helper_companion, "rbtree.rb_erase_init_cached");

    try expectSliceContains(manifest.readable_non_owner_paths, "scripts/zigux/validate-phase7.py");
    try expectSliceContains(manifest.readable_non_owner_paths, "zigux/Makefile");
    try expectSliceContains(manifest.readable_non_owner_paths, ".github/workflows/zigux-bootstrap.yml");

    try expectSliceNotContains(manifest.missing_paths, "Documentation/zigux/phase7-rbtree-slice.md");
    try expectSliceContains(manifest.missing_paths, "lib/rbtree.zig");
    try expectSliceContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_rbtree.json");
    try expectSliceContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    try expectSliceContains(manifest.missing_paths, "zigux/tests/phase7_build.zig");
    try expectSliceNotContains(manifest.missing_paths, "scripts/zigux/validate-phase7.py");
    try expectSliceNotContains(manifest.missing_paths, "scripts/zigux/check-phase7-rbtree-parity.py");
    try expectSliceNotContains(manifest.missing_paths, "zigux/tests/phase7_rbtree.zig");

    try expectSliceContains(manifest.absent_makefile_markers, "phase7-validate:");
    try expectSliceContains(manifest.absent_makefile_markers, "phase7-rbtree-test:");
    try expectSliceContains(manifest.absent_makefile_markers, "phase7-rbtree-survey:");
    try expectSliceContains(manifest.absent_makefile_markers, "phase7-test:");
    try expectSliceContains(manifest.absent_makefile_markers, "phase7:");

    try expectSliceContains(manifest.absent_workflow_markers, "Validate Phase 7 runtime helper gates");
    try expectSliceContains(manifest.absent_workflow_markers, "Run Phase 7 runtime helper tests");
    try expectSliceContains(manifest.absent_workflow_markers, "make -C zigux phase7-validate");
    try expectSliceContains(manifest.absent_workflow_markers, "make -C zigux phase7-test");

    try expectSliceContains(manifest.ownership_focus, "the currently readable same-lane rbtree packet now includes the direct helper at `tools/lib/rbtree.zig`, the dedicated slice note at `Documentation/zigux/phase7-rbtree-slice.md`, the direct-anchor note, the dedicated parity checker at `scripts/zigux/check-phase7-rbtree-parity.py`, the dedicated replay at `zigux/tests/phase7_rbtree.zig`, and the returned survey and manifest, so same-lane truthfulness must keep those returned surfaces explicit while still not presenting the roadmap-path port, fixture pair, or shared build file as returned on current master");
    try expectSliceContains(manifest.ownership_focus, "path truthfulness must keep the currently returned helper rooted at `tools/lib/rbtree.zig` explicit while the roadmap destination `lib/rbtree.zig` still remains a repo-reality gap on current master");
    try expectSliceContains(manifest.ownership_focus, "cross-helper truthfulness must keep the landed string_helpers packet explicit while keeping the cmdline, argv_split, and rbtree packets distinct instead of collapsing them into one shared reminder claim");
    try expectSliceContains(manifest.ownership_focus, "build-graph truthfulness must keep the split non-owner evidence explicit: `scripts/zigux/validate-phase7.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` are readable, while the roadmap-path port, fixture pair, and shared build file still do not directly materialize on current master");
    try expectContains(manifest.next_bounded_step, "slice-backed direct-helper packet");
    try expectContains(manifest.next_bounded_step, "`lib/rbtree.zig`");
    try expectContains(manifest.next_bounded_step, "`zigux/tests/fixtures/phase7_rbtree.json`");
    try expectContains(manifest.next_bounded_step, "`zigux/tests/phase7_build.zig`");
    try expectNotContains(manifest.next_bounded_step, "`scripts/zigux/validate-phase7.py`");

    try expectContains(direct_anchor_note, "Current direct-readback Phase 7 rbtree helper packet now rematerializes a dedicated helper-local slice note and parity checker on current `master`");
    try expectContains(direct_anchor_note, "`Documentation/zigux/phase7-rbtree-slice.md`");
    try expectContains(direct_anchor_note, "`scripts/zigux/check-phase7-rbtree-parity.py`");
    try expectContains(direct_anchor_note, "Fresh authenticated GitHub reread in this slot directly returned:");
    try expectContains(direct_anchor_note, "Fresh authenticated GitHub reread in this slot also directly returned this shared non-owner surface:");
    try expectContains(direct_anchor_note, "`scripts/zigux/validate-phase7.py`");
    try expectContains(direct_anchor_note, "Fresh authenticated GitHub reread in this slot still returned 404 for these dedicated companion or roadmap-path surfaces:");
    try expectNotContains(direct_anchor_note, "- `Documentation/zigux/phase7-rbtree-slice.md`\n- `lib/rbtree.zig`");
    try expectContains(direct_anchor_note, "`lib/rbtree.zig`");
    try expectContains(direct_anchor_note, "`zigux/tests/fixtures/phase7_rbtree.json`");
    try expectContains(direct_anchor_note, "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_build.zig`");
    try expectContains(direct_anchor_note, "`zigux/Makefile` still lacks dedicated `phase7-*` wrapper markers");
    try expectContains(direct_anchor_note, "Keep the current Phase 7 rbtree reminder surface tied to the returned tool-root helper, the dedicated slice note, the dedicated replay companion, the returned survey and manifest, the parity checker, and the directly readable shared validator evidence");
    try expectContains(direct_anchor_note, "`string_helpers` remains the Phase 7 fully landed sibling packet");
    try expectContains(direct_anchor_note, "`cmdline` and `argv_split` keep their own helper-local packet ownership");
    try expectContains(direct_anchor_note, "Do not widen this note into make-wrapper or workflow-recovery claims until a fresh same-lane reread proves one more concrete rbtree companion surface");
}
