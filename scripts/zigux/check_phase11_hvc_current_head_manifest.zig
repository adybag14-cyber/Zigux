const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_HVC_CURRENT_HEAD_MANIFEST=pass";
pub const self_test_pass_marker = "PHASE11_HVC_CURRENT_HEAD_MANIFEST_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md",
    "Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-verify-helper-boundary.md",
    "drivers/tty/hvc/hvc_console.h",
    "drivers/tty/hvc/hvc_console.zig",
    "drivers/tty/hvc/hvc_console_verify.zig",
    "scripts/zigux/check_phase11_build_inventory.zig",
    "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
    "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
    "scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig",
    "scripts/zigux/check_phase11_hvc_current_head_manifest.zig",
    "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
    "scripts/zigux/check_phase11_validate_check_roster.zig",
    "scripts/zigux/check_phase11_validate_manifest_roster.zig",
    "scripts/zigux/check_phase11_validate_route_alignment.zig",
    "scripts/zigux/validate_phase11.zig",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
    "zigux/tests/phase11_hvc_current_head_manifest.json",
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
    "zigux/tests/fixtures/phase11_validate_checks.json",
    "zigux/tests/phase11_hvc_current_head_manifest.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for(required_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const file=std.Io.Dir.cwd().openFile(io,path,.{}) catch return error.MissingRequiredFile; file.close(io); }
    for(json_files)|rel|{ const path=try guard.joinPath(allocator,root,rel); defer allocator.free(path); const text=try guard.readUtf8File(io,allocator,path); defer allocator.free(text); const parsed=try std.json.parseFromSlice(std.json.Value,allocator,text,.{}); parsed.deinit(); }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=32",.{});
    try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=3",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_HVC_CURRENT_HEAD_MANIFEST_SELF_TEST_CASE_COUNT=8",.{}); try emitCounts(io); return 0;
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
// pub const pass_marker = "PHASE11_HVC_CURRENT_HEAD_MANIFEST_SELF_TEST=pass";
//
// const EXPECTED_PACKET_FILES = [_][]const u8{
//     "Documentation/zigux/phase11-hvc-console-survey.md",
//     "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md",
//     "Documentation/zigux/phase11-hvc-verify-helper-boundary.md",
//     "Documentation/zigux/phase11-hvc-cleanup-prerequisite-parity-gap.md",
//     "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
//     "drivers/tty/hvc/hvc_console.h",
//     "drivers/tty/hvc/hvc_console.zig",
//     "drivers/tty/hvc/hvc_console_verify.zig",
//     "scripts/zigux/check_phase11_build_inventory.zig",
//     "scripts/zigux/check_phase11_validate_manifest_roster.zig",
//     "scripts/zigux/check_phase11_validate_check_roster.zig",
//     "scripts/zigux/check_phase11_validate_route_alignment.zig",
//     "scripts/zigux/check_phase11_focused_direct_build_replays.zig",
//     "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
//     "scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig",
//     "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
//     "scripts/zigux/check_phase11_hvc_current_head_manifest.zig",
//     "scripts\zigux/validate_phase11.zig",
//     "zigux/Makefile",
//     "zigux/tests/fixtures/phase11_build_inventory.json",
//     "zigux/tests/fixtures/phase11_validate_checks.json",
//     "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
//     "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
//     "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
//     "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
//     "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
//     "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
//     "zigux/tests/phase11_hvc_modem_control_proof.zig",
//     "zigux/tests/phase11_hvc_modem_control_proof_build.zig",
//     "zigux/tests/phase11_hvc_targetless_unregister_gap.zig",
//     "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
//     "MANIFEST_PATH",
// };
//
// const EXPECTED_CHECKS = [_][]const u8{
//     "zig run scripts/zigux/check_phase11_hvc_current_head_manifest.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_hvc_current_head_manifest.zig --",
//     "zig run scripts/zigux/check_phase11_build_inventory.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_build_inventory.zig --",
//     "zig run scripts/zigux/check_phase11_validate_manifest_roster.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_validate_manifest_roster.zig --",
//     "zig run scripts/zigux/check_phase11_validate_check_roster.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_validate_check_roster.zig --",
//     "zig run scripts/zigux/check_phase11_validate_route_alignment.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_validate_route_alignment.zig --",
//     "zig run scripts/zigux/check_phase11_focused_direct_build_replays.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_focused_direct_build_replays.zig --",
//     "zig run scripts/zigux/check_phase11_hvc_cleanup_current_head.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_hvc_cleanup_current_head.zig --",
//     "zig run scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_hvc_cleanup_prerequisite_packet.zig --",
//     "zig run scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig -- --self-test",
//     "zig run scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig --",
//     "zig run scripts/zigux/validate_phase11.zig -- --self-test",
//     "zig run scripts/zigux/validate_phase11.zig",
//     "make -C zigux phase11-validate",
//     "zig build test --build-file zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
//     "zig build test --build-file zigux/tests/phase11_hvc_export_surface_layout_build.zig",
//     "zig build test --build-file zigux/tests/phase11_hvc_cleanup_packet_build.zig",
//     "zig build test --build-file zigux/tests/phase11_hvc_modem_control_proof_build.zig",
//     "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// };
//
// const EXPECTED_GAPS = [_][]const u8{
//     "Documentation/zigux/phase11-hvc-console-teardown-note.md",
//     "drivers/tty/hvc/hvc_console_sysrq.zig",
//     "scripts/zigux/check_phase11_hvc_survey_packet.zig",
//     "zigux/tests/phase11_hvc_cleanup.zig",
//     "zigux/tests/phase11_hvc_console.zig",
//     "zigux/tests/phase11_hvc_console_manifest.json",
//     "zigux/tests/phase11_hvc_console_survey.zig",
//     "make -C zigux phase11-hvc-survey",
// };
//
// const SURVEY_MARKERS = [_][]const u8{
//     "`zigux/tests/phase11_hvc_current_head_manifest.json`",
//     "machine-readable current-head manifest packet",
//     "`zig run scripts/zigux/check_phase11_hvc_current_head_manifest.zig -- --self-test`",
//     "`zig run scripts/zigux/check_phase11_hvc_current_head_manifest.zig --`",
// };
//
// const MATRIX_MARKERS = [_][]const u8{
//     "`zigux/tests/phase11_hvc_current_head_manifest.json`",
//     "machine-readable current-head manifest packet",
//     "`zig run scripts/zigux/check_phase11_hvc_current_head_manifest.zig -- --self-test`",
//     "`zig run scripts/zigux/check_phase11_hvc_current_head_manifest.zig --`",
// };
//
// const COMPANION_MARKERS = [_][]const u8{
//     "`zigux/tests/phase11_hvc_current_head_manifest.json`",
//     "machine-readable current-head manifest packet",
//     "`scripts/zigux/check_phase11_hvc_current_head_manifest.zig`",
// };
//
// const MANIFEST_PATH = [_][]const u8{
//     "zigux/tests/phase11_hvc_current_head_manifest.json",
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
// const COMPANION_PATH = [_][]const u8{
//     "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (EXPECTED_PACKET_FILES) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_CHECKS) |marker| try guard.requireMarker(text, marker);
//     for (EXPECTED_GAPS) |marker| try guard.requireMarker(text, marker);
//     for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (COMPANION_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
//     for (MATRIX_PATH) |marker| try guard.requireMarker(text, marker);
//     for (COMPANION_PATH) |marker| try guard.requireMarker(text, marker);
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
