const std = @import("std");

test "phase 15 governance-lane sequencing manifest records the new direct replay packet" {
    try std.testing.expectEqualStrings("P15-Y06", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 15", manifest.phase);
    try std.testing.expectEqualStrings("current-master-readback-2026-05-19", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Documentation/zigux/phase15-governance-lane-sequencing.md", manifest.sequencing_note);
    try expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_governance_lane_sequencing_manifest.json");
    try expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_governance_lane_sequencing.zig");
    try expectSliceContains(manifest.direct_packet_paths, "zigux/tests/phase15_handoff_next_steps_manifest.json");
    try expectSliceContains(manifest.direct_packet_paths, "scripts/zigux/check-phase15-handoff-note-alignment.py");
    try expectSliceContains(manifest.direct_packet_paths, "Documentation/zigux/phase15-study-only-anchor-accounting.md");
    try expectSliceContains(manifest.direct_packet_paths, "Documentation/zigux/phase15-shared-summary-gap.md");
    try expectSliceContains(manifest.still_missing_broader_paths, "scripts/zigux/validate-phase15.py");
    try expectSliceContains(manifest.maintenance_replay_commands, "python3 scripts/zigux/check-phase15-handoff-note-alignment.py");
    try expectSliceContains(manifest.maintenance_replay_commands, "zig test zigux/tests/phase15_governance_lane_sequencing.zig");
}
