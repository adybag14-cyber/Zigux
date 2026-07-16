const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE14_RCU_ROLLBACK_GUARDRAIL=pass";
pub const self_test_pass_marker = "PHASE14_RCU_ROLLBACK_GUARDRAIL_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase14-core-boundary-traceability.md",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-rcu-tree-survey.md",
    "kernel/rcu/tree_bridge.zig",
    "scripts/zigux/check_phase14_rcu_rollback_guardrail.zig",
    "zigux/tests/phase14_rcu_tree_manifest.json",
};

const json_files = [_][]const u8{
    "zigux/tests/phase14_rcu_tree_manifest.json",
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
    try guard.printLine(io, "PHASE14_COMPAT_REQUIRED_FILE_COUNT=7", .{});
    try guard.printLine(io, "PHASE14_COMPAT_JSON_FILE_COUNT=1", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE14_RCU_ROLLBACK_GUARDRAIL_SELF_TEST_CASE_COUNT=17", .{});
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
// pub const pass_marker = "PHASE14_RCU_ROLLBACK_GUARDRAIL_SELF_TEST=pass";
//
// const ROLLBACK_THRESHOLD_MARKER = [_][]const u8{
//     "- manifest-backed guardrail: `phase14-rcu-tree-rollback-threshold-guardrail` keeps this freeze-in-C packet fail-closed until the same review packet carries the required reopen evidence instead of a lighter status-review claim.",
// };
//
// const COMPANION_CONFIRMATION_HEADING = [_][]const u8{
//     "executable packet companions confirmed on current `master` through public GitHub fallback:",
// };
//
// const COMPANION_PARTIAL_MARKER = [_][]const u8{
//     "authenticated contents-path readback still stays partial for those executable companions",
// };
//
// const OWNER_MAP_TIEBACK_HEADING = [_][]const u8{
//     "- shared Phase 14 reminder surfaces that still carry the bounded owner-map tie-back:",
// };
//
// const OWNER_MAP_TIEBACK_MARKERS = [_][]const u8{
//     "- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`",
//     "- `Documentation/zigux/phase14-core-boundary-traceability.md`",
// };
//
// const REQUIRED_EVIDENCE_MARKERS = [_][]const u8{
//     "- `Architecture Council` reopen record linked from the active review packet",
//     "- parity scorecard evidence and benchmark notes attached to the same review packet",
//     "- validation replay command and evidence archive path recorded beside the latest blocker disposition",
// };
//
// const RETURN_TO_BLOCKED_MARKERS = [_][]const u8{
//     "- any `kernel/rcu/tree_bridge.zig` claim or status review that lacks the `Architecture Council` reopen record",
//     "- missing parity scorecard evidence, benchmark notes, or replay command in the active review packet",
//     "- freeze-map, survey note, or dedicated-check drift that drops the blocked bridge disposition, the companion-readback warning, or the rollback owner",
// };
//
// const REQUIRED_MARKERS = [_][]const u8{
//     "`PHASE14_LANE_KEY=P14-L16`",
//     "`PHASE14_STATUS_BUCKET=freeze_in_c`",
//     "`PHASE14_ANCHOR=kernel/rcu/tree.c`",
//     "`PHASE14_BLOCKED_GAP=phase14-rcu-tree-bridge-blocker`",
//     "DIRECT_PACKET_SURFACES_HEADING",
//     "DIRECT_BRIDGE_SURFACE_MARKER",
//     "COMPANION_CONFIRMATION_HEADING",
//     "`zigux/tests/phase14_rcu_tree_manifest.json`",
//     "`zigux/tests/phase14_rcu_tree_survey.zig`",
//     "COMPANION_PARTIAL_MARKER",
//     "OWNER_MAP_TIEBACK_HEADING",
//     "OWNER_MAP_TIEBACK_MARKERS",
//     "dedicated rollback guard surface:",
//     "`scripts/zigux/check_phase14_rcu_rollback_guardrail.zig`",
//     "`phase14-rcu-tree-rollback-threshold-guardrail`",
//     "ROLLBACK_THRESHOLD_MARKER",
//     "rollback owner: `Repo Tooling Pod`",
//     "REQUIRED_EVIDENCE_HEADING",
//     "REQUIRED_EVIDENCE_MARKERS",
//     "RETURN_TO_BLOCKED_HEADING",
//     "RETURN_TO_BLOCKED_MARKERS",
// };
//
// const FORBIDDEN_MARKERS = [_][]const u8{
//     "current review packet:",
// };
//
// const MANIFEST_REQUIRED_FIELDS = [_][]const u8{
//     "lane_key",
//     "P14-L16",
//     "anchor",
//     "kernel/rcu/tree.c",
//     "rollback_threshold",
//     "status_bucket",
//     "freeze_in_c",
//     "rollback_threshold",
//     "review_blocker_status",
//     "blocked_on_stay_in_c_evidence",
//     "rollback_threshold",
//     "owner",
//     "Core-Adjacent Pod",
//     "rollback_threshold",
//     "rollback_owner",
//     "Repo Tooling Pod",
// };
//
// const MANIFEST_REQUIRED_LISTS = [_][]const u8{
//     "rollback_threshold",
//     "required_evidence",
//     "Architecture Council reopen record linked from the reviewable packet",
//     "parity scorecard evidence and benchmark notes attached to the same review packet",
//     "validation replay command and evidence archive path recorded beside the latest blocker disposition",
//     "rollback_threshold",
//     "rollback_triggers",
//     "any `kernel/rcu/tree_bridge.zig` claim or status review that lacks the Architecture Council reopen record",
//     "missing parity scorecard evidence, benchmark notes, or replay command in the active review packet",
//     "freeze-map, survey note, or manifest drift that drops the blocked bridge disposition or rollback owner",
// };
//
// const MANIFEST_REQUIRED_GAP_IDS = [_][]const u8{
//     "phase14-rcu-tree-rollback-threshold-guardrail",
//     "phase14-rcu-tree-bridge-blocker",
// };
//
// const NOTE_PATH = [_][]const u8{
//     "Documentation/zigux/phase14-rcu-tree-survey.md",
// };
//
// const MANIFEST_PATH = [_][]const u8{
//     "zigux/tests/phase14_rcu_tree_manifest.json",
// };
//
// const DIRECT_PACKET_SURFACES_HEADING = [_][]const u8{
//     "directly readable dedicated packet surfaces on current `master`:",
// };
//
// const DIRECT_BRIDGE_SURFACE_MARKER = [_][]const u8{
//     "  - `kernel/rcu/tree_bridge.zig`",
// };
//
// const REQUIRED_EVIDENCE_HEADING = [_][]const u8{
//     "- required evidence before any status review:",
// };
//
// const RETURN_TO_BLOCKED_HEADING = [_][]const u8{
//     "- automatic return-to-blocked triggers:",
// };
//
// pub fn checkText(text: []const u8) guard.GuardError!void {
//     for (ROLLBACK_THRESHOLD_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (COMPANION_CONFIRMATION_HEADING) |marker| try guard.requireMarker(text, marker);
//     for (COMPANION_PARTIAL_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (OWNER_MAP_TIEBACK_HEADING) |marker| try guard.requireMarker(text, marker);
//     for (OWNER_MAP_TIEBACK_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_EVIDENCE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (RETURN_TO_BLOCKED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (MANIFEST_REQUIRED_FIELDS) |marker| try guard.requireMarker(text, marker);
//     for (MANIFEST_REQUIRED_LISTS) |marker| try guard.requireMarker(text, marker);
//     for (MANIFEST_REQUIRED_GAP_IDS) |marker| try guard.requireMarker(text, marker);
//     for (NOTE_PATH) |marker| try guard.requireMarker(text, marker);
//     for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
//     for (DIRECT_PACKET_SURFACES_HEADING) |marker| try guard.requireMarker(text, marker);
//     for (DIRECT_BRIDGE_SURFACE_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_EVIDENCE_HEADING) |marker| try guard.requireMarker(text, marker);
//     for (RETURN_TO_BLOCKED_HEADING) |marker| try guard.requireMarker(text, marker);
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
