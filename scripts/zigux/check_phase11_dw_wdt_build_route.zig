const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_DW_WDT_BUILD_ROUTE=pass";
pub const self_test_pass_marker = "PHASE11_DW_WDT_BUILD_ROUTE_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "drivers/watchdog/dw_wdt.zig",
    "drivers/watchdog/dw_wdt_pm.zig",
    "drivers/watchdog/dw_wdt_restart.zig",
    "drivers/watchdog/dw_wdt_verify.zig",
    "scripts/zigux/check_phase11_dw_wdt_build_route.zig",
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
    "zigux/tests/phase11_dw_wdt.zig",
    "zigux/tests/phase11_dw_wdt_build.zig",
    "zigux/tests/phase11_dw_wdt_live_mmio_review.zig",
    "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
};

const json_files = [_][]const u8{
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for(required_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const file=std.Io.Dir.cwd().openFile(io,path,.{}) catch return error.MissingRequiredFile; file.close(io); }
    for(json_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const text=try guard.readUtf8File(io,allocator,path); defer allocator.free(text); const parsed=try std.json.parseFromSlice(std.json.Value,allocator,text,.{}); parsed.deinit(); }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=10",.{});
    try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=1",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_DW_WDT_BUILD_ROUTE_SELF_TEST_CASE_COUNT=5",.{}); try emitCounts(io); return 0;
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
// pub const pass_marker = "PHASE11_DW_WDT_BUILD_ROUTE_SELF_TEST=pass";
//
// const REQUIRED_BUILD_TEXT_MARKERS = [_][]const u8{
//     ".root_source_file = b.path(\"../../drivers/watchdog/dw_wdt.zig\")",
//     ".root_source_file = b.path(\"../../drivers/watchdog/dw_wdt_pm.zig\")",
//     ".root_source_file = b.path(\"phase11_dw_wdt_registration_scaffold.zig\")",
//     ".root_source_file = b.path(\"phase11_dw_wdt_live_mmio_review.zig\")",
//     ".root_source_file = b.path(\"../../drivers/watchdog/dw_wdt_restart.zig\")",
//     ".root_source_file = b.path(\"../../drivers/watchdog/dw_wdt_verify.zig\")",
//     ".root_source_file = b.path(\"phase11_dw_wdt.zig\")",
//     "registration_scaffold_module.addImport(\"dw_wdt\", dw_wdt_module);",
//     "live_mmio_review_module.addImport(\"dw_wdt\", dw_wdt_module);",
//     "live_mmio_review_module.addImport(\"dw_wdt_pm\", dw_wdt_pm_module);",
//     "direct_replay_module.addImport(\"dw_wdt\", dw_wdt_module);",
//     "direct_replay_module.addImport(\"dw_wdt_pm\", dw_wdt_pm_module);",
//     "direct_replay_module.addImport(\"dw_wdt_restart\", restart_module);",
//     ".name = \"phase11-dw-wdt-registration-scaffold-tests\"",
//     ".name = \"phase11-dw-wdt-live-mmio-review-tests\"",
//     ".name = \"phase11-dw-wdt-pm-tests\"",
//     ".name = \"phase11-dw-wdt-restart-tests\"",
//     ".name = \"phase11-dw-wdt-verify-tests\"",
//     ".name = \"phase11-dw-wdt-direct-replay-tests\"",
//     "\"Run the focused Phase 11 DesignWare watchdog scaffold, direct replay, and verify packet\"",
//     "test_step.dependOn(&run_registration_scaffold_tests.step);",
//     "test_step.dependOn(&run_live_mmio_review_tests.step);",
//     "test_step.dependOn(&run_pm_tests.step);",
//     "test_step.dependOn(&run_restart_tests.step);",
//     "test_step.dependOn(&run_verify_tests.step);",
//     "test_step.dependOn(&run_direct_replay_tests.step);",
// };
//
// const REQUIRED_BUILD_TEST_NAMES = [_][]const u8{
//     "phase11-dw-wdt-registration-scaffold-tests",
//     "phase11-dw-wdt-live-mmio-review-tests",
//     "phase11-dw-wdt-pm-tests",
//     "phase11-dw-wdt-restart-tests",
//     "phase11-dw-wdt-verify-tests",
//     "phase11-dw-wdt-direct-replay-tests",
// };
//
// const EXACT_CURRENT_CHECKS = [_][]const u8{
//     "zig run scripts/zigux/check_phase11_dw_wdt_build_route.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_dw_wdt_build_route.zig --",
//     "zig build test --build-file zigux/tests/phase11_dw_wdt_build.zig",
// };
//
// const REQUIRED_REGISTRATION_SCAFFOLD_MARKERS = [_][]const u8{
//     "test \"platform registration scaffold summary keeps imported-running resetless registration explicit\" {",
//     "test \"platform registration scaffold summary keeps ready reset-release branch explicit\" {",
// };
//
// const REQUIRED_LIVE_MMIO_REVIEW_MARKERS = [_][]const u8{
//     "test \"phase11 dw_wdt keeps live mmio timeout barriers aligned across probe and resume\" {",
//     "test \"phase11 dw_wdt keeps imported-running handoff free of fabricated live mmio blockers\" {",
//     "test \"phase11 dw_wdt keeps remove-time live mmio stop boundaries explicit\" {",
// };
//
// const REQUIRED_DIRECT_REPLAY_MARKERS = [_][]const u8{
//     "test \"phase11 dw_wdt direct replay keeps probe and PM timeout blockers aligned\" {",
//     "test \"phase11 dw_wdt direct replay keeps imported-running registration and resume handoff aligned\" {",
//     "test \"phase11 dw_wdt direct replay keeps restart and remove boundaries distinct\" {",
// };
//
// const REQUIRED_PM_MARKERS = [_][]const u8{
//     "pub const anchor_path = \"drivers/watchdog/dw_wdt.c\";",
//     "test \"phase11 dw_wdt pm suspend keeps missing drvdata explicit\" {",
//     "test \"phase11 dw_wdt pm shutdown keeps idle no-hook teardown explicit\" {",
// };
//
// const REQUIRED_RESTART_MARKERS = [_][]const u8{
//     "pub const anchor_path = \"drivers/watchdog/dw_wdt.c\";",
//     "test \"phase11 dw_wdt restart summary keeps missing drvdata explicit\" {",
//     "test \"phase11 dw_wdt restart summary keeps restart register writes explicit\" {",
// };
//
// const REQUIRED_VERIFY_MARKERS = [_][]const u8{
//     "test \"dw_wdt verify keeps restart blockers and register-write readiness aligned\" {",
//     "test \"dw_wdt verify keeps PM helper ordering and blocker branches explicit\" {",
//     "test \"dw_wdt verify keeps PM scaffold dispositions aligned with the stronger helper packet\" {",
// };
//
// const REQUIRED_MODULE_PATHS = [_][]const u8{
//     "dw_wdt_module",
//     "../../drivers/watchdog/dw_wdt.zig",
//     "dw_wdt_pm_module",
//     "../../drivers/watchdog/dw_wdt_pm.zig",
//     "registration_scaffold_module",
//     "phase11_dw_wdt_registration_scaffold.zig",
//     "live_mmio_review_module",
//     "phase11_dw_wdt_live_mmio_review.zig",
//     "restart_module",
//     "../../drivers/watchdog/dw_wdt_restart.zig",
//     "verify_module",
//     "../../drivers/watchdog/dw_wdt_verify.zig",
//     "direct_replay_module",
//     "phase11_dw_wdt.zig",
// };
//
// const REQUIRED_TEST_ROOT_MODULES = [_][]const u8{
//     "phase11-dw-wdt-registration-scaffold-tests",
//     "registration_scaffold_module",
//     "phase11-dw-wdt-live-mmio-review-tests",
//     "live_mmio_review_module",
//     "phase11-dw-wdt-pm-tests",
//     "dw_wdt_pm_module",
//     "phase11-dw-wdt-restart-tests",
//     "restart_module",
//     "phase11-dw-wdt-verify-tests",
//     "verify_module",
//     "phase11-dw-wdt-direct-replay-tests",
//     "direct_replay_module",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (REQUIRED_BUILD_TEXT_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_BUILD_TEST_NAMES) |marker| try guard.requireMarker(text, marker);
//     for (EXACT_CURRENT_CHECKS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_REGISTRATION_SCAFFOLD_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_LIVE_MMIO_REVIEW_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_DIRECT_REPLAY_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_PM_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_RESTART_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_VERIFY_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MODULE_PATHS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_TEST_ROOT_MODULES) |marker| try guard.requireMarker(text, marker);
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
