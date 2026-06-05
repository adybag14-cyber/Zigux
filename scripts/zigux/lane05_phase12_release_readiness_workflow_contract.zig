const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const phase12_front_markers = [_][]const u8{
    "      - name: Self-test current Phase 12 build-only surface checker\n        run: python3 scripts/zigux/check-build-only-phase12-surface.py --self-test",
    "      - name: Check current Phase 12 build-only surface\n        run: python3 scripts/zigux/check-build-only-phase12-surface.py",
    "      - name: Self-test current Phase 12 build inventory checker\n        run: python3 scripts/zigux/check-phase12-build-inventory.py --self-test",
    "      - name: Check current Phase 12 build inventory packet\n        run: python3 scripts/zigux/check-phase12-build-inventory.py",
    "      - name: Self-test current Phase 12 complex-driver lane packet checker\n        run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py --self-test",
    "      - name: Check current Phase 12 complex-driver lane packet\n        run: python3 scripts/zigux/check-phase12-complex-driver-lane-packet.py",
    "      - name: Self-test current Phase 12 cross-compile smoke checker\n        run: python3 scripts/zigux/check-phase12-cross-compile-smoke.py --self-test",
    "      - name: Check current Phase 12 cross-compile smoke packet\n        run: python3 scripts/zigux/check-phase12-cross-compile-smoke.py",
};

const phase12_release_markers = [_][]const u8{
    "      - name: Self-test current Phase 12 release-readiness packet checker\n        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
    "      - name: Check current Phase 12 release-readiness packet\n        run: python3 scripts/zigux/check-phase12-release-readiness-packet.py",
};

const phase12_libbpf_support_markers = [_][]const u8{
    "      - name: Self-test current Phase 12 libbpf snapshot checker\n        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test",
    "      - name: Check current Phase 12 libbpf snapshot packet\n        run: python3 scripts/zigux/check-phase12-libbpf-snapshot.py",
    "      - name: Self-test current Phase 12 libbpf heavy-consumer packet checker\n        run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test",
    "      - name: Check current Phase 12 libbpf heavy-consumer packet\n        run: python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py",
    "      - name: Validate current Phase 12 support bundle\n        run: python3 scripts/zigux/validate-phase12.py",
};

const phase12_route_markers = [_][]const u8{
    "      - name: Run current Phase 12 smoke packet\n        run: make -C zigux phase12-smoke",
    "      - name: Run current Phase 12 shared test packet\n        run: make -C zigux phase12-test",
    "      - name: Run current Phase 12 aggregate route\n        run: make -C zigux phase12",
    "      - name: Run current Phase 12 virtio_net syntax-lab companion\n        run: make -C zigux phase12-virtio-net-syntax-lab-test",
};

const phase14_entry_marker =
    "      - name: Self-test current Phase 14 shared smoke route checker\n        run: python3 scripts/zigux/check-phase14-shared-smoke-route.py --self-test";

fn readWorkflowSource(allocator: std.mem.Allocator) ![]u8 {
    return try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        allocator,
        .limited(1024 * 1024),
    );
}

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

test "phase12 release readiness remains after early phase12 packet checks" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase12_front_markers);
    try expectOrdered(workflow_source, &phase12_release_markers);

    const cross_smoke_check = try markerIndex(workflow_source, phase12_front_markers[phase12_front_markers.len - 1]);
    const release_selftest = try markerIndex(workflow_source, phase12_release_markers[0]);
    const release_check = try markerIndex(workflow_source, phase12_release_markers[phase12_release_markers.len - 1]);

    try std.testing.expect(cross_smoke_check < release_selftest);
    try std.testing.expect(release_selftest < release_check);
}

test "phase12 libbpf support checks stay between release readiness and validation" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase12_libbpf_support_markers);

    const release_check = try markerIndex(workflow_source, phase12_release_markers[phase12_release_markers.len - 1]);
    const libbpf_snapshot_selftest = try markerIndex(workflow_source, phase12_libbpf_support_markers[0]);
    const validate_phase12 = try markerIndex(workflow_source, phase12_libbpf_support_markers[phase12_libbpf_support_markers.len - 1]);

    try std.testing.expect(release_check < libbpf_snapshot_selftest);
    try std.testing.expect(libbpf_snapshot_selftest < validate_phase12);
}

test "phase12 executable routes remain before the phase14 handoff" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase12_route_markers);

    const validate_phase12 = try markerIndex(workflow_source, phase12_libbpf_support_markers[phase12_libbpf_support_markers.len - 1]);
    const smoke_route = try markerIndex(workflow_source, phase12_route_markers[0]);
    const syntax_lab = try markerIndex(workflow_source, phase12_route_markers[phase12_route_markers.len - 1]);
    const phase14_entry = try markerIndex(workflow_source, phase14_entry_marker);

    try std.testing.expect(validate_phase12 < smoke_route);
    try std.testing.expect(smoke_route < syntax_lab);
    try std.testing.expect(syntax_lab < phase14_entry);
}
