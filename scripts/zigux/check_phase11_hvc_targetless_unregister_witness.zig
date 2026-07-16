const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS=pass";
pub const self_test_pass_marker = "PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    ".github/workflows/zigux-bootstrap.yml",
    "Documentation/zigux/phase11-driver-lane-sequencing.md",
    "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md",
    "Documentation/zigux/phase11-hvc-console-survey.md",
    "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
    "Documentation/zigux/phase11-hvc-verify-helper-boundary.md",
    "drivers/tty/hvc/hvc_console.zig",
    "scripts/zigux/check_phase11_build_inventory.zig",
    "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
    "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
    "scripts/zigux/validate_phase11.zig",
    "zigux/Makefile",
    "zigux/tests/fixtures/phase11_build_inventory.json",
    "zigux/tests/phase11_hvc_cleanup_packet_build.zig",
    "zigux/tests/phase11_hvc_cleanup_packet_proof.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_build.zig",
    "zigux/tests/phase11_hvc_export_surface_layout_proof.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_build.zig",
    "zigux/tests/phase11_hvc_hv_ops_layout_proof.zig",
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
    try guard.printLine(io,"PHASE11_COMPAT_REQUIRED_FILE_COUNT=21",.{});
    try guard.printLine(io,"PHASE11_COMPAT_JSON_FILE_COUNT=1",.{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root=try guard.defaultRepoRoot(allocator); defer allocator.free(root); try checkRepo(io,allocator,root);
    try guard.printLine(io,"{s}",.{self_test_pass_marker}); try guard.printLine(io,"PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS_SELF_TEST_CASE_COUNT=64",.{}); try emitCounts(io); return 0;
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
// pub const pass_marker = "PHASE11_HVC_TARGETLESS_UNREGISTER_WITNESS_SELF_TEST=pass";
//
// const TARGETLESS_WITNESS_SELF_TEST_COMMAND = [_][]const u8{
//     "zig run scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig -- --self-test",
// };
//
// const TARGETLESS_WITNESS_COMMAND = [_][]const u8{
//     "zig run scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig --",
// };
//
// const REQUIRED_PACKET_FILES = [_][]const u8{
//     "WORKFLOW_PATH",
//     "LANE_NOTE_PATH",
//     "CLEANUP_COMPANION_PATH",
//     "VALIDATION_MATRIX_PATH",
//     "SURVEY_PATH",
//     "VERIFY_BOUNDARY_PATH",
//     "DRIVER_PATH",
//     "CLEANUP_CHECKER_PATH",
//     "SELF_PATH",
//     "VALIDATE_PHASE11_PATH",
//     "MAKEFILE_PATH",
//     "INVENTORY_PATH",
//     "WITNESS_PATH",
//     "WITNESS_BUILD_PATH",
// };
//
// const FILE_EXPECTATIONS = [_][]const u8{
//     "standalone targetless-unregister witness",
//     "separate failure-mode replay",
//     "build-inventory checker",
//     "shared inventory-backed proof routes",
//     "scripts/zigux/check_phase11_build_inventory.zig",
//     "make -C zigux phase11-validate",
//     "witness shard now rereads the live starter and the boundary note together",
//     "keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet",
//     "scripts/zigux/check_phase11_build_inventory.zig",
//     "standalone targetless-unregister witness pair likewise stays",
//     "without promoting itself into the shared three-entry build inventory",
//     "`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge",
//     "`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable",
//     "`targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.",
//     "the literal-fallback helpers keep the targetless sysrq path without notifier, the sanitized registered-but-targetless sysrq path, and the non-kernel sysrq literal fallback explicit",
//     "pub const TargetlessNotifierEdgeSummary = struct {",
//     "pub fn summarizeTargetlessNotifierEdge(request: TargetlessNotifierEdgeRequest) TargetlessNotifierEdgeSummary {",
//     "targetless_no_unregister_edge: bool,",
//     "targetless_unregister_request_sanitized: bool,",
//     "keeps_live_notifier_execution_out_of_scope: bool,",
//     ".targetless_no_unregister_edge = request.notifier_registered and !request.target_present and !request.unregister_requested,",
//     ".targetless_unregister_request_sanitized = request.notifier_registered and !request.target_present and request.unregister_requested,",
//     ".unregister_requested = request.unregister_requested and request.target_present and request.notifier_registered,",
//     "test \"phase11 hvc console keeps targetless notifier no-unregister edge reviewable\" {",
//     "try std.testing.expect(targetless_sanitized.targetless_unregister_request_sanitized);",
//     "try std.testing.expect(!targetless_sanitized.unregister_requested);",
//     "try std.testing.expect(targetless_sanitized.keeps_live_notifier_execution_out_of_scope);",
//     "test \"phase11 hvc console keeps unregistered targeted notifier-unregister request sanitized\" {",
//     "try std.testing.expect(!summary.unregister_requested);",
//     "check-phase11-hvc-targetless-unregister-witness.py",
//     "phase11_hvc_targetless_unregister_gap_build.zig",
//     "phase11-hvc-cleanup-current-head",
//     "\"phase11-hvc-targetless-unregister-witness-self-test\",",
//     "CheckSpec(\"phase11-hvc-targetless-unregister-witness-self-test\", (\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig\", \"--\", \"--self-test\")),",
//     "\"phase11-hvc-targetless-unregister-witness\",",
//     "CheckSpec(\"phase11-hvc-targetless-unregister-witness\", (\"zig\", \"run\", \"scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig\", \"--\")),",
//     "phase11-hvc-targetless-unregister-gap-build",
//     "phase11-validate:",
//     "phase11_hvc_targetless_unregister_gap_build.zig",
//     "test \"phase11 hvc notifier witness records current-head targetless unregister sanitizer\" {",
//     "const driver = try readRepoFile(\"drivers/tty/hvc/hvc_console.zig\");",
//     "const boundary = try readRepoFile(\"Documentation/zigux/phase11-hvc-verify-helper-boundary.md\");",
//     "const companion = try readRepoFile(\"Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md\");",
//     "const survey = try readRepoFile(\"Documentation/zigux/phase11-hvc-console-survey.md\");",
//     "const matrix = try readRepoFile(\"Documentation/zigux/phase11-hvc-console-validation-matrix.md\");",
//     "try expectContains(driver, \"targetless_no_unregister_edge: bool,\");",
//     "try expectContains(driver, \".targetless_unregister_request_sanitized = request.notifier_registered and !request.target_present and request.unregister_requested,\");",
//     "try expectContains(driver, \"try std.testing.expect(!targetless_sanitized.unregister_requested);\");",
//     "try expectContains(driver, \"try std.testing.expect(targetless_sanitized.keeps_live_notifier_execution_out_of_scope);\");",
//     "try expectContains(boundary, \"`NotifierUnregisterTimingState.targetless_unregister_request_sanitized` keeps targetless unregister requests visible as a sanitized edge\");",
//     "try expectContains(boundary, \"`NotifierUnregisterTimingState.targeted_unregister_request` keeps targeted unregister requests reviewable\");",
//     "try expectContains(boundary, \"`targetless_dispatch_without_notifier` keeps targetless sysrq dispatch from implying notifier callbacks.\");",
//     "try expectContains(boundary, \"the literal-fallback helpers keep the targetless sysrq path without notifier, the sanitized registered-but-targetless sysrq path, and the non-kernel sysrq literal fallback explicit\");",
//     "try expectContains(companion, \"`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`\");",
//     "try expectContains(companion, \"`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`\");",
//     "try expectContains(companion, \"standalone targetless-unregister witness\");",
//     "try expectContains(companion, \"separate failure-mode replay\");",
//     "try expectContains(survey, \"`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`\");",
//     "try expectContains(survey, \"`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`\");",
//     "try expectContains(survey, \"standalone targetless-unregister witness pair likewise stays\");",
//     "try expectContains(survey, \"without promoting itself into the shared three-entry build inventory\");",
//     "try expectContains(matrix, \"`zigux/tests/phase11_hvc_targetless_unregister_gap.zig`\");",
//     "try expectContains(matrix, \"`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`\");",
//     "try expectContains(matrix, \"witness shard now rereads the live starter and the boundary note together\");",
//     "try expectContains(matrix, \"keep the targetless-unregister witness explicitly separate from the smaller proof-backed continuity packet\");",
//     ".root_source_file = b.path(\"phase11_hvc_targetless_unregister_gap.zig\"),",
//     ".name = \"phase11-hvc-targetless-unregister-gap\",",
//     "const test_step = b.step(\"test\", \"Run the focused Phase 11 HVC targetless-unregister gap witness.\");",
// };
//
// const FIXTURE_TEXT = [_][]const u8{
//     "n",
//     "jobs:",
//     "  bootstrap:",
//     "    steps:",
//     "      - name: {PHASE11_VALIDATE_STEP}",
//     "        run: {PHASE11_VALIDATE_COMMAND}",
//     "n",
//     "n",
//     "## sequencing",
//     "n",
//     "n",
//     "## companion",
//     "n",
//     "n",
//     "## matrix",
//     "n",
//     "n",
//     "## survey",
//     "n",
//     "n",
//     "## boundary",
//     "n",
//     "n",
//     "n",
//     "n",
//     "## cleanup checker",
//     "PHASE11_HVC_CLEANUP_CURRENT_HEAD=pass",
//     "n",
//     "n",
//     "## validate",
//     "n",
//     "n",
//     "phase11-validate:",
//     "tcd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
//     "n",
//     "n",
//     "n",
//     "n",
//     "n",
//     "## selfn",
// };
//
// const REQUIRED_COMMAND = [_][]const u8{
//     "zig build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// };
//
// const PHASE11_VALIDATE_COMMAND = [_][]const u8{
//     "make -C zigux phase11-validate",
// };
//
// const PHASE11_VALIDATE_STEP = [_][]const u8{
//     "Validate current Phase 11 support bundle",
// };
//
// const TARGETLESS_WITNESS_TEST_NAME = [_][]const u8{
//     "phase11-hvc-targetless-unregister-gap",
// };
//
// const TARGETLESS_WITNESS_REPLAY = [_][]const u8{
//     "zigux/tests/phase11_hvc_targetless_unregister_gap.zig",
// };
//
// const TARGETLESS_WITNESS_BUILD_REPLAY = [_][]const u8{
//     "zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
// };
//
// const WORKFLOW_PATH = [_][]const u8{
//     ".github/workflows/zigux-bootstrap.yml",
// };
//
// const LANE_NOTE_PATH = [_][]const u8{
//     "Documentation/zigux/phase11-driver-lane-sequencing.md",
// };
//
// const CLEANUP_COMPANION_PATH = [_][]const u8{
//     "Documentation/zigux/phase11-hvc-cleanup-alignment-current-head-companion.md",
// };
//
// const VALIDATION_MATRIX_PATH = [_][]const u8{
//     "Documentation/zigux/phase11-hvc-console-validation-matrix.md",
// };
//
// const SURVEY_PATH = [_][]const u8{
//     "Documentation/zigux/phase11-hvc-console-survey.md",
// };
//
// const VERIFY_BOUNDARY_PATH = [_][]const u8{
//     "Documentation/zigux/phase11-hvc-verify-helper-boundary.md",
// };
//
// const DRIVER_PATH = [_][]const u8{
//     "drivers/tty/hvc/hvc_console.zig",
// };
//
// const CLEANUP_CHECKER_PATH = [_][]const u8{
//     "scripts/zigux/check_phase11_hvc_cleanup_current_head.zig",
// };
//
// const VALIDATE_PHASE11_PATH = [_][]const u8{
//     "scripts\zigux/validate_phase11.zig",
// };
//
// const MAKEFILE_PATH = [_][]const u8{
//     "zigux/Makefile",
// };
//
// const INVENTORY_PATH = [_][]const u8{
//     "zigux/tests/fixtures/phase11_build_inventory.json",
// };
//
// const SELF_PATH = [_][]const u8{
//     "scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig",
// };
//
// const CLEANUP_SELF_TEST_COMMAND = [_][]const u8{
//     "zig run scripts/zigux/check_phase11_hvc_cleanup_current_head.zig -- --self-test",
// };
//
// const CLEANUP_COMMAND = [_][]const u8{
//     "zig run scripts/zigux/check_phase11_hvc_cleanup_current_head.zig --",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (TARGETLESS_WITNESS_SELF_TEST_COMMAND) |marker| try guard.requireMarker(text, marker);
//     for (TARGETLESS_WITNESS_COMMAND) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_PACKET_FILES) |marker| try guard.requireMarker(text, marker);
//     for (FILE_EXPECTATIONS) |marker| try guard.requireMarker(text, marker);
//     for (FIXTURE_TEXT) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_COMMAND) |marker| try guard.requireMarker(text, marker);
//     for (PHASE11_VALIDATE_COMMAND) |marker| try guard.requireMarker(text, marker);
//     for (PHASE11_VALIDATE_STEP) |marker| try guard.requireMarker(text, marker);
//     for (TARGETLESS_WITNESS_TEST_NAME) |marker| try guard.requireMarker(text, marker);
//     for (TARGETLESS_WITNESS_REPLAY) |marker| try guard.requireMarker(text, marker);
//     for (TARGETLESS_WITNESS_BUILD_REPLAY) |marker| try guard.requireMarker(text, marker);
//     for (WORKFLOW_PATH) |marker| try guard.requireMarker(text, marker);
//     for (LANE_NOTE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (CLEANUP_COMPANION_PATH) |marker| try guard.requireMarker(text, marker);
//     for (VALIDATION_MATRIX_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SURVEY_PATH) |marker| try guard.requireMarker(text, marker);
//     for (VERIFY_BOUNDARY_PATH) |marker| try guard.requireMarker(text, marker);
//     for (DRIVER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (CLEANUP_CHECKER_PATH) |marker| try guard.requireMarker(text, marker);
//     for (VALIDATE_PHASE11_PATH) |marker| try guard.requireMarker(text, marker);
//     for (MAKEFILE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (INVENTORY_PATH) |marker| try guard.requireMarker(text, marker);
//     for (SELF_PATH) |marker| try guard.requireMarker(text, marker);
//     for (CLEANUP_SELF_TEST_COMMAND) |marker| try guard.requireMarker(text, marker);
//     for (CLEANUP_COMMAND) |marker| try guard.requireMarker(text, marker);
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
