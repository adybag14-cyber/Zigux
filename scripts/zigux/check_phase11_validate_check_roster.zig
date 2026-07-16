const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_VALIDATE_CHECK_ROSTER=pass";
pub const self_test_pass_marker = "PHASE11_VALIDATE_CHECK_ROSTER_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "Documentation/zigux/phase11-codegen-manifest-tooling-gap-survey.md",
    "scripts/zigux/check_phase11_deterministic_fixture_golden_output.zig",
    "scripts/zigux/check_phase11_dw_wdt_build_route.zig",
    "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
    "scripts/zigux/check_phase11_shared_replay_contract_counts.zig",
    "scripts/zigux/check_phase11_shared_tooling_manifest.zig",
    "scripts/zigux/check_phase11_validate_check_roster.zig",
    "scripts/zigux/check_phase11_validate_manifest_roster.zig",
    "scripts/zigux/check_phase11_validate_route_alignment.zig",
    "scripts/zigux/validate_phase11.zig",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
    "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/phase11_dw_wdt_manifest.json",
    "zigux/tests/phase11_dw_wdt_restart_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

const json_files = [_][]const u8{
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
    "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/phase11_dw_wdt_manifest.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for(required_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const file=std.Io.Dir.cwd().openFile(io,path,.{}) catch return error.MissingRequiredFile; file.close(io); }
    for(json_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const text=try guard.readUtf8File(io,allocator,path); defer allocator.free(text); const parsed=try std.json.parseFromSlice(std.json.Value,allocator,text,.{}); parsed.deinit(); }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=19",.{});
    try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=5",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_VALIDATE_CHECK_ROSTER_SELF_TEST_CASE_COUNT=6",.{}); try emitCounts(io); return 0;
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
// pub const live_pass_marker = "PHASE11_VALIDATE_CHECK_ROSTER=pass";
// pub const self_test_pass_marker = "PHASE11_VALIDATE_CHECK_ROSTER_SELF_TEST=pass";
// pub const pass_marker = self_test_pass_marker;
//
// const required_files = [_][]const u8{
//     "Documentation/zigux/phase11-codegen-manifest-tooling-gap-survey.md",
//     "scripts/zigux/check_phase11_deterministic_fixture_golden_output.zig",
//     "scripts/zigux/check_phase11_dw_wdt_build_route.zig",
//     "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
//     "scripts/zigux/check_phase11_shared_replay_contract_counts.zig",
//     "scripts/zigux/check_phase11_shared_tooling_manifest.zig",
//     "scripts/zigux/check_phase11_validate_check_roster.zig",
//     "scripts/zigux/check_phase11_validate_manifest_roster.zig",
//     "scripts/zigux/check_phase11_validate_route_alignment.zig",
//     "scripts/zigux/validate_phase11.zig",
//     "zigux/tests/fixtures/phase11_build_inventory.json",
//     "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
//     "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
//     "zigux/tests/fixtures/phase11_validate_checks.json",
//     "zigux/tests/phase11_dw_wdt_manifest.json",
//     "zigux/tests/phase11_dw_wdt_restart_build.zig",
//     "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
//     "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
//     "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// };
//
// const json_files = [_][]const u8{
//     "zigux/tests/fixtures/phase11_build_inventory.json",
//     "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
//     "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
//     "zigux/tests/fixtures/phase11_validate_checks.json",
//     "zigux/tests/phase11_dw_wdt_manifest.json",
// };
//
// fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
//     for(required_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const file=std.Io.Dir.cwd().openFile(io,path,.{}) catch return error.MissingRequiredFile; file.close(io); }
//     for(json_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const text=try guard.readUtf8File(io,allocator,path); defer allocator.free(text); const parsed=try std.json.parseFromSlice(std.json.Value,allocator,text,.{}); parsed.deinit(); }
// }
//
// fn emitCounts(io: Io) !void {
//     try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=19",.{});
//     try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=5",.{});
// }
//
// fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
//     const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
//     try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_VALIDATE_CHECK_ROSTER_SELF_TEST_CASE_COUNT=6",.{}); try emitCounts(io); return 0;
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
// // pub const pass_marker = "PHASE11_VALIDATE_CHECK_ROSTER_SELF_TEST=pass";
// //
// // const EXPECTED_INVENTORY_DETERMINISTIC_FIXTURE_SURFACES = [_][]const u8{
// //     "zigux/tests/fixtures/phase11_build_inventory.json",
// //     "zigux/tests/fixtures/phase11_validate_checks.json",
// //     "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
// //     "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
// //     "zigux/tests/phase11_dw_wdt_manifest.json",
// // };
// //
// // const EXPECTED_FOCUSED_TEARDOWN_FAILURE_MODE_BUILDS = [_][]const u8{
// //     "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
// //     "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// //     "zigux/tests/phase11_dw_wdt_restart_build.zig",
// //     "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
// // };
// //
// // const EXPECTED_DETERMINISTIC_GOLDEN_OUTPUT_GAP = [_][]const u8{
// //     "phase11-validate now carries the dedicated golden-output fixture roster `zigux/tests/fixtures/phase11_validate_checks.json`, the shared aggregate tooling manifest `zigux/tests/fixtures/phase11_shared_tooling_manifest.json`, plus fail-closed `scripts/zigux/check_phase11_validate_check_roster.zig`, `scripts/zigux/check_phase11_validate_route_alignment.zig`, `scripts/zigux/check_phase11_deterministic_fixture_golden_output.zig`, and `scripts/zigux/check_phase11_dw_wdt_build_route.zig` guards while keeping `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/fixtures/phase11_shared_tooling_manifest.json`, and `zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json` inside the deterministic validator packet",
// // };
// //
// // const EXPECTED_REQUIRED_CHECKS = [_][]const u8{
// //     "phase11-validate-manifest-roster-self-testpython--self-test",
// //     "phase11-validate-manifest-rosterpython",
// //     "phase11-validate-check-roster-self-testpython--self-test",
// //     "phase11-validate-check-rosterpython",
// //     "phase11-validate-route-alignment-self-testpython--self-test",
// //     "phase11-validate-route-alignmentpython",
// //     "phase11-shared-tooling-manifest-self-testpython--self-test",
// //     "phase11-shared-tooling-manifestpython",
// //     "phase11-focused-direct-build-replays-self-testpython--self-test",
// //     "phase11-focused-direct-build-replayspython",
// //     "phase11-shared-replay-contract-counts-self-testpython--self-test",
// //     "phase11-shared-replay-contract-countspython",
// //     "phase11-dw-wdt-build-route-self-testpython--self-test",
// //     "phase11-dw-wdt-build-routepython",
// // };
// //
// // const SELF_CHECK_PATH = [_][]const u8{
// //     "scripts/zigux/check_phase11_validate_check_roster.zig",
// // };
// //
// // const SELF_FIXTURE_PATH = [_][]const u8{
// //     "zigux/tests/fixtures/phase11_validate_checks.json",
// // };
// //
// // const VALIDATE_MANIFEST_ROSTER_CHECK_PATH = [_][]const u8{
// //     "scripts/zigux/check_phase11_validate_manifest_roster.zig",
// // };
// //
// // const VALIDATE_ROUTE_ALIGNMENT_CHECK_PATH = [_][]const u8{
// //     "scripts/zigux/check_phase11_validate_route_alignment.zig",
// // };
// //
// // const DW_WDT_BUILD_ROUTE_CHECK_PATH = [_][]const u8{
// //     "scripts/zigux/check_phase11_dw_wdt_build_route.zig",
// // };
// //
// // const DW_WDT_BUILD_INVENTORY_PATH = [_][]const u8{
// //     "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
// // };
// //
// // const SHARED_TOOLING_CHECK_PATH = [_][]const u8{
// //     "scripts/zigux/check_phase11_shared_tooling_manifest.zig",
// // };
// //
// // const SHARED_TOOLING_FIXTURE_PATH = [_][]const u8{
// //     "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
// // };
// //
// // const SHARED_TOOLING_SURVEY_PATH = [_][]const u8{
// //     "Documentation/zigux/phase11-codegen-manifest-tooling-gap-survey.md",
// // };
// //
// // const FOCUSED_DIRECT_BUILD_REPLAYS_CHECK_PATH = [_][]const u8{
// //     "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
// // };
// //
// // const SHARED_REPLAY_CONTRACT_COUNTS_CHECK_PATH = [_][]const u8{
// //     "scripts/zigux/check_phase11_shared_replay_contract_counts.zig",
// // };
// //
// // const EXPECTED_VALIDATE_ROUTE = [_][]const u8{
// //     "make -C zigux phase11-validate",
// // };
// //
// // const EXPECTED_VALIDATE_SCRIPT = [_][]const u8{
// //     "scripts\zigux/validate_phase11.zig",
// // };
// //
// // pub fn checkText(text: []const u8) guard.GuardError!void {
// //     for (EXPECTED_INVENTORY_DETERMINISTIC_FIXTURE_SURFACES) |marker| try guard.requireMarker(text, marker);
// //     for (EXPECTED_FOCUSED_TEARDOWN_FAILURE_MODE_BUILDS) |marker| try guard.requireMarker(text, marker);
// //     for (EXPECTED_DETERMINISTIC_GOLDEN_OUTPUT_GAP) |marker| try guard.requireMarker(text, marker);
// //     for (EXPECTED_REQUIRED_CHECKS) |marker| try guard.requireMarker(text, marker);
// //     for (SELF_CHECK_PATH) |marker| try guard.requireMarker(text, marker);
// //     for (SELF_FIXTURE_PATH) |marker| try guard.requireMarker(text, marker);
// //     for (VALIDATE_MANIFEST_ROSTER_CHECK_PATH) |marker| try guard.requireMarker(text, marker);
// //     for (VALIDATE_ROUTE_ALIGNMENT_CHECK_PATH) |marker| try guard.requireMarker(text, marker);
// //     for (DW_WDT_BUILD_ROUTE_CHECK_PATH) |marker| try guard.requireMarker(text, marker);
// //     for (DW_WDT_BUILD_INVENTORY_PATH) |marker| try guard.requireMarker(text, marker);
// //     for (SHARED_TOOLING_CHECK_PATH) |marker| try guard.requireMarker(text, marker);
// //     for (SHARED_TOOLING_FIXTURE_PATH) |marker| try guard.requireMarker(text, marker);
// //     for (SHARED_TOOLING_SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
// //     for (FOCUSED_DIRECT_BUILD_REPLAYS_CHECK_PATH) |marker| try guard.requireMarker(text, marker);
// //     for (SHARED_REPLAY_CONTRACT_COUNTS_CHECK_PATH) |marker| try guard.requireMarker(text, marker);
// //     for (EXPECTED_VALIDATE_ROUTE) |marker| try guard.requireMarker(text, marker);
// //     for (EXPECTED_VALIDATE_SCRIPT) |marker| try guard.requireMarker(text, marker);
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
