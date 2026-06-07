const std = @import("std");

const required_validate_bootstrap_entries = [_][]const u8{
    "\"run: python3 scripts/zigux/check-zig-toolchain.py --self-test\"",
    "\"run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\"",
    "\"run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\"",
    "\"run: python3 scripts/zigux/validate-bootstrap.py --self-test\"",
    "\"run: python3 scripts/zigux/validate-bootstrap.py\"",
};

const required_workflow_lines = [_][]const u8{
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/validate-bootstrap.py --self-test",
    "run: python3 scripts/zigux/validate-bootstrap.py",
};

fn repoPath(comptime rel: []const u8) []const u8 {
    return rel;
}

fn readRepoFile(allocator: std.mem.Allocator, comptime rel: []const u8) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, repoPath(rel), allocator, .limited(1024 * 1024));
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectStrictOrder(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const relative = std.mem.indexOf(u8, haystack[cursor..], needle);
        try std.testing.expect(relative != null);
        cursor += relative.? + needle.len;
    }
}

fn countLinesEqual(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    return count;
}

test "bootstrap validator keeps ordered toolchain workflow requirements" {
    const allocator = std.testing.allocator;
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-bootstrap.py");
    defer allocator.free(validator);

    try expectContains(validator, "REQUIRED_WORKFLOW_LINES = (");
    try expectStrictOrder(validator, &required_validate_bootstrap_entries);
    try expectContains(validator, "\"DUPLICATE_WORKFLOW_LINE\"");
    try expectContains(validator, "BOOTSTRAP_WORKFLOW_LINE_COUNT");
}

test "workflow runs toolchain checks before bootstrap validator replay" {
    const allocator = std.testing.allocator;
    const workflow = try readRepoFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(workflow);

    try expectStrictOrder(workflow, &required_workflow_lines);
    for (required_workflow_lines) |line| {
        try std.testing.expectEqual(@as(usize, 1), countLinesEqual(workflow, line));
    }
}

test "bootstrap packet still points at the pinned toolchain policy" {
    const allocator = std.testing.allocator;
    const validator = try readRepoFile(allocator, "scripts/zigux/validate-bootstrap.py");
    defer allocator.free(validator);

    const policy = try readRepoFile(allocator, "scripts/zigux/zig-toolchain-policy.json");
    defer allocator.free(policy);

    try expectContains(validator, "\"scripts/zigux/check-zig-toolchain.py\"");
    try expectContains(validator, "\"scripts/zigux/zig-toolchain-policy.json\"");
    try expectContains(policy, "\"channel\": \"0.17.0-dev.758+748e7c5e3\"");
    try expectContains(policy, "\"archive_target_scope\"");
    try expectContains(policy, "\"required_make_routes\"");
}
