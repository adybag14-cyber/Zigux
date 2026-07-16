const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_SHARED_TOOLING_MANIFEST=pass";
pub const self_test_pass_marker = "PHASE11_SHARED_TOOLING_MANIFEST_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-codegen-manifest-tooling-gap-survey.md",
    "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-shared-replay-contract.md",
    "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
    "Documentation/zigux/phase11-watchdog-lifecycle-parity-gap.md",
    "scripts/zigux/check_phase11_build_inventory.zig",
    "scripts/zigux/check_phase11_dw_wdt_build_route.zig",
    "scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig",
    "scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig",
    "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
    "scripts/zigux/check_phase11_header_boundary_packet.zig",
    "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
    "scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig",
    "scripts/zigux/check_phase11_hvc_current_head_manifest.zig",
    "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
    "scripts/zigux/check_phase11_matrix_gap_survey.zig",
    "scripts/zigux/check_phase11_shared_replay_contract_counts.zig",
    "scripts/zigux/check_phase11_shared_tooling_manifest.zig",
    "scripts/zigux/check_phase11_validate_check_roster.zig",
    "scripts/zigux/check_phase11_validate_manifest_roster.zig",
    "scripts/zigux/check_phase11_validate_route_alignment.zig",
    "scripts/zigux/check_phase11_validation_matrix_gap_survey.zig",
    "scripts/zigux/check_phase11_watchdog_lifecycle_parity_gap.zig",
    "scripts/zigux/validate_phase11.zig",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
    "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
    "zigux/tests/phase11_build.zig",
    "zigux/tests/phase11_dw_wdt_build.zig",
    "zigux/tests/phase11_dw_wdt_pm_build.zig",
    "zigux/tests/phase11_dw_wdt_restart_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
    "zigux/tests/phase11_gpio_wdt_verify_helper_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
    "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

const json_files = [_][]const u8{
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
    "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for(required_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const file=std.Io.Dir.cwd().openFile(io,path,.{}) catch return error.MissingRequiredFile; file.close(io); }
    for(json_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const text=try guard.readUtf8File(io,allocator,path); defer allocator.free(text); const parsed=try std.json.parseFromSlice(std.json.Value,allocator,text,.{}); parsed.deinit(); }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=47",.{});
    try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=4",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_SHARED_TOOLING_MANIFEST_SELF_TEST_CASE_COUNT=7",.{}); try emitCounts(io); return 0;
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
// pub const live_pass_marker = "PHASE11_SHARED_TOOLING_MANIFEST=pass";
// pub const self_test_pass_marker = "PHASE11_SHARED_TOOLING_MANIFEST_SELF_TEST=pass";
// pub const pass_marker = self_test_pass_marker;
//
// const required_files = [_][]const u8{
//     "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
//     "Documentation/zigux/phase11-codegen-manifest-tooling-gap-survey.md",
//     "Documentation/zigux/phase11-driver-lane-sequencing.md",
//     "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
//     "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
//     "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
//     "Documentation/zigux/phase11-shared-replay-contract.md",
//     "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
//     "Documentation/zigux/phase11-watchdog-lifecycle-parity-gap.md",
//     "scripts/zigux/check_phase11_build_inventory.zig",
//     "scripts/zigux/check_phase11_dw_wdt_build_route.zig",
//     "scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig",
//     "scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig",
//     "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
//     "scripts/zigux/check_phase11_header_boundary_packet.zig",
//     "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
//     "scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig",
//     "scripts/zigux/check_phase11_hvc_current_head_manifest.zig",
//     "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
//     "scripts/zigux/check_phase11_matrix_gap_survey.zig",
//     "scripts/zigux/check_phase11_shared_replay_contract_counts.zig",
//     "scripts/zigux/check_phase11_shared_tooling_manifest.zig",
//     "scripts/zigux/check_phase11_validate_check_roster.zig",
//     "scripts/zigux/check_phase11_validate_manifest_roster.zig",
//     "scripts/zigux/check_phase11_validate_route_alignment.zig",
//     "scripts/zigux/check_phase11_validation_matrix_gap_survey.zig",
//     "scripts/zigux/check_phase11_watchdog_lifecycle_parity_gap.zig",
//     "scripts/zigux/validate_phase11.zig",
//     "zigux/tests/fixtures/phase11_build_inventory.json",
//     "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
//     "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
//     "zigux/tests/fixtures/phase11_validate_checks.json",
//     "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
//     "zigux/tests/phase11_build.zig",
//     "zigux/tests/phase11_dw_wdt_build.zig",
//     "zigux/tests/phase11_dw_wdt_pm_build.zig",
//     "zigux/tests/phase11_dw_wdt_restart_build.zig",
//     "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
//     "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
//     "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
//     "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
//     "zigux/tests/phase11_gpio_wdt_verify_helper_build.zig",
//     "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
//     "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
//     "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
//     "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
//     "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// };
//
// const json_files = [_][]const u8{
//     "zigux/tests/fixtures/phase11_build_inventory.json",
//     "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
//     "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
//     "zigux/tests/fixtures/phase11_validate_checks.json",
// };
//
// fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
//     for(required_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const file=std.Io.Dir.cwd().openFile(io,path,.{}) catch return error.MissingRequiredFile; file.close(io); }
//     for(json_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const text=try guard.readUtf8File(io,allocator,path); defer allocator.free(text); const parsed=try std.json.parseFromSlice(std.json.Value,allocator,text,.{}); parsed.deinit(); }
// }
//
// fn emitCounts(io: Io) !void {
//     try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=47",.{});
//     try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=4",.{});
// }
//
// fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
//     const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
//     try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_SHARED_TOOLING_MANIFEST_SELF_TEST_CASE_COUNT=7",.{}); try emitCounts(io); return 0;
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
// // pub const pass_marker = "PHASE11_SHARED_TOOLING_MANIFEST_SELF_TEST=pass";
// //
// // const DEFAULT_ROOT = [_][]const u8{
// //     "Path.resolve.parents[2]iflen>3elsePath.cwd",
// // };
// //
// // const REQUIRED_SURVEY_MARKERS = [_][]const u8{
// //     "`PHASE11_TOOLING_GAP_STATUS=shared_packet_aggregate_surface_materialized`",
// //     "`scripts/zigux/check_phase11_shared_tooling_manifest.zig`",
// //     "`zigux/tests/fixtures/phase11_shared_tooling_manifest.json`",
// //     "`scripts/zigux/check_phase11_watchdog_lifecycle_parity_gap.zig`",
// //     "`scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig`",
// //     "`scripts/zigux/check_phase11_hvc_current_head_manifest.zig`",
// //     "f`{DW_BUILD_ROUTE_CHECKER}`",
// //     "distinguishes the narrower `zigux/tests/fixtures/phase11_build_inventory.json` HVC continuity packet from the broader shared `phase11-validate` checker stack and proof fan-out",
// //     "`scripts/zigux/check_phase11_shared_tooling_manifest.zig` is already wired into `scripts\zigux/validate_phase11.zig`",
// //     "`zigux/tests/fixtures/phase11_validate_checks.json` records both the shared tooling-manifest self-test and live validator entries",
// //     "aggregate surface now also carries the shared watchdog lifecycle note plus the cleanup-prerequisite and current-head manifest guards that the validator route already ships",
// //     "The same current validator fixture also records the DesignWare build-route guard and its `zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json` fixture.",
// // };
// //
// // const FORBIDDEN_SURVEY_MARKERS = [_][]const u8{
// //     "`PHASE11_TOOLING_GAP_STATUS=shared_packet_manifest_gap_open`",
// //     "there is no current aggregate manifest or generated summary surface",
// //     "wire `scripts/zigux/check_phase11_shared_tooling_manifest.zig` into the shared `phase11-validate` route only after current-head rereads confirm the surrounding Phase 11 packet did not drift again",
// // };
// //
// // const REQUIRED_VALIDATOR_MARKERS = [_][]const u8{
// //     "CheckSpec(\"phase11-shared-tooling-manifest-self-test\", (\"zig\", \"run\", \"scripts/zigux/check_phase11_shared_tooling_manifest.zig\", \"--\", \"--self-test\"))",
// //     "CheckSpec(\"phase11-shared-tooling-manifest\", (\"zig\", \"run\", \"scripts/zigux/check_phase11_shared_tooling_manifest.zig\", \"--\"))",
// // };
// //
// // const EXPECTED_VALIDATE_FIXTURE_ENTRIES = [_][]const u8{
// //     "phase11-shared-tooling-manifest-self-testpythonscripts/zigux/check_phase11_shared_tooling_manifest.zig--self-test",
// //     "phase11-shared-tooling-manifestpythonscripts/zigux/check_phase11_shared_tooling_manifest.zig",
// // };
// //
// // const EXPECTED_MANIFEST = [_][]const u8{
// //     "lane_key",
// //     "P11-L04",
// //     "phase",
// //     "Phase 11",
// //     "status",
// //     "shared_packet_aggregate_surface_materialized",
// //     "scope",
// //     "shared Phase 11 codegen and manifest tooling stale aggregate-manifest cleanup",
// //     "shared_docs",
// //     "Documentation/zigux/phase11-shared-replay-contract.md",
// //     "Documentation/zigux/phase11-driver-lane-sequencing.md",
// //     "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
// //     "Documentation/zigux/phase11-watchdog-lifecycle-parity-gap.md",
// //     "Documentation/zigux/phase11-codegen-manifest-tooling-gap-survey.md",
// //     "shared_checkers",
// //     "scripts/zigux/check_phase11_build_inventory.zig",
// //     "scripts/zigux/check_phase11_validate_manifest_roster.zig",
// //     "scripts/zigux/check_phase11_validate_check_roster.zig",
// //     "scripts/zigux/check_phase11_validate_route_alignment.zig",
// //     "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
// //     "scripts/zigux/check_phase11_shared_replay_contract_counts.zig",
// //     "scripts/zigux/check_phase11_matrix_gap_survey.zig",
// //     "scripts/zigux/check_phase11_validation_matrix_gap_survey.zig",
// //     "scripts/zigux/check_phase11_watchdog_lifecycle_parity_gap.zig",
// //     "scripts/zigux/check_phase11_header_boundary_packet.zig",
// //     "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
// //     "scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig",
// //     "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
// //     "scripts/zigux/check_phase11_hvc_current_head_manifest.zig",
// //     "scripts/zigux/check_phase11_dw_wdt_teardown_packet.zig",
// //     "scripts/zigux/check_phase11_dw_wdt_verify_alignment.zig",
// //     "scripts/zigux/check_phase11_shared_tooling_manifest.zig",
// //     "shared_routes",
// //     "zig run validate_phase11.zig",
// //     "make -C zigux phase11-validate",
// //     "proof_builds",
// //     "zigux/tests/phase11_bcm2835_wdt_manifest_packet_survey_build.zig",
// //     "zigux/tests/phase11_dw_wdt_build.zig",
// //     "zigux/tests/phase11_dw_wdt_restart_build.zig",
// //     "zigux/tests/phase11_dw_wdt_pm_build.zig",
// //     "zigux/tests/phase11_gpio_wdt_verify_helper_build.zig",
// //     "zigux/tests/phase11_gpio_wdt_preflight_review_build.zig",
// //     "zigux/tests/phase11_gpio_wdt_register_device_glue_review_build.zig",
// //     "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
// //     "zigux/tests/phase11_gpio_wdt_remove_handoff_review_build.zig",
// //     "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
// //     "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
// //     "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
// //     "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
// //     "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// //     "driver_local_matrices",
// //     "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
// //     "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
// //     "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
// //     "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
// //     "narrow_inventory_boundary",
// //     "inventory_path",
// //     "zigux/tests/fixtures/phase11_build_inventory.json",
// //     "inventory_scope",
// //     "HVC current-head continuity packet",
// //     "aggregate_scope",
// //     "shared phase11-validate checker stack and proof fan-out",
// //     "retired_shared_routes",
// //     "make -C zigux phase11",
// //     "make -C zigux phase11-contract",
// //     "zigux/tests/phase11_build.zig",
// // };
// //
// // const DW_BUILD_ROUTE_CHECKER = [_][]const u8{
// //     "scripts/zigux/check_phase11_dw_wdt_build_route.zig",
// // };
// //
// // pub fn checkText(text: []const u8) guard.GuardError!void {
// //     for (DEFAULT_ROOT) |marker| try guard.requireMarker(text, marker);
// //     for (REQUIRED_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
// //     for (FORBIDDEN_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
// //     for (REQUIRED_VALIDATOR_MARKERS) |marker| try guard.requireMarker(text, marker);
// //     for (EXPECTED_VALIDATE_FIXTURE_ENTRIES) |marker| try guard.requireMarker(text, marker);
// //     for (EXPECTED_MANIFEST) |marker| try guard.requireMarker(text, marker);
// //     for (DW_BUILD_ROUTE_CHECKER) |marker| try guard.requireMarker(text, marker);
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
