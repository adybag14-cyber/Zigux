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

test "phase11 hvc cleanup packet proof keeps missing teardown anchors explicit" {
    const survey_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(survey_doc);

    const companion_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(companion_doc);

    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    try expectContains(survey_doc, "`Documentation/zigux/phase11-hvc-console-teardown-note.md`");
    try expectContains(companion_doc, "`zigux/tests/phase11_hvc_console_manifest.json`");
    try expectContains(companion_doc, "proof-backed HVC continuity packet remains reviewable");
    try expectContains(matrix_doc, "repo-reality gaps instead of returned fallback evidence");
}

test "phase11 hvc cleanup packet proof keeps route boundaries explicit" {
    const survey_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(survey_doc);

    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    try expectContains(survey_doc, "`make -C zigux phase11-validate`");
    try expectContains(survey_doc, "`make -C zigux phase11-hvc-survey`");
    try expectContains(matrix_doc, "`make -C zigux phase11-validate`");
    try expectContains(matrix_doc, "`make -C zigux phase11-hvc-survey`");
}

test "phase11 hvc cleanup packet proof keeps verify-boundary failure modes explicit" {
    const verify_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-verify-helper-boundary.md",
        16 * 1024,
    );
    defer std.testing.allocator.free(verify_doc);

    try expectContains(verify_doc, "`error.CleanupRequiresFinalCloseOrHangup`");
    try expectContains(verify_doc, "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`");
    try expectContains(verify_doc, "`targetless_dispatch_without_notifier`");
}

test "phase11 hvc cleanup packet proof keeps starter teardown helpers tied to matrix evidence" {
    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    const driver = try readRepoFileAlloc(
        std.testing.allocator,
        "drivers/tty/hvc/hvc_console.zig",
        24 * 1024,
    );
    defer std.testing.allocator.free(driver);

    try expectContains(matrix_doc, "flush intent");
    try expectContains(matrix_doc, "`hvc_install()` ownership");
    try expectContains(matrix_doc, "`hvc_cleanup()` tty-port");
    try expectContains(driver, "pub fn summarizeCleanupHandoff(request: CleanupHandoffRequest) CleanupHandoffSummary {");
    try expectContains(driver, "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {");
}

test "phase11 hvc cleanup packet proof keeps close teardown carryover details tied to matrix evidence" {
    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    const driver = try readRepoFileAlloc(
        std.testing.allocator,
        "drivers/tty/hvc/hvc_console.zig",
        24 * 1024,
    );
    defer std.testing.allocator.free(driver);

    try expectContains(matrix_doc, "DTR/RTS shutdown");
    try expectContains(matrix_doc, "`wait_until_sent()` carryover");
    try expectContains(matrix_doc, "`close_wait` ownership");
    try expectContains(matrix_doc, "`port_initialized` clearing");
    try expectContains(driver, "pub const CloseTeardownSummary = struct {");
    try expectContains(driver, "dtr_rts_shutdown: bool,");
    try expectContains(driver, "wait_until_sent_intent: bool,");
    try expectContains(driver, "close_wait_ownership: bool,");
    try expectContains(driver, "port_initialized_cleared: bool,");
    try expectContains(driver, "pub fn summarizeCloseTeardown(request: CloseTeardownRequest) CloseTeardownSummary {");
}

test "phase11 hvc cleanup packet proof keeps newer failure-mode helpers tied to matrix evidence" {
    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        24 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    const driver = try readRepoFileAlloc(
        std.testing.allocator,
        "drivers/tty/hvc/hvc_console.zig",
        24 * 1024,
    );
    defer std.testing.allocator.free(driver);

    try expectContains(matrix_doc, "`hvc_kick()` wakeup-cue");
    try expectContains(matrix_doc, "notifier-irq");
    try expectContains(matrix_doc, "modem-control helper summaries reviewable on current `master`");
    try expectContains(driver, "pub fn summarizeCleanupPrerequisite(");
    try expectContains(driver, ") error{CleanupRequiresFinalCloseOrHangup}!CleanupPrerequisiteSummary {");
    try expectContains(driver, "pub fn summarizeKickWakeupCue(request: KickWakeupCueRequest) KickWakeupCueSummary {");
    try expectContains(driver, "pub fn summarizeNotifierIrqHelper(request: NotifierIrqHelperRequest) NotifierIrqHelperSummary {");
    try expectContains(driver, "pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {");
    try expectContains(driver, "const targetless_hangup_short_circuit = request.notifier_registered and");
    try expectContains(driver, ".targetless_hangup_short_circuit = targetless_hangup_short_circuit,");
    try expectContains(driver, "try std.testing.expect(!active.targetless_hangup_short_circuit);");
    try expectContains(driver, "try std.testing.expect(targetless.targetless_hangup_short_circuit);");
    try expectContains(driver, "try std.testing.expect(!invalid.targetless_hangup_short_circuit);");
}
