const std = @import("std");

const Gap = struct {
    id: []const u8,
    status: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
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

test "phase14 workqueue checklist remains aligned with the current study-only shard" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_workqueue_bridge_manifest.json",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P14-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("9b98d3b9c812840bf279508030be0b8de093736c", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("kernel/workqueue.c", manifest.anchor);
    try expectGapStatus(manifest, "phase14-workqueue-scheduler-visible-worker-state-refinement", "starter_landed");
    try expectGapStatus(manifest, "phase14-workqueue-live-execution-blocker", "blocked_on_live_concurrency");

    const survey_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-workqueue-bridge-survey.md",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(survey_note);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_STATUS=blocked_maintenance") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "PHASE14_LANE_KEY=P14-L04") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "phase14-workqueue-scheduler-visible-worker-state-refinement") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "zig test zigux/tests/phase14_workqueue_reviewability.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "boundary-map-only submission routing through `queue_work_on()` and `__queue_work()`") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_note, "delayed timer handoff back into `__queue_work()`") != null);

    const traceability_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-core-boundary-traceability.md",
        std.testing.allocator,
        .limited(24 * 1024),
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
    try std.testing.expect(std.mem.indexOf(
        u8,
        smoke_survey,
        "workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-L04`, surveyed commit `9b98d3b9c812840bf279508030be0b8de093736c`, ready-next `none currently recorded`, blocked `phase14-workqueue-live-execution-blocker`",
    ) != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_survey, "`phase14-workqueue-reviewability-tests` -> `phase14_workqueue_reviewability.zig` -> `full_bundle_only`") != null);

    const review_checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(review_checklist);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "shared Phase 14 smoke packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, review_checklist, "`scripts/zigux/validate-phase14.py` framed as blob-readable mixed-source evidence") != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        review_checklist,
        "`kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` explicit as the directly readable workqueue reviewability shard",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        review_checklist,
        "`zigux/Makefile` framed as a readable non-owner surface whose live body now exposes shipped Phase 2 toolchain and kbuild routes together with the bounded Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 route families while still omitting all `phase14-*` targets",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        review_checklist,
        "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` explicit as study-only anchors plus `net/core/skbuff.c` and `kernel/rcu/tree.c` as freeze-in-C anchors",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        review_checklist,
        "`scripts/zigux/check-phase14-release-boundary-exact-counts.py`, `zigux/tests/phase14_build.zig`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/tests/phase14_end_to_end_smoke_survey.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_ring_buffer_survey.zig`, `zigux/tests/phase14_rcu_tree_survey.zig`, and `net/core/skbuff_bridge.zig` framed as repo-reality gaps rather than shipped current-`master` proof",
    ) != null);
}
