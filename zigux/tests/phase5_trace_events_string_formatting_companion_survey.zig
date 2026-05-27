const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 5 trace-events string-formatting survey keeps the companion markers explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const companion = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/trace_events_string_formatting_sample.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(companion);

    const required_markers = [_][]const u8{
        "pub const SampleFocus = enum {",
        "string_selection,",
        "formatted_message,",
        "bounded_destination_discipline,",
        "non_allocating_runtime_safe,",
        "\"iter={d}\"",
        "\"{s} iter={d}\"",
        "runStringFormattingCycleReplay",
        "One ring to rule them all",
    };
    for (required_markers) |marker| {
        try expectContains(companion, marker);
    }
}

test "phase 5 trace-events string-formatting survey keeps the focused replay aligned with the live companion" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const replay = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "zigux/tests/phase5_trace_events_string_formatting_companion.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(replay);

    const required_markers = [_][]const u8{
        "const companion = @import(\"trace_events_string_formatting_sample\");",
        "phase 5 trace-events string-formatting companion keeps the selected-string and formatting anchor reviewable",
        "phase 5 trace-events string-formatting companion keeps modulo string replay and exact-fit boundaries explicit",
        "runStringFormattingCycleReplay",
        "formatSelectedIterationMessageInto",
        "One ring to rule them all iter=9",
    };
    for (required_markers) |marker| {
        try expectContains(replay, marker);
    }
}
