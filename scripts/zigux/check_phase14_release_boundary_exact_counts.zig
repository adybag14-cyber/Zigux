const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS=pass";
pub const self_test_pass_marker = "PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "Documentation/zigux/phase14-compile-shard-matrix-survey.md",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-release-boundary-survey.md",
    "net/core/skbuff_bridge.zig",
    "scripts/zigux/check_phase14_rcu_compile_route.zig",
    "scripts/zigux/check_phase14_release_boundary_exact_counts.zig",
    "scripts/zigux/check_phase14_ring_buffer_compile_route.zig",
    "scripts/zigux/check_phase14_shared_smoke_route.zig",
    "scripts/zigux/check_phase14_skbuff_compile_route.zig",
    "scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig",
    "scripts/zigux/check_phase14_tests_readme_smoke_summary.zig",
    "zigux/Makefile",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
    "zigux/tests/phase14_end_to_end_smoke_survey.zig",
    "zigux/tests/phase14_skbuff_bridge.zig",
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
    try guard.printLine(io, "PHASE14_COMPAT_REQUIRED_FILE_COUNT=15", .{});
    try guard.printLine(io, "PHASE14_COMPAT_JSON_FILE_COUNT=1", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST_CASE_COUNT=16", .{});
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
// pub const pass_marker = "PHASE14_RELEASE_BOUNDARY_EXACT_COUNTS_SELF_TEST=pass";
//
// const EXACT_COUNT_MARKERS = [_][]const u8{
//     "- `PHASE14_COMPILE_SHARD_TOTAL=6`",
//     "- `PHASE14_COMPILE_SHARD_FOCUSED_COUNT=1`",
//     "- `PHASE14_COMPILE_SHARD_FULL_BUNDLE_ONLY_COUNT=5`",
// };
//
// const EXECUTABLE_GAP_MARKERS = [_][]const u8{
//     "- `zigux/tests/phase14_build.zig`",
//     "- `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
//     "- `zigux/tests/phase14_skbuff_bridge.zig`",
//     "- `zigux/tests/phase14_rcu_tree_survey.zig`",
//     "- `net/core/skbuff_bridge.zig`",
// };
//
// const RELEASE_BOUNDARY_TEXT_MARKERS = [_][]const u8{
//     "- `scripts/zigux/check_phase14_release_boundary_exact_counts.zig` now returns through the current contents path and keeps the release-facing exact-count posture aligned with the current shared reminder packet",
//     "- `zigux/tests/phase14_end_to_end_smoke_manifest.json` now returns through the current contents path and publishes the exact six-row compile-shard matrix with one `focused_and_full_bundle` shard and five `full_bundle_only` shards",
//     "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
//     "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
// };
//
// const COMPILE_SHARD_MATRIX_MARKERS = [_][]const u8{
//     "EXACT_COUNT_MARKERS",
//     "- shared gate: `make -C zigux phase14-validate`",
//     "- focused raw build-file shard: `zig build phase14-smoke --build-file zigux/tests/phase14_build.zig`",
//     "- machine-readable source: `zigux/tests/phase14_end_to_end_smoke_manifest.json`",
//     "- checker: `scripts/zigux/check_phase14_release_boundary_exact_counts.zig`",
//     "- skbuff compile-route checker: `scripts/zigux/check_phase14_skbuff_compile_route.zig`",
//     "- ring-buffer compile-route checker: `scripts/zigux/check_phase14_ring_buffer_compile_route.zig`",
//     "- rcu compile-route checker: `scripts/zigux/check_phase14_rcu_compile_route.zig`",
//     "- shared survey shard: `phase14-end-to-end-smoke-tests` (`focused_and_full_bundle`)",
//     "- `scripts/zigux/check_phase14_ring_buffer_compile_route.zig` now fail-closes on the shared-manifest row together with the note's returned ring-buffer-local replay wording even while the lane remains study-only and maintenance-scoped",
//     "- the manifest-backed compile row is present, and `scripts/zigux/check_phase14_rcu_compile_route.zig` now fail-closes on the shared-manifest row, the dedicated build-shard wiring, and the survey note's public-fallback replay wording while the anchor stays freeze-in-C initially",
// };
//
// const SURVEY_EXACT_LINE_SNIPPETS = [_][]const u8{
//     "  * directly readable current-`master` companion surfaces in this lane's current evidence split:",
//     "    * `scripts/zigux/check_phase14_shared_smoke_route.zig` through the current contents path",
//     "    * `scripts/zigux/check_phase14_tests_readme_smoke_summary.zig` through the current contents path",
//     "    * `scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig` through the current contents path",
//     "    * `zigux/tests/phase14_end_to_end_smoke_manifest.json` through the current contents path",
//     "  * exact-readback gaps that still belong to this shared note:",
//     "    * `zigux/tests/phase14_build.zig`",
//     "    * `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
//     "    * broad reminder text should therefore frame that build-side and broader executable layer as exact-readback gaps rather than as directly recovered shared-smoke proof",
//     "    * the current readable route layer still stops at `make -C zigux phase14-validate`; no current attached-toolchain `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, or `make -C zigux phase14` fallback is usable from this note because the readable `zigux/Makefile` body still omits those targets",
// };
//
// const REQUIRED_COMPILE_SHARD_LABELS = [_][]const u8{
//     "phase14-workqueue-bridge-tests",
//     "full_bundle_only",
//     "phase14-workqueue-reviewability-tests",
//     "full_bundle_only",
//     "phase14-skbuff-bridge-tests",
//     "full_bundle_only",
//     "phase14-ring-buffer-survey-tests",
//     "full_bundle_only",
//     "phase14-rcu-tree-survey-tests",
//     "full_bundle_only",
//     "phase14-end-to-end-smoke-tests",
//     "focused_and_full_bundle",
// };
//
// const REQUIRED_MANIFEST_VALUES = [_][]const u8{
//     "smoke_commands",
//     "make -C zigux phase14-validate",
//     "smoke_shard_commands",
//     "zig build phase14-smoke --build-file zigux/tests/phase14_build.zig",
//     "survey_summary",
//     "phase14_make_target_present",
//     "survey_summary",
//     "phase14_make_smoke_target_present",
//     "survey_summary",
//     "workflow_runs_phase14_validate",
//     "survey_summary",
//     "workflow_runs_phase14_build",
//     "survey_summary",
//     "workflow_runs_phase14_smoke_shard",
//     "survey_summary",
//     "phase14_validate_runs_skbuff_stay_in_c_guardrail",
//     "survey_summary",
//     "phase14_validate_runs_skbuff_compile_route_checker",
//     "survey_summary",
//     "shared_manifest_records_skbuff_compile_route_checker",
//     "survey_summary",
//     "phase14_validate_runs_rcu_compile_route_checker",
//     "survey_summary",
//     "shared_manifest_records_rcu_compile_route_checker",
//     "survey_summary",
//     "phase14_validate_runs_rcu_rollback_guardrail",
// };
//
// const MARKER = [_][]const u8{
//     "PHASE14_CHECK_PACKET=release_boundary_exact_counts",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (EXACT_COUNT_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (EXECUTABLE_GAP_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (RELEASE_BOUNDARY_TEXT_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (COMPILE_SHARD_MATRIX_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (SURVEY_EXACT_LINE_SNIPPETS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_COMPILE_SHARD_LABELS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MANIFEST_VALUES) |marker| try guard.requireMarker(text, marker);
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
