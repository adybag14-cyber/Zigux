const std = @import("std");
const build_options = @import("build_options");

const validator_source = @embedFile(build_options.validator_path);
const workflow_source = @embedFile(build_options.workflow_path);

const RequiredLine = struct {
    line: []const u8,
};

const required_workflow_lines = [_]RequiredLine{
    .{ .line = "run: python3 scripts/zigux/check-zig-toolchain.py --self-test" },
    .{ .line = "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only" },
    .{ .line = "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing" },
    .{ .line = "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test" },
    .{ .line = "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py" },
    .{ .line = "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test" },
    .{ .line = "run: python3 scripts/zigux/check-lane05-local-archive-readme.py" },
    .{ .line = "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test" },
    .{ .line = "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py" },
    .{ .line = "run: python3 scripts/zigux/install-zig.py --self-test" },
    .{ .line = "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test" },
    .{ .line = "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test" },
    .{ .line = "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py" },
    .{ .line = "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test" },
    .{ .line = "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py" },
    .{ .line = "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py --self-test" },
    .{ .line = "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py" },
    .{ .line = "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test" },
    .{ .line = "run: python3 scripts/zigux/check-phase1-route-summary-counts.py" },
    .{ .line = "run: make -C zigux phase6-validate" },
    .{ .line = "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all" },
    .{ .line = "run: python3 scripts/zigux/validate-bootstrap.py --self-test" },
    .{ .line = "run: python3 scripts/zigux/validate-bootstrap.py" },
};

fn contains(haystack: []const u8, needle: []const u8) bool {
    return std.mem.indexOf(u8, haystack, needle) != null;
}

fn indexOfRequired(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn countExactTrimmedLines(text: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), marker)) {
            count += 1;
        }
    }
    return count;
}

fn countPythonTupleStringLines(text: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        const trimmed = std.mem.trim(u8, line, " \t\r");
        if (trimmed.len < marker.len + 3) continue;
        if (trimmed[0] != '"' or trimmed[trimmed.len - 2] != '"' or trimmed[trimmed.len - 1] != ',') continue;
        if (std.mem.eql(u8, trimmed[1 .. trimmed.len - 2], marker)) {
            count += 1;
        }
    }
    return count;
}

fn indexOfExactTrimmedLine(text: []const u8, marker: []const u8) !usize {
    var offset: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), marker)) {
            return offset;
        }
        offset += line.len + 1;
    }
    return error.MissingMarker;
}

test "bootstrap validator owns the required workflow roster and fail-closed diagnostics" {
    try std.testing.expect(contains(validator_source, "REQUIRED_WORKFLOW_LINES = ("));
    try std.testing.expect(contains(validator_source, "MISSING_WORKFLOW_LINE"));
    try std.testing.expect(contains(validator_source, "DUPLICATE_WORKFLOW_LINE"));
    try std.testing.expect(contains(validator_source, "count_exact_lines(workflow, marker)"));

    inline for (required_workflow_lines) |entry| {
        try std.testing.expectEqual(@as(usize, 1), countPythonTupleStringLines(validator_source, entry.line));
    }
}

test "bootstrap workflow exposes each validator-required command exactly once" {
    inline for (required_workflow_lines) |entry| {
        try std.testing.expectEqual(@as(usize, 1), countExactTrimmedLines(workflow_source, entry.line));
    }
}

test "bootstrap workflow keeps toolchain checks before the final validator handoff" {
    const compile_scripts = try indexOfRequired(workflow_source, "name: Compile current scripts");
    const checker_self_test = try indexOfRequired(workflow_source, required_workflow_lines[0].line);
    const policy_only = try indexOfRequired(workflow_source, required_workflow_lines[1].line);
    const archive_allow_missing = try indexOfRequired(workflow_source, required_workflow_lines[2].line);
    const installer_self_test = try indexOfRequired(workflow_source, required_workflow_lines[9].line);
    const validator_self_test = try indexOfExactTrimmedLine(workflow_source, required_workflow_lines[21].line);
    const validator_live = try indexOfExactTrimmedLine(workflow_source, required_workflow_lines[22].line);

    try std.testing.expect(compile_scripts < checker_self_test);
    try std.testing.expect(checker_self_test < policy_only);
    try std.testing.expect(policy_only < archive_allow_missing);
    try std.testing.expect(archive_allow_missing < installer_self_test);
    try std.testing.expect(installer_self_test < validator_self_test);
    try std.testing.expect(validator_self_test < validator_live);
}

test "validator workflow roster stays scoped to bootstrap validation helpers" {
    try std.testing.expect(!contains(validator_source, "run: zig build test --build-file zigux/tests/build.zig"));
    try std.testing.expect(!contains(validator_source, "run: make -C zigux phase2"));
    try std.testing.expect(!contains(validator_source, "run: make -C zigux phase3"));
}
