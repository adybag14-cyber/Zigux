const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoRelative(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    const io = std.testing.io;
    return try std.Io.Dir.cwd().readFileAlloc(io, relative_path, allocator, .limited(64 * 1024));
}

test "phase10 virtio mmio survey note keeps the dedicated survey gate explicit beside the helper-local packet" {
    const allocator = std.testing.allocator;

    const survey_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-mmio-survey.md",
    );
    defer allocator.free(survey_note);

    const build_file = try readRepoRelative(allocator, "zigux/tests/phase10_build.zig");
    defer allocator.free(build_file);

    try expectContains(survey_note, "PHASE10_STATUS=parked");
    try expectContains(survey_note, "drivers/virtio/virtio_mmio.zig");
    try expectContains(survey_note, "drivers/virtio/virtio_mmio_verify.zig");
    try expectContains(survey_note, "config-write disposition reporting");
    try expectContains(survey_note, "feature-negotiation deltas");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_mmio_survey.zig");
    try expectContains(survey_note, "zig test zigux/tests/phase10_virtio_mmio_survey.zig");
    try expectContains(build_file, "phase10_virtio_mmio_survey_module");
    try expectContains(build_file, "\"phase10-virtio-mmio-survey-tests\"");
    try expectContains(build_file, "run_phase10_virtio_mmio_survey_tests.step");
}

test "phase10 virtio mmio survey gate keeps manifest lane identity and risky transport posture explicit" {
    const allocator = std.testing.allocator;

    const manifest = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_virtio_mmio_manifest.json",
    );
    defer allocator.free(manifest);

    try expectContains(manifest, "\"lane_key\": \"P10-L11\"");
    try expectContains(manifest, "\"risky_transport_posture\": \"blocked_on_risky_transport\"");
    try expectContains(manifest, "\"id\": \"phase10-virtio-mmio-survey-gate\"");
}

test "phase10 virtio mmio survey note keeps risky transport work blocked" {
    const allocator = std.testing.allocator;

    const survey_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-mmio-survey.md",
    );
    defer allocator.free(survey_note);

    try expectContains(survey_note, "transport-backed queue setup or queue reset execution");
    try expectContains(survey_note, "shared IRQ delivery parity");
    try expectContains(survey_note, "DMA-facing behavior");
    try expectContains(survey_note, "probe, remove, freeze, restore, or device-lifecycle closure");
}
