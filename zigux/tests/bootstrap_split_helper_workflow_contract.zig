const std = @import("std");
const testing = std.testing;

const workflow_paths = [_][]const u8{
    ".github/workflows/zigux-bootstrap-split-helper.yml",
    "../../.github/workflows/zigux-bootstrap-split-helper.yml",
};

const checker_paths = [_][]const u8{
    "scripts/zigux/check-lane05-split-helper-workflow.py",
    "../../scripts/zigux/check-lane05-split-helper-workflow.py",
};

fn readFirstExisting(allocator: std.mem.Allocator, paths: []const []const u8) ![]u8 {
    var last_error: anyerror = error.FileNotFound;
    for (paths) |path| {
        return std.Io.Dir.cwd().readFileAlloc(testing.io, path, allocator, .limited(1024 * 1024)) catch |err| {
            last_error = err;
            continue;
        };
    }
    return last_error;
}

fn requireContains(text: []const u8, marker: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, text, marker) != null);
}

fn requireOrdered(text: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return error.MissingLaterMarker;
    try testing.expect(earlier_index < later_index);
}

fn requireLineCount(text: []const u8, wanted: []const u8, expected: usize) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), wanted)) {
            count += 1;
        }
    }
    try testing.expectEqual(expected, count);
}

test "Lane 05 split-helper workflow keeps checkout and guard steps viable" {
    const workflow = try readFirstExisting(testing.allocator, &workflow_paths);
    defer testing.allocator.free(workflow);

    try requireContains(workflow, "name: zigux-bootstrap-split-helper");
    try requireContains(workflow, "branches: [ master ]");
    try requireContains(workflow, "permissions:\n  contents: read");
    try requireContains(workflow, "cancel-in-progress: true");

    try requireContains(workflow, "- 'scripts/zigux/**'");
    try requireContains(workflow, "- 'third_party/**'");
    try requireContains(workflow, "- '.github/workflows/zigux-bootstrap-split-helper.yml'");
    try requireOrdered(workflow, "- 'scripts/zigux/**'", "- 'third_party/**'");
    try requireOrdered(workflow, "- 'third_party/**'", "- '.github/workflows/zigux-bootstrap-split-helper.yml'");

    try requireContains(workflow, "- name: Checkout workspace snapshot");
    try requireContains(workflow, "https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}");
    try requireContains(workflow, "find \"$GITHUB_WORKSPACE\" -mindepth 1 -maxdepth 1 -exec rm -rf {} +");
    try requireContains(workflow, "mv \"$src_dir\"/* \"$GITHUB_WORKSPACE\"/");

    try requireLineCount(workflow, "- name: Setup Python", 1);
    try requireLineCount(workflow, "- name: Compile current split-helper packet scripts", 1);
    try requireLineCount(workflow, "- name: Self-test current split pinned Zig archive helper", 1);
    try requireLineCount(workflow, "- name: Self-test current Lane 05 split helper selftest checker", 1);
    try requireLineCount(workflow, "- name: Self-test current Lane 05 split-helper workflow checker", 1);
    try requireLineCount(workflow, "- name: Check current Lane 05 split-helper workflow packet", 1);

    try requireContains(workflow, "python3 -m py_compile scripts/zigux/split-pinned-zig-archive.py scripts/zigux/check-lane05-split-helper-selftest.py scripts/zigux/check-lane05-split-helper-workflow.py");
    try requireContains(workflow, "python3 scripts/zigux/split-pinned-zig-archive.py --self-test");
    try requireContains(workflow, "python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test");
    try requireContains(workflow, "python3 scripts/zigux/check-lane05-split-helper-workflow.py --self-test");
    try requireContains(workflow, "python3 scripts/zigux/check-lane05-split-helper-workflow.py");

    try requireOrdered(workflow, "- name: Checkout workspace snapshot", "- name: Setup Python");
    try requireOrdered(workflow, "- name: Setup Python", "- name: Compile current split-helper packet scripts");
    try requireOrdered(workflow, "- name: Compile current split-helper packet scripts", "- name: Self-test current split pinned Zig archive helper");
    try requireOrdered(workflow, "- name: Self-test current split pinned Zig archive helper", "- name: Self-test current Lane 05 split helper selftest checker");
    try requireOrdered(workflow, "- name: Self-test current Lane 05 split helper selftest checker", "- name: Self-test current Lane 05 split-helper workflow checker");
    try requireOrdered(workflow, "- name: Self-test current Lane 05 split-helper workflow checker", "- name: Check current Lane 05 split-helper workflow packet");
}

test "Lane 05 split-helper workflow checker protects the same packet" {
    const checker = try readFirstExisting(testing.allocator, &checker_paths);
    defer testing.allocator.free(checker);

    try requireContains(checker, "WORKFLOW_PATH = Path(\".github/workflows/zigux-bootstrap-split-helper.yml\")");
    try requireContains(checker, "WORKFLOW_NAME = \"name: zigux-bootstrap-split-helper\"");
    try requireContains(checker, "SCRIPTS_PATH = \"- 'scripts/zigux/**'\"");
    try requireContains(checker, "THIRD_PARTY_PATH = \"- 'third_party/**'\"");
    try requireContains(checker, "WORKFLOW_PATH_FILTER = \"- '.github/workflows/zigux-bootstrap-split-helper.yml'\"");
    try requireContains(checker, "COMPILE_STEP = \"- name: Compile current split-helper packet scripts\"");
    try requireContains(checker, "HELPER_SELF_TEST_CMD = \"python3 scripts/zigux/split-pinned-zig-archive.py --self-test\"");
    try requireContains(checker, "SELFTEST_CHECKER_CMD = \"python3 scripts/zigux/check-lane05-split-helper-selftest.py --self-test\"");
    try requireContains(checker, "WORKFLOW_CHECKER_SELF_TEST_CMD =");
    try requireContains(checker, "WORKFLOW_CHECKER_CMD = \"python3 scripts/zigux/check-lane05-split-helper-workflow.py\"");

    try requireContains(checker, "require_exact_line(text, line, label)");
    try requireContains(checker, "require_order(text, SCRIPTS_PATH, THIRD_PARTY_PATH, \"pull_request path order\")");
    try requireContains(checker, "require_order(text, CHECKOUT_STEP, PYTHON_STEP, \"step order\")");
    try requireContains(checker, "LANE05_SPLIT_HELPER_WORKFLOW_SELF_TEST=pass");
    try requireContains(checker, "LANE05_SPLIT_HELPER_WORKFLOW=pass");
}
