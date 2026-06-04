const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const ContractError = error{
    MissingMarker,
    MarkerOutOfOrder,
};

const ordered_phase12_support_markers = [_][]const u8{
    "run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test\n",
    "run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py\n",
    "run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test\n",
    "run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py\n",
    "run: python3 scripts/zigux/validate-phase12.py\n",
    "run: make -C zigux phase12-smoke\n",
    "run: make -C zigux phase12-test\n",
    "run: make -C zigux phase12\n",
    "run: make -C zigux phase12-virtio-net-syntax-lab-test\n",
    "run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test\n",
};

const descriptive_step_markers = [_][]const u8{
    "Self-test current Phase 12 libbpf snapshot checker",
    "Check current Phase 12 libbpf snapshot packet",
    "Self-test current Phase 12 libbpf heavy-consumer packet checker",
    "Check current Phase 12 libbpf heavy-consumer packet",
    "Validate current Phase 12 support bundle",
    "Run current Phase 12 smoke packet",
    "Run current Phase 12 shared test packet",
    "Run current Phase 12 aggregate route",
    "Run current Phase 12 virtio_net syntax-lab companion",
    "Self-test current Phase 14 shared smoke route checker",
};

fn requireContains(haystack: []const u8, needle: []const u8) ContractError!usize {
    return std.mem.indexOf(u8, haystack, needle) orelse ContractError.MissingMarker;
}

fn requireOrdered(haystack: []const u8, markers: []const []const u8) ContractError!void {
    var previous: usize = 0;
    for (markers, 0..) |marker, index| {
        const position = try requireContains(haystack, marker);
        if (index != 0 and position <= previous) {
            return ContractError.MarkerOutOfOrder;
        }
        previous = position;
    }
}

fn validatePhase12SupportWorkflow(workflow: []const u8) ContractError!void {
    for (&descriptive_step_markers) |marker| {
        _ = try requireContains(workflow, marker);
    }
    try requireOrdered(workflow, &ordered_phase12_support_markers);
}

pub fn main(init: std.process.Init) !void {
    const workflow = try std.Io.Dir.cwd().readFileAlloc(init.io, workflow_path, init.gpa, .limited(1024 * 1024));
    defer init.gpa.free(workflow);

    validatePhase12SupportWorkflow(workflow) catch |err| {
        std.debug.print("LANE05_PHASE12_SUPPORT_WORKFLOW_CONTRACT=fail\n", .{});
        std.debug.print("LANE05_PHASE12_SUPPORT_WORKFLOW_CONTRACT_NOTE={s}\n", .{@errorName(err)});
        return err;
    };

    std.debug.print("LANE05_PHASE12_SUPPORT_WORKFLOW_CONTRACT=pass\n", .{});
    std.debug.print("LANE05_PHASE12_SUPPORT_WORKFLOW_CONTRACT_MARKER_COUNT={d}\n", .{ordered_phase12_support_markers.len + descriptive_step_markers.len});
}

test "accepts current phase12 support workflow cluster" {
    const workflow =
        \\      - name: Self-test current Phase 12 libbpf snapshot checker
        \\        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test
        \\
        \\      - name: Check current Phase 12 libbpf snapshot packet
        \\        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py
        \\
        \\      - name: Self-test current Phase 12 libbpf heavy-consumer packet checker
        \\        run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test
        \\
        \\      - name: Check current Phase 12 libbpf heavy-consumer packet
        \\        run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py
        \\
        \\      - name: Validate current Phase 12 support bundle
        \\        run: python3 scripts/zigux/validate-phase12.py
        \\
        \\      - name: Run current Phase 12 smoke packet
        \\        run: make -C zigux phase12-smoke
        \\
        \\      - name: Run current Phase 12 shared test packet
        \\        run: make -C zigux phase12-test
        \\
        \\      - name: Run current Phase 12 aggregate route
        \\        run: make -C zigux phase12
        \\
        \\      - name: Run current Phase 12 virtio_net syntax-lab companion
        \\        run: make -C zigux phase12-virtio-net-syntax-lab-test
        \\
        \\      - name: Self-test current Phase 14 shared smoke route checker
        \\        run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
        \\
    ;

    try validatePhase12SupportWorkflow(workflow);
}

test "rejects missing heavy consumer checker route" {
    const workflow =
        \\      - name: Self-test current Phase 12 libbpf snapshot checker
        \\        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test
        \\      - name: Check current Phase 12 libbpf snapshot packet
        \\        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py
        \\      - name: Validate current Phase 12 support bundle
        \\        run: python3 scripts/zigux/validate-phase12.py
        \\      - name: Run current Phase 12 smoke packet
        \\        run: make -C zigux phase12-smoke
        \\      - name: Run current Phase 12 shared test packet
        \\        run: make -C zigux phase12-test
        \\      - name: Run current Phase 12 aggregate route
        \\        run: make -C zigux phase12
        \\      - name: Run current Phase 12 virtio_net syntax-lab companion
        \\        run: make -C zigux phase12-virtio-net-syntax-lab-test
        \\      - name: Self-test current Phase 14 shared smoke route checker
        \\        run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
        \\
    ;

    try std.testing.expectError(ContractError.MissingMarker, validatePhase12SupportWorkflow(workflow));
}

test "rejects aggregate before shared test route" {
    const workflow =
        \\      - name: Self-test current Phase 12 libbpf snapshot checker
        \\        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test
        \\      - name: Check current Phase 12 libbpf snapshot packet
        \\        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py
        \\      - name: Self-test current Phase 12 libbpf heavy-consumer packet checker
        \\        run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test
        \\      - name: Check current Phase 12 libbpf heavy-consumer packet
        \\        run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py
        \\      - name: Validate current Phase 12 support bundle
        \\        run: python3 scripts/zigux/validate-phase12.py
        \\      - name: Run current Phase 12 smoke packet
        \\        run: make -C zigux phase12-smoke
        \\      - name: Run current Phase 12 aggregate route
        \\        run: make -C zigux phase12
        \\      - name: Run current Phase 12 shared test packet
        \\        run: make -C zigux phase12-test
        \\      - name: Run current Phase 12 virtio_net syntax-lab companion
        \\        run: make -C zigux phase12-virtio-net-syntax-lab-test
        \\      - name: Self-test current Phase 14 shared smoke route checker
        \\        run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
        \\
    ;

    try std.testing.expectError(ContractError.MarkerOutOfOrder, validatePhase12SupportWorkflow(workflow));
}

test "rejects phase14 handoff before syntax lab companion" {
    const workflow =
        \\      - name: Self-test current Phase 12 libbpf snapshot checker
        \\        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test
        \\      - name: Check current Phase 12 libbpf snapshot packet
        \\        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py
        \\      - name: Self-test current Phase 12 libbpf heavy-consumer packet checker
        \\        run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test
        \\      - name: Check current Phase 12 libbpf heavy-consumer packet
        \\        run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py
        \\      - name: Validate current Phase 12 support bundle
        \\        run: python3 scripts/zigux/validate-phase12.py
        \\      - name: Run current Phase 12 smoke packet
        \\        run: make -C zigux phase12-smoke
        \\      - name: Run current Phase 12 shared test packet
        \\        run: make -C zigux phase12-test
        \\      - name: Run current Phase 12 aggregate route
        \\        run: make -C zigux phase12
        \\      - name: Self-test current Phase 14 shared smoke route checker
        \\        run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
        \\      - name: Run current Phase 12 virtio_net syntax-lab companion
        \\        run: make -C zigux phase12-virtio-net-syntax-lab-test
        \\
    ;

    try std.testing.expectError(ContractError.MarkerOutOfOrder, validatePhase12SupportWorkflow(workflow));
}
