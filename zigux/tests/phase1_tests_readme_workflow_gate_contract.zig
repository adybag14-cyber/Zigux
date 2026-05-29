const std = @import("std");

const readme = @embedFile("README.md");

const Gate = struct {
    name: []const u8,
    command: []const u8,
};

const phase1_workflow_gates = [_]Gate{
    .{
        .name = "direct-owner markers self-test",
        .command = "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    },
    .{
        .name = "direct-owner markers packet",
        .command = "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    },
    .{
        .name = "direct-anchor manifest self-test",
        .command = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    },
    .{
        .name = "direct-anchor manifest packet",
        .command = "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    },
    .{
        .name = "string review self-test",
        .command = "python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    },
    .{
        .name = "string review packet",
        .command = "python3 scripts/zigux/check-phase1-string-review-packet.py",
    },
    .{
        .name = "bench checker self-test",
        .command = "python3 scripts/zigux/check-phase1-bench.py --self-test",
    },
    .{
        .name = "shared reminder self-test",
        .command = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    },
    .{
        .name = "shared reminder packet",
        .command = "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    },
    .{
        .name = "closure validator self-test",
        .command = "python3 scripts/zigux/validate-phase1-closure.py --self-test",
    },
    .{
        .name = "closure validator packet",
        .command = "python3 scripts/zigux/validate-phase1-closure.py",
    },
    .{
        .name = "shared tests-root smoke",
        .command = "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    },
};

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectCommandOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = lineIndex(haystack, earlier) orelse return error.MissingEarlierGate;
    const later_index = lineIndex(haystack, later) orelse return error.MissingLaterGate;
    try std.testing.expect(earlier_index < later_index);
}

fn lineIndex(haystack: []const u8, needle: []const u8) ?usize {
    var offset: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, line, needle)) return offset;
        offset += line.len + 1;
    }
    return null;
}

fn scriptPath(command: []const u8) []const u8 {
    const start = std.mem.indexOf(u8, command, "scripts/zigux/") orelse return command;
    const rest = command[start..];
    const end = std.mem.indexOfScalar(u8, rest, ' ') orelse rest.len;
    return rest[0..end];
}

test "tests README keeps the Phase 1 direct-readback packet explicit" {
    const readme_markers = [_][]const u8{
        "## Phase 1 host-tools review packet",
        "current direct-readback Phase 1 reminder packet",
        "Documentation/zigux/phase1-closure.md",
        "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
        "scripts/zigux/check-phase1-direct-owner-markers.py",
        "scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
        "scripts/zigux/check-phase1-string-review-packet.py",
        "scripts/zigux/check-phase1-bench.py",
        "scripts/zigux/check-phase1-shared-reminder-packet.py",
        "scripts/zigux/validate-phase1-closure.py",
        "zigux/tests/build.zig",
        "zigux/tests/phase1_host_tools_smoke.zig",
        ".github/workflows/zigux-bootstrap.yml",
        "current shared Phase 1 smoke route: `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`",
        "broader Phase 1 closure companions stay outside the narrow direct-readback packet",
    };

    for (readme_markers) |marker| {
        try expectContains(readme, marker);
    }
}

test "Phase 1 workflow gate command roster keeps paired checks ordered" {
    var roster: []const u8 = "";
    for (phase1_workflow_gates) |gate| {
        try std.testing.expect(gate.name.len > 0);
        try std.testing.expect(gate.command.len > 0);
        roster = gate.command;
    }
    try std.testing.expect(roster.len > 0);

    const ordered_commands = comptime blk: {
        var joined: []const u8 = "";
        for (phase1_workflow_gates) |gate| {
            joined = joined ++ gate.command ++ "\n";
        }
        break :blk joined;
    };

    try expectCommandOrder(
        ordered_commands,
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
        "python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    );
    try expectCommandOrder(
        ordered_commands,
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
        "python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
    );
    try expectCommandOrder(
        ordered_commands,
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
        "python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    );
    try expectCommandOrder(
        ordered_commands,
        "python3 scripts/zigux/validate-phase1-closure.py --self-test",
        "python3 scripts/zigux/validate-phase1-closure.py",
    );
    try expectCommandOrder(
        ordered_commands,
        "python3 scripts/zigux/validate-phase1-closure.py",
        "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    );
}

test "README names every workflow Phase 1 script gate path" {
    for (phase1_workflow_gates) |gate| {
        const path = scriptPath(gate.command);
        if (!std.mem.startsWith(u8, path, "scripts/zigux/")) continue;
        try expectContains(readme, path);
    }
}
