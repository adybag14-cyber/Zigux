const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const Phase12TailStep = struct {
    name: []const u8,
    command: []const u8,
};

const phase12_tail_steps = [_]Phase12TailStep{
    .{
        .name = "Self-test current Phase 12 libbpf heavy-consumer packet checker",
        .command = "python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test",
    },
    .{
        .name = "Check current Phase 12 libbpf heavy-consumer packet",
        .command = "python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py",
    },
    .{
        .name = "Validate current Phase 12 support bundle",
        .command = "python3 scripts/zigux/validate-phase12.py",
    },
    .{
        .name = "Run current Phase 12 smoke packet",
        .command = "make -C zigux phase12-smoke",
    },
    .{
        .name = "Run current Phase 12 shared test packet",
        .command = "make -C zigux phase12-test",
    },
    .{
        .name = "Run current Phase 12 aggregate route",
        .command = "make -C zigux phase12",
    },
    .{
        .name = "Run current Phase 12 virtio_net syntax-lab companion",
        .command = "make -C zigux phase12-virtio-net-syntax-lab-test",
    },
};

const phase14_shared_smoke_name = "Self-test current Phase 14 shared smoke route checker";
const phase14_shared_smoke_command = "python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test";
const phase14_validate_name = "Run current Phase 14 validate route";
const phase14_validate_command = "make -C zigux phase14-validate";
const phase12_throughput_name = "Run current Phase 12 throughput-parity anchor";
const phase12_throughput_command = "zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all";

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, workflow_path, allocator, .limited(1024 * 1024));
}

fn workflowLineMatches(line: []const u8, needle: []const u8) bool {
    const trimmed = std.mem.trim(u8, line, " \t\r");
    if (std.mem.eql(u8, trimmed, needle)) return true;
    if (std.mem.startsWith(u8, trimmed, "- name: ")) {
        return std.mem.eql(u8, trimmed["- name: ".len..], needle);
    }
    if (std.mem.startsWith(u8, trimmed, "run: ")) {
        return std.mem.eql(u8, trimmed["run: ".len..], needle);
    }
    return false;
}

fn requireUniqueLine(workflow: []const u8, line: []const u8) !usize {
    var matches: usize = 0;
    var match_index: usize = 0;
    var cursor: usize = 0;
    var lines = std.mem.splitScalar(u8, workflow, '\n');
    while (lines.next()) |workflow_line| {
        if (workflowLineMatches(workflow_line, line)) {
            matches += 1;
            match_index = cursor;
        }
        cursor += workflow_line.len + 1;
    }
    try std.testing.expectEqual(@as(usize, 1), matches);
    return match_index;
}

fn requireOrdered(after: *usize, workflow: []const u8, line: []const u8) !void {
    const index = try requireUniqueLine(workflow, line);
    try std.testing.expect(index > after.*);
    after.* = index;
}

test "Phase 12 tail handoff into Phase 14 stays ordered and unique" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    var cursor: usize = 0;
    for (phase12_tail_steps) |step| {
        try requireOrdered(&cursor, workflow, step.name);
        try requireOrdered(&cursor, workflow, step.command);
    }
    try requireOrdered(&cursor, workflow, phase14_shared_smoke_name);
    try requireOrdered(&cursor, workflow, phase14_shared_smoke_command);
    try requireOrdered(&cursor, workflow, phase14_validate_name);
    try requireOrdered(&cursor, workflow, phase14_validate_command);
}

test "Phase 14 bridge remains between Phase 12 syntax lab and throughput anchor" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const syntax_lab = try requireUniqueLine(workflow, phase12_tail_steps[phase12_tail_steps.len - 1].name);
    const phase14_smoke = try requireUniqueLine(workflow, phase14_shared_smoke_name);
    const phase14_validate = try requireUniqueLine(workflow, phase14_validate_name);
    const throughput = try requireUniqueLine(workflow, phase12_throughput_name);
    _ = try requireUniqueLine(workflow, phase12_throughput_command);

    try std.testing.expect(syntax_lab < phase14_smoke);
    try std.testing.expect(phase14_smoke < phase14_validate);
    try std.testing.expect(phase14_validate < throughput);
}

test "Phase 12 to Phase 14 window does not silently backtrack to older phases" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const window_start = try requireUniqueLine(workflow, phase12_tail_steps[0].name);
    const window_end = try requireUniqueLine(workflow, phase12_throughput_name);
    try std.testing.expect(window_start < window_end);

    const window = workflow[window_start..window_end];
    try std.testing.expect(std.mem.indexOf(u8, window, "Phase 9 ") == null);
    try std.testing.expect(std.mem.indexOf(u8, window, "Phase 10 ") == null);
    try std.testing.expect(std.mem.indexOf(u8, window, "Phase 11 ") == null);
}
