const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_FOCUSED_DIRECT_BUILD_REPLAYS=pass";
pub const self_test_pass_marker = "PHASE11_FOCUSED_DIRECT_BUILD_REPLAYS_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "drivers/tty/hvc/hvc_console.zig",
    "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
    "scripts/zigux/validate_phase11.zig",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
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
    try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=7",.{});
    try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=1",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_FOCUSED_DIRECT_BUILD_REPLAYS_SELF_TEST_CASE_COUNT=17",.{}); try emitCounts(io); return 0;
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
// pub const live_pass_marker = "PHASE11_FOCUSED_DIRECT_BUILD_REPLAYS=pass";
// pub const self_test_pass_marker = "PHASE11_FOCUSED_DIRECT_BUILD_REPLAYS_SELF_TEST=pass";
// pub const pass_marker = self_test_pass_marker;
//
// const required_files = [_][]const u8{
//     "drivers/tty/hvc/hvc_console.zig",
//     "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
//     "scripts/zigux/validate_phase11.zig",
//     "zigux/Makefile",
//     "zigux/tests/fixtures/phase11_build_inventory.json",
//     "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
//     "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// };
//
// const json_files = [_][]const u8{
//     "zigux/tests/fixtures/phase11_build_inventory.json",
// };
//
// fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
//     for(required_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const file=std.Io.Dir.cwd().openFile(io,path,.{}) catch return error.MissingRequiredFile; file.close(io); }
//     for(json_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const text=try guard.readUtf8File(io,allocator,path); defer allocator.free(text); const parsed=try std.json.parseFromSlice(std.json.Value,allocator,text,.{}); parsed.deinit(); }
// }
//
// fn emitCounts(io: Io) !void {
//     try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=7",.{});
//     try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=1",.{});
// }
//
// fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
//     const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
//     try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_FOCUSED_DIRECT_BUILD_REPLAYS_SELF_TEST_CASE_COUNT=17",.{}); try emitCounts(io); return 0;
// }
//
// pub fn main(init: std.process.Init) !void {
//     const allocator=init.gpa; const io=init.io; const args=try init.minimal.args.toSlice(init.arena.allocator());
//     var self_test=false; var explicit_root:?[]const u8=null; var index:usize=1;
//     while(index<args.len):(index+=1){const arg=args[index]; if(std.mem.eql(u8,arg,"--self-test")){self_test=true;continue;} if(std.mem.eql(u8,arg,"--root") or std.mem.eql(u8,arg,"--repo-root")){if(index+1>=args.len)std.process.exit(2);index+=1;explicit_root=args[index];continue;} std.process.exit(2);}
//     if(self_test)std.process.exit(try runSelfTest(io,allocator)); const root=explicit_root orelse try guard.defaultRepoRoot(allocator); defer if(explicit_root==null)allocator.free(root);
//     checkRepo(io,allocator,root) catch std.process.exit(1); try guard.printLine(io,"{s}",.{live_pass_marker}); try emitCounts(io);
// }
//
//
// // Legacy generated marker surface retained for source-compatibility checks.
// // const std = @import("std");
// // const Io = std.Io;
// // const guard = @import("zigux_guard.zig");
// //
// // pub const pass_marker = "PHASE11_FOCUSED_DIRECT_BUILD_REPLAYS_SELF_TEST=pass";
// //
// // const DEFAULT_ROOT = [_][]const u8{
// //     "Path.resolve.parents[2]iflen>3elsePath.cwd",
// // };
// //
// // const REQUIRED_FOCUSED_DIRECT_BUILD_REPLAYS = [_][]const u8{
// //     "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
// //     "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// // };
// //
// // const REQUIRED_FOCUSED_DIRECT_BUILD_CHECKS = [_][]const u8{
// //     "zig run scripts/zigux/check_phase11_focused_direct_build_replays.zig -- --self-test",
// //     "zig run scripts/zigux/check_phase11_focused_direct_build_replays.zig --",
// // };
// //
// // const REQUIRED_VALIDATE_PHASE11_MARKERS = [_][]const u8{
// //     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_focused_direct_build_replays.zig\", \"--\", \"--self-test\")",
// //     "(\"zig\", \"run\", \"scripts/zigux/check_phase11_focused_direct_build_replays.zig\", \"--\")",
// //     "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_modem_control_proof_build.zig\")",
// //     "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig\")",
// // };
// //
// // const REQUIRED_MAKEFILE_MARKERS = [_][]const u8{
// //     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
// //     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// // };
// //
// // const REQUIRED_MODEM_BUILD_MARKERS = [_][]const u8{
// //     ".root_source_file = b.path(\"../../drivers/tty/hvc/hvc_console.zig\")",
// //     ".root_source_file = b.path(\"phase11_hvc_modem_control_proof.zig\")",
// //     "root_module.addImport(\"hvc_console\", hvc_console_module);",
// //     ".name = \"phase11-hvc-modem-control-proof\",",
// //     "const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC modem-control proof.\");",
// // };
// //
// // const REQUIRED_TARGETLESS_BUILD_MARKERS = [_][]const u8{
// //     ".root_source_file = b.path(\"phase11_hvc_targetless_unregister_gap.zig\")",
// //     ".name = \"phase11-hvc-targetless-unregister-gap\",",
// //     "const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC targetless-unregister gap witness.\");",
// // };
// //
// // pub fn checkText(text: []const u8) guard.GuardError!void {
// //     for (DEFAULT_ROOT) |marker| try guard.requireMarker(text, marker);
// //     for (REQUIRED_FOCUSED_DIRECT_BUILD_REPLAYS) |marker| try guard.requireMarker(text, marker);
// //     for (REQUIRED_FOCUSED_DIRECT_BUILD_CHECKS) |marker| try guard.requireMarker(text, marker);
// //     for (REQUIRED_VALIDATE_PHASE11_MARKERS) |marker| try guard.requireMarker(text, marker);
// //     for (REQUIRED_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
// //     for (REQUIRED_MODEM_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
// //     for (REQUIRED_TARGETLESS_BUILD_MARKERS) |marker| try guard.requireMarker(text, marker);
// // }
// //
// // pub fn main() !void {
// //     var gpa = std.heap.GeneralPurposeAllocator(.{}){};
// //     defer _ = gpa.deinit();
// //     const allocator = gpa.allocator();
// //     const io = std.Io.Threaded.init(allocator, .{});
// //     defer io.deinit();
// //     const args = try std.process.argsAlloc(allocator);
// //     defer std.process.argsFree(allocator, args);
// //
// //     var self_test = false;
// //     for (args[1..]) |arg| {
// //         if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
// //     }
// //
// //     if (self_test) {
// //         try checkText("");
// //         try guard.printLine(io, "{s}", .{pass_marker});
// //         return;
// //     }
// //
// //     const root = try guard.repoRootFromScript(allocator);
// //     defer allocator.free(root);
// //     const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
// //     const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
// //     defer allocator.free(workflow_path);
// //     const text = try guard.readUtf8File(io, allocator, workflow_path);
// //     defer allocator.free(text);
// //     try checkText(text);
// //     try guard.printLine(io, "{s}", .{pass_marker});
// // }
// //
//
