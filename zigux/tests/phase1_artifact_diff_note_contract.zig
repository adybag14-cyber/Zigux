const std = @import("std");

const artifact_note_path = "Documentation/zigux/artifact-diff.md";
const artifact_diff_path = "scripts/zigux/artifact_diff.py";
const replay_blockers_path = "zigux/tests/fixtures/phase1_replay_blockers.json";

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, std.testing.allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |index| {
        count += 1;
        offset += index + needle.len;
    }
    return count;
}

fn sectionBetween(haystack: []const u8, start_marker: []const u8, end_marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, haystack, start_marker) orelse return error.MissingStartMarker;
    const body_start = start + start_marker.len;
    const rel_end = std.mem.indexOf(u8, haystack[body_start..], end_marker) orelse return error.MissingEndMarker;
    return haystack[body_start .. body_start + rel_end];
}

test "Phase 1 artifact-diff note keeps the parity-fixture route explicit" {
    const artifact_note = try readRepoFile(artifact_note_path);
    defer std.testing.allocator.free(artifact_note);

    try std.testing.expectEqual(@as(usize, 1), countOccurrences(artifact_note, "## Current Phase 1 use"));

    const phase1 = try sectionBetween(
        artifact_note,
        "## Current Phase 1 use",
        "## Current Phase 2 use",
    );

    try expectContains(phase1, "scripts/zigux/artifact_diff.py");
    try expectContains(phase1, "phase1_helpers.json");
    try expectContains(phase1, "Phase 1 parity reminder packet");
    try expectNotContains(phase1, "sha256_pass");
    try expectNotContains(phase1, "sha256_drift");
}

test "artifact_diff helper keeps the current mode and self-test packet" {
    const artifact_diff = try readRepoFile(artifact_diff_path);
    defer std.testing.allocator.free(artifact_diff);

    try expectContains(artifact_diff, "MODE_CHOICES = (\"text\", \"json\", \"bytes\")");
    try expectContains(artifact_diff, "LEGACY_MODE_ALIASES = {\"sha256\": \"bytes\"}");
    try expectContains(artifact_diff, "SELF_TEST_CASES = [");
    try expectContains(artifact_diff, "ARTIFACT_DIFF_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}");
    try expectContains(artifact_diff, "ARTIFACT_DIFF_SELF_TEST_CASES=\" + \",\".join(SELF_TEST_CASES)");

    try expectContains(artifact_diff, "text_pass");
    try expectContains(artifact_diff, "json_invalid_expected");
    try expectContains(artifact_diff, "json_invalid_actual");
    try expectContains(artifact_diff, "json_invalid_both");
    try expectContains(artifact_diff, "bytes_pass");
    try expectContains(artifact_diff, "bytes_drift");
    try expectContains(artifact_diff, "legacy_sha256_alias");
    try expectContains(artifact_diff, "missing_mode_value_rejected");
    try expectContains(artifact_diff, "missing_positional_arguments_rejected");
    try expectContains(artifact_diff, "extra_positional_rejected");

    try expectContains(artifact_diff, "EXPECTED_JSON_ERROR=");
    try expectContains(artifact_diff, "ACTUAL_JSON_ERROR=");
    try expectContains(artifact_diff, "EXPECTED_UTF8_ERROR=");
    try expectContains(artifact_diff, "ACTUAL_UTF8_ERROR=");
    try expectContains(artifact_diff, "EXPECTED_SHA256=");
    try expectContains(artifact_diff, "ACTUAL_SHA256=");
}

test "Phase 1 replay-blocker fixture stays parked on the documented blocker packet" {
    const replay_blockers = try readRepoFile(replay_blockers_path);
    defer std.testing.allocator.free(replay_blockers);

    try expectContains(replay_blockers, "\"status\": \"parked\"");
    try expectContains(replay_blockers, "\"manifest\": \"zigux/tests/fixtures/phase1_helper_manifest.json\"");
    try expectContains(replay_blockers, "\"shared_replay_parked_helper_count\": 9");
    try expectContains(replay_blockers, "\"direct_anchor_followup_helper_count\": 4");
    try expectContains(replay_blockers, "\"path\": \"zigux/tests/phase1_helpers.zig\"");
    try expectContains(replay_blockers, "\"state\": \"blocked\"");
    try expectContains(replay_blockers, "phase1_helpers_zig_slab_zero_after_kmalloc");
    try expectContains(replay_blockers, "\"path\": \"zigux/tests/fixtures/phase1_helpers_c_harness.c\"");
    try expectContains(replay_blockers, "phase1_helpers_c_harness_missing_c_sources");
    try expectContains(replay_blockers, "\"helper_count\": 13");
}
