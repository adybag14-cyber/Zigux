const std = @import("std");
const options = @import("lane17_phase8_exec_cmd_libbpf_workflow_options");

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

const phase8_tooling_mini_ladder = [_]Gate{
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
};

const stale_phase8_markers = [_][]const u8{
    "      - name: Run focused Phase 8 help tests",
    "        run: make -C zigux phase8-help-test",
    "      - name: Run focused Phase 8 kallsyms tests",
    "        run: make -C zigux phase8-kallsyms-test",
    "      - name: Run focused Phase 8 cpu-mask tests",
    "        run: make -C zigux phase8-cpu-mask-test",
    "      - name: Run focused Phase 8 help and kallsyms tests",
    "        run: make -C zigux phase8-help-kallsyms-test",
    "      - name: Run focused Phase 8 file-path and perf-buffer shard tests",
    "        run: make -C zigux phase8-file-path-perf-buffer-test",
    "        run: make -C zigux phase8",
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
    if (indexOfExactLine(haystack, needle) != null) return error.StaleMarker;
}

fn validatePhase8ToolingMiniLadder(text: []const u8) WorkflowError!void {
    var previous: ?usize = null;

    for (phase8_tooling_mini_ladder) |gate| {
        var name_buf: [192]u8 = undefined;
        var command_buf: [192]u8 = undefined;
        const name_line = std.fmt.bufPrint(&name_buf, "      - name: {s}", .{gate.name}) catch unreachable;
        const command_line = std.fmt.bufPrint(&command_buf, "        run: {s}", .{gate.command}) catch unreachable;
        try requireAfter(&previous, text, name_line);
        try requireAfter(&previous, text, command_line);
    }

    inline for (stale_phase8_markers) |marker| {
        try requireAbsent(text, marker);
    }
}

test "current bootstrap workflow keeps the Phase 8 exec-cmd and libbpf mini-ladder ordered" {
    try validatePhase8ToolingMiniLadder(workflow);
}

test "contract rejects a missing Phase 8 libbpf segment route" {
    const fixture =
        \\      - name: Validate Phase 8 tooling routes
        \\        run: make -C zigux phase8-validate
        \\      - name: Run focused Phase 8 exec-cmd tests
        \\        run: make -C zigux phase8-exec-cmd-test
        \\      - name: Run Phase 8 tooling tests
        \\        run: make -C zigux phase8-test
    ;

    try std.testing.expectError(error.MissingMarker, validatePhase8ToolingMiniLadder(fixture));
}

test "contract rejects reordered Phase 8 focused routes" {
    const fixture =
        \\      - name: Validate Phase 8 tooling routes
        \\        run: make -C zigux phase8-validate
        \\      - name: Run focused Phase 8 libbpf segment tests
        \\        run: make -C zigux phase8-libbpf-segments-test
        \\      - name: Run focused Phase 8 exec-cmd tests
        \\        run: make -C zigux phase8-exec-cmd-test
        \\      - name: Run Phase 8 tooling tests
        \\        run: make -C zigux phase8-test
    ;

    try std.testing.expectError(error.ReorderedMarker, validatePhase8ToolingMiniLadder(fixture));
}

test "contract rejects duplicate aggregate Phase 8 tooling commands" {
    const duplicate = workflow ++ "\n        run: make -C zigux phase8-test\n";

    try std.testing.expectError(error.DuplicateMarker, validatePhase8ToolingMiniLadder(duplicate));
}

test "contract rejects stale granular Phase 8 workflow shards" {
    const stale = workflow ++
        "\n      - name: Run focused Phase 8 help tests\n" ++
        "        run: make -C zigux phase8-help-test\n";

    try std.testing.expectError(error.StaleMarker, validatePhase8ToolingMiniLadder(stale));
}
