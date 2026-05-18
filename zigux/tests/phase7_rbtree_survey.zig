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
    missing_paths: []const []const u8,
    readable_makefile_markers: []const []const u8,
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

test "phase 7 rbtree survey keeps the surviving anchor packet truthful" {
    const allocator = std.testing.allocator;

    const manifest_json = try readRepoFile(allocator, "zigux/tests/phase7_rbtree_manifest.json");
    defer allocator.free(manifest_json);

    const sequencing_note = try readRepoFile(allocator, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    defer allocator.free(sequencing_note);

    const makefile = try readRepoFile(allocator, "zigux/Makefile");
    defer allocator.free(makefile);

    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    const string_helper = try readRepoFile(allocator, "lib/string_helpers.zig");
    defer allocator.free(string_helper);

    const string_helper_tests = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers.zig");
    defer allocator.free(string_helper_tests);

    const string_helper_survey = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_survey.zig");
    defer allocator.free(string_helper_survey);

    const string_helper_manifest = try readRepoFile(allocator, "zigux/tests/phase7_string_helpers_manifest.json");
    defer allocator.free(string_helper_manifest);

    const parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P7-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 7", manifest.phase);
    try std.testing.expectEqualStrings("lib/rbtree.c", manifest.anchor);
    try std.testing.expectEqualStrings("survey_and_manifest_anchor", manifest.current_direct_readback_state);
    try std.testing.expectEqual(@as(usize, 1), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("lib/rbtree.zig", manifest.roadmap_destinations[0]);
    try std.testing.expect(manifest.verified_on_utc.len != 0);

    try expectStringSliceContains(manifest.visible_paths, "Documentation/zigux/phase7-helper-lane-sequencing.md");
    try expectStringSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree_survey.zig");
    try expectStringSliceContains(manifest.visible_paths, "zigux/tests/phase7_rbtree_manifest.json");

    try expectStringSliceContains(manifest.readable_non_owner_paths, "zigux/Makefile");
    try expectStringSliceContains(manifest.readable_non_owner_paths, ".github/workflows/zigux-bootstrap.yml");

    try expectStringSliceContains(manifest.missing_paths, "Documentation/zigux/phase7-rbtree-slice.md");
    try expectStringSliceContains(manifest.missing_paths, "lib/rbtree.zig");
    try expectStringSliceContains(manifest.missing_paths, "zigux/tests/phase7_rbtree.zig");
    try expectStringSliceContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_rbtree.json");
    try expectStringSliceContains(manifest.missing_paths, "zigux/tests/fixtures/phase7_rbtree_c_harness.c");
    try expectStringSliceContains(manifest.missing_paths, "scripts/zigux/check-phase7-rbtree-parity.py");
    try expectStringSliceContains(manifest.missing_paths, "zigux/tests/phase7_build.zig");
    try expectStringSliceContains(manifest.missing_paths, "scripts/zigux/validate-phase7.py");

    try expectStringSliceContains(manifest.readable_makefile_markers, "phase7-validate:");
    try expectStringSliceContains(manifest.readable_makefile_markers, "phase7-rbtree-test:");
    try expectStringSliceContains(manifest.readable_makefile_markers, "phase7-rbtree-survey:");
    try expectStringSliceContains(manifest.readable_makefile_markers, "phase7-test:");
    try expectStringSliceContains(manifest.readable_makefile_markers, "phase7:");

    try expectStringSliceContains(manifest.absent_workflow_markers, "Validate Phase 7 runtime helper gates");
    try expectStringSliceContains(manifest.absent_workflow_markers, "Run Phase 7 runtime helper tests");
    try expectStringSliceContains(manifest.absent_workflow_markers, "make -C zigux phase7-validate");
    try expectStringSliceContains(manifest.absent_workflow_markers, "make -C zigux phase7-test");

    try expectStringSliceContains(manifest.ownership_focus, "the surviving survey-plus-manifest anchor must not be presented as proof that the broader rbtree helper, dedicated test, fixture, checker, or shared build files have returned on current master");
    try expectStringSliceContains(manifest.ownership_focus, "same-lane follow-through stays inside the surviving survey and manifest anchors until a fresh reread proves another rbtree companion returned on current master");
    try expectStringSliceContains(manifest.ownership_focus, "cross-helper truthfulness must keep the landed string_helpers packet explicit instead of repeating the older blocked-by-missing-string-helper claim");
    try expectStringSliceContains(manifest.ownership_focus, "build-graph truthfulness must keep the split non-owner evidence explicit: `zigux/Makefile` now exposes the current `phase7-*` wrapper routes, `.github/workflows/zigux-bootstrap.yml` still lacks dedicated Phase 7 runtime-helper steps, and the missing helper, dedicated test, checker, and shared build files still block any claim that the broader rbtree build packet returned");
    try expectContains(manifest.next_bounded_step, "survey-or-manifest truthfulness");

    try expectContains(sequencing_note, "rbtree currently survives through the direct anchors `zigux/tests/phase7_rbtree_survey.zig` and `zigux/tests/phase7_rbtree_manifest.json`.");
    try expectContains(sequencing_note, "keep same-lane work anchored to those two surviving files");
    try expectContains(sequencing_note, "instead of repeating the older blocked-by-missing-string-helpers story");
    try expectContains(sequencing_note, "shared wrapper stack as parked reminder vocabulary until those files rematerialize");

    try expectContains(makefile, "phase7-validate:");
    try expectContains(makefile, "phase7-rbtree-test:");
    try expectContains(makefile, "phase7-rbtree-survey:");
    try expectContains(makefile, "phase7-test:");
    try expectContains(makefile, "phase7:");

    try expectNotContains(workflow, "Validate Phase 7 runtime helper gates");
    try expectNotContains(workflow, "Run Phase 7 runtime helper tests");
    try expectNotContains(workflow, "make -C zigux phase7-validate");
    try expectNotContains(workflow, "make -C zigux phase7-test");

    try expectContains(string_helper, "pub fn sysfsStreq");
    try expectContains(string_helper, "pub fn kstrdupQuotableCmdline");
    try expectContains(string_helper_tests, "phase 7 string helpers starter quotes cmdlines after collapsing trailing NULs and replacing inter-argument separators");
    try expectContains(string_helper_survey, "phase 7 string helpers survey keeps the expanded starter packet truthful");
    try expectContains(string_helper_manifest, "\"current_master_state\": \"expanded_starter_packet\"");
}
