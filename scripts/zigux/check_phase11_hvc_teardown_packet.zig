const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_HVC_TEARDOWN_PACKET_SELF_TEST=pass";

const SURVEY_MARKERS = [_][]const u8{
    "`PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`",
    "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`scripts/zigux/check_phase11_hvc_cleanup_current_head.zig`",
    "`scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "repo-reality gaps or archival vocabulary",
    "`make -C zigux phase11-validate`",
};

const COMPANION_MARKERS = [_][]const u8{
    "`PHASE11_STATUS=current_head_companion_landed`",
    "build-inventory checker",
    "cleanup-current-head checker",
    "targetless-unregister witness checker",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "repo-reality gaps or archival vocabulary",
    "standalone targetless-unregister witness",
    "dedicated modem-control proof pair",
    "proof-backed continuity packet remains reviewable",
};

const VERIFY_MARKERS = [_][]const u8{
    "`error.CleanupRequiresFinalCloseOrHangup`",
    "`CleanupTrigger.hangup_only` and `CleanupTrigger.final_close_and_hangup`",
    "`error.NotifierDispatchRequiresTtyRegistration`",
    "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`",
    "`NotifierUnregisterTimingState.targeted_unregister_request`",
    "`targetless_dispatch_without_notifier`",
};

const MATRIX_MARKERS = [_][]const u8{
    "`PHASE11_HVC_CONSOLE_STATUS=current_head_companion_packet_truthful`",
    "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`scripts/zigux/check_phase11_hvc_cleanup_current_head.zig`",
    "`scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
    "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
    "repo-reality gaps instead of returned fallback evidence",
    "`hvc_hangup()` disconnect",
    "`hvc_remove()` handoff",
    "`hvc_cleanup()` tty-port",
    "modem-control helper summaries reviewable on current `master`",
    "targetless-unregister witness explicit as standalone direct-readback coverage",
};

const DRIVER_MARKERS = [_][]const u8{
    "pub fn summarizeHangupDisconnect(request: HangupDisconnectRequest) HangupDisconnectSummary {",
    "pub fn summarizeRemoveHandoff(request: RemoveHandoffRequest) RemoveHandoffSummary {",
    "pub fn summarizeCleanupHandoff(request: CleanupHandoffRequest) CleanupHandoffSummary {",
    "pub fn summarizeCleanupPrerequisite(",
    "error{CleanupRequiresFinalCloseOrHangup}!CleanupPrerequisiteSummary",
    "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {",
    "pub fn summarizeKickWakeupCue(request: KickWakeupCueRequest) KickWakeupCueSummary {",
    "pub fn summarizeNotifierIrqHelper(request: NotifierIrqHelperRequest) NotifierIrqHelperSummary {",
    "pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {",
    "test \"phase11 hvc console keeps active hangup and cleanup ownership handoffs reviewable\" {",
    "test \"phase11 hvc console keeps stale hangup short-circuit ownership reviewable\" {",
    "test \"phase11 hvc console keeps remove handoff summary reviewable\" {",
    "test \"phase11 hvc console keeps targetless notifier no-unregister edge reviewable\" {",
};

const CLEANUP_CHECKER_MARKERS = [_][]const u8{
    "PHASE11_HVC_CLEANUP_CURRENT_HEAD=pass",
    "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
    "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
    "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
    "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
    "phase11_hvc_targetless_unregister_gap_build.zig",
};

const TARGETLESS_CHECKER_MARKERS = [_][]const u8{
    "PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS=pass",
    "standalone targetless-unregister witness",
    "phase11-hvc-targetless-unregister-gap",
};

const FORBIDDEN_MAKEFILE_MARKERS = [_][]const u8{
    "phase11-hvc-survey:",
};

const REQUIRED_PACKET_FILES = [_][]const u8{
    "SURVEY_PATH",
    "COMPANION_PATH",
    "VERIFY_PATH",
    "MATRIX_PATH",
    "DRIVER_PATH",
    "CLEANUP_CHECKER_PATH",
    "TARGETLESS_CHECKER_PATH",
    "INVENTORY_PATH",
    "MAKEFILE_PATH",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (COMPANION_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VERIFY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (DRIVER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (CLEANUP_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TARGETLESS_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_PACKET_FILES) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
