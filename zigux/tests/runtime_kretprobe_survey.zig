const std = @import("std");

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const LifecycleBoundarySummary = struct {
    pre_execution_handoff_only: bool,
    requires_idle_registration_snapshot: bool,
    failed_exit_state_retained_until_drain: bool,
    metadata_only_registration_labels: []const []const u8,
    shared_request_surface: []const u8,
    shared_loader_lane: []const u8,
    live_registration_parity: []const u8,
    prepared_snapshot_owned_by_loader_request: bool = false,
};

const RollbackBoundarySummary = struct {
    release_without_substrate_path: []const u8,
    release_without_substrate_api: []const u8,
    release_without_substrate_state: []const u8,
    failed_exit_state_retained_until_drain: bool,
    maxactive_overflow_retained_until_drain: bool,
    live_registration_surfaces: []const []const u8,
    blocked_parity_status: []const u8,
};

const RoadmapGapSummary = struct {
    roadmap_phase_goal: []const u8,
    landed_pilot_state: []const u8,
    missing_capability: []const u8,
    blocked_deliverable: []const u8,
    next_gate: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    roadmap_gap_summary: RoadmapGapSummary,
    lifecycle_boundary_summary: LifecycleBoundarySummary,
    rollback_boundary_summary: RollbackBoundarySummary,
    gaps: []const Gap,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(max_bytes),
    );
}

fn findGap(gaps: []const Gap, id: []const u8) ?Gap {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

test "phase 9 runtime kretprobe survey gate restores the shipped loader review packet" {
    const manifest_json = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/runtime_kretprobe_manifest.json",
        32 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-kretprobe-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    const module_slice_note = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-kretprobe-module-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(module_slice_note);

    const phase9_build = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/phase9_build.zig",
        96 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    const runtime_loader_allocator_init_flow = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/runtime_loader_allocator_init_flow.zig",
        96 * 1024,
    );
    defer std.testing.allocator.free(runtime_loader_allocator_init_flow);

    const runtime_kretprobe_loader = try readRepoFileAlloc(
        std.testing.allocator,
        "samples/zigux/runtime_kretprobe_loader.zig",
        96 * 1024,
    );
    defer std.testing.allocator.free(runtime_kretprobe_loader);
    const runtime_kretprobe_sample = try readRepoFileAlloc(
        std.testing.allocator,
        "samples/zigux/runtime_kretprobe.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(runtime_kretprobe_sample);
    const runtime_kretprobe_diff = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/runtime_kretprobe_diff.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(runtime_kretprobe_diff);

    const runtime_kretprobe_module = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/runtime_kretprobe_module.zig",
        160 * 1024,
    );
    defer std.testing.allocator.free(runtime_kretprobe_module);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P9-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expectEqualStrings("samples/kprobes/kretprobe_example.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("zigux/tests/runtime_*", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_*", manifest.roadmap_destinations[1]);
    try std.testing.expectEqualStrings(
        "first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity",
        manifest.roadmap_gap_summary.roadmap_phase_goal,
    );
    try std.testing.expectEqualStrings(
        "starter_landed_without_loadable_runtime_substrate",
        manifest.roadmap_gap_summary.landed_pilot_state,
    );
    try std.testing.expectEqualStrings(
        "shared runtime substrate that can turn the bounded register_kretprobe and unregister_kretprobe handoff plan into a real loadable module path",
        manifest.roadmap_gap_summary.missing_capability,
    );
    try std.testing.expectEqualStrings(
        "loadable Phase 9 runtime kretprobe pilot module parity",
        manifest.roadmap_gap_summary.blocked_deliverable,
    );
    try std.testing.expectEqualStrings(
        "keep the loader scaffold, shared-request lifecycle proof, and prepared-plan drift guard explicit until the shared runtime loader substrate can consume the handoff plan",
        manifest.roadmap_gap_summary.next_gate,
    );

    try std.testing.expect(manifest.lifecycle_boundary_summary.pre_execution_handoff_only);
    try std.testing.expect(manifest.lifecycle_boundary_summary.requires_idle_registration_snapshot);
    try std.testing.expect(manifest.lifecycle_boundary_summary.failed_exit_state_retained_until_drain);
    try std.testing.expect(manifest.lifecycle_boundary_summary.prepared_snapshot_owned_by_loader_request);
    try std.testing.expectEqualStrings(
        "zigux/kernel/runtime_loader.zig",
        manifest.lifecycle_boundary_summary.shared_request_surface,
    );
    try std.testing.expectEqualStrings(
        "P9-L11",
        manifest.lifecycle_boundary_summary.shared_loader_lane,
    );
    try std.testing.expectEqualStrings(
        "blocked_on_runtime_substrate",
        manifest.lifecycle_boundary_summary.live_registration_parity,
    );
    try std.testing.expectEqual(@as(usize, 2), manifest.lifecycle_boundary_summary.metadata_only_registration_labels.len);
    try std.testing.expectEqualStrings(
        "register_kretprobe",
        manifest.lifecycle_boundary_summary.metadata_only_registration_labels[0],
    );
    try std.testing.expectEqualStrings(
        "unregister_kretprobe",
        manifest.lifecycle_boundary_summary.metadata_only_registration_labels[1],
    );

    try std.testing.expectEqualStrings(
        "samples/zigux/runtime_kretprobe_loader.zig",
        manifest.rollback_boundary_summary.release_without_substrate_path,
    );
    try std.testing.expectEqualStrings(
        "releaseSharedWithoutSubstrate",
        manifest.rollback_boundary_summary.release_without_substrate_api,
    );
    try std.testing.expectEqualStrings(
        "released_without_substrate",
        manifest.rollback_boundary_summary.release_without_substrate_state,
    );
    try std.testing.expect(manifest.rollback_boundary_summary.failed_exit_state_retained_until_drain);
    try std.testing.expect(manifest.rollback_boundary_summary.maxactive_overflow_retained_until_drain);
    try std.testing.expectEqual(@as(usize, 2), manifest.rollback_boundary_summary.live_registration_surfaces.len);
    try std.testing.expectEqualStrings(
        "register_kretprobe",
        manifest.rollback_boundary_summary.live_registration_surfaces[0],
    );
    try std.testing.expectEqualStrings(
        "unregister_kretprobe",
        manifest.rollback_boundary_summary.live_registration_surfaces[1],
    );
    try std.testing.expectEqualStrings(
        "review_only_until_runtime_substrate",
        manifest.rollback_boundary_summary.blocked_parity_status,
    );

    const loader_plan_gap = findGap(manifest.gaps, "runtime-kretprobe-loader-plan") orelse return error.MissingLoaderPlanGap;
    try std.testing.expectEqualStrings("starter_landed", loader_plan_gap.status);
    try std.testing.expectEqualStrings("runtime_loader_scaffold", loader_plan_gap.kind);
    try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe_loader.zig", loader_plan_gap.zigux_destination);
    try expectContains(loader_plan_gap.why_now, "register_kretprobe");
    try expectContains(loader_plan_gap.why_now, "unregister_kretprobe");

    const prepared_plan_drift_gap = findGap(manifest.gaps, "runtime-kretprobe-shared-prepared-plan-drift") orelse return error.MissingPreparedPlanDriftGap;
    try std.testing.expectEqualStrings("starter_landed", prepared_plan_drift_gap.status);
    try std.testing.expectEqualStrings("shared_loader_review_guard", prepared_plan_drift_gap.kind);
    try std.testing.expectEqualStrings("samples/zigux/runtime_kretprobe_loader.zig", prepared_plan_drift_gap.zigux_destination);
    try expectContains(prepared_plan_drift_gap.why_now, "requestSharedRuntimeLoad");
    try expectContains(prepared_plan_drift_gap.why_now, "waiting_on_runtime_substrate");

    const substrate_gap = findGap(manifest.gaps, "runtime-kretprobe-substrate-handoff") orelse return error.MissingSubstrateGap;
    try std.testing.expectEqualStrings("blocked_on_runtime_substrate", substrate_gap.status);
    try std.testing.expectEqualStrings("runtime_substrate", substrate_gap.kind);
    try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", substrate_gap.zigux_destination);
    try expectContains(substrate_gap.why_now, "real register_kretprobe parity");

    try expectContains(survey_note, "`PHASE9_LANE_KEY=P9-L13`");
    try expectContains(
        survey_note,
        "initialized-stage and selftest-complete shared-request handoff snapshots explicit",
    );
    try expectContains(
        survey_note,
        "an initialized prepared request stays pinned even if later sample selftest activity runs before the shared runtime-loader handoff",
    );
    try expectContains(
        survey_note,
        "selftest-complete prepared snapshot explicit across later exit activity",
    );
    try expectContains(
        survey_note,
        "prepared selftest-hook drift rejection, prepared shared-plan drift rejection, and release-without-substrate behavior",
    );
    try expectContains(
        survey_note,
        "`zig build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig`",
    );
    try expectContains(survey_note, "`make -C zigux phase9-runtime-kretprobe-test`");
    try expectContains(survey_note, "`make -C zigux phase9`");

    try expectContains(
        module_slice_note,
        "initialized and selftest-complete shared-request snapshot replays",
    );
    try expectContains(
        module_slice_note,
        "a selftest-complete shared-request snapshot replay that stays explicit even if later sample exit activity runs before the shared runtime-loader handoff",
    );
    try expectContains(
        module_slice_note,
        "the shared `phase9-runtime-loader-shared-tests` shard plus the workflow-backed `make -C zigux phase9` route",
    );
    try expectContains(
        module_slice_note,
        "makes the kretprobe handoff and failure-mode evidence reviewable without claiming loadable-module parity",
    );

    try expectContains(phase9_build, "runtime_kretprobe.zig");
    try expectContains(phase9_build, "phase9-runtime-kretprobe-sample-tests");
    try expectContains(phase9_build, "runtime_kretprobe_module.zig");
    try expectContains(phase9_build, "phase9-runtime-kretprobe-module-tests");
    try expectContains(phase9_build, "runtime_kretprobe_diff.zig");
    try expectContains(phase9_build, "phase9-runtime-kretprobe-diff-tests");
    try expectContains(phase9_build, "runtime_kretprobe_loader.zig");
    try expectContains(phase9_build, "phase9-runtime-kretprobe-loader-tests");
    try expectContains(phase9_build, ".root_source_file = b.path(\"runtime_kretprobe_survey.zig\")");
    try expectContains(phase9_build, ".name = \"phase9-runtime-kretprobe-survey-tests\"");
    try expectContains(phase9_build, "phase9-runtime-kretprobe-tests");
    try expectContains(phase9_build, "runtime_kretprobe_tests_step.dependOn(&run_runtime_kretprobe_survey_tests.step);");
    try expectContains(phase9_build, "runtime_kretprobe_tests_step.dependOn(&run_runtime_loader_contract_tests.step);");
    try expectContains(phase9_build, "runtime_kretprobe_tests_step.dependOn(&run_runtime_loader_facade_tests.step);");
    try expectContains(phase9_build, "runtime_kretprobe_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);");

    try expectContains(
        runtime_loader_allocator_init_flow,
        "samples/kprobes/kretprobe_example.c",
    );
    try expectContains(
        runtime_loader_allocator_init_flow,
        "\"runtime_kretprobe\", \"samples/kprobes/kretprobe_example.c\", \"zigux_runtime_kretprobe_init\", \"zigux_runtime_kretprobe_exit\", .kernel_heap",
    );
    try expectContains(
        runtime_loader_allocator_init_flow,
        "test \"phase 9 runtime loader allocator/init-flow replay keeps initialized prepared snapshots stable even if later live state would look exited\"",
    );
    try expectContains(
        runtime_loader_allocator_init_flow,
        "test \"phase 9 runtime loader allocator/init-flow replay keeps selftest-complete prepared snapshots stable even if later live state would look exited\"",
    );

    try expectContains(
        runtime_kretprobe_loader,
        "test \"runtime kretprobe loader bridges the shared request lifecycle without widening registration claims\"",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "test \"runtime kretprobe loader keeps initialized-stage shared contract plans explicit\"",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "test \"runtime kretprobe loader keeps initialized shared-request snapshots stable across later selftest activity\"",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "test \"runtime kretprobe loader keeps selftest-complete shared-request snapshots stable across later exit activity\"",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "test \"runtime kretprobe loader surfaces prepared shared selftest-hook drift before any live registration claim\"",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "test \"runtime kretprobe loader rejects prepared shared runtime-substrate drift before any live registration claim\"",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "test \"runtime kretprobe loader rejects prepared shared allocator and init-flow drift before any live registration claim\"",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "test \"runtime kretprobe loader keeps shared release failures from desynchronizing loader state\"",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "test \"runtime kretprobe loader surfaces shared request drift before any live registration claim\"",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "test \"runtime kretprobe loader rejects shared-load-plan snapshot drift\"",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "test \"runtime kretprobe loader rejects non-prepared shared requests before any live registration claim\"",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "try std.testing.expectError(error.InvalidSelftestHookEvidence, loader.requestSharedRuntimeLoad(&shared_request));",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "try std.testing.expectError(error.LoaderNotRequired, loader.requestSharedRuntimeLoad(&shared_request));",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, pending_plan.init_flow.handoff_stage);",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, pending_plan.init_flow.handoff_stage);",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "try std.testing.expectEqual(LoaderStage.released_without_substrate, loader.stage());",
    );
    try expectContains(
        runtime_kretprobe_loader,
        "try std.testing.expectEqual(runtime_loader.RequestState.released_without_substrate, shared_request.state);",
    );
    try expectContains(
        runtime_kretprobe_sample,
        "test \"kretprobe sample preserves initialized-stage failed-exit state until the active probe drains before selftest\"",
    );
    try expectContains(
        runtime_kretprobe_sample,
        "test \"kretprobe sample preserves failed-exit state until the active probe drains after selftest\"",
    );
    try expectContains(
        runtime_kretprobe_sample,
        "try std.testing.expectError(error.OutstandingProbeInstance, module.exit());",
    );
    try expectContains(
        runtime_kretprobe_diff,
        "test \"runtime kretprobe diff gate keeps maxactive pressure and nmissed explicit\"",
    );
    try expectContains(
        runtime_kretprobe_diff,
        "test \"runtime kretprobe diff gate keeps overlapping entry stamps distinct under concurrent load\"",
    );
    try expectContains(
        runtime_kretprobe_diff,
        "try std.testing.expectEqual(@as(i64, 140), outer.duration_ns);",
    );

    try expectContains(
        runtime_kretprobe_module,
        "test \"runtime kretprobe sample preserves summary state across failed exit until the active probe drains\"",
    );
    try expectContains(
        runtime_kretprobe_module,
        "test \"runtime kretprobe sample preserves selftest-ready failed-exit summary state until the active probe drains\"",
    );
    try expectContains(
        runtime_kretprobe_module,
        "test \"runtime kretprobe sample preserves maxactive-overflow summary state until the active probe drains\"",
    );
    try expectContains(
        runtime_kretprobe_module,
        "test \"runtime kretprobe sample preserves selftest-ready maxactive-overflow state until the active probe drains\"",
    );
    try expectContains(
        runtime_kretprobe_module,
        "try std.testing.expectError(error.OutstandingProbeInstance, module.exit());",
    );
    try expectContains(
        runtime_kretprobe_module,
        "try std.testing.expectError(error.MaxactiveExceeded, module.entryHandler(true, 420));",
    );
}
