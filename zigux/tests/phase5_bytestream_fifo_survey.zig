const std = @import("std");

const ExactCheck = struct {
    id: []const u8,
    kind: []const u8,
    expected: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    sample_path: []const u8,
    validation_entrypoint: []const u8,
    review_prompts: []const []const u8,
    exact_checks: []const ExactCheck,
    non_goals: []const []const u8,
};

fn readText(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn isLowerHexCommitSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isDigit(byte) and (byte < 'a' or byte > 'f')) return false;
    }
    return true;
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactCheck(manifest: Manifest, id: []const u8, expected_marker: []const u8) !void {
    for (manifest.exact_checks) |check| {
        if (std.mem.eql(u8, check.id, id)) {
            try expectContains(check.expected, expected_marker);
            return;
        }
    }
    return error.MissingExpectedCheck;
}

test "phase5 bytestream manifest matches the current bounded packet" {
    const manifest_json = try readText("zigux/tests/phase5_bytestream_fifo_manifest.json", 32 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P5-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expect(isLowerHexCommitSha(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("samples/kfifo/bytestream-example.c", manifest.anchor);
    try std.testing.expectEqualStrings("samples/zigux/bytestream_fifo.zig", manifest.sample_path);
    try expectContains(manifest.validation_entrypoint, "phase5_build.zig");
    try std.testing.expectEqual(@as(usize, 8), manifest.review_prompts.len);
    try std.testing.expectEqual(@as(usize, 17), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.non_goals.len);

    try expectExactCheck(manifest, "transfer-count-contract", "initial string copy count is 5");
    try expectExactCheck(manifest, "preview-truncation-boundary", "stage_before_replay and stage_after_replay stay initialized");
    try expectExactCheck(manifest, "anchor-preview-truncation-contract", "preview_total_visible is 32");
    try expectExactCheck(manifest, "remaining-capacity", "available() reports 32 at cold");
    try expectExactCheck(manifest, "occupancy-summary-boundary", "wrapped_window=true");
    try expectExactCheck(manifest, "wrapped-storage-window-boundary", "visibleSpanSummary() keeps the bounded split cues explicit");
    try expectExactCheck(manifest, "writable-span-boundary", "tail_index=17");
    try expectExactCheck(manifest, "short-drain-prefix", "\"hel\"");
    try expectExactCheck(manifest, "lifecycle-boundary", "requires init before replay");
}

test "phase5 bytestream survey note records the current split-readback packet" {
    const note = try readText("Documentation/zigux/phase5-kfifo-sample-survey.md", 96 * 1024);
    defer std.testing.allocator.free(note);

    const required_markers = [_][]const u8{
        "PHASE5_STATUS=verified-split-readback-packet",
        "PHASE5_SLICE=kfifo-reference-sample-readback",
        "PHASE5_LANE_KEY=P5-L01",
        "samples/kfifo/bytestream-example.c",
        "authenticated contents readback for `zigux/tests/phase5_bytestream_fifo_manifest.json`",
        "public-tree blob readback for `zigux/tests/phase5_bytestream_fifo_survey.zig`",
        "public-tree blob readback for `zigux/tests/phase5_build.zig`",
        "focused sample-local replay rerun on 2026-05-16 passed formatting and `8/8` in-file tests",
        "preserved broader snapshot still recorded `5/5` build steps and `8/8` tests",
        "writableSpanSummary() reports `tail_index = 0`",
        "tail_index = 17",
        "tail_index = 4",
        "{ 31, 1 }",
        "{28,4}",
        "/workspace/agent_files",
    };

    for (required_markers[0 .. required_markers.len - 1]) |needle| try expectContains(note, needle);
    try std.testing.expect(std.mem.indexOf(u8, note, required_markers[required_markers.len - 1]) == null);
}

test "phase5 bytestream survey note keeps the queue-shape and helper boundaries explicit" {
    const note = try readText("Documentation/zigux/phase5-kfifo-sample-survey.md", 96 * 1024);
    defer std.testing.allocator.free(note);

    const markers = [_][]const u8{
        "draining a three-byte destination from the queued string `\"hello\"` yields `\"hel\"`",
        "leaves the remaining prefix `\"lo\"` queued in order",
        "runPreviewBoundaryReplay() still yields snapshot prefix `{ 2, 3, 4, 5 }`",
        "runWrappedPreviewReplay() still yields drained prefix `\"hell\"`",
        "preview truncation boundary plus preview-boundary replay also held",
        "`available()` reports `32` at cold, initialized, replay-complete, reset, and exited boundaries",
        "`usesWrappedStorageWindow()` stays `false` at cold, initialized, reset, preview-boundary, replay-complete, and full-capacity states",
    };

    for (markers) |needle| try expectContains(note, needle);
}

test "phase5 build file still wires the bytestream sample and survey routes" {
    const build_zig = try readText("zigux/tests/phase5_build.zig", 16 * 1024);
    defer std.testing.allocator.free(build_zig);

    const required_markers = [_][]const u8{
        "../../samples/zigux/bytestream_fifo.zig",
        "phase5_bytestream_fifo.zig",
        "phase5_bytestream_fifo_survey.zig",
        "phase5-bytestream-fifo-tests",
        "phase5-bytestream-fifo-survey-tests",
        "run_phase5_bytestream_fifo_tests.step",
        "run_phase5_bytestream_fifo_survey_tests.step",
    };

    for (required_markers) |needle| try expectContains(build_zig, needle);
}
