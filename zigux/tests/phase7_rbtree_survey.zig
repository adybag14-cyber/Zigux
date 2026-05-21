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
    public_fallback_non_owner_paths: []const []const u8,
    missing_paths: []const []const u8,
    absent_makefile_markers: []const []const u8,
    absent_workflow_markers: []const []const u8,
    ownership_focus: []const []const u8,
    next_bounded_step: []const u8,
};

const direct_anchor_fallback_provenance_marker =
    "Machine-readable fallback provenance stays explicit through " ++
    "`public_fallback_non_owner_paths` in `zigux/tests/phase7_rbtree_manifest.json`, " ++
    "which currently names only `zigux/tests/phase7_build.zig` because the other listed " ++
    "shared or roadmap-aligned non-owner surfaces still rematerialized through authenticated " ++
    "rereads in this slot.";

const ownership_focus_fallback_marker =
    "machine-readable fallback provenance must stay explicit too: " ++
    "`public_fallback_non_owner_paths` currently names only `zigux/tests/phase7_build.zig`, " ++
    "because that shared non-owner surface needed public fallback in this runtime while the " ++
    "other listed shared or roadmap-aligned non-owner surfaces still rematerialized through " ++
    "authenticated rereads";

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

test "phase 7 rbtree survey keeps roadmap-path readback truthful without claiming helper-local ownership" {
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
    const roadmap_helper = try readRepoFile(allocator, "lib/rbtree.zig");
    defer allocator.free(roadmap_helper);
    const helper_companion = try readRepoFile(allocator, "zigux/tests/phase7_rbtree.zig");
    defer allocator.free(helper_companion);
    const build_file = try readRepoFile(allocator, "zigux/tests/phase7_build.zig");
    defer allocator.free(build_file);
    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);
    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P7-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.anchor);
    try std.testing.expectEqualStrings("direct_helper_slice_checker_test_note_survey_manifest", manifest.current_direct_readback_state);
    try std.testing.expectEqualStrings("lib/rbtree.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.verified_on_utc.len != 0);

    try expectContains(checker, "PHASE7_RBTREE_PARITY=pass");
    try expectContains(checker, "PHASE7_RBTREE_PARITY_SELF_TEST=pass");
    try expectContains(checker, "\"lib/rbtree.zig\",");

    try expectContains(slice_note, "The helper-local implementation remains rooted at `tools/lib/rbtree.zig`, while the roadmap destination `lib/rbtree.zig` now rematerializes as readable runtime-family companion evidence rather than proof that helper-local ownership has moved off the tool-root packet.");
    try expectContains(slice_note, "public-fallback provenance");

    try expectContains(direct_anchor_note, "Fresh current-master reread in this slot also confirmed these shared or roadmap-aligned non-owner surfaces:");
    try expectContains(direct_anchor_note, "- `lib/rbtree.zig`");
    try expectContains(direct_anchor_note, direct_anchor_fallback_provenance_marker);
    try expectContains(direct_anchor_note, "Fresh authenticated GitHub reread in this slot still returned `404` for these dedicated companion surfaces:");

    try expectContains(helper, "pub fn rb_find_add_cached");
    try expectContains(roadmap_helper, "pub fn rb_find_add_cached");
    try expectContains(helper_companion, "../../tools/lib/rbtree.zig");
    try expectContains(build_file, "../../lib/rbtree.zig");

    try expectContains(makefile, "phase7-validate:");
    try expectNotContains(makefile, "phase7-rbtree-test:");
    try expectNotContains(workflow, "Validate Phase 7 runtime helper gates");
    try expectNotContains(workflow, "Run Phase 7 runtime helper tests");

    try expectSliceContains(manifest.visible_paths, "tools/lib/rbtree.zig");
    try expectSliceContains(manifest.readable_non_owner_paths, "lib/rbtree.zig");
    try expectSliceContains(manifest.readable_non_owner_paths, "zigux/tests/phase7_build.zig");
    try expectSliceContains(manifest.public_fallback_non_owner_paths, "zigux/tests/phase7_build.zig");
    try expectSliceNotContains(manifest.public_fallback_non_owner_paths, "lib/rbtree.zig");
    try expectSliceNotContains(manifest.missing_paths, "lib/rbtree.zig");
    try expectSliceContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_rbtree.json");
    try expectSliceContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    try expectSliceContains(manifest.absent_makefile_markers, "phase7-rbtree-test:");
    try expectSliceContains(manifest.absent_workflow_markers, "Validate Phase 7 runtime helper gates");
    try expectSliceContains(manifest.ownership_focus, "path truthfulness must keep the currently returned helper rooted at `tools/lib/rbtree.zig` explicit while the readable roadmap destination `lib/rbtree.zig` stays explicit as shared runtime-family companion evidence rather than helper-local ownership on current master");
    try expectSliceContains(manifest.ownership_focus, ownership_focus_fallback_marker);
    try expectContains(manifest.next_bounded_step, "public-fallback provenance");
    try expectContains(manifest.next_bounded_step, "`lib/rbtree.zig` roadmap-path companion");
}
