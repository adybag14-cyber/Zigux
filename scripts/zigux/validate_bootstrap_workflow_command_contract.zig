const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";
const validator_path = "scripts/zigux/validate-bootstrap.py";

const required_commands = [_][]const u8{
    "run: python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "run: python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "run: python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "run: python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "run: python3 scripts/zigux/install-zig.py --self-test",
    "run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py --self-test",
    "run: python3 scripts/zigux/check-lane01-bootstrap-charter-alignment.py",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "run: make -C zigux phase6-validate",
    "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
    "run: python3 scripts/zigux/validate-bootstrap.py --self-test",
    "run: python3 scripts/zigux/validate-bootstrap.py",
};

fn trimLine(line: []const u8) []const u8 {
    return std.mem.trim(u8, line, " \t\r");
}

fn countExactLines(text: []const u8, marker: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, trimLine(line), marker)) {
            count += 1;
        }
    }
    return count;
}

fn indexOfExactLineAfter(text: []const u8, marker: []const u8, after: usize) ?usize {
    var offset: usize = 0;
    var lines = std.mem.splitScalar(u8, text, '\n');
    while (lines.next()) |line| {
        const line_start = offset;
        offset += line.len + 1;
        if (line_start < after) {
            continue;
        }
        if (std.mem.eql(u8, trimLine(line), marker)) {
            return line_start;
        }
    }
    return null;
}

fn expectUniqueCommandSequence(text: []const u8) !void {
    var next_offset: usize = 0;
    for (required_commands) |command| {
        if (countExactLines(text, command) != 1) {
            return error.RequiredCommandCountMismatch;
        }
        const found_at = indexOfExactLineAfter(text, command, next_offset) orelse return error.RequiredCommandOutOfOrder;
        next_offset = found_at + command.len;
    }
}

fn expectValidatorListsCommand(text: []const u8, command: []const u8) !void {
    const quoted_command = try std.fmt.allocPrint(std.testing.allocator, "\"{s}\"", .{command});
    defer std.testing.allocator.free(quoted_command);
    try std.testing.expect(std.mem.indexOf(u8, text, quoted_command) != null);
}

test "bootstrap validator and workflow agree on required command roster" {
    const allocator = std.testing.allocator;
    const io = std.Io.Threaded.global_single_threaded.io();
    const cwd = std.Io.Dir.cwd();
    const workflow = try cwd.readFileAlloc(io, workflow_path, allocator, .limited(1024 * 1024));
    defer allocator.free(workflow);
    const validator = try cwd.readFileAlloc(io, validator_path, allocator, .limited(512 * 1024));
    defer allocator.free(validator);

    try expectUniqueCommandSequence(workflow);
    for (required_commands) |command| {
        try expectValidatorListsCommand(validator, command);
    }
}

test "command roster catches duplicate and reordered workflow lines" {
    const valid = required_commands[0] ++ "\n" ++
        required_commands[1] ++ "\n" ++
        required_commands[2] ++ "\n" ++
        required_commands[3] ++ "\n" ++
        required_commands[4] ++ "\n" ++
        required_commands[5] ++ "\n" ++
        required_commands[6] ++ "\n" ++
        required_commands[7] ++ "\n" ++
        required_commands[8] ++ "\n" ++
        required_commands[9] ++ "\n" ++
        required_commands[10] ++ "\n" ++
        required_commands[11] ++ "\n" ++
        required_commands[12] ++ "\n" ++
        required_commands[13] ++ "\n" ++
        required_commands[14] ++ "\n" ++
        required_commands[15] ++ "\n" ++
        required_commands[16] ++ "\n" ++
        required_commands[17] ++ "\n" ++
        required_commands[18] ++ "\n" ++
        required_commands[19] ++ "\n" ++
        required_commands[20] ++ "\n" ++
        required_commands[21] ++ "\n" ++
        required_commands[22] ++ "\n";

    try expectUniqueCommandSequence(valid);
    try std.testing.expectError(error.RequiredCommandCountMismatch, expectUniqueCommandSequence(valid ++ required_commands[0] ++ "\n"));

    const reordered = required_commands[1] ++ "\n" ++
        required_commands[0] ++ "\n" ++
        required_commands[2] ++ "\n" ++
        required_commands[3] ++ "\n" ++
        required_commands[4] ++ "\n" ++
        required_commands[5] ++ "\n" ++
        required_commands[6] ++ "\n" ++
        required_commands[7] ++ "\n" ++
        required_commands[8] ++ "\n" ++
        required_commands[9] ++ "\n" ++
        required_commands[10] ++ "\n" ++
        required_commands[11] ++ "\n" ++
        required_commands[12] ++ "\n" ++
        required_commands[13] ++ "\n" ++
        required_commands[14] ++ "\n" ++
        required_commands[15] ++ "\n" ++
        required_commands[16] ++ "\n" ++
        required_commands[17] ++ "\n" ++
        required_commands[18] ++ "\n" ++
        required_commands[19] ++ "\n" ++
        required_commands[20] ++ "\n" ++
        required_commands[21] ++ "\n" ++
        required_commands[22] ++ "\n";
    try std.testing.expectError(error.RequiredCommandOutOfOrder, expectUniqueCommandSequence(reordered));
}
