const std = @import("std");
const Io = std.Io;

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const Anchor = struct {
    step: []const u8,
    command: []const u8,
};

const phase12_validate = Anchor{
    .step = "- name: Validate current Phase 12 support bundle",
    .command = "run: python3 scripts/zigux/validate-phase12.py",
};

const phase12_smoke = Anchor{
    .step = "- name: Run current Phase 12 smoke packet",
    .command = "run: make -C zigux phase12-smoke",
};

const phase12_shared = Anchor{
    .step = "- name: Run current Phase 12 shared test packet",
    .command = "run: make -C zigux phase12-test",
};

const phase12_aggregate = Anchor{
    .step = "- name: Run current Phase 12 aggregate route",
    .command = "run: make -C zigux phase12",
};

const phase12_syntax_lab = Anchor{
    .step = "- name: Run current Phase 12 virtio_net syntax-lab companion",
    .command = "run: make -C zigux phase12-virtio-net-syntax-lab-test",
};

const phase14_smoke_selftest = Anchor{
    .step = "- name: Self-test current Phase 14 shared smoke route checker",
    .command = "run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
};

const phase14_validate = Anchor{
    .step = "- name: Run current Phase 14 validate route",
    .command = "run: make -C zigux phase14-validate",
};

const throughput_anchor = Anchor{
    .step = "- name: Run current Phase 12 throughput-parity anchor",
    .command = "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
};

fn requireContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn requireExactCount(haystack: []const u8, needle: []const u8, expected: usize) !void {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOf(u8, haystack[offset..], needle)) |relative| {
        count += 1;
        offset += relative + needle.len;
    }
    try std.testing.expectEqual(expected, count);
}

fn markerIndex(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingMarker;
}

fn requireOrder(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    try std.testing.expect(try markerIndex(haystack, earlier) < try markerIndex(haystack, later));
}

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return try Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

fn requireAnchor(workflow: []const u8, anchor: Anchor) !void {
    try requireContains(workflow, anchor.step);
    try requireContains(workflow, anchor.command);
    try requireExactCount(workflow, anchor.step, 1);
    const step_index = try markerIndex(workflow, anchor.step);
    const command_index = std.mem.indexOf(u8, workflow[step_index..], anchor.command) orelse return error.MissingMarker;
    try std.testing.expect(command_index > 0);
}

fn lastNonEmptyLine(text: []const u8) []const u8 {
    var end = text.len;
    while (end > 0 and isTrimByte(text[end - 1])) : (end -= 1) {}
    var start = end;
    while (start > 0 and text[start - 1] != '\n') : (start -= 1) {}
    while (start < end and isTrimByte(text[start])) : (start += 1) {}
    return text[start..end];
}

fn isTrimByte(byte: u8) bool {
    return byte == ' ' or byte == '\t' or byte == '\r' or byte == '\n';
}

test "phase12 throughput anchor remains the terminal bootstrap command" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireAnchor(workflow, throughput_anchor);
    try requireExactCount(workflow, throughput_anchor.command, 1);
    try std.testing.expectEqualStrings(throughput_anchor.command, lastNonEmptyLine(workflow));
}

test "phase12 support routes still hand off into phase14 validation before throughput parity" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const anchors = [_]Anchor{
        phase12_validate,
        phase12_smoke,
        phase12_shared,
        phase12_aggregate,
        phase12_syntax_lab,
        phase14_smoke_selftest,
        phase14_validate,
        throughput_anchor,
    };
    for (anchors) |anchor| {
        try requireAnchor(workflow, anchor);
    }

    try requireOrder(workflow, phase12_validate.step, phase12_smoke.step);
    try requireOrder(workflow, phase12_smoke.step, phase12_shared.step);
    try requireOrder(workflow, phase12_shared.step, phase12_aggregate.step);
    try requireOrder(workflow, phase12_aggregate.step, phase12_syntax_lab.step);
    try requireOrder(workflow, phase12_syntax_lab.step, phase14_smoke_selftest.step);
    try requireOrder(workflow, phase14_smoke_selftest.step, phase14_validate.step);
    try requireOrder(workflow, phase14_validate.step, throughput_anchor.step);
}

test "throughput parity route keeps the exact build file and summary contract" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try requireContains(workflow, "phase12-virtio-net-throughput-parity");
    try requireContains(workflow, "--build-file zigux/tests/phase12_build.zig");
    try requireContains(workflow, "--summary all");
    try requireExactCount(workflow, "phase12-virtio-net-throughput-parity", 1);
}
