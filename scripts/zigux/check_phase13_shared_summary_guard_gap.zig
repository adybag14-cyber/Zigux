const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_SHARED_SUMMARY_GUARD_GAP_SELF_TEST=pass";

const FORBIDDEN_MARKERS = [_][]const u8{
    "missing guard path: `scripts/zigux/check_phase13_shared_summary_surfaces.zig`",
    "`scripts/zigux/check_phase13_shared_summary_surfaces.zig` is still absent on current `master`",
    "The remaining follow-up is broader README and tests-root packet refresh work, not another missing guard.",
    "zigux/tests/README.md still needs the returned `scripts\zigux/validate_phase13_release.zig` kept explicit as shipped release-discipline support",
    "the remaining broader shared reminder drift has contracted to one stale scripts-root repo-reality-gap sentence that still lists returned `scripts\zigux/validate_phase13_release.zig` as missing",
    "one stale tests-root repo-reality-gap sentence that lists returned `scripts\zigux/validate_phase13_release.zig` as missing",
    "But that same scripts-root section still treats missing `Documentation/zigux/phase13-libfs-survey.md` as shipped `libfs` evidence and still leaves returned `scripts\zigux/validate_phase13_release.zig` in repo-reality-gap wording",
    "while `scripts/zigux/README.md` still needs the shipped `libfs` packet kept anchored on `Documentation/zigux/phase13-libfs-slice.md`, `fs/libfs.zig`, `zigux/tests/phase13_libfs.zig`, `zigux/tests/phase13_libfs_reviewability.zig`, and `zigux/tests/phase13_libfs_manifest.json`",
    "What remains open inside this shared-subsystems lane has therefore moved out of the stable contributor-facing handle and into `Documentation/zigux/phase13-release-notes-survey.md`",
    "`Documentation/zigux/phase13-release-notes-survey.md` claim about `zigux/tests/README.md`",
};

const REQUIRED_MARKERS = [_][]const u8{
    "Documentation/zigux/phase13-shared-summary-guard-gap.md",
    "This note records the closure of the old missing-checker gap.",
    "The shipped guard is `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig --`.",
    "- companion handoff check: `zig run scripts/zigux/check_phase13_shared_summary_guard_gap.zig --`",
    "The remaining follow-up is now narrower than the old missing-checker gap and no longer includes the earlier tests-root release-validator undercount.",
    "`include/zigux/notifier_abi.h` materialized on current `master`",
    "What remains open inside this shared-subsystems lane has narrowed again:",
    "`Documentation/zigux/phase13-release-notes-survey.md` no longer carries the older tests-root validator-gap claim",
    "`scripts\zigux/validate_phase13_release.zig` is shipped current-`master` release-discipline support.",
    "- `Documentation/zigux/phase13-release-notes-survey.md`",
    "`scripts/zigux/README.md`",
    "`zigux/tests/README.md`",
    "Documentation/zigux/phase13-contributor-workflow-guide.md",
    "stable shared-summary guard: `zig run scripts/zigux/check_phase13_shared_summary_surfaces.zig --`",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
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
