const std = @import("std");
const archive_parts_contract_inputs = @import("archive_parts_contract_inputs");

fn readRepoFile(path: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn requireContains(text: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, text, needle) != null);
}

fn requireExactLine(text: []const u8, line: []const u8) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |current| {
        if (std.mem.eql(u8, std.mem.trim(u8, current, " \t\r"), line)) {
            count += 1;
        }
    }

    try std.testing.expectEqual(@as(usize, 1), count);
}

fn requireOrder(text: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, text, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, text, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn exactLineIndex(text: []const u8, line: []const u8) !usize {
    var byte_index: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |current| {
        if (std.mem.eql(u8, std.mem.trim(u8, current, " \t\r"), line)) {
            return byte_index;
        }
        byte_index += current.len + 1;
    }
    return error.MissingLine;
}

fn requireExactLineOrder(text: []const u8, earlier: []const u8, later: []const u8) !void {
    try std.testing.expect(try exactLineIndex(text, earlier) < try exactLineIndex(text, later));
}

test "Lane 05 archive-parts workflow keeps the bootstrap packet guard route" {
    const workflow_text = try readRepoFile(archive_parts_contract_inputs.workflow_path);
    defer std.testing.allocator.free(workflow_text);

    const ordered_path_filters = [_][]const u8{
        "- 'scripts/zigux/check-lane05-archive-parts-workflow.py'",
        "- 'scripts/zigux/check-lane05-archive-parts-packet.py'",
        "- 'scripts/zigux/zig-toolchain-policy.json'",
        "- 'third_party/**'",
        "- '.github/workflows/zigux-bootstrap-archive-parts-packet.yml'",
    };
    const ordered_steps = [_][]const u8{
        "- name: Checkout workspace snapshot",
        "- name: Setup Python",
        "- name: Compile current Lane 05 archive-parts workflow scripts",
        "- name: Self-test current Lane 05 archive-parts workflow checker",
        "- name: Check current Lane 05 archive-parts workflow packet",
        "- name: Self-test current Lane 05 archive parts packet checker",
        "- name: Check current Lane 05 archive parts packet",
    };

    try requireExactLine(workflow_text, "name: zigux-bootstrap-archive-parts-packet");
    try requireExactLine(workflow_text, "branches: [ master ]");
    try requireExactLine(workflow_text, "contents: read");
    try requireContains(workflow_text, "curl -L --fail \"https://codeload.github.com/${GITHUB_REPOSITORY}/tar.gz/${GITHUB_SHA}\" -o \"$archive\"");

    for (ordered_path_filters) |path_filter| {
        try requireExactLine(workflow_text, path_filter);
    }
    for (ordered_steps) |step| {
        try requireExactLine(workflow_text, step);
    }

    for (ordered_path_filters[0 .. ordered_path_filters.len - 1], ordered_path_filters[1..]) |earlier, later| {
        try requireOrder(workflow_text, earlier, later);
    }
    for (ordered_steps[0 .. ordered_steps.len - 1], ordered_steps[1..]) |earlier, later| {
        try requireOrder(workflow_text, earlier, later);
    }
}

test "Lane 05 archive-parts workflow runs both checker self-tests before the allow-missing payload check" {
    const workflow_text = try readRepoFile(archive_parts_contract_inputs.workflow_path);
    defer std.testing.allocator.free(workflow_text);

    const compile_cmd = "run: python3 -m py_compile scripts/zigux/check-zig-toolchain.py scripts/zigux/check-lane05-archive-parts-packet.py scripts/zigux/check-lane05-archive-parts-workflow.py";
    const workflow_self_test_cmd = "run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py --self-test";
    const workflow_check_cmd = "run: python3 scripts/zigux/check-lane05-archive-parts-workflow.py";
    const packet_self_test_cmd = "run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --self-test";
    const packet_check_cmd = "run: python3 scripts/zigux/check-lane05-archive-parts-packet.py --allow-missing";

    try requireExactLine(workflow_text, compile_cmd);
    try requireExactLine(workflow_text, workflow_self_test_cmd);
    try requireExactLine(workflow_text, workflow_check_cmd);
    try requireExactLine(workflow_text, packet_self_test_cmd);
    try requireExactLine(workflow_text, packet_check_cmd);

    try requireExactLineOrder(workflow_text, compile_cmd, workflow_self_test_cmd);
    try requireExactLineOrder(workflow_text, workflow_self_test_cmd, workflow_check_cmd);
    try requireExactLineOrder(workflow_text, workflow_check_cmd, packet_self_test_cmd);
    try requireExactLineOrder(workflow_text, packet_self_test_cmd, packet_check_cmd);
}
