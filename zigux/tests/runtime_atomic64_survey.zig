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
    const manifest_json = try readRepoFileAlloc(std.testing.allocator, "zigux/tests/runtime_atomic64_manifest.json", 64 * 1024);
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try readRepoFileAlloc(std.testing.allocator, "Documentation/zigux/phase9-runtime-atomic64-survey.md", 32 * 1024);
    defer std.testing.allocator.free(survey_note);

    const module_slice = try readRepoFileAlloc(std.testing.allocator, "Documentation/zigux/phase9-runtime-atomic64-module-slice.md", 32 * 1024);
    defer std.testing.allocator.free(module_slice);

    const runtime_atomic64_loader = try readRepoFileAlloc(std.testing.allocator, "samples/zigux/runtime_atomic64_loader.zig", 128 * 1024);
    defer std.testing.allocator.free(runtime_atomic64_loader);

    const runtime_loader_allocator_init_flow = try readRepoFileAlloc(std.testing.allocator, "zigux/tests/runtime_loader_allocator_init_flow.zig", 128 * 1024);
    defer std.testing.allocator.free(runtime_loader_allocator_init_flow);

    const phase9_build = try readRepoFileAlloc(std.testing.allocator, "zigux/tests/phase9_build.zig", 128 * 1024);
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
        "starter_landed_with_visible_shared_loader_packet",
        manifest.roadmap_gap_summary.landed_pilot_state,
    );
    try std.testing.expectEqualStrings(
        "shared runtime substrate that would turn the bounded atomic64 loader scaffold plus the visible shared loader-facing reminder packet into a real loadable runtime-module path",
        manifest.roadmap_gap_summary.missing_capability,
    );
    try std.testing.expectEqualStrings(
        "loadable Phase 9 runtime atomic64 pilot module lifecycle parity",
        manifest.roadmap_gap_summary.blocked_deliverable,
    );
    try std.testing.expectEqualStrings(
        "keep the direct atomic64 starter packet explicit, treat the visible shared loader-facing reminder packet as review-only evidence, and leave the broader runtime-substrate blocker explicit",
        manifest.roadmap_gap_summary.next_gate,
    );

    const build_gap = findGap(manifest.gaps, "phase9-build-gate") orelse return error.MissingBuildGap;
    try std.testing.expectEqualStrings("visible_review_only_packet", build_gap.status);
    try std.testing.expectEqualStrings("shared_build_route", build_gap.kind);
    try std.testing.expectEqualStrings("zigux/tests/phase9_build.zig", build_gap.zigux_destination);
    try expectContains(build_gap.why_now, "visible on current master");
    try expectContains(build_gap.why_now, "runtime_loader_gap_survey.zig");

    const survey_gap = findGap(manifest.gaps, "runtime-atomic64-survey-gate") orelse return error.MissingSurveyGap;
    try std.testing.expectEqualStrings("starter_landed", survey_gap.status);
    try std.testing.expectEqualStrings("survey_gate", survey_gap.kind);
    try std.testing.expectEqualStrings("zigux/tests/runtime_atomic64_survey.zig", survey_gap.zigux_destination);

    const loader_gap = findGap(manifest.gaps, "runtime-atomic64-loader-scaffold") orelse return error.MissingLoaderGap;
    try std.testing.expectEqualStrings("starter_landed", loader_gap.status);
    try std.testing.expectEqualStrings("runtime_loader_scaffold", loader_gap.kind);
    try std.testing.expectEqualStrings("samples/zigux/runtime_atomic64_loader.zig", loader_gap.zigux_destination);
    try expectContains(loader_gap.why_now, "entry and exit symbol names");
    try expectContains(loader_gap.why_now, "shared loader-facing reminder packet");

    const substrate_gap = findGap(manifest.gaps, "runtime-atomic64-live-loader-binding") orelse return error.MissingSubstrateGap;
    try std.testing.expectEqualStrings("blocked_on_runtime_substrate", substrate_gap.status);
    try std.testing.expectEqualStrings("runtime_substrate", substrate_gap.kind);
    try std.testing.expectEqualStrings("zigux/kernel/runtime_loader.zig", substrate_gap.zigux_destination);
    try expectContains(substrate_gap.why_now, "broader runtime substrate");

    try expectContains(survey_note, "`PHASE9_STATUS=active`");
    try expectContains(survey_note, "`PHASE9_SLICE=runtime-atomic64-survey`");
    try expectContains(survey_note, "`PHASE9_LANE_KEY=P9-L04`");
    try expectSurveyedCommitMarker(survey_note, manifest.surveyed_commit);
    try expectContains(survey_note, "`samples/zigux/runtime_atomic64.zig`");
    try expectContains(survey_note, "`samples/zigux/runtime_atomic64_loader.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_atomic64_module.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_atomic64_diff.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_atomic64_survey.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_atomic64_manifest.json`");
    try expectContains(survey_note, "`zigux/tests/runtime_loader_allocator_init_flow.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_loader_gap_survey.zig`");
    try expectContains(survey_note, "`zigux/kernel/runtime_loader.zig`");
    try expectContains(survey_note, "`zigux/kernel/runtime_loader_contract.zig`");
    try expectContains(survey_note, "shared-loader reminder surfaces visible");
    try expectContains(survey_note, "visible shared-loader reminder packet");
    try expectContains(survey_note, "not a completed loadable runtime-module path");
    try expectContains(survey_note, "`phase9-runtime-loader-shared-tests`");

    try expectContains(module_slice, "`PHASE9_LANE_KEY=P9-L04`");
    try expectSurveyedCommitMarker(module_slice, manifest.surveyed_commit);
    try expectContains(module_slice, "## Direct Packet");
    try expectContains(module_slice, "## Adjacent Shared Loader-Facing Reminder Packet");
    try expectContains(module_slice, "`samples/zigux/runtime_atomic64_loader.zig`");
    try expectContains(module_slice, "`zigux/tests/runtime_loader_allocator_init_flow.zig`");
    try expectContains(module_slice, "`zigux/tests/runtime_loader_gap_survey.zig`");
    try expectContains(module_slice, "`zigux/tests/phase9_build.zig`");
    try expectContains(module_slice, "`zigux/kernel/runtime_loader.zig`");
    try expectContains(module_slice, "`zigux/kernel/runtime_loader_contract.zig`");
    try expectContains(module_slice, "visible review-only evidence");
    try expectContains(module_slice, "not a completed loadable runtime-module path");

    try expectContains(runtime_atomic64_loader, "runtime atomic64 loader keeps initialized shared-request snapshots stable across later selftest activity");
    try expectContains(runtime_atomic64_loader, "runtime atomic64 loader keeps selftest-complete shared-request snapshots stable across later exit activity");
    try expectContains(runtime_atomic64_loader, "runtime atomic64 loader rejects prepared shared allocator and init-flow drift before any local runtime handoff");
    try expectContains(runtime_atomic64_loader, "runtime atomic64 loader surfaces prepared shared selftest-hook drift before any live atomic64 claim");
    try expectContains(runtime_atomic64_loader, "runtime atomic64 loader keeps shared release failures from desynchronizing loader state");

    try expectContains(runtime_loader_allocator_init_flow, "zigux_runtime_atomic64_init");
    try expectContains(runtime_loader_allocator_init_flow, "zigux_runtime_atomic64_exit");
    try expectContains(runtime_loader_allocator_init_flow, "phase 9 runtime loader allocator/init-flow replay keeps selftest-complete prepared snapshots stable even if later live state would look exited");

    try expectContains(phase9_build, "runtime_atomic64_loader.zig");
    try expectContains(phase9_build, "runtime_loader_allocator_init_flow.zig");
    try expectContains(phase9_build, "runtime_loader_gap_survey.zig");
    try expectContains(phase9_build, "../kernel/runtime_loader_contract.zig");
    try expectContains(phase9_build, "../kernel/runtime_loader.zig");
    try expectContains(phase9_build, "phase9-runtime-loader-shared-tests");
}
