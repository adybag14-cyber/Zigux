const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_WORKQUEUE_STUDY_ONLY_GUARDRAIL_SELF_TEST=pass";

const GUARDRAIL_MARKER = [_][]const u8{
    "- manifest-backed guardrail: `phase14-workqueue-study-only-guardrail` keeps this study-only packet fail-closed until the same bridge-local packet carries narrower stay-in-C evidence instead of a lighter bridge-presence or shared-route claim.",
};

const REQUIRED_EVIDENCE_MARKERS = [_][]const u8{
    "- direct bridge-local trust gate: `zig test zigux/tests/phase14_workqueue_reviewability.zig`",
    "- bridge-local reread of `kernel/workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_bridge.zig`, `zigux/tests/phase14_workqueue_reviewability.zig`, `zigux/tests/phase14_workqueue_bridge_manifest.json`, `Documentation/zigux/phase14-workqueue-bridge-slice.md`, and `Documentation/zigux/phase14-workqueue-bridge-survey.md`",
    "- explicit blocker retention for `phase14-workqueue-live-execution-blocker` together with the current `blocked_maintenance` posture",
};

const RETURN_TO_BLOCKED_MARKERS = [_][]const u8{
    "- any wording that treats `make -C zigux phase14-validate` or shared packet-local validation as a replacement for the direct bridge-local trust gate",
    "- missing `phase14-workqueue-live-execution-blocker`, `blocked_maintenance`, or `shared_packet_local_only` wording in the active survey or manifest",
    "- any claim of live worker execution, callback dispatch ownership, flush or drain completion ownership, delayed-work requeue control, scheduler-visible worker-state parity, rescuer execution ownership, or hotplug-driven topology rebinding ownership",
};

const REQUIRED_NOTE_MARKERS = [_][]const u8{
    "`PHASE14_STATUS=blocked_maintenance`",
    "`PHASE14_LANE_KEY=P14-L04`",
    "`PHASE14_ANCHOR=kernel/workqueue.c`",
    "`PHASE14_CURRENT_SLICE=phase14-workqueue-scheduler-visible-worker-state-refinement`",
    "`PHASE14_REVIEWABILITY_TEST=zigux/tests/phase14_workqueue_reviewability.zig`",
    "`PHASE14_BLOCKER=phase14-workqueue-live-execution-blocker`",
    "the bridge-local trusted rerun still stops at `zig test zigux/tests/phase14_workqueue_reviewability.zig`, while `make -C zigux phase14-validate` remains the broader shared packet-local validation route rather than bridge-local proof",
    "GUARDRAIL_MARKER",
    "`scripts/zigux/check_phase14_workqueue_study_only_guardrail.zig`",
    "REQUIRED_EVIDENCE_HEADING",
    "REQUIRED_EVIDENCE_MARKERS",
    "RETURN_TO_BLOCKED_HEADING",
    "RETURN_TO_BLOCKED_MARKERS",
};

const MANIFEST_REQUIRED_MARKERS = [_][]const u8{
    "\"lane_key\": \"P14-L04\"",
    "\"anchor\": \"kernel/workqueue.c\"",
    "\"current_lane_posture\": \"blocked_maintenance\"",
    "\"productization_posture\": \"shared_packet_local_only\"",
    "\"shared_packet_local_validation\": \"make -C zigux phase14-validate\"",
    "\"zig run scripts/zigux/check_phase14_workqueue_study_only_guardrail.zig -- --self-test\"",
    "\"zig run scripts/zigux/check_phase14_workqueue_study_only_guardrail.zig --\"",
    "\"phase14-workqueue-study-only-guardrail\"",
    "\"direct_bridge_local_trust_gate\": \"zig test zigux/tests/phase14_workqueue_reviewability.zig\"",
    "\"phase14-workqueue-live-execution-blocker\"",
};

const FORBIDDEN_NOTE_MARKERS = [_][]const u8{
    "returned make-backed focused workqueue route",
};

const NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase14-workqueue-bridge-survey.md",
};

const MANIFEST_PATH = [_][]const u8{
    "zigux/tests/phase14_workqueue_bridge_manifest.json",
};

const REQUIRED_EVIDENCE_HEADING = [_][]const u8{
    "- required evidence before any trust promotion:",
};

const RETURN_TO_BLOCKED_HEADING = [_][]const u8{
    "- automatic return-to-blocked triggers:",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (GUARDRAIL_MARKER) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_EVIDENCE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RETURN_TO_BLOCKED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (NOTE_PATH) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_PATH) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_EVIDENCE_HEADING) |marker| try guard.requireMarker(text, marker);
    for (RETURN_TO_BLOCKED_HEADING) |marker| try guard.requireMarker(text, marker);
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
