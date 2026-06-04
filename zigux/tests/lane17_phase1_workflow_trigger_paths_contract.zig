const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const required_pull_request_paths = [_][]const u8{
    "- 'Documentation/zigux/**'",
    "- 'scripts/zigux/**'",
    "- 'tools/lib/*.zig'",
    "- 'tools/lib/**/*.zig'",
    "- 'zigux/**'",
    "- 'include/linux/zigux.h'",
    "- 'include/zigux/**'",
    "- '.github/workflows/zigux-bootstrap.yml'",
};

const required_master_push_markers = [_][]const u8{
    "push:",
    "branches: [ master ]",
};

const stale_narrow_paths = [_][]const u8{
    "- 'zigux/tests/**'",
    "- 'scripts/zigux/*.py'",
    "- 'tools/lib/bitmap.zig'",
};

fn countTrimmedLines(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    return count;
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |match| {
        count += 1;
        index = match + needle.len;
    }
    return count;
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireTrimmedLineOnce(haystack: []const u8, line: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countTrimmedLines(haystack, line));
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(haystack, needle));
}

fn pullRequestBlock(workflow: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, workflow, "\n  pull_request:") orelse
        return error.MissingPullRequestTrigger;
    const rest = workflow[start + 1 ..];
    const end = std.mem.indexOf(u8, rest, "\n  workflow_dispatch:") orelse
        return error.MissingWorkflowDispatchBoundary;
    return rest[0..end];
}

fn requireWorkflowTriggers(workflow: []const u8) !void {
    for (required_master_push_markers) |marker| {
        try requireContains(workflow, marker);
    }

    const pr_block = try pullRequestBlock(workflow);
    try requireContains(pr_block, "paths:");
    for (required_pull_request_paths) |path| {
        try requireTrimmedLineOnce(pr_block, path);
    }
    for (stale_narrow_paths) |path| {
        try requireAbsent(pr_block, path);
    }
}

fn loadWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

const current_trigger_sample =
    \\on:
    \\  push:
    \\    branches: [ master ]
    \\  pull_request:
    \\    paths:
    \\      - 'lib/**'
    \\      - 'Documentation/zigux/**'
    \\      - 'scripts/zigux/**'
    \\      - 'tools/lib/*.zig'
    \\      - 'tools/lib/**/*.zig'
    \\      - 'zigux/**'
    \\      - 'include/linux/zigux.h'
    \\      - 'include/zigux/**'
    \\      - '.github/workflows/zigux-bootstrap.yml'
    \\  workflow_dispatch:
;

test "lane17 workflow trigger paths keep Phase 1 sources in pull_request coverage" {
    const workflow = try loadWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireWorkflowTriggers(workflow);
}

test "lane17 workflow trigger contract accepts the current Phase 1 trigger shape" {
    try requireWorkflowTriggers(current_trigger_sample);
}

test "lane17 workflow trigger contract rejects missing script coverage" {
    const missing_scripts =
        \\on:
        \\  push:
        \\    branches: [ master ]
        \\  pull_request:
        \\    paths:
        \\      - 'Documentation/zigux/**'
        \\      - 'tools/lib/*.zig'
        \\      - 'tools/lib/**/*.zig'
        \\      - 'zigux/**'
        \\      - 'include/linux/zigux.h'
        \\      - 'include/zigux/**'
        \\      - '.github/workflows/zigux-bootstrap.yml'
        \\  workflow_dispatch:
    ;
    try std.testing.expectError(error.TestExpectedEqual, requireWorkflowTriggers(missing_scripts));
}

test "lane17 workflow trigger contract rejects duplicate broad Zigux coverage" {
    const duplicate_zigux =
        \\on:
        \\  push:
        \\    branches: [ master ]
        \\  pull_request:
        \\    paths:
        \\      - 'Documentation/zigux/**'
        \\      - 'scripts/zigux/**'
        \\      - 'tools/lib/*.zig'
        \\      - 'tools/lib/**/*.zig'
        \\      - 'zigux/**'
        \\      - 'zigux/**'
        \\      - 'include/linux/zigux.h'
        \\      - 'include/zigux/**'
        \\      - '.github/workflows/zigux-bootstrap.yml'
        \\  workflow_dispatch:
    ;
    try std.testing.expectError(error.TestExpectedEqual, requireWorkflowTriggers(duplicate_zigux));
}

test "lane17 workflow trigger contract rejects stale narrow Phase 1 path filters" {
    const stale_narrow =
        \\on:
        \\  push:
        \\    branches: [ master ]
        \\  pull_request:
        \\    paths:
        \\      - 'Documentation/zigux/**'
        \\      - 'scripts/zigux/**'
        \\      - 'tools/lib/*.zig'
        \\      - 'tools/lib/**/*.zig'
        \\      - 'zigux/**'
        \\      - 'zigux/tests/**'
        \\      - 'include/linux/zigux.h'
        \\      - 'include/zigux/**'
        \\      - '.github/workflows/zigux-bootstrap.yml'
        \\  workflow_dispatch:
    ;
    try std.testing.expectError(error.TestExpectedEqual, requireWorkflowTriggers(stale_narrow));
}
