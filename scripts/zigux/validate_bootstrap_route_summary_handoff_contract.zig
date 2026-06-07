const std = @import("std");
const testing = std.testing;

const validator = @embedFile("validate-bootstrap.py");

const route_summary_path = "scripts/zigux/check-phase1-route-summary-counts.py";
const route_summary_selftest = "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test";
const route_summary_run = "run: python3 scripts/zigux/check-phase1-route-summary-counts.py";
const route_summary_run_line = "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py\",";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try testing.expect(before_index < after_index);
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

test "route-summary checker remains in required path roster" {
    try expectContains(validator, "REQUIRED_PATHS = (");
    try expectContains(validator, route_summary_path);
    try expectOrdered(validator, "scripts/zigux/check-lane05-stage-helper-selftest.py", route_summary_path);
    try expectOrdered(validator, route_summary_path, "scripts/zigux/install-zig.py");
}

test "route-summary workflow handoff keeps self-test before direct run" {
    try expectContains(validator, "REQUIRED_WORKFLOW_LINES = (");
    try expectContains(validator, route_summary_selftest);
    try expectContains(validator, route_summary_run_line);
    try expectOrdered(validator, route_summary_selftest, route_summary_run_line);
    try expectOrdered(validator, route_summary_run_line, "python3 scripts/zigux/validate-bootstrap.py --self-test");
}

test "validator self-test fails closed when route-summary checker disappears" {
    try expectContains(validator, "(root / \"scripts/zigux/check-phase1-route-summary-counts.py\").unlink()");
    try expectContains(validator, "\"MISSING_REQUIRED_PATH\",\n        \"scripts/zigux/check-phase1-route-summary-counts.py\"");
    try expectOrdered(validator, "(root / \"scripts/zigux/check-phase1-route-summary-counts.py\").unlink()", "scripts/zigux/zig-toolchain-policy.json");
}

test "pass output keeps required path and workflow line count envelopes" {
    try expectContains(validator, "BOOTSTRAP_VALIDATION=pass");
    try expectContains(validator, "BOOTSTRAP_REQUIRED_PATH_COUNT={len(REQUIRED_PATHS)}");
    try expectContains(validator, "BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}");
    try testing.expect(countOccurrences(validator, route_summary_path) >= 4);
}
