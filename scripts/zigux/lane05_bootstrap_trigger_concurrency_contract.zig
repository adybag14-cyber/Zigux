const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const ContractError = error{
    MissingMarker,
    DuplicateMarker,
    OutOfOrderMarker,
};

const required_markers = [_][]const u8{
    "name: zigux-bootstrap",
    "  push:",
    "    branches: [ master ]",
    "  pull_request:",
    "  workflow_dispatch:",
    "permissions:",
    "  contents: read",
    "concurrency:",
    "  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}",
    "  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}",
};

const required_pr_paths = [_][]const u8{
    "      - 'scripts/zigux/**'",
    "      - 'third_party/**'",
    "      - 'tools/lib/*.zig'",
    "      - 'tools/lib/**/*.zig'",
    "      - 'zigux/**'",
    "      - 'include/linux/zigux.h'",
    "      - 'include/zigux/**'",
    "      - '.github/workflows/zigux-bootstrap.yml'",
};

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const workflow = try std.fs.cwd().readFileAlloc(allocator, workflow_path, 1024 * 1024);
    defer allocator.free(workflow);

    try validateWorkflowPolicy(workflow);
}

fn validateWorkflowPolicy(workflow: []const u8) ContractError!void {
    for (required_markers) |marker| {
        _ = try requireLineExactlyOnce(workflow, marker);
    }
    for (required_pr_paths) |marker| {
        _ = try requireLineExactlyOnce(workflow, marker);
    }

    try requireOrder(workflow, "on:", "  push:");
    try requireOrder(workflow, "  push:", "  pull_request:");
    try requireOrder(workflow, "  pull_request:", "  workflow_dispatch:");
    try requireOrder(workflow, "  workflow_dispatch:", "permissions:");
    try requireOrder(workflow, "permissions:", "concurrency:");
    try requireOrder(workflow, "concurrency:", "jobs:");
    try requireOrder(workflow, "  pull_request:", "    paths:");
    try requireOrder(workflow, "    paths:", "      - 'scripts/zigux/**'");
    try requireOrder(workflow, "      - 'scripts/zigux/**'", "      - 'third_party/**'");
    try requireOrder(workflow, "      - 'third_party/**'", "      - 'zigux/**'");
    try requireOrder(workflow, "      - 'zigux/**'", "      - '.github/workflows/zigux-bootstrap.yml'");
}

fn requireLineExactlyOnce(haystack: []const u8, needle: []const u8) ContractError!usize {
    const normalized_needle = std.mem.trim(u8, needle, " \t\r");
    var first_index: ?usize = null;
    var offset: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        const trimmed = std.mem.trim(u8, line, " \t\r");
        if (std.mem.eql(u8, trimmed, normalized_needle)) {
            if (first_index != null) return error.DuplicateMarker;
            first_index = offset;
        }
        offset += line.len + 1;
    }
    return first_index orelse error.MissingMarker;
}

fn requireOrder(haystack: []const u8, earlier: []const u8, later: []const u8) ContractError!void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingMarker;
    if (earlier_index >= later_index) return error.OutOfOrderMarker;
}

test "accepts current bootstrap trigger and concurrency policy" {
    try validateWorkflowPolicy(current_workflow);
}

test "rejects missing master push trigger" {
    const stale = replace(current_workflow, "    branches: [ master ]", "    branches: [ main ]");
    defer std.testing.allocator.free(stale);
    try std.testing.expectError(error.MissingMarker, validateWorkflowPolicy(stale));
}

test "rejects pull request filter that drops third party archive changes" {
    const stale = replace(current_workflow, "      - 'third_party/**'", "      - 'third-party/**'");
    defer std.testing.allocator.free(stale);
    try std.testing.expectError(error.MissingMarker, validateWorkflowPolicy(stale));
}

test "rejects master cancellation regression" {
    const stale = replace(
        current_workflow,
        "  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}",
        "  cancel-in-progress: true",
    );
    defer std.testing.allocator.free(stale);
    try std.testing.expectError(error.MissingMarker, validateWorkflowPolicy(stale));
}

test "rejects branch-ref grouping for master runs" {
    const stale = replace(
        current_workflow,
        "  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}",
        "  group: ${{ format('{0}-{1}', github.workflow, github.ref) }}",
    );
    defer std.testing.allocator.free(stale);
    try std.testing.expectError(error.MissingMarker, validateWorkflowPolicy(stale));
}

test "rejects duplicate workflow path trigger" {
    const stale = current_workflow ++
        \\      - '.github/workflows/zigux-bootstrap.yml'
        \\
    ;
    try std.testing.expectError(error.DuplicateMarker, validateWorkflowPolicy(stale));
}

fn replace(source: []const u8, needle: []const u8, replacement: []const u8) []u8 {
    return std.mem.replaceOwned(u8, std.testing.allocator, source, needle, replacement) catch unreachable;
}

const current_workflow =
    \\name: zigux-bootstrap
    \\# Keep this lane tied to files that the current checkout actually contains.
    \\# Run every master push so exact-head bootstrap status stays attached even when path filtering misses a live change.
    \\
    \\on:
    \\  push:
    \\    branches: [ master ]
    \\  pull_request:
    \\    paths:
    \\      - 'lib/**'
    \\      - 'zigux-alpha/**'
    \\      - 'Documentation/zigux/**'
    \\      - 'samples/zigux/**'
    \\      - 'kernel/**/*.zig'
    \\      - 'net/**/*.zig'
    \\      - 'drivers/**/*.zig'
    \\      - 'scripts/basic/fixdep.c'
    \\      - 'scripts/include/xalloc.h'
    \\      - 'scripts/kconfig/conf.c'
    \\      - 'scripts/kconfig/confdata.c'
    \\      - 'scripts/zigux/**'
    \\      - 'third_party/**'
    \\      - 'tools/lib/*.zig'
    \\      - 'tools/lib/**/*.zig'
    \\      - 'tools/lib/subcmd/exec-cmd.c'
    \\      - 'tools/lib/subcmd/help.c'
    \\      - 'tools/lib/symbol/kallsyms.c'
    \\      - 'zigux/**'
    \\      - 'include/linux/zigux.h'
    \\      - 'include/zigux/**'
    \\      - '.github/workflows/zigux-bootstrap.yml'
    \\  workflow_dispatch:
    \\
    \\permissions:
    \\  contents: read
    \\
    \\env:
    \\  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
    \\
    \\concurrency:
    \\  group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}
    \\  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}
    \\
    \\jobs:
    \\  bootstrap:
    \\    runs-on: ubuntu-latest
    \\
;