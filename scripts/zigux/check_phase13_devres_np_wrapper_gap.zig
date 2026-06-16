const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE13_DEVRES_NP_WRAPPER_GAP_SELF_TEST=pass";

const REQUIRED_FILES = [_][]const u8{
    "GAP_NOTE_PATH",
    "IOMAP_NOTE_PATH",
    "SURVEY_PATH",
    "MANIFEST_PATH",
    "REPLAY_PATH",
    "HELPER_PATH",
    "IOMAP_CHECKER_PATH",
    "WORKFLOW_GUIDE_PATH",
    "RELEASE_SURVEY_PATH",
    "TRACEABILITY_PATH",
};

const GAP_NOTE_MARKERS = [_][]const u8{
    "blocked `devm_ioremap_np()` wrapper",
    "`Documentation/zigux/phase13-contributor-workflow-guide.md`",
    "`Documentation/zigux/phase13-release-notes-survey.md`",
    "`Documentation/zigux/phase13-roadmap-traceability.md`",
    "`zig run scripts/zigux/check_phase13_devres_np_wrapper_gap.zig --`",
};

const IOMAP_NOTE_MARKERS = [_][]const u8{
    "translated helper-first remap would still require the blocked `devm_ioremap_np()` wrapper",
    "devm_ioremap_np()",
};

const SURVEY_MARKERS = [_][]const u8{
    "blocked `phase13-devres-missing-devm-ioremap-np-surface`",
    "helper-first iomap planning evidence",
};

const MANIFEST_MARKERS = [_][]const u8{
    "\"packet\": \"phase13-devres-iomap-planner\"",
    "\"id\": \"phase13-devres-missing-devm-ioremap-np-surface\"",
};

const REPLAY_MARKERS = [_][]const u8{
    "phase13 devres iomap planning keeps the blocked non-posted wrapper requirement explicit",
};

const HELPER_REQUIRED_MARKERS = [_][]const u8{
    ".provides_of_iomap_planning = true",
    ".provides_of_iomap_cleanup_handoff_planning = true",
    ".touches_live_mmio = false",
    "requires_nonposted_ioremap",
};

const HELPER_FORBIDDEN_MARKERS = [_][]const u8{
    "devm_ioremap_np(",
};

const IOMAP_CHECKER_MARKERS = [_][]const u8{
    "devm_ioremap_np()",
    "\"\\\"id\\\": \\\"phase13-devres-missing-devm-ioremap-np-surface\\\"\"",
};

const SUMMARY_FORBIDDEN_MARKERS = [_][]const u8{
    "devm_ioremap_np()",
    "phase13-devres-missing-devm-ioremap-np-surface",
    "requires_nonposted_ioremap",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (REQUIRED_FILES) |marker| try guard.requireMarker(text, marker);
    for (GAP_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (IOMAP_NOTE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (MANIFEST_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (REPLAY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (HELPER_REQUIRED_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (HELPER_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (IOMAP_CHECKER_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (SUMMARY_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
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
