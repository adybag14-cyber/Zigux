const std = @import("std");

const validator_source = @embedFile("validate-bootstrap.py");

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return error.MissingBeforeMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return error.MissingAfterMarker;
    try std.testing.expect(before_index < after_index);
}

fn sliceFromMarker(source: []const u8, marker: []const u8) ![]const u8 {
    const start = std.mem.indexOf(u8, source, marker) orelse return error.MissingSectionMarker;
    return source[start..];
}

test "required paths keep the bootstrap toolchain helper roster visible" {
    const required_paths = try sliceFromMarker(validator_source, "REQUIRED_PATHS = (");

    try requireContains(required_paths, "\"scripts/zigux/check-zig-toolchain.py\"");
    try requireContains(required_paths, "\"scripts/zigux/install-zig.py\"");
    try requireContains(required_paths, "\"scripts/zigux/validate-bootstrap.py\"");
    try requireContains(required_paths, "\"scripts/zigux/zig-toolchain-policy.json\"");

    try requireOrdered(
        required_paths,
        "\"scripts/zigux/check-zig-toolchain.py\"",
        "\"scripts/zigux/install-zig.py\"",
    );
    try requireOrdered(
        required_paths,
        "\"scripts/zigux/install-zig.py\"",
        "\"scripts/zigux/validate-bootstrap.py\"",
    );
    try requireOrdered(
        required_paths,
        "\"scripts/zigux/validate-bootstrap.py\"",
        "\"scripts/zigux/zig-toolchain-policy.json\"",
    );
}

test "required paths keep the Lane 05 local archive helper chain visible" {
    const required_paths = try sliceFromMarker(validator_source, "REQUIRED_PATHS = (");

    try requireContains(required_paths, "\"scripts/zigux/check-lane05-local-first-archive-workflow.py\"");
    try requireContains(required_paths, "\"scripts/zigux/check-lane05-local-archive-readme.py\"");
    try requireContains(required_paths, "\"scripts/zigux/check-lane05-install-zig-archive-verification.py\"");
    try requireContains(required_paths, "\"scripts/zigux/stage-pinned-zig-archive.py\"");
    try requireContains(required_paths, "\"scripts/zigux/check-lane05-stage-helper-contract.py\"");
    try requireContains(required_paths, "\"scripts/zigux/check-lane05-stage-helper-selftest.py\"");

    try requireOrdered(
        required_paths,
        "\"scripts/zigux/check-lane05-local-first-archive-workflow.py\"",
        "\"scripts/zigux/check-lane05-local-archive-readme.py\"",
    );
    try requireOrdered(
        required_paths,
        "\"scripts/zigux/check-lane05-local-archive-readme.py\"",
        "\"scripts/zigux/check-lane05-install-zig-archive-verification.py\"",
    );
    try requireOrdered(
        required_paths,
        "\"scripts/zigux/check-lane05-install-zig-archive-verification.py\"",
        "\"scripts/zigux/stage-pinned-zig-archive.py\"",
    );
    try requireOrdered(
        required_paths,
        "\"scripts/zigux/stage-pinned-zig-archive.py\"",
        "\"scripts/zigux/check-lane05-stage-helper-contract.py\"",
    );
    try requireOrdered(
        required_paths,
        "\"scripts/zigux/check-lane05-stage-helper-contract.py\"",
        "\"scripts/zigux/check-lane05-stage-helper-selftest.py\"",
    );
}

test "workflow roster keeps toolchain policy and archive checks before Lane 05 handoff" {
    const workflow_lines = try sliceFromMarker(validator_source, "REQUIRED_WORKFLOW_LINES = (");

    try requireOrdered(
        workflow_lines,
        "\"run: python3 scripts/zigux/check-zig-toolchain.py --self-test\"",
        "\"run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\"",
    );
    try requireOrdered(
        workflow_lines,
        "\"run: python3 scripts/zigux/check-zig-toolchain.py --policy-only\"",
        "\"run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\"",
    );
    try requireOrdered(
        workflow_lines,
        "\"run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing\"",
        "\"run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test\"",
    );
    try requireOrdered(
        workflow_lines,
        "\"run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py\"",
        "\"run: python3 scripts/zigux/install-zig.py --self-test\"",
    );
    try requireOrdered(
        workflow_lines,
        "\"run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test\"",
        "\"run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test\"",
    );
}

test "validator self-test removes representative toolchain helper paths" {
    const self_test_source = try sliceFromMarker(validator_source, "def run_self_test() -> int:");

    try requireContains(self_test_source, "(root / \"scripts/zigux/check-zig-toolchain.py\").unlink()");
    try requireContains(self_test_source, "(root / \"scripts/zigux/stage-pinned-zig-archive.py\").unlink()");
    try requireContains(self_test_source, "(root / \"scripts/zigux/check-lane05-stage-helper-selftest.py\").unlink()");
    try requireContains(self_test_source, "(root / \"scripts/zigux/install-zig.py\").unlink()");
    try requireContains(self_test_source, "(root / \"scripts/zigux/zig-toolchain-policy.json\").unlink()");
}
