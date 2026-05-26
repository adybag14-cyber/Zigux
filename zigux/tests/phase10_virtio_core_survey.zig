const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn stripAsciiWhitespace(allocator: std.mem.Allocator, input: []const u8) ![]u8 {
    var kept: usize = 0;
    for (input) |byte| {
        switch (byte) {
            ' ', '\n', '\r', '\t' => {},
            else => kept += 1,
        }
    }

    const output = try allocator.alloc(u8, kept);
    errdefer allocator.free(output);

    var index: usize = 0;
    for (input) |byte| {
        switch (byte) {
            ' ', '\n', '\r', '\t' => {},
            else => {
                output[index] = byte;
                index += 1;
            },
        }
    }

    return output;
}

fn readRepoRelative(allocator: std.mem.Allocator, relative_path: []const u8) ![]u8 {
    const io = std.testing.io;
    return try std.Io.Dir.cwd().readFileAlloc(io, relative_path, allocator, .limited(64 * 1024));
}

test "phase10 virtio core survey gate keeps verify, checker, driver-model, and focused replay surfaces explicit" {
    const allocator = std.testing.allocator;

    const survey_note = try readRepoRelative(
        allocator,
        "Documentation/zigux/phase10-virtio-core-survey.md",
    );
    defer allocator.free(survey_note);

    const build_file = try readRepoRelative(allocator, "zigux/tests/phase10_build.zig");
    defer allocator.free(build_file);

    const shared_build_file = try readRepoRelative(allocator, "zigux/tests/build.zig");
    defer allocator.free(shared_build_file);

    const closure_manifest = try readRepoRelative(
        allocator,
        "zigux/tests/phase10_closure_manifest.json",
    );
    defer allocator.free(closure_manifest);
    const compact_closure_manifest = try stripAsciiWhitespace(allocator, closure_manifest);
    defer allocator.free(compact_closure_manifest);

    const core_file = try readRepoRelative(allocator, "drivers/virtio/virtio.zig");
    defer allocator.free(core_file);

    const core_replay = try readRepoRelative(allocator, "zigux/tests/phase10_virtio_core.zig");
    defer allocator.free(core_replay);

    const core_packet_checker = try readRepoRelative(
        allocator,
        "scripts/zigux/check-phase10-core-packet.py",
    );
    defer allocator.free(core_packet_checker);

    try expectContains(survey_note, "drivers/virtio/virtio_verify.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_core_reset_queue.zig");
    try expectContains(survey_note, "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig");
    try expectContains(survey_note, "driverModelSummary()");
    try expectContains(survey_note, "DriverModelStage");
    try expectContains(survey_note, "phase10-driver-id-review-gate");
    try expectContains(survey_note, "phase10-core-probe-remove-lifecycle");
    try expectContains(core_file, "pub const DriverModelStage = enum {");
    try expectContains(core_file, "pub const DriverModelSummary = struct {");
    try expectContains(core_file, "pub fn driverModelSummary(");
    try expectContains(
        core_replay,
        "test \"phase10 virtio core driver model replay keeps wrapper stages reviewable\" {",
    );
    try expectContains(build_file, "\"phase10-virtio-core-verify-tests\"");
    try expectContains(build_file, "\"phase10-virtio-core-reset-queue-tests\"");
    try expectContains(build_file, "\"phase10-virtio-core-interrupt-compound-ack-tests\"");
    try expectContains(build_file, "run_phase10_virtio_core_verify_tests.step");
    try expectContains(build_file, "run_phase10_virtio_core_reset_queue_tests.step");
    try expectContains(build_file, "run_phase10_virtio_core_interrupt_compound_ack_tests.step");
    try expectContains(shared_build_file, "\"phase10-virtio-core-survey\"");
    try expectContains(shared_build_file, "\"phase10_virtio_core_survey.zig\"");
    try expectContains(shared_build_file, "phase10_step.dependOn(&phase10_virtio_core_survey.step);");
    try expectContains(shared_build_file, "smoke_step.dependOn(&phase10_virtio_core_survey.step);");
    try expectContains(shared_build_file, "test_step.dependOn(&phase10_virtio_core_survey.step);");
    try expectContains(core_packet_checker, "\"lane_key\": \"P10-L01\",");
    try expectContains(core_packet_checker, "phase10-driver-id-helper");
    try expectContains(core_packet_checker, "phase10-driver-id-coverage-disposition-helper");
    try expectContains(core_packet_checker, "phase10-core-probe-remove-lifecycle");
    try expectContains(core_packet_checker, "\"drivers/virtio/virtio_driver_id.zig\"");
    try expectContains(core_packet_checker, "\"zigux/tests/phase10_virtio_driver_id.zig\"");
    try expectContains(core_packet_checker, "\"zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig\"");
    try expectContains(core_packet_checker, ".name = \"phase10-virtio-core-survey-tests\"");
    try expectContains(compact_closure_manifest, "\"drivers/virtio/virtio_verify.zig\"");
    try expectContains(compact_closure_manifest, "\"zigux/tests/phase10_virtio_core_reset_queue.zig\"");
    try expectContains(compact_closure_manifest, "\"zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig\"");
    try expectContains(compact_closure_manifest, "\"phase10-lifecycle-guard-bookkeeping-helper\"");
    try expectContains(compact_closure_manifest, "\"phase10-reset-replay-bookkeeping-helper\"");
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
    const compact_manifest = try stripAsciiWhitespace(allocator, manifest);
    defer allocator.free(compact_manifest);

    try expectContains(slice_note, "drivers/virtio/virtio_verify.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_core_reset_queue.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig");
    try expectContains(slice_note, "zigux/tests/phase10_virtio_core_survey.zig");
    try expectContains(compact_manifest, "\"lane_key\":\"P10-L01\"");
    try expectContains(compact_manifest, "\"id\":\"phase10-build-gate\"");
    try expectContains(compact_manifest, "\"id\":\"phase10-virtio-core-slice-note\"");
    try expectContains(compact_manifest, "\"id\":\"phase10-virtio-core-survey-note\"");
    try expectContains(compact_manifest, "\"id\":\"phase10-queue-shape-bookkeeping-helper\"");
    try expectContains(compact_manifest, "\"id\":\"phase10-config-generation-bookkeeping-helper\"");
    try expectContains(compact_manifest, "\"id\":\"phase10-interrupt-ack-bookkeeping-helper\"");
    try expectContains(compact_manifest, "\"id\":\"phase10-lifecycle-guard-bookkeeping-helper\"");
    try expectContains(compact_manifest, "\"id\":\"phase10-reset-replay-bookkeeping-helper\"");
    try expectContains(compact_manifest, "\"id\":\"phase10-core-dual-implementation-bridge\"");
    try expectContains(compact_manifest, "\"id\":\"phase10-core-probe-remove-lifecycle\"");
}
