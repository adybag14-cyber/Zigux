const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const ContractError = error{
    MissingMarker,
    MarkerOutOfOrder,
};

const ordered_tail_markers = [_][]const u8{
    "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test\n",
    "run: python3 scripts/zigux/check-phase12-release-readiness-packet.py\n",
    "run: python3 scripts/zigux/validate-phase12.py\n",
    "run: make -C zigux phase12-smoke\n",
    "run: make -C zigux phase12-test\n",
    "run: make -C zigux phase12\n",
    "run: make -C zigux phase12-virtio-net-syntax-lab-test\n",
    "run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test\n",
    "run: make -C zigux phase14-validate\n",
    "run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all\n",
};

const descriptive_step_markers = [_][]const u8{
    "Self-test current Phase 12 release-readiness packet checker",
    "Validate current Phase 12 support bundle",
    "Run current Phase 12 aggregate route",
    "Self-test current Phase 14 shared smoke route checker",
    "Run current Phase 14 validate route",
    "Run current Phase 12 throughput-parity anchor",
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

fn validateTailPhaseRoutes(workflow: []const u8) ContractError!void {
    for (&descriptive_step_markers) |marker| {
        _ = try requireContains(workflow, marker);
    }
    try requireOrdered(workflow, &ordered_tail_markers);
}

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    defer _ = gpa.deinit();
    const allocator = gpa.allocator();

    const workflow = try std.fs.cwd().readFileAlloc(allocator, workflow_path, 1024 * 1024);
    defer allocator.free(workflow);

    validateTailPhaseRoutes(workflow) catch |err| {
        std.debug.print("LANE05_BOOTSTRAP_TAIL_PHASE_ROUTES_CONTRACT=fail\n", .{});
        std.debug.print("LANE05_BOOTSTRAP_TAIL_PHASE_ROUTES_CONTRACT_NOTE={s}\n", .{@errorName(err)});
        return err;
    };

    std.debug.print("LANE05_BOOTSTRAP_TAIL_PHASE_ROUTES_CONTRACT=pass\n", .{});
    std.debug.print("LANE05_BOOTSTRAP_TAIL_PHASE_ROUTES_CONTRACT_MARKER_COUNT={d}\n", .{ordered_tail_markers.len + descriptive_step_markers.len});
}

test "accepts current tail phase route cluster" {
    const workflow =
        \\      - name: Self-test current Phase 12 release-readiness packet checker
        \\        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test
        \\
        \\      - name: Check current Phase 12 release-readiness packet
        \\        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py
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
        \\      - name: Run current Phase 14 validate route
        \\        run: make -C zigux phase14-validate
        \\
        \\      - name: Run current Phase 12 throughput-parity anchor
        \\        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all
        \\
    ;

    try validateTailPhaseRoutes(workflow);
}

test "rejects missing phase14 validator route" {
    const workflow =
        \\      - name: Self-test current Phase 12 release-readiness packet checker
        \\        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test
        \\      - name: Check current Phase 12 release-readiness packet
        \\        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py
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
        \\      - name: Run current Phase 12 throughput-parity anchor
        \\        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all
        \\
    ;

    try std.testing.expectError(ContractError.MissingMarker, validateTailPhaseRoutes(workflow));
}

test "rejects throughput anchor before phase14 validation" {
    const workflow =
        \\      - name: Self-test current Phase 12 release-readiness packet checker
        \\        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test
        \\      - name: Check current Phase 12 release-readiness packet
        \\        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py
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
        \\      - name: Run current Phase 12 throughput-parity anchor
        \\        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all
        \\      - name: Self-test current Phase 14 shared smoke route checker
        \\        run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test
        \\      - name: Run current Phase 14 validate route
        \\        run: make -C zigux phase14-validate
        \\
    ;

    try std.testing.expectError(ContractError.MarkerOutOfOrder, validateTailPhaseRoutes(workflow));
}
