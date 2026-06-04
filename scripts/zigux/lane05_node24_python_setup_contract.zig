const std = @import("std");
const testing = std.testing;

const build_options = @import("build_options");
const workflow = build_options.workflow_text;

fn requireContains(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn requireBefore(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = try requireContains(haystack, before);
    const after_index = try requireContains(haystack, after);
    try testing.expect(before_index < after_index);
}

test "bootstrap workflow forces JavaScript actions onto Node 24" {
    _ = try requireContains(workflow, "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true");
    try requireBefore(workflow, "env:\n  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true", "jobs:\n  bootstrap:");
}

test "bootstrap workflow keeps setup-python on the Node 24 compatible action" {
    _ = try requireContains(workflow, "- name: Setup Python");
    _ = try requireContains(workflow, "uses: actions/setup-python@v6.2.0");
    _ = try requireContains(workflow, "python-version: '3.x'");
}

test "setup-python stays between snapshot checkout and pinned Zig setup" {
    try requireBefore(workflow, "- name: Checkout workspace snapshot", "- name: Setup Python");
    try requireBefore(workflow, "- name: Setup Python", "- name: Setup pinned Zig toolchain");
}

test "Python setup precedes script compilation checks" {
    try requireBefore(workflow, "- name: Setup Python", "- name: Compile current scripts");
    try requireBefore(workflow, "uses: actions/setup-python@v6.2.0", "python3 -m py_compile");
}
