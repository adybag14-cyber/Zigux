const std = @import("std");

const phase4_build_source = @embedFile("phase4_build.zig");
const bitmap_survey_source = @embedFile("phase4_bitmap_diff_survey.zig");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase4 bitmap survey routes remain present in the dedicated differential build" {
    try expectContains(
        phase4_build_source,
        ".root_source_file = b.path(\"phase4_bitmap_diff_survey.zig\")",
    );
    try expectContains(
        phase4_build_source,
        ".name = \"phase4-bitmap-diff-survey-tests\"",
    );
    try expectContains(
        phase4_build_source,
        "\"phase4-bitmap-diff-survey\"",
    );
    try expectContains(
        phase4_build_source,
        "Run the manifest-backed Phase 4 bitmap rollback survey",
    );
}

test "phase4 bitmap helper replay remains paired with the survey route" {
    try expectContains(
        phase4_build_source,
        ".root_source_file = b.path(\"phase4_bitmap_live_helper_replay.zig\")",
    );
    try expectContains(
        phase4_build_source,
        ".name = \"phase4-bitmap-live-helper-replay-tests\"",
    );
    try expectContains(
        phase4_build_source,
        "\"phase4-bitmap-live-helper-replay\"",
    );
}

test "phase4 bitmap survey still documents the repo-root embed boundary" {
    try expectContains(
        bitmap_survey_source,
        "const gate_evidence_source = @embedFile(\"../../Documentation/zigux/phase4-gate-evidence.md\");",
    );
    try expectContains(
        bitmap_survey_source,
        "try std.testing.expectEqualStrings(&gitBlobShaHex(gate_evidence_source), manifest.gate_evidence_blob_sha);",
    );
}
