const std = @import("std");

const SurveyManifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    roadmap_anchor: []const u8,
    loader_surface: []const u8,
    current_master_state: []const u8,
    next_bounded_step: []const u8,
};

const survey_manifest = SurveyManifest{
    .lane_key = "P9-L09",
    .phase = "Phase 9",
    .roadmap_anchor = "samples/trace_events/trace-events-sample.c",
    .loader_surface = "samples/zigux/runtime_trace_events_loader.zig",
    .current_master_state = "trace_events_loader_exists_but_phase9_build_omits_a_dedicated_loader_route",
    .next_bounded_step = "Add a dedicated phase9 runtime trace-events loader test route to zigux/tests/phase9_build.zig and fold it into the phase9 runtime trace-events aggregate without widening beyond the sample-side pilot-module packet.",
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn readRepoFile(allocator: std.mem.Allocator, path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(256 * 1024));
}

test "phase9 trace-events loader gap survey keeps the current pilot-module delta explicit" {
    const allocator = std.testing.allocator;

    const loader_file = try readRepoFile(
        allocator,
        "samples/zigux/runtime_trace_events_loader.zig",
    );
    defer allocator.free(loader_file);

    const sample_file = try readRepoFile(
        allocator,
        "samples/zigux/runtime_trace_events.zig",
    );
    defer allocator.free(sample_file);

    const phase9_build_file = try readRepoFile(
        allocator,
        "zigux/tests/phase9_build.zig",
    );
    defer allocator.free(phase9_build_file);

    const runtime_trace_events_survey = try readRepoFile(
        allocator,
        "zigux/tests/runtime_trace_events_survey.zig",
    );
    defer allocator.free(runtime_trace_events_survey);

    const samples_readme = try readRepoFile(allocator, "samples/zigux/README.md");
    defer allocator.free(samples_readme);

    try std.testing.expectEqualStrings("P9-L09", survey_manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", survey_manifest.phase);
    try std.testing.expectEqualStrings(
        "samples/trace_events/trace-events-sample.c",
        survey_manifest.roadmap_anchor,
    );
    try std.testing.expectEqualStrings(
        "samples/zigux/runtime_trace_events_loader.zig",
        survey_manifest.loader_surface,
    );
    try std.testing.expectEqualStrings(
        "trace_events_loader_exists_but_phase9_build_omits_a_dedicated_loader_route",
        survey_manifest.current_master_state,
    );

    try expectContains(sample_file, ".requires_runtime_substrate = true");
    try expectContains(sample_file, ".provides_selftest_hook = true");
    try expectContains(loader_file, "const runtime_trace_events_sample = @import(\"runtime_trace_events_sample\");");
    try expectContains(loader_file, "const runtime_loader = @import(\"runtime_loader\");");
    try expectContains(loader_file, "\"zigux_runtime_trace_events_init\"");
    try expectContains(loader_file, "\"zigux_runtime_trace_events_exit\"");
    try expectContains(loader_file, "test \"runtime trace-events loader keeps selftest-complete shared contract plans explicit\" {");
    try expectContains(loader_file, "test \"runtime trace-events loader keeps initialized-stage shared requests blocked by the current loader family contract\" {");

    try expectContains(phase9_build_file, "\"phase9-runtime-bitmap-loader-tests\"");
    try expectContains(phase9_build_file, "\"phase9-runtime-kretprobe-loader-tests\"");
    try expectContains(phase9_build_file, "runtime_trace_events_loader_substrate_drift.zig");
    try expectContains(phase9_build_file, "\"phase9-runtime-trace-events-tests\"");
    try expectNotContains(phase9_build_file, "\"phase9-runtime-trace-events-loader-tests\"");
    try expectNotContains(phase9_build_file, "../../samples/zigux/runtime_trace_events_loader.zig");

    try expectContains(runtime_trace_events_survey, "sample-local pilot-module reviewability rather than returned shared runtime-loader parity");
    try expectContains(runtime_trace_events_survey, "\"phase9-runtime-trace-events-loader-substrate-drift-tests\"");
    try expectNotContains(runtime_trace_events_survey, "\"phase9-runtime-trace-events-loader-tests\"");

    try expectContains(samples_readme, "`samples/zigux/runtime_trace_events_loader.zig`");
    try expectContains(samples_readme, "historical wider-family vocabulary");
    try expectContains(samples_readme, "`zigux/tests/phase9_build.zig` shard");
}
