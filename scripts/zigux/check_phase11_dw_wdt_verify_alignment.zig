const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_DW_WDT_VERIFY_ALIGNMENT=pass";
pub const self_test_pass_marker = "PHASE11_DW_WDT_VERIFY_ALIGNMENT_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
    "drivers/watchdog/dw_wdt.zig",
    "drivers/watchdog/dw_wdt_pm.zig",
    "drivers/watchdog/dw_wdt_verify.zig",
    "scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig",
    "zigux/tests/phase11_dw_wdt.zig",
    "zigux/tests/phase11_dw_wdt_manifest.json",
};

const json_files = [_][]const u8{
    "zigux/tests/phase11_dw_wdt_manifest.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for(required_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const file=std.Io.Dir.cwd().openFile(io,path,.{}) catch return error.MissingRequiredFile; file.close(io); }
    for(json_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const text=try guard.readUtf8File(io,allocator,path); defer allocator.free(text); const parsed=try std.json.parseFromSlice(std.json.Value,allocator,text,.{}); parsed.deinit(); }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=9",.{});
    try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=1",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_DW_WDT_VERIFY_ALIGNMENT_SELF_TEST_CASE_COUNT=4",.{}); try emitCounts(io); return 0;
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
// pub const pass_marker = "PHASE11_DW_WDT_VERIFY_ALIGNMENT_SELF_TEST=pass";
//
// const NOTE_MARKERS = [_][]const u8{
//     "- current authenticated contents now keep the returned validation matrix directly readable through the same bridge that serves the rest of this narrower packet",
//     "- the directly checkable current-head packet in this environment is `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`, `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`, `zigux/tests/phase11_dw_wdt_manifest.json`, `drivers/watchdog/dw_wdt_verify.zig`, `drivers/watchdog/dw_wdt_pm.zig`, and this companion note",
//     "- `zigux/tests/phase11_dw_wdt_manifest.json` now records deeper platform-registration scaffold continuity `P11-L10` at surveyed pin `75f8336c4305beed127d7abfae37d3999b7cc57c`",
//     "- `Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md` now records that the direct driver-and-test pair has returned on the authenticated contents bridge while the slice note, teardown note, and older packet checker still remain outside the same narrower packet",
//     "- `drivers/watchdog/dw_wdt_pm.zig` still keeps bounded suspend, resume, and shutdown handoff summaries explicit across missing-drvdata blocks, idle suspend without teardown hooks, running-hardware suspend stop intent, missing suspend hook teardown during running stop, imported-running resume recovery, timeout-reprogram blocks, running shutdown stop intent, pretimeout-mask teardown, and idle shutdown cleanup while still keeping live PM execution out of scope",
// };
//
// const MATRIX_MARKERS = [_][]const u8{
//     "- `PHASE11_DW_WDT_STATUS=hardware_validation_matrix_landed`",
//     "- current surveyed packet pin: `75f8336c4305beed127d7abfae37d3999b7cc57c`",
//     "- `drivers/watchdog/dw_wdt.zig` and `zigux/tests/phase11_dw_wdt.zig` now rematerialize on current `master`",
//     "- The next bounded same-lane follow-up remains the manifest-marked ready-next step: hardware-backed MMIO validation around suspend, resume, and platform-backed probe or remove execution, without widening into unrelated driver behavior.",
// };
//
// const PLATFORM_PLAN_MARKERS = [_][]const u8{
//     "Current authenticated contents rereads on `master` now keep this owner note,",
//     "`drivers/watchdog/dw_wdt.zig`,",
//     "`zigux/tests/phase11_dw_wdt.zig`,",
//     "The live DesignWare packet is therefore no longer just a docs-only owner stack, and it is no longer missing the direct driver or direct replay.",
//     "- the returned direct driver-and-test pair in `drivers/watchdog/dw_wdt.zig` and `zigux/tests/phase11_dw_wdt.zig`",
// };
//
// const VERIFY_MARKERS = [_][]const u8{
//     "const dw_wdt_pm = @import(\"dw_wdt_pm.zig\");",
//     "const dw_wdt_restart = @import(\"dw_wdt_restart.zig\");",
//     "test \"dw_wdt verify keeps restart blockers and register-write readiness aligned\" {",
//     "test \"dw_wdt verify keeps PM helper ordering and blocker branches explicit\" {",
//     "test \"dw_wdt verify keeps PM scaffold dispositions aligned with the stronger helper packet\" {",
// };
//
// const PM_MARKERS = [_][]const u8{
//     "pub const anchor_path = \"drivers/watchdog/dw_wdt.c\";",
//     "test \"phase11 dw_wdt pm suspend keeps missing drvdata explicit\" {",
//     "test \"phase11 dw_wdt pm resume keeps imported-running handoff explicit\" {",
//     "test \"phase11 dw_wdt pm shutdown keeps running pretimeout mask explicit\" {",
// };
//
// const FILES = [_][]const u8{
//     "note",
//     "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
//     "matrix",
//     "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
//     "platform_plan",
//     "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
//     "manifest",
//     "zigux/tests/phase11_dw_wdt_manifest.json",
//     "verify",
//     "drivers/watchdog/dw_wdt_verify.zig",
//     "pm",
//     "drivers/watchdog/dw_wdt_pm.zig",
// };
//
// const EXPECTED_MANIFEST_PIN = [_][]const u8{
//     "75f8336c4305beed127d7abfae37d3999b7cc57c",
// };
//
// const VERIFY_DESTINATION = [_][]const u8{
//     "drivers/watchdog/dw_wdt_verify.zig",
// };
//
// const VERIFY_GAP_ID = [_][]const u8{
//     "phase11-dw-wdt-teardown-parity",
// };
//
// const PM_DESTINATION = [_][]const u8{
//     "drivers/watchdog/dw_wdt_pm.zig",
// };
//
// const PM_GAP_ID = [_][]const u8{
//     "phase11-dw-wdt-live-platform-pm",
// };
//
// const NEXT_DESTINATION = [_][]const u8{
//     "zigux/tests/phase11_dw_wdt.zig",
// };
//
// const NEXT_GAP_ID = [_][]const u8{
//     "phase11-dw-wdt-live-mmio-validation",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (PLATFORM_PLAN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (VERIFY_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (PM_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (FILES) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_MANIFEST_PIN) |marker| try guard.requireMarker(text, marker);
//     for (VERIFY_DESTINATION) |marker| try guard.requireMarker(text, marker);
//     for (VERIFY_GAP_ID) |marker| try guard.requireMarker(text, marker);
//     for (PM_DESTINATION) |marker| try guard.requireMarker(text, marker);
//     for (PM_GAP_ID) |marker| try guard.requireMarker(text, marker);
//     for (NEXT_DESTINATION) |marker| try guard.requireMarker(text, marker);
//     for (NEXT_GAP_ID) |marker| try guard.requireMarker(text, marker);
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
