const std = @import("std");

const DeterminismEvidence = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    ordered_path_count: usize,
    ordered_paths_joined_with_newline_sha256: []const u8,
    ordered_paths: []const []const u8,
};

fn joinedOrderedPaths(
    allocator: std.mem.Allocator,
    ordered_paths: []const []const u8,
) ![]u8 {
    var joined = std.ArrayList(u8).empty;
    errdefer joined.deinit(allocator);

    for (ordered_paths) |path| {
        try joined.appendSlice(allocator, path);
        try joined.append(allocator, '\n');
    }

    return joined.toOwnedSlice(allocator);
}

test "phase12 libbpf snapshot determinism evidence fixes the exact ordered helper list" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const evidence_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(evidence_json);

    const parsed = try std.json.parseFromSlice(
        DeterminismEvidence,
        std.testing.allocator,
        evidence_json,
        .{},
    );
    defer parsed.deinit();

    const evidence = parsed.value;
    const expected_paths = [_][]const u8{
        "tools/lib/bpf/zigux_segments/type_names.zig",
        "tools/lib/bpf/zigux_segments/cpu_mask.zig",
        "tools/lib/bpf/zigux_segments/logging.zig",
        "tools/lib/bpf/zigux_segments/pin_path.zig",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    };

    try std.testing.expectEqualStrings("P12-L15", evidence.lane_key);
    try std.testing.expectEqualStrings("Phase 12", evidence.phase);
    try std.testing.expectEqualStrings("c0ae127363e3d4e5feeb36efb665a12ece3392c7", evidence.surveyed_commit);
    try std.testing.expectEqual(@as(usize, expected_paths.len), evidence.ordered_path_count);
    try std.testing.expectEqual(evidence.ordered_path_count, evidence.ordered_paths.len);

    for (expected_paths, 0..) |expected_path, index| {
        try std.testing.expectEqualStrings(expected_path, evidence.ordered_paths[index]);
    }

    const joined = try joinedOrderedPaths(std.testing.allocator, evidence.ordered_paths);
    defer std.testing.allocator.free(joined);

    var digest: [32]u8 = undefined;
    std.crypto.hash.sha2.Sha256.hash(joined, &digest, .{});

    var expected_digest: [32]u8 = undefined;
    _ = try std.fmt.hexToBytes(&expected_digest, evidence.ordered_paths_joined_with_newline_sha256);
    try std.testing.expectEqualSlices(u8, &expected_digest, &digest);
}
