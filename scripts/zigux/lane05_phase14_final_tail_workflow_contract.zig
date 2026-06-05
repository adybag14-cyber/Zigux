const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const Marker = struct {
    label: []const u8,
    text: []const u8,
};

const final_tail_markers = [_]Marker{
    .{
        .label = "phase14 shared smoke checker self-test step",
        .text = "- name: Self-test current Phase 14 shared smoke route checker",
    },
    .{
        .label = "phase14 shared smoke checker self-test command",
        .text = "python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    },
    .{
        .label = "phase14 validate route step",
        .text = "- name: Run current Phase 14 validate route",
    },
    .{
        .label = "phase14 validate route command",
        .text = "make -C zigux phase14-validate",
    },
    .{
        .label = "phase12 throughput parity anchor step",
        .text = "- name: Run current Phase 12 throughput-parity anchor",
    },
    .{
        .label = "phase12 throughput parity anchor command",
        .text = "zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
    },
};

const ContractReport = struct {
    marker_count: usize,
};

fn requireOrderedMarkers(workflow: []const u8, markers: []const Marker) !usize {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = std.mem.indexOfPos(u8, workflow, cursor, marker.text) orelse {
            std.debug.print("missing or reordered Lane 05 Phase 14 final-tail marker: {s}\n", .{marker.label});
            return error.MissingLane05Phase14FinalTailMarker;
        };
        cursor = found + marker.text.len;
    }
    return cursor;
}

fn requireNoLaterWorkflowStep(workflow: []const u8, cursor: usize) !void {
    if (std.mem.indexOf(u8, workflow[cursor..], "\n      - name: ") != null) {
        std.debug.print("unexpected bootstrap workflow step after Phase 12 throughput-parity final anchor\n", .{});
        return error.UnexpectedLane05StepAfterFinalAnchor;
    }
}

fn evaluate(workflow: []const u8) !ContractReport {
    const cursor = try requireOrderedMarkers(workflow, final_tail_markers[0..]);
    try requireNoLaterWorkflowStep(workflow, cursor);
    return .{ .marker_count = final_tail_markers.len };
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.arena.allocator();
    const workflow = try std.Io.Dir.cwd().readFileAlloc(init.io, workflow_path, allocator, .limited(1024 * 1024));
    const report = try evaluate(workflow);

    var stdout_buffer: [256]u8 = undefined;
    var stdout_writer = std.Io.File.stdout().writer(init.io, &stdout_buffer);
    try stdout_writer.interface.print("LANE05_PHASE14_FINAL_TAIL_WORKFLOW_CONTRACT=pass\n", .{});
    try stdout_writer.interface.print("LANE05_PHASE14_FINAL_TAIL_WORKFLOW_CONTRACT_MARKER_COUNT={d}\n", .{report.marker_count});
    try stdout_writer.interface.flush();
}

test "accepts current Phase 14 final-tail workflow markers" {
    const workflow =
        \\      - name: Self-test current Phase 14 shared smoke route checker
        \\        run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
        \\
        \\      - name: Run current Phase 14 validate route
        \\        run: make -C zigux phase14-validate
        \\
        \\      - name: Run current Phase 12 throughput-parity anchor
        \\        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all
        \\
    ;

    const report = try evaluate(workflow);
    try std.testing.expectEqual(@as(usize, 6), report.marker_count);
}

test "rejects reordered final-tail commands" {
    const workflow =
        \\      - name: Run current Phase 14 validate route
        \\        run: make -C zigux phase14-validate
        \\
        \\      - name: Self-test current Phase 14 shared smoke route checker
        \\        run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
        \\
        \\      - name: Run current Phase 12 throughput-parity anchor
        \\        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all
        \\
    ;

    try std.testing.expectError(error.MissingLane05Phase14FinalTailMarker, evaluate(workflow));
}

test "rejects later workflow steps after throughput anchor" {
    const workflow =
        \\      - name: Self-test current Phase 14 shared smoke route checker
        \\        run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
        \\
        \\      - name: Run current Phase 14 validate route
        \\        run: make -C zigux phase14-validate
        \\
        \\      - name: Run current Phase 12 throughput-parity anchor
        \\        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all
        \\
        \\      - name: Unexpected later step
        \\        run: echo late
        \\
    ;

    try std.testing.expectError(error.UnexpectedLane05StepAfterFinalAnchor, evaluate(workflow));
}
