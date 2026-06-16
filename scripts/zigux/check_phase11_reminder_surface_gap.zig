const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const pass_marker = "PHASE11_REMINDER_SURFACE_GAP_SELF_TEST=pass";

const SURVEY_MARKERS = [_][]const u8{
    "`phase11-shared-reminder-surface-gap`",
    "`scripts/zigux/README.md` and `zigux/tests/README.md` still omit a Phase 11 packet entry",
    "narrower validator-backed packet is landed",
};

const COVERAGE_MARKERS = [_][]const u8{
    "the shared reminder surfaces outside this note stack still lag the roadmap",
    "`scripts/zigux/README.md` and `zigux/tests/README.md` currently skip Phase 11",
    "`Documentation/zigux/phase11-uapi-header-parity-survey.md`",
    "`scripts\zigux/validate_phase11.zig`",
    "`make -C zigux phase11-validate`",
};

const README_FORBIDDEN_MARKERS = [_][]const u8{
    "phase11-validate",
    "check-phase11-header-boundary-packet.py",
};

pub fn checkText(text: []const u8) guard.GuardError!void {
    for (SURVEY_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (COVERAGE_MARKERS) |marker| try guard.requireMarker(text, marker);
    for (README_FORBIDDEN_MARKERS) |marker| try guard.requireMarker(text, marker);
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
