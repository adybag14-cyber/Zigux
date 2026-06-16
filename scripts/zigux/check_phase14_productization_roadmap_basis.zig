const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_PRODUCTIZATION_ROADMAP_BASIS_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "PRODUCTIZATION_GAP_PATH",
    "SMOKE_SURVEY_PATH",
    "FREEZE_MAP_PATH",
    "STUDY_ONLY_ACCOUNTING_PATH",
    "ROUTE_CHECKER_PATH",
    "TESTS_README_CHECKER_PATH",
    "VALIDATOR_PATH",
    "MAKEFILE_PATH",
    "MANIFEST_PATH",
    "WORKQUEUE_MANIFEST_PATH",
    "RING_BUFFER_SURVEY_PATH",
};

const PRODUCTIZATION_MARKERS = [_][]const u8{
    "Phase 14 in `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` is the `Core-Adjacent Bounded Internals` lane.",
    "- boundary maps",
    "- concurrency audits",
    "- explicit stay-in-C decisions where warranted",
    "- wrapper-first or study-only posture",
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
    "- `net/core/skbuff.c`",
    "- `kernel/rcu/tree.c`",
    "`zigux/Makefile` is readable again on current `master`, and its live body currently exposes the Phase 2 toolchain and kbuild routes together with the bounded Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes plus `phase14-validate`, but no `phase14-smoke`, `phase14-test`, or `phase14` targets",
    "`scripts/zigux/check_phase14_shared_smoke_route.zig` now returns through the current contents path",
    "`scripts/zigux/check_phase14_tests_readme_smoke_summary.zig` now returns through the current contents path",
    "`scripts\zigux/validate_phase14.zig` now returns through the current contents path",
    "`scripts/zigux/check_phase14_release_boundary_exact_counts.zig` now returns through the current contents path",
    "`zigux/tests/phase14_end_to_end_smoke_manifest.json` now returns through the current contents path",
    "`kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, and `zigux/tests/phase14_workqueue_bridge_manifest.json` are directly readable again as the workqueue-local reviewability shard",
    "`zigux/tests/phase14_ring_buffer_survey.zig` now returns through the current contents path as a directly readable ring-buffer survey companion",
    "- `zigux/tests/phase14_build.zig`",
    "- `zigux/tests/phase14_end_to_end_smoke_survey.zig`",
    "- `zigux/tests/phase14_skbuff_bridge.zig`",
    "- `zigux/tests/phase14_rcu_tree_survey.zig`",
    "- `net/core/skbuff_bridge.zig`",
    "Given the roadmap, the correct Phase 14 posture remains study-only and wrapper-first.",
    "the directly readable shared-smoke route checker",
    "the directly readable tests-root reminder checker",
    "the directly readable validator body",
    "the directly readable release-boundary exact-count guard",
};

const SMOKE_SURVEY_MARKERS = [_][]const u8{
    "Primary product goal:",
    "The Phase 14 roadmap treats `kernel/workqueue.c`, `net/core/skbuff.c`, `kernel/trace/ring_buffer.c`, and `kernel/rcu/tree.c` as boundary-study or freeze-in-C anchors.",
    "`zigux/tests/phase14_ring_buffer_survey.zig` is directly readable again on current `master`",
    "the current readable route layer still stops at `make -C zigux phase14-validate`",
};

const FREEZE_MAP_MARKERS = [_][]const u8{
    "- `kernel/rcu/tree.c`",
    "- `net/core/skbuff.c`",
    "- `kernel/workqueue.c`",
    "- `kernel/trace/ring_buffer.c`",
};

const STUDY_ONLY_ACCOUNTING_MARKERS = [_][]const u8{
    "The roadmap keeps two deep-core areas in a narrower posture than the four freeze-in-C anchors: `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` stay study-only",
};

const ROUTE_CHECKER_MARKERS = [_][]const u8{
    "PHASE14_CHECK_PACKET=shared_smoke_route",
    "run: make -C zigux phase14-validate",
};

const TESTS_README_CHECKER_MARKERS = [_][]const u8{
    "Check that the shared Phase 14 tests-root reminder stays aligned with repo reality.",
    "PHASE14_TESTS_README_SMOKE_SUMMARY_SELF_TEST=pass",
};

const VALIDATOR_MARKERS = [_][]const u8{
    "PHASE14_VALIDATION=pass",
    "PHASE14_VALIDATOR_SELF_TEST=pass",
    "Documentation/zigux/phase14-productization-gap-survey.md",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase14-validate:",
    "scripts/zigux/check_phase14_shared_smoke_route.zig --self-test",
    "scripts/zigux/check_phase14_tests_readme_smoke_summary.zig --self-test",
    "scripts\zigux/validate_phase14.zig --self-test",
};

const FORBIDDEN_MAKEFILE_MARKERS = [_][]const u8{
    "phase14-smoke:",
    "phase14-test:",
    "phase14: phase14-validate",
};

const MANIFEST_MARKERS = [_][]const u8{
    "\"validation_gate\": \"make -C zigux phase14-validate\"",
    "\"smoke_commands\": [",
    "\"make -C zigux phase14-validate\"",
    "\"smoke_shard_commands\": []",
    "\"phase14_make_smoke_target_present\": false",
};

const WORKQUEUE_MANIFEST_MARKERS = [_][]const u8{
    "\"lane_key\": \"P14-L04\"",
    "\"current_lane_posture\": \"blocked_maintenance\"",
};

const RING_BUFFER_SURVEY_MARKERS = [_][]const u8{
    "phase14-ring-buffer-maintenance-handoff",
    "phase14-ring-buffer-tracefs-reader-serialization-followup",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=productization_roadmap_basis",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (PRODUCTIZATION_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SMOKE_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FREEZE_MAP_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (STUDY_ONLY_ACCOUNTING_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (ROUTE_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (VALIDATOR_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (WORKQUEUE_MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RING_BUFFER_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
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
