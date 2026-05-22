const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoRelative(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    const io = std.testing.io;
    return try std.Io.Dir.cwd().readFileAlloc(io, relative_path, allocator, .limited(64 * 1024));
}

test "phase10 virtio core survey gate keeps verify and focused replay surfaces explicit" {
    const allocator = std.testing.allocator;

    const survey_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-core-survey.md",
    );
    defer allocator.free(survey_note);

    const build_file = try readRepoRelative(allocator, "zigux/tests/phase10_build.zig");
    defer allocator.free(build_file);

    const closure_manifest = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_closure_manifest.json",
    );
    defer allocator.free(closure_manifest);

    try expectContains(survey_note, "drivers/virtio/virtio_verify.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_core_reset_queue.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig");
    try expectContains(survey_note, "phase10-core-probe-remove-lifecycle");
    try expectContains(build_file, "\"phase10-virtio-core-verify-tests\"");
    try expectContains(build_file, "\"phase10-virtio-core-reset-queue-tests\"");
    try expectContains(build_file, "\"phase10-virtio-core-interrupt-compound-ack-tests\"");
    try expectContains(build_file, "run_phase10_virtio_core_verify_tests.step");
    try expectContains(build_file, "run_phase10_virtio_core_reset_queue_tests.step");
    try expectContains(build_file, "run_phase10_virtio_core_interrupt_compound_ack_tests.step");
    try expectContains(closure_manifest, "\"drivers/virtio/virtio_verify.zig\"");
    try expectContains(closure_manifest, "\"zigux/tests/phase10_virtio_core_reset_queue.zig\"");
    try expectContains(closure_manifest, "\"zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig\"");
}

test "phase10 virtio core survey gate keeps slice-local review surfaces and blockers explicit" {
    const allocator = std.testing.allocator;

    const slice_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-core-slice.md",
    );
    defer allocator.free(slice_note);

    const manifest = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_virtio_core_manifest.json",
    );
    defer allocator.free(manifest);

    try expectContains(slice_note, "drivers/virtio/virtio_verify.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_core_reset_queue.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_core_survey.zig");
    try expectContains(manifest, "\"lane_key\": \"P10-L01\"");
    try expectContains(manifest, "\"id\": \"phase10-lifecycle-guard-bookkeeping-helper\"");
    try expectContains(manifest, "\"id\": \"phase10-reset-replay-bookkeeping-helper\"");
    try expectContains(manifest, "\"id\": \"phase10-core-dual-implementation-bridge\"");
    try expectContains(manifest, "\"id\": \"phase10-core-probe-remove-lifecycle\"");
}
