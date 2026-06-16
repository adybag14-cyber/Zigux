const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "{CHECK_NAME}_SELF_TEST=pass";

const EXPECTED_GAP_STATUSES = [_][]const u8{
    "queueing",
    "starter_verifier_direct_test_manifest_and_survey_gate_present_shared_build_absent",
    "throughput",
    "recovery_budget_summary_dedicated_direct_replay_present_throughput_gate_missing",
    "segmented",
    "driver_local_slice_note_manifest_survey_note_and_survey_gate_present_shared_build_absent",
    "shared_route",
    "shared_build_absent_direct_replay_and_survey_standalone",
    "survey_note",
    "survey_present_dedicated_verify_and_survey_retained_shared_build_absent",
    "survey_gate",
    "survey_present_packet_local_route_retained",
};

const CHECK_NAME = [_][]const u8{
    "PHASE12_NVME_PCI_PACKET",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (EXPECTED_GAP_STATUSES) |marker| try guard.requireMarker(text, marker);
    for (CHECK_NAME) |marker| try guard.requireMarker(text, marker);
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
