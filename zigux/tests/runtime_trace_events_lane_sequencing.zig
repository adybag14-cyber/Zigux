const std = @import("std");

test "phase 9 runtime trace-events sequencing note keeps the shared-loader and trace-events pilot split explicit" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const sequencing_note = try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        "Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md",
        std.testing.allocator,
        .limited(32 * 1024),
    );
    defer std.testing.allocator.free(sequencing_note);

    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "Treat the shared loader lane as the only owner of:") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "`zigux/kernel/runtime_loader.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "`zigux/tests/runtime_loader_allocator_init_flow.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "### Trace-events pilot lane") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "`samples/zigux/runtime_trace_events.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "`samples/zigux/runtime_trace_events_loader.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "`zigux/tests/runtime_trace_events_survey.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "the `phase9-runtime-trace-events-tests` step in `zigux/tests/phase9_build.zig`") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "If a scheduled Phase 9 run is assigned a pilot-family lane") != null);
    try std.testing.expect(std.mem.indexOf(u8, sequencing_note, "If the shared-loader lane is assigned, do not consume pilot-local backlog just because the shared lane has spare room.") != null);
}
