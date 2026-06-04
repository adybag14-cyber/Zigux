const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const RequiredPath = struct {
    path: []const u8,
    reason: []const u8,
};

const required_pr_paths = [_]RequiredPath{
    .{ .path = "      - 'scripts/zigux/**'\n", .reason = "Lane 05 checker and installer scripts must trigger bootstrap on pull requests" },
    .{ .path = "      - 'third_party/**'\n", .reason = "trusted archive and archive parts packets must trigger bootstrap on pull requests" },
    .{ .path = "      - 'zigux/**'\n", .reason = "shared Zigux build/test roots must trigger bootstrap on pull requests" },
    .{ .path = "      - '.github/workflows/zigux-bootstrap.yml'\n", .reason = "bootstrap workflow edits must self-trigger on pull requests" },
};

fn requireContains(haystack: []const u8, needle: []const u8, reason: []const u8) !void {
    _ = reason;
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        return error.MissingWorkflowMarker;
    }
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8, reason: []const u8) !void {
    _ = reason;
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse {
        return error.MissingWorkflowMarker;
    };
    const later_index = std.mem.indexOf(u8, haystack, later) orelse {
        return error.MissingWorkflowMarker;
    };
    if (earlier_index >= later_index) {
        return error.WorkflowMarkerOrderDrifted;
    }
}

pub fn checkWorkflowTriggers(workflow: []const u8) !void {
    try requireContains(
        workflow,
        "name: zigux-bootstrap\n",
        "the contract is scoped to the bootstrap workflow",
    );
    try requireContains(
        workflow,
        "  push:\n    branches: [ master ]\n",
        "exact-head bootstrap status must attach to every master push",
    );
    try requireContains(
        workflow,
        "  pull_request:\n    paths:\n",
        "pull requests should remain path-filtered instead of silently disabling bootstrap",
    );
    try requireContains(
        workflow,
        "  workflow_dispatch:\n",
        "manual reruns are needed while CI viability is being repaired",
    );
    try requireContains(
        workflow,
        "permissions:\n  contents: read\n",
        "the bootstrap workflow should stay read-only at repository contents scope",
    );
    try requireContains(
        workflow,
        "  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}\n",
        "master exact-head runs must not cancel each other while pull request runs can collapse stale heads",
    );

    for (required_pr_paths) |required| {
        try requireContains(workflow, required.path, required.reason);
    }
}

pub fn checkWorkflowOrdering(workflow: []const u8) !void {
    try requireBefore(
        workflow,
        "  push:\n    branches: [ master ]\n",
        "  pull_request:\n    paths:\n",
        "master push coverage should stay outside the pull-request path filter",
    );
    try requireBefore(
        workflow,
        "  pull_request:\n    paths:\n",
        "  workflow_dispatch:\n",
        "manual dispatch should remain a separate trigger after the pull-request filter",
    );
    try requireBefore(
        workflow,
        "      - 'third_party/**'\n",
        "      - '.github/workflows/zigux-bootstrap.yml'\n",
        "Lane 05 payload paths should be visible in the main pull-request path packet before the self-workflow guard",
    );
    try requireBefore(
        workflow,
        "concurrency:\n",
        "jobs:\n",
        "concurrency policy must apply before any bootstrap job starts",
    );
}

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

test "Lane 05 bootstrap workflow keeps trigger and permission viability markers" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try checkWorkflowTriggers(workflow);
}

test "Lane 05 bootstrap workflow keeps trigger ordering viable" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try checkWorkflowOrdering(workflow);
}

test "Lane 05 trigger contract rejects missing trusted archive pull-request path" {
    const broken =
        \\name: zigux-bootstrap
        \\
        \\on:
        \\  push:
        \\    branches: [ master ]
        \\  pull_request:
        \\    paths:
        \\      - 'scripts/zigux/**'
        \\      - 'zigux/**'
        \\      - '.github/workflows/zigux-bootstrap.yml'
        \\  workflow_dispatch:
        \\
        \\permissions:
        \\  contents: read
        \\
        \\concurrency:
        \\  group: ${{ github.workflow }}
        \\  cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}
        \\
        \\jobs:
        \\  bootstrap:
        \\
    ;

    try std.testing.expectError(error.MissingWorkflowMarker, checkWorkflowTriggers(broken));
}

test "Lane 05 trigger contract rejects master cancellation drift" {
    const broken =
        \\name: zigux-bootstrap
        \\
        \\on:
        \\  push:
        \\    branches: [ master ]
        \\  pull_request:
        \\    paths:
        \\      - 'scripts/zigux/**'
        \\      - 'third_party/**'
        \\      - 'zigux/**'
        \\      - '.github/workflows/zigux-bootstrap.yml'
        \\  workflow_dispatch:
        \\
        \\permissions:
        \\  contents: read
        \\
        \\concurrency:
        \\  group: ${{ github.workflow }}
        \\  cancel-in-progress: true
        \\
        \\jobs:
        \\  bootstrap:
        \\
    ;

    try std.testing.expectError(error.MissingWorkflowMarker, checkWorkflowTriggers(broken));
}
