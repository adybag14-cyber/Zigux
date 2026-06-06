const std = @import("std");

const ContractFile = struct {
    path: []const u8,
    text: []const u8,
};

const stage_helper_paths = [_][]const u8{
    "scripts/zigux/stage-pinned-zig-archive.py",
    "scripts/zigux/check-lane05-stage-helper-contract.py",
    "scripts/zigux/check-lane05-stage-helper-selftest.py",
};

const stage_helper_workflow_commands = [_][]const u8{
    "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
};

fn readContractFile(allocator: std.mem.Allocator, path: []const u8) !ContractFile {
    return .{
        .path = path,
        .text = try std.Io.Dir.cwd().readFileAlloc(std.testing.io, path, allocator, .limited(2 * 1024 * 1024)),
    };
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectExactlyOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn expectExactLineOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trim(u8, line, " \t\r"), needle)) {
            count += 1;
        }
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

fn expectBefore(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_index = std.mem.indexOf(u8, haystack, later) orelse return error.MissingLaterMarker;
    try std.testing.expect(earlier_index < later_index);
}

fn expectAllContains(haystack: []const u8, markers: []const []const u8) !void {
    for (markers) |marker| {
        try expectContains(haystack, marker);
    }
}

test "phase2 closure manifest keeps staged archive helper packet explicit" {
    const allocator = std.testing.allocator;
    const manifest = try readContractFile(allocator, "zigux/tests/fixtures/phase2_tool_manifest.json");
    defer allocator.free(manifest.text);

    try expectAllContains(manifest.text, &stage_helper_paths);
    try expectContains(manifest.text, "\"bootstrap_helpers\"");
    try expectContains(manifest.text, "\"checkers\"");
    try expectContains(manifest.text, "\"status\": \"active\"");
    try expectContains(manifest.text, "\"repo_reality_gaps\": []");
    try expectBefore(
        manifest.text,
        "scripts/zigux/stage-pinned-zig-archive.py",
        "scripts/zigux/check-lane05-stage-helper-contract.py",
    );
}

test "aggregate phase2 validator requires the staged archive helper surfaces" {
    const allocator = std.testing.allocator;
    const validator = try readContractFile(allocator, "scripts/zigux/validate-phase2.py");
    defer allocator.free(validator.text);

    try expectAllContains(validator.text, &stage_helper_paths);
    try expectContains(validator.text, "\"scripts/zigux/install-zig.py\"");
    try expectContains(validator.text, "\"scripts/zigux/check-lane05-install-zig-archive-verification.py\"");
    try expectContains(validator.text, "STATIC_REQUIRED_WORKFLOW_LINES");
    try expectContains(validator.text, "DEFAULT_REQUIRED_MAKE_ROUTES");
    try expectBefore(
        validator.text,
        "\"scripts/zigux/stage-pinned-zig-archive.py\"",
        "\"scripts/zigux/check-lane05-stage-helper-contract.py\"",
    );
}

test "makefile and workflow route stage helper checks before later phase2 gates" {
    const allocator = std.testing.allocator;
    const makefile = try readContractFile(allocator, "zigux/Makefile");
    const workflow = try readContractFile(allocator, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(makefile.text);
    defer allocator.free(workflow.text);

    for (stage_helper_workflow_commands) |command| {
        var line_buf: [160]u8 = undefined;
        const line = try std.fmt.bufPrint(&line_buf, "run: {s}", .{command});
        try expectExactLineOnce(workflow.text, line);
    }
    try expectBefore(
        workflow.text,
        "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
        "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    );

    try expectExactLineOnce(makefile.text, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test");
    try expectExactLineOnce(makefile.text, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py --self-test");
    try expectExactLineOnce(makefile.text, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-contract.py");
    try expectExactLineOnce(makefile.text, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py --self-test");
    try expectExactLineOnce(makefile.text, "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-lane05-stage-helper-selftest.py");
    try expectBefore(
        makefile.text,
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/stage-pinned-zig-archive.py --self-test",
        "$(PYTHON) $(PHASE2_SCRIPT_ROOT)/check-phase2-toolchain-pinning.py --self-test",
    );
}

test "stage helper checkers expose exact self-test and pass output contracts" {
    const allocator = std.testing.allocator;
    const stage_contract = try readContractFile(allocator, "scripts/zigux/check-lane05-stage-helper-contract.py");
    const stage_selftest = try readContractFile(allocator, "scripts/zigux/check-lane05-stage-helper-selftest.py");
    defer allocator.free(stage_contract.text);
    defer allocator.free(stage_selftest.text);

    try expectContains(stage_contract.text, "STAGE_PINNED_ZIG_ARCHIVE=pass");
    try expectContains(stage_contract.text, "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST=pass");
    try expectContains(stage_contract.text, "STAGE_PINNED_ZIG_ARCHIVE_SELF_TEST_CASE_COUNT=");
    try expectContains(stage_contract.text, "duplicate-suffix archive copies");
    try expectContains(stage_contract.text, "STAGE_PINNED_ZIG_ARCHIVE_EXPECTED_SHA256=");
    try expectContains(stage_contract.text, "STAGE_PINNED_ZIG_ARCHIVE_DESTINATION=");

    try expectContains(stage_selftest.text, "LANE05_STAGE_HELPER_SELFTEST_SELF_TEST=pass");
    try expectContains(stage_selftest.text, "LANE05_STAGE_HELPER_SELFTEST_SELF_TEST_CASE_COUNT=");
    try expectContains(stage_selftest.text, "Self-test current Lane 05 stage helper contract checker");
    try expectContains(stage_selftest.text, "Check current Lane 05 stage helper selftest packet");
}
