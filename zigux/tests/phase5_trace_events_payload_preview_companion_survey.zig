const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 5 trace-events payload-preview survey keeps the sample-owned checks explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const sample = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/trace_events_payload_preview_contract.zig",
        std.testing.allocator,
        .limited(24 * 1024),
    );
    defer std.testing.allocator.free(sample);

    const required_markers = [_][]const u8{
        "pub const linux_anchor = \"samples/trace_events/trace-events-sample.c\";",
        "pub const SampleFocus = enum {",
        ".payload_shape,",
        ".string_selection,",
        ".formatted_message,",
        ".conditional_event_families,",
        ".function_callback_registration,",
        ".ownership_and_lifetime,",
        "pub fn referencePattern() PayloadBoundaryContract {",
        ".event_family_count = 6,",
        ".callback_family_count = 2,",
        ".preserves_initialized_stage = true,",
        ".conditional_paths_checked = true,",
        ".vararg_payload_path_checked = true,",
        ".relative_location_path_checked = true,",
        "\"trace-events payload-preview companion keeps the anchor and focus order explicit\"",
        "\"trace-events payload-preview companion keeps the modulo-selected payload ladder explicit\"",
        "\"trace-events payload-preview companion keeps the largest bounded preview case explicit\"",
        "\"One ring to rule them all\"",
        "\"iter=4\"",
    };
    for (required_markers) |marker| {
        try expectContains(sample, marker);
    }
}

test "phase 5 trace-events payload-preview survey keeps the shared phase5 build route aware of the companion checks" {
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
        "../../samples/zigux/trace_events_payload_preview_contract.zig",
        "\"phase5-trace-events-payload-preview-companion-tests\"",
        "\"phase5-trace-events-payload-preview-companion\"",
        "Run the Phase 5 trace-events payload-preview companion checks",
        "test_step.dependOn(&run_phase5_trace_events_payload_preview_companion_tests.step);",
    };
    for (required_markers) |marker| {
        try expectContains(build_file, marker);
    }
}
