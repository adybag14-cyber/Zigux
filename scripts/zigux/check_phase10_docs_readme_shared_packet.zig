const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE10_DOCS_ROOT_CHECKER_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "Phase 10 notes - `Documentation/zigux/phase10-closure-evidence.md`",
    "`Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`",
    "`Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`",
    "`scripts/zigux/README.md`",
    "`scripts/zigux/check_phase10_bootstrap_route.zig`",
    "`scripts/zigux/check_phase10_shared_freeze_boundary.zig`",
    "`scripts/zigux/check_phase10_ring_packet.zig`",
    "`scripts/zigux/check_phase10_input_packet.zig`",
    "`scripts/zigux/check_phase10_mmio_packet.zig`",
    "`scripts/zigux/check_phase10_harness_coverage.zig`",
    "`scripts/zigux/check_phase10_tests_readme_core_surfaces.zig`",
    "`scripts\zigux/validate_phase10.zig`",
    "`scripts\zigux/validate_phase10_closure.zig`",
    "`zigux/tests/phase10_closure_manifest.json`",
    "`zigux/tests/phase10_build.zig`",
    "`zigux/Makefile`",
    "current `master` does materialize `zigux/Makefile`, and its live body now exposes `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10`",
    "`zig run scripts/zigux/check_phase10_bootstrap_route.zig --`",
    "`make -C zigux phase10-validate`",
    "`make -C zigux phase10-test`",
    "`make -C zigux phase10`",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "while still treating them as missing-route vocabulary in the docs root",
    "while still treating them as missing direct-readback gaps",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
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
