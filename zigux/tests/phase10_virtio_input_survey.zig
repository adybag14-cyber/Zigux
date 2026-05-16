const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoRelative(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    const io = std.testing.io;
    return try std.Io.Dir.cwd().readFileAlloc(io, relative_path, allocator, .limited(64 * 1024));
}

fn expectSurveyedCommitAlignment(
    allocator: std.mem.Allocator,
    survey_note: []const u8,
    manifest: []const u8,
) !void {
    const manifest_marker = "\"surveyed_commit\": \"";
    const marker_index = std.mem.indexOf(u8, manifest, manifest_marker) orelse return error.MissingManifestSurveyedCommit;
    const commit_start = marker_index + manifest_marker.len;
    const commit_end = std.mem.indexOfScalarPos(u8, manifest, commit_start, '"') orelse return error.UnterminatedManifestSurveyedCommit;
    const commit = manifest[commit_start..commit_end];

    const note_marker = try std.fmt.allocPrint(allocator, "PHASE10_SURVEYED_COMMIT={s}", .{commit});
    defer allocator.free(note_marker);
    try expectContains(survey_note, note_marker);
}

test "phase10 virtio input survey note keeps the restored verifier and queue callback packet explicit" {
    const allocator = std.testing.allocator;
    const survey_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-input-survey.md",
    );
    defer allocator.free(survey_note);

    const manifest = try readRepoRelative(allocator, "zigux/tests/phase10_virtio_input_manifest.json");
    defer allocator.free(manifest);

    try expectContains(survey_note, "PHASE10_STATUS=parked");
    try expectContains(survey_note, "PHASE10_DUAL_IMPLEMENTATION_POSTURE=blocked_on_risky_transport");
    try expectSurveyedCommitAlignment(allocator, survey_note, manifest);
    try expectContains(survey_note, "drivers/virtio/virtio_input_verify.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_input_survey.zig");
}

test "phase10 virtio input manifest keeps the restored replay ids and blocked lifecycle posture explicit" {
    const allocator = std.testing.allocator;
    const manifest = try readRepoRelative(allocator, "zigux/tests/phase10_virtio_input_manifest.json");
    defer allocator.free(manifest);

    try expectContains(manifest, "\"id\": \"phase10-virtio-input-verify-replay\"");
    try expectContains(manifest, "\"zigux_destination\": \"drivers/virtio/virtio_input_verify.zig\"");
    try expectContains(manifest, "\"id\": \"phase10-virtio-input-queue-callback-preflight-replay\"");
    try expectContains(manifest, "\"zigux_destination\": \"zigux/tests/phase10_virtio_input_queue_callback_preflight.zig\"");
    try expectContains(manifest, "\"id\": \"phase10-virtio-input-survey-gate\"");
    try expectContains(manifest, "\"status\": \"blocked_on_risky_transport\"");
    try expectContains(manifest, "\"id\": \"phase10-virtio-input-registration-lifecycle\"");
}

test "phase10 virtio input slice companions keep the replay inventory and blocked lifecycle boundary explicit" {
    const allocator = std.testing.allocator;
    const slice_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-input-slice.md",
    );
    defer allocator.free(slice_note);

    const module_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-input-module-slice.md",
    );
    defer allocator.free(module_note);

    try expectContains(slice_note, "scripts/zigux/check-phase10-input-packet.py");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_input_registration_preflight.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_input_teardown_observation.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_input_status_drain.zig");

    try expectContains(module_note, "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig");
    try expectContains(module_note, "zigux/tests/phase10_virtio_input_registration_preflight.zig");
    try expectContains(module_note, "zigux/tests/phase10_virtio_input_teardown_observation.zig");
    try expectContains(module_note, "the bounded status-drain helper");
    try expectContains(module_note, "registration lifecycle closure, freeze, restore, remove, and broader transport-backed lifecycle work remain outside this module slice");
}
