const std = @import("std");
const checker = @embedFile("check-phase1-parity.py");

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn expectExactCount(haystack: []const u8, needle: []const u8, expected_count: usize) !void {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    try std.testing.expectEqual(expected_count, count);
}

test "read_json reports invalid json with label line and column" {
    try expectContains(checker, "except json.JSONDecodeError as exc:");
    try expectContains(
        checker,
        "issues.append(f\"{label}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}\")",
    );
    try expectOrdered(
        checker,
        "except json.JSONDecodeError as exc:",
        "issues.append(f\"{label}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}\")",
    );
    try expectOrdered(
        checker,
        "issues.append(f\"{label}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}\")",
        "return None",
    );
}

test "invalid json diagnostic stays separate from duplicate key diagnostics" {
    try expectOrdered(
        checker,
        "payload = load_json_with_duplicate_tracking(read_text(path))",
        "except json.JSONDecodeError as exc:",
    );
    try expectOrdered(
        checker,
        "except json.JSONDecodeError as exc:",
        "duplicate_paths = collect_duplicate_json_key_paths(payload)",
    );
    try expectContains(
        checker,
        "issues.extend(f\"{label}:duplicate_json_key:{duplicate_path}\" for duplicate_path in duplicate_paths)",
    );
}

test "fixture manifest and blocker packets use read_json labels" {
    try expectExactCount(checker, "read_json(root / FIXTURE_REL, \"fixture\", issues)", 1);
    try expectExactCount(checker, "read_json(root / MANIFEST_REL, \"manifest\", issues)", 1);
    try expectExactCount(checker, "read_json(root / BLOCKERS_REL, \"blockers\", issues)", 1);
    try expectOrdered(
        checker,
        "read_json(root / FIXTURE_REL, \"fixture\", issues)",
        "read_json(root / MANIFEST_REL, \"manifest\", issues)",
    );
    try expectOrdered(
        checker,
        "read_json(root / MANIFEST_REL, \"manifest\", issues)",
        "read_json(root / BLOCKERS_REL, \"blockers\", issues)",
    );
}
