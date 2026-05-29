const std = @import("std");

const Productization = struct {
    owner: []const u8,
    status_bucket: []const u8,
    validation_gate: []const u8,
    rollback_owner: []const u8,
    transfer_rationale: []const u8,
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

const CompileShard = struct {
    label: []const u8,
    root_source: []const u8,
    coverage: []const u8,
};

const SurveySummary = struct {
    phase14_validate_script_present: bool,
    phase14_build_has_shared_smoke_step: bool,
    phase14_build_has_smoke_shard_step: bool,
    phase14_make_target_present: bool,
    phase14_make_smoke_target_present: bool,
    workflow_runs_phase14_validate: bool,
    workflow_runs_phase14_build: bool,
    workflow_runs_phase14_smoke_shard: bool,
    phase14_validate_runs_skbuff_compile_route_checker: bool,
    phase14_validate_runs_ring_buffer_compile_route_checker: bool,
    phase14_validate_runs_rcu_compile_route_checker: bool,
    freeze_map_lists_workqueue_c: bool,
    freeze_map_lists_skbuff_c: bool,
    freeze_map_lists_ring_buffer_c: bool,
    freeze_map_lists_tree_c: bool,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    productization: Productization,
    shared_smoke_surfaces: []const []const u8,
    anchor_packets: []const AnchorPacket,
    smoke_commands: []const []const u8,
    smoke_shard_commands: []const []const u8,
    compile_shards: []const CompileShard,
    survey_summary: SurveySummary,
};

const ExpectedAnchor = struct {
    lane_key: []const u8,
    anchor: []const u8,
    manifest_path: []const u8,
    survey_note_path: []const u8,
    blocked_gap: []const u8,
};

const expected_anchors = [_]ExpectedAnchor{
    .{
        .lane_key = "P14-L04",
        .anchor = "kernel/workqueue.c",
        .manifest_path = "zigux/tests/phase14_workqueue_bridge_manifest.json",
        .survey_note_path = "Documentation/zigux/phase14-workqueue-bridge-survey.md",
        .blocked_gap = "phase14-workqueue-live-execution-blocker",
    },
    .{
        .lane_key = "P14-L11",
        .anchor = "net/core/skbuff.c",
        .manifest_path = "zigux/tests/phase14_skbuff_bridge_manifest.json",
        .survey_note_path = "Documentation/zigux/phase14-skbuff-bridge-survey.md",
        .blocked_gap = "phase14-skbuff-live-ownership-blocker",
    },
    .{
        .lane_key = "P14-L08",
        .anchor = "kernel/trace/ring_buffer.c",
        .manifest_path = "zigux/tests/phase14_ring_buffer_manifest.json",
        .survey_note_path = "Documentation/zigux/phase14-ring-buffer-survey.md",
        .blocked_gap = "phase14-ring-buffer-zig-port-blocker",
    },
    .{
        .lane_key = "P14-L16",
        .anchor = "kernel/rcu/tree.c",
        .manifest_path = "zigux/tests/phase14_rcu_tree_manifest.json",
        .survey_note_path = "Documentation/zigux/phase14-rcu-tree-survey.md",
        .blocked_gap = "phase14-rcu-tree-bridge-blocker",
    },
};

const expected_compile_shards = [_][]const u8{
    "phase14-workqueue-bridge-tests",
    "phase14-workqueue-reviewability-tests",
    "phase14-skbuff-bridge-tests",
    "phase14-ring-buffer-survey-tests",
    "phase14-rcu-tree-survey-tests",
    "phase14-end-to-end-smoke-tests",
};

fn expectContains(list: []const []const u8, needle: []const u8) !void {
    for (list) |item| {
        if (std.mem.eql(u8, item, needle)) return;
    }
    return error.MissingExpectedItem;
}

fn expectNoContains(list: []const []const u8, needle: []const u8) !void {
    for (list) |item| {
        try std.testing.expect(!std.mem.eql(u8, item, needle));
    }
}

fn expectAnchor(packet: AnchorPacket, expected: ExpectedAnchor) !void {
    try std.testing.expectEqualStrings(expected.lane_key, packet.lane_key);
    try std.testing.expectEqualStrings(expected.anchor, packet.anchor);
    try std.testing.expectEqualStrings(expected.manifest_path, packet.manifest_path);
    try std.testing.expectEqualStrings(expected.survey_note_path, packet.survey_note_path);
    try std.testing.expectEqualStrings("", packet.ready_next_gap);
    try std.testing.expectEqualStrings(expected.blocked_gap, packet.blocked_gap);
    try std.testing.expect(packet.surveyed_commit.len == 40);
}

fn expectCompileShard(shard: CompileShard, label: []const u8, is_smoke_shard: bool) !void {
    try std.testing.expectEqualStrings(label, shard.label);
    if (is_smoke_shard) {
        try std.testing.expectEqualStrings("phase14_end_to_end_smoke_survey.zig", shard.root_source);
        try std.testing.expectEqualStrings("focused_and_full_bundle", shard.coverage);
    } else {
        try std.testing.expectEqualStrings("full_bundle_only", shard.coverage);
    }
}

test "phase14 shared smoke manifest covers the four roadmap anchors and the focused smoke shard" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase14_end_to_end_smoke_manifest.json",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P14-L07", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("Core-Adjacent Pod", manifest.productization.owner);
    try std.testing.expectEqualStrings("study_only", manifest.productization.status_bucket);
    try std.testing.expectEqualStrings("make -C zigux phase14-validate", manifest.productization.validation_gate);
    try std.testing.expectEqualStrings("Repo Tooling Pod", manifest.productization.rollback_owner);
    try std.testing.expect(std.mem.indexOf(u8, manifest.productization.transfer_rationale, "product discipline only") != null);

    try std.testing.expectEqual(expected_anchors.len, manifest.anchor_packets.len);
    for (expected_anchors, 0..) |expected, index| {
        try expectAnchor(manifest.anchor_packets[index], expected);
    }

    try std.testing.expectEqual(expected_compile_shards.len, manifest.compile_shards.len);
    for (expected_compile_shards, 0..) |label, index| {
        try expectCompileShard(
            manifest.compile_shards[index],
            label,
            std.mem.eql(u8, label, "phase14-end-to-end-smoke-tests"),
        );
    }

    try expectContains(manifest.smoke_commands, "make -C zigux phase14-validate");
    try expectNoContains(manifest.smoke_commands, "make -C zigux phase14-smoke");
    try expectNoContains(manifest.smoke_commands, "make -C zigux phase14-test");
    try expectContains(
        manifest.smoke_shard_commands,
        "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig",
    );

    try expectContains(manifest.shared_smoke_surfaces, "scripts/zigux/check-phase14-shared-smoke-route.py");
    try expectContains(manifest.shared_smoke_surfaces, "scripts/zigux/check-phase14-skbuff-compile-route.py");
    try expectContains(manifest.shared_smoke_surfaces, "scripts/zigux/check-phase14-ring-buffer-compile-route.py");
    try expectContains(manifest.shared_smoke_surfaces, "scripts/zigux/check-phase14-rcu-compile-route.py");
    try expectContains(manifest.shared_smoke_surfaces, "zigux/tests/phase14_end_to_end_smoke_survey.zig");

    try std.testing.expect(manifest.survey_summary.phase14_validate_script_present);
    try std.testing.expect(manifest.survey_summary.phase14_build_has_shared_smoke_step);
    try std.testing.expect(manifest.survey_summary.phase14_build_has_smoke_shard_step);
    try std.testing.expect(manifest.survey_summary.phase14_make_target_present);
    try std.testing.expect(!manifest.survey_summary.phase14_make_smoke_target_present);
    try std.testing.expect(manifest.survey_summary.workflow_runs_phase14_validate);
    try std.testing.expect(!manifest.survey_summary.workflow_runs_phase14_build);
    try std.testing.expect(!manifest.survey_summary.workflow_runs_phase14_smoke_shard);
    try std.testing.expect(manifest.survey_summary.phase14_validate_runs_skbuff_compile_route_checker);
    try std.testing.expect(manifest.survey_summary.phase14_validate_runs_ring_buffer_compile_route_checker);
    try std.testing.expect(manifest.survey_summary.phase14_validate_runs_rcu_compile_route_checker);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_workqueue_c);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_skbuff_c);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_ring_buffer_c);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_tree_c);
}
