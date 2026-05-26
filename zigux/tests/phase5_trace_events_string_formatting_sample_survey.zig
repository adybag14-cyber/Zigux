const std = @import("std");

const ExactCheck = struct {
    id: []const u8,
    expected: []const u8,
};

const Manifest = struct {
    lane_key: []const u8,
    phase: []const u8,
    anchor: []const u8,
    sample_path: []const u8,
    focused_replay_path: []const u8,
    validation_entrypoints: []const []const u8,
    exact_checks: []const ExactCheck,
    non_goals: []const []const u8,
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 5 trace-events string-formatting survey keeps the bounded companion markers explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const companion = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/trace_events_string_formatting_sample.zig",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(companion);

    const required_markers = [_][]const u8{
        ".anchor = \"samples/trace_events/trace-events-sample.c\"",
        ".requires_runtime_substrate = false",
        ".provides_selfcheck = true",
        "pub fn formatIterationMessageInto(",
        "pub fn formatSelectedIterationMessageInto(",
        "pub fn runStringFormattingCycleReplay(self: *Self) !StringFormattingCycleSummary",
        "\"iter={d}\"",
        "\"{s} iter={d}\"",
        ".string_selection,",
        ".formatted_message,",
        ".bounded_destination_discipline,",
        ".non_allocating_runtime_safe,",
        "\"One ring to rule them all iter=9\"",
    };
    for (required_markers) |marker| {
        try expectContains(companion, marker);
    }
}

test "phase 5 trace-events string-formatting survey keeps the focused replay aligned with the bounded companion" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const replay = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_trace_events_string_formatting_sample.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(replay);

    const required_markers = [_][]const u8{
        "const companion = @import(\"trace_events_string_formatting_sample\");",
        "phase 5 trace-events string-formatting companion keeps the anchor-local formatting idiom reviewable through a focused replay",
        "phase 5 trace-events string-formatting companion keeps exact-fit and wrapped boundaries explicit through the focused replay",
        "descriptor.requires_runtime_substrate",
        "descriptor.provides_selfcheck",
        "\"Gandalf iter=7\"",
        "\"Gandalf iter=2\"",
        "\"One ring to rule them all iter=9\"",
        "sample.replay_runs",
    };
    for (required_markers) |marker| {
        try expectContains(replay, marker);
    }
}

test "phase 5 trace-events string-formatting survey keeps the manifest-backed evidence packet explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const manifest_json = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_trace_events_string_formatting_sample_manifest.json",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(manifest_json);

    const parsed = try std.json.parseFromSlice(Manifest, std.testing.allocator, manifest_json, .{});
    defer parsed.deinit();

    const manifest = parsed.value;
    try std.testing.expectEqualStrings("P5-L17", manifest.lane_key);
    try std.testing.expectEqualStrings("Phase 5", manifest.phase);
    try std.testing.expectEqualStrings("samples/trace_events/trace-events-sample.c", manifest.anchor);
    try std.testing.expectEqualStrings(
        "samples/zigux/trace_events_string_formatting_sample.zig",
        manifest.sample_path,
    );
    try std.testing.expectEqualStrings(
        "zigux/tests/phase5_trace_events_string_formatting_sample.zig",
        manifest.focused_replay_path,
    );
    try std.testing.expectEqual(@as(usize, 3), manifest.validation_entrypoints.len);
    try std.testing.expectEqual(@as(usize, 5), manifest.exact_checks.len);
    try std.testing.expectEqual(@as(usize, 3), manifest.non_goals.len);

    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoints[0], "zig test samples/zigux/trace_events_string_formatting_sample.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoints[1], "phase5_trace_events_string_formatting_sample.zig") != null);
    try std.testing.expect(std.mem.indexOf(u8, manifest.validation_entrypoints[2], "phase5_trace_events_string_formatting_sample_survey.zig") != null);

    var saw_descriptor_anchor = false;
    var saw_selected_string_replay = false;
    var saw_exact_fit_iteration = false;
    var saw_exact_fit_selected_string = false;
    var saw_wrapped_selected_string = false;
    for (manifest.exact_checks) |check| {
        if (std.mem.eql(u8, check.id, "descriptor-anchor")) saw_descriptor_anchor = true;
        if (std.mem.eql(u8, check.id, "selected-string-replay")) saw_selected_string_replay = true;
        if (std.mem.eql(u8, check.id, "exact-fit-iteration")) saw_exact_fit_iteration = true;
        if (std.mem.eql(u8, check.id, "exact-fit-selected-string")) saw_exact_fit_selected_string = true;
        if (std.mem.eql(u8, check.id, "wrapped-selected-string")) saw_wrapped_selected_string = true;
        try std.testing.expect(check.expected.len > 0);
    }

    try std.testing.expect(saw_descriptor_anchor);
    try std.testing.expect(saw_selected_string_replay);
    try std.testing.expect(saw_exact_fit_iteration);
    try std.testing.expect(saw_exact_fit_selected_string);
    try std.testing.expect(saw_wrapped_selected_string);
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[0], "standalone Phase 5 string-helper delivery"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[1], "standalone broad formatting sample delivery"));
    try std.testing.expect(std.mem.eql(u8, manifest.non_goals[2], "runtime trace-events registration parity"));
}
