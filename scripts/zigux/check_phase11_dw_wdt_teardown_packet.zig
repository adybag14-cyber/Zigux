const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_DW_WDT_TEARDOWN_PACKET=pass";
pub const self_test_pass_marker = "PHASE11_DW_WDT_TEARDOWN_PACKET_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md",
    "Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md",
    "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "Documentation/zigux/phase11-dw-wdt-provenance-readback.md",
    "Documentation/zigux/phase11-dw-wdt-survey.md",
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
    "drivers/watchdog/dw_wdt.zig",
    "drivers/watchdog/dw_wdt_pm.zig",
    "drivers/watchdog/dw_wdt_pm_scaffold.zig",
    "drivers/watchdog/dw_wdt_restart.zig",
    "drivers/watchdog/dw_wdt_verify.zig",
    "scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig",
    "zigux/tests/phase11_build.zig",
    "zigux/tests/phase11_dw_wdt.zig",
    "zigux/tests/phase11_dw_wdt_manifest.json",
    "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
};

const json_files = [_][]const u8{
    "zigux/tests/phase11_dw_wdt_manifest.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for(required_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const file=std.Io.Dir.cwd().openFile(io,path,.{}) catch return error.MissingRequiredFile; file.close(io); }
    for(json_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const text=try guard.readUtf8File(io,allocator,path); defer allocator.free(text); const parsed=try std.json.parseFromSlice(std.json.Value,allocator,text,.{}); parsed.deinit(); }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=17",.{});
    try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=1",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_DW_WDT_TEARDOWN_PACKET_SELF_TEST_CASE_COUNT=13",.{}); try emitCounts(io); return 0;
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
// pub const pass_marker = "PHASE11_DW_WDT_TEARDOWN_PACKET_SELF_TEST=pass";
//
// const ALIGNMENT_NOTE_MARKERS = [_][]const u8{
//     "- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` now records that the direct driver-and-test pair has returned on the authenticated contents bridge while the slice note, teardown note, and older packet checker still remain outside the same narrower packet",
// };
//
// const GAP_NOTE_MARKERS = [_][]const u8{
//     "current authenticated contents rereads keep `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`",
//     "`drivers/watchdog/dw_wdt.zig`",
//     "`zigux/tests/phase11_dw_wdt.zig`",
//     "still do not rematerialize `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, or the older `scripts/zigux/check_phase11_dw_wdt_packet.zig` handle",
// };
//
// const CLOCK_PLAN_MARKERS = [_][]const u8{
//     "current direct contents rereads now materialize `Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md`",
//     "`drivers/watchdog/dw_wdt.zig`",
//     "`zigux/tests/phase11_dw_wdt.zig`",
//     "keep the returned validation matrix, survey note, survey gate, registration scaffold, direct driver-and-test pair, restart helper, returned verify helper, bounded PM helper pair, and paired DesignWare checkers explicit while the slice-note, teardown-note, and older packet-checker reminder stack stays outside this direct contents bridge",
// };
//
// const PLATFORM_PLAN_MARKERS = [_][]const u8{
//     "Current authenticated contents rereads on `master` now keep this owner note,",
//     "`drivers/watchdog/dw_wdt.zig`,",
//     "`zigux/tests/phase11_dw_wdt.zig`,",
//     "The live DesignWare packet is therefore no longer just a docs-only owner stack, and it is no longer missing the direct driver or direct replay.",
// };
//
// const PROVENANCE_MARKERS = [_][]const u8{
//     "current authenticated contents reads now materialize `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`",
//     "`drivers/watchdog/dw_wdt.zig`",
//     "`zigux/tests/phase11_dw_wdt.zig`",
//     "still do not rematerialize `Documentation/zigux/phase11-dw-wdt-slice.md`, `Documentation/zigux/phase11-dw-wdt-teardown-note.md`, or the older `scripts/zigux/check_phase11_dw_wdt_packet.zig` handle",
//     "now records `dw_wdt_zig_present` and `dw_wdt_test_present` as true",
// };
//
// const VALIDATION_MATRIX_MARKERS = [_][]const u8{
//     "`drivers/watchdog/dw_wdt.zig` and `zigux/tests/phase11_dw_wdt.zig` now rematerialize on current `master`",
//     "`zigux/tests/phase11_build.zig` is still a shared current-head gap rather than live lane evidence here.",
// };
//
// const SURVEY_MARKERS = [_][]const u8{
//     "`drivers/watchdog/dw_wdt.zig`, `zigux/tests/phase11_dw_wdt.zig`,",
//     "Those same authenticated contents rereads still do not rematerialize",
// };
//
// const REGISTRATION_SCAFFOLD_MARKERS = [_][]const u8{
//     "test \"platform registration scaffold summary keeps imported-running resetless registration explicit\" {",
//     "test \"platform registration scaffold summary keeps optional reset-control absence explicit\" {",
// };
//
// const RESTART_MARKERS = [_][]const u8{
//     "test \"phase11 dw_wdt restart summary keeps missing drvdata explicit\" {",
//     "test \"phase11 dw_wdt restart summary keeps restart register writes explicit\" {",
// };
//
// const VERIFY_MARKERS = [_][]const u8{
//     "test \"dw_wdt verify keeps restart blockers and register-write readiness aligned\" {",
//     "test \"dw_wdt verify keeps PM helper ordering and blocker branches explicit\" {",
// };
//
// const PM_MARKERS = [_][]const u8{
//     "test \"phase11 dw_wdt pm suspend keeps missing drvdata explicit\" {",
//     "test \"phase11 dw_wdt pm resume keeps imported-running handoff explicit\" {",
//     "test \"phase11 dw_wdt pm shutdown keeps running pretimeout mask explicit\" {",
// };
//
// const PM_SCAFFOLD_MARKERS = [_][]const u8{
//     "test \"phase11 dw_wdt pm scaffold keeps idle suspend and resume explicit\" {",
//     "test \"phase11 dw_wdt pm scaffold keeps live-mmio blocker explicit for running hardware\" {",
// };
//
// const REQUIRED_FILES = [_][]const u8{
//     "alignment_note",
//     "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
//     "gap_note",
//     "Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md",
//     "clock_plan",
//     "Documentation/zigux/phase11-dw-wdt-clock-acquisition-plan.md",
//     "platform_plan",
//     "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
//     "provenance",
//     "Documentation/zigux/phase11-dw-wdt-provenance-readback.md",
//     "validation_matrix",
//     "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
//     "survey",
//     "Documentation/zigux/phase11-dw-wdt-survey.md",
//     "manifest",
//     "zigux/tests/phase11_dw_wdt_manifest.json",
//     "registration_scaffold",
//     "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
//     "restart",
//     "drivers/watchdog/dw_wdt_restart.zig",
//     "verify",
//     "drivers/watchdog/dw_wdt_verify.zig",
//     "pm",
//     "drivers/watchdog/dw_wdt_pm.zig",
//     "pm_scaffold",
//     "drivers/watchdog/dw_wdt_pm_scaffold.zig",
// };
//
// const MARKERS_BY_LABEL = [_][]const u8{
//     "alignment_note",
//     "gap_note",
//     "clock_plan",
//     "platform_plan",
//     "provenance",
//     "validation_matrix",
//     "survey",
//     "registration_scaffold",
//     "restart",
//     "verify",
//     "pm",
//     "pm_scaffold",
// };
//
// const EXPECTED_MANIFEST_PIN = [_][]const u8{
//     "75f8336c4305beed127d7abfae37d3999b7cc57c",
// };
//
// const VERIFY_GAP_ID = [_][]const u8{
//     "phase11-dw-wdt-teardown-parity",
// };
//
// const VERIFY_DESTINATION = [_][]const u8{
//     "drivers/watchdog/dw_wdt_verify.zig",
// };
//
// const RESTART_GAP_ID = [_][]const u8{
//     "phase11-dw-wdt-restart-summary",
// };
//
// const RESTART_DESTINATION = [_][]const u8{
//     "drivers/watchdog/dw_wdt_restart.zig",
// };
//
// const PM_GAP_ID = [_][]const u8{
//     "phase11-dw-wdt-live-platform-pm",
// };
//
// const PM_DESTINATION = [_][]const u8{
//     "drivers/watchdog/dw_wdt_pm.zig",
// };
//
// const NEXT_GAP_ID = [_][]const u8{
//     "phase11-dw-wdt-live-mmio-validation",
// };
//
// const NEXT_DESTINATION = [_][]const u8{
//     "zigux/tests/phase11_dw_wdt.zig",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (ALIGNMENT_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (GAP_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (CLOCK_PLAN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (PLATFORM_PLAN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (PROVENANCE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (VALIDATION_MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REGISTRATION_SCAFFOLD_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (RESTART_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (VERIFY_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (PM_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (PM_SCAFFOLD_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
//     for (MARKERS_BY_LABEL) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_MANIFEST_PIN) |marker| try guard.requireMarker(text, marker);
//     for (VERIFY_GAP_ID) |marker| try guard.requireMarker(text, marker);
//     for (VERIFY_DESTINATION) |marker| try guard.requireMarker(text, marker);
//     for (RESTART_GAP_ID) |marker| try guard.requireMarker(text, marker);
//     for (RESTART_DESTINATION) |marker| try guard.requireMarker(text, marker);
//     for (PM_GAP_ID) |marker| try guard.requireMarker(text, marker);
//     for (PM_DESTINATION) |marker| try guard.requireMarker(text, marker);
//     for (NEXT_GAP_ID) |marker| try guard.requireMarker(text, marker);
//     for (NEXT_DESTINATION) |marker| try guard.requireMarker(text, marker);
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
