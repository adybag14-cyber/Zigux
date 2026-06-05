const std = @import("std");

const phase12_checker_markers = [_][]const u8{
    "      - name: Self-test current Phase 12 build-only surface checker\n        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "      - name: Check current Phase 12 build-only surface\n        run: python3 scripts/zigux/check-build-only-phase12-surface.py",
    "      - name: Self-test current Phase 12 build inventory checker\n        run: python3 scripts/zigux/check-phase12-build-inventory.py --self-test",
    "      - name: Check current Phase 12 build inventory packet\n        run: python3 scripts/zigux/check-phase12-build-inventory.py",
    "      - name: Self-test current Phase 12 complex-driver lane packet checker\n        run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test",
    "      - name: Check current Phase 12 complex-driver lane packet\n        run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py",
    "      - name: Self-test current Phase 12 cross-compile smoke checker\n        run: python3 scripts/zigux/check-phase12-cross-compile-smoke.py --self-test",
    "      - name: Check current Phase 12 cross-compile smoke packet\n        run: python3 scripts/zigux/check-phase12-cross-compile-smoke.py",
    "      - name: Self-test current Phase 12 release-readiness packet checker\n        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "      - name: Check current Phase 12 release-readiness packet\n        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py",
    "      - name: Self-test current Phase 12 libbpf snapshot checker\n        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test",
    "      - name: Check current Phase 12 libbpf snapshot packet\n        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py",
    "      - name: Self-test current Phase 12 libbpf heavy-consumer packet checker\n        run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test",
    "      - name: Check current Phase 12 libbpf heavy-consumer packet\n        run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py",
};

const phase12_route_markers = [_][]const u8{
    "      - name: Validate current Phase 12 support bundle\n        run: python3 scripts/zigux/validate-phase12.py",
    "      - name: Run current Phase 12 smoke packet\n        run: make -C zigux phase12-smoke",
    "      - name: Run current Phase 12 shared test packet\n        run: make -C zigux phase12-test",
    "      - name: Run current Phase 12 aggregate route\n        run: make -C zigux phase12",
    "      - name: Run current Phase 12 virtio_net syntax-lab companion\n        run: make -C zigux phase12-virtio-net-syntax-lab-test",
};

const phase14_tail_markers = [_][]const u8{
    "      - name: Self-test current Phase 14 shared smoke route checker\n        run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test",
    "      - name: Run current Phase 14 validate route\n        run: make -C zigux phase14-validate",
    "      - name: Run current Phase 12 throughput-parity anchor\n        run: zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all",
};

fn markerIndex(source: []const u8, marker: []const u8) !usize {
    return std.mem.indexOf(u8, source, marker) orelse error.MissingWorkflowMarker;
}

fn expectOrdered(source: []const u8, markers: []const []const u8) !void {
    var previous: ?usize = null;
    for (markers) |marker| {
        const current = try markerIndex(source, marker);
        if (previous) |prev| {
            try std.testing.expect(current > prev);
        }
        previous = current;
    }
}

fn readWorkflowSource(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        ".github/workflows/zigux-bootstrap.yml",
        allocator,
        .limited(1024 * 1024),
    );
}

test "phase12 checker block keeps self-tests immediately ahead of live checks" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase12_checker_markers);

    var index: usize = 0;
    while (index < phase12_checker_markers.len) : (index += 2) {
        const selftest = try markerIndex(workflow_source, phase12_checker_markers[index]);
        const live_check = try markerIndex(workflow_source, phase12_checker_markers[index + 1]);
        try std.testing.expect(selftest < live_check);
    }
}

test "phase12 support routes stay after checker block and before phase14 tail" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase12_route_markers);
    try expectOrdered(workflow_source, &phase14_tail_markers);

    const checker_end = try markerIndex(workflow_source, phase12_checker_markers[phase12_checker_markers.len - 1]);
    const route_start = try markerIndex(workflow_source, phase12_route_markers[0]);
    const route_end = try markerIndex(workflow_source, phase12_route_markers[phase12_route_markers.len - 1]);
    const phase14_start = try markerIndex(workflow_source, phase14_tail_markers[0]);

    try std.testing.expect(checker_end < route_start);
    try std.testing.expect(route_end < phase14_start);
}

test "phase14 tail preserves smoke, validate, and throughput parity order" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    const phase14_smoke_selftest = try markerIndex(workflow_source, phase14_tail_markers[0]);
    const phase14_validate = try markerIndex(workflow_source, phase14_tail_markers[1]);
    const throughput_anchor = try markerIndex(workflow_source, phase14_tail_markers[2]);

    try std.testing.expect(phase14_smoke_selftest < phase14_validate);
    try std.testing.expect(phase14_validate < throughput_anchor);
}
