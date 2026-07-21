const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const index_rel = "Documentation/zigux/release-planning-index.md";
pub const pass_marker = "RELEASE_PLANNING_INDEX=pass";
pub const fail_marker = "RELEASE_PLANNING_INDEX=fail";
pub const self_test_pass_marker = "RELEASE_PLANNING_INDEX_SELFTEST=pass";

const REQUIRED_DOCS = [_][]const u8{
    "Documentation/zigux/phase12-release-sequencing.md",
    "Documentation/zigux/phase12-release-readiness-survey.md",
    "Documentation/zigux/phase12-release-closure-checklist.md",
    "Documentation/zigux/phase12-release-coordination-matrix.md",
    "Documentation/zigux/phase12-raw-github-coverage-survey.md",
    "Documentation/zigux/phase13-release-coordination-matrix.md",
    "Documentation/zigux/phase13-release-notes-survey.md",
    "Documentation/zigux/phase13-roadmap-traceability.md",
    "Documentation/zigux/phase14-release-boundary-survey.md",
    "Documentation/zigux/phase15-architecture-council-review-process.md",
};

const REQUIRED_MARKERS = [_][]const u8{
    "`RELEASE_PACKET_STATUS=active_not_closed`",
    "docs-root release index guard: `zig run scripts/zigux/check_release_planning_index.zig`",
    "- Phase 12 remains the active shared release packet",
    "- Phase 13 remains the active helper-release packet",
    "- Phase 14 remains the release-boundary and productization reminder packet.",
    "- Phase 15 remains Architecture Council governance",
};

fn collectIssues(
    io: Io,
    allocator: std.mem.Allocator,
    root: []const u8,
    issues: *std.ArrayList([]const u8),
) !void {
    const index_path = try guard.joinPath(allocator, root, index_rel);
    defer allocator.free(index_path);

    if (!guard.pathExists(io, index_path)) {
        const issue = try std.fmt.allocPrint(allocator, "missing_file:{s}", .{index_rel});
        try issues.append(allocator, issue);
        return;
    }

    const text = try guard.readUtf8File(io, allocator, index_path);
    defer allocator.free(text);

    for (REQUIRED_MARKERS) |marker| {
        if (std.mem.indexOf(u8, text, marker) == null) {
            const issue = try std.fmt.allocPrint(allocator, "missing_marker:{s}", .{marker});
            try issues.append(allocator, issue);
        }
    }

    for (REQUIRED_DOCS) |relpath| {
        if (std.mem.indexOf(u8, text, relpath) == null) {
            const issue = try std.fmt.allocPrint(allocator, "missing_doc_reference:{s}", .{relpath});
            try issues.append(allocator, issue);
        }
        const support_path = try guard.joinPath(allocator, root, relpath);
        defer allocator.free(support_path);
        if (!guard.pathExists(io, support_path)) {
            const issue = try std.fmt.allocPrint(allocator, "missing_support_file:{s}", .{relpath});
            try issues.append(allocator, issue);
        }
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    var tmp = try guard.TempWorkspace.init(io, allocator, "release_planning_index");
    defer tmp.deinit();

    var lines: std.ArrayList(u8) = .empty;
    defer lines.deinit(allocator);
    try lines.appendSlice(allocator, "# Release Planning Index\n\n");
    for (REQUIRED_MARKERS) |marker| {
        try lines.appendSlice(allocator, marker);
        try lines.append(allocator, '\n');
    }
    for (REQUIRED_DOCS) |relpath| {
        try lines.appendSlice(allocator, relpath);
        try lines.append(allocator, '\n');
    }
    try tmp.write(index_rel, lines.items);

    for (REQUIRED_DOCS) |relpath| {
        try tmp.write(relpath, "ok\n");
    }

    const root = try tmp.rootPath(allocator);
    defer allocator.free(root);

    var issues: std.ArrayList([]const u8) = .empty;
    defer {
        for (issues.items) |issue| allocator.free(issue);
        issues.deinit(allocator);
    }
    try collectIssues(io, allocator, root, &issues);
    try guard.expectSelfTest(issues.items.len == 0);

    const first_doc = REQUIRED_DOCS[0];
    const first_doc_path = try std.fmt.allocPrint(allocator, ".zig-cache/tmp/{s}/{s}", .{ tmp.sub_path, first_doc });
    defer allocator.free(first_doc_path);
    try guard.deleteFile(io, first_doc_path);

    issues.clearRetainingCapacity();
    try collectIssues(io, allocator, root, &issues);
    const expected_issue = try std.fmt.allocPrint(allocator, "missing_support_file:{s}", .{first_doc});
    defer allocator.free(expected_issue);
    var found = false;
    for (issues.items) |issue| {
        if (std.mem.eql(u8, issue, expected_issue)) found = true;
    }
    try guard.expectSelfTest(found);

    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(init.arena.allocator());

    var self_test = false;
    for (args[1..]) |arg| {
        if (std.mem.eql(u8, arg, "--self-test")) self_test = true;
    }

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    const root = try guard.repoRootFromScript(allocator);
    defer allocator.free(root);

    var issues: std.ArrayList([]const u8) = .empty;
    defer {
        for (issues.items) |issue| allocator.free(issue);
        issues.deinit(allocator);
    }
    try collectIssues(io, allocator, root, &issues);

    if (issues.items.len != 0) {
        try guard.printLine(io, "{s}", .{fail_marker});
        for (issues.items) |issue| try guard.printLine(io, "{s}", .{issue});
        std.process.exit(1);
    }

    try guard.printLine(io, "{s}", .{pass_marker});
}