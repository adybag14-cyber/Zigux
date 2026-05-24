const std = @import("std");

const BoundarySummary = struct {
    metadata_only_fields: []const []const u8,
    ready_states: []const []const u8,
    blocked_live_markers: []const []const u8,
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
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    surveyed_commit: []const u8,
    required_features: []const []const u8,
    recommended_destinations: []const []const u8,
    shared_loader_surfaces: []const []const u8,
    boundary_summary: BoundarySummary,
    roadmap_gap_summary: RoadmapGapSummary,
    ownership_map: []const OwnershipEntry,
};

fn readRepoFileAlloc(path: []const u8, max_bytes: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        std.testing.allocator,
        .limited(max_bytes),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase9 runtime-loader initcall and registration boundary survey matches the shared metadata-only packet" {
    const manifest_json = try readRepoFileAlloc(
        "zigux/tests/runtime_loader_initcall_registration_manifest.json",
        32 * 1024,
    );
    defer std.testing.allocator.free(manifest_json);

    const survey_note = try readRepoFileAlloc(
        "Documentation/zigux/phase9-runtime-loader-initcall-registration-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(survey_note);

    const runtime_loader_contract = try readRepoFileAlloc(
        "zigux/kernel/runtime_loader_contract.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(runtime_loader_contract);

    const runtime_loader = try readRepoFileAlloc(
        "zigux/kernel/runtime_loader.zig",
        48 * 1024,
    );
    defer std.testing.allocator.free(runtime_loader);

    const boundary_guard = try readRepoFileAlloc(
        "zigux/kernel/runtime_loader_command_env_boundary_guard.zig",
        48 * 1024,
    );
    defer std.testing.allocator.free(boundary_guard);

    const phase9_build = try readRepoFileAlloc(
        "zigux/tests/phase9_build.zig",
        48 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();
    const manifest = parsed.value;

    try std.testing.expectEqualStrings("P9-L13", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expectEqualStrings(
        "2026-05-24-runtime-loader-initcall-registration-boundary",
        manifest.surveyed_commit,
    );
    try std.testing.expectEqual(@as(usize, 3), manifest.required_features.len);
    try std.testing.expectEqualStrings("first loadable Zigux runtime modules", manifest.required_features[0]);
    try std.testing.expectEqualStrings("selftest hooks", manifest.required_features[1]);
    try std.testing.expectEqualStrings("runtime module lifecycle parity", manifest.required_features[2]);
    try std.testing.expectEqual(@as(usize, 2), manifest.recommended_destinations.len);
    try std.testing.expectEqualStrings("zigux/tests/runtime_*", manifest.recommended_destinations[0]);
    try std.testing.expectEqualStrings("samples/zigux/runtime_*", manifest.recommended_destinations[1]);
    try std.testing.expectEqual(@as(usize, 6), manifest.shared_loader_surfaces.len);
    try std.testing.expectEqual(@as(usize, 4), manifest.boundary_summary.metadata_only_fields.len);
    try std.testing.expectEqual(@as(usize, 2), manifest.boundary_summary.ready_states.len);
    try std.testing.expectEqual(@as(usize, 8), manifest.boundary_summary.blocked_live_markers.len);
    try std.testing.expectEqual(@as(usize, 9), manifest.ownership_map.len);

    try std.testing.expectEqualStrings(
        "first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity",
        manifest.roadmap_gap_summary.roadmap_phase_goal,
    );
    try std.testing.expect(std.mem.indexOf(
        u8,
        manifest.roadmap_gap_summary.landed_pilot_state,
        "metadata packet",
    ) != null);
    try std.testing.expect(std.mem.indexOf(
        u8,
        manifest.roadmap_gap_summary.missing_capability,
        "runtime registration callbacks",
    ) != null);

    try expectContains(survey_note, "`PHASE9_STATUS=active`");
    try expectContains(survey_note, "`PHASE9_SLICE=runtime-loader-initcall-registration-boundary`");
    try expectContains(survey_note, "`PHASE9_LANE_KEY=P9-L13`");
    try expectContains(survey_note, "`PHASE9_SURVEYED_COMMIT=2026-05-24-runtime-loader-initcall-registration-boundary`");
    try expectContains(survey_note, "`zigux/kernel/runtime_loader_contract.zig`");
    try expectContains(survey_note, "`zigux/kernel/runtime_loader.zig`");
    try expectContains(survey_note, "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`");
    try expectContains(survey_note, "`zigux/tests/runtime_loader_allocator_init_flow.zig`");
    try expectContains(survey_note, "`zigux/tests/phase9_build.zig`");
    try expectContains(survey_note, "`entry_symbol` and `exit_symbol` explicit");
    try expectContains(survey_note, "`PreparedRequest` keeps the shared request state bounded");
    try expectContains(survey_note, "`module_init(`");
    try expectContains(survey_note, "`module_exit(`");
    try expectContains(survey_note, "`register_kretprobe(`");
    try expectContains(survey_note, "`tracepoint_probe_register(`");
    try expectContains(survey_note, "metadata-only and pre-execution boundary");

    try expectContains(runtime_loader_contract, "entry_symbol");
    try expectContains(runtime_loader_contract, "exit_symbol");
    try expectContains(runtime_loader_contract, "pub fn readyForRuntimeLoad");
    try expectContains(runtime_loader_contract, ".initialized => self.selftest_runs == 0");
    try expectContains(runtime_loader_contract, ".selftest_complete => self.selftest_runs == 1");
    try expectContains(runtime_loader_contract, "LoadPlan keeps blocked registration-summary surfaces out of the shared request contract");
    try expectContains(runtime_loader_contract, "register_api");
    try expectContains(runtime_loader_contract, "unregister_api");

    try expectContains(runtime_loader, "pub const PreparedRequest");
    try expectContains(runtime_loader, "pub fn prepareRequest");
    try expectContains(runtime_loader, "pub fn requestRuntimeLoad");
    try expectContains(runtime_loader, "pub fn releaseWithoutSubstrate");
    try expectContains(runtime_loader, "waiting_on_runtime_substrate");
    try expectContains(runtime_loader, "released_without_substrate");
    try expectContains(runtime_loader, "error.InvalidLoaderState");

    try expectContains(boundary_guard, "shared runtime loader surface rejects live initcall and runtime registration bleed-through");
    try expectContains(boundary_guard, "module_init(");
    try expectContains(boundary_guard, "module_exit(");
    try expectContains(boundary_guard, "register_kretprobe(");
    try expectContains(boundary_guard, "unregister_kretprobe(");
    try expectContains(boundary_guard, "register_trace_");
    try expectContains(boundary_guard, "tracepoint_probe_register(");

    try expectContains(phase9_build, "phase9-runtime-loader-contract-tests");
    try expectContains(phase9_build, "phase9-runtime-loader-command-env-boundary-guard-tests");
    try expectContains(phase9_build, "phase9-runtime-loader-shared-tests");
}
