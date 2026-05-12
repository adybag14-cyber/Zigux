const std = @import("std");

const SurveySummary = struct {
    atomic64_test_c_lines: usize,
    preexisting_runtime_test_files: usize,
    preexisting_samples_zigux_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_phase9_doc_present: bool,
};

const RoadmapGapSummary = struct {
    roadmap_phase_goal: []const u8,
    landed_pilot_state: []const u8,
    missing_capability: []const u8,
    blocked_deliverable: []const u8,
    next_gate: []const u8,
};

const Gap = struct {
    id: []const u8,
    status: []const u8,
    kind: []const u8,
    zigux_destination: []const u8,
    why_now: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    anchor: []const u8,
    roadmap_destinations: []const []const u8,
    survey_summary: SurveySummary,
    roadmap_gap_summary: RoadmapGapSummary,
    gaps: []const Gap,
};

fn readRepoFileAlloc(allocator: std.mem.Allocator, path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(max_bytes));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn isLowerHexCommit(commit: []const u8) bool {
    if (commit.len != 40) return false;
    for (commit) |char| {
        if (!((char >= '0' and char <= '9') or (char >= 'a' and char <= 'f'))) return false;
    }
    return true;
}

fn expectSurveyedCommitMarker(text: []const u8, commit: []const u8) !void {
    var marker_buffer: [96]u8 = undefined;
    const marker = try std.fmt.bufPrint(&marker_buffer, "`PHASE9_SURVEYED_COMMIT={s}`", .{commit});
    try expectContains(text, marker);
}

fn findGap(gaps: []const Gap, id: []const u8) ?Gap {
    for (gaps) |gap| {
        if (std.mem.eql(u8, gap.id, id)) return gap;
    }
    return null;
}

test "phase 9 runtime atomic64 survey keeps the manifest and current review packet aligned" {
    const manifest_json = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/runtime_atomic64_manifest.json",
        64 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-atomic64-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    const module_slice = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-atomic64-module-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(module_slice);

    const runtime_atomic64_loader = try readRepoFileAlloc(
        std.testing.allocator,
        "samples/zigux/runtime_atomic64_loader.zig",
        128 * 1024,
    );
    defer std.testing.allocator.free(runtime_atomic64_loader);

    const runtime_loader_allocator_init_flow = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/runtime_loader_allocator_init_flow.zig",
        128 * 1024,
    );
    defer std.testing.allocator.free(runtime_loader_allocator_init_flow);

    const phase9_build = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/phase9_build.zig",
        128 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P9-L04", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expect(isLowerHexCommit(manifest.surveyed_commit));
    try std.testing.expectEqualStrings("lib/atomic64_test.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expectEqualStrings("zigux/tests/runtime_*", manifest.roadmap_destinations[0]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_*", manifest.roadmap_destinations[1]);
    try std.testing.expect(manifest.survey_summary.atomic64_test_c_lines >= 250);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_runtime_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_samples_zigux_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_doc_present);
    try std.testing.expectEqualStrings(
        "first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity",
        manifest.roadmap_gap_summary.roadmap_phase_goal,
    );
    try std.testing.expectEqualStrings(
        "starter_landed_without_loadable_runtime_substrate",
        manifest.roadmap_gap_summary.landed_pilot_state,
    );
    try std.testing.expectEqualStrings(
        "shared runtime substrate that can turn the bounded atomic64 loader scaffold into a real loadable module path",
        manifest.roadmap_gap_summary.missing_capability,
    );
    try std.testing.expectEqualStrings(
        "loadable Phase 9 runtime atomic64 pilot module parity",
        manifest.roadmap_gap_summary.blocked_deliverable,
    );
    try std.testing.expectEqualStrings(
        "keep the loader scaffold and shared-request lifecycle proof explicit until the shared runtime loader substrate can consume the handoff plan",
        manifest.roadmap_gap_summary.next_gate,
    );

    const survey_gap = findGap(manifest.gaps, "runtime-atomic64-survey-gate") orelse return error.MissingSurveyGap;
    try std.testing.expectEqualStrings("starter_landed", survey_gap.status);
    try std.testing.expectEqualStrings("survey_gate", survey_gap.kind);
    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_survey.zig", survey_gap.zigux_destination);

    const loader_gap = findGap(manifest.gaps, "runtime-atomic64-loader-scaffold") orelse return error.MissingLoaderGap;
    try std.testing.expectEqualStrings("starter_landed", loader_gap.status);
    try std.testing.expectEqualStrings("runtime_loader_scaffold", loader_gap.kind);
    try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64_loader.zig", loader_gap.zigux_destination);

    const substrate_gap = findGap(manifest.gaps, "runtime-atomic64-live-loader-binding") orelse return error.MissingSubstrateGap;
    try std.testing.expectEqualStrings("blocked_on_runtime_substrate", substrate_gap.status);
    try std.testing.expectEqualStrings("runtime_substrate", substrate_gap.kind);
    try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", substrate_gap.zigux_destination);

    try expectContains(survey_note, "`PHASE9_STATUS=active`");
    try expectContains(survey_note, "`PHASE9_SLICE=runtime-atomic64-survey`");
    try expectContains(survey_note, "`PHASE9_LANE_KEY=P9-L04`");
    try expectSurveyedCommitMarker(survey_note, manifest.surveyed_commit);
    try expectContains(survey_note, "`samples/zigux/runtime_atomic64.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_atomic64_module.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_atomic64_diff.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_atomic64_survey.zig`");
    try expectContains(survey_note, "`samples/zigux/runtime_atomic64_loader.zig`");
    try expectContains(survey_note, "`zigux/kernel/runtime_loader.zig`");
    try expectContains(survey_note, "`zigux/kernel/runtime_loader_contract.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_loader_allocator_init_flow.zig`");
    try expectContains(survey_note, "`zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`");
    try expectContains(survey_note, "`make -C zigux phase9-runtime-loader-shared-tests`");
    try expectContains(survey_note, "`make -C zigux phase9`");
    try expectContains(survey_note, "adjacent review-only shared loader-facing packet");
    try expectContains(survey_note, "not a completed loadable runtime-module path");

    try expectContains(module_slice, "`PHASE9_LANE_KEY=P9-L04`");
    try expectSurveyedCommitMarker(module_slice, manifest.surveyed_commit);
    try expectContains(module_slice, "`samples/zigux/runtime_atomic64_loader.zig`");
    try expectContains(module_slice, "`zigux/tests/runtime_loader_allocator_init_flow.zig`");
    try expectContains(module_slice, "`zigux/kernel/runtime_loader.zig`");
    try expectContains(module_slice, "`zigux/kernel/runtime_loader_contract.zig`");
    try expectContains(module_slice, "`make -C zigux phase9-runtime-loader-shared-tests`");
    try expectContains(module_slice, "shared request path explicit without implying scheduler-facing substrate closure");

    try expectContains(
        runtime_atomic64_loader,
        "test \"runtime atomic64 loader keeps initialized shared-request snapshots stable across later selftest activity\"",
    );
    try expectContains(
        runtime_atomic64_loader,
        "test \"runtime atomic64 loader keeps selftest-complete shared-request snapshots stable across later exit activity\"",
    );
    try expectContains(
        runtime_atomic64_loader,
        "test \"runtime atomic64 loader rejects prepared shared allocator and init-flow drift before any local runtime handoff\"",
    );
    try expectContains(
        runtime_atomic64_loader,
        "test \"runtime atomic64 loader surfaces prepared shared selftest-hook drift before any live atomic64 claim\"",
    );
    try expectContains(
        runtime_atomic64_loader,
        "test \"runtime atomic64 loader keeps shared release failures from desynchronizing loader state\"",
    );
    try expectContains(
        runtime_atomic64_loader,
        "try std.testing.expectEqual(runtime_loader.HandoffStage.initialized, pending_plan.init_flow.handoff_stage);",
    );
    try expectContains(
        runtime_atomic64_loader,
        "try std.testing.expectEqual(runtime_loader.HandoffStage.selftest_complete, pending_plan.init_flow.handoff_stage);",
    );

    try expectContains(
        runtime_loader_allocator_init_flow,
        "\"runtime_atomic64\", \"lib/atomic64_test.c\", \"zigux_runtime_atomic64_init\", \"zigux_runtime_atomic64_exit\", .caller_provided",
    );
    try expectContains(
        runtime_loader_allocator_init_flow,
        "test \"phase 9 runtime loader allocator/init-flow replay keeps initialized prepared snapshots stable even if later live state would look exited\"",
    );
    try expectContains(
        runtime_loader_allocator_init_flow,
        "test \"phase 9 runtime loader allocator/init-flow replay keeps selftest-complete prepared snapshots stable even if later live state would look exited\"",
    );

    try expectContains(phase9_build, "runtime_atomic64_loader.zig");
    try expectContains(phase9_build, "runtime_loader_allocator_init_flow.zig");
    try expectContains(phase9_build, "\"phase9-runtime-atomic64-loader-tests\"");
    try expectContains(phase9_build, "\"phase9-runtime-loader-shared-tests\"");
    try expectContains(phase9_build, "runtime_atomic64_tests_step.dependOn(&run_runtime_loader_allocator_init_flow_tests.step);");
    try expectContains(phase9_build, "runtime_atomic64_tests_step.dependOn(&run_runtime_loader_gap_survey_tests.step);");
}
