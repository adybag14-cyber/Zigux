const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const phase2_to_phase1_handoff_marker =
    "      - name: Check current Phase 2 closure packet\n        run: python3 scripts/zigux/validate-phase2-closure.py";

const direct_owner_markers = [_][]const u8{
    "      - name: Self-test current Phase 1 direct-owner checker\n        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test",
    "      - name: Check current Phase 1 direct-owner markers\n        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py",
    "      - name: Self-test current Phase 1 direct-anchor manifest gate\n        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test",
    "      - name: Check current Phase 1 direct-anchor manifest gate\n        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py",
};

const review_packet_markers = [_][]const u8{
    "      - name: Self-test current Phase 1 string review checker\n        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test",
    "      - name: Check current Phase 1 string review packet\n        run: python3 scripts/zigux/check-phase1-string-review-packet.py",
    "      - name: Self-test current Phase 1 find-bit review checker\n        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py --self-test",
    "      - name: Check current Phase 1 find-bit review packet\n        run: python3 scripts/zigux/check-phase1-find-bit-review-packet.py",
    "      - name: Self-test current Phase 1 bitmap direct-anchor checker\n        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py --self-test",
    "      - name: Check current Phase 1 bitmap direct-anchor packet\n        run: python3 scripts/zigux/check-phase1-bitmap-direct-anchors.py",
    "      - name: Self-test current Phase 1 rbtree review checker\n        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py --self-test",
    "      - name: Check current Phase 1 rbtree review packet\n        run: python3 scripts/zigux/check-phase1-rbtree-review-packet.py",
};

const bench_closure_markers = [_][]const u8{
    "      - name: Self-test current Phase 1 route summary checker\n        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test",
    "      - name: Check current Phase 1 route summary packet\n        run: python3 scripts/zigux/check-phase1-route-summary-counts.py",
    "      - name: Self-test current Phase 1 bench checker\n        run: python3 scripts/zigux/check-phase1-bench.py --self-test",
    "      - name: Check current Phase 1 bench packet\n        run: python3 scripts/zigux/check-phase1-bench.py",
    "      - name: Self-test current Phase 1 bench live-check workflow guard\n        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py --self-test",
    "      - name: Check current Phase 1 bench live-check workflow guard packet\n        run: python3 scripts/zigux/check-phase1-bench-live-check-workflow.py",
    "      - name: Self-test current Phase 1 find-bit bench anchor checker\n        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py --self-test",
    "      - name: Check current Phase 1 find-bit bench anchor packet\n        run: python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py",
    "      - name: Self-test current Phase 1 shared reminder checker\n        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test",
    "      - name: Check current Phase 1 shared reminder packet\n        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py",
    "      - name: Self-test current Phase 1 closure validator\n        run: python3 scripts/zigux/validate-phase1-closure.py --self-test",
    "      - name: Check current Phase 1 closure packet\n        run: python3 scripts/zigux/validate-phase1-closure.py",
};

const phase3_handoff_marker =
    "      - name: Self-test current Phase 3 interop packet\n        run: python3 scripts/zigux/validate_phase3_selftest.py";

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

test "phase1 direct-owner gates follow phase2 closure" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &direct_owner_markers);

    const phase2_closure = try markerIndex(workflow_source, phase2_to_phase1_handoff_marker);
    const direct_owner_start = try markerIndex(workflow_source, direct_owner_markers[0]);
    const direct_anchor_check = try markerIndex(workflow_source, direct_owner_markers[direct_owner_markers.len - 1]);

    try std.testing.expect(phase2_closure < direct_owner_start);
    try std.testing.expect(direct_owner_start < direct_anchor_check);
}

test "phase1 review packets stay between direct anchors and route summary" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &review_packet_markers);

    const direct_anchor_tail = try markerIndex(workflow_source, direct_owner_markers[direct_owner_markers.len - 1]);
    const review_start = try markerIndex(workflow_source, review_packet_markers[0]);
    const review_tail = try markerIndex(workflow_source, review_packet_markers[review_packet_markers.len - 1]);
    const route_summary_start = try markerIndex(workflow_source, bench_closure_markers[0]);

    try std.testing.expect(direct_anchor_tail < review_start);
    try std.testing.expect(review_start < review_tail);
    try std.testing.expect(review_tail < route_summary_start);
}

test "phase1 bench and closure gates hand off to phase3" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &bench_closure_markers);

    const bench_start = try markerIndex(workflow_source, bench_closure_markers[2]);
    const closure_tail = try markerIndex(workflow_source, bench_closure_markers[bench_closure_markers.len - 1]);
    const phase3_handoff = try markerIndex(workflow_source, phase3_handoff_marker);

    try std.testing.expect(bench_start < closure_tail);
    try std.testing.expect(closure_tail < phase3_handoff);
}
