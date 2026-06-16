const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_MMIO_APPLY_OBSERVATION_PACKET_SELF_TEST=pass";

const FILES = [_][]const u8{
    "Documentation/zigux/phase10-virtio-mmio-survey.md",
    "Documentation/zigux/phase10-closure-evidence.md",
    "drivers/virtio/virtio_mmio_apply_observation.zig",
    "zigux/tests/phase10_virtio_mmio_manifest.json",
    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
    "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig",
    "zigux/tests/phase10_virtio_mmio_survey.zig",
    "zigux/tests/phase10_build.zig",
};

const SURVEY_NOTE_MARKERS = [_][]const u8{
    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
    "zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig",
    "changed-byte coverage, no-op planning, and stale-plan rejection explicit",
    "zig build test --build-file zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig --summary all",
    "The shared gate should still be read as helper-local MMIO coverage plus one direct lab replay, one wrapper-facing verify replay, and one survey replay rather than a broader transport-backed replay.",
};

const CLOSURE_NOTE_MARKERS = [_][]const u8{
    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig",
    "zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig, `zigux/tests/phase10_virtio_mmio_survey.zig`",
    "phase10-mmio-config-write-apply-observation-helper",
};

const HELPER_MARKERS = [_][]const u8{
    "pub const ConfigWriteApplyObservationSummary = struct {",
    "pub fn summarizeConfigWriteApplyObservation(",
    "pub fn touchedByteCount(summary: ConfigWriteApplyObservationSummary) u3 {",
    "pub fn changedByteCount(summary: ConfigWriteApplyObservationSummary) u3 {",
    "pub fn changedBytesStayWithinTouchedMask(summary: ConfigWriteApplyObservationSummary) bool {",
    "pub fn appliesByteChanges(summary: ConfigWriteApplyObservationSummary) bool {",
};

const MANIFEST_MARKERS = [_][]const u8{
    "\"id\": \"phase10-mmio-config-write-apply-observation-helper\"",
    "\"id\": \"phase10-mmio-config-write-apply-observation-replay\"",
    "\"zigux_destination\": \"zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig\"",
};

const REPLAY_MARKERS = [_][]const u8{
    "test \"phase10 virtio mmio apply-observation replay keeps changed bytes explicit\" {",
    "const summary = try apply_observation.summarizeConfigWriteApplyObservation(&device);",
    "try std.testing.expectEqual(@as(u4, 0b1111), summary.touched_byte_mask);",
    "try std.testing.expectEqual(@as(u3, 2), apply_observation.changedByteCount(summary));",
    "test \"phase10 virtio mmio apply-observation replay keeps no-op and stale plans distinct\" {",
    "try std.testing.expectError(",
    "error.ConfigWritePlanUnavailable,",
};

const BUILD_SHARD_MARKERS = [_][]const u8{
    "../../drivers/virtio/virtio_mmio_apply_observation.zig",
    "b.path(\"phase10_virtio_mmio_apply_observation_replay.zig\")",
    ".name = \"phase10-virtio-mmio-apply-observation-replay\"",
    "\"phase10-virtio-mmio-apply-observation-replay\"",
    "Run the bounded Phase 10 virtio MMIO apply-observation replay",
};

const SURVEY_GATE_MARKERS = [_][]const u8{
    "try expectContains(survey_note, \"zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig\");",
    "try expectContains(survey_note, \"zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig\");",
    "try expectContains(",
    "        \"zig build test --build-file zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig --summary all\",",
    "    const replay_build_file = try readRepoRelative(",
    "        \"zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig\",",
    "    try expectContains(replay_build_file, \"phase10_virtio_mmio_apply_observation_replay.zig\");",
    "    try expectContains(replay_build_file, \"\\\"phase10-virtio-mmio-apply-observation-replay\\\"\");",
};

const SHARED_BUILD_MARKERS = [_][]const u8{
    "const virtio_mmio_apply_observation_module = b.createModule(.{",
    ".name = \"phase10-virtio-mmio-apply-observation-tests\"",
    "const run_phase10_virtio_mmio_apply_observation_tests = b.addRunArtifact(",
    "        \"phase10-virtio-mmio-apply-observation-tests\",",
    "phase10_virtio_mmio_apply_observation_step.dependOn(",
    "test_step.dependOn(&run_phase10_virtio_mmio_apply_observation_tests.step);",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (FILES) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CLOSURE_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (HELPER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REPLAY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (BUILD_SHARD_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_GATE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SHARED_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
