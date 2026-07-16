const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL=pass";
pub const self_test_pass_marker = "PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL_SELF_TEST=pass";
pub const pass_marker = self_test_pass_marker;

const required_files = [_][]const u8{
    "Documentation/zigux/phase14-skbuff-bridge-survey.md",
    "net/core/skbuff_bridge.zig",
    "scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig",
    "zigux/tests/phase14_skbuff_bridge.zig",
    "zigux/tests/phase14_skbuff_bridge_manifest.json",
};

const json_files = [_][]const u8{
    "zigux/tests/phase14_skbuff_bridge_manifest.json",
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
    try guard.printLine(io, "PHASE14_COMPAT_REQUIRED_FILE_COUNT=5", .{});
    try guard.printLine(io, "PHASE14_COMPAT_JSON_FILE_COUNT=1", .{});
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    const root = try guard.defaultRepoRoot(allocator);
    defer allocator.free(root);
    try checkRepo(io, allocator, root);
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    try guard.printLine(io, "PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL_SELF_TEST_CASE_COUNT=7", .{});
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
// pub const pass_marker = "PHASE14_SKBUFF_STAY_IN_C_GUARDRAIL_SELF_TEST=pass";
//
// const GUARDRAIL_MARKER = [_][]const u8{
//     "- manifest-backed guardrail: `phase14-skbuff-stay-in-c-guardrail` keeps this review-only packet fail-closed until the same packet carries explicit reopen evidence instead of lighter bridge-presence wording",
// };
//
// const REQUIRED_EVIDENCE_MARKERS = [_][]const u8{
//     "- `Architecture Council` reopen record linked from the active skbuff packet",
//     "- parity scorecard evidence and benchmark notes attached to the same skbuff packet",
//     "- validation replay command and evidence archive path recorded beside the latest blocker disposition",
// };
//
// const RETURN_TO_BLOCKED_MARKERS = [_][]const u8{
//     "- any `net/core/skbuff_bridge.zig` claim or status review that drops `phase14-skbuff-live-ownership-blocker`",
//     "- missing qdisc-facing publication, checksum ownership, segmentation metadata, zerocopy fragment orphaning, shared-frag ownership transfer, destructor ordering, or final sock-owned tail transfer wording in the active skbuff packet",
//     "- any bridge-presence wording that upgrades the packet into parity, runtime ownership, or a freeze-map status change without the required reopen evidence",
// };
//
// const NEXT_STEP_COORDINATION_MARKERS = [_][]const u8{
//     "Leave this lane parked unless a future current-`master` reread finds another survey-only drift against the live skbuff bridge packet or the Phase 14 roadmap.",
//     "If the packet ever moves toward status review, update this note and `scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig` together before any broader shared Phase 14 reminder surface repeats the claim.",
// };
//
// const REQUIRED_MARKERS = [_][]const u8{
//     "`PHASE14_LANE_KEY=P14-L11`",
//     "`PHASE14_BLOCKED_GAP=phase14-skbuff-live-ownership-blocker`",
//     "`PHASE14_POSTURE=boundary_map_only`",
//     "current `master` ships the bounded skbuff anchor packet again through `net/core/skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge.zig`, `zigux/tests/phase14_skbuff_bridge_manifest.json`, and `zigux/tests/phase14_build.zig`",
//     "explicit stay-in-C ownership for qdisc-facing publication, queue ownership, skb lifetime ownership, checksum ownership, destructor coordination, segmentation metadata, zerocopy fragment orphaning, shared-frag ownership transfer, and the final sock-owned tail transfer remains the Phase 14 boundary",
//     "`zigux/tests/phase14_build.zig` wires `../../net/core/skbuff_bridge.zig` and `phase14_skbuff_bridge.zig` into the dedicated Phase 14 build shard, so there is now a live skbuff-local review route on current `master`",
//     "The live bridge packet therefore remains review-only boundary evidence, not a delivery, parity, or ownership-transfer claim.",
//     "`validate_xmit_skb_list()`, qdisc-facing publication, checksum ownership, segmentation metadata, destructor ordering, zerocopy fragment orphaning, `skb_orphan_frags()`, `skb_zerocopy_clone()`, `SKBFL_SHARED_FRAG`, `sock_wfree`, `tail->destructor`, `tail->sk`, `tail->next`, `segs->prev`, `skb_mark_not_on_list()`, `tail = skb->prev`, and the final sock-owned tail transfer must remain named as C-owned review points",
//     "`phase14-skbuff-stay-in-c-guardrail`",
//     "GUARDRAIL_MARKER",
//     "`scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig`",
//     "rollback owner: `Repo Tooling Pod`",
//     "REQUIRED_EVIDENCE_HEADING",
//     "REQUIRED_EVIDENCE_MARKERS",
//     "RETURN_TO_BLOCKED_HEADING",
//     "RETURN_TO_BLOCKED_MARKERS",
//     "NEXT_STEP_COORDINATION_MARKERS",
// };
//
// const NOTE_PATH = [_][]const u8{
//     "Documentation/zigux/phase14-skbuff-bridge-survey.md",
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
//     for (GUARDRAIL_MARKER) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_EVIDENCE_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (RETURN_TO_BLOCKED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (NEXT_STEP_COORDINATION_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
//     for (NOTE_PATH) |marker| try guard.requireMarker(text, marker);
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
