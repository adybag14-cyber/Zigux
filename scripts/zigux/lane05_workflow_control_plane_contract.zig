const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readWorkflow() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) == null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn sliceBetween(haystack: []const u8, start: []const u8, end: []const u8) ![]const u8 {
    const start_index = std.mem.indexOf(u8, haystack, start) orelse return error.MissingStartMarker;
    const body_start = start_index + start.len;
    const end_index = std.mem.indexOf(u8, haystack[body_start..], end) orelse return error.MissingEndMarker;
    return haystack[body_start .. body_start + end_index];
}

test "bootstrap workflow keeps master pushes exact-head and pull request paths bounded" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    const push_block = try sliceBetween(workflow, "  push:\n", "  pull_request:\n");
    const pull_request_block = try sliceBetween(workflow, "  pull_request:\n", "  workflow_dispatch:\n");

    try expectContains(workflow, "on:\n");
    try expectContains(push_block, "branches: [ master ]");
    try expectNotContains(push_block, "paths:");
    try expectContains(pull_request_block, "paths:");
    try expectContains(pull_request_block, "      - 'third_party/**'");
    try expectContains(pull_request_block, "      - 'scripts/include/xalloc.h'");
    try expectContains(pull_request_block, "      - 'scripts/zigux/**'");
    try expectContains(pull_request_block, "      - 'zigux/**'");
    try expectContains(pull_request_block, "      - '.github/workflows/zigux-bootstrap.yml'");
    try expectOrdered(workflow, "  push:\n", "  pull_request:\n");
    try expectOrdered(workflow, "  pull_request:\n", "  workflow_dispatch:\n");
}

test "bootstrap workflow control plane stays least-privilege and master-safe" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "permissions:\n  contents: read");
    try expectContains(workflow, "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true");
    try expectContains(
        workflow,
        "group: ${{ github.ref == 'refs/heads/master' && format('{0}-{1}', github.workflow, github.sha) || format('{0}-{1}', github.workflow, github.ref) }}",
    );
    try expectContains(workflow, "cancel-in-progress: ${{ github.ref != 'refs/heads/master' }}");
    try expectOrdered(workflow, "permissions:\n", "env:\n");
    try expectOrdered(workflow, "env:\n", "concurrency:\n");
    try expectOrdered(workflow, "concurrency:\n", "jobs:\n");
}

test "bootstrap workflow uses codeload snapshot checkout before setup" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "- name: Checkout workspace snapshot");
    try expectContains(workflow, "curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\" -o \"$archive\"");
    try expectContains(workflow, "tar -xzf \"$archive\" -C \"$tmpdir\"");
    try expectContains(workflow, "find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +");
    try expectContains(workflow, "shopt -s dotglob");
    try expectContains(workflow, "mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/");
    try expectNotContains(workflow, "uses: actions/checkout");
    try expectOrdered(workflow, "- name: Checkout workspace snapshot", "- name: Setup Python");
    try expectOrdered(workflow, "- name: Setup Python", "- name: Setup pinned Zig toolchain");
}

test "bootstrap workflow validates script and toolchain surfaces before broad gates" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    try expectOrdered(workflow, "- name: Setup pinned Zig toolchain", "- name: Compile current scripts");
    try expectOrdered(workflow, "- name: Compile current scripts", "- name: Self-test current Zig toolchain checker");
    try expectOrdered(workflow, "run: python3 scripts/zigux/check-zig-toolchain.py --self-test", "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only");
    try expectOrdered(workflow, "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only", "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
    try expectOrdered(workflow, "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing", "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test");
    try expectOrdered(workflow, "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py", "run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test");
}
