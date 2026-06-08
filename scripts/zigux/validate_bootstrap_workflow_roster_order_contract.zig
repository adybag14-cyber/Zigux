const std = @import("std");

const validator_source = @embedFile("validate-bootstrap.py");

const required_workflow_lines = [_][]const u8{
    "\"run: python3 scripts/zigux/check-zig-toolchain.py --self-test\"",
    "\"run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\"",
    "\"run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\"",
    "\"run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test\"",
    "\"run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py\"",
    "\"run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test\"",
    "\"run: python3 scripts/zigux/check-lane05-local-archive-readme.py\"",
    "\"run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test\"",
    "\"run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py\"",
    "\"run: python3 scripts/zigux/install-zig.py --self-test\"",
    "\"run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test\"",
    "\"run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test\"",
    "\"run: python3 scripts/zigux/check-lane05-stage-helper-contract.py\"",
    "\"run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test\"",
    "\"run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py\"",
    "\"run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py --self-test\"",
    "\"run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py\"",
    "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test\"",
    "\"run: python3 scripts/zigux/check-phase1-route-summary-counts.py\"",
    "\"run: make -C zigux phase6-validate\"",
    "\"run: zig build test --build-file zigux/tests/phase6_build.zig --summary all\"",
    "\"run: python3 scripts/zigux/validate-bootstrap.py --self-test\"",
    "\"run: python3 scripts/zigux/validate-bootstrap.py\"",
};

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn markerIndex(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    return count;
}

fn requiredWorkflowTuple() ![]const u8 {
    const start_marker = "REQUIRED_WORKFLOW_LINES = (";
    const start = try markerIndex(validator_source, start_marker);
    const after_start = validator_source[start..];
    const end = try markerIndex(after_start, "\n)\n\n\ndef read_text");
    return after_start[0 .. end + 3];
}

test "bootstrap validator workflow roster remains exact and summary counted" {
    const tuple = try requiredWorkflowTuple();

    try requireContains(validator_source, "BOOTSTRAP_WORKFLOW_LINE_COUNT={len(REQUIRED_WORKFLOW_LINES)}");
    try std.testing.expectEqual(@as(usize, 23), required_workflow_lines.len);

    for (required_workflow_lines) |line| {
        try std.testing.expectEqual(@as(usize, 1), countOccurrences(tuple, line));
    }
}

test "bootstrap validator keeps setup and Lane 05 workflow probes in order" {
    const tuple = try requiredWorkflowTuple();
    var previous_index: usize = 0;

    for (required_workflow_lines[0..15], 0..) |line, ordinal| {
        const index = try markerIndex(tuple, line);
        if (ordinal != 0) {
            try std.testing.expect(previous_index < index);
        }
        previous_index = index;
    }
}

test "bootstrap validator keeps its own self-test before live validation" {
    const tuple = try requiredWorkflowTuple();
    const phase6_validate_index = try markerIndex(tuple, "\"run: make -C zigux phase6-validate\"");
    const phase6_test_index = try markerIndex(tuple, "\"run: zig build test --build-file zigux/tests/phase6_build.zig --summary all\"");
    const validator_self_test_index = try markerIndex(tuple, "\"run: python3 scripts/zigux/validate-bootstrap.py --self-test\"");
    const validator_live_index = try markerIndex(tuple, "\"run: python3 scripts/zigux/validate-bootstrap.py\"");

    try std.testing.expect(phase6_validate_index < phase6_test_index);
    try std.testing.expect(phase6_test_index < validator_self_test_index);
    try std.testing.expect(validator_self_test_index < validator_live_index);
}

test "bootstrap validator self-test still covers missing and duplicate workflow lines" {
    try requireContains(validator_source, "MISSING_WORKFLOW_LINE");
    try requireContains(validator_source, "DUPLICATE_WORKFLOW_LINE");
    try requireContains(validator_source, "replace_exact_line");
    try requireContains(validator_source, "duplicate_exact_line");
}
