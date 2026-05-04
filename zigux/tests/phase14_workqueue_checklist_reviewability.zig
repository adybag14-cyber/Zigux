const std = @import("std");

const Gap = struct {
    id: []const u8,
    status: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    gaps: []const Gap,
};

test "phase14 workqueue checklist stays aligned with blocked maintenance posture" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_workqueue_bridge_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P14-Y05", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("02264a3240cd30ce45c9a932047a0204b7ab5029", manifest.surveyed_commit);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_delayed_timer_handoff = false;
    var saw_live_execution_blocker = false;

    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.status, "starter_landed")) starter_landed_count += 1;
        if (std.mem.eql(u8, gap.status, "blocked_on_live_concurrency")) blocked_count += 1;

        if (std.mem.eql(u8, gap.id, "phase14-workqueue-delayed-timer-handoff-followup")) {
            saw_delayed_timer_handoff = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }

        if (std.mem.eql(u8, gap.id, "phase14-workqueue-live-execution-blocker")) {
            saw_live_execution_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_live_concurrency", gap.status);
        }
    }

    try std.testing.expectEqual(@as(usize, 17), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_delayed_timer_handoff);
    try std.testing.expect(saw_live_execution_blocker);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-workqueue-bridge-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_LANE_KEY=P14-Y05") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_SLICE=workqueue-blocked-maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "delayed_work_timer_fn()") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Leave this lane in blocked maintenance") != null);

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-workqueue-bridge-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice_note);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "eighteen-checkpoint concurrency audit outline") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "timer-base") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "CPU-affinity") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "requeue ownership") != null);

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "Phase 14 workqueue bridge lane") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "kernel/workqueue_bridge.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "zigux/tests/phase14_workqueue_bridge_manifest.json") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "Documentation/zigux/phase14-workqueue-bridge-survey.md") != null);
}
