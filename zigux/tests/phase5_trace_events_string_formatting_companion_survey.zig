const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 5 trace-events string-formatting survey keeps the sample-owned checks explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const sample = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/trace_events_string_formatting_sample.zig",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(sample);

    const required_markers = [_][]const u8{
        "pub const SampleFocus = enum {",
        ".string_selection,",
        ".formatted_message,",
        ".bounded_destination_discipline,",
        ".non_allocating_runtime_safe,",
        "return std.fmt.bufPrint(destination, \"iter={d}\", .{iteration_count});",
        "\"{s} iter={d}\"",
        "phase 5 trace-events formatting companion keeps the selected-string cue reviewable",
        "phase 5 trace-events formatting companion keeps the modulo-selected string cycle reviewable",
        "phase 5 trace-events formatting companion keeps lifecycle boundaries explicit",
        "phase 5 trace-events formatting companion keeps bounded destination failures explicit",
        "phase 5 trace-events formatting companion keeps selected-string exact-fit boundaries explicit",
        "phase 5 trace-events formatting companion keeps wrapped selected-string exact-fit boundaries explicit",
        "\"One ring to rule them all iter=9\"",
    };
    for (required_markers) |marker| {
        try expectContains(sample, marker);
    }
}

test "phase 5 trace-events string-formatting survey keeps the shared phase5 build route aware of the sample and survey guard" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const build_file = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_build.zig",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(build_file);

    const required_markers = [_][]const u8{
        "../../samples/zigux/trace_events_string_formatting_sample.zig",
        "phase5_trace_events_string_formatting_companion_survey.zig",
        "\"phase5-trace-events-string-formatting-companion-tests\"",
        "\"phase5-trace-events-string-formatting-companion-survey-tests\"",
        "\"phase5-trace-events-string-formatting-companion-survey\"",
        "Run the Phase 5 trace-events string-formatting companion survey guard",
        "test_step.dependOn(&run_phase5_trace_events_string_formatting_companion_tests.step);",
        "test_step.dependOn(&run_phase5_trace_events_string_formatting_companion_survey_tests.step);",
    };
    for (required_markers) |marker| {
        try expectContains(build_file, marker);
    }
}
