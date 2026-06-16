const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_ROADMAP_TRACEABILITY_SELF_TEST=pass";

const REQUIRED_MARKERS = [_][]const u8{
    "This note restores the roadmap-to-repo owner map for the active Phase 13 shared-helper packet on current `master`.",
    "Phase 13 in the Zigux roadmap is the shared-subsystem-helper tranche bounded to four Linux anchors:",
    "- `fs/libfs.c`",
    "- `lib/devres.c`",
    "- `security/landlock/ruleset.c`",
    "- `security/landlock/syscalls.c`",
    "- stable shared-summary guard: `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig --`",
    "- stable roadmap-traceability guard: `zig run scripts/zigux/check_phase13_roadmap_traceability.zig --`",
    "Keep the broader docs-root, scripts-root, tests-root, shared-summary-gap, and notifier-gap packet explicit as the current reminder surface",
    "`Documentation/zigux/phase13-devres-iomap-planner.md`",
    "`scripts/zigux/check_phase13_devres_dmam_alloc_coherent_planner.zig`",
    "direct replay and direct reviewability companions through `zigux/tests/phase13_landlock_syscalls.zig` and `zigux/tests/phase13_landlock_syscalls_reviewability.zig`",
    "Adjacent notifier evidence can support release-surface truthfulness, but it does not become a fifth roadmap anchor.",
    "`zigux/tests/phase13_landlock_syscalls_manifest.json`",
    "Keep `Documentation/zigux/phase13-notifier-list-survey.md`, `scripts/zigux/check_phase13_notifier_packet.zig`, `zigux/tests/phase13_notifier_list_manifest.json`, `zigux/tests/phase13_notifier_list_reviewability.zig`, `zigux/bindings/notifier_abi.zig`, `zigux/helpers/notifier_chain_view.zig`, `zigux/helpers/list_view.zig`, `zigux/helpers/hlist_view.zig`, `include/zigux/abi.h`, `include/zigux/notifier_abi.h`, and `drivers/tty/hvc/hvc_console.h` explicit as the adjacent current-`master` packet while `scripts/zigux/check_phase13_notifier_priority_signal.zig` stays recorded as a repo-reality gap.",
    "Current `master` now materializes `scripts\zigux/validate_phase13_release.zig`, so keep that validator explicit as shipped release-discipline support for the shared Phase 13 reminder packet instead of carrying it with the still-missing validator-first checker packet, absent shared build companion, older direct devres companions, and the still-missing notifier priority-signal companion.",
    "- This note does not promote adjacent evidence into a fifth helper anchor.",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "keep `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json` framed as repo-reality gaps until current `master` materializes them again.",
    "while `zigux/helpers/notifier_chain_view.zig`, `include/zigux/notifier_abi.h`, and `scripts/zigux/check_phase13_notifier_priority_signal.zig` stay recorded as repo-reality gaps.",
    "and missing notifier-chain companion.",
    "- `zigux/helpers/notifier_chain_view.zig`n- `scripts/zigux/check_phase13_notifier_priority_signal.zig`",
};

const ROADMAP_NOTE = [_][]const u8{
    "Documentation/zigux/phase13-roadmap-traceability.md",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (ROADMAP_NOTE) |marker| try guard.requireMarker(text, marker);
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
