const std = @import("std");

const SurveySummary = struct {
    phase14_validate_script_present: bool,
    phase14_validate_entrypoint_present: bool,
    phase14_build_has_shared_smoke_step: bool,
    phase14_build_has_smoke_shard_step: bool,
    phase14_make_target_present: bool,
    phase14_make_smoke_target_present: bool,
    workflow_runs_phase14_validate: bool,
    workflow_runs_phase14_build: bool,
    workflow_runs_phase14_smoke_shard: bool,
    review_checklist_has_phase14_smoke_prompt: bool,
    review_checklist_has_productization_prompt: bool,
    smoke_note_records_owner_and_rollback: bool,
    smoke_note_records_transfer_rationale: bool,
    freeze_map_lists_workqueue_c: bool,
    freeze_map_lists_skbuff_c: bool,
    freeze_map_lists_ring_buffer_c: bool,
    freeze_map_lists_tree_c: bool,
};

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
    artifact_name: []const u8,
    root_source_file: []const u8,
    coverage_mode: []const u8,
    dedicated_step: []const u8,
    bridge_import: []const u8,
    bridge_source_file: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    productization: Productization,
    shared_smoke_surfaces: []const []const u8,
    anchor_packets: []const AnchorPacket,
    smoke_commands: []const []const u8,
    smoke_shard_commands: []const []const u8,
    compile_shards: []const CompileShard,
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
    try std.testing.expectEqualStrings("05b7de54039c875e09b27425f57b73945232aa03", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Core-Adjacent Pod", manifest.productization.owner);
    try std.testing.expectEqualStrings("study_only", manifest.productization.status_bucket);
    try std.testing.expectEqualStrings(
        "zig build test --build-file zigux/tests/phase14_build.zig --summary all && make -C zigux phase14",
        manifest.productization.validation_gate,
    );
    try std.testing.expectEqualStrings("Repo Tooling Pod", manifest.productization.rollback_owner);
    try std.testing.expect(std.mem.indexOf(u8, manifest.productization.transfer_rationale, "ZAR runtime research") != null);
    try std.testing.expectEqual(@as(usize, 10), manifest.shared_smoke_surfaces.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchor_packets.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.smoke_commands.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.smoke_shard_commands.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.compile_shards.len);
    try std.testing.expect(manifest.survey_summary.phase14_validate_script_present);
    try std.testing.expect(manifest.survey_summary.phase14_validate_entrypoint_present);
    try std.testing.expect(manifest.survey_summary.phase14_build_has_shared_smoke_step);
    try std.testing.expect(manifest.survey_summary.phase14_build_has_smoke_shard_step);
    try std.testing.expect(manifest.survey_summary.phase14_make_target_present);
    try std.testing.expect(manifest.survey_summary.phase14_make_smoke_target_present);
    try std.testing.expect(manifest.survey_summary.workflow_runs_phase14_validate);
    try std.testing.expect(manifest.survey_summary.workflow_runs_phase14_build);
    try std.testing.expect(manifest.survey_summary.workflow_runs_phase14_smoke_shard);
    try std.testing.expect(manifest.survey_summary.review_checklist_has_phase14_smoke_prompt);
    try std.testing.expect(manifest.survey_summary.review_checklist_has_productization_prompt);
    try std.testing.expect(manifest.survey_summary.smoke_note_records_owner_and_rollback);
    try std.testing.expect(manifest.survey_summary.smoke_note_records_transfer_rationale);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_workqueue_c);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_skbuff_c);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_ring_buffer_c);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_tree_c);

    try std.testing.expectEqualStrings("P14-L01", manifest.anchor_packets[0].lane_key);
    try std.testing.expectEqualStrings("1b346dbd77659625fedfdc2a45f5016e391043f8", manifest.anchor_packets[0].surveyed_commit);
    try std.testing.expectEqualStrings("phase14-workqueue-drain-cancel-followup", manifest.anchor_packets[0].ready_next_gap);
    try std.testing.expectEqualStrings("phase14-workqueue-live-execution-blocker", manifest.anchor_packets[0].blocked_gap);
    try std.testing.expectEqualStrings("P14-L14", manifest.anchor_packets[3].lane_key);
    try std.testing.expectEqualStrings("4e45e5a392cca82429228d42d89c480fd413042b", manifest.anchor_packets[3].surveyed_commit);
    try std.testing.expectEqualStrings("", manifest.anchor_packets[3].ready_next_gap);
    try std.testing.expectEqualStrings("phase14-rcu-tree-bridge-blocker", manifest.anchor_packets[3].blocked_gap);

    try std.testing.expectEqualStrings("phase14-workqueue-bridge-tests", manifest.compile_shards[0].artifact_name);
    try std.testing.expectEqualStrings("phase14_workqueue_bridge.zig", manifest.compile_shards[0].root_source_file);
    try std.testing.expectEqualStrings("full_bundle_only", manifest.compile_shards[0].coverage_mode);
    try std.testing.expectEqualStrings("", manifest.compile_shards[0].dedicated_step);
    try std.testing.expectEqualStrings("workqueue_bridge", manifest.compile_shards[0].bridge_import);
    try std.testing.expectEqualStrings("../../kernel/workqueue_bridge.zig", manifest.compile_shards[0].bridge_source_file);
    try std.testing.expectEqualStrings("phase14-skbuff-bridge-tests", manifest.compile_shards[1].artifact_name);
    try std.testing.expectEqualStrings("phase14_skbuff_bridge.zig", manifest.compile_shards[1].root_source_file);
    try std.testing.expectEqualStrings("full_bundle_only", manifest.compile_shards[1].coverage_mode);
    try std.testing.expectEqualStrings("", manifest.compile_shards[1].dedicated_step);
    try std.testing.expectEqualStrings("skbuff_bridge", manifest.compile_shards[1].bridge_import);
    try std.testing.expectEqualStrings("../../net/core/skbuff_bridge.zig", manifest.compile_shards[1].bridge_source_file);
    try std.testing.expectEqualStrings("phase14-ring-buffer-survey-tests", manifest.compile_shards[2].artifact_name);
    try std.testing.expectEqualStrings("phase14_ring_buffer_survey.zig", manifest.compile_shards[2].root_source_file);
    try std.testing.expectEqualStrings("full_bundle_only", manifest.compile_shards[2].coverage_mode);
    try std.testing.expectEqualStrings("", manifest.compile_shards[2].dedicated_step);
    try std.testing.expectEqualStrings("phase14-rcu-tree-survey-tests", manifest.compile_shards[3].artifact_name);
    try std.testing.expectEqualStrings("phase14_rcu_tree_survey.zig", manifest.compile_shards[3].root_source_file);
    try std.testing.expectEqualStrings("full_bundle_only", manifest.compile_shards[3].coverage_mode);
    try std.testing.expectEqualStrings("", manifest.compile_shards[3].dedicated_step);
    try std.testing.expectEqualStrings("phase14-end-to-end-smoke-tests", manifest.compile_shards[4].artifact_name);
    try std.testing.expectEqualStrings("phase14_end_to_end_smoke_survey.zig", manifest.compile_shards[4].root_source_file);
    try std.testing.expectEqualStrings("focused_and_full_bundle", manifest.compile_shards[4].coverage_mode);
    try std.testing.expectEqualStrings("phase14-smoke", manifest.compile_shards[4].dedicated_step);
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
    var focused_shard_count: usize = 0;
    var full_bundle_only_count: usize = 0;
    for (smoke_manifest.value.compile_shards) |shard| {
        try std.testing.expect(std.mem.indexOf(u8, build_file, shard.artifact_name) != null);
        try std.testing.expect(std.mem.indexOf(u8, build_file, shard.root_source_file) != null);
        if (std.mem.eql(u8, shard.coverage_mode, "focused_and_full_bundle")) {
            focused_shard_count += 1;
            try std.testing.expect(shard.dedicated_step.len > 0);
            try std.testing.expect(std.mem.indexOf(u8, build_file, shard.dedicated_step) != null);
        } else {
            full_bundle_only_count += 1;
            try std.testing.expectEqualStrings("full_bundle_only", shard.coverage_mode);
            try std.testing.expectEqualStrings("", shard.dedicated_step);
        }
        if (shard.bridge_import.len > 0) {
            try std.testing.expect(std.mem.indexOf(u8, build_file, shard.bridge_import) != null);
            try std.testing.expect(std.mem.indexOf(u8, build_file, shard.bridge_source_file) != null);
        }
    }
    try std.testing.expectEqual(@as(usize, 1), focused_shard_count);
    try std.testing.expectEqual(@as(usize, 4), full_bundle_only_count);

    const makefile = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/Makefile",
        allocator,
        .limited(16 * 1024),
    );
    defer allocator.free(makefile);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase14-test:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase14-validate:") != null);
    try std.testing.expect(std.mem.indexOf(u8, makefile, "phase14: phase14-validate phase14-test") != null);
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
    try std.testing.expect(std.mem.indexOf(u8, checklist, "named owner") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "rollback owner") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "ZAR-to-product transfer rationale") != null);

    const script_readme = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "scripts/zigux/README.md",
        allocator,
        .limited(32 * 1024),
    );
    defer allocator.free(script_readme);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "make -C zigux phase14-validate") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "make -C zigux phase14-smoke") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "focused smoke-shard replay contract") != null);

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
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_SMOKE_VALIDATOR=present") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_COMPILE_ARTIFACT_COUNT=5") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_FOCUSED_SHARD_COUNT=1") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=4") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, smoke_manifest.value.productization.owner) != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, smoke_manifest.value.productization.rollback_owner) != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, smoke_manifest.value.productization.validation_gate) != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "ZAR runtime research") != null);
    for (smoke_manifest.value.compile_shards) |shard| {
        try std.testing.expect(std.mem.indexOf(u8, smoke_note, shard.artifact_name) != null);
        try std.testing.expect(std.mem.indexOf(u8, smoke_note, shard.coverage_mode) != null);
        if (shard.dedicated_step.len > 0) {
            try std.testing.expect(std.mem.indexOf(u8, smoke_note, shard.dedicated_step) != null);
        }
    }
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "only the shared smoke survey has a dedicated shard today") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "four anchor-local artifacts still replay only through the broader `test` bundle") != null);

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
        try std.testing.expect(std.mem.indexOf(u8, smoke_note, packet.lane_key) != null);
        try std.testing.expect(std.mem.indexOf(u8, smoke_note, packet.surveyed_commit) != null);
        if (packet.ready_next_gap.len > 0) {
            try std.testing.expect(std.mem.indexOf(u8, survey_note, "Next bounded step") != null);
        }
    }
}
