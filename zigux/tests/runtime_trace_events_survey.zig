const std = @import("std");

const SurveySummary = struct {
    direct_runtime_trace_events_test_files: usize,
    surviving_sample_family_files: usize,
    survey_note_present: bool,
    module_slice_present: bool,
};

const SamplePacketSummary = struct {
    direct_sample: []const u8,
    companion_files: []const []const u8,
    selftest_hook_marker: []const u8,
    lifecycle_marker: []const u8,
};

const ModuleSliceAlignment = struct {
    module_slice_path: []const u8,
    survey_note_path: []const u8,
    manifest_path: []const u8,
    alignment_focus: []const u8,
};

const RoadmapGapSummary = struct {
    roadmap_phase_goal: []const u8,
    landed_pilot_state: []const u8,
    missing_capability: []const u8,
    next_gate: []const u8,
};

const OwnershipEntry = struct {
    surface: []const u8,
    role: []const u8,
    owner: []const u8,
    boundary: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    sample_packet_summary: SamplePacketSummary,
    module_slice_alignment: ModuleSliceAlignment,
    roadmap_gap_summary: RoadmapGapSummary,
    ownership_map: []const OwnershipEntry,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectSurveyedCommitMarker(note: []const u8, surveyed_commit: []const u8) !void {
    var marker_buffer: [96]u8 = undefined;
    const marker = try std.fmt.bufPrint(&marker_buffer, "PHASE9_SURVEYED_COMMIT={s}", .{surveyed_commit});
    try expectContains(note, marker);
}

test "phase9 trace-events survey packet matches the narrow current-master pilot-module story" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const cwd = std.Io.Dir.cwd();

    const manifest_json = try cwd.readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_trace_events_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try cwd.readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-trace-events-survey.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(survey_note);

    const module_slice_note = try cwd.readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(module_slice_note);

    const sequencing_note = try cwd.readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
        std.testing.allocator,
        .limited(48 * 1024),
    );
    defer std.testing.allocator.free(sequencing_note);

    const workflow_file = try cwd.readFileAlloc(
        io_instance.io(),
        ".github/workflows/zigux-bootstrap.yml",
        std.testing.allocator,
        .limited(48 * 1024),
    );
    defer std.testing.allocator.free(workflow_file);

    const sample_file = try cwd.readFileAlloc(
        io_instance.io(),
        "samples/zigux/runtime_trace_events.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(sample_file);

    const fail_closed_file = try cwd.readFileAlloc(
        io_instance.io(),
        "samples/zigux/runtime_trace_events_unregistered_gate.zig",
        std.testing.allocator,
        .limited(48 * 1024),
    );
    defer std.testing.allocator.free(fail_closed_file);

    const exit_guard_file = try cwd.readFileAlloc(
        io_instance.io(),
        "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
        std.testing.allocator,
        .limited(48 * 1024),
    );
    defer std.testing.allocator.free(exit_guard_file);

    const reentry_file = try cwd.readFileAlloc(
        io_instance.io(),
        "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
        std.testing.allocator,
        .limited(64 * 1024),
    );
    defer std.testing.allocator.free(reentry_file);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P9-L09", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expectEqualStrings("70542337d15e9f26941f6a247da00077dddcebe8", manifest.surveyed_commit);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("zigux/tests/runtime_*", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_*", manifest.roadmap_destinations[1]);

    try std.testing.expectEqual(@as(usize, 2), manifest.survey_summary.direct_runtime_trace_events_test_files);
    try std.testing.expectEqual(@as(usize, 4), manifest.survey_summary.surviving_sample_family_files);
    try std.testing.expect(manifest.survey_summary.survey_note_present);
    try std.testing.expect(manifest.survey_summary.module_slice_present);

    try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events.zig", manifest.sample_packet_summary.direct_sample);
    try std.testing.expectEqual(@as(usize, 3), manifest.sample_packet_summary.companion_files.len);
    try std.testing.expectEqualStrings(
        "samples/zigux/runtime_trace_events_unregistered_gate.zig",
        manifest.sample_packet_summary.companion_files[0],
    );
    try std.testing.expectEqualStrings(
        "samples/zigux/runtime_trace_events_exit_rollback_guard.zig",
        manifest.sample_packet_summary.companion_files[1],
    );
    try std.testing.expectEqualStrings(
        "samples/zigux/runtime_trace_events_registration_reentry_gate.zig",
        manifest.sample_packet_summary.companion_files[2],
    );
    try std.testing.expectEqualStrings(".provides_selftest_hook = true", manifest.sample_packet_summary.selftest_hook_marker);
    try std.testing.expectEqualStrings(
        "initialized, selftest_complete, and exited lifecycle tracking",
        manifest.sample_packet_summary.lifecycle_marker,
    );

    try std.testing.expectEqualStrings(
        "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
        manifest.module_slice_alignment.module_slice_path,
    );
    try std.testing.expectEqualStrings(
        "Documentation/zigux/phase9-runtime-trace-events-survey.md",
        manifest.module_slice_alignment.survey_note_path,
    );
    try std.testing.expectEqualStrings(
        "zigux/tests/runtime_trace_events_manifest.json",
        manifest.module_slice_alignment.manifest_path,
    );
    try std.testing.expectEqualStrings(
        "sample-local pilot-module reviewability rather than returned shared runtime-loader parity",
        manifest.module_slice_alignment.alignment_focus,
    );

    try std.testing.expectEqualStrings(
        "first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity",
        manifest.roadmap_gap_summary.roadmap_phase_goal,
    );
    try std.testing.expectEqualStrings(
        "narrow trace-events sample packet plus family-local survey witness",
        manifest.roadmap_gap_summary.landed_pilot_state,
    );
    try std.testing.expectEqualStrings(
        "broader shared runtime-loader, shared build route, and shared runtime_* replay family remain absent on current master",
        manifest.roadmap_gap_summary.missing_capability,
    );
    try std.testing.expectEqualStrings(
        "keep the survey note, manifest, survey gate, and module-slice aligned with the surviving sample family while shared loader work stays parked",
        manifest.roadmap_gap_summary.next_gate,
    );

    try std.testing.expectEqual(@as(usize, 6), manifest.ownership_map.len);
    try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-trace-events-survey.md", manifest.ownership_map[0].surface);
    try std.testing.expectEqualStrings("survey_note", manifest.ownership_map[0].role);
    try std.testing.expectEqualStrings("P9-L09", manifest.ownership_map[0].owner);
    try std.testing.expectEqualStrings("zigux/tests/runtime_trace_events_manifest.json", manifest.ownership_map[1].surface);
    try std.testing.expectEqualStrings("packet_truth_manifest", manifest.ownership_map[1].role);
    try std.testing.expectEqualStrings("zigux/tests/runtime_trace_events_survey.zig", manifest.ownership_map[2].surface);
    try std.testing.expectEqualStrings("survey_gate", manifest.ownership_map[2].role);
    try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-trace-events-module-slice.md", manifest.ownership_map[3].surface);
    try std.testing.expectEqualStrings("module_slice_note", manifest.ownership_map[3].role);
    try std.testing.expectEqualStrings("Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md", manifest.ownership_map[4].surface);
    try std.testing.expectEqualStrings("adjacent_shared_reminder", manifest.ownership_map[4].role);
    try std.testing.expectEqualStrings("P9-L11", manifest.ownership_map[4].owner);
    try std.testing.expectEqualStrings(".github/workflows/zigux-bootstrap.yml", manifest.ownership_map[5].surface);
    try std.testing.expectEqualStrings("adjacent_shared_workflow_guard", manifest.ownership_map[5].role);
    try std.testing.expectEqualStrings("P9-L11", manifest.ownership_map[5].owner);

    try expectSurveyedCommitMarker(survey_note, manifest.surveyed_commit);
    try expectContains(survey_note, "`samples/zigux/runtime_trace_events.zig`");
    try expectContains(survey_note, "`samples/zigux/runtime_trace_events_unregistered_gate.zig`");
    try expectContains(survey_note, "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`");
    try expectContains(survey_note, "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_trace_events_manifest.json`");
    try expectContains(survey_note, "`zigux/tests/runtime_trace_events_survey.zig`");
    try expectContains(survey_note, ".provides_selftest_hook = true");
    try expectContains(survey_note, "initialized, selftest_complete, and exited lifecycle tracking");
    try expectContains(survey_note, "direct family-local `zigux/tests/runtime_*` witness");
    try expectContains(survey_note, "`zigux/tests/phase9_build.zig`");
    try expectContains(survey_note, "`zigux/kernel/runtime_loader.zig`");
    try expectContains(survey_note, "`zigux/kernel/runtime_loader_contract.zig`");
    try expectContains(survey_note, "Do not invent `validate-phase9.py`");

    try expectContains(module_slice_note, "`Documentation/zigux/phase9-runtime-trace-events-survey.md`");
    try expectContains(module_slice_note, "`zigux/tests/runtime_trace_events_manifest.json`");
    try expectContains(module_slice_note, "`zigux/tests/runtime_trace_events_survey.zig`");
    try expectContains(module_slice_note, ".provides_selftest_hook = true");
    try expectContains(module_slice_note, "initialized, selftest_complete, and exited lifecycle tracking");
    try expectContains(module_slice_note, "sample-local pilot-module reviewability");
    try expectContains(module_slice_note, "broader shared runtime-loader packet");
    try expectContains(module_slice_note, "`zigux/tests/phase9_build.zig`");
    try expectContains(module_slice_note, "Do not invent `validate-phase9.py`");

    try expectContains(sequencing_note, "`samples/zigux/runtime_trace_events.zig`");
    try expectContains(sequencing_note, "`samples/zigux/runtime_trace_events_unregistered_gate.zig`");
    try expectContains(sequencing_note, "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`");
    try expectContains(sequencing_note, "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`");
    try expectContains(sequencing_note, "does not currently expose the broader shared runtime-loader packet");

    try expectContains(workflow_file, "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test");
    try expectContains(workflow_file, "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py");
    try expectContains(workflow_file, "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test");
    try expectContains(workflow_file, "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py");
    try expectContains(workflow_file, "zig test samples/zigux/runtime_trace_events.zig");
    try expectContains(workflow_file, "zig test samples/zigux/runtime_trace_events_unregistered_gate.zig");
    try expectContains(workflow_file, "zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig");
    try expectContains(workflow_file, "zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig");
    try expectContains(workflow_file, "zig test zigux/tests/runtime_trace_events_survey.zig");

    try expectContains(sample_file, ".provides_selftest_hook = true");
    try expectContains(sample_file, "pub fn runSelftest(self: *Self) !EmissionSummary {");
    try expectContains(sample_file, "pub fn exit(self: *Self) !void {");
    try expectContains(sample_file, "test \"trace-events sample rejects duplicate function-thread registration\" {");
    try expectContains(sample_file, "test \"trace-events sample preserves initialized summary across direct exit without selftest\" {");
    try expectContains(sample_file, "try std.testing.expectEqual(ModuleStage.initialized, before_exit.stage);");
    try expectContains(sample_file, "try std.testing.expectEqual(@as(usize, 0), before_exit.selftest_runs);");
    try expectContains(sample_file, "try module.exit();");
    try expectContains(sample_file, "const after_exit = module.summary();");
    try expectContains(sample_file, "try std.testing.expectEqual(ModuleStage.exited, after_exit.stage);");
    try expectContains(sample_file, "try std.testing.expectEqual(@as(usize, 1), after_exit.exit_runs);");
    try expectContains(sample_file, "try std.testing.expectEqual(before_exit.total_events, after_exit.total_events);");
    try expectContains(sample_file, "try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());");
    try expectContains(sample_file, "try std.testing.expectError(error.InvalidLifecycleTransition, module.emitMainIteration(9));");
    try expectContains(sample_file, "test \"trace-events sample keeps failed-exit rollback explicit after selftest-ready replay\" {");
    try expectContains(sample_file, "test \"trace-events sample keeps rejected re-selftest rollback explicit\" {");
    try expectContains(sample_file, "try std.testing.expectEqual(ModuleStage.selftest_complete, before_rejected_selftest.stage);");
    try expectContains(sample_file, "try std.testing.expectEqual(@as(usize, 1), before_rejected_selftest.selftest_runs);");
    try expectContains(sample_file, "try std.testing.expectError(error.InvalidLifecycleTransition, module.runSelftest());");

    try expectContains(fail_closed_file, "phase9 trace-events sample keeps unregistered function-thread failures fail-closed");
    try expectContains(exit_guard_file, "phase9 trace-events sample keeps exit rollback explicit after reusable selftest replay");
    try expectContains(reentry_file, "phase9 trace-events sample keeps registration reentry reusable across initialized and selftest_complete stages");
}
