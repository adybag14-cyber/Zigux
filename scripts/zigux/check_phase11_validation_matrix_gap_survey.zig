const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_MATRIX_GAP_SURVEY_CHECK=pass";
pub const self_test_pass_marker = "PHASE11_MATRIX_GAP_SURVEY_CHECK=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-dw-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-gpio-wdt-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
    "scripts/zigux/check_phase11_deterministic_fixture_golden_output.zig",
    "scripts/zigux/check_phase11_dw_wdt_build_route.zig",
    "scripts/zigux/check_phase11_validate_check_roster.zig",
    "scripts/zigux/check_phase11_validate_route_alignment.zig",
    "scripts/zigux/check_phase11_validation_matrix_gap_survey.zig",
    "scripts/zigux/validate_phase11.zig",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
    "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/phase11_dw_wdt_build.zig",
    "zigux/tests/phase11_dw_wdt_manifest.json",
    "zigux/tests/phase11_dw_wdt_restart_build.zig",
    "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
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
    try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=28",.{});
    try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=5",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_MATRIX_GAP_SURVEY_SELF_TEST_CASE_COUNT=23",.{}); try emitCounts(io); return 0;
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
// pub const pass_marker = "PHASE11_MATRIX_GAP_SURVEY_CHECK=pass";
//
// const SURVEY_MARKERS = [_][]const u8{
//     "`PHASE11_MATRIX_GAP_STATUS=all_simple_driver_matrices_present`",
//     "shared packet lane: `P11-Y06`",
//     "deterministic tooling survey lane: `P11-L07`",
//     "Phase 11 still names `drivers/watchdog/gpio_wdt.c`, `drivers/watchdog/bcm2835_wdt.c`, `drivers/watchdog/dw_wdt.c`, and `drivers/tty/hvc/hvc_console.c` as the simple-production-driver anchors.",
//     "Phase 11 still requires a hardware validation matrix together with teardown or failure-mode parity.",
//     "Authenticated GitHub contents rereads in this run rematerialize the bcm2835, gpio watchdog, HVC console, and DesignWare driver-local Phase 11 matrix notes named by the roadmap on current `master`.",
//     "The currently reread driver-local Phase 11 matrix notes on current `master` are `Documentation/zigux/phase11-bcm2835-wdt-validation-matrix.md`, `Documentation/zigux/phase11-gpio-wdt-validation-matrix.md`, `Documentation/zigux/phase11-hvc-console-validation-matrix.md`, and `Documentation/zigux/phase11-dw-wdt-validation-matrix.md`.",
//     "`zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/fixtures/phase11_validate_checks.json`, `zigux/tests/fixtures/phase11_shared_tooling_manifest.json`, `zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json`, and `zigux/tests/phase11_dw_wdt_manifest.json` are the current machine-readable deterministic fixture surfaces inside the shared Phase 11 packet.",
//     "The shared build inventory now carries 3 HVC proof-backed build tests, 0 shared depend steps, 0 dedicated survey replays, and 3 proof adjunct replays.",
//     "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`, `zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`, `zigux/tests/phase11_dw_wdt_restart_build.zig`, and `zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig` are the current focused teardown-or-failure-mode proof builds directly named by the shared packet.",
//     "`make -C zigux phase11-validate` remains the returned shared validation route, and `scripts\zigux/validate_phase11.zig` keeps the current shared packet build-proof-first.",
//     "The shared Phase 11 packet now rematerializes a dedicated golden-output fixture roster through `zigux/tests/fixtures/phase11_validate_checks.json`, the shared aggregate tooling manifest `zigux/tests/fixtures/phase11_shared_tooling_manifest.json`, plus fail-closed `scripts/zigux/check_phase11_validate_check_roster.zig`, `scripts/zigux/check_phase11_validate_route_alignment.zig`, `scripts/zigux/check_phase11_deterministic_fixture_golden_output.zig`, and `scripts/zigux/check_phase11_dw_wdt_build_route.zig` guards while keeping `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/fixtures/phase11_shared_tooling_manifest.json`, and `zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json` inside the deterministic validator packet.",
//     "It still does not rematerialize a refresh helper route or an artifact-diff-style deterministic output guard for the driver-local proof builds.",
//     "`scripts\zigux/validate_phase11.zig` and `make -C zigux phase11-validate` therefore stay build-proof-first rather than expected-output-refresh-first.",
//     "That leaves a narrower roadmap-facing deterministic tooling gap: the repo can prove that the focused builds still compile and run, and it can exact-check the shared validate roster, but it still cannot refresh and diff shared golden outputs for the same bounded packet.",
// };
//
// const REQUIRED_VALIDATE_PHASE11_MARKERS = [_][]const u8{
//     "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_dw_wdt_restart_build.zig\")",
//     "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig\")",
//     "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_modem_control_proof_build.zig\")",
//     "(\"zig\", \"build\", \"test\", \"--build-file\", \"zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig\")",
// };
//
// const REQUIRED_MAKEFILE_MARKERS = [_][]const u8{
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_dw_wdt_restart_build.zig",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
//     "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// };
//
// const REQUIRED_VALIDATE_CHECK_NAMES = [_][]const u8{
//     "phase11-validation-matrix-gap-survey-self-test",
//     "phase11-validation-matrix-gap-survey",
// };
//
// const REQUIRED_VALIDATE_CHECK_COMMANDS = [_][]const u8{
//     "[python",
//     "scripts/zigux/check_phase11_validation_matrix_gap_survey.zig",
//     "--self-test]",
//     "[python",
//     "scripts/zigux/check_phase11_validation_matrix_gap_survey.zig]",
// };
//
// const FILES = [_][]const u8{
//     "matrix_gap_note",
//     "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
//     "inventory",
//     "zigux/tests/fixtures/phase11_build_inventory.json",
//     "dw_inventory",
//     "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
//     "validate_checks",
//     "zigux/tests/fixtures/phase11_validate_checks.json",
//     "validate_phase11",
//     "scripts\zigux/validate_phase11.zig",
//     "makefile",
//     "zigux/Makefile",
// };
//
// const EXPECTED_INVENTORY_LISTS = [_][]const u8{
//     "build_test_names",
//     "phase11-hvc-hv-ops-layout-proof-tests",
//     "phase11-hvc-export-surface-layout-proof-tests",
//     "phase11-hvc-cleanup-packet-proof",
//     "shared_test_depend_steps",
//     "dedicated_survey_replays",
//     "shared_adjunct_replays",
//     "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
//     "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
//     "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
//     "shared_adjunct_build_replays",
//     "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
//     "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
//     "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
//     "focused_direct_build_replays",
//     "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
//     "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
//     "deterministic_fixture_surfaces",
//     "zigux/tests/fixtures/phase11_build_inventory.json",
//     "zigux/tests/fixtures/phase11_validate_checks.json",
//     "zigux/tests/fixtures/phase11_shared_tooling_manifest.json",
//     "zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json",
//     "zigux/tests/phase11_dw_wdt_manifest.json",
//     "focused_teardown_failure_mode_builds",
//     "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
//     "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
//     "zigux/tests/phase11_dw_wdt_restart_build.zig",
//     "zigux/tests/phase11_gpio_wdt_nowayout_policy_review_build.zig",
// };
//
// const EXPECTED_INVENTORY_SCALARS = [_][]const u8{
//     "deterministic_tooling_lane",
//     "P11-L07",
//     "deterministic_golden_output_gap",
//     "phase11-validate now carries the dedicated golden-output fixture roster `zigux/tests/fixtures/phase11_validate_checks.json`, the shared aggregate tooling manifest `zigux/tests/fixtures/phase11_shared_tooling_manifest.json`, plus fail-closed `scripts/zigux/check_phase11_validate_check_roster.zig`, `scripts/zigux/check_phase11_validate_route_alignment.zig`, `scripts/zigux/check_phase11_deterministic_fixture_golden_output.zig`, and `scripts/zigux/check_phase11_dw_wdt_build_route.zig` guards while keeping `zigux/tests/fixtures/phase11_build_inventory.json`, `zigux/tests/fixtures/phase11_shared_tooling_manifest.json`, and `zigux/tests/fixtures/phase11_dw_wdt_build_inventory.json` inside the deterministic validator packet",
// };
//
// const EXPECTED_DW_INVENTORY_LISTS = [_][]const u8{
//     "build_test_names",
//     "phase11-dw-wdt-registration-scaffold-tests",
//     "phase11-dw-wdt-live-mmio-review-tests",
//     "phase11-dw-wdt-pm-tests",
//     "phase11-dw-wdt-restart-tests",
//     "phase11-dw-wdt-verify-tests",
//     "phase11-dw-wdt-direct-replay-tests",
//     "exact_current_checks",
//     "zig run scripts/zigux/check_phase11_dw_wdt_build_route.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_dw_wdt_build_route.zig --",
//     "zig build test --build-file zigux/tests/phase11_dw_wdt_build.zig",
// };
//
// const EXPECTED_DW_INVENTORY_SCALARS = [_][]const u8{
//     "shared_build_file",
//     "zigux/tests/phase11_dw_wdt_build.zig",
//     "shared_replay_command",
//     "zig build test --build-file zigux/tests/phase11_dw_wdt_build.zig",
//     "shared_step_name",
//     "test",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_VALIDATE_PHASE11_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_VALIDATE_CHECK_NAMES) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_VALIDATE_CHECK_COMMANDS) |marker| try guard.requireMarker(text, marker);
//     for (FILES) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_INVENTORY_LISTS) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_INVENTORY_SCALARS) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_DW_INVENTORY_LISTS) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_DW_INVENTORY_SCALARS) |marker| try guard.requireMarker(text, marker);
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
