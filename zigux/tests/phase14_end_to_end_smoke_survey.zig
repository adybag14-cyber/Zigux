const std = @import("std");

const SurveySummary = struct {
    phase14_validate_script_present: bool,
    phase14_validate_entrypoint_present: bool,
    phase14_build_has_shared_smoke_step: bool,
    phase14_build_has_smoke_shard_step: bool,
    phase14_build_full_bundle_routes_all_compile_artifacts: bool,
    phase14_build_smoke_shard_routes_only_smoke_survey: bool,
    phase14_make_target_present: bool,
    phase14_make_smoke_target_present: bool,
    workflow_runs_phase14_validate: bool,
    workflow_runs_phase14_build: bool,
    workflow_runs_phase14_smoke_shard: bool,
    workflow_runs_phase14_smoke_wrapper: bool,
    review_checklist_has_phase14_smoke_prompt: bool,
    review_checklist_has_productization_prompt: bool,
    review_checklist_has_risk_bundle_prompt: bool,
    review_checklist_has_rollback_threshold_prompt: bool,
    review_checklist_has_fallback_path_prompt: bool,
    review_checklist_has_return_to_blocked_trigger_prompt: bool,
    review_checklist_has_boundary_map_prompt: bool,
    review_checklist_has_concurrency_audit_prompt: bool,
    smoke_note_records_owner_and_rollback: bool,
    smoke_note_records_risk_bundle: bool,
    smoke_note_records_review_blocker_status: bool,
    smoke_note_records_rollback_threshold: bool,
    smoke_note_records_fallback_path: bool,
    smoke_note_records_return_to_blocked_triggers: bool,
    smoke_note_records_transfer_rationale: bool,
    smoke_note_records_boundary_map: bool,
    smoke_note_records_concurrency_audit_scope: bool,
    scripts_readme_records_rollback_threshold: bool,
    scripts_readme_records_fallback_path: bool,
    scripts_readme_records_return_to_blocked_triggers: bool,
    scripts_readme_records_boundary_map: bool,
    scripts_readme_records_concurrency_audit_scope: bool,
    release_boundary_note_records_shared_smoke_packet: bool,
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
    risk_bundle: []const []const u8,
};

const RollbackThreshold = struct {
    status_bucket: []const u8,
    review_blocker_status: []const u8,
    owner: []const u8,
    rollback_owner: []const u8,
    fallback_path: []const u8,
    required_evidence: []const []const u8,
    rollback_triggers: []const []const u8,
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
    rollback_threshold: RollbackThreshold,
    shared_smoke_surfaces: []const []const u8,
    anchor_packets: []const AnchorPacket,
    smoke_commands: []const []const u8,
    smoke_shard_commands: []const []const u8,
    attached_toolchain_commands: []const []const u8,
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
    try std.testing.expectEqualStrings("P14-L01", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 14", manifest.phase);
    try std.testing.expectEqualStrings("02264a3240cd30ce45c9a932047a0204b7ab5029", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("Core-Adjacent Pod", manifest.productization.owner);
    try std.testing.expectEqualStrings("study_only", manifest.productization.status_bucket);
    try std.testing.expectEqualStrings(
        "zig build test --build-file zigux/tests/phase14_build.zig --summary all && make -C zigux phase14",
        manifest.productization.validation_gate,
    );
    try std.testing.expectEqualStrings("Repo Tooling Pod", manifest.productization.rollback_owner);
    try std.testing.expect(std.mem.indexOf(u8, manifest.productization.transfer_rationale, "ZAR runtime research") != null);
    try std.testing.expectEqual(@as(usize, 4), manifest.productization.risk_bundle.len);
    try std.testing.expectEqualStrings("hidden runtime behavior", manifest.productization.risk_bundle[0]);
    try std.testing.expectEqualStrings("memory-ordering mistakes", manifest.productization.risk_bundle[1]);
    try std.testing.expectEqualStrings("overpromising full parity", manifest.productization.risk_bundle[2]);
    try std.testing.expectEqualStrings("deep-core scope creep", manifest.productization.risk_bundle[3]);
    try std.testing.expectEqualStrings("study_only", manifest.rollback_threshold.status_bucket);
    try std.testing.expectEqualStrings("blocked_on_stay_in_c_evidence", manifest.rollback_threshold.review_blocker_status);
    try std.testing.expectEqualStrings("Core-Adjacent Pod", manifest.rollback_threshold.owner);
    try std.testing.expectEqualStrings("Repo Tooling Pod", manifest.rollback_threshold.rollback_owner);
    try std.testing.expect(std.mem.indexOf(u8, manifest.rollback_threshold.fallback_path, "source of truth") != null);
    try std.testing.expectEqual(@as(usize, 3), manifest.rollback_threshold.required_evidence.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.rollback_threshold.rollback_triggers.len);
    try std.testing.expectEqual(@as(usize, 15), manifest.shared_smoke_surfaces.len);
    var has_rcu_tree_shared_surface = false;
    for (manifest.shared_smoke_surfaces) |surface| {
        if (std.mem.eql(u8, surface, "zigux/tests/phase14_rcu_tree_survey.zig")) {
            has_rcu_tree_shared_surface = true;
        }
    }
    try std.testing.expect(has_rcu_tree_shared_surface);
    try std.testing.expectEqual(@as(usize, 4), manifest.anchor_packets.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.smoke_commands.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.smoke_shard_commands.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.attached_toolchain_commands.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.compile_shards.len);
    try std.testing.expect(manifest.survey_summary.phase14_validate_script_present);
    try std.testing.expect(manifest.survey_summary.phase14_validate_entrypoint_present);
    try std.testing.expect(manifest.survey_summary.phase14_build_has_shared_smoke_step);
    try std.testing.expect(manifest.survey_summary.phase14_build_has_smoke_shard_step);
    try std.testing.expect(manifest.survey_summary.phase14_build_full_bundle_routes_all_compile_artifacts);
    try std.testing.expect(manifest.survey_summary.phase14_build_smoke_shard_routes_only_smoke_survey);
    try std.testing.expect(manifest.survey_summary.phase14_make_target_present);
    try std.testing.expect(manifest.survey_summary.phase14_make_smoke_target_present);
    try std.testing.expect(manifest.survey_summary.workflow_runs_phase14_validate);
    try std.testing.expect(manifest.survey_summary.workflow_runs_phase14_build);
    try std.testing.expect(manifest.survey_summary.workflow_runs_phase14_smoke_shard);
    try std.testing.expect(manifest.survey_summary.workflow_runs_phase14_smoke_wrapper);
    try std.testing.expect(manifest.survey_summary.review_checklist_has_phase14_smoke_prompt);
    try std.testing.expect(manifest.survey_summary.review_checklist_has_productization_prompt);
    try std.testing.expect(manifest.survey_summary.review_checklist_has_risk_bundle_prompt);
    try std.testing.expect(manifest.survey_summary.review_checklist_has_rollback_threshold_prompt);
    try std.testing.expect(manifest.survey_summary.review_checklist_has_fallback_path_prompt);
    try std.testing.expect(manifest.survey_summary.review_checklist_has_return_to_blocked_trigger_prompt);
    try std.testing.expect(manifest.survey_summary.review_checklist_has_boundary_map_prompt);
    try std.testing.expect(manifest.survey_summary.review_checklist_has_concurrency_audit_prompt);
    try std.testing.expect(manifest.survey_summary.smoke_note_records_owner_and_rollback);
    try std.testing.expect(manifest.survey_summary.smoke_note_records_risk_bundle);
    try std.testing.expect(manifest.survey_summary.smoke_note_records_review_blocker_status);
    try std.testing.expect(manifest.survey_summary.smoke_note_records_rollback_threshold);
    try std.testing.expect(manifest.survey_summary.smoke_note_records_fallback_path);
    try std.testing.expect(manifest.survey_summary.smoke_note_records_return_to_blocked_triggers);
    try std.testing.expect(manifest.survey_summary.smoke_note_records_transfer_rationale);
    try std.testing.expect(manifest.survey_summary.smoke_note_records_boundary_map);
    try std.testing.expect(manifest.survey_summary.smoke_note_records_concurrency_audit_scope);
    try std.testing.expect(manifest.survey_summary.scripts_readme_records_rollback_threshold);
    try std.testing.expect(manifest.survey_summary.scripts_readme_records_fallback_path);
    try std.testing.expect(manifest.survey_summary.scripts_readme_records_return_to_blocked_triggers);
    try std.testing.expect(manifest.survey_summary.scripts_readme_records_boundary_map);
    try std.testing.expect(manifest.survey_summary.scripts_readme_records_concurrency_audit_scope);
    try std.testing.expect(manifest.survey_summary.release_boundary_note_records_shared_smoke_packet);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_workqueue_c);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_skbuff_c);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_ring_buffer_c);
    try std.testing.expect(manifest.survey_summary.freeze_map_lists_tree_c);

    try std.testing.expectEqualStrings(
        "make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>",
        manifest.attached_toolchain_commands[0],
    );
    try std.testing.expectEqualStrings(
        "make -C zigux phase14-smoke ZIG=<attached-zig-path>",
        manifest.attached_toolchain_commands[1],
    );
    try std.testing.expectEqualStrings(
        "make -C zigux phase14-test ZIG=<attached-zig-path>",
        manifest.attached_toolchain_commands[2],
    );
    try std.testing.expectEqualStrings(
        "make -C zigux phase14 ZIG=<attached-zig-path>",
        manifest.attached_toolchain_commands[3],
    );

    try std.testing.expectEqualStrings("P14-Y05", manifest.anchor_packets[0].lane_key);
    try std.testing.expectEqualStrings("02264a3240cd30ce45c9a932047a0204b7ab5029", manifest.anchor_packets[0].surveyed_commit);
    try std.testing.expectEqualStrings("", manifest.anchor_packets[0].ready_next_gap);
    try std.testing.expectEqualStrings("phase14-workqueue-live-execution-blocker", manifest.anchor_packets[0].blocked_gap);
    try std.testing.expectEqualStrings("P14-L08", manifest.anchor_packets[2].lane_key);
    try std.testing.expectEqualStrings("f9a7a6e93c8e6a1b6550fd7b2aa5571729aab05b", manifest.anchor_packets[2].surveyed_commit);
    try std.testing.expectEqualStrings("", manifest.anchor_packets[2].ready_next_gap);
    try std.testing.expectEqualStrings("phase14-ring-buffer-zig-port-blocker", manifest.anchor_packets[2].blocked_gap);
    try std.testing.expectEqualStrings("P14-L12", manifest.anchor_packets[1].lane_key);
    try std.testing.expectEqualStrings("02264a3240cd30ce45c9a932047a0204b7ab5029", manifest.anchor_packets[1].surveyed_commit);
    try std.testing.expectEqualStrings("", manifest.anchor_packets[1].ready_next_gap);
    try std.testing.expectEqualStrings("phase14-skbuff-live-ownership-blocker", manifest.anchor_packets[1].blocked_gap);
    try std.testing.expectEqualStrings("P14-Y04", manifest.anchor_packets[3].lane_key);
    try std.testing.expectEqualStrings("355b71d89807a217a6b7c405c996cbd623c48ca0", manifest.anchor_packets[3].surveyed_commit);
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
    try std.testing.expect(std.mem.indexOf(u8, build_file, "phase14_smoke_step.dependOn(&run_phase14_end_to_end_smoke_tests.step);") != null);
    var focused_shard_count: usize = 0;
    var full_bundle_only_count: usize = 0;
    var anchor_local_step_count: usize = 0;
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
        if (shard.dedicated_step.len > 0 and !std.mem.eql(u8, shard.artifact_name, "phase14-end-to-end-smoke-tests")) {
            anchor_local_step_count += 1;
        }
        if (shard.bridge_import.len > 0) {
            try std.testing.expect(std.mem.indexOf(u8, build_file, shard.bridge_import) != null);
            try std.testing.expect(std.mem.indexOf(u8, build_file, shard.bridge_source_file) != null);
        }
    }
    try std.testing.expectEqual(@as(usize, 1), focused_shard_count);
    try std.testing.expectEqual(@as(usize, 0), anchor_local_step_count);
    try std.testing.expectEqual(@as(usize, 4), full_bundle_only_count);
    try std.testing.expectEqual(@as(usize, 5), std.mem.count(u8, build_file, "test_step.dependOn(&run_phase14_"));
    try std.testing.expectEqual(@as(usize, 1), std.mem.count(u8, build_file, "phase14_smoke_step.dependOn(&run_phase14_"));

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
    try std.testing.expect(std.mem.indexOf(u8, workflow, "make -C zigux phase14-smoke") != null);

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
    try std.testing.expect(std.mem.indexOf(u8, checklist, "stated rollback owner and fallback path?") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "automatic return-to-blocked trigger catalog") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "hidden runtime behavior") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "memory-ordering mistakes") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "overpromising full parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "deep-core scope creep") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "ZAR-to-product transfer rationale") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "rollback threshold") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "four-anchor boundary map") != null);
    try std.testing.expect(std.mem.indexOf(u8, checklist, "bounded concurrency-audit scope") != null);

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
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "roadmap risk bundle") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "hidden runtime behavior") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "memory-ordering mistakes") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "overpromising full parity") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "deep-core scope creep") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "rollback threshold") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "fallback path") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "automatic return-to-blocked trigger catalog") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "four-anchor boundary map") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "bounded concurrency-audit scope") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "make -C zigux phase14-validate PYTHON=python3 ZIG=<attached-zig-path>") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "make -C zigux phase14-smoke ZIG=<attached-zig-path>") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "make -C zigux phase14-test ZIG=<attached-zig-path>") != null);
    try std.testing.expect(std.mem.indexOf(u8, script_readme, "make -C zigux phase14 ZIG=<attached-zig-path>") != null);

    const release_boundary = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase14-release-boundary-survey.md",
        allocator,
        .limited(16 * 1024),
    );
    defer allocator.free(release_boundary);
    try std.testing.expect(smoke_manifest.value.survey_summary.release_boundary_note_records_shared_smoke_packet);
    try std.testing.expect(std.mem.indexOf(u8, release_boundary, "PHASE14_SHARED_REPLAY_PRESENT=yes") != null);
    try std.testing.expect(std.mem.indexOf(u8, release_boundary, "shared smoke packet: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, and `zig build test --build-file zigux/tests/phase14_build.zig --summary all` now keep the four-anchor boundary map, the focused smoke shard, and the shared full-bundle replay explicit from a study-only posture") != null);
    try std.testing.expect(std.mem.indexOf(u8, release_boundary, "combined shared replay entrypoint: `make -C zigux phase14` remains the published convenience route for the validator-backed smoke packet, so release-facing review and local replay still name the same one-command path as the shared smoke note and manifest instead of leaving that wrapper path implicit in `zigux/Makefile`") != null);
    try std.testing.expect(std.mem.indexOf(u8, release_boundary, "PHASE14_SHARED_SMOKE_GATE_COUNT=1") != null);
    try std.testing.expect(std.mem.indexOf(u8, release_boundary, "PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0") != null);

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
    var shared_lane_marker_buf: [64]u8 = undefined;
    const shared_lane_marker = try std.fmt.bufPrint(&shared_lane_marker_buf, "PHASE14_SHARED_LANE={s}", .{smoke_manifest.value.lane_key});
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, shared_lane_marker) != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_SMOKE_VALIDATOR=present") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_VALIDATE_ENTRYPOINT=make -C zigux phase14-validate") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_COMPILE_ARTIFACT_COUNT=5") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_FOCUSED_SHARD_COUNT=1") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_ANCHOR_LOCAL_STEP_COUNT=0") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_FULL_BUNDLE_ONLY_ARTIFACT_COUNT=4") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_FULL_BUNDLE_DEPENDENCY_COUNT=5") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_FOCUSED_SHARD_DEPENDENCY_COUNT=1") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_FOCUSED_SHARD_ONLY_ARTIFACT=phase14-end-to-end-smoke-tests") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_BOUNDARY_MAP=shared-anchor-packet-bundle") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_CONCURRENCY_AUDIT_SCOPE=anchor-local-packets-only") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "PHASE14_ATTACHED_TOOLCHAIN_FALLBACK=ZIG=<attached-zig-path>") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, smoke_manifest.value.productization.owner) != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, smoke_manifest.value.productization.rollback_owner) != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, smoke_manifest.value.productization.validation_gate) != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "ZAR runtime research") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, smoke_manifest.value.rollback_threshold.fallback_path) != null);
    for (smoke_manifest.value.productization.risk_bundle) |risk| {
        try std.testing.expect(std.mem.indexOf(u8, smoke_note, risk) != null);
    }
    for (smoke_manifest.value.rollback_threshold.required_evidence) |required_evidence| {
        try std.testing.expect(std.mem.indexOf(u8, smoke_note, required_evidence) != null);
    }
    for (smoke_manifest.value.rollback_threshold.rollback_triggers) |rollback_trigger| {
        try std.testing.expect(std.mem.indexOf(u8, smoke_note, rollback_trigger) != null);
    }
    for (smoke_manifest.value.compile_shards) |shard| {
        try std.testing.expect(std.mem.indexOf(u8, smoke_note, shard.artifact_name) != null);
        try std.testing.expect(std.mem.indexOf(u8, smoke_note, shard.root_source_file) != null);
        try std.testing.expect(std.mem.indexOf(u8, smoke_note, shard.coverage_mode) != null);
        if (shard.dedicated_step.len > 0) {
            try std.testing.expect(std.mem.indexOf(u8, smoke_note, shard.dedicated_step) != null);
        }
        if (shard.bridge_import.len > 0) {
            try std.testing.expect(std.mem.indexOf(u8, smoke_note, shard.bridge_import) != null);
            try std.testing.expect(std.mem.indexOf(u8, smoke_note, shard.bridge_source_file) != null);
        }
    }
    for (smoke_manifest.value.attached_toolchain_commands) |command| {
        try std.testing.expect(std.mem.indexOf(u8, smoke_note, command) != null);
        try std.testing.expect(std.mem.indexOf(u8, script_readme, command) != null);
    }
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "only the shared smoke survey has a dedicated shard today") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "four anchor-local artifacts still replay only through the broader `test` bundle") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "current four-anchor boundary map") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "bounded concurrency-audit scope") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "phase14_smoke_step") != null);
    try std.testing.expect(std.mem.indexOf(u8, smoke_note, "run_phase14_end_to_end_smoke_tests.step") != null);

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
