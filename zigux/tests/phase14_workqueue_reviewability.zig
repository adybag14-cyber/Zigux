const std = @import("std");

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const MaintenanceHandoff = struct {
    current_lane_posture: []const u8,
    replay_before_trusting: []const []const u8,
    reopen_conditions: []const []const u8,
    next_future_target: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    maintenance_handoff: MaintenanceHandoff,
    gaps: []const Gap,
};

fn expectGapStatus(manifest: Manifest, id: []const u8, status: []const u8) !void {
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) {
            try std.testing.expectEqualStrings(status, gap.status);
            return;
        }
    }

    return error.MissingExpectedGap;
}

test "phase14 workqueue reviewability packet stays wired to the blocked-maintenance packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_workqueue_bridge_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P14-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("9b98d3b9c812840bf279508030be0b8de093736c", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.anchor);
    try std.testing.expectEqualStrings("blocked_maintenance", manifest.maintenance_handoff.current_lane_posture);
    try std.testing.expectEqual(@as(usize, 3), manifest.maintenance_handoff.replay_before_trusting.len);
    try std.testing.expectEqualStrings(
        "zig test zigux/tests/phase14_workqueue_reviewability.zig",
        manifest.maintenance_handoff.replay_before_trusting[0],
    );
    try std.testing.expectEqualStrings(
        "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
        manifest.maintenance_handoff.replay_before_trusting[1],
    );
    try std.testing.expectEqualStrings("make -C zigux phase14", manifest.maintenance_handoff.replay_before_trusting[2]);
    try std.testing.expect(std.mem.indexOf(u8, manifest.maintenance_handoff.next_future_target, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.maintenance_handoff.next_future_target, "workqueue-local") != null);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.status, "starter_landed")) starter_landed_count += 1;
        if (std.mem.eql(u8, gap.status, "blocked_on_live_concurrency")) blocked_count += 1;
    }

    try std.testing.expectEqual(@as(usize, 17), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try expectGapStatus(manifest, "phase14-workqueue-delayed-timer-expiry-followup", "starter_landed");
    try expectGapStatus(manifest, "phase14-workqueue-delayed-requeue-governance", "starter_landed");
    try expectGapStatus(manifest, "phase14-workqueue-flush-drain-governance", "starter_landed");
    try expectGapStatus(manifest, "phase14-workqueue-rescuer-mayday-governance", "starter_landed");
    try expectGapStatus(manifest, "phase14-workqueue-scheduler-visible-worker-state-refinement", "starter_landed");
    try expectGapStatus(manifest, "phase14-workqueue-live-execution-blocker", "blocked_on_live_concurrency");

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "shared Phase 14 smoke packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "phase14_workqueue_reviewability.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "same study-only stay-in-C posture") != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        review_checklist,
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` kept explicit as the two boundary-study-only anchors",
    ) != null);

    const phase14_build = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_build.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(phase14_build);
    try std.testing.expect(std.mem.indexOf(
        u8,
        phase14_build,
        ".root_source_file = b.path(\"phase14_workqueue_reviewability.zig\")",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        phase14_build,
        ".name = \"phase14-workqueue-reviewability-tests\"",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        phase14_build,
        "test_step.dependOn(&run_phase14_workqueue_reviewability_tests.step);",
    ) != null);
}
