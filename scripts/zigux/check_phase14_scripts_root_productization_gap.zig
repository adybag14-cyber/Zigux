const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_SCRIPTS_ROOT_PRODUCTIZATION_GAP_SELF_TEST=pass";

const README_FORBIDDEN_MARKERS = [_][]const u8{
    "scripts/zigux/check_phase14_shared_smoke_route.zig` keep the current Phase 14",
};

const NOTE_REQUIRED_MARKERS = [_][]const u8{
    "PHASE14_GAP_KIND=scripts_root_productization_gap",
    "PHASE14_LANE_KEY=P14-L01",
    "Phase 14 stays bounded to study-only, wrapper-first, or stay-in-C evidence",
    "`scripts/zigux/README.md` currently jumps from `## Phase 13` to `## Phase 15`",
    "`scripts/zigux/check_phase14_shared_smoke_route.zig`",
    "`scripts/zigux/check_phase14_tests_readme_smoke_summary.zig`",
    "`scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig`",
    "`scripts/zigux/check_phase14_skbuff_compile_route.zig`",
    "`scripts/zigux/check_phase14_rcu_compile_route.zig`",
    "`scripts/zigux/check_phase14_rcu_rollback_guardrail.zig`",
    "`scripts/zigux/check_phase14_release_boundary_exact_counts.zig`",
    "`make -C zigux phase14-validate`",
    "do not restore `phase14-smoke`, `phase14-test`, or `phase14` as shipped wrapper claims",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=scripts_root_productization_gap",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (README_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (NOTE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
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
