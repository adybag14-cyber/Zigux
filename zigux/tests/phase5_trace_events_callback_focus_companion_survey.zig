const std = @import("std");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase 5 trace-events callback-focus survey keeps the sample-owned checks explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const sample = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "samples/zigux/trace_events_callback_focus_contract.zig",
        std.testing.allocator,
        .limited(16 * 1024),
    );
    defer std.testing.allocator.free(sample);

    const required_markers = [_][]const u8{
        "pub const SampleFocus = enum {",
        ".payload_shape,",
        ".string_selection,",
        ".formatted_message,",
        ".conditional_event_families,",
        ".function_callback_registration,",
        ".ownership_and_lifetime,",
        "pub fn anchorFocusOrder() []const SampleFocus {",
        "pub fn callbackBoundaryContract() CallbackBoundaryContract {",
        ".callback_iteration_count = 5,",
        ".total_event_calls_after_recovery = 2,",
        ".registration_depth_after_recovery = 0,",
        ".missing_registration_rejected = true,",
        ".underflow_before_registration_rejected = true,",
        ".double_registration_rejected = true,",
        ".invalid_callback_count_rejected = true,",
        ".outstanding_registration_exit_rejected = true,",
        ".callback_path_checked = true,",
        "callback boundary keeps the same checked focus order as the main anchor replay",
        "callback boundary keeps rollback and registration cues explicit",
    };
    for (required_markers) |marker| {
        try expectContains(sample, marker);
    }
}
