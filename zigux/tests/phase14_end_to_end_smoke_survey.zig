const std = @import("std");

const SurveySummary = struct {
    phase14_build_has_shared_smoke_step: bool,
    phase14_build_has_smoke_shard_step: bool,
    phase14_make_target_present: bool,
    phase14_make_smoke_target_present: bool,
    workflow_runs_phase14_build: bool,
    workflow_runs_phase14_smoke_shard: bool,
    review_checklist_has_phase14_smoke_prompt: bool,
    freeze_map_lists_workqueue_c: bool,
    freeze_map_lists_skbuff_c: bool,
    freeze_map_lists_ring_buffer_c: bool,
    freeze_map_lists_tree_c: bool,
};

const AnchorPacket = struct {
    lane_key: []const u8,
    anchor: []const u8,
    surveyed_commit: []const u8,
    manifest_path: []const u8,
    survey_note_path: []const u8,
    ready_next_gap: []const u8,
    blocked_gap: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    shared_smoke_surfaces: []const []const u8,
    anchor_packets: []const AnchorPacket,
    smoke_commands: []const []const u8,
    smoke_shard_commands: []const []const u8,
    survey_summary: SurveySummary,
};

const AnchorGap = struct {
    id: []const u8,
    status: []const u8,
};

const AnchorManifest = struct {
    lane_key: []const u8,
    anchor: []const u8,
    surveyed_commit: []const u8,
    gaps: []const AnchorGap,
};

fn hasGapWithStatus(gaps: []const AnchorGap, gap_id: []const u8, status: []const u8) bool {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, gap_id) and std.mem.eql(u8, gap.status, status)) {
            return true;
        }
    }
    return false;
}

test "phase14 shared smoke manifest records the current evidence bundle" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_end_to_end_smoke_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P14-L03", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("8dcddb52137c4cfbb2f81cdc621c2ba11010db1e", manifest.surveyed_commit);
    try std.testing.expectEqual(@as(usize, 8), manifest.shared_smoke_surfaces.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchor_packets.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.smoke_commands.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.smoke_shard_commands.len);
    try std.testing.expect(manifest.survey_summary.phase14_build_has_shared_smoke_step);
    try std.testing.expect(manifest.survey_summary.phase14_build_has_smoke_shard_step);
    try std.testing.expect(manifest.survey_summary.phase14_make_target_present);
    try std.testing.expect(manifest.survey_summary.phase14_make_smoke_target_present);
    try std.testing.expect(manifest.survey_summary.workflow_runs_phase14_build);
    try std.testing.expect(manifest.survey_summary.workflow_runs_phase14_smoke_shard);
    try std.testing.expect(manifest.survey_summary.review_checklist_has_phase14_smoke_prompt);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_workqueue_c);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_skbuff_c);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_ring_buffer_c);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_tree_c);

    try std.testing.expectEqualStrings("P14-L01", manifest.anchor_packets[0].lane_key);
    try std.testing.expectEqualStrings("007f00d0c6b6b430bfbb2110555544cc5faefe8b", manifest.anchor_packets[0].surveyed_commit);
    try std.testing.expectEqualStrings("phase14-workqueue-drain-cancel-followup", manifest.anchor_packets[0].ready_next_gap);
    try std.testing.expectEqualStrings("phase14-workqueue-live-execution-blocker", manifest.anchor_packets[0].blocked_gap);
    try std.testing.expectEqualStrings("P14-L14", manifest.anchor_packets[3].lane_key);
    try std.testing.expectEqualStrings("d839457a2f2dbdc7b53711401741b5e88541c818", manifest.anchor_packets[3].surveyed_commit);
    try std.testing.expectEqualStrings("", manifest.anchor_packets[3].ready_next_gap);
    try std.testing.expectEqualStrings("phase14-rcu-tree-bridge-blocker", manifest.anchor_packets[3].blocked_gap);
}

test "phase14 shared smoke survey matches the live anchor packets and shared gate wiring" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const allocator = std.testing.allocator;

    const smoke_manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_end_to_end_smoke_manifest.json",
        allocator,
        .limited(32 * 1024),
    );
    defer allocator.free(smoke_manifest_json);

    const smoke_manifest = try std.json.parseFromSlice(Manifest, allocator, smoke_manifest_json, .{});
    defer smoke_manifest.deinit();

    const build_file = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_build.zig",
        allocator,
        .limited(16 * 1024),
    );
    defer allocator.free(build_file);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase14-end-to-end-smoke-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase14_end_to_end_smoke_survey.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase14-smoke") != null);

    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        allocator,
        .limited(16 * 1024),
    );
    defer allocator.free(makefile);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase14-test:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase14: phase14-test") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase14-smoke:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all") != null);

    const workflow = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        allocator,
        .limited(32 * 1024),
    );
    defer allocator.free(workflow);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "Run Phase 14 internal bridge tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "zig build test --build-file zigux/tests/phase14_build.zig --summary all") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "Run Phase 14 smoke shard") != null);
    try std.testing.expect(std.mem.indexOf(u8, workflow, "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig --summary all") != null);

    const checklist = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/review-checklist.md",
        allocator,
        .limited(32 * 1024),
    );
    defer allocator.free(checklist);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "shared Phase 14 smoke packet") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "phase14_end_to_end_smoke_manifest.json") != null);

    const freeze_map = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/freeze-map.md",
        allocator,
        .limited(32 * 1024),
    );
    defer allocator.free(freeze_map);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "kernel/workqueue.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "net/core/skbuff.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "kernel/trace/ring_buffer.c") != null);
    try std.testing.expect(std.mem.indexOf(u8, freeze_map, "kernel/rcu/tree.c") != null);

    const smoke_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
        allocator,
        .limited(32 * 1024),
    );
    defer allocator.free(smoke_note);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, smoke_manifest.value.surveyed_commit) != null);

    for (smoke_manifest.value.anchor_packets) |packet| {
        const anchor_manifest_json = try std.Io.Dir.cwd().readFileAlloc(
            io_instance.io(),
            packet.manifest_path,
            allocator,
            .limited(32 * 1024),
        );
        defer allocator.free(anchor_manifest_json);

        const anchor_manifest = try std.json.parseFromSlice(AnchorManifest, allocator, anchor_manifest_json, .{
            .ignore_unknown_fields = true,
        });
        defer anchor_manifest.deinit();

        try std.testing.expectEqualStrings(packet.lane_key, anchor_manifest.value.lane_key);
        try std.testing.expectEqualStrings(packet.anchor, anchor_manifest.value.anchor);
        try std.testing.expectEqualStrings(packet.surveyed_commit, anchor_manifest.value.surveyed_commit);
        if (packet.ready_next_gap.len > 0) {
            try std.testing.expect(hasGapWithStatus(anchor_manifest.value.gaps, packet.ready_next_gap, "ready_next"));
        }
        try std.testing.expect(hasGapWithStatus(anchor_manifest.value.gaps, packet.blocked_gap, "blocked_on_live_concurrency") or
            hasGapWithStatus(anchor_manifest.value.gaps, packet.blocked_gap, "blocked_on_stay_in_c_evidence"));

        const survey_note = try std.Io.Dir.cwd().readFileAlloc(
            io_instance.io(),
            packet.survey_note_path,
            allocator,
            .limited(32 * 1024),
        );
        defer allocator.free(survey_note);
        try std.testing.expect(std.mem.indexOf(u8, survey_note, packet.anchor) != null);
        try std.testing.expect(std.mem.indexOf(u8, smoke_note, packet.surveyed_commit) != null);
        if (packet.ready_next_gap.len > 0) {
            try std.testing.expect(std.mem.indexOf(u8, survey_note, "Next bounded step") != null);
        }
    }
}
