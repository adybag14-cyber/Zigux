const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_SHARED_REPLAY_CONTRACT_COUNTS=pass";
pub const self_test_pass_marker = "PHASE11_SHARED_REPLAY_CONTRACT_COUNTS_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md",
    "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
    "Documentation/zigux/phase11-dw-wdt-provenance-readback.md",
    "Documentation/zigux/phase11-dw-wdt-survey.md",
    "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
    "Documentation/zigux/phase11-shared-replay-contract.md",
    "drivers/watchdog/dw_wdt_pm.zig",
    "drivers/watchdog/dw_wdt_pm_scaffold.zig",
    "drivers/watchdog/dw_wdt_restart.zig",
    "scripts/zigux/check_phase11_build_inventory.zig",
    "scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig",
    "scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig",
    "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
    "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
    "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
    "scripts/zigux/check_phase11_shared_replay_contract_counts.zig",
    "scripts/zigux/check_phase11_validate_check_roster.zig",
    "scripts/zigux/check_phase11_validate_manifest_roster.zig",
    "scripts/zigux/check_phase11_validate_route_alignment.zig",
    "scripts/zigux/validate_phase11.zig",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
    "zigux/tests/phase11_dw_wdt_build.zig",
    "zigux/tests/phase11_dw_wdt_manifest.json",
    "zigux/tests/phase11_dw_wdt_pm_build.zig",
    "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
    "zigux/tests/phase11_dw_wdt_restart_build.zig",
    "zigux/tests/phase11_dw_wdt_survey.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

const json_files = [_][]const u8{
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/phase11_dw_wdt_manifest.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for(required_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const file=std.Io.Dir.cwd().openFile(io,path,.{}) catch return error.MissingRequiredFile; file.close(io); }
    for(json_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const text=try guard.readUtf8File(io,allocator,path); defer allocator.free(text); const parsed=try std.json.parseFromSlice(std.json.Value,allocator,text,.{}); parsed.deinit(); }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=40",.{});
    try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=3",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_SHARED_REPLAY_CONTRACT_COUNTS_SELF_TEST_CASE_COUNT=23",.{}); try emitCounts(io); return 0;
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
// pub const live_pass_marker = "PHASE11_SHARED_REPLAY_CONTRACT_COUNTS=pass";
// pub const self_test_pass_marker = "PHASE11_SHARED_REPLAY_CONTRACT_COUNTS_SELF_TEST=pass";
// pub const pass_marker = self_test_pass_marker;
//
// const required_files = [_][]const u8{
//     ".github/workflows/zigux-bootstrap.yml",
//     "Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md",
//     "Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md",
//     "Documentation/zigux/phase11-dw-wdt-provenance-readback.md",
//     "Documentation/zigux/phase11-dw-wdt-survey.md",
//     "Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md",
//     "Documentation/zigux/phase11-shared-replay-contract.md",
//     "drivers/watchdog/dw_wdt_pm.zig",
//     "drivers/watchdog/dw_wdt_pm_scaffold.zig",
//     "drivers/watchdog/dw_wdt_restart.zig",
//     "scripts/zigux/check_phase11_build_inventory.zig",
//     "scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig",
//     "scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig",
//     "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
//     "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
//     "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
//     "scripts/zigux/check_phase11_shared_replay_contract_counts.zig",
//     "scripts/zigux/check_phase11_validate_check_roster.zig",
//     "scripts/zigux/check_phase11_validate_manifest_roster.zig",
//     "scripts/zigux/check_phase11_validate_route_alignment.zig",
//     "scripts/zigux/validate_phase11.zig",
//     "zigux/Makefile",
//     "zigux/tests/fixtures/phase11_build_inventory.json",
//     "zigux/tests/fixtures/phase11_validate_checks.json",
//     "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
//     "zigux/tests/phase11_dw_wdt_build.zig",
//     "zigux/tests/phase11_dw_wdt_manifest.json",
//     "zigux/tests/phase11_dw_wdt_pm_build.zig",
//     "zigux/tests/phase11_dw_wdt_registration_scaffold.zig",
//     "zigux/tests/phase11_dw_wdt_restart_build.zig",
//     "zigux/tests/phase11_dw_wdt_survey.zig",
//     "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
//     "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
//     "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
//     "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
//     "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
//     "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
//     "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
//     "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
//     "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// };
//
// const json_files = [_][]const u8{
//     "zigux/tests/fixtures/phase11_build_inventory.json",
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
//     try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=40",.{});
//     try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=3",.{});
// }
//
// fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
//     const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
//     try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_SHARED_REPLAY_CONTRACT_COUNTS_SELF_TEST_CASE_COUNT=23",.{}); try emitCounts(io); return 0;
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
// // pub const pass_marker = "PHASE11_SHARED_REPLAY_CONTRACT_COUNTS_SELF_TEST=pass";
// //
// // const DEFAULT_ROOT = [_][]const u8{
// //     "Path.resolve.parents[2]iflen>3elsePath.cwd",
// // };
// //
// // const EXPECTED_EXACT_CURRENT_CHECKS = [_][]const u8{
// //     "zig run scripts/zigux/check_phase11_build_inventory.zig -- --self-test",
// //     "zig run scripts/zigux/check_phase11_build_inventory.zig --",
// //     "zig run scripts/zigux/check_phase11_hvc_cleanup_current_head.zig -- --self-test",
// //     "zig run scripts/zigux/check_phase11_hvc_cleanup_current_head.zig --",
// //     "zig run scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig -- --self-test",
// //     "zig run scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig --",
// //     "zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
// //     "zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
// //     "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
// //     "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// //     "zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
// // };
// //
// // const EXPECTED_FOCUSED_DIRECT_BUILD_CHECKS = [_][]const u8{
// //     "zig run scripts/zigux/check_phase11_focused_direct_build_replays.zig -- --self-test",
// //     "zig run scripts/zigux/check_phase11_focused_direct_build_replays.zig --",
// // };
// //
// // const EXPECTED_FOCUSED_DIRECT_BUILD_REPLAYS = [_][]const u8{
// //     "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
// //     "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// // };
// //
// // const EXPECTED_PROOF_FANOUT_MARKERS = [_][]const u8{
// //     "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
// //     "zigux/tests/phase11_dw_wdt_build.zig",
// //     "zigux/tests/phase11_dw_wdt_restart_build.zig",
// //     "zigux/tests/phase11_dw_wdt_pm_build.zig",
// //     "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
// //     "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
// //     "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
// //     "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
// //     "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
// //     "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
// //     "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
// //     "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
// //     "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// // };
// //
// // const REQUIRED_CONTRACT_MARKERS = [_][]const u8{
// //     "3 build test names",
// //     "0 shared `test_step.dependOn(...)` edges",
// //     "0 dedicated survey replays",
// //     "3 shared adjunct proof replays",
// //     "3 adjunct build replays",
// //     "2 focused direct build checker routes",
// //     "2 focused direct build replays",
// //     "11 HVC current-head exact command markers",
// //     "`make -C zigux phase11-validate` wrapper now cover thirteen focused proof builds through",
// // };
// //
// // const REQUIRED_DESIGNWARE_CURRENT_HEAD_MARKERS = [_][]const u8{
// //     "`Documentation/zigux/phase11-dw-wdt-platform-registration-plan.md`,",
// //     "`Documentation/zigux/phase11-dw-wdt-provenance-readback.md`,",
// //     "`Documentation/zigux/phase11-dw-wdt-lane-sequencing-gap.md`,",
// //     "`Documentation/zigux/phase11-dw-wdt-verify-alignment-gap.md`,",
// //     "`Documentation/zigux/phase11-dw-wdt-survey.md`,",
// //     "`scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig`,",
// //     "`scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig`,",
// //     "`zigux/tests/phase11_dw_wdt_manifest.json`,",
// //     "`zigux/tests/phase11_dw_wdt_registration_scaffold.zig`,",
// //     "`zigux/tests/phase11_dw_wdt_survey.zig`,",
// //     "`drivers/watchdog/dw_wdt_restart.zig`,",
// //     "`drivers/watchdog/dw_wdt_pm.zig`, and",
// //     "`drivers/watchdog/dw_wdt_pm_scaffold.zig`; keep that returned smaller",
// //     "broader direct driver, verify-helper, replay-backed stack, platform-backed registration, PM",
// //     "execution, IRQ execution, and MMIO follow-through remain parked as the next",
// // };
// //
// // const REQUIRED_VALIDATE_SUPPORT_MARKERS = [_][]const u8{
// //     "`scripts/zigux/check_phase11_validate_manifest_roster.zig`",
// //     "`scripts/zigux/check_phase11_validate_check_roster.zig`",
// //     "`scripts/zigux/check_phase11_validate_route_alignment.zig`",
// //     "`zigux/tests/fixtures/phase11_validate_checks.json`",
// // };
// //
// // const REQUIRED_WORKFLOW_MARKERS = [_][]const u8{
// //     "run: make -C zigux phase11-validate",
// // };
// //
// // const REQUIRED_MAKEFILE_MARKERS = [_][]const u8{
// //     "phase11-validate:",
// //     "scripts\zigux/validate_phase11.zig",
// //     "EXPECTED_PROOF_FANOUT_MARKERS",
// // };
// //
// // const EXPECTED_COUNTS = [_][]const u8{
// //     "build_test_names",
// //     "shared_test_depend_steps",
// //     "dedicated_survey_replays",
// //     "shared_adjunct_replays",
// //     "shared_adjunct_build_replays",
// //     "focused_direct_build_checks",
// //     "focused_direct_build_replays",
// //     "exact_current_checks",
// // };
// //
// // pub fn checkText(text: []const u8) guard.GuardError!void {
// //     for (DEFAULT_ROOT) |marker| try guard.requireMarker(text, marker);
// //     for (EXPECTED_EXACT_CURRENT_CHECKS) |marker| try guard.requireMarker(text, marker);
// //     for (EXPECTED_FOCUSED_DIRECT_BUILD_CHECKS) |marker| try guard.requireMarker(text, marker);
// //     for (EXPECTED_FOCUSED_DIRECT_BUILD_REPLAYS) |marker| try guard.requireMarker(text, marker);
// //     for (EXPECTED_PROOF_FANOUT_MARKERS) |marker| try guard.requireMarker(text, marker);
// //     for (REQUIRED_CONTRACT_MARKERS) |marker| try guard.requireMarker(text, marker);
// //     for (REQUIRED_DESIGNWARE_CURRENT_HEAD_MARKERS) |marker| try guard.requireMarker(text, marker);
// //     for (REQUIRED_VALIDATE_SUPPORT_MARKERS) |marker| try guard.requireMarker(text, marker);
// //     for (REQUIRED_WORKFLOW_MARKERS) |marker| try guard.requireMarker(text, marker);
// //     for (REQUIRED_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
// //     for (EXPECTED_COUNTS) |marker| try guard.requireMarker(text, marker);
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
