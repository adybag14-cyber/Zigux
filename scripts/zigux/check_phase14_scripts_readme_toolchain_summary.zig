const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_CHECK_PACKET=scripts_readme_toolchain_summary_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "the current scripts-root shared smoke packet stays reviewable",
    "make -C zigux phase14-validate",
    "the readable `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)` chain in `zigux/Makefile`",
    "without implying that manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides are the default current rerun path",
    "scripts/zigux/check_phase14_shared_smoke_route.zig",
    "scripts/zigux/check_phase14_tests_readme_smoke_summary.zig",
    "scripts\zigux/validate_phase14.zig",
    "scripts/zigux/check_phase14_skbuff_stay_in_c_guardrail.zig",
    "scripts/zigux/check_phase14_rcu_rollback_guardrail.zig",
    "Documentation/zigux/phase14-attached-toolchain-guidance-gap.md",
    "Documentation/zigux/phase14-skbuff-bridge-survey.md",
    "Documentation/zigux/freeze-map.md",
    "Documentation/zigux/phase15-study-only-anchor-accounting.md",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "make -C zigux phase14-smoke replays the shipped",
    "make -C zigux phase14-test replays the shipped",
    "make -C zigux phase14 replays the shipped",
    "Phase 14 bridge parity is complete",
    "deep-core ownership has moved to Zigux",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=scripts_readme_toolchain_summary",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
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
