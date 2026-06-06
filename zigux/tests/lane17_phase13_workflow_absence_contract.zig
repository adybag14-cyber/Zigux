const std = @import("std");
const build_options = @import("build_options");

const workflow_path = build_options.workflow_path;

const Error = error{
    MissingWorkflowMarker,
    ReorderedWorkflowMarker,
    UnexpectedPhase13WorkflowMarker,
};

const phase12_tail_markers = [_][]const u8{
    "- name: Self-test current Phase 12 release-readiness packet checker",
    "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "- name: Check current Phase 12 release-readiness packet",
    "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py",
    "- name: Self-test current Phase 12 libbpf snapshot checker",
    "run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test",
    "- name: Check current Phase 12 libbpf snapshot packet",
    "run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py",
    "- name: Self-test current Phase 12 libbpf heavy-consumer packet checker",
    "run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test",
    "- name: Check current Phase 12 libbpf heavy-consumer packet",
    "run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py",
    "- name: Validate current Phase 12 support bundle",
    "run: python3 scripts/zigux/validate-phase12.py",
    "- name: Run current Phase 12 smoke packet",
    "run: make -C zigux phase12-smoke",
    "- name: Run current Phase 12 shared test packet",
    "run: make -C zigux phase12-test",
    "- name: Run current Phase 12 aggregate route",
    "run: make -C zigux phase12",
    "- name: Run current Phase 12 virtio_net syntax-lab companion",
    "run: make -C zigux phase12-virtio-net-syntax-lab-test",
};

const phase14_tail_markers = [_][]const u8{
    "- name: Self-test current Phase 14 shared smoke route checker",
    "run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "- name: Run current Phase 14 validate route",
    "run: make -C zigux phase14-validate",
    "- name: Run current Phase 12 throughput-parity anchor",
    "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
};

const forbidden_phase13_markers = [_][]const u8{
    "Phase 13",
    "phase13",
    "phase13-validate",
    "phase13-test",
    "validate-phase13",
    "check-phase13",
    "zigux/tests/phase13",
    "Documentation/zigux/phase13",
};

fn readWorkflow() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn expectNotContains(haystack: []const u8, needle: []const u8) !void {
    if (std.mem.indexOf(u8, haystack, needle) != null) {
        return Error.UnexpectedPhase13WorkflowMarker;
    }
}

fn countExactTrimmedLines(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var lines = std.mem.splitScalar(u8, haystack, '\n');
    while (lines.next()) |line| {
        if (std.mem.eql(u8, std.mem.trimStart(u8, line, " \t"), needle)) {
            count += 1;
        }
    }
    return count;
}

fn expectOnce(haystack: []const u8, needle: []const u8) !void {
    if (countExactTrimmedLines(haystack, needle) != 1) {
        return Error.MissingWorkflowMarker;
    }
}

fn expectOrdered(haystack: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = std.mem.indexOf(u8, haystack, before) orelse return Error.MissingWorkflowMarker;
    const after_index = std.mem.indexOf(u8, haystack, after) orelse return Error.MissingWorkflowMarker;
    if (before_index >= after_index) return Error.ReorderedWorkflowMarker;
}

fn verifyNoPhase13WorkflowSurface(workflow: []const u8) !void {
    inline for (forbidden_phase13_markers) |marker| {
        try expectNotContains(workflow, marker);
    }
}

fn verifyPhase12ToPhase14Boundary(workflow: []const u8) !void {
    inline for (phase12_tail_markers) |marker| {
        try expectOnce(workflow, marker);
    }
    inline for (phase14_tail_markers) |marker| {
        try expectOnce(workflow, marker);
    }

    try expectOrdered(
        workflow,
        "run: make -C zigux phase12-virtio-net-syntax-lab-test",
        "run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    );
    try expectOrdered(
        workflow,
        "run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
        "run: make -C zigux phase14-validate",
    );
    try expectOrdered(
        workflow,
        "run: make -C zigux phase14-validate",
        "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
    );
}

test "lane17 phase13 workflow absence keeps the current phase12 to phase14 boundary explicit" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    try verifyPhase12ToPhase14Boundary(workflow);
    try verifyNoPhase13WorkflowSurface(workflow);
}

test "lane17 phase13 workflow absence rejects partial phase13 step names" {
    const partial_phase13_step =
        "- name: Run current Phase 12 virtio_net syntax-lab companion\n" ++
        "  run: make -C zigux phase12-virtio-net-syntax-lab-test\n" ++
        "- name: Validate current Phase 13 shared helper packet\n" ++
        "  run: make -C zigux phase14-validate\n";

    try std.testing.expectError(
        Error.UnexpectedPhase13WorkflowMarker,
        verifyNoPhase13WorkflowSurface(partial_phase13_step),
    );
}

test "lane17 phase13 workflow absence rejects partial phase13 make routes" {
    const partial_phase13_route =
        "- name: Run current Phase 12 virtio_net syntax-lab companion\n" ++
        "  run: make -C zigux phase12-virtio-net-syntax-lab-test\n" ++
        "- name: Run current shared helper validate route\n" ++
        "  run: make -C zigux phase13-validate\n" ++
        "- name: Run current Phase 14 validate route\n" ++
        "  run: make -C zigux phase14-validate\n";

    try std.testing.expectError(
        Error.UnexpectedPhase13WorkflowMarker,
        verifyNoPhase13WorkflowSurface(partial_phase13_route),
    );
}

test "lane17 phase13 workflow absence rejects reordered phase14 handoff" {
    const reordered_tail =
        "- name: Self-test current Phase 14 shared smoke route checker\n" ++
        "run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test\n" ++
        "- name: Run current Phase 12 virtio_net syntax-lab companion\n" ++
        "run: make -C zigux phase12-virtio-net-syntax-lab-test\n" ++
        "- name: Run current Phase 14 validate route\n" ++
        "run: make -C zigux phase14-validate\n" ++
        "- name: Run current Phase 12 throughput-parity anchor\n" ++
        "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all\n";

    try std.testing.expectError(
        Error.MissingWorkflowMarker,
        verifyPhase12ToPhase14Boundary(reordered_tail),
    );
}
