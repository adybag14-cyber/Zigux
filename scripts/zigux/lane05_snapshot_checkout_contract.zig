const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) == null) {
        return error.MissingWorkflowMarker;
    }
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) != null) {
        return error.ForbiddenWorkflowMarker;
    }
}

fn requireOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingWorkflowMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingWorkflowMarker;
    if (earlier_index >= later_index) {
        return error.WorkflowMarkerOrderDrifted;
    }
}

pub fn checkSnapshotCheckout(workflow: []const u8) !void {
    try requireContains(workflow, "      - name: Checkout workspace snapshot\n");
    try requireContains(workflow, "          set -euxo pipefail\n");
    try requireContains(workflow, "          tmpdir=\"$(mktemp -d)\"\n");
    try requireContains(workflow, "          archive=\"$tmpdir/source.tar.gz\"\n");
    try requireContains(
        workflow,
        "          curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\" -o \"$archive\"\n",
    );
    try requireContains(workflow, "          tar -xzf \"$archive\" -C \"$tmpdir\"\n");
    try requireContains(
        workflow,
        "          src_dir=\"$(find \"$tmpdir\" -mindepth 1 -maxdepth 1 -type d | head -n 1)\"\n",
    );
    try requireContains(
        workflow,
        "          find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +\n",
    );
    try requireContains(workflow, "          shopt -s dotglob\n");
    try requireContains(workflow, "          mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/\n");
    try requireAbsent(workflow, "uses: actions/checkout@");
}

pub fn checkSnapshotOrdering(workflow: []const u8) !void {
    try requireOrder(workflow, "      - name: Checkout workspace snapshot\n", "      - name: Setup Python\n");
    try requireOrder(workflow, "          tmpdir=\"$(mktemp -d)\"\n", "          archive=\"$tmpdir/source.tar.gz\"\n");
    try requireOrder(workflow, "          archive=\"$tmpdir/source.tar.gz\"\n", "          curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\" -o \"$archive\"\n");
    try requireOrder(workflow, "          curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\" -o \"$archive\"\n", "          tar -xzf \"$archive\" -C \"$tmpdir\"\n");
    try requireOrder(workflow, "          tar -xzf \"$archive\" -C \"$tmpdir\"\n", "          src_dir=\"$(find \"$tmpdir\" -mindepth 1 -maxdepth 1 -type d | head -n 1)\"\n");
    try requireOrder(workflow, "          src_dir=\"$(find \"$tmpdir\" -mindepth 1 -maxdepth 1 -type d | head -n 1)\"\n", "          find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +\n");
    try requireOrder(workflow, "          find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +\n", "          shopt -s dotglob\n");
    try requireOrder(workflow, "          shopt -s dotglob\n", "          mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/\n");
}

test "Lane 05 bootstrap uses codeload snapshot checkout instead of checkout action" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try checkSnapshotCheckout(workflow);
}

test "Lane 05 snapshot checkout keeps acquisition and workspace replacement order" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try checkSnapshotOrdering(workflow);
}

test "Lane 05 snapshot checkout rejects checkout action regression" {
    const broken =
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Checkout
        \\        uses: actions/checkout@v6.0.2
        \\      - name: Setup Python
        \\
    ;

    try std.testing.expectError(error.MissingWorkflowMarker, checkSnapshotCheckout(broken));
}

test "Lane 05 snapshot checkout rejects workspace replacement before extraction" {
    const broken =
        \\jobs:
        \\  bootstrap:
        \\    steps:
        \\      - name: Checkout workspace snapshot
        \\        run: |
        \\          set -euxo pipefail
        \\          tmpdir="$(mktemp -d)"
        \\          archive="$tmpdir/source.tar.gz"
        \\          curl -L --fail "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}" -o "$archive"
        \\          src_dir="$(find "$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
        \\          find "$GITHUB_WORKSPACE" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
        \\          tar -xzf "$archive" -C "$tmpdir"
        \\          shopt -s dotglob
        \\          mv "$src_dir"/* "$GITHUB_WORKSPACE"/
        \\      - name: Setup Python
        \\
    ;

    try checkSnapshotCheckout(broken);
    try std.testing.expectError(error.WorkflowMarkerOrderDrifted, checkSnapshotOrdering(broken));
}
