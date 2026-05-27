const std = @import("std");

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    verified_on_utc: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    current_direct_readback_state: []const u8,
    visible_paths: []const []const u8,
    readable_non_owner_paths: []const []const u8,
    readable_makefile_markers: []const []const u8,
    public_fallback_non_owner_paths: []const []const u8,
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
        if (std.mem.eql(u8, item, needle)) try std.testing.expect(false);
    }
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase 7 rbtree survey keeps the returned json fixture, C harness, and direct helper packet truthful" {
    const allocator = std.testing.allocator;

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_rbtree_manifest.json");
    defer allocator.free(manifest_json);
    const slice_note = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-slice.md");
    defer allocator.free(slice_note);
    const direct_anchor_note = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-direct-anchor-note.md");
    defer allocator.free(direct_anchor_note);
    const checker = try readRepoFile(allocator, "scripts/zigux/check-phase7-rbtree-parity.py");
    defer allocator.free(checker);
    const helper = try readRepoFile(allocator, "lib/rbtree.zig");
    defer allocator.free(helper);
    const legacy_helper = try readRepoFile(allocator, "tools/lib/rbtree.zig");
    defer allocator.free(legacy_helper);
    const helper_companion = try readRepoFile(allocator, "zigux/tests/phase7_rbtree.zig");
    defer allocator.free(helper_companion);
    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);
    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);
    const fixture = try readRepoFile(allocator, "zigux/tests/fixtures/phase7_rbtree.json");
    defer allocator.free(fixture);
    const c_harness = try readRepoFile(allocator, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    defer allocator.free(c_harness);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P7-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.anchor);
    try std.testing.expectEqualStrings("direct_helper_slice_checker_test_note_survey_manifest_fixture_harness", manifest.current_direct_readback_state);
    try std.testing.expectEqualStrings("lib/rbtree.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.verified_on_utc.len != 0);

    try expectSliceContains(manifest.visible_paths, "zigux/tests/fixtures/phase7_rbtree.json");
    try expectSliceContains(manifest.visible_paths, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    try expectSliceContains(manifest.readable_non_owner_paths, "tools/lib/rbtree.zig");
    try expectSliceContains(manifest.readable_non_owner_paths, "zigux/tests/phase7_build.zig");
    try expectSliceContains(manifest.readable_makefile_markers, "phase7-validate:");
    try expectSliceContains(manifest.readable_makefile_markers, "phase7-rbtree-test:");
    try expectSliceContains(manifest.readable_makefile_markers, "phase7-rbtree-survey:");
    try std.testing.expectEqual(@as(usize, 0), manifest.public_fallback_non_owner_paths.len);
    try expectSliceNotContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_rbtree.json");
    try expectSliceNotContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    try expectSliceContains(manifest.absent_makefile_markers, "phase7-test:");
    try expectSliceContains(manifest.absent_workflow_markers, "Validate Phase 7 runtime helper gates");
    try expectSliceContains(manifest.ownership_focus, "fixture truthfulness must keep `zigux/tests/fixtures/phase7_rbtree.json` and `zigux/tests/fixtures/phase7_rbtree_c_harness.c` explicit as returned parity evidence");
    try expectSliceContains(manifest.ownership_focus, "fixture truthfulness now also keeps the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed boundaries explicit across the returned JSON fixture, returned C harness, dedicated survey, and dedicated replay");
    try expectContains(manifest.next_bounded_step, "including the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed cases");
    try expectContains(manifest.next_bounded_step, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    try expectContains(manifest.next_bounded_step, "phase7-rbtree-test:");
    try expectContains(manifest.next_bounded_step, "phase7-rbtree-survey:");
    try expectContains(manifest.next_bounded_step, "phase7-test:");
    try expectContains(manifest.next_bounded_step, "phase7:");

    try expectContains(slice_note, "`PHASE7_STATUS=helper_local_slice_note_test_survey_manifest_checker_fixture_harness_anchor`");
    try expectContains(slice_note, "`zigux/tests/fixtures/phase7_rbtree.json`");
    try expectContains(slice_note, "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`");
    try expectContains(slice_note, "non-leftmost cached erase, singleton cached erase, and plain erase-init reseed ownership boundaries");
    try expectContains(slice_note, "public-fallback provenance stays explicit");

    try expectContains(direct_anchor_note, "`zigux/tests/fixtures/phase7_rbtree.json`");
    try expectContains(direct_anchor_note, "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`");
    try expectContains(direct_anchor_note, "non-leftmost cached erase, singleton cached erase, and plain erase-init reseed scenarios");
    try expectContains(direct_anchor_note, "phase7-rbtree-test:");
    try expectContains(direct_anchor_note, "phase7-rbtree-survey:");
    try expectNotContains(direct_anchor_note, "still returned `404` for this dedicated companion surface");

    try expectContains(checker, "PHASE7_RBTREE_PARITY=pass");
    try expectContains(checker, "PHASE7_RBTREE_PARITY_SELF_TEST=pass");
    try expectContains(checker, "zigux/tests/fixtures/phase7_rbtree.json");
    try expectContains(checker, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");

    try expectContains(helper, "pub fn rb_find_add_cached");
    try expectContains(helper, "pub fn rb_prev");
    try expectContains(helper, "pub fn rb_next_postorder");
    try expectContains(legacy_helper, "pub fn rb_find_add_cached");
    try expectContains(helper_companion, "phase 7 rbtree companion replays ordered traversal and duplicate-range helpers");
    try expectContains(helper_companion, "phase 7 rbtree companion replays cached-leftmost promotion and erase-init ownership boundaries");
    try expectContains(helper_companion, "phase 7 rbtree companion replays non-leftmost cached erase ownership boundaries");
    try expectContains(helper_companion, "phase 7 rbtree companion replays singleton cached erase ownership until clearNode");
    try expectContains(helper_companion, "phase 7 rbtree companion replays plain erase-init ownership boundaries");
    try expectContains(helper_companion, "phase 7 rbtree companion replays reverse traversal aliases and detached null stops");
    try expectContains(build_file, "../../lib/rbtree.zig");

    try expectContains(makefile, "phase7-validate:");
    try expectContains(makefile, "phase7-rbtree-test:");
    try expectContains(makefile, "phase7-rbtree-survey:");
    try expectNotContains(workflow, "Validate Phase 7 runtime helper gates");

    try expectContains(fixture, "\"packet\": \"phase7-rbtree-parity-fixture\"");
    try expectContains(fixture, "\"current_master_state\": \"ordered-duplicate-cached-eraseinit-postorder-reverse\"");
    try expectContains(fixture, "\"ordered_duplicate_range\"");
    try expectContains(fixture, "\"cached_leftmost_promotion\"");
    try expectContains(fixture, "\"non_leftmost_cached_erase\"");
    try expectContains(fixture, "\"singleton_cached_erase\"");
    try expectContains(fixture, "\"plain_erase_init_reseed\"");
    try expectContains(fixture, "\"postorder_null_stop\"");
    try expectContains(fixture, "\"reverse_alias_detached\"");

    try expectContains(c_harness, "struct phase7_rbtree_c_harness");
    try expectContains(c_harness, "ordered-duplicate-cached-eraseinit-postorder-reverse-c-harness");
    try expectContains(c_harness, "phase7_rbtree_c_harness");
    try expectContains(c_harness, ".non_leftmost_cached_erase = {");
    try expectContains(c_harness, ".singleton_cached_erase = {");
    try expectContains(c_harness, ".plain_erase_init_reseed = {");
    try expectContains(c_harness, "reverse_alias_detached");
}
