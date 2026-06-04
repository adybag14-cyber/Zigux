const std = @import("std");

const phase3_tail_markers = [_][]const u8{
    "      - name: Run current Phase 3 shared tests-root packet\n        run: zig build phase3-test --build-file zigux/tests/build.zig",
    "      - name: Run current Phase 3 ABI dump replay\n        run: zig build phase3-dump --build-file zigux/tests/build.zig",
    "      - name: Run current Phase 1 shared tests-root smoke\n        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
};

const phase4_markers = [_][]const u8{
    "      - name: Self-test current Phase 4 repo-reality warning checker\n        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
    "      - name: Check current Phase 4 repo-reality warning packet\n        run: python3 scripts/zigux/check-phase4-repo-reality-warning.py",
    "      - name: Self-test current Phase 4 reversible-delivery pin checker\n        run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test",
    "      - name: Check current Phase 4 reversible-delivery pin packet\n        run: python3 scripts/zigux/check-phase4-reversible-delivery-pins.py",
    "      - name: Self-test current Phase 4 tests README checker\n        run: python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test",
    "      - name: Check current Phase 4 tests README packet\n        run: python3 scripts/zigux/check-phase4-tests-readme-packet.py",
    "      - name: Validate Phase 4 rollback routes\n        run: make -C zigux phase4-validate",
    "      - name: Run Phase 4 rollback tests\n        run: make -C zigux phase4-test",
    "      - name: Run Phase 4 artifact-diff contract make route\n        run: make -C zigux phase4-artifact-diff-contract",
    "      - name: Self-test current Phase 4 artifact-diff helper\n        run: python3 scripts/zigux/artifact_diff.py --self-test",
    "      - name: Self-test current Phase 4 artifact-diff contract checker\n        run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
    "      - name: Check current Phase 4 artifact-diff contract packet\n        run: python3 scripts/zigux/check-artifact-diff-contract.py",
    "      - name: Self-test current Phase 4 artifact-diff determinism checker\n        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "      - name: Check current Phase 4 artifact-diff determinism packet\n        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "      - name: Self-test current Phase 4 artifact-diff validator replay checker\n        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
    "      - name: Check current Phase 4 artifact-diff validator replay packet\n        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
};

const later_route_markers = [_][]const u8{
    "      - name: Validate current Phase 6 helper packet\n        run: make -C zigux phase6-validate",
    "      - name: Run current Phase 6 leaf helper tests\n        run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
    "      - name: Validate Phase 8 tooling routes\n        run: make -C zigux phase8-validate",
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

test "phase3 shared routes hand off to phase4 rollback gates before later phase routes" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase3_tail_markers);
    try expectOrdered(workflow_source, &phase4_markers);
    try expectOrdered(workflow_source, &later_route_markers);

    const phase3_tail_end = try markerIndex(workflow_source, phase3_tail_markers[phase3_tail_markers.len - 1]);
    const phase4_start = try markerIndex(workflow_source, phase4_markers[0]);
    const phase4_end = try markerIndex(workflow_source, phase4_markers[phase4_markers.len - 1]);
    const phase6_start = try markerIndex(workflow_source, later_route_markers[0]);

    try std.testing.expect(phase3_tail_end < phase4_start);
    try std.testing.expect(phase4_end < phase6_start);
}

test "phase4 rollback gates stay ahead of artifact-diff gates" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    const rollback_validate = try markerIndex(workflow_source, "      - name: Validate Phase 4 rollback routes\n        run: make -C zigux phase4-validate");
    const rollback_tests = try markerIndex(workflow_source, "      - name: Run Phase 4 rollback tests\n        run: make -C zigux phase4-test");
    const artifact_route = try markerIndex(workflow_source, "      - name: Run Phase 4 artifact-diff contract make route\n        run: make -C zigux phase4-artifact-diff-contract");
    const artifact_helper = try markerIndex(workflow_source, "      - name: Self-test current Phase 4 artifact-diff helper\n        run: python3 scripts/zigux/artifact_diff.py --self-test");

    try std.testing.expect(rollback_validate < rollback_tests);
    try std.testing.expect(rollback_tests < artifact_route);
    try std.testing.expect(artifact_route < artifact_helper);
}

test "phase4 artifact-diff live packet keeps helper self-tests before packet checks" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    const artifact_contract_selftest = try markerIndex(workflow_source, "      - name: Self-test current Phase 4 artifact-diff contract checker\n        run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test");
    const artifact_contract_check = try markerIndex(workflow_source, "      - name: Check current Phase 4 artifact-diff contract packet\n        run: python3 scripts/zigux/check-artifact-diff-contract.py");
    const determinism_selftest = try markerIndex(workflow_source, "      - name: Self-test current Phase 4 artifact-diff determinism checker\n        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test");
    const determinism_check = try markerIndex(workflow_source, "      - name: Check current Phase 4 artifact-diff determinism packet\n        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py");
    const replay_selftest = try markerIndex(workflow_source, "      - name: Self-test current Phase 4 artifact-diff validator replay checker\n        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test");
    const replay_check = try markerIndex(workflow_source, "      - name: Check current Phase 4 artifact-diff validator replay packet\n        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py");

    try std.testing.expect(artifact_contract_selftest < artifact_contract_check);
    try std.testing.expect(artifact_contract_check < determinism_selftest);
    try std.testing.expect(determinism_selftest < determinism_check);
    try std.testing.expect(determinism_check < replay_selftest);
    try std.testing.expect(replay_selftest < replay_check);
}
