const std = @import("std");

fn readCandidateAlloc(
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();

    return std.Io.Dir.cwd().readFileAlloc(io_instance.io(), path, allocator, .limited(limit));
}

fn readRepoFileAlloc(
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    return readCandidateAlloc(allocator, path, limit) catch |err| switch (err) {
        error.FileNotFound => {
            const prefixed = try std.fmt.allocPrint(allocator, "../../{s}", .{path});
            defer allocator.free(prefixed);
            return readCandidateAlloc(allocator, prefixed, limit);
        },
        else => return err,
    };
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

test "phase11 hvc cleanup packet proof keeps cleanup replay markers explicit" {
    const cleanup_replay = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/phase11_hvc_console.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(cleanup_replay);

    const cleanup_companion = try readRepoFileAlloc(
        std.testing.allocator,
        "zigux/tests/phase11_hvc_cleanup.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(cleanup_companion);

    try expectContains(cleanup_replay, "test \"phase11 hvc console keeps hvc_cleanup tty-port release boundaries reviewable\" {");
    try expectContains(cleanup_replay, "try std.testing.expect(final_cleanup.tty_port_put_requested);");
    try expectContains(cleanup_replay, "try std.testing.expect(hangup_cleanup.close_skipped);");
    try expectContains(cleanup_replay, "try std.testing.expect(hangup_cleanup.drops_tty_port_reference);");
    try expectContains(cleanup_companion, "phase11 hvc cleanup");
}

test "phase11 hvc cleanup packet proof keeps teardown notes aligned with the landed cleanup handoff" {
    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    const teardown_note = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-teardown-note.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(teardown_note);

    try expectContains(matrix_doc, "`hvc_cleanup()` tty-port release handoff");
    try expectContains(matrix_doc, "final-close and hangup-driven cleanup handoff assertions inside the shared Phase 11 replay");
    try expectContains(teardown_note, "final-close and hangup-driven cleanup handoff boundaries are now pinned separately from the broader remove packet");
    try expectContains(teardown_note, "close-skipped requests");
    try expectContains(teardown_note, "deferred final release explicit");
}
