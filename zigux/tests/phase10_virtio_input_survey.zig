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

test "phase10 virtio input survey note keeps the restored verifier, teardown parity, and queue callback packet explicit" {
    const allocator = std.testing.allocator;
    const survey_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-input-survey.md",
    );
    defer allocator.free(survey_note);

    const manifest = try readRepoRelative(allocator, "zigux/tests/phase10_virtio_input_manifest.json");
    defer allocator.free(manifest);

    try expectContains(survey_note, "PHASE10_STATUS=parked");
    try expectContains(survey_note, "PHASE10_LANE_KEY=P10-L22");
    try expectContains(survey_note, "PHASE10_DUAL_IMPLEMENTATION_POSTURE=blocked_on_risky_transport");
    try expectContains(survey_note, "roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`");
    try expectContains(survey_note, "lab-only driver validation");
    try expectSurveyedCommitAlignment(allocator, survey_note, manifest);
    try expectContains(survey_note, "drivers/virtio/virtio_input_verify.zig");
    try expectContains(survey_note, "drivers/virtio/virtio_input_queue_callback_preflight.zig");
    try expectContains(survey_note, "drivers/virtio/virtio_input_registration_preflight.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_input_status_drain.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_input_teardown_observation.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_input_survey.zig");
    try expectContains(
        survey_note,
        "the direct input gate, the probe-preflight replay, the queue-callback-preflight replay, the registration-preflight replay, the status-drain replay, the teardown-observation replay, the dedicated survey replay, and the wrapper-facing verify replay into one bounded shared gate for the live input packet.",
    );
    try expectContains(
        survey_note,
        "wrapper-facing teardown-reset verify parity stays explicit across reset",
    );
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "helper-local MMIO tests") == null);
}

test "phase10 virtio input manifest keeps the restored replay ids and blocked lifecycle posture explicit" {
    const allocator = std.testing.allocator;
    const manifest = try readRepoRelative(allocator, "zigux/tests/phase10_virtio_input_manifest.json");
    defer allocator.free(manifest);

    try expectContains(manifest, "\"preexisting_virtio_core_zig_present\": true");
    try expectContains(manifest, "\"preexisting_virtio_ring_zig_present\": true");
    try expectContains(manifest, "\"preexisting_virtio_mmio_survey_present\": true");
    try expectContains(manifest, "\"id\": \"phase10-virtio-input-queue-callback-preflight-helper\"");
    try expectContains(manifest, "\"zigux_destination\": \"drivers/virtio/virtio_input_queue_callback_preflight.zig\"");
    try expectContains(manifest, "\"id\": \"phase10-virtio-input-verify-replay\"");
    try expectContains(manifest, "\"zigux_destination\": \"drivers/virtio/virtio_input_verify.zig\"");
    try expectContains(
        manifest,
        "teardown-reset parity across reset explicit without widening into transport-backed queue execution or freeze, restore, or remove lifecycle claims",
    );
    try expectContains(manifest, "\"id\": \"phase10-virtio-input-queue-callback-preflight-replay\"");
    try expectContains(manifest, "\"zigux_destination\": \"zigux/tests/phase10_virtio_input_queue_callback_preflight.zig\"");
    try expectContains(manifest, "\"id\": \"phase10-virtio-input-registration-preflight-helper\"");
    try expectContains(manifest, "\"zigux_destination\": \"drivers/virtio/virtio_input_registration_preflight.zig\"");
    try expectContains(manifest, "\"id\": \"phase10-virtio-input-survey-gate\"");
    try expectContains(manifest, "\"roadmap_destinations\": [");
    try expectContains(manifest, "\"drivers/virtio/*.zig\"");
    try expectContains(manifest, "\"zigux/kernel/\"");
    try expectContains(manifest, "\"zigux/helpers/\"");
    try expectContains(manifest, "\"allowed_evidence_kinds\": [");
    try expectContains(manifest, "\"driver_local_lab_slices\"");
    try expectContains(manifest, "\"survey_manifests\"");
    try expectContains(manifest, "\"shared_validation_gates\"");
    try expectContains(manifest, "\"status\": \"blocked_on_risky_transport\"");
    try expectContains(manifest, "\"id\": \"phase10-virtio-input-registration-lifecycle\"");
}

test "phase10 virtio input queue callback helper stays explicit in the survey packet" {
    const allocator = std.testing.allocator;
    const survey_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-input-survey.md",
    );
    defer allocator.free(survey_note);

    const manifest = try readRepoRelative(allocator, "zigux/tests/phase10_virtio_input_manifest.json");
    defer allocator.free(manifest);

    const helper = try readRepoRelative(
        allocator,
        "drivers/virtio/virtio_input_queue_callback_preflight.zig",
    );
    defer allocator.free(helper);

    try expectContains(survey_note, "drivers/virtio/virtio_input_queue_callback_preflight.zig");
    try expectContains(manifest, "\"id\": \"phase10-virtio-input-queue-callback-preflight-helper\"");
    try expectContains(manifest, "\"zigux_destination\": \"drivers/virtio/virtio_input_queue_callback_preflight.zig\"");
    try expectContains(helper, "pub const QueueCallbackPreflightSummary = virtio_input.QueueCallbackPreflightSummary;");
    try expectContains(helper, "pub const QueueCallbackPreflightBlocker = virtio_input.QueueCallbackPreflightBlocker;");
    try expectContains(helper, "pub fn summarize(device: *const virtio_input.VirtioInputLab) QueueCallbackPreflightSummary {");
    try expectContains(helper, "pub fn blockerTag(blocker: QueueCallbackPreflightBlocker) []const u8 {");
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
    try expectContains(slice_note, "drivers/virtio/virtio_input_registration_preflight.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_input_registration_preflight.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_input_teardown_observation.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_input_status_drain.zig");
    try expectContains(slice_note, "teardown-reset parity explicit across reset");

    try expectContains(module_note, "drivers/virtio/virtio_input_registration_preflight.zig");
    try expectContains(module_note, "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig");
    try expectContains(module_note, "zigux/tests/phase10_virtio_input_registration_preflight.zig");
    try expectContains(module_note, "zigux/tests/phase10_virtio_input_status_drain.zig");
    try expectContains(module_note, "zigux/tests/phase10_virtio_input_teardown_observation.zig");
    try expectContains(module_note, "teardown-reset parity across reset");
    try expectContains(module_note, "the dedicated status-drain helper plus replay");
    try expectContains(module_note, "registration lifecycle closure, freeze, restore, remove, and broader transport-backed lifecycle work remain outside this module slice");
}
