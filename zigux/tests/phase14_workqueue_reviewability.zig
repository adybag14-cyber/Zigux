const std = @import("std");
const workqueue_bridge = @import("workqueue_bridge");

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
    productization_posture: []const u8,
    productization_exact_checks: []const []const u8,
    productization_behavior_note: []const u8,
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

const expected_productization_exact_checks = [_][]const u8{
    "python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "python3 scripts/zigux/check-phase14-shared-smoke-route.py",
    "python3 scripts/zigux/check-phase14-tests-readme-smoke-summary.py --self-test",
    "python3 scripts/zigux/check-phase14-tests-readme-smoke-summary.py",
    "python3 scripts/zigux/validate-phase14.py --self-test",
    "python3 scripts/zigux/validate-phase14.py",
    "python3 scripts/zigux/check-phase14-rollback-threshold-sequencing.py --self-test",
    "python3 scripts/zigux/check-phase14-rollback-threshold-sequencing.py",
    "python3 scripts/zigux/check-phase14-workqueue-study-only-guardrail.py --self-test",
    "python3 scripts/zigux/check-phase14-workqueue-study-only-guardrail.py",
    "python3 scripts/zigux/check-phase14-release-boundary-exact-counts.py --self-test",
    "python3 scripts/zigux/check-phase14-release-boundary-exact-counts.py",
    "make -C zigux phase14-validate",
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

fn expectBridgeRereadSurfaces(surface: []const u8, handoff: workqueue_bridge.MaintenanceHandoff) !void {
    for (handoff.reread_surfaces) |path| {
        try std.testing.expect(std.mem.indexOf(u8, surface, path) != null);
    }
}

fn expectExactStringList(actual: []const []const u8, expected: []const []const u8) !void {
    try std.testing.expectEqual(expected.len, actual.len);
    for (expected, 0..) |item, index| {
        try std.testing.expectEqualStrings(item, actual[index]);
    }
}

fn expectListExcludes(list: []const []const u8, needle: []const u8) !void {
    for (list) |item| {
        try std.testing.expect(!std.mem.eql(u8, item, needle));
    }
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

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    const bridge_handoff = workqueue_bridge.WorkqueueBridgeLab.maintenanceHandoff();
    try std.testing.expectEqualStrings("P14-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("9b98d3b9c812840bf279508030be0b8de093736c", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.anchor);
    try std.testing.expectEqualStrings("blocked_maintenance", manifest.maintenance_handoff.current_lane_posture);
    try std.testing.expectEqualStrings(bridge_handoff.posture, manifest.maintenance_handoff.current_lane_posture);
    try std.testing.expectEqual(@as(usize, 1), manifest.maintenance_handoff.replay_before_trusting.len);
    try std.testing.expectEqualStrings(
        "zig test zigux/tests/phase14_workqueue_reviewability.zig",
        manifest.maintenance_handoff.replay_before_trusting[0],
    );
    try std.testing.expectEqualStrings("shared_packet_local_only", manifest.maintenance_handoff.productization_posture);
    try expectExactStringList(
        manifest.maintenance_handoff.productization_exact_checks,
        expected_productization_exact_checks[0..],
    );
    try std.testing.expectEqualStrings(
        "These checks verify shared packet-local productization behavior around the current phase14-validate route and its reminder surfaces. They do not replace the direct workqueue reviewability replay as the bridge-local trust gate.",
        manifest.maintenance_handoff.productization_behavior_note,
    );
    try expectListExcludes(
        manifest.maintenance_handoff.productization_exact_checks,
        manifest.maintenance_handoff.replay_before_trusting[0],
    );
    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "\"preexisting_phase14_build_present\": true") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "zig build test --build-file zigux/tests/phase14_build.zig --summary all") == null);
    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "\"make -C zigux phase14-smoke\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, manifest_json, "\"make -C zigux phase14-test\"") == null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.maintenance_handoff.next_future_target, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.maintenance_handoff.next_future_target, "workqueue-local") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.maintenance_handoff.next_future_target, "phase14_build") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.maintenance_handoff.next_future_target, "shared-packet evidence rather than a bridge-local trust promotion signal") != null);

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

    const slice_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-workqueue-bridge-slice.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(slice_note);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "PHASE14_LANE_KEY=P14-L04") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "PHASE14_SLICE=phase14-workqueue-scheduler-visible-worker-state-refinement") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "zigux/tests/phase14_workqueue_reviewability.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "blocked maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, slice_note, "shared-packet evidence rather than a bridge-local trust promotion signal") != null);
    try expectBridgeRereadSurfaces(slice_note, bridge_handoff);

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-workqueue-bridge-survey.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(survey_note);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_STATUS=blocked_maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_LANE_KEY=P14-L04") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_SURVEYED_COMMIT=9b98d3b9c812840bf279508030be0b8de093736c") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase14-workqueue-scheduler-visible-worker-state-refinement") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared Phase 14 smoke packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase14_workqueue_reviewability.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Documentation/zigux/phase14-release-boundary-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Documentation/zigux/phase14-productization-gap-survey.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Documentation/zigux/phase14-shared-smoke-current-master-gap.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Documentation/zigux/phase14-attached-toolchain-guidance-gap.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "Documentation/zigux/phase15-study-only-anchor-accounting.md") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "scripts/zigux/check-phase14-shared-smoke-route.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "scripts/zigux/check-phase14-release-boundary-exact-counts.py") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zigux/Makefile") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "boundary-map-only submission routing through `queue_work_on()` and `__queue_work()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "boundary-map-only allocation and attribute shaping through `__alloc_workqueue()` and `devm_alloc_workqueue()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "runtime `max_active` retuning") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "scheduler-visible worker-state transitions") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig test zigux/tests/phase14_workqueue_reviewability.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "make -C zigux phase14-validate") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared packet-local validation rather than direct bridge-local trust gates") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "missing `phase14-smoke`, `phase14-test`, and `phase14` wrappers") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "shared-packet evidence rather than a bridge-local trust promotion signal") != null);
    try expectBridgeRereadSurfaces(survey_note, bridge_handoff);

    const traceability_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-core-boundary-traceability.md",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(traceability_note);
    try std.testing.expect(std.mem.indexOf(u8, traceability_note, "`kernel/workqueue.c`: `Study / Boundary Only`") != null);
    try std.testing.expect(std.mem.indexOf(u8, traceability_note, "`kernel/workqueue_bridge.zig` remains review-only boundary evidence") != null);
    try std.testing.expect(std.mem.indexOf(u8, traceability_note, "delayed-work requeue ownership") != null);

    const smoke_survey = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(smoke_survey);
    try std.testing.expect(std.mem.indexOf(u8, smoke_survey, "`zigux/tests/phase14_workqueue_reviewability.zig`") != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        smoke_survey,
        "workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-L04`, surveyed commit `9b98d3b9c812840bf279508030be0b8de093736c`, current slice `phase14-workqueue-scheduler-visible-worker-state-refinement`, posture `blocked_maintenance`, blocked `phase14-workqueue-live-execution-blocker`",
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_survey, "boundary-map-and-reviewability foothold") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_survey, "`make -C zigux phase14-validate`") != null);

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
}
