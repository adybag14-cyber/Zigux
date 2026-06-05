const std = @import("std");
const options = @import("lane17_phase8_phase9_handoff_options");

const WorkflowError = error{
    MissingMarker,
    DuplicateMarker,
    ReorderedMarker,
    StaleMarker,
};

const workflow = options.workflow_text;

const Gate = struct {
    name: []const u8,
    command: []const u8,
};

const phase8_phase9_handoff = [_]Gate{
    .{
        .name = "Validate Phase 8 tooling routes",
        .command = "make -C zigux phase8-validate",
    },
    .{
        .name = "Run focused Phase 8 exec-cmd tests",
        .command = "make -C zigux phase8-exec-cmd-test",
    },
    .{
        .name = "Run focused Phase 8 libbpf segment tests",
        .command = "make -C zigux phase8-libbpf-segments-test",
    },
    .{
        .name = "Run Phase 8 tooling tests",
        .command = "make -C zigux phase8-test",
    },
    .{
        .name = "Self-test current Phase 9 review-checklist boundaries checker",
        .command = "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test",
    },
    .{
        .name = "Check current Phase 9 review-checklist boundaries packet",
        .command = "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py",
    },
    .{
        .name = "Self-test current Phase 9 freeze-map study-boundaries checker",
        .command = "python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test",
    },
    .{
        .name = "Check current Phase 9 freeze-map study-boundaries packet",
        .command = "python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py",
    },
    .{
        .name = "Self-test current Phase 9 build-only surface checker",
        .command = "python3 scripts/zigux/check-phase9-build-only-surface.py --self-test",
    },
    .{
        .name = "Check current Phase 9 build-only surface packet",
        .command = "python3 scripts/zigux/check-phase9-build-only-surface.py",
    },
    .{
        .name = "Self-test current Phase 9 trace-events runtime packet checker",
        .command = "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 9 trace-events runtime packet",
        .command = "python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py",
    },
    .{
        .name = "Run current Phase 9 shared loader command-environment boundary guard tests",
        .command = "zig build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig",
    },
    .{
        .name = "Run current Phase 9 shared loader allocator-init-flow packet",
        .command = "zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig",
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

fn validatePhase8Phase9Handoff(text: []const u8) WorkflowError!void {
    var previous: ?usize = null;

    for (phase8_phase9_handoff) |gate| {
        var name_buf: [192]u8 = undefined;
        var command_buf: [192]u8 = undefined;
        const name_line = std.fmt.bufPrint(&name_buf, "      - name: {s}", .{gate.name}) catch unreachable;
        const command_line = std.fmt.bufPrint(&command_buf, "        run: {s}", .{gate.command}) catch unreachable;
        try requireAfter(&previous, text, name_line);
        try requireAfter(&previous, text, command_line);
    }

    try requireAbsent(text, "        run: make -C zigux phase8\n");
    try requireAbsent(text, "        run: make -C zigux phase9-validate\n");
    try requireAbsent(text, "        run: make -C zigux phase9-test\n");
    try requireAbsent(text, "        run: make -C zigux phase9\n");
}

test "current bootstrap workflow keeps the Phase 8 to Phase 9 handoff ordered" {
    try validatePhase8Phase9Handoff(workflow);
}

test "contract rejects a missing Phase 9 checker gate" {
    const fixture =
        \\      - name: Validate Phase 8 tooling routes
        \\        run: make -C zigux phase8-validate
        \\      - name: Run focused Phase 8 exec-cmd tests
        \\        run: make -C zigux phase8-exec-cmd-test
        \\      - name: Run focused Phase 8 libbpf segment tests
        \\        run: make -C zigux phase8-libbpf-segments-test
        \\      - name: Run Phase 8 tooling tests
        \\        run: make -C zigux phase8-test
    ;

    try std.testing.expectError(error.MissingMarker, validatePhase8Phase9Handoff(fixture));
}

test "contract rejects reordered Phase 8 and Phase 9 workflow markers" {
    const fixture =
        \\      - name: Self-test current Phase 9 review-checklist boundaries checker
        \\        run: python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test
        \\      - name: Validate Phase 8 tooling routes
        \\        run: make -C zigux phase8-validate
        \\      - name: Run focused Phase 8 exec-cmd tests
        \\        run: make -C zigux phase8-exec-cmd-test
        \\      - name: Run focused Phase 8 libbpf segment tests
        \\        run: make -C zigux phase8-libbpf-segments-test
        \\      - name: Run Phase 8 tooling tests
        \\        run: make -C zigux phase8-test
        \\      - name: Check current Phase 9 review-checklist boundaries packet
        \\        run: python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py
        \\      - name: Self-test current Phase 9 freeze-map study-boundaries checker
        \\        run: python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py --self-test
        \\      - name: Check current Phase 9 freeze-map study-boundaries packet
        \\        run: python3 scripts/zigux/check-phase9-freeze-map-study-boundaries.py
        \\      - name: Self-test current Phase 9 build-only surface checker
        \\        run: python3 scripts/zigux/check-phase9-build-only-surface.py --self-test
        \\      - name: Check current Phase 9 build-only surface packet
        \\        run: python3 scripts/zigux/check-phase9-build-only-surface.py
        \\      - name: Self-test current Phase 9 trace-events runtime packet checker
        \\        run: python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py --self-test
        \\      - name: Check current Phase 9 trace-events runtime packet
        \\        run: python3 scripts/zigux/check-phase9-trace-events-runtime-packet.py
        \\      - name: Run current Phase 9 shared loader command-environment boundary guard tests
        \\        run: zig build phase9-runtime-loader-command-env-boundary-guard-tests --build-file zigux/tests/phase9_build.zig
        \\      - name: Run current Phase 9 shared loader allocator-init-flow packet
        \\        run: zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig
    ;

    try std.testing.expectError(error.ReorderedMarker, validatePhase8Phase9Handoff(fixture));
}

test "contract rejects duplicate handoff commands" {
    const duplicate = workflow ++ "\n        run: make -C zigux phase8-test\n";

    try std.testing.expectError(error.DuplicateMarker, validatePhase8Phase9Handoff(duplicate));
}

test "contract rejects stale broad Phase 9 aggregate routes" {
    const stale = workflow ++ "\n        run: make -C zigux phase9\n";

    try std.testing.expectError(error.StaleMarker, validatePhase8Phase9Handoff(stale));
}
