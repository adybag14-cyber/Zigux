const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const phase3_tail_markers = [_][]const u8{
    "      - name: Run current Phase 3 shared tests-root packet\n        run: zig build phase3-test --build-file zigux/tests/build.zig",
    "      - name: Run current Phase 3 ABI dump replay\n        run: zig build phase3-dump --build-file zigux/tests/build.zig",
    "      - name: Run current Phase 1 shared tests-root smoke\n        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
};

const phase4_entry_markers = [_][]const u8{
    "      - name: Self-test current Phase 4 repo-reality warning checker\n        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
    "      - name: Check current Phase 4 repo-reality warning packet\n        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py",
    "      - name: Self-test current Phase 4 reversible-delivery pin checker\n        run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test",
    "      - name: Check current Phase 4 reversible-delivery pin packet\n        run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "      - name: Self-test current Phase 4 tests README checker\n        run: python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test",
    "      - name: Check current Phase 4 tests README packet\n        run: python3 scripts/zigux/check-phase4-tests-readme-packet.py",
};

const phase4_rollback_markers = [_][]const u8{
    "      - name: Validate Phase 4 rollback routes\n        run: make -C zigux phase4-validate",
    "      - name: Run Phase 4 rollback tests\n        run: make -C zigux phase4-test",
    "      - name: Run Phase 4 artifact-diff contract make route\n        run: make -C zigux phase4-artifact-diff-contract",
};

const phase4_artifact_diff_markers = [_][]const u8{
    "      - name: Self-test current Phase 4 artifact-diff helper\n        run: python3 scripts/zigux/artifact_diff.py --self-test",
    "      - name: Self-test current Phase 4 artifact-diff contract checker\n        run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
    "      - name: Check current Phase 4 artifact-diff contract packet\n        run: python3 scripts/zigux/check-artifact-diff-contract.py",
    "      - name: Self-test current Phase 4 artifact-diff determinism checker\n        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "      - name: Check current Phase 4 artifact-diff determinism packet\n        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "      - name: Self-test current Phase 4 artifact-diff validator replay checker\n        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
    "      - name: Check current Phase 4 artifact-diff validator replay packet\n        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
};

const phase6_entry_marker =
    "      - name: Validate current Phase 6 helper packet\n        run: make -C zigux phase6-validate";

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

test "phase4 entry checks follow phase3 tail and precede rollback routes" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase3_tail_markers);
    try expectOrdered(workflow_source, &phase4_entry_markers);
    try expectOrdered(workflow_source, &phase4_rollback_markers);

    const phase3_tail_end = try markerIndex(workflow_source, phase3_tail_markers[phase3_tail_markers.len - 1]);
    const phase4_entry_start = try markerIndex(workflow_source, phase4_entry_markers[0]);
    const phase4_entry_end = try markerIndex(workflow_source, phase4_entry_markers[phase4_entry_markers.len - 1]);
    const rollback_start = try markerIndex(workflow_source, phase4_rollback_markers[0]);

    try std.testing.expect(phase3_tail_end < phase4_entry_start);
    try std.testing.expect(phase4_entry_end < rollback_start);
}

test "phase4 rollback routes stay grouped before artifact diff validation" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase4_rollback_markers);
    try expectOrdered(workflow_source, &phase4_artifact_diff_markers);

    const rollback_validate = try markerIndex(workflow_source, phase4_rollback_markers[0]);
    const rollback_test = try markerIndex(workflow_source, phase4_rollback_markers[1]);
    const artifact_route = try markerIndex(workflow_source, phase4_rollback_markers[2]);
    const artifact_helper = try markerIndex(workflow_source, phase4_artifact_diff_markers[0]);

    try std.testing.expect(rollback_validate < rollback_test);
    try std.testing.expect(rollback_test < artifact_route);
    try std.testing.expect(artifact_route < artifact_helper);
}

test "phase4 artifact-diff tail remains ordered ahead of phase6 entry" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase4_artifact_diff_markers);

    const artifact_diff_start = try markerIndex(workflow_source, phase4_artifact_diff_markers[0]);
    const artifact_diff_tail = try markerIndex(workflow_source, phase4_artifact_diff_markers[phase4_artifact_diff_markers.len - 1]);
    const phase6_entry = try markerIndex(workflow_source, phase6_entry_marker);

    try std.testing.expect(artifact_diff_start < artifact_diff_tail);
    try std.testing.expect(artifact_diff_tail < phase6_entry);
}
