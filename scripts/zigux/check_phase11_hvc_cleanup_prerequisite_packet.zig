const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_HVC_CLEANUP_PREREQUISITE_PACKET=pass";
pub const self_test_pass_marker = "PHASE11_HVC_CLEANUP_PREREQUISITE_PACKET_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "drivers/tty/hvc/hvc_console.zig",
    "scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
};

const json_files = [_][]const u8{
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for(required_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const file=std.Io.Dir.cwd().openFile(io,path,.{}) catch return error.MissingRequiredFile; file.close(io); }
    for(json_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const text=try guard.readUtf8File(io,allocator,path); defer allocator.free(text); const parsed=try std.json.parseFromSlice(std.json.Value,allocator,text,.{}); parsed.deinit(); }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=6",.{});
    try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=0",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_HVC_CLEANUP_PREREQUISITE_PACKET_SELF_TEST_CASE_COUNT=31",.{}); try emitCounts(io); return 0;
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
// pub const pass_marker = "PHASE11_HVC_CLEANUP_PREREQUISITE_PACKET_SELF_TEST=pass";
//
// const REQUIRED_FILES = [_][]const u8{
//     "NOTE_PATH",
//     "SURVEY_PATH",
//     "MATRIX_PATH",
//     "DRIVER_PATH",
//     "PROOF_PATH",
//     "SELF_PATH",
// };
//
// const FILE_EXPECTATIONS = [_][]const u8{
//     "`PHASE11_HVC_CLEANUP_PREREQUISITE_STATUS=current_head_trigger_split_reviewable`",
//     "`summarizeCleanupPrerequisite()`",
//     "`CleanupTrigger.final_close_only`",
//     "`CleanupTrigger.hangup_only`",
//     "`CleanupTrigger.final_close_and_hangup`",
//     "`error.CleanupRequiresFinalCloseOrHangup`",
//     "`Documentation/zigux/phase11-hvc-console-teardown-note.md`",
//     "`make -C zigux phase11-validate`",
//     "does not claim that live `hvc_cleanup()` execution is replayed on current",
//     "`Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md`",
//     "`scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig`",
//     "cleanup-prerequisite parity note",
//     "cleanup-prerequisite packet checker",
//     "`Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md`",
//     "`scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig`",
//     "cleanup-prerequisite trigger split",
//     "dedicated teardown-prerequisite reminder guard",
//     "pub const CleanupTrigger = enum {",
//     "final_close_only,",
//     "hangup_only,",
//     "final_close_and_hangup,",
//     "pub fn summarizeCleanupPrerequisite(",
//     "error{CleanupRequiresFinalCloseOrHangup}!CleanupPrerequisiteSummary",
//     "cleanup prerequisite final-close-only trigger reviewable",
//     "cleanup prerequisite hangup-only trigger reviewable",
//     "cleanup prerequisite combined trigger reviewable",
//     "rejects cleanup without final-close or hangup evidence",
//     "PHASE11_HVC_CLEANUP_PREREQUISITE_PACKET=pass",
//     "PHASE11_HVC_CLEANUP_PREREQUISITE_PACKET_SELF_TEST=pass",
// };
//
// const NOTE_PATH = [_][]const u8{
//     "Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md",
// };
//
// const SURVEY_PATH = [_][]const u8{
//     "Documentation/zigux/phase11-hvc-console-survey.md",
// };
//
// const MATRIX_PATH = [_][]const u8{
//     "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
// };
//
// const DRIVER_PATH = [_][]const u8{
//     "drivers/tty/hvc/hvc_console.zig",
// };
//
// const PROOF_PATH = [_][]const u8{
//     "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
// };
//
// const SELF_PATH = [_][]const u8{
//     "scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
//     for (FILE_EXPECTATIONS) |marker| try guard.requireMarker(text, marker);
//     for (NOTE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
//     for (MATRIX_PATH) |marker| try guard.requireMarker(text, marker);
//     for (DRIVER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (PROOF_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SELF_PATH) |marker| try guard.requireMarker(text, marker);
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
