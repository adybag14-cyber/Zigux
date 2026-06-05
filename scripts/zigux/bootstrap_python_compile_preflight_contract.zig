const std = @import("std");

const allocator = std.testing.allocator;

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(1024 * 1024));
}

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

test "workflow keeps Python compile preflight exact and fail closed" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try requireContains(workflow, "- name: Compile current scripts");
    try requireContains(workflow, "set -euxo pipefail");
    try requireContains(workflow, "mapfile -t scripts < <(find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort)");
    try requireContains(workflow, "if [ \"${#scripts[@]}\" -eq 0 ]; then");
    try requireContains(workflow, "echo 'no Python scripts found under scripts/zigux' >&2");
    try requireContains(workflow, "python3 -m py_compile \"${scripts[@]}\"");
}

test "compile preflight stays after setup and before checker handoff" {
    const workflow = try readRepoFile(".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try requireBefore(workflow, "- name: Setup Python", "- name: Compile current scripts");
    try requireBefore(workflow, "- name: Setup pinned Zig toolchain", "- name: Compile current scripts");
    try requireBefore(workflow, "- name: Compile current scripts", "- name: Self-test current Zig toolchain checker");
    try requireBefore(workflow, "- name: Compile current scripts", "- name: Self-test current bootstrap validator");
    try requireBefore(workflow, "- name: Self-test current bootstrap validator", "- name: Validate current bootstrap packet");
}

test "compile preflight is tied to bootstrap validator tail" {
    const validator = try readRepoFile("scripts/zigux/validate-bootstrap.py");
    defer allocator.free(validator);

    try requireContains(validator, "\"run: python3 scripts/zigux/check-zig-toolchain.py --self-test\"");
    try requireContains(validator, "\"run: python3 scripts/zigux/validate-bootstrap.py --self-test\"");
    try requireContains(validator, "\"run: python3 scripts/zigux/validate-bootstrap.py\"");
    try requireContains(validator, "BOOTSTRAP_WORKFLOW_LINE_COUNT");
}
