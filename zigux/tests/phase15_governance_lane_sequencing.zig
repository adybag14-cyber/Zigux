const std = @import("std");

const SequencingManifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    sequencing_note: []const u8,
    readiness_manifest: []const u8,
    shared_summary_gap_note: []const u8,
    direct_packet_paths: []const []const u8,
    still_missing_broader_paths: []const []const u8,
    maintenance_replay_commands: []const []const u8,
};

const ReadinessManifest = struct {
    surveyed_commit_mode: []const u8,
    surveyed_commit: []const u8,
    readiness_packet_checker: []const u8,
    direct_packet_paths: []const []const u8,
    still_missing_broader_paths: []const []const u8,
};

fn readRepoFile(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, std.testing.allocator, .limited(limit));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |entry| {
        if (std.mem.eql(u8, entry, needle)) return;
    }
    return error.TestUnexpectedResult;
}

test "phase 15 governance-lane sequencing manifest records the new direct replay packet" {
    const manifest_json = try readRepoFile("zigux/tests/phase15_governance_lane_sequencing_manifest.json", 16 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(SequencingManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("arch-council", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-18", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-governance-lane-sequencing.md", manifest.sequencing_note);
    try std.testing.expectEqualStrings("zigux/tests/phase15_readiness_gate_manifest.json", manifest.readiness_manifest);
    try std.testing.expectEqual(@as(usize, 14), manifest.direct_packet_paths.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.still_missing_broader_paths.len);
    try std.testing.expectEqual(@as(usize, 6), manifest.maintenance_replay_commands.len);

    try expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_governance_lane_sequencing_manifest.json");
    try expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_governance_lane_sequencing.zig");
    try expectSliceContains(manifest.direct_packet_paths, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectSliceContains(manifest.direct_packet_paths, "Documentation/zigux/phase15-shared-summary-gap.md");
    try expectSliceContains(manifest.still_missing_broader_paths, "scripts/zigux/validate-phase15.py");
    try expectSliceContains(manifest.maintenance_replay_commands, "zig test zigux/tests/phase15_governance_lane_sequencing.zig");
}

test "phase 15 governance-lane sequencing note names the direct replay and remaining gaps honestly" {
    const sequencing_note = try readRepoFile("Documentation/zigux/phase15-governance-lane-sequencing.md", 24 * 1024);
    defer std.testing.allocator.free(sequencing_note);

    const manifest_json = try readRepoFile("zigux/tests/phase15_governance_lane_sequencing_manifest.json", 16 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(SequencingManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try expectContains(sequencing_note, "PHASE15_STATUS=governance_lane_sequencing_packet_landed");
    try expectContains(sequencing_note, "PHASE15_LANE_KEY=arch-council");
    try expectContains(sequencing_note, "PHASE15_PROVENANCE_MODE=dated_master_readback");
    try expectContains(sequencing_note, manifest.surveyed_commit);
    try expectContains(sequencing_note, "dedicated governance-lane sequencing manifest plus focused replay are now landed");
    try expectContains(sequencing_note, "`zigux/tests/phase15_governance_lane_sequencing_manifest.json` and `zigux/tests/phase15_governance_lane_sequencing.zig`");
    try expectContains(sequencing_note, "`Documentation/zigux/phase15-study-only-anchor-accounting.md`");
    try expectContains(sequencing_note, "`Documentation/zigux/phase15-shared-summary-gap.md`");
    try expectContains(sequencing_note, "python3 scripts/zigux/check-phase15-tests-readme-alignment.py");
    try expectContains(sequencing_note, "zig test zigux/tests/phase15_governance_lane_sequencing.zig");
    try expectContains(sequencing_note, "a missing focused replay, handoff-manifest, dedicated build file, or other absent companion is already landed on current `master`");

    for (manifest.still_missing_broader_paths) |path| {
        try expectContains(sequencing_note, path);
    }
}

test "phase 15 readiness manifest records the sequencing replay as direct packet evidence" {
    const readiness_json = try readRepoFile("zigux/tests/phase15_readiness_gate_manifest.json", 16 * 1024);
    defer std.testing.allocator.free(readiness_json);

    const parsed = try std.json.parseFromSlice(ReadinessManifest, std.testing.allocator, readiness_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const readiness = parsed.value;

    try std.testing.expectEqualStrings("dated_master_readback", readiness.surveyed_commit_mode);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-18", readiness.surveyed_commit);
    try std.testing.expectEqualStrings("scripts/zigux/check-phase15-readiness-gate-packet.py", readiness.readiness_packet_checker);
    try expectSliceContains(readiness.direct_packet_paths, "zigux/tests/phase15_governance_lane_sequencing_manifest.json");
    try expectSliceContains(readiness.direct_packet_paths, "zigux/tests/phase15_governance_lane_sequencing.zig");
    try expectSliceContains(readiness.still_missing_broader_paths, "zigux/tests/phase15_indefinite_c_lane_owner_alignment.zig");
}
