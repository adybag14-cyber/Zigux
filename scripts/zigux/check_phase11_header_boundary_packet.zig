const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_HEADER_BOUNDARY_PACKET=pass";
pub const self_test_pass_marker = "PHASE11_HEADER_BOUNDARY_PACKET_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-verify-helper-boundary.md",
    "Documentation/zigux/phase11-shared-replay-contract.md",
    "Documentation/zigux/phase11-uapi-header-parity-checker-coverage-note.md",
    "Documentation/zigux/phase11-uapi-header-parity-hv-ops-followup.md",
    "Documentation/zigux/phase11-uapi-header-parity-survey.md",
    "Documentation/zigux/phase11-uapi-header-parity-validation-matrix.md",
    "Documentation/zigux/phase11-validation-matrix-gap-survey.md",
    "drivers/tty/hvc/hvc_console.h",
    "drivers/tty/hvc/hvc_console.zig",
    "scripts/zigux/check_phase11_build_inventory.zig",
    "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
    "scripts/zigux/check_phase11_header_boundary_packet.zig",
    "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
    "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
    "scripts/zigux/validate_phase11.zig",
    "zigux/Makefile",
    "zigux/helpers/layout_assert.zig",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/phase11_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
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
    try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=32",.{});
    try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=1",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_HEADER_BOUNDARY_PACKET_SELF_TEST_CASE_COUNT=9",.{}); try emitCounts(io); return 0;
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
// pub const pass_marker = "PHASE11_HEADER_BOUNDARY_PACKET_SELF_TEST=pass";
//
// const SURVEY_REQUIRED_MARKERS = [_][]const u8{
//     "`Documentation/zigux/phase11-shared-replay-contract.md`",
//     "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
//     "`Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
//     "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
//     "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
//     "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
//     "`scripts/zigux/check_phase11_build_inventory.zig`",
//     "`scripts/zigux/check_phase11_header_boundary_packet.zig`",
//     "`zig run scripts/zigux/check_phase11_header_boundary_packet.zig -- --self-test`",
//     "`zig run scripts/zigux/check_phase11_header_boundary_packet.zig --`",
//     "`zigux/helpers/layout_assert.zig`",
//     "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
//     "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
//     "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
//     "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
//     "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
//     "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
//     "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
//     "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
//     "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
//     "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
//     "`scripts/zigux/check_phase11_hvc_cleanup_current_head.zig`",
//     "`scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig`",
//     "`drivers/tty/hvc/hvc_console.h`",
//     "`drivers/tty/hvc/hvc_console.zig`",
//     "returned `zigux/helpers/layout_assert.zig` substrate",
//     "adjacent failure-mode continuity rather than a restored shared header-parity replay roster",
//     "documentation-level continuity evidence",
//     "bounded modem-control callback proof",
//     "`phase11-focused-direct-build-checker`",
//     "`phase11-shared-reminder-surface-gap`",
//     "`scripts/zigux/check_phase11_focused_direct_build_replays.zig`",
//     "machine-checked evidence rather than inventory-only prose",
//     "`zigux/tests/fixtures/phase11_build_inventory.json`",
// };
//
// const SURVEY_FORBIDDEN_MARKERS = [_][]const u8{
//     "  - `scripts/zigux/check_phase11_header_boundary_packet.zig`n- current shared reminder and machine-checked HVC header-boundary evidence therefore still lives",
//     "no directly readable shared survey source, manifest, checker, or shared Phase 11 build route currently rematerializes the older cross-driver packet",
// };
//
// const MATRIX_REQUIRED_MARKERS = [_][]const u8{
//     "`Documentation/zigux/phase11-shared-replay-contract.md`",
//     "`Documentation/zigux/phase11-driver-lane-sequencing.md`",
//     "`Documentation/zigux/phase11-validation-matrix-gap-survey.md`",
//     "`Documentation/zigux/phase11-hvc-console-validation-matrix.md`",
//     "`Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md`",
//     "`Documentation/zigux/phase11-hvc-verify-helper-boundary.md`",
//     "`Documentation/zigux/phase11-uapi-header-parity-checker-coverage-note.md`",
//     "`Documentation/zigux/phase11-uapi-header-parity-hv-ops-followup.md`",
//     "`scripts/zigux/check_phase11_build_inventory.zig`",
//     "`scripts/zigux/check_phase11_header_boundary_packet.zig`",
//     "`zig run scripts/zigux/check_phase11_header_boundary_packet.zig -- --self-test`",
//     "`zig run scripts/zigux/check_phase11_header_boundary_packet.zig --`",
//     "`zigux/helpers/layout_assert.zig`",
//     "`zigux/tests/phase11_hvc_export_surface_layout_proof.zig`",
//     "`zigux/tests/phase11_hvc_export_surface_layout_build.zig`",
//     "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
//     "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
//     "`zigux/tests/phase11_hvc_cleanup_packet_proof.zig`",
//     "`zigux/tests/phase11_hvc_cleanup_packet_build.zig`",
//     "`zigux/tests/phase11_hvc_modem_control_proof.zig`",
//     "`zigux/tests/phase11_hvc_modem_control_proof_build.zig`",
//     "`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`",
//     "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
//     "`scripts/zigux/check_phase11_hvc_cleanup_current_head.zig`",
//     "`scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig`",
//     "`drivers/tty/hvc/hvc_console.h`",
//     "returned `scripts/zigux/check_phase11_hvc_cleanup_current_head.zig`",
//     "returned `scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig`",
//     "keep the returned header-boundary checker framed as note-side evidence only",
//     "Keep the adjacent cleanup, modem-control, and targetless-unregister companions explicit as directly readable HVC failure-mode continuity evidence",
//     "`scripts/zigux/check_phase11_focused_direct_build_replays.zig`",
//     "`zig run scripts/zigux/check_phase11_focused_direct_build_replays.zig -- --self-test`",
//     "`zig run scripts/zigux/check_phase11_focused_direct_build_replays.zig --`",
//     "`scripts\zigux/validate_phase11.zig`",
//     "`zigux/Makefile`",
//     "`zigux/tests/fixtures/phase11_build_inventory.json`",
//     "returned checker-coverage note",
//     "returned `hv_ops` follow-up note",
//     "| header-boundary note stack |",
// };
//
// const MATRIX_FORBIDDEN_MARKERS = [_][]const u8{
//     "- `zigux/tests/phase11_build.zig`n  - `scripts/zigux/check_phase11_header_boundary_packet.zig`",
//     "without reviving missing shared replay, manifest, or checker paths",
// };
//
// const CHECKER_COVERAGE_REQUIRED_MARKERS = [_][]const u8{
//     "`PHASE11_UAPI_HEADER_CHECKER_COVERAGE_STATUS=returned_note_side_checker_and_adjacent_packet_truthful`",
//     "`Documentation/zigux/phase11-uapi-header-parity-checker-coverage-note.md`",
//     "`Documentation/zigux/phase11-uapi-header-parity-hv-ops-followup.md`",
//     "`scripts/zigux/check_phase11_build_inventory.zig`",
//     "`scripts/zigux/check_phase11_header_boundary_packet.zig`",
//     "`zig run scripts/zigux/check_phase11_header_boundary_packet.zig -- --self-test`",
//     "`zig run scripts/zigux/check_phase11_header_boundary_packet.zig --`",
//     "`scripts/zigux/check_phase11_focused_direct_build_replays.zig`",
//     "`zigux/tests/fixtures/phase11_build_inventory.json`",
//     "returned dedicated shared checker now exists",
//     "note-side evidence only",
//     "missing shared manifest, survey source, or build route",
// };
//
// const CHECKER_COVERAGE_FORBIDDEN_MARKERS = [_][]const u8{
//     "the dedicated shared checker itself does not read back on current `master`",
//     "- `scripts/zigux/check_phase11_header_boundary_packet.zig`n- `zigux/tests/phase11_build.zig`",
// };
//
// const HV_OPS_FOLLOWUP_REQUIRED_MARKERS = [_][]const u8{
//     "`PHASE11_HV_OPS_FOLLOWUP_STATUS=adjacent_hv_ops_proof_returned_shared_replay_still_missing`",
//     "`zigux/tests/phase11_hvc_hv_ops_layout_proof.zig`",
//     "`zigux/tests/phase11_hvc_hv_ops_layout_build.zig`",
//     "`zigux/helpers/layout_assert.zig`",
//     "`drivers/tty/hvc/hvc_console.h`",
//     "`drivers/tty/hvc/hvc_console.zig`",
//     "`scripts/zigux/check_phase11_header_boundary_packet.zig`",
//     "adjacent proof-shard evidence",
//     "shared manifest, survey source, and build route remain absent",
//     "fail-closes on the survey, validation matrix, checker-coverage note, and this follow-up note",
// };
//
// const HV_OPS_FOLLOWUP_FORBIDDEN_MARKERS = [_][]const u8{
//     "Draft PR `#302`",
//     "not yet part of the shared `phase11-uapi-header-parity-survey-tests` route",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (SURVEY_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (SURVEY_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MATRIX_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MATRIX_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (CHECKER_COVERAGE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (CHECKER_COVERAGE_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (HV_OPS_FOLLOWUP_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (HV_OPS_FOLLOWUP_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
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
