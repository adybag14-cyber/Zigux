const std = @import("std");

const pinned_workflow_lines = [_][]const u8{
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
};

const lane05_handoff_line = "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test";

fn pythonTupleEntry(line: []const u8) []const u8 {
    return std.fmt.allocPrint(std.testing.allocator, "\"{s}\",", .{line}) catch unreachable;
}

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |index| {
        count += 1;
        offset = index + needle.len;
    }
    return count;
}

fn requireOrderedAfter(haystack: []const u8, previous: usize, needle: []const u8) !usize {
    const index = std.mem.indexOfPos(u8, haystack, previous, needle) orelse return error.MarkerMissing;
    try std.testing.expect(index >= previous);
    return index + needle.len;
}

test "pinned Zig workflow roster is present once and ordered before Lane 05 handoff" {
    const allocator = std.testing.allocator;
    const source = @embedFile("validate-bootstrap.py");

    try std.testing.expect(std.mem.indexOf(u8, source, "REQUIRED_WORKFLOW_LINES = (") != null);

    var cursor = std.mem.indexOf(u8, source, "REQUIRED_WORKFLOW_LINES = (").?;
    for (pinned_workflow_lines) |line| {
        const entry = pythonTupleEntry(line);
        defer allocator.free(entry);
        try std.testing.expectEqual(@as(usize, 1), countNeedle(source, entry));
        cursor = try requireOrderedAfter(source, cursor, entry);
    }

    const lane05_entry = pythonTupleEntry(lane05_handoff_line);
    defer allocator.free(lane05_entry);
    const lane05_index = std.mem.indexOf(u8, source, lane05_entry) orelse return error.MarkerMissing;
    try std.testing.expect(lane05_index > cursor);
}

test "self-test fixture seeds the same pinned setup ladder" {
    const source = @embedFile("validate-bootstrap.py");

    try std.testing.expect(std.mem.indexOf(u8, source, "write_text(root, WORKFLOW, \"\\n\".join((\"name: zigux-bootstrap\", *REQUIRED_WORKFLOW_LINES)) + \"\\n\")") != null);
    try std.testing.expect(std.mem.indexOf(u8, source, "BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}") != null);

    for (pinned_workflow_lines) |line| {
        try std.testing.expect(std.mem.indexOf(u8, source, line) != null);
    }
}

test "duplicate archive-only workflow line remains a pinned self-test case" {
    const source = @embedFile("validate-bootstrap.py");

    try std.testing.expect(std.mem.indexOf(u8, source, "duplicate_exact_line(") != null);
    try std.testing.expect(std.mem.indexOf(u8, source, "REQUIRED_WORKFLOW_LINES[2]") != null);
    try std.testing.expect(std.mem.indexOf(u8, source, "\"DUPLICATE_WORKFLOW_LINE\"") != null);
    try std.testing.expect(std.mem.indexOf(u8, source, "f\"{REQUIRED_WORKFLOW_LINES[2]}:count=2\"") != null);
}

test "pinned toolchain files remain required bootstrap paths" {
    const source = @embedFile("validate-bootstrap.py");

    const required_paths = [_][]const u8{
        "\"scripts/zigux/check-zig-toolchain.py\",",
        "\"scripts/zigux/install-zig.py\",",
        "\"scripts/zigux/validate-bootstrap.py\",",
        "\"scripts/zigux/zig-toolchain-policy.json\",",
    };
    for (required_paths) |entry| {
        try std.testing.expectEqual(@as(usize, 1), countNeedle(source, entry));
    }
}
