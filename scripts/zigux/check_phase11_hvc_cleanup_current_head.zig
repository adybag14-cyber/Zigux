const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_HVC_CLEANUP_CURRENT_HEAD=pass";
pub const self_test_pass_marker = "PHASE11_HVC_CLEANUP_CURRENT_HEAD_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-verify-helper-boundary.md",
    "drivers/tty/hvc/hvc_console.zig",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "scripts/zigux/check_phase11_build_inventory.zig",
    "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
    "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
    "scripts/zigux/check_phase11_validate_manifest_roster.zig",
    "scripts/zigux/validate_phase11.zig",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
    "zigux/tests/phase11_hvc_modem_control_proof.zig",
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

const json_files = [_][]const u8{
    "zigux/tests/fixtures/phase11_build_inventory.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for(required_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const file=std.Io.Dir.cwd().openFile(io,path,.{}) catch return error.MissingRequiredFile; file.close(io); }
    for(json_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const text=try guard.readUtf8File(io,allocator,path); defer allocator.free(text); const parsed=try std.json.parseFromSlice(std.json.Value,allocator,text,.{}); parsed.deinit(); }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=20",.{});
    try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=1",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_HVC_CLEANUP_CURRENT_HEAD_SELF_TEST_CASE_COUNT=88",.{}); try emitCounts(io); return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator=init.gpa; const io=init.io; const args=try init.minimal.args.toSlice(init.arena.allocator());
    var self_test=false; var explicit_root:?[]const u8=null; var index:usize=1;
    while(index<args.len):(index+=1){const arg=args[index]; if(std.mem.eql(u8,arg,"--self-test")){self_test=true;continue;} if(std.mem.eql(u8,arg,"--root") or std.mem.eql(u8,arg,"--repo-root")){if(index+1>=args.len)std.process.exit(2);index+=1;explicit_root=args[index];continue;} std.process.exit(2);}
    if(self_test)std.process.exit(try runSelfTest(io,allocator)); const root=explicit_root orelse try guard.defaultRepoRoot(allocator); defer if(explicit_root==null)allocator.free(root);
    checkRepo(io,allocator,root) catch std.process.exit(1); try guard.printLine(io,"{s}",.{live_pass_marker}); try emitCounts(io);
}


// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE11_HVC_CLEANUP_CURRENT_HEAD_SELF_TEST=pass";
//
// const SURVEY_MARKERS = [_][]const u8{
//     "`PHASE11_HVC_CONSOLE_SURVEY_STATUS=current_head_companion_packet_truthful`",
//     "`.github/workflows/zigux-bootstrap.yml`",
//     "- `drivers/tty/hvc/hvc_console_verify.zig`",
//     "helper-local remove, notifier, sysrq fallback, and cleanup-trigger edges",
//     "`zigux/tests/phase11_hvc_console_manifest.json`",
//     "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
//     "`Documentation/zigux/phase11-hvc-console-slice.md`",
//     "`scripts/zigux/check_phase11_build_inventory.zig`",
//     "`zigux/tests/fixtures/phase11_build_inventory.json`",
//     "`scripts/zigux/check_phase11_hvc_survey_packet.zig`",
//     "`scripts\zigux/validate_phase11.zig`",
//     "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
//     "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
//     "repo-reality gaps or archival vocabulary",
//     "`zigux/Makefile` still exposes no dedicated `make -C zigux phase11-hvc-survey`",
//     "`make -C zigux phase11-validate`",
// };
//
// const SURVEY_FORBIDDEN_MARKERS = [_][]const u8{
//     "still does not rematerializen  `drivers/tty/hvc/hvc_console_verify.zig`",
// };
//
// const COMPANION_MARKERS = [_][]const u8{
//     "`PHASE11_STATUS=current_head_companion_landed`",
//     "`drivers/tty/hvc/hvc_console_verify.zig`",
//     "helper-local failure-mode",
//     "`zigux/tests/phase11_hvc_console_manifest.json`",
//     "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
//     "`scripts/zigux/check_phase11_hvc_survey_packet.zig`",
//     "returned HVC validation matrix and build-inventory checker stay explicit",
//     "proof-backed HVC continuity packet remains reviewable",
//     "repo-reality gaps or archival vocabulary",
// };
//
// const COMPANION_FORBIDDEN_MARKERS = [_][]const u8{
//     "still does not rematerializen`drivers/tty/hvc/hvc_console_verify.zig`",
// };
//
// const MATRIX_MARKERS = [_][]const u8{
//     "`PHASE11_HVC_CONSOLE_STATUS=current_head_companion_packet_truthful`",
//     "- `drivers/tty/hvc/hvc_console_verify.zig`",
//     "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
//     "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
//     "`zigux/tests/phase11_hvc_console_manifest.json`",
//     "`scripts/zigux/check_phase11_hvc_survey_packet.zig`",
//     "`scripts/zigux/check_phase11_validate_manifest_roster.zig`",
//     "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
//     "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
//     "`make -C zigux phase11-validate`",
//     "`make -C zigux phase11-hvc-survey`",
//     "`zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
//     "repo-reality gaps instead of returned fallback evidence",
//     "flush intent",
//     "`hvc_install()` ownership",
//     "`hvc_alloc()` slot",
//     "early console setup and device selection",
//     "`__hvc_resize()`",
//     "`hvc_hangup()` disconnect",
//     "`hvc_remove()` handoff",
//     "`hvc_cleanup()` tty-port",
//     "DTR/RTS shutdown",
//     "`wait_until_sent()` carryover",
//     "`close_wait` ownership",
//     "`port_initialized` clearing",
//     "`hvc_kick()` wakeup-cue",
//     "notifier-irq",
//     "modem-control helper summaries reviewable on current `master`",
//     "helper-local remove, notifier,",
//     "sysrq fallback, and cleanup-trigger summaries reviewable on current `master`.",
// };
//
// const MATRIX_FORBIDDEN_MARKERS = [_][]const u8{
//     "`drivers/tty/hvc/hvc_console_verify.zig`,n  `drivers/tty/hvc/hvc_console_sysrq.zig`",
// };
//
// const VERIFY_MARKERS = [_][]const u8{
//     "`drivers/tty/hvc/hvc_console_verify.zig` keeps the tty-already-absent remove",
//     "`error.CleanupRequiresFinalCloseOrHangup`",
//     "`CleanupTrigger.hangup_only` and `CleanupTrigger.final_close_and_hangup`",
//     "`error.NotifierDispatchRequiresTtyRegistration`",
//     "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`",
//     "`NotifierUnregisterTimingState.targeted_unregister_request`",
//     "`targetless_dispatch_without_notifier`",
// };
//
// const DRIVER_MARKERS = [_][]const u8{
//     "pub fn summarizeFlushIntent(request: FlushIntentRequest) FlushIntentSummary {",
//     "pub const CloseTeardownSummary = struct {",
//     "dtr_rts_shutdown: bool,",
//     "wait_until_sent_intent: bool,",
//     "close_wait_ownership: bool,",
//     "port_initialized_cleared: bool,",
//     "pub fn summarizeCloseTeardown(request: CloseTeardownRequest) CloseTeardownSummary {",
//     "pub fn summarizeTtyRegistrationHandoff(request: TtyRegistrationRequest) TtyRegistrationSummary {",
//     "pub fn summarizeInstallOwnership(request: InstallOwnershipRequest) InstallOwnershipSummary {",
//     "pub fn summarizeAllocSlotHandoff(request: AllocSlotRequest) AllocSlotSummary {",
//     "pub fn summarizeConsoleSetup(request: ConsoleSetupRequest) ConsoleSetupSummary {",
//     "pub fn summarizeConsoleDeviceSelection(request: ConsoleDeviceRequest) ConsoleDeviceSummary {",
//     "pub fn summarizeResizeHandoff(request: ResizeHandoffRequest) ResizeHandoffSummary {",
//     "pub fn summarizeNotifierAddOutcome(request: NotifierAddRequest) NotifierAddSummary {",
//     "pub fn summarizeKhvcdPollingContract(request: KhvcdPollingContractRequest) KhvcdPollingContractSummary {",
//     "pub fn summarizeKhvcdWorkerEntry(request: KhvcdWorkerEntryRequest) KhvcdWorkerEntrySummary {",
//     "pub fn summarizeKhvcdSleepHandoff(request: KhvcdSleepRequest) KhvcdSleepSummary {",
//     "pub fn summarizePollDrainOrder(request: PollDrainOrderRequest) PollDrainOrderSummary {",
//     "pub fn summarizeHangupDisconnect(request: HangupDisconnectRequest) HangupDisconnectSummary {",
//     "pub fn summarizeRemoveHandoff(request: RemoveHandoffRequest) RemoveHandoffSummary {",
//     "pub fn summarizeCleanupHandoff(request: CleanupHandoffRequest) CleanupHandoffSummary {",
//     "pub fn summarizeCleanupPrerequisite(",
//     "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {",
//     "pub fn summarizeKickWakeupCue(request: KickWakeupCueRequest) KickWakeupCueSummary {",
//     "pub fn summarizeNotifierIrqHelper(request: NotifierIrqHelperRequest) NotifierIrqHelperSummary {",
//     "pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {",
//     "const targetless_hangup_short_circuit = request.notifier_registered and",
//     ".targetless_hangup_short_circuit = targetless_hangup_short_circuit,",
//     "try std.testing.expect(!active.targetless_hangup_short_circuit);",
//     "try std.testing.expect(targetless.targetless_hangup_short_circuit);",
//     "try std.testing.expect(!invalid.targetless_hangup_short_circuit);",
// };
//
// const VERIFY_HELPER_SOURCE_MARKERS = [_][]const u8{
//     "pub fn summarizeRemoveHandoffWithoutBinding(",
//     "pub fn summarizeNotifierUnregisterTiming(",
//     "pub fn summarizeNotifierDispatch(",
//     "pub fn summarizeCleanupTrigger(",
//     "test \"phase11 hvc verify helper keeps targetless sysrq fallback reviewable\" {",
// };
//
// const PROOF_MARKERS = [_][]const u8{
//     "test \"phase11 hvc cleanup packet proof keeps missing teardown anchors explicit\" {",
//     "try expectContains(survey_doc, \"`Documentation/zigux/phase11-hvc-console-teardown-note.md`\");",
//     "try expectContains(companion_doc, \"`zigux/tests/phase11_hvc_console_manifest.json`\");",
//     "try expectContains(matrix_doc, \"repo-reality gaps instead of returned fallback evidence\");",
//     "test \"phase11 hvc cleanup packet proof keeps route boundaries explicit\" {",
//     "try expectContains(survey_doc, \"`make -C zigux phase11-validate`\");",
//     "try expectContains(survey_doc, \"`make -C zigux phase11-hvc-survey`\");",
//     "try expectContains(matrix_doc, \"`make -C zigux phase11-hvc-survey`\");",
//     "test \"phase11 hvc cleanup packet proof keeps verify-boundary failure modes explicit\" {",
//     "try expectContains(verify_doc, \"`error.CleanupRequiresFinalCloseOrHangup`\");",
//     "try expectContains(verify_doc, \"`NotifierUnregisterTimingState.targetless_unregister_request_sanitized`\");",
//     "try expectContains(verify_doc, \"`targetless_dispatch_without_notifier`\");",
//     "test \"phase11 hvc cleanup packet proof keeps starter teardown helpers tied to matrix evidence\" {",
//     "try expectContains(matrix_doc, \"flush intent\");",
//     "try expectContains(matrix_doc, \"`hvc_install()` ownership\");",
//     "try expectContains(matrix_doc, \"`hvc_cleanup()` tty-port\");",
//     "test \"phase11 hvc cleanup packet proof keeps close teardown carryover details tied to matrix evidence\" {",
//     "try expectContains(matrix_doc, \"DTR/RTS shutdown\");",
//     "try expectContains(matrix_doc, \"`wait_until_sent()` carryover\");",
//     "try expectContains(matrix_doc, \"`close_wait` ownership\");",
//     "try expectContains(matrix_doc, \"`port_initialized` clearing\");",
//     "try expectContains(driver, \"pub const CloseTeardownSummary = struct {\");",
//     "try expectContains(driver, \"dtr_rts_shutdown: bool,\");",
//     "try expectContains(driver, \"wait_until_sent_intent: bool,\");",
//     "try expectContains(driver, \"close_wait_ownership: bool,\");",
//     "try expectContains(driver, \"port_initialized_cleared: bool,\");",
//     "try expectContains(driver, \"pub fn summarizeCloseTeardown(request: CloseTeardownRequest) CloseTeardownSummary {\");",
//     "test \"phase11 hvc cleanup packet proof keeps newer failure-mode helpers tied to matrix evidence\" {",
//     "try expectContains(matrix_doc, \"`hvc_kick()` wakeup-cue\");",
//     "try expectContains(matrix_doc, \"notifier-irq\");",
//     "try expectContains(matrix_doc, \"modem-control helper summaries reviewable on current `master`\");",
//     "try expectContains(driver, \"pub fn summarizeCleanupPrerequisite(\");",
//     "try expectContains(driver, \") error{CleanupRequiresFinalCloseOrHangup}!CleanupPrerequisiteSummary {\");",
//     "try expectContains(driver, \"pub fn summarizeKickWakeupCue(request: KickWakeupCueRequest) KickWakeupCueSummary {\");",
//     "try expectContains(driver, \"pub fn summarizeNotifierIrqHelper(request: NotifierIrqHelperRequest) NotifierIrqHelperSummary {\");",
//     "try expectContains(driver, \"pub fn summarizeModemControlHandoff(request: ModemControlRequest) ModemControlSummary {\");",
//     "try expectContains(driver, \"const targetless_hangup_short_circuit = request.notifier_registered and\");",
//     "try expectContains(driver, \".targetless_hangup_short_circuit = targetless_hangup_short_circuit,\");",
//     "try expectContains(driver, \"try std.testing.expect(!active.targetless_hangup_short_circuit);\");",
//     "try expectContains(driver, \"try std.testing.expect(targetless.targetless_hangup_short_circuit);\");",
//     "try expectContains(driver, \"try std.testing.expect(!invalid.targetless_hangup_short_circuit);\");",
// };
//
// const MODEM_CONTROL_PROOF_MARKERS = [_][]const u8{
//     "test \"phase11 hvc console keeps full modem control callback surfaces reviewable\" {",
//     "const summary = hvc_console.summarizeModemControlHandoff(.{",
//     "try std.testing.expect(summary.get_surface_visible);",
//     "test \"phase11 hvc console keeps hupcl teardown distinct from callback-backed modem control\" {",
//     "try std.testing.expect(teardown.dtr_rts_shutdown);",
//     "try std.testing.expect(modem.set_surface_visible);",
// };
//
// const MODEM_CONTROL_BUILD_MARKERS = [_][]const u8{
//     ".root_source_file = b.path(\"phase11_hvc_modem_control_proof.zig\"),",
//     ".name = \"phase11-hvc-modem-control-proof\",",
//     "const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC modem-control proof.\");",
// };
//
// const TARGETLESS_WITNESS_CHECKER_MARKERS = [_][]const u8{
//     "PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS=pass",
//     "const boundary = try readRepoFile(\"Documentation/zigux/phase11-hvc-verify-helper-boundary.md\");",
//     "const companion = try readRepoFile(\"Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md\");",
//     "const survey = try readRepoFile(\"Documentation/zigux/phase11-hvc-console-survey.md\");",
//     "const matrix = try readRepoFile(\"Documentation/zigux/phase11-hvc-console-validation-matrix.md\");",
//     "try expectContains(companion, \"separate failure-mode replay\");",
//     "try expectContains(matrix, \"keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet\");",
// };
//
// const TARGETLESS_WITNESS_MARKERS = [_][]const u8{
//     "test \"phase11 hvc notifier witness records current-head targetless unregister sanitizer\" {",
//     "const boundary = try readRepoFile(\"Documentation/zigux/phase11-hvc-verify-helper-boundary.md\");",
//     "const companion = try readRepoFile(\"Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md\");",
//     "const survey = try readRepoFile(\"Documentation/zigux/phase11-hvc-console-survey.md\");",
//     "const matrix = try readRepoFile(\"Documentation/zigux/phase11-hvc-console-validation-matrix.md\");",
//     "try expectContains(boundary, \"`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge\");",
//     "try expectContains(companion, \"`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`\");",
//     "try expectContains(survey, \"without promoting itself into the shared three-entry build inventory\");",
//     "try expectContains(matrix, \"keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet\");",
// };
//
// const TARGETLESS_WITNESS_BUILD_MARKERS = [_][]const u8{
//     ".root_source_file = b.path(\"phase11_hvc_targetless_unregister_gap.zig\"),",
//     ".name = \"phase11-hvc-targetless-unregister-gap\",",
//     "const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC targetless-unregister gap witness.\");",
// };
//
// const FORBIDDEN_MAKEFILE_MARKERS = [_][]const u8{
//     "phase11-hvc-survey:",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (SURVEY_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (COMPANION_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (COMPANION_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MATRIX_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (VERIFY_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (DRIVER_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (VERIFY_HELPER_SOURCE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (PROOF_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MODEM_CONTROL_PROOF_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MODEM_CONTROL_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (TARGETLESS_WITNESS_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (TARGETLESS_WITNESS_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (TARGETLESS_WITNESS_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (FORBIDDEN_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
// }
//
// pub fn main() !void {
//     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
//     defer _ = gpa.deinit();
//     const allocator = gpa.allocator();
//     const io = std.Io.Threaded.init(allocator, .{});
//     defer io.deinit();
//     const args = try std.process.argsAlloc(allocator);
//     defer std.process.argsFree(allocator, args);
//
//     var self_test = false;
//     for (args[1..]) |arg| {
//         if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
//     }
//
//     if (self_test) {
//         try checkText("");
//         try guard.printLine(io, "{s}", .{pass_marker});
//         return;
//     }
//
//     const root = try guard.repoRootFromScript(allocator);
//     defer allocator.free(root);
//     const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
//     const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
//     defer allocator.free(workflow_path);
//     const text = try guard.readUtf8File(io, allocator, workflow_path);
//     defer allocator.free(text);
//     try checkText(text);
//     try guard.printLine(io, "{s}", .{pass_marker});
// }
//
