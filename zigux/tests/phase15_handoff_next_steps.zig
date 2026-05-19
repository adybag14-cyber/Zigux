const std = @import("std");

const HandoffManifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    handoff_note: []const u8,
    checker: []const u8,
    present_paths: []const []const u8,
    still_missing_paths: []const []const u8,
    required_markers: []const []const u8,
    checker_group_markers: []const []const u8,
    handoff_rule_markers: []const []const u8,
};

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

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |entry| {
        if (std.mem.eql(u8, entry, needle)) return;
    }
    return error.TestUnexpectedResult;
}

test "phase 15 handoff manifest records the focused replay as landed packet evidence" {
    const manifest_json = try readRepoFile("zigux/tests/phase15_handoff_next_steps_manifest.json", 20 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(HandoffManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P15-L08", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-19", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-handoff-next-steps-survey.md", manifest.handoff_note);
    try std.testing.expectEqualStrings("scripts/zigux/check-phase15-handoff-note-alignment.py", manifest.checker);
    try std.testing.expectEqual(@as(usize, 22), manifest.present_paths.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.still_missing_paths.len);
    try std.testing.expectEqual(@as(usize, 7), manifest.required_markers.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.checker_group_markers.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.handoff_rule_markers.len);

    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_architecture_council_review_process.zig");
    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_handoff_next_steps_manifest.json");
    try expectSliceContains(manifest.present_paths, "zigux/tests/phase15_handoff_next_steps.zig");
    try expectSliceContains(manifest.present_paths, "scripts/zigux/check-phase15-handoff-note-alignment.py");
    try expectSliceContains(manifest.still_missing_paths, "scripts/zigux/validate-phase15.py");
    try expectSliceContains(manifest.still_missing_paths, "zigux/tests/phase15_build.zig");
}

test "phase 15 handoff note treats the focused replay as present and broader companions as still missing" {
    const handoff_note = try readRepoFile("Documentation/zigux/phase15-handoff-next-steps-survey.md", 24 * 1024);
    defer std.testing.allocator.free(handoff_note);

    const manifest_json = try readRepoFile("zigux/tests/phase15_handoff_next_steps_manifest.json", 20 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(HandoffManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try expectContains(handoff_note, "PHASE15_STATUS=handoff_next_steps_survey_landed");
    try expectContains(handoff_note, "PHASE15_LANE_KEY=P15-L08");
    try expectContains(handoff_note, "PHASE15_PROVENANCE_MODE=dated_master_readback");
    try expectContains(handoff_note, manifest.surveyed_commit);
    try expectContains(handoff_note, "the dedicated handoff-specific manifest `zigux/tests/phase15_handoff_next_steps_manifest.json` and the focused handoff-specific Zig replay `zigux/tests/phase15_handoff_next_steps.zig` are directly materialized on current `master`");
    try expectContains(handoff_note, "Treat this note together with `zigux/tests/phase15_handoff_next_steps_manifest.json` and `zigux/tests/phase15_handoff_next_steps.zig` as the handoff-specific source of truth while the broader validator-first, dedicated-build, and lane-owner companions remain gap-tracked.");
    try expectNotContains(handoff_note, "no dedicated handoff-specific Zig replay is directly materialized on current `master`");

    for (manifest.present_paths) |path| {
        try expectContains(handoff_note, path);
    }
    for (manifest.still_missing_paths) |path| {
        try expectContains(handoff_note, path);
    }
    for (manifest.required_markers) |marker| {
        try expectContains(handoff_note, marker);
    }
    for (manifest.checker_group_markers) |marker| {
        try expectContains(handoff_note, marker);
    }
    for (manifest.handoff_rule_markers) |marker| {
        try expectContains(handoff_note, marker);
    }
}
