const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const note_rel = "Documentation/zigux/release-tranche-status.md";

const REQUIRED_MARKERS = [_][]const u8{
    "# Zigux Release Tranche Status",
    "`RELEASE_STATUS=active`",
    "`RELEASE_CLOSURE_COMPLETE=no`",
    "commit-train entries `15. docs(zigux): close bounded phase-1 helper tranche` and `22. docs(zigux): close bounded Phase 2 toolchain tranche`",
    "`Documentation/zigux/phase12-release-sequencing.md`",
    "`Documentation/zigux/phase12-release-closure-checklist.md`",
    "`Documentation/zigux/phase12-release-readiness-survey.md`",
    "`Documentation/zigux/phase12-release-coordination-matrix.md`",
    "`Documentation/zigux/phase1-closure.md`",
    "`Documentation/zigux/phase2-closure.md`",
    "historical tranche targets that need re-materialization",
    "starting with `Documentation/zigux/README.md`",
};

const FORBIDDEN_MARKERS = [_][]const u8{
    "`RELEASE_CLOSURE_COMPLETE=yes`",
    "Phase 1 is directly readable on current `master`",
    "Phase 2 is directly readable on current `master`",
};

fn validateNote(text: []const u8, problems: *std.ArrayList([]const u8), allocator: std.mem.Allocator) !void {
    for (REQUIRED_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text, marker) == null) {
            const problem = try std.fmt.allocPrint(allocator, "missing required marker: {s}", .{marker});
            try problems.append(allocator, problem);
        }
    }
    for (FORBIDDEN_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text, marker) != null) {
            const problem = try std.fmt.allocPrint(allocator, "forbidden marker present: {s}", .{marker});
            try problems.append(allocator, problem);
        }
    }
}

fn printStderr(io: Io, comptime fmt: []const u8, args: anytype) !void {
    var buffer: [1024]u8 = undefined;
    var writer = Io.File.stderr().writer(io, &buffer);
    try writer.interface.print(fmt ++ "\n", args);
    try writer.interface.flush();
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var sample: std.ArrayList(u8) = .empty;
    defer sample.deinit(allocator);
    for (REQUIRED_MARKERS, 0..) |marker, index| {
        if (index != 0) try sample.append(allocator, '\n');
        try sample.appendSlice(allocator, marker);
    }

    var problems: std.ArrayList([]const u8) = .empty;
    defer {
        for (problems.items) |problem| allocator.free(problem);
        problems.deinit(allocator);
    }
    try validateNote(sample.items, &problems, allocator);
    if (problems.items.len != 0) {
        try printStderr(io, "self-test failed: valid sample should pass", .{});
        return 1;
    }

    const broken_text = try std.mem.replaceOwned(u8, allocator, sample.items, "`RELEASE_CLOSURE_COMPLETE=no`", "`RELEASE_CLOSURE_COMPLETE=yes`");
    defer allocator.free(broken_text);
    problems.clearRetainingCapacity();
    try validateNote(broken_text, &problems, allocator);
    if (problems.items.len == 0) {
        try printStderr(io, "self-test failed: broken sample should fail", .{});
        return 1;
    }

    try guard.printLine(io, "self-test passed", .{});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    var repo_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--repo-root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            repo_root = args[index];
            continue;
        }
        std.process.exit(2);
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = repo_root orelse try guard.repoRootFromScript(allocator);
    defer if (repo_root == null) allocator.free(root);

    const note_path = try guard.joinPath(allocator, root, note_rel);
    defer allocator.free(note_path);

    if (!guard.pathExists(io, note_path)) {
        try printStderr(io, "missing note: {s}", .{note_path});
        std.process.exit(1);
    }

    const text = try guard.readUtf8File(io, allocator, note_path);
    defer allocator.free(text);

    var problems: std.ArrayList([]const u8) = .empty;
    defer {
        for (problems.items) |problem| allocator.free(problem);
        problems.deinit(allocator);
    }
    try validateNote(text, &problems, allocator);

    if (problems.items.len != 0) {
        for (problems.items) |problem| try printStderr(io, "{s}", .{problem});
        std.process.exit(1);
    }

    try guard.printLine(io, "ok: {s}", .{note_rel});
}