const std = @import("std");

const SurveySummary = struct {
    trace_events_sample_c_lines: usize,
    preexisting_runtime_trace_events_test_files: usize,
    preexisting_runtime_trace_events_sample_present: bool,
    runtime_trace_events_loader_present: bool,
    preexisting_phase9_build_present: bool,
    preexisting_runtime_trace_events_doc_present: bool,
    preexisting_runtime_trace_events_summary_surface_present: bool,
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
    gaps: []const Gap,
};

fn isAllowedStatus(status: []const u8) bool {
    return std.mem.eql(u8, status, "starter_landed") or
        std.mem.eql(u8, status, "ready_next") or
        std.mem.eql(u8, status, "blocked_on_runtime_substrate");
}

fn readWorkspaceFile(
    io: anytype,
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(limit));
}

test "phase 9 runtime trace-events survey manifest stays anchored to the survey lane while recording the landed diff gate and blocker" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/runtime_trace_events_manifest.json",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P9-L09", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 9", manifest.phase);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", manifest.anchor);
    try std.testing.expectEqual(@as(usize, 2), manifest.roadmap_destinations.len);
    try std.testing.expect(manifest.survey_summary.trace_events_sample_c_lines >= 150);
    try std.testing.expectEqual(@as(usize, 3), manifest.survey_summary.preexisting_runtime_trace_events_test_files);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_trace_events_sample_present);
    try std.testing.expect(!manifest.survey_summary.runtime_trace_events_loader_present);
    try std.testing.expect(manifest.survey_summary.preexisting_phase9_build_present);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_trace_events_doc_present);
    try std.testing.expect(manifest.survey_summary.preexisting_runtime_trace_events_summary_surface_present);
    try std.testing.expect(manifest.gaps.len >= 5);

    var runtime_test_destination_count: usize = 0;
    var starter_landed_count: usize = 0;
    var ready_next_count: usize = 0;
    var blocked_count: usize = 0;
    var saw_sample_module = false;
    var saw_diff_gate = false;

    for (manifest.gaps, 0..) |gap, i| {
        try std.testing.expect(gap.id.len > 0);
        try std.testing.expect(gap.kind.len > 0);
        try std.testing.expect(gap.why_now.len > 0);
        try std.testing.expect(isAllowedStatus(gap.status));

        if (std.mem.startsWith(u8, gap.zigux_destination, "zigux/tests/")) {
            runtime_test_destination_count += 1;
        } else {
            try std.testing.expect(std.mem.startsWith(u8, gap.zigux_destination, "samples/zigux/"));
        }

        if (std.mem.eql(u8, gap.status, "ready_next")) {
            ready_next_count += 1;
        } else if (std.mem.eql(u8, gap.status, "starter_landed")) {
            starter_landed_count += 1;
        } else if (std.mem.eql(u8, gap.status, "blocked_on_runtime_substrate")) {
            blocked_count += 1;
        }

        if (std.mem.eql(u8, gap.id, "runtime-trace-events-sample-module")) {
            saw_sample_module = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-trace-events-diff-gate")) {
            saw_diff_gate = true;
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expectEqualStrings("zigux/tests/runtime_trace_events_diff.zig", gap.zigux_destination);
        }
        if (std.mem.eql(u8, gap.id, "runtime-trace-events-module-tests")) {
            try std.testing.expectEqualStrings("starter_landed", gap.status);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "diagnostics-summary") != null);
        }
        if (std.mem.eql(u8, gap.id, "runtime-trace-events-substrate-handoff")) {
            try std.testing.expectEqualStrings("blocked_on_runtime_substrate", gap.status);
            try std.testing.expectEqualStrings("samples/zigux/runtime_trace_events_loader.zig", gap.zigux_destination);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "runtime task ownership") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "polling and event-loop substrate") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "thread creation") != null);
            try std.testing.expect(std.mem.indexOf(u8, gap.why_now, "tracepoint registration parity") != null);
        }

        for (manifest.gaps[i + 1 ..]) |other| {
            try std.testing.expect(!std.mem.eql(u8, gap.id, other.id));
            try std.testing.expect(!std.mem.eql(u8, gap.zigux_destination, other.zigux_destination));
        }
    }

    try std.testing.expect(runtime_test_destination_count >= 4);
    try std.testing.expect(starter_landed_count >= 5);
    try std.testing.expectEqual(@as(usize, 0), ready_next_count);
    try std.testing.expect(blocked_count >= 1);
    try std.testing.expect(saw_sample_module);
    try std.testing.expect(saw_diff_gate);
}

test "phase 9 runtime trace-events docs keep the task and event-loop substrate gap explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const survey_doc = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-trace-events-survey.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(survey_doc);

    const module_doc = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase9-runtime-trace-events-module-slice.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(module_doc);

    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "runtime task ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "polling and event-loop substrate") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "thread creation") != null);
    try std.testing.expect(std.mem.indexOf(u8, survey_doc, "tracepoint-registration lifecycle wiring") != null);

    try std.testing.expect(std.mem.indexOf(u8, module_doc, "runtime task ownership") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "polling and event-loop substrate") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "thread creation") != null);
    try std.testing.expect(std.mem.indexOf(u8, module_doc, "tracepoint-registration lifecycle wiring") != null);
}

test "phase 9 runtime trace-events blocker stays loader-free until the scheduler substrate exists" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const phase9_build = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase9_build.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(phase9_build);

    try std.testing.expectError(
        error.FileNotFound,
        std.Io.Dir.cwd().openFile(
            io_instance.io(),
            "samples/zigux/runtime_trace_events_loader.zig",
            .{},
        ),
    );
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "runtime_trace_events_loader") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-trace-events-loader-tests") == null);
    try std.testing.expect(std.mem.indexOf(u8, phase9_build, "phase9-runtime-trace-events-module-tests") != null);
}
