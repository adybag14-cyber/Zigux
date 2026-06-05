const std = @import("std");
const options = @import("lane17_phase3_phase4_handoff_options");

const WorkflowError = error{
    MissingMarker,
    DuplicateMarker,
    ReorderedMarker,
    StaleMarker,
};

const workflow = @embedFile(options.workflow_path);

const Gate = struct {
    name: []const u8,
    command: []const u8,
};

const phase3_phase4_handoff = [_]Gate{
    .{
        .name = "Run current Phase 3 shared tests-root packet",
        .command = "zig build phase3-test --build-file zigux/tests/build.zig",
    },
    .{
        .name = "Run current Phase 3 ABI dump replay",
        .command = "zig build phase3-dump --build-file zigux/tests/build.zig",
    },
    .{
        .name = "Run current Phase 1 shared tests-root smoke",
        .command = "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    },
    .{
        .name = "Self-test current Phase 4 repo-reality warning checker",
        .command = "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
    },
    .{
        .name = "Check current Phase 4 repo-reality warning packet",
        .command = "python3 scripts/zigux/check-phase4-repo-reality-warning.py",
    },
    .{
        .name = "Self-test current Phase 4 reversible-delivery pin checker",
        .command = "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test",
    },
    .{
        .name = "Check current Phase 4 reversible-delivery pin packet",
        .command = "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py",
    },
    .{
        .name = "Self-test current Phase 4 tests README checker",
        .command = "python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 4 tests README packet",
        .command = "python3 scripts/zigux/check-phase4-tests-readme-packet.py",
    },
    .{
        .name = "Validate Phase 4 rollback routes",
        .command = "make -C zigux phase4-validate",
    },
    .{
        .name = "Run Phase 4 rollback tests",
        .command = "make -C zigux phase4-test",
    },
};

fn countExactLines(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, line, needle)) count += 1;
    }
    return count;
}

fn indexOfExactLine(haystack: []const u8, needle: []const u8) ?usize {
    var start: usize = 0;
    while (start <= haystack.len) {
        const end = std.mem.indexOfScalarPos(u8, haystack, start, '\n') orelse haystack.len;
        if (std.mem.eql(u8, haystack[start..end], needle)) return start;
        if (end == haystack.len) break;
        start = end + 1;
    }
    return null;
}

fn requireOnce(haystack: []const u8, needle: []const u8) WorkflowError!usize {
    const first = indexOfExactLine(haystack, needle) orelse return error.MissingMarker;
    if (countExactLines(haystack, needle) != 1) return error.DuplicateMarker;
    return first;
}

fn requireAfter(previous: *?usize, haystack: []const u8, needle: []const u8) WorkflowError!void {
    const index = try requireOnce(haystack, needle);
    if (previous.*) |previous_index| {
        if (index <= previous_index) return error.ReorderedMarker;
    }
    previous.* = index;
}

fn requireAbsent(haystack: []const u8, needle: []const u8) WorkflowError!void {
    if (std.mem.indexOf(u8, haystack, needle) != null) return error.StaleMarker;
}

fn validatePhase3Phase4Handoff(text: []const u8) WorkflowError!void {
    var previous: ?usize = null;

    for (phase3_phase4_handoff) |gate| {
        var name_buf: [192]u8 = undefined;
        var command_buf: [192]u8 = undefined;
        const name_line = std.fmt.bufPrint(&name_buf, "      - name: {s}", .{gate.name}) catch unreachable;
        const command_line = std.fmt.bufPrint(&command_buf, "        run: {s}", .{gate.command}) catch unreachable;
        try requireAfter(&previous, text, name_line);
        try requireAfter(&previous, text, command_line);
    }

    try requireAbsent(text, "        run: make -C zigux phase3\n");
    try requireAbsent(text, "        run: make -C zigux phase3-test\n");
    try requireAbsent(text, "        run: make -C zigux phase4\n");
}

test "current bootstrap workflow keeps the Phase 3 to Phase 4 handoff ordered" {
    try validatePhase3Phase4Handoff(workflow);
}

test "contract rejects a missing Phase 1 smoke handoff marker" {
    const fixture =
        \\      - name: Run current Phase 3 shared tests-root packet
        \\        run: zig build phase3-test --build-file zigux/tests/build.zig
        \\      - name: Run current Phase 3 ABI dump replay
        \\        run: zig build phase3-dump --build-file zigux/tests/build.zig
        \\      - name: Self-test current Phase 4 repo-reality warning checker
        \\        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test
        \\      - name: Check current Phase 4 repo-reality warning packet
        \\        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py
        \\      - name: Self-test current Phase 4 reversible-delivery pin checker
        \\        run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test
        \\      - name: Check current Phase 4 reversible-delivery pin packet
        \\        run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py
        \\      - name: Self-test current Phase 4 tests README checker
        \\        run: python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test
        \\      - name: Check current Phase 4 tests README packet
        \\        run: python3 scripts/zigux/check-phase4-tests-readme-packet.py
        \\      - name: Validate Phase 4 rollback routes
        \\        run: make -C zigux phase4-validate
        \\      - name: Run Phase 4 rollback tests
        \\        run: make -C zigux phase4-test
    ;

    try std.testing.expectError(error.MissingMarker, validatePhase3Phase4Handoff(fixture));
}

test "contract rejects reordered Phase 3 dump and shared Phase 3 test markers" {
    const fixture =
        \\      - name: Run current Phase 3 ABI dump replay
        \\        run: zig build phase3-dump --build-file zigux/tests/build.zig
        \\      - name: Run current Phase 3 shared tests-root packet
        \\        run: zig build phase3-test --build-file zigux/tests/build.zig
        \\      - name: Run current Phase 1 shared tests-root smoke
        \\        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig
        \\      - name: Self-test current Phase 4 repo-reality warning checker
        \\        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test
        \\      - name: Check current Phase 4 repo-reality warning packet
        \\        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py
        \\      - name: Self-test current Phase 4 reversible-delivery pin checker
        \\        run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test
        \\      - name: Check current Phase 4 reversible-delivery pin packet
        \\        run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py
        \\      - name: Self-test current Phase 4 tests README checker
        \\        run: python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test
        \\      - name: Check current Phase 4 tests README packet
        \\        run: python3 scripts/zigux/check-phase4-tests-readme-packet.py
        \\      - name: Validate Phase 4 rollback routes
        \\        run: make -C zigux phase4-validate
        \\      - name: Run Phase 4 rollback tests
        \\        run: make -C zigux phase4-test
    ;

    try std.testing.expectError(error.ReorderedMarker, validatePhase3Phase4Handoff(fixture));
}

test "contract rejects duplicate handoff commands" {
    const duplicate = workflow ++ "\n        run: zig build phase3-test --build-file zigux/tests/build.zig\n";

    try std.testing.expectError(error.DuplicateMarker, validatePhase3Phase4Handoff(duplicate));
}

test "contract rejects stale broad Phase 3 and Phase 4 aggregate routes" {
    const stale = workflow ++ "\n        run: make -C zigux phase4\n";

    try std.testing.expectError(error.StaleMarker, validatePhase3Phase4Handoff(stale));
}
