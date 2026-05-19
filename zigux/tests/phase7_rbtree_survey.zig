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

test "phase 7 rbtree survey keeps the restored public-fallback packet scoped to rbtree only" {
    const allocator = std.testing.allocator;

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_rbtree_manifest.json");
    defer allocator.free(manifest_json);

    const direct_anchor_note = try readRepoFile(allocator, "Documentation/zigux/phase7-rbtree-direct-anchor-note.md");
    defer allocator.free(direct_anchor_note);

    const sequencing_note = try readRepoFile(allocator, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    defer allocator.free(sequencing_note);

    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    const parsed = try std.json.parseFromSlice(RbtreeManifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P7-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.anchor);
    try std.testing.expectEqualStrings("public_fallback_core_packet", manifest.current_direct_readback_state);
    try std.testing.expectEqualStrings("lib/rbtree.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.verified_on_utc.len != 0);

    try expectStringSliceContains(manifest.visible_paths, "Documentation/zigux/phase7-rbtree-slice.md");
    try expectStringSliceContains(manifest.visible_paths, "lib/rbtree.zig");
    try expectStringSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree.zig");
    try expectStringSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree_survey.zig");
    try expectStringSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree_manifest.json");
    try expectStringSliceContains(manifest.visible_paths, "scripts/zigux/check-phase7-rbtree-parity.py");
    try expectStringSliceContains(manifest.readable_non_owner_paths, "zigux/Makefile");
    try expectStringSliceContains(manifest.readable_non_owner_paths, ".github/workflows/zigux-bootstrap.yml");

    try expectStringSliceContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_rbtree.json");
    try expectStringSliceContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    try expectStringSliceContains(manifest.missing_paths, "zigux/tests/phase7_build.zig");
    try expectStringSliceContains(manifest.missing_paths, "scripts/zigux/validate-phase7.py");
    try expectNotContains(manifest_json, "\"missing_paths\": [\n    \"Documentation/zigux/phase7-rbtree-slice.md\"");
    try expectNotContains(manifest_json, "\"missing_paths\": [\n    \"lib/rbtree.zig\"");
    try expectNotContains(manifest_json, "\"missing_paths\": [\n    \"zigux/tests/phase7_rbtree.zig\"");
    try expectNotContains(manifest_json, "\"missing_paths\": [\n    \"scripts/zigux/check-phase7-rbtree-parity.py\"");

    try expectStringSliceContains(manifest.absent_makefile_markers, "phase7-validate:");
    try expectStringSliceContains(manifest.absent_makefile_markers, "phase7-rbtree-test:");
    try expectStringSliceContains(manifest.absent_makefile_markers, "phase7-rbtree-survey:");
    try expectStringSliceContains(manifest.absent_makefile_markers, "phase7-test:");
    try expectStringSliceContains(manifest.absent_makefile_markers, "phase7:");

    try expectStringSliceContains(manifest.ownership_focus, "the current public-fallback-visible rbtree core packet includes the slice note, helper, dedicated test, survey, manifest, and parity checker, but it still must not be presented as proof that the missing fixture pair or shared build-and-validator routes have returned on current master");
    try expectStringSliceContains(manifest.ownership_focus, "same-lane follow-through stays inside the restored slice-helper-test-survey-manifest-checker packet until a fresh reread proves the fixture pair or shared build-and-validator companions returned on current master");
    try expectStringSliceContains(manifest.ownership_focus, "cross-helper truthfulness must keep the landed string_helpers packet explicit instead of repeating the older blocked-by-missing-string-helper claim");
    try expectStringSliceContains(manifest.ownership_focus, "build-graph truthfulness must keep the split non-owner evidence explicit: `zigux/Makefile` is directly readable again but still lacks dedicated `phase7-*` wrapper routes, `.github/workflows/zigux-bootstrap.yml` still lacks dedicated Phase 7 runtime-helper steps, and the missing fixture pair plus shared build-and-validator files still block any claim that the broader rbtree build packet is fully restored");
    try expectContains(manifest.next_bounded_step, "restored rbtree slice-helper-test-survey-manifest-checker packet");

    try expectContains(direct_anchor_note, "Current direct-readback Phase 7 rbtree packet is publicly visible again through:");
    try expectContains(direct_anchor_note, "`Documentation/zigux/phase7-rbtree-slice.md`");
    try expectContains(direct_anchor_note, "`lib/rbtree.zig`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_rbtree.zig`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_rbtree_survey.zig`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_rbtree_manifest.json`");
    try expectContains(direct_anchor_note, "`scripts/zigux/check-phase7-rbtree-parity.py`");
    try expectContains(direct_anchor_note, "Fresh public GitHub fallback reread in this slot confirmed the slice note, helper, dedicated test, survey, manifest, and parity checker are visible again on current `master`.");
    try expectContains(direct_anchor_note, "Repo-reality warning for the still-missing Phase 7 rbtree companions:");
    try expectContains(direct_anchor_note, "`zigux/tests/fixtures/phase7_rbtree.json`");
    try expectContains(direct_anchor_note, "`zigux/tests/fixtures/phase7_rbtree_c_harness.c`");
    try expectContains(direct_anchor_note, "`zigux/tests/phase7_build.zig`");
    try expectContains(direct_anchor_note, "`scripts/zigux/validate-phase7.py`");
    try expectContains(direct_anchor_note, "`string_helpers` stays the only fully checker-backed and fixture-backed helper-local Phase 7 packet that this lane can treat as entirely reread through the authenticated contents route today");
    try expectContains(direct_anchor_note, "`cmdline` stays reviewable through the returned Phase 7 helper-local foothold");
    try expectContains(direct_anchor_note, "`argv_split` keeps its returned helper-plus-survey-manifest-checker anchor separate from the restored rbtree packet");
    try expectContains(direct_anchor_note, "do not present the missing rbtree fixture pair or the shared build-and-validator routes as restored until a fresh same-lane reread materializes them on current `master`");
    try expectContains(direct_anchor_note, "Do not widen this note into fixture-backed parity or make-wrapper recovery claims without a fresh same-lane reread of those still-missing companion surfaces.");
    try expectNotContains(direct_anchor_note, "Repo-reality warning for the broader Phase 7 rbtree packet:\n- `Documentation/zigux/phase7-rbtree-slice.md`");
    try expectNotContains(direct_anchor_note, "- `scripts/zigux/check-phase7-rbtree-parity.py`\n- `zigux/tests/phase7_rbtree.zig`");

    try expectContains(sequencing_note, "`rbtree` now survives through the public-fallback-visible core packet `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, and `scripts/zigux/check-phase7-rbtree-parity.py`.");
    try expectContains(sequencing_note, "Fresh authenticated contents reads in this slot still returned missing for `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `zigux/tests/phase7_build.zig`, and `scripts/zigux/validate-phase7.py`.");
    try expectContains(sequencing_note, "That means `P7-L13` should keep same-lane work anchored to that restored core packet");
    try expectContains(sequencing_note, "Treat scheduled lane `P7-Y04` as the rbtree alias for `P7-L13`");
    try expectContains(sequencing_note, "because the current slot could directly reread the slice note, helper, dedicated test, survey, manifest, and checker");
    try expectNotContains(sequencing_note, "Fresh authenticated contents reads in this slot still returned missing for `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, and `scripts/zigux/check-phase7-rbtree-parity.py`");
    try expectNotContains(sequencing_note, "keep same-lane work anchored to those two surviving files");

    try expectNotContains(makefile, "phase7-validate:");
    try expectNotContains(makefile, "phase7-rbtree-test:");
    try expectNotContains(makefile, "phase7-rbtree-survey:");
    try expectNotContains(makefile, "phase7-test:");
    try expectNotContains(makefile, "phase7:");
}
