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

fn readFixture(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(32 * 1024),
    );
}

test "phase14 workqueue packet keeps blocked-maintenance stay-in-C evidence explicit" {
    const manifest_json = try readFixture(
        std.testing.allocator,
        "zigux/tests/phase14_workqueue_bridge_manifest.json",
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P14-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("9e278f632d6d5097cb8cfc2dc61744ae105baa8c", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 15), manifest.gaps.len);

    var starter_landed_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_delayed_submission_alias_followup = false;
    var saw_delayed_timer_expiry_followup = false;
    var saw_delayed_requeue_governance = false;
    var saw_live_execution_blocker = false;

    for (manifest.gaps) |gap| {
        if (std.mem.eql(u8, gap.status, "starter_landed")) starter_landed_count += 1;
        if (std.mem.eql(u8, gap.status, "blocked_on_live_concurrency")) blocked_count += 1;

        if (std.mem.eql(u8, gap.id, "phase14-workqueue-delayed-submission-alias-followup")) {
            saw_delayed_submission_alias_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-delayed-timer-expiry-followup")) {
            saw_delayed_timer_expiry_followup = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-delayed-requeue-governance")) {
            saw_delayed_requeue_governance = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
        }
        if (std.mem.eql(u8, gap.id, "phase14-workqueue-live-execution-blocker")) {
            saw_live_execution_blocker = true;
            try std.testing.expectEqualStrings("blocked_on_live_concurrency", gap.status);
        }
    }

    try std.testing.expectEqual(@as(usize, 14), starter_landed_count);
    try std.testing.expectEqual(@as(usize, 1), blocked_count);
    try std.testing.expect(saw_delayed_submission_alias_followup);
    try std.testing.expect(saw_delayed_timer_expiry_followup);
    try std.testing.expect(saw_delayed_requeue_governance);
    try std.testing.expect(saw_live_execution_blocker);

    const survey_note = try readFixture(
        std.testing.allocator,
        "Documentation/zigux/phase14-workqueue-bridge-survey.md",
    );
    defer std.testing.allocator.free(survey_note);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_LANE_KEY=P14-L01") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_SLICE=workqueue-delayed-requeue-governance") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "timer-base ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "CPU hotplug behavior") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "hotplug-driven worker migration or flush-drain ownership") != null);

    const slice_note = try readFixture(
        std.testing.allocator,
        "Documentation/zigux/phase14-workqueue-bridge-slice.md",
    );
    defer std.testing.allocator.free(slice_note);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "thirteen-checkpoint concurrency audit outline") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "timer-base, CPU-affinity, and delayed-work rearm rules in C") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "does not claim live worker pools") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "hotplug transitions") != null);
}
