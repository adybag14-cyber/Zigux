const std = @import("std");

fn readCandidateAlloc(
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    const io = std.testing.io;
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(limit));
}

fn readRepoFile(path: []const u8) ![]u8 {
    return readCandidateAlloc(std.testing.allocator, path, 128 * 1024) catch |err| switch (err) {
        error.FileNotFound => {
            const prefixed = try std.fmt.allocPrint(std.testing.allocator, "../../{s}", .{path});
            defer std.testing.allocator.free(prefixed);
            return readCandidateAlloc(std.testing.allocator, prefixed, 128 * 1024);
        },
        else => return err,
    };
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

    const verify_helper = try readRepoFile("drivers/tty/hvc/hvc_console_verify.zig");
    defer std.testing.allocator.free(verify_helper);

    try expectContains(verify_helper, "targetless_dispatch_with_notifier_sanitized: bool,");
    try expectContains(verify_helper, "const targetless_dispatch_with_notifier_sanitized =");
    try expectContains(verify_helper, "request.sysrq_requested and request.notifier_registered and !request.target_present;");
    try expectContains(verify_helper, ".targetless_dispatch_with_notifier_sanitized = targetless_dispatch_with_notifier_sanitized,");
    try expectContains(verify_helper, "test \"phase11 hvc verify helper keeps registered targetless sysrq fallback sanitized\" {");
    try expectContains(verify_helper, "try std.testing.expect(summary.targetless_dispatch_with_notifier_sanitized);");
    try expectContains(verify_helper, "test \"phase11 hvc verify helper keeps targeted notifier SysRq dispatch explicit\" {");
    try expectContains(verify_helper, "try std.testing.expect(summary.dispatch_allowed);");
    try expectContains(verify_helper, "try std.testing.expect(!summary.literal_fallback_required);");

    const boundary = try readRepoFile("Documentation/zigux/phase11-hvc-verify-helper-boundary.md");
    defer std.testing.allocator.free(boundary);

    try expectContains(boundary, "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge");
    try expectContains(boundary, "`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable");
    try expectContains(boundary, "`targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.");
    try expectContains(boundary, "`targetless_dispatch_with_notifier_sanitized` keeps registered-but-targetless sysrq fallback visible");
    try expectContains(boundary, "the literal-fallback helpers keep the targetless sysrq path without notifier, the sanitized registered-but-targetless sysrq path, and the non-kernel sysrq literal fallback explicit");

    const companion = try readRepoFile("Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md");
    defer std.testing.allocator.free(companion);

    try expectContains(companion, "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`");
    try expectContains(companion, "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`");
    try expectContains(companion, "standalone targetless-unregister witness");
    try expectContains(companion, "separate failure-mode replay");

    const survey = try readRepoFile("Documentation/zigux/phase11-hvc-console-survey.md");
    defer std.testing.allocator.free(survey);

    try expectContains(survey, "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`");
    try expectContains(survey, "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`");
    try expectContains(survey, "standalone targetless-unregister witness pair likewise stays");
    try expectContains(survey, "without promoting itself into the shared three-entry build inventory");

    const matrix = try readRepoFile("Documentation/zigux/phase11-hvc-console-validation-matrix.md");
    defer std.testing.allocator.free(matrix);

    try expectContains(matrix, "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`");
    try expectContains(matrix, "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`");
    try expectContains(matrix, "witness shard now rereads the live starter and the boundary note together");
    try expectContains(matrix, "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet");
}
