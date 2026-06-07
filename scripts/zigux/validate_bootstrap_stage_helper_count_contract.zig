const std = @import("std");

const source = @embedFile("validate-bootstrap.py");

fn contains(needle: []const u8) bool {
    return std.mem.indexOf(u8, source, needle) != null;
}

fn countOccurrences(needle: []const u8) usize {
    var count: usize = 0;
    var cursor: usize = 0;
    while (std.mem.indexOfPos(u8, source, cursor, needle)) |index| {
        count += 1;
        cursor = index + needle.len;
    }
    return count;
}

fn requireOrdered(first: []const u8, second: []const u8) !void {
    const first_index = std.mem.indexOf(u8, source, first) orelse return error.MissingFirstMarker;
    const second_index = std.mem.indexOf(u8, source, second) orelse return error.MissingSecondMarker;
    try std.testing.expect(first_index < second_index);
}

test "staged helper files stay in the required bootstrap path roster" {
    try std.testing.expect(contains("REQUIRED_PATHS = ("));
    try std.testing.expect(countOccurrences("\"scripts/zigux/check-lane05-stage-helper-contract.py\"") >= 2);
    try std.testing.expect(countOccurrences("\"scripts/zigux/check-lane05-stage-helper-selftest.py\"") >= 2);
    try requireOrdered(
        "\"scripts/zigux/stage-pinned-zig-archive.py\"",
        "\"scripts/zigux/check-lane05-stage-helper-contract.py\"",
    );
    try requireOrdered(
        "\"scripts/zigux/check-lane05-stage-helper-contract.py\"",
        "\"scripts/zigux/check-lane05-stage-helper-selftest.py\"",
    );
}

test "staged helper workflow commands remain exact-counted" {
    try std.testing.expect(contains("REQUIRED_WORKFLOW_LINES = ("));
    try std.testing.expect(contains("run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test"));
    try std.testing.expect(contains("run: python3 scripts/zigux/check-lane05-stage-helper-contract.py"));
    try std.testing.expect(contains("run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test"));
    try std.testing.expect(contains("run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py"));
    try requireOrdered(
        "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
        "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    );
    try requireOrdered(
        "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
        "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    );
}

test "validator self-test covers missing staged helper path failures" {
    try std.testing.expect(contains("write_text(root, \"scripts/zigux/check-lane05-stage-helper-contract.py\", \"present\\n\")"));
    try std.testing.expect(contains("write_text(root, \"scripts/zigux/check-lane05-stage-helper-selftest.py\", \"present\\n\")"));
    try std.testing.expect(contains("(root / \"scripts/zigux/check-lane05-stage-helper-selftest.py\").unlink()"));
    try std.testing.expect(contains("\"MISSING_REQUIRED_PATH\""));
    try requireOrdered(
        "write_text(root, \"scripts/zigux/check-lane05-stage-helper-contract.py\", \"present\\n\")",
        "write_text(root, \"scripts/zigux/check-lane05-stage-helper-selftest.py\", \"present\\n\")",
    );
    try requireOrdered(
        "(root / \"scripts/zigux/stage-pinned-zig-archive.py\").unlink()",
        "(root / \"scripts/zigux/check-lane05-stage-helper-selftest.py\").unlink()",
    );
}

test "pass output keeps required path and workflow count envelopes visible" {
    try std.testing.expect(contains("print(\"BOOTSTRAP_VALIDATION=pass\")"));
    try std.testing.expect(contains("print(f\"BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}\")"));
    try std.testing.expect(contains("print(f\"BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}\")"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences("BOOTSTRAP_REQUIRED_PATH_COUNT"));
    try std.testing.expectEqual(@as(usize, 1), countOccurrences("BOOTSTRAP_WORKFLOW_LINE_COUNT"));
    try requireOrdered(
        "print(\"BOOTSTRAP_VALIDATION=pass\")",
        "print(f\"BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}\")",
    );
}
