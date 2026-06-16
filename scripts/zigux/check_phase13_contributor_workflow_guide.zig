const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_CONTRIBUTOR_WORKFLOW_GUIDE_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "Use this guide when a change touches the active Phase 13 shared-helper packet and the review needs one contributor-facing workflow note instead of reconstructing the packet from scattered reminder surfaces.",
    "Keep the contributor-facing shared handle aligned through:",
    "1. `Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "2. `scripts/zigux/README.md`",
    "3. `zigux/tests/README.md`",
    "stable shared-summary guard: `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig --`",
    "tests-root alignment companion: `zig run scripts/zigux/check_phase13_tests_readme_alignment.zig --`",
    "`zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`, so keep the file itself distinct from those missing Phase 13 route names and keep only the route names recorded as repo-reality gaps until the shared build handle returns.",
    "Keep `zigux/tests/phase13_devres.zig`, `zigux/tests/phase13_devres_reviewability.zig`, `zigux/tests/phase13_devres_boundary_evidence.zig`, `zigux/tests/phase13_devres_manifest.json`, `scripts/zigux/check_phase13_devres_packet.zig`, and `scripts/zigux/check_phase13_devres_packet_alignment.zig` recorded as repo-reality gaps until they rematerialize on current `master`.",
    "Keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` recorded as repo-reality gaps until they rematerialize on current `master`.",
    "Keep notifier evidence explicit as adjacent release-surface support through:",
    "- `Documentation/zigux/phase13-notifier-list-survey.md`",
    "- `scripts/zigux/check_phase13_notifier_packet.zig`",
    "- `zigux/tests/phase13_notifier_list_manifest.json`",
    "- `zigux/tests/phase13_notifier_list_reviewability.zig`",
    "- `zigux/bindings/notifier_abi.zig`",
    "- `zigux/helpers/list_view.zig`",
    "- `zigux/helpers/hlist_view.zig`",
    "- `include/zigux/abi.h`",
    "- `drivers/tty/hvc/hvc_console.h`",
    "Keep `zigux/helpers/notifier_chain_view.zig`, `scripts/zigux/check_phase13_notifier_priority_signal.zig`, and `include/zigux/notifier_abi.h` recorded as repo-reality gaps until they rematerialize on current `master`.",
    "- adjacent notifier evidence stays adjacent rather than becoming a fifth helper family",
    "- promote adjacent notifier evidence into a fifth helper family",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "Keep `make -C zigux phase13-validate` explicit as the stable contributor-facing handle until the shared build companion lands.",
    "`landlock/syscalls` owns the syscall governance, slice, survey, and focused helper-local replay packet through `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `security/landlock/syscalls.zig`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "Adjacent notifier evidence has become a fifth helper family.",
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
