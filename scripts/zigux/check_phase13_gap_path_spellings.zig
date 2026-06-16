const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_GAP_PATH_SPELLINGS_SELF_TEST=pass";

const TRACKED_FILES = [_][]const u8{
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md",
    "Documentation/zigux/phase13-shared-summary-guard-gap.md",
    "Documentation/zigux/phase13-gap-path-spellings.md",
    "scripts/zigux/README.md",
    "zigux/tests/README.md",
};

const CANONICAL_PATHS = [_][]const u8{
    "zigux/tests/phase13_devres.zig",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13_devres_boundary_evidence.zig",
    "zigux/tests/phase13_devres_manifest.json",
    "Documentation/zigux/phase13-landlock-syscalls-survey.md",
    "zigux/tests/phase13_landlock_syscalls.zig",
    "zigux/tests/phase13_landlock_syscalls_reviewability.zig",
    "zigux/tests/phase13_landlock_syscalls_manifest.json",
    "zigux/helpers/notifier_chain_view.zig",
    "include/zigux/notifier_abi.h",
    "make -C zigux phase13-validate",
    "make -C zigux phase13",
};

const STALE_SPELLINGS = [_][]const u8{
    "zigux/tests/phase13Devres_reviewability.zig",
};

const ALLOWED_STALE_CONTEXT_MARKERS = [_][]const u8{
    "treat that as stale wording",
    "Stale Spellings To Reject",
    "historical wording only",
};

const NOTE_REQUIRED_MARKERS = [_][]const u8{
    "validator: `zig run scripts/zigux/check_phase13_gap_path_spellings.zig --`",
    "zigux/tests/phase13_devres_reviewability.zig",
    "zigux/tests/phase13Devres_reviewability.zig",
    "Keep `zigux/Makefile` distinct from the still-missing Phase 13 route names above.",
};

const NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase13-gap-path-spellings.md",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (TRACKED_FILES) |marker| try guard.requireMarker(text, marker);
    for (CANONICAL_PATHS) |marker| try guard.requireMarker(text, marker);
    for (STALE_SPELLINGS) |marker| try guard.requireMarker(text, marker);
    for (ALLOWED_STALE_CONTEXT_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (NOTE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (NOTE_PATH) |marker| try guard.requireMarker(text, marker);
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
