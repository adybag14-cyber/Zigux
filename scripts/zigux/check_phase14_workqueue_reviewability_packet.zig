const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_WORKQUEUE_REVIEWABILITY_PACKET_SELF_TEST=pass";

const ROOT = [_][]const u8{
    "Path.resolve.parents[2]iflen>2elsePath.resolve.parent",
};

const DIRECT_PACKET_FILES = [_][]const u8{
    "Documentation/zigux/phase14-core-boundary-traceability.md",
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "Documentation/zigux/phase14-workqueue-bridge-slice.md",
    "Documentation/zigux/phase14-workqueue-bridge-survey.md",
    "Documentation/zigux/review-checklist.md",
    "kernel/workqueue_bridge.zig",
    "zigux/tests/phase14_build.zig",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
    "zigux/tests/phase14_workqueue_bridge.zig",
    "zigux/tests/phase14_workqueue_bridge_manifest.json",
    "zigux/tests/phase14_workqueue_reviewability.zig",
};

const EXPECTED_ROADMAP_DESTINATIONS = [_][]const u8{
    "kernel/workqueue_bridge.zig",
    "zigux/tests/",
    "Documentation/zigux/",
};

const EXPECTED_REPLAY = [_][]const u8{
    "zig test zigux/tests/phase14_workqueue_reviewability.zig",
    "zig build test --build-file zigux/tests/phase14_build.zig --summary all",
    "make -C zigux phase14",
};

const MARKERS = [_][]const u8{
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "`zigux/tests/phase14_workqueue_reviewability.zig`",
    "`phase14-workqueue-reviewability-tests` -> `phase14_workqueue_reviewability.zig` -> `full_bundle_only`",
    "focused workqueue reviewability replay",
    "workqueue: `zigux/tests/phase14_workqueue_bridge_manifest.json`, lane `P14-L04`, ",
    "surveyed commit `{SURVEYED_COMMIT}`, ready-next `none currently recorded`, blocked `{BLOCKED_GAP}`",
    "the same packet also keeps the two landed bridge-backed roadmap destinations explicit by tying ",
    "`phase14-workqueue-bridge-tests` to `../../kernel/workqueue_bridge.zig` and ",
    "`phase14-skbuff-bridge-tests` to `../../net/core/skbuff_bridge.zig`, instead of letting the matrix ",
    "collapse to test-root names alone.",
    "Documentation/zigux/phase14-core-boundary-traceability.md",
    "lane key: `{LANE_KEY}`",
    "surveyed commit: `{SURVEYED_COMMIT}`",
    "ready-next gap: none currently recorded",
    "blocked gap: `{BLOCKED_GAP}`",
    "Documentation/zigux/phase14-workqueue-bridge-survey.md",
    "PHASE14_STATUS=blocked_maintenance",
    "PHASE14_LANE_KEY={LANE_KEY}",
    "PHASE14_SURVEYED_COMMIT={SURVEYED_COMMIT}",
    "phase14-workqueue-delayed-requeue-governance",
    "phase14-workqueue-flush-drain-governance",
    "phase14-workqueue-rescuer-mayday-governance",
    "phase14-workqueue-scheduler-visible-worker-state-refinement",
    "hotplug-topology-rebinding",
    "scheduler-visible-worker-state-refinement",
    "CPU-hotplug pool rebinding",
    "scheduler-facing runnable-state transitions",
    "delayed-work requeue control",
    "runtime `max_active` retuning ownership",
    "## Reviewability guardrails",
    "lane `{LANE_KEY}`",
    "surveyed commit `{SURVEYED_COMMIT}`",
    "Do not treat this lane as permission to claim wrapper ownership",
    "Leave this lane in blocked maintenance",
    "flush-drain active-color governance note",
    "timer-base ownership",
    "CPU affinity",
    "delayed-work requeue ownership",
    "runtime `max_active` retuning boundary",
    "live execution in C",
    "`make -C zigux phase14-test`",
    "Documentation/zigux/phase14-workqueue-bridge-slice.md",
    "# Phase 14 Workqueue Bridge Slice",
    "`PHASE14_LANE_KEY={LANE_KEY}`",
    "`{SURVEYED_COMMIT}`",
    "`kernel/workqueue_bridge.zig`",
    "`zigux/tests/phase14_workqueue_bridge.zig`",
    "`zigux/tests/phase14_workqueue_reviewability.zig`",
    "eight boundary areas",
    "fifteen review-only audit checkpoints",
    "seven blocked live behaviors",
    "delayed-work timer expiry",
    "flush, drain, and cancellation completion ownership",
    "hotplug-driven worker migration and topology rebinding",
    "Documentation/zigux/review-checklist.md",
    "if the change touches the shared Phase 14 smoke packet",
    "`zigux/tests/phase14_workqueue_reviewability.zig`",
    "`zigux/tests/phase14_workqueue_bridge.zig`",
    "`zigux/tests/phase14_workqueue_bridge_manifest.json`",
    "`kernel/workqueue.c` and `kernel/trace/ring_buffer.c` kept explicit as the two boundary-study-only anchors",
    "`kernel/rcu/tree.c` plus `net/core/skbuff.c` kept explicit as the two freeze-in-C-governed anchors",
    "without implying an active deep-core port claim",
    "zigux/tests/phase14_build.zig",
    "../../kernel/workqueue_bridge.zig",
    "../../net/core/skbuff_bridge.zig",
    "zigux/tests/phase14_end_to_end_smoke_manifest.json",
    "\"zigux/tests/phase14_workqueue_reviewability.zig\"",
    "\"label\": \"phase14-workqueue-reviewability-tests\"",
    "\"root_source\": \"phase14_workqueue_reviewability.zig\"",
    "\"coverage\": \"full_bundle_only\"",
    "zigux/tests/phase14_workqueue_reviewability.zig",
    "phase14 shared smoke manifest keeps workqueue reviewability explicit",
    "phase14 workqueue anchor packet keeps the delayed-work governance follow-through explicit",
    "phase14 workqueue survey keeps hotplug and scheduler-visible checkpoints explicit",
    "phase14 workqueue survey keeps reviewer guardrails explicit",
    "\"lane_key\": \"{LANE_KEY}\"",
    "\"surveyed_commit\": \"{SURVEYED_COMMIT}\"",
    "\"blocked_gap\": \"{BLOCKED_GAP}\"",
    "phase14-workqueue-delayed-requeue-governance",
    "phase14-workqueue-scheduler-visible-worker-state-refinement",
    "phase14-workqueue-pending-bit-audit",
    "zigux/tests/phase14_workqueue_bridge.zig",
    "phase14-workqueue-live-execution-blocker",
    "blocked_maintenance",
    "delayed-work",
    "scheduler-visible",
    "kernel/workqueue_bridge.zig",
    "phase14-workqueue-delayed-requeue-governance",
    "phase14-workqueue-flush-drain-governance",
    "phase14-workqueue-rescuer-mayday-governance",
    "phase14-workqueue-scheduler-visible-worker-state-refinement",
    "hotplug-topology-rebinding",
};

const ABSENT_MARKERS = [_][]const u8{
    "Documentation/zigux/phase14-end-to-end-smoke-survey.md",
    "phase14-workqueue-pending-bit-audit",
    "Documentation/zigux/phase14-core-boundary-traceability.md",
    "phase14-workqueue-pending-bit-audit",
    "lane key: `P14-L01`",
    "`007f00d0c6b6b430bfbb2110555544cc5faefe8b`",
    "Documentation/zigux/phase14-workqueue-bridge-survey.md",
    "`make -C zigux phase14-smoke`",
    "zigux/tests/phase14_workqueue_reviewability.zig",
    "\"ready_next_gap\": \"phase14-workqueue-pending-bit-audit\"",
};

const MANIFEST_SCALARS = [_][]const u8{
    "lane_key",
    "phase",
    "Phase 14",
    "surveyed_commit",
    "anchor",
    "kernel/workqueue.c",
};

const EXPECTED_SURVEY_SUMMARY = [_][]const u8{
    "workqueue_c_lines",
    "workqueue_internal_h_lines",
    "test_workqueue_c_lines",
    "preexisting_kernel_export_shim_present",
    "preexisting_phase14_build_present",
    "preexisting_phase14_make_target_present",
    "preexisting_workqueue_bridge_present",
    "preexisting_phase14_workqueue_test_present",
    "preexisting_phase14_workqueue_manifest_present",
    "preexisting_phase14_workqueue_slice_note_present",
    "preexisting_phase14_workqueue_survey_note_present",
};

const EXPECTED_GAP_IDS = [_][]const u8{
    "phase14-build-gate",
    "phase14-make-target",
    "phase14-kernel-export-shim-foundation",
    "phase14-workqueue-boundary-map-starter",
    "phase14-workqueue-test-gate",
    "phase14-workqueue-slice-note",
    "phase14-workqueue-survey-note",
    "phase14-workqueue-concurrency-audit-outline",
    "phase14-workqueue-max-active-audit",
    "phase14-workqueue-lock-handoff-audit",
    "phase14-workqueue-pending-bit-followup",
    "phase14-workqueue-delayed-submission-alias-followup",
    "phase14-workqueue-delayed-timer-expiry-followup",
    "phase14-workqueue-delayed-requeue-governance",
    "phase14-workqueue-flush-drain-governance",
    "phase14-workqueue-rescuer-mayday-governance",
    "phase14-workqueue-scheduler-visible-worker-state-refinement",
};

const EXPECTED_BLOCKED_STATUS = [_][]const u8{
    "blocked_on_live_concurrency",
};

const SURVEYED_COMMIT = [_][]const u8{
    "9b98d3b9c812840bf279508030be0b8de093736c",
};

const BLOCKED_GAP = [_][]const u8{
    "phase14-workqueue-live-execution-blocker",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (ROOT) |marker| try guard.requireMarker(text, marker);
    for (DIRECT_PACKET_FILES) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_ROADMAP_DESTINATIONS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_REPLAY) |marker| try guard.requireMarker(text, marker);
    for (MARKERS) |marker| try guard.requireMarker(text, marker);
    for (ABSENT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_SCALARS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_SURVEY_SUMMARY) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_GAP_IDS) |marker| try guard.requireMarker(text, marker);
    for (EXPECTED_BLOCKED_STATUS) |marker| try guard.requireMarker(text, marker);
    for (SURVEYED_COMMIT) |marker| try guard.requireMarker(text, marker);
    for (BLOCKED_GAP) |marker| try guard.requireMarker(text, marker);
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
