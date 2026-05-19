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
        "current authenticated contents readback keeps the bounded HVC current-head",
    );
    try expectContains(
        survey_doc,
        "starter-depth packet framed as archival or repo-reality-gap vocabulary until",
    );
    try expectContains(
        survey_doc,
        "`zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey`",
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
        "the current matrix packet now stays aligned with the smaller",
    );
    try expectContains(
        matrix_doc,
        "keep helper-local failure-mode edges reviewable through",
    );
    try expectContains(
        matrix_doc,
        "do not treat the deeper verify helper, sysrq helper, manifest, teardown note,",
    );
    try expectContains(
        matrix_doc,
        "`scripts/zigux/check-phase11-hvc-survey-packet.py` and a dedicated `make -C zigux phase11-hvc-survey` route do not",
    );
    try expectContains(
        verify_boundary,
        "`error.CleanupRequiresFinalCloseOrHangup` keeps cleanup-time tty-port release evidence tied to a prior final-close or hangup boundary",
    );
    try expectContains(
        verify_boundary,
        "`CleanupTrigger.hangup_only` and `CleanupTrigger.final_close_and_hangup` keep the hangup-only and combined cleanup trigger split explicit beside the earlier final-close-only path.",
    );
    try expectContains(
        verify_boundary,
        "`error.NotifierDispatchRequiresTtyRegistration` keeps notifier prerequisite failures explicit instead of implying sysrq-triggered notifier dispatch can occur before tty registration.",
    );
    try expectContains(
        verify_boundary,
        "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge instead of implying notifier callback execution.",
    );
    try expectContains(
        verify_boundary,
        "`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable without claiming that notifier teardown has become live runtime behavior.",
    );
    try expectContains(
        verify_boundary,
        "`targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.",
    );
}

test "phase11 hvc cleanup packet proof keeps starter teardown helpers tied to matrix evidence" {
    const matrix_doc = try readRepoFileAlloc(
        std.testing.allocator,
        "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(matrix_doc);

    const driver = try readRepoFileAlloc(
        std.testing.allocator,
        "drivers/tty/hvc/hvc_console.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(driver);

    try expectContains(matrix_doc, "khvcd sleep-and-reschedule handoff");
    try expectContains(matrix_doc, "`__hvc_poll` drain-order");
    try expectContains(matrix_doc, "`hvc_hangup()` disconnect");
    try expectContains(matrix_doc, "`hvc_remove()` handoff");
    try expectContains(matrix_doc, "`hvc_cleanup()` tty-port release");
    try expectContains(matrix_doc, "targetless notifier, `hvc_kick()` wakeup-cue, notifier-irq, and");
    try expectContains(matrix_doc, "modem-control helper summaries reviewable on current `master`.");

    try expectContains(driver, "pub fn summarizeKhvcdSleepHandoff(request: KhvcdSleepRequest) KhvcdSleepSummary {");
    try expectContains(driver, "pub fn summarizePollDrainOrder(request: PollDrainOrderRequest) PollDrainOrderSummary {");
    try expectContains(driver, "pub fn summarizeHangupDisconnect(request: HangupDisconnectRequest) HangupDisconnectSummary {");
    try expectContains(driver, "pub const RemoveHandoffRequest = struct {");
    try expectContains(driver, "pub fn summarizeRemoveHandoff(request: RemoveHandoffRequest) RemoveHandoffSummary {");
    try expectContains(driver, "pub const CleanupHandoffRequest = struct {");
    try expectContains(driver, "pub fn summarizeCleanupHandoff(request: CleanupHandoffRequest) CleanupHandoffSummary {");
    try expectContains(driver, "pub const TargetlessNotifierEdgeRequest = struct {");
    try expectContains(driver, "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {");
    try expectContains(driver, "pub fn summarizeKickWakeupCue(request: KickWakeupCueRequest) KickWakeupCueSummary {");
    try expectContains(driver, "pub fn summarizeNotifierIrqHelper(request: NotifierIrqHelperRequest) NotifierIrqHelperSummary {");
    try expectContains(driver, "pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {");
    try expectContains(driver, "test \"phase11 hvc console keeps khvcd sleep-and-reschedule handoff reviewable\" {");
    try expectContains(driver, "test \"phase11 hvc console keeps __hvc_poll drain-order summary reviewable\" {");
    try expectContains(driver, "test \"phase11 hvc console keeps active hangup and cleanup ownership handoffs reviewable\" {");
    try expectContains(driver, "test \"phase11 hvc console keeps stale hangup short-circuit ownership reviewable\" {");
    try expectContains(driver, "test \"phase11 hvc console keeps remove handoff summary reviewable\" {");
    try expectContains(driver, "test \"phase11 hvc console keeps targetless notifier no-unregister edge reviewable\" {");
    try expectContains(driver, "test \"phase11 hvc console keeps hvc_kick wakeup cue reviewable\" {");
    try expectContains(driver, "test \"phase11 hvc console keeps notifier irq helper surface reviewable\" {");
    try expectContains(driver, "test \"phase11 hvc console keeps modem-control helper surface reviewable\" {");
}
