const std = @import("std");

fn readFileAlloc(allocator: std.mem.Allocator, path: []const u8, limit: usize) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        path,
        allocator,
        .limited(limit),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase11 hvc teardown note records close, cleanup, and remove ownership" {
    const note = try readFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-teardown-note.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(note);

    try expectContains(note, "drivers/tty/hvc/hvc_console.c");
    try expectContains(note, "summarizeCloseBoundary()");
    try expectContains(note, "summarizeCleanupHandoff()");
    try expectContains(note, "summarizeRemoveHandoff()");
    try expectContains(note, "HVC_CLOSE_WAIT");
    try expectContains(note, "tty_port_put()");
    try expectContains(note, "tty_vhangup()");
    try expectContains(note, "tty_kref_put()");
    try expectContains(note, "host-free");
    try expectContains(note, "host-backed hypervisor teardown");
}

test "phase11 hvc teardown note stays referenced by the driver-local slice and matrix" {
    const slice = try readFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(slice);

    const matrix = try readFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(matrix);

    try expectContains(slice, "phase11-hvc-console-teardown-note.md");
    try expectContains(slice, "driver-local note");
    try expectContains(matrix, "phase11-hvc-console-teardown-note.md");
    try expectContains(matrix, "driver-local teardown handoff anchor");
    try expectContains(matrix, "close, cleanup, and remove ownership split");
}