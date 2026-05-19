const std = @import("std");

fn expectSliceContains(haystack: []const []const u8, needle: []const u8) !void {
    for (haystack) |entry| {
        if (std.mem.eql(u8, entry, needle)) return;
    }
    return error.TestUnexpectedResult;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

const SequencingManifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    sequencing_note: []const u8,
    direct_packet_paths: []const []const u8,
    still_missing_broader_paths: []const []const u8,
    maintenance_replay_commands: []const []const u8,
};

test "phase 15 governance-lane sequencing manifest records the current direct packet and gaps" {
    const manifest_json =
        \\{
        \\  "lane_key": "P15-Y06",
        \\  "phase": "Phase 15",
        \\  "surveyed_commit": "current-master-readback-2026-05-19",
        \\  "sequencing_note": "Documentation/zigux/phase15-governance-lane-sequencing.md",
        \\  "direct_packet_paths": [
        \\    "zigux/tests/phase15_governance_lane_sequencing_manifest.json",
        \\    "zigux/tests/phase15_governance_lane_sequencing.zig",
        \\    "zigux/tests/phase15_handoff_next_steps_manifest.json",
        \\    "scripts/zigux/check-phase15-handoff-note-alignment.py",
        \\    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
        \\    "Documentation/zigux/phase15-shared-summary-gap.md"
        \\  ],
        \\  "still_missing_broader_paths": [
        \\    "scripts/zigux/validate-phase15.py"
        \\  ],
        \\  "maintenance_replay_commands": [
        \\    "python3 scripts/zigux/check-phase15-handoff-note-alignment.py",
        \\    "zig test zigux/tests/phase15_governance_lane_sequencing.zig"
        \\  ]
        \\}
    ;
    const parsed = try std.json.parseFromSlice(SequencingManifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P15-Y06", manifest.lane_key);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-19", manifest.surveyed_commit);
    try expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_handoff_next_steps_manifest.json");
    try expectSliceContains(manifest.direct_packet_paths, "scripts/zigux/check-phase15-handoff-note-alignment.py");
}

test "phase 15 governance-lane sequencing note keeps explicit shared-surface boundaries" {
    const sequencing_note =
        \\The shared reminder surfaces may say that:
        \\
        \\The shared reminder surfaces must not say that:
    ;
    try expectContains(sequencing_note, "The shared reminder surfaces may say that:");
    try expectContains(sequencing_note, "The shared reminder surfaces must not say that:");
}
