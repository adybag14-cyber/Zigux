const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_BOOTSTRAP_SUPPORT_PACKET_SELF_TEST=pass";

const WORKFLOW_MARKERS = [_][]const u8{
    "- name: Validate current Phase 11 support bundle",
    "run: make -C zigux phase11-validate",
};

const MAKEFILE_MARKERS = [_][]const u8{
    "phase11-validate:",
    "cd $(ZIGUX_ROOT) && $(ZIG) run scripts/zigux/validate_phase11.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_dw_wdt_build.zig",
    "cd $(ZIGUX_ROOT) && $(ZIG_REPO_ROOT) build test --build-file zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig",
};

const SHARED_CONTRACT_MARKERS = [_][]const u8{
    "`scripts\zigux/validate_phase11.zig`",
    "`zigux/tests/fixtures/phase11_build_inventory.json`",
    "`make -C zigux phase11-validate` explicit together instead of reviving",
    "removed `phase11-contract`, `phase11`, `phase11-hvc-survey`,",
};

const SCRIPTS_README_MARKERS = [_][]const u8{
    "`scripts/zigux/check_phase11_build_inventory.zig`",
    "`scripts/zigux/check_phase11_hvc_targetless_unregister_witness.zig`",
    "`scripts\zigux/validate_phase11.zig`",
    "`make -C zigux phase11-validate`",
};

const TESTS_README_MARKERS = [_][]const u8{
    "`scripts/zigux/check_phase11_build_inventory.zig`",
    "`scripts\zigux/validate_phase11.zig`",
    "`zigux/Makefile`",
    "`make -C zigux phase11-validate`",
    "`zigux/tests/phase11_hvc_targetless_unregister_gap_build.zig`",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (WORKFLOW_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MAKEFILE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SHARED_CONTRACT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SCRIPTS_README_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (TESTS_README_MARKERS) |marker| try guard.requireMarker(text, marker);
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
