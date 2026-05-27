const std = @import("std");
const cpu_mask = @import("cpu_mask");
const bpf_type_names = @import("bpf_type_names");
const logging = @import("logging");
const pin_path = @import("pin_path");
const perf_buffer_poll = @import("perf_buffer_poll");
const online_cpu_routing = @import("online_cpu_routing");

const SnapshotFile = struct {
    path: []const u8,
    blob_sha: []const u8,
};

const SnapshotChecker = struct {
    path: []const u8,
    blob_sha: []const u8,
    self_test_case_count: usize,
};

const SnapshotNoteBlob = struct {
    path: []const u8,
    blob_sha: []const u8,
};

const SnapshotVerificationEvidence = struct {
    readback_mode: []const u8,
    checker: SnapshotChecker,
    current_note_blobs: []const SnapshotNoteBlob,
};

const SnapshotFixture = struct {
    lane_key: []const u8,
    phase: []const u8,
    tracked_file_count: usize,
    tracked_paths: []const []const u8,
    supporting_notes: []const []const u8,
    files: []const SnapshotFile,
    verification_evidence: SnapshotVerificationEvidence,
};

const DeterminismHelperBlob = struct {
    path: []const u8,
    blob_sha: []const u8,
};

const DeterminismVerificationEvidence = struct {
    readback_mode: []const u8,
    checker: SnapshotChecker,
    current_helper_blob: DeterminismHelperBlob,
};

const DeterminismFixture = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    tracked_file_count: usize,
    tracked_paths: []const []const u8,
    files: []const SnapshotFile,
    verification_evidence: DeterminismVerificationEvidence,
};

fn readFileAlloc(path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(limit),
    );
}

fn pathExists(path: []const u8) !bool {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    std.Io.Dir.cwd().access(io_instance.io(), path, .{}) catch |err| switch (err) {
        error.FileNotFound => return false,
        else => return err,
    };
    return true;
}

fn isHexSha(value: []const u8) bool {
    if (value.len != 40) return false;
    for (value) |byte| {
        if (!std.ascii.isHex(byte) or std.ascii.isUpper(byte)) return false;
    }
    return true;
}

fn expectExactPaths(actual: []const []const u8, expected: []const []const u8) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (actual, expected) |actual_path, expected_path| {
        try std.testing.expectEqualStrings(expected_path, actual_path);
    }
}

test "phase12 libbpf reviewability gate keeps the current snapshot anchor exact" {
    const fixture_json = try readFileAlloc("zigux/tests/fixtures/phase12_libbpf_snapshot.json", 16 * 1024);
    defer std.testing.allocator.free(fixture_json);

    const parsed = try std.json.parseFromSlice(SnapshotFixture, std.testing.allocator, fixture_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const fixture = parsed.value;
    const expected_paths = [_][]const u8{
        "Documentation/zigux/phase12-libbpf-segment-survey.md",
        "Documentation/zigux/phase12-libbpf-verify-shard-note.md",
        "Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md",
        "Documentation/zigux/phase12-release-coordination-matrix.md",
    };

    try std.testing.expectEqualStrings("P12-L16", fixture.lane_key);
    try std.testing.expectEqualStrings("Phase 12", fixture.phase);
    try std.testing.expectEqual(expected_paths.len, fixture.tracked_file_count);
    try expectExactPaths(fixture.tracked_paths, &expected_paths);
    try expectExactPaths(fixture.supporting_notes, &expected_paths);
    try std.testing.expectEqual(expected_paths.len, fixture.files.len);
    try std.testing.expectEqual(expected_paths.len, fixture.verification_evidence.current_note_blobs.len);
    try std.testing.expectEqualStrings("github-contents-readback", fixture.verification_evidence.readback_mode);
    try std.testing.expectEqualStrings(
        "scripts/zigux/check-phase12-libbpf-snapshot.py",
        fixture.verification_evidence.checker.path,
    );
    try std.testing.expectEqualStrings(
        "277554397ab1a236c71f1dac9061ffe4cfbeaf67",
        fixture.verification_evidence.checker.blob_sha,
    );
    try std.testing.expectEqual(@as(usize, 30), fixture.verification_evidence.checker.self_test_case_count);

    for (fixture.files, fixture.verification_evidence.current_note_blobs, expected_paths) |file_entry, note_blob, expected_path| {
        try std.testing.expectEqualStrings(expected_path, file_entry.path);
        try std.testing.expectEqualStrings(expected_path, note_blob.path);
        try std.testing.expect(isHexSha(file_entry.blob_sha));
        try std.testing.expect(isHexSha(note_blob.blob_sha));
    }
}

test "phase12 libbpf reviewability gate keeps the helper-local determinism fixture exact" {
    const fixture_json = try readFileAlloc("zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json", 16 * 1024);
    defer std.testing.allocator.free(fixture_json);

    const parsed = try std.json.parseFromSlice(DeterminismFixture, std.testing.allocator, fixture_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const fixture = parsed.value;
    const expected_path = "tools/lib/bpf/zigux_segments/pin_path.zig";

    try std.testing.expectEqualStrings("P12-L17", fixture.lane_key);
    try std.testing.expectEqualStrings("Phase 12", fixture.phase);
    try std.testing.expect(isHexSha(fixture.surveyed_commit));
    try std.testing.expectEqual(@as(usize, 1), fixture.tracked_file_count);
    try expectExactPaths(fixture.tracked_paths, &[_][]const u8{expected_path});
    try std.testing.expectEqual(@as(usize, 1), fixture.files.len);
    try std.testing.expectEqualStrings(expected_path, fixture.files[0].path);
    try std.testing.expect(isHexSha(fixture.files[0].blob_sha));
    try std.testing.expectEqualStrings("github-contents-readback", fixture.verification_evidence.readback_mode);
    try std.testing.expectEqualStrings(
        "scripts/zigux/check-phase12-libbpf-snapshot.py",
        fixture.verification_evidence.checker.path,
    );
    try std.testing.expectEqualStrings(
        "277554397ab1a236c71f1dac9061ffe4cfbeaf67",
        fixture.verification_evidence.checker.blob_sha,
    );
    try std.testing.expectEqual(@as(usize, 30), fixture.verification_evidence.checker.self_test_case_count);
    try std.testing.expectEqualStrings(expected_path, fixture.verification_evidence.current_helper_blob.path);
    try std.testing.expect(isHexSha(fixture.verification_evidence.current_helper_blob.blob_sha));
    try std.testing.expectEqualStrings(
        fixture.files[0].path,
        fixture.verification_evidence.current_helper_blob.path,
    );
    try std.testing.expectEqualStrings(
        fixture.files[0].blob_sha,
        fixture.verification_evidence.current_helper_blob.blob_sha,
    );
}

test "phase12 libbpf reviewability gate keeps the parked replay boundaries and note-owned anchors explicit" {
    const survey_note = try readFileAlloc("Documentation/zigux/phase12-libbpf-segment-survey.md", 24 * 1024);
    defer std.testing.allocator.free(survey_note);
    const verify_note = try readFileAlloc("Documentation/zigux/phase12-libbpf-verify-shard-note.md", 16 * 1024);
    defer std.testing.allocator.free(verify_note);
    const heavy_note = try readFileAlloc("Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md", 24 * 1024);
    defer std.testing.allocator.free(heavy_note);

    try std.testing.expect(try pathExists("Documentation/zigux/phase12-libbpf-segment-survey.md"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-libbpf-verify-shard-note.md"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md"));
    try std.testing.expect(try pathExists("Documentation/zigux/phase12-release-coordination-matrix.md"));
    try std.testing.expect(try pathExists("zigux/tests/fixtures/phase12_libbpf_snapshot.json"));
    try std.testing.expect(try pathExists("zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json"));

    try std.testing.expect(try pathExists("tools/lib/bpf/zigux_segments/cpu_mask.zig"));
    try std.testing.expect(try pathExists("tools/lib/bpf/zigux_segments/logging.zig"));
    try std.testing.expect(try pathExists("tools/lib/bpf/zigux_segments/pin_path.zig"));
    try std.testing.expect(try pathExists("tools/lib/bpf/zigux_segments/type_names.zig"));
    try std.testing.expect(try pathExists("tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"));
    try std.testing.expect(try pathExists("tools/lib/bpf/zigux_segments/online_cpu_routing.zig"));
    try std.testing.expect(try pathExists("tools/lib/bpf/zigux_segments/manifest.json"));

    try std.testing.expect(!(try pathExists("zigux/tests/phase12_libbpf_manifest.json")));
    try std.testing.expect(!(try pathExists("zigux/tests/phase12_libbpf_segments.zig")));
    try std.testing.expect(!(try pathExists("tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig")));

    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12_libbpf_*") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12_libbpf_snapshot.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase12_libbpf_reviewability.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, verify_note, "phase12_libbpf_*") != null);
    try std.testing.expect(std.mem.indexOf(u8, verify_note, "file_path_handle_bridge.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, heavy_note, "phase12_libbpf_snapshot_determinism.json") != null);
}

test "phase12 libbpf reviewability gate still compiles the surviving helper-first footing" {
    var parsed_mask = try cpu_mask.parseCpuMaskString(std.testing.allocator, "0-1,3");
    defer parsed_mask.deinit(std.testing.allocator);

    var version_buffer: [16]u8 = undefined;
    var pin_path_buffer: [64]u8 = undefined;

    try std.testing.expectEqual(@as(usize, 3), cpu_mask.countPossibleCpus(parsed_mask.values));
    try std.testing.expectEqual(@as(usize, 2), cpu_mask.derivePerfBufferAutoCpuCount(3, 2));
    try std.testing.expectEqualStrings("v1.7", try logging.libbpfVersionString(version_buffer[0..]));
    try std.testing.expectEqualStrings("xdp", bpf_type_names.libbpfBpfAttachTypeStr(37).?);
    try std.testing.expectEqualStrings("ringbuf", bpf_type_names.libbpfBpfMapTypeStr(27).?);
    try std.testing.expectEqualStrings(
        "/sys/fs/bpf/demo_map",
        try pin_path.buildValidatedSanitizedMapPinPath(&pin_path_buffer, null, "demo.map"),
    );

    const poll_result = try perf_buffer_poll.summarizePollExecutionResultFromWaitResult(
        12,
        2,
        &.{
            .{ .ready = true },
            .{ .ready = true },
        },
        &.{
            .{ .records_processed = 1 },
            .{ .records_processed = 2 },
        },
    );
    try std.testing.expectEqual(perf_buffer_poll.PollReturnDisposition.ready_count, poll_result.disposition);
    try std.testing.expectEqual(@as(i32, 2), poll_result.return_value);
    try std.testing.expectEqual(@as(usize, 3), poll_result.execution.processed_record_count);

    const route_summary = online_cpu_routing.summarizeOnlineCpuRouting(
        &.{ false, true, false, true },
        0,
        &.{ 11, 17 },
    );
    try std.testing.expectEqual(online_cpu_routing.OnlineCpuRoutingDisposition.complete, route_summary.disposition);
    try std.testing.expectEqual(@as(usize, 2), route_summary.routed_cpu_count);
    try std.testing.expectEqual(@as(?usize, 1), route_summary.first_routed_cpu_index);
}
