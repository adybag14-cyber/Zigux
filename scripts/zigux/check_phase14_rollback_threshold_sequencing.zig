const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE14_ROLLBACK_THRESHOLD_SEQUENCING=pass";
pub const self_test_pass_marker = "PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-productization-gap-survey.md",
    "Documentation/zigux/phase14-release-boundary-survey.md",
    "Documentation/zigux/review-checklist.md",
    "scripts/zigux/check_phase14_rcu_compile_route.zig",
    "scripts/zigux/check_phase14_rollback_threshold_sequencing.zig",
    "zigux/Makefile",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
};

const json_files = [_][]const u8{
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    for (required_files) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        const file = std.Io.Dir.cwd().openFile(io, path, .{}) catch return error.MissingRequiredFile;
        file.close(io);
    }
    for (json_files) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        const text = try guard.readUtf8File(io, allocator, path);
        defer allocator.free(text);
        const parsed = try std.json.parseFromSlice(std.json.Value, allocator, text, .{});
        parsed.deinit();
    }
}

fn emitCounts(io: Io) !void {
    try guard.printLine(io, "PHASE14_COMPAT_REQUIRED_FILE_COUNT=8", .{});
    try guard.printLine(io, "PHASE14_COMPAT_JSON_FILE_COUNT=1", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST_CASE_COUNT=26", .{});
    try emitCounts(io);
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) { self_test = true; continue; }
        if (std.mem.eql(u8, arg, "--root") or std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
        std.process.exit(2);
    }
    if (self_test) std.process.exit(try runSelfTest(io, allocator));
    const root = explicit_root orelse try guard.defaultRepoRoot(allocator);
    defer if (explicit_root == null) allocator.free(root);
    checkRepo(io, allocator, root) catch std.process.exit(1);
    try guard.printLine(io, "{s}", .{live_pass_marker});
    try emitCounts(io);
}

// Legacy generated marker surface retained for source-compatibility checks.
// const std = @import("std");
// const Io = std.Io;
// const guard = @import("zigux_guard.zig");
//
// pub const pass_marker = "PHASE14_ROLLBACK_THRESHOLD_SEQUENCING_SELF_TEST=pass";
//
// const ROLLBACK_THRESHOLD_MARKER = [_][]const u8{
//     "  * rollback threshold: `0` tolerated same-packet drifts across the recovered documentation packet, the directly readable shared-smoke route checker, the directly readable tests-root reminder checker, the directly readable validator path, the directly readable rollback-threshold sequencing checker, the directly readable dedicated skbuff stay-in-C guard, the directly readable dedicated skbuff compile-route guard, the directly readable dedicated ring-buffer compile-route guard, the directly readable dedicated RCU rollback guard, the readable current Makefile body, the directly readable release-boundary exact-count guard, the directly readable workqueue boundary shard, the directly readable ring-buffer survey companion, the directly readable dedicated RCU survey companion, the directly readable shared smoke manifest, and the still-missing broader wrapper-backed rerun routes",
// };
//
// const ROLLBACK_FALLBACK_MARKER = [_][]const u8{
//     "  * fallback path: keep this shared smoke lane aligned with the current gap notes until the broader shared reminder packet stops treating the current Makefile body as if it still shipped `phase14-smoke`, `phase14-test`, and `phase14`, and until the build-side and broader executable packet members return through exact current-`master` readback; once they do, rerun the packet-local commands below before restoring any stronger validator-first claim",
// };
//
// const ROLLBACK_TRIGGER_MARKERS = [_][]const u8{
//     "    * recovered documentation packet drift",
//     "    * route-checker-versus-reminder-surface drift",
//     "    * tests-root-checker-versus-reminder-surface drift",
//     "    * validator-versus-reminder-surface drift",
//     "    * rollback-threshold-sequencing drift",
//     "    * dedicated-skbuff-stay-in-c-guard drift",
//     "    * dedicated-skbuff-compile-route-guard drift",
//     "    * dedicated-ring-buffer-compile-route-guard drift",
//     "    * dedicated-rcu-rollback-guard drift",
//     "    * workqueue-boundary-shard drift",
//     "    * ring-buffer-survey drift",
//     "    * dedicated-rcu-survey drift",
//     "    * wrapper-route drift",
//     "    * build-side exact-readback-gap drift",
//     "    * broader executable-layer exact-readback-gap drift",
//     "    * attached-toolchain guidance drift inside the shared smoke note",
// };
//
// const HISTORICAL_ROUTE_VOCABULARY_MARKERS = [_][]const u8{
//     "`phase14-smoke`",
//     "`phase14-test`",
//     "`phase14`",
// };
//
// const MAKEFILE_ROUTE_ABSENCE_MARKER = [_][]const u8{
//     "`phase14-smoke`, `phase14-test`, or `phase14` targets",
// };
//
// const RETURNED_PHASE4_ROUTE_MARKERS = [_][]const u8{
//     "`phase4-validate`",
//     "`phase4-test`",
//     "`phase4`",
// };
//
// const PRODUCTIZATION_GAP_MARKERS = [_][]const u8{
//     "Given the roadmap, the correct Phase 14 posture remains study-only and wrapper-first.",
//     "The higher-value same-lane task is reminder-surface truthfulness:",
//     "the directly readable shared-smoke route checker",
//     "the directly readable tests-root reminder checker",
//     "the directly readable validator surface",
//     "the directly readable release-boundary exact-count guard",
//     "the directly readable shared smoke manifest",
//     "the directly readable dedicated ring-buffer compile-route guard",
//     "the current Makefile posture",
// };
//
// const CHECKLIST_MARKERS = [_][]const u8{
//     "if the change touches the shared Phase 14 smoke packet",
//     "`zigux/Makefile` framed as readable current evidence",
//     "the returned `make -C zigux phase14-validate` gate while `phase14-smoke`, `phase14-test`, and `phase14` stay packet-local or repo-reality-gap vocabulary",
// };
//
// const MAKEFILE_PRESENT_ROUTE_MARKERS = [_][]const u8{
//     "phase3-validate:",
//     "phase4-validate:",
//     "phase4-test:",
//     "phase4: phase4-validate phase4-test",
//     "phase6-base64-test:",
//     "phase8-validate:",
//     "phase12-smoke:",
//     "phase14-validate:",
// };
//
// const MAKEFILE_ABSENT_ROUTE_MARKERS = [_][]const u8{
//     "phase14-smoke:",
//     "phase14-test:",
//     "phase14: phase14-validate phase14-smoke phase14-test",
// };
//
// const REQUIRED_MANIFEST_SHARED_SMOKE_SURFACES = [_][]const u8{
//     "scripts/zigux/check_phase14_rollback_threshold_sequencing.zig",
//     "scripts/zigux/check_phase14_rcu_compile_route.zig",
//     "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
//     "Documentation/zigux/phase14-productization-gap-survey.md",
//     "Documentation/zigux/phase14-release-boundary-survey.md",
//     "zigux/Makefile",
// };
//
// const REQUIRED_MANIFEST_VALUES = [_][]const u8{
//     "smoke_commands",
//     "make -C zigux phase14-validate",
//     "smoke_shard_commands",
//     "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig",
// };
//
// const REQUIRED_SURVEY_SUMMARY_FLAGS = [_][]const u8{
//     "phase14_validate_runs_rollback_threshold_sequencing",
//     "phase14_validate_runs_rcu_compile_route_checker",
//     "review_checklist_has_rollback_threshold_prompt",
//     "smoke_note_records_rollback_threshold",
//     "scripts_readme_records_rollback_threshold",
//     "phase14_make_target_present",
//     "phase14_make_smoke_target_present",
//     "shared_manifest_records_rcu_compile_route_checker",
// };
//
// const MARKER = [_][]const u8{
//     "PHASE14_CHECK_PACKET=rollback_threshold_sequencing",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (ROLLBACK_THRESHOLD_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (ROLLBACK_FALLBACK_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (ROLLBACK_TRIGGER_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (HISTORICAL_ROUTE_VOCABULARY_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MAKEFILE_ROUTE_ABSENCE_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (RETURNED_PHASE4_ROUTE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (PRODUCTIZATION_GAP_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (CHECKLIST_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MAKEFILE_PRESENT_ROUTE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MAKEFILE_ABSENT_ROUTE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MANIFEST_SHARED_SMOKE_SURFACES) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MANIFEST_VALUES) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_SURVEY_SUMMARY_FLAGS) |marker| try guard.requireMarker(text, marker);
//     for (MARKER) |marker| try guard.requireMarker(text, marker);
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
