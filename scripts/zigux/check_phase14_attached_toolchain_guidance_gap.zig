const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE_GAP_SELF_TEST=pass";

const ATTACHED_GUIDANCE_MARKERS = [_][]const u8{
    "- lane: `P14-L10`",
    "- status: `current-master reminder truthfulness follow-through`",
    "attached Zig bundle used by this lane still behaves like a usable bounded-check fallback rather than a stale archival assumption",
    "`phase14-validate`",
    "manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides remain optional packet-local escape hatches rather than the primary current rerun path",
    "the scripts-root Phase 14 summary still owns the smallest same-lane reminder repair because it undercounts the returned skbuff stay-in-C guard",
};

const SMOKE_SURVEY_MARKERS = [_][]const u8{
    "* `PHASE14_ATTACHED_TOOLCHAIN_GUIDANCE=packet_local_only`",
    "the current readable route layer still stops at `make -C zigux phase14-validate`",
    "Keep those older wrapper names recorded only as historical packet vocabulary until the same exact readback mode restores the missing broader Phase 14 Makefile routes on current `master`.",
};

const RELEASE_BOUNDARY_MARKERS = [_][]const u8{
    "- `PHASE14_SHARED_SMOKE_GATE_COUNT=1`",
    "- `PHASE14_ACTIVE_DELIVERY_GATE_COUNT=0`",
    "Keep the attached-toolchain boundary here as historical packet-local vocabulary too, without restating the older `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-*` wrapper triplet as current fallback guidance while the readable Makefile still omits those broader targets.",
};

const PRODUCTIZATION_GAP_MARKERS = [_][]const u8{
    "The higher-value same-lane task is reminder-surface truthfulness:",
    "the directly readable shared smoke manifest",
    "the readable non-owner Makefile body with shipped Phase 2, Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12 routes plus `phase14-validate` but no `phase14-smoke`, `phase14-test`, or `phase14` targets",
};

const SHARED_SMOKE_GAP_MARKERS = [_][]const u8{
    "the returned `phase14-validate` gate",
    "the returned route checker",
    "the returned tests-root reminder checker",
    "the aligned manifest posture",
    "the continued absence of the broader `phase14-smoke`, `phase14-test`, and `phase14` wrappers on current `master`",
};

const SCRIPTS_README_MARKERS = [_][]const u8{
    "the current scripts-root shared smoke packet stays reviewable",
    "the readable `ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)` chain in `zigux/Makefile`",
    "without implying that manual `ZIG=/absolute/path/to/attached-zig/zig ...` overrides are the default current rerun path",
};

const MAKEFILE_PRESENT_MARKERS = [_][]const u8{
    "ZIG ?= $(if $(ZIG_PINNED_TOOLCHAIN),$(ZIG_PINNED_TOOLCHAIN),zig)",
    "phase12-smoke:",
    "phase14-validate:",
};

const MAKEFILE_ABSENT_MARKERS = [_][]const u8{
    "phase14-smoke:",
    "phase14-test:",
    "phase14: phase14-validate phase14-smoke phase14-test",
};

const MARKER = [_][]const u8{
    "PHASE14_CHECK_PACKET=attached_toolchain_guidance_gap",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (ATTACHED_GUIDANCE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SMOKE_SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (RELEASE_BOUNDARY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (PRODUCTIZATION_GAP_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SHARED_SMOKE_GAP_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_PRESENT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_ABSENT_MARKERS) |marker| try guard.requireMarker(text, marker);
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
