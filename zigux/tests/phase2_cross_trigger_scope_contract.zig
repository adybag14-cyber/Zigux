const std = @import("std");
const testing = std.testing;

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, haystack, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, haystack, second) orelse return error.MissingSecondMarker;
    try testing.expect(first_index < second_index);
}

fn afterMarker(haystack: []const u8, marker: []const u8) ![]const u8 {
    const index = std.mem.indexOf(u8, haystack, marker) orelse return error.MissingMarker;
    return haystack[index + marker.len ..];
}

fn exactLineCount(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    return count;
}

fn occurrenceCount(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOf(u8, haystack[cursor..], needle)) |offset| {
        count += 1;
        cursor += offset + needle.len;
    }
    return count;
}

test "workflow keeps always-on master and manual triggers" {
    const workflow = try readWorkflow(testing.allocator);
    defer testing.allocator.free(workflow);

    try expectContains(workflow, "on:\n");
    try expectContains(workflow, "  push:\n");
    try expectContains(workflow, "    branches: [ master ]\n");
    try expectContains(workflow, "  pull_request:\n");
    try expectContains(workflow, "  workflow_dispatch:\n");
    try expectOrdered(workflow, "  push:\n", "  pull_request:\n");
    try expectOrdered(workflow, "  pull_request:\n", "  workflow_dispatch:\n");
}

test "pull request path filters cover direct cross packet surfaces" {
    const workflow = try readWorkflow(testing.allocator);
    defer testing.allocator.free(workflow);
    const pull_request_block = try afterMarker(workflow, "  pull_request:\n");

    try expectContains(pull_request_block, "    paths:\n");
    try expectContains(pull_request_block, "      - 'scripts/zigux/**'\n");
    try expectContains(pull_request_block, "      - 'zigux/**'\n");
    try expectContains(pull_request_block, "      - '.github/workflows/zigux-bootstrap.yml'\n");

    try expectOrdered(pull_request_block, "    paths:\n", "      - 'scripts/zigux/**'\n");
    try expectOrdered(pull_request_block, "    paths:\n", "      - 'zigux/**'\n");
    try expectOrdered(pull_request_block, "    paths:\n", "      - '.github/workflows/zigux-bootstrap.yml'\n");
}

test "workflow still runs the direct cross checks inside triggered bootstrap" {
    const workflow = try readWorkflow(testing.allocator);
    defer testing.allocator.free(workflow);

    const direct_self_test = "run: python3 scripts/zigux/check-phase2-cross.py --self-test";
    const direct_check = "python3 scripts/zigux/check-phase2-cross.py";
    const alignment_self_test = "run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test";
    const alignment_check = "python3 scripts/zigux/check-phase2-cross-selftest-alignment.py";

    try testing.expectEqual(@as(usize, 1), exactLineCount(workflow, direct_self_test));
    try testing.expect(occurrenceCount(workflow, direct_check) >= 2);
    try testing.expectEqual(@as(usize, 1), exactLineCount(workflow, alignment_self_test));
    try testing.expect(occurrenceCount(workflow, alignment_check) >= 2);
    try expectOrdered(workflow, direct_self_test, direct_check);
    try expectOrdered(workflow, direct_check, alignment_self_test);
    try expectOrdered(workflow, alignment_self_test, alignment_check);
}
