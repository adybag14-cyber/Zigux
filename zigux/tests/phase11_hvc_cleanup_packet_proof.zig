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

test "phase11 hvc cleanup packet proof keeps current-head cleanup packet explicit" {
    const survey_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(survey_doc);

    const cleanup_companion = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(cleanup_companion);

    const verify_boundary = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-verify-helper-boundary.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(verify_boundary);

    try expectContains(survey_doc, "`scripts/zigux/check-phase11-hvc-cleanup-current-head.py`");
    try expectContains(
        survey_doc,
        "current public GitHub file-page readback confirms the bounded HVC starter,",
    );
    try expectContains(cleanup_companion, "smaller proof-backed HVC continuity packet reviewable");
    try expectContains(cleanup_companion, "`scripts/zigux/check-phase11-hvc-survey-packet.py`");
    try expectContains(
        verify_boundary,
        "`drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove handoff explicit",
    );
}

test "phase11 hvc cleanup packet proof keeps current-head cleanup handoff markers aligned" {
    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    const verify_boundary = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-verify-helper-boundary.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(verify_boundary);

    try expectContains(
        matrix_doc,
        "the cleanup replay keeps tty-port release boundaries explicit; the verify helper remains present",
    );
    try expectContains(matrix_doc, "keep those handoffs named directly in the matrix");
    try expectContains(matrix_doc, "if one new same-lane wording gap appears");
    try expectContains(
        verify_boundary,
        "`error.CleanupRequiresFinalCloseOrHangup` keeps cleanup-time tty-port release evidence tied to a prior final-close or hangup boundary",
    );
    try expectContains(
        verify_boundary,
        "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.",
    );
}
