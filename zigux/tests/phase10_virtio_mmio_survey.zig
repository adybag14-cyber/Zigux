const std = @import("std");

const SurveySummary = struct {
    preexisting_phase10_test_files: usize,
    preexisting_virtio_mmio_verify_present: bool,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    roadmap_destinations: []const []const u8,
    risky_transport_posture: []const u8,
    survey_summary: SurveySummary,
    gaps: []const Gap,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoRelative(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    const io = std.testing.io;
    return try std.Io.Dir.cwd().readFileAlloc(io, relative_path, allocator, .limited(64 * 1024));
}

test "phase10 virtio mmio survey manifest records the landed identity-backed packet" {
    const allocator = std.testing.allocator;
    const manifest_text = try readRepoRelative(allocator, "zigux/tests/phase10_virtio_mmio_manifest.json");
    defer allocator.free(manifest_text);
    var parsed = try std.json.parseFromSlice(Manifest, allocator, manifest_text, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    const survey_note = try readRepoRelative(allocator, "Documentation/zigux/phase10-virtio-mmio-survey.md");
    defer allocator.free(survey_note);
    const build_file = try readRepoRelative(allocator, "zigux/tests/phase10_build.zig");
    defer allocator.free(build_file);

    try std.testing.expectEqualStrings("P10-L11", manifest.lane_key);
    try std.testing.expectEqual(@as(usize, 11), manifest.survey_summary.preexisting_phase10_test_files);
    try std.testing.expectEqual(@as(usize, 3), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("drivers/virtio/*.zig", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("zigux/kernel/", manifest.roadmap_destinations[1]);
    try std.testing.expectEqualStrings("zigux/helpers/", manifest.roadmap_destinations[2]);
    try std.testing.expectEqualStrings("blocked_on_risky_transport", manifest.risky_transport_posture);
    try expectContains(survey_note, "zigux/tests/phase10_virtio_input_probe_preflight.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_input_queue_callback_preflight.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_input_registration_preflight.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_input_teardown_observation.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_input_status_drain.zig");
    try expectContains(survey_note, "drivers/virtio/virtio_ring_verify.zig");
    try expectContains(survey_note, "drivers/virtio/virtio_input_verify.zig");
    try expectContains(survey_note, "drivers/virtio/virtio_mmio_verify.zig");
    try expectContains(survey_note, "transport-identity summary");
    try expectContains(survey_note, "consumes that identity snapshot");
    try expectContains(survey_note, "selected-queue readiness summary");
    try expectContains(survey_note, "probe-preflight summary flips from ready to blocked");
    try expectContains(build_file, "phase10-virtio-mmio-verify-tests");
    try expectContains(build_file, "run_phase10_virtio_mmio_verify_tests.step");
    try std.testing.expect(manifest.survey_summary.preexisting_virtio_mmio_verify_present);

    const starter_landed_count = std.mem.count(u8, manifest_text, "\"starter_landed\"");
    try std.testing.expect(starter_landed_count >= 16);
}
