const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_TESTS_ROOT_RETURNED_ANCHOR_SELF_TEST=pass";

const SCRIPTS_ROOT_PHRASE = [_][]const u8{
    "Treat `scripts/zigux/README.md` as the current dedicated Phase 10 scripts-root packet on current `master` and keep it aligned with the shared closure note, lane-sequencing note, review checklist, and tests-root reminder instead of leaving it in neighboring-surface wording.",
};

const REQUIRED_MARKERS = [_][]const u8{
    "returned shared closure packet anchors: `scripts\zigux/validate_phase10.zig`, `scripts\zigux/validate_phase10_closure.zig`, `Documentation/zigux/phase10-virtio-core-survey.md`, and `zigux/tests/phase10_closure_manifest.json`",
    "The returned shared build gate now runs through `zigux/Makefile`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, `make -C zigux phase10`, and `zigux/tests/phase10_build.zig`.",
    "Current `master` does materialize `zigux/Makefile`, and its live body now exposes the dedicated `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` routes, so keep the returned file and those returned Phase 10 route names explicit as the shared build gate instead of treating them as repo-reality gaps.",
    "SCRIPTS_ROOT_PHRASE",
    "Keep the returned shared validator pair `scripts\zigux/validate_phase10.zig` and `scripts\zigux/validate_phase10_closure.zig` plus the returned `zigux/Makefile` explicit in that directly re-readable anchor set instead of leaving them visible only in the shared build-gate reminder.",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (SCRIPTS_ROOT_PHRASE) |marker| try guard.requireMarker(text, marker);
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
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
