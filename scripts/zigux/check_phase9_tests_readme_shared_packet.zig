const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE9_TESTS_README_SHARED_PACKET_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`",
    "`Documentation/zigux/review-checklist.md`",
    "`Documentation/zigux/README.md`",
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "`scripts/zigux/check_phase9_review_checklist_phase_boundaries.zig`",
    "`scripts/zigux/check_phase9_trace_events_runtime_packet.zig`",
    "`scripts/zigux/check_phase9_freeze_map_study_boundaries.zig`",
    "`samples/zigux/runtime_trace_events.zig`",
    "`samples/zigux/runtime_trace_events_unregistered_gate.zig`",
    "`samples/zigux/runtime_trace_events_exit_rollback_guard.zig`",
    "`samples/zigux/runtime_trace_events_registration_reentry_gate.zig`",
    "`zigux/tests/runtime_loader_allocator_init_flow.zig`",
    "`zigux/kernel/runtime_loader.zig`",
    "`zigux/kernel/runtime_loader_contract.zig`",
    "`zigux/kernel/runtime_loader_command_env_boundary_guard.zig`",
    "`phase9-runtime-loader-shared-tests`",
    "`phase9-runtime-loader-command-env-boundary-guard-tests`",
    "`Documentation/zigux/phase9-runtime-bitmap-survey.md`",
    "`zigux/tests/runtime_bitmap_manifest.json`",
    "`phase9-runtime-bitmap-cold-stage-guard-tests`",
    "`phase9-runtime-bitmap-tests`",
    "`samples/zigux/runtime_kretprobe.zig`",
    "`samples/zigux/runtime_kretprobe_loader.zig`",
    "`samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`",
    "`samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`",
    "`zigux/tests/runtime_kretprobe_survey.zig`",
    "`zigux/tests/runtime_kretprobe_module.zig`",
    "`zigux/tests/runtime_first_loadable_parity_behavior.zig`",
    "`phase9-runtime-kretprobe-sample-tests`",
    "`phase9-runtime-kretprobe-loader-tests`",
    "`phase9-runtime-kretprobe-initialized-snapshot-guard-tests`",
    "`phase9-runtime-kretprobe-registration-reentry-gate-tests`",
    "`phase9-runtime-kretprobe-survey-tests`",
    "`phase9-runtime-kretprobe-module-tests`",
    "`phase9-runtime-kretprobe-tests`",
    "`phase9-first-loadable-runtime-module-parity-behavior-tests`",
    "`Documentation/zigux/phase9-runtime-loader-gap-survey.md`",
    "`zigux/tests/runtime_loader_gap_manifest.json`",
    "`zigux/tests/runtime_loader_gap_survey.zig`",
    "`samples/zigux/runtime_trace_events_loader.zig`",
    "historical wider-family vocabulary",
    "family-local pilot evidence rather than proof that the broader shared runtime-loader packet, blocked publication boundaries, or install-root surfaces are complete",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "Phase 9 still has no dedicated tests-root reminder packet",
    "treat the returned kretprobe pilot as absent",
};

const SECTION_HEADING = [_][]const u8{
    "## Phase 9 shared runtime packet",
};

const NEXT_HEADING = [_][]const u8{
    "## Phase 10 shared virtio closure packet",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SECTION_HEADING) |marker| try guard.requireMarker(text, marker);
    for (NEXT_HEADING) |marker| try guard.requireMarker(text, marker);
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
