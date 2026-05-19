const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoRelative(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    const io = std.testing.io;
    return try std.Io.Dir.cwd().readFileAlloc(io, relative_path, allocator, .limited(64 * 1024));
}

test "phase10 virtio ring survey note keeps the missing broader replay explicit beside the queue-local helper packet" {
    const allocator = std.testing.allocator;

    const survey_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-ring-survey.md",
    );
    defer allocator.free(survey_note);

    const build_file = try readRepoRelative(allocator, "zigux/tests/phase10_build.zig");
    defer allocator.free(build_file);

    const verify_file = try readRepoRelative(allocator, "drivers/virtio/virtio_ring_verify.zig");
    defer allocator.free(verify_file);

    try expectContains(survey_note, "PHASE10_STATUS=parked");
    try expectContains(survey_note, "drivers/virtio/virtio_ring.zig");
    try expectContains(survey_note, "drivers/virtio/virtio_ring_verify.zig");
    try expectContains(
        survey_note,
        "broader replay `zigux/tests/phase10_virtio_ring.zig` still does not materialize",
    );
    try expectContains(survey_note, "zigux/tests/phase10_virtio_ring_survey.zig");
    try expectContains(survey_note, "zig test zigux/tests/phase10_virtio_ring_survey.zig");
    try expectContains(
        verify_file,
        "test \"phase10 virtio ring verify exposes reset-readiness blocker ordering after clearBroken releases queue debt\" {",
    );
    try expectContains(
        verify_file,
        "test \"phase10 virtio ring verify keeps reset-readiness blockers ordered through queue-local replay\" {",
    );
    try expectContains(build_file, "phase10_virtio_ring_survey_module");
    try expectContains(build_file, "\\\"phase10-virtio-ring-survey-tests\\\"");
    try expectContains(build_file, "run_phase10_virtio_ring_survey_tests.step");
}

test "phase10 virtio ring survey manifest keeps lane identity and blocked transport posture explicit" {
    const allocator = std.testing.allocator;

    const manifest = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_virtio_ring_manifest.json",
    );
    defer allocator.free(manifest);

    try expectContains(manifest, "\"lane_key\": \"P10-L05\"");
    try expectContains(manifest, "\"risky_transport_posture\": \"blocked_on_risky_transport\"");
    try expectContains(manifest, "\"id\": \"phase10-virtio-ring-survey-gate\"");
    try expectContains(manifest, "\"id\": \"phase10-queue-reset-helper\"");
    try expectContains(manifest, "\"id\": \"phase10-queue-reset-readiness-helper\"");
    try expectContains(manifest, "\"status\": \"starter_landed\"");
    try expectContains(manifest, "\"zigux_destination\": \"zigux/tests/phase10_virtio_ring_survey.zig\"");
}

test "phase10 virtio ring slice companions keep the broader replay gap and landed survey replay explicit" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-ring-slice.md",
    );
    defer allocator.free(slice_note);

    try expectContains(
        slice_note,
        "the broader ring replay still remains outside direct current-head evidence in this slice",
    );
    try expectContains(slice_note, "zigux/tests/phase10_virtio_ring_survey.zig");
    try expectContains(slice_note, "the dedicated survey gate is now a landed review surface inside this slice");
}

test "phase10 virtio ring freeze-boundary note keeps risky transport work blocked" {
    const allocator = std.testing.allocator;

    const freeze_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-ring-freeze-boundary-survey.md",
    );
    defer allocator.free(freeze_note);

    try expectContains(freeze_note, "transport-backed queue setup or reset parity");
    try expectContains(freeze_note, "IRQ parity");
    try expectContains(freeze_note, "DMA-facing paths");
    try expectContains(freeze_note, "probe or remove lifecycle closure");
    try expectContains(
        freeze_note,
        "the broader ring replay `zigux/tests/phase10_virtio_ring.zig` still remains a direct-readback gap",
    );
    try expectContains(freeze_note, "zigux/tests/phase10_virtio_ring_survey.zig");
}
