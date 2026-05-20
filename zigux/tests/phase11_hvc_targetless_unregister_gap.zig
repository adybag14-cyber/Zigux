const std = @import("std");

fn readRepoFile(path: []const u8) ![]u8 {
    const io = std.testing.io;
    return std.Io.Dir.cwd().readFileAlloc(
        io,
        path,
        std.testing.allocator,
        .limited(128 * 1024),
    );
}

fn expectContains(contents: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, contents, needle) != null);
}

test "phase11 hvc notifier witness records current-head targetless unregister sanitizer" {
    const driver = try readRepoFile("drivers/tty/hvc/hvc_console.zig");
    defer std.testing.allocator.free(driver);

    try expectContains(driver, "pub const TargetlessNotifierEdgeSummary = struct {");
    try expectContains(driver, "targetless_no_unregister_edge: bool,");
    try expectContains(driver, "targetless_unregister_request_sanitized: bool,");
    try expectContains(driver, ".targetless_no_unregister_edge = request.notifier_registered and !request.target_present and !request.unregister_requested,");
    try expectContains(driver, ".targetless_unregister_request_sanitized = request.notifier_registered and !request.target_present and request.unregister_requested,");
    try expectContains(driver, ".unregister_requested = request.unregister_requested and request.target_present and request.notifier_registered,");
    try expectContains(driver, "test \"phase11 hvc console keeps targetless notifier no-unregister edge reviewable\" {");

    const boundary = try readRepoFile("Documentation/zigux/phase11-hvc-verify-helper-boundary.md");
    defer std.testing.allocator.free(boundary);

    try expectContains(boundary, "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge");
    try expectContains(boundary, "`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable");
    try expectContains(boundary, "`targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.");
    try expectContains(boundary, "the literal-fallback helpers keep both the sanitized targetless sysrq path and the non-kernel sysrq literal fallback explicit");

    const companion = try readRepoFile("Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md");
    defer std.testing.allocator.free(companion);

    try expectContains(companion, "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`");
    try expectContains(companion, "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`");
    try expectContains(companion, "standalone targetless-unregister witness");
    try expectContains(companion, "separate failure-mode replay");
}