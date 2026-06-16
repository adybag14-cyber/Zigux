const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_PRODUCTIZATION_GAP_ROADMAP_ALIGNMENT_SELF_TEST=pass";

const ROADMAP_MARKERS = [_][]const u8{
    "Phase 14 in `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` is the `Core-Adjacent Bounded Internals` lane.",
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
    "- `net/core/skbuff.c`",
    "- `kernel/rcu/tree.c`",
    "Given the roadmap, the correct Phase 14 posture remains study-only and wrapper-first.",
};

const RETURNED_PACKET_MARKERS = [_][]const u8{
    "- `Documentation/zigux/phase14-release-boundary-survey.md`",
    "- `Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`",
    "- `Documentation/zigux/freeze-map.md`",
    "- `Documentation/zigux/phase15-study-only-anchor-accounting.md`",
    "- `scripts/zigux/check_phase14_shared_smoke_route.zig` through the current contents path",
    "- `scripts/zigux/check_phase14_tests_readme_smoke_summary.zig` through the current contents path",
    "- `scripts/zigux/check_phase14_rollback_threshold_sequencing.zig` through the current contents path",
    "- `scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig` through the current contents path",
    "- `scripts/zigux/check_phase14_rcu_rollback_guardrail.zig` through the current contents path",
    "- `scripts\zigux/validate_phase14.zig` through the current contents path",
    "- `scripts/zigux/check_phase14_release_boundary_exact_counts.zig` through the current contents path",
    "- `zigux/tests/phase14_end_to_end_smoke_manifest.json` through the current contents path",
    "- `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` are directly readable again as the workqueue-local reviewability shard",
    "- `zigux/tests/phase14_ring_buffer_survey.zig` now returns through the current contents path as a directly readable ring-buffer survey companion",
    "- `Documentation/zigux/phase14-rcu-tree-survey.md` is directly readable again through the current contents path",
};

const MAKEFILE_AND_GAP_MARKERS = [_][]const u8{
    "but no `phase14-smoke`, `phase14-test`, or `phase14` targets",
    "- `zigux/tests/phase14_build.zig`",
    "- `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    "- `zigux/tests/phase14_skbuff_bridge.zig`",
    "- `zigux/tests/phase14_rcu_tree_survey.zig`",
    "- `net/core/skbuff_bridge.zig`",
};

const NEXT_STEP_MARKERS = [_][]const u8{
    "The next honest follow-up is now whichever smaller shared reminder surface or executable-layer readback boundary next drifts against that recovered packet.",
    "`Documentation/zigux/phase14-release-boundary-survey.md`",
    "`Documentation/zigux/phase14-attached-toolchain-guidance-gap.md`",
    "`Documentation/zigux/phase14-rcu-tree-survey.md`",
    "`scripts/zigux/check_phase14_rollback_threshold_sequencing.zig`",
    "`scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig`",
    "`scripts/zigux/check_phase14_rcu_rollback_guardrail.zig`",
    "without promoting the missing executable-layer paths or the absent `phase14-smoke`, `phase14-test`, and `phase14` wrappers.",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=productization_gap_roadmap_alignment",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (ROADMAP_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RETURNED_PACKET_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_AND_GAP_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (NEXT_STEP_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MARKER) |marker| try guard.requireMarker(text, marker);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();
    const io = std.Io.Threaded.init(allocator, .{});
    defer io.deinit();
    const args = try std.process.argsAlloc(allocator);
    defer std.process.argsFree(allocator, args);

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        try checkText("");
        try guard.printLine(io, "{s}", .{pass_marker});
        return;
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);
    const workflow_rel = ".github/workflows/zigux-bootstrap.yml";
    const workflow_path = try std.fmt.allocPrint(allocator, "{s}/{s}", .{ root, workflow_rel });
    defer allocator.free(workflow_path);
    const text = try guard.readUtf8File(io, allocator, workflow_path);
    defer allocator.free(text);
    try checkText(text);
    try guard.printLine(io, "{s}", .{pass_marker});
}
