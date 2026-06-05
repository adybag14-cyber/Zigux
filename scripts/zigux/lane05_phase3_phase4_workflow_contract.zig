const std = @import("std");

const phase3_entry_markers = [_][]const u8{
    "      - name: Self-test current Phase 3 interop packet\n        run: python3 scripts/zigux/validate_phase3_selftest.py",
    "      - name: Check current Phase 3 interop packet\n        run: python3 scripts/zigux/run-phase3-checks.py",
    "      - name: Run current Phase 3 export/UAPI C header smoke\n        run: python3 scripts/zigux/check-phase3-export-uapi-c-header-smoke.py",
    "      - name: Run current Phase 3 export/UAPI layout replay\n        run: zig build phase3-export-uapi-layout-test --build-file zigux/tests/phase3_export_uapi_layout_build.zig",
    "      - name: Run current Phase 3 export shim replay\n        run: zig build phase3-export-shim-test --build-file zigux/tests/phase3_export_shim_build.zig",
};

const phase3_policy_markers = [_][]const u8{
    "      - name: Run current Phase 3 policy starter-packet replay\n        run: make -C zigux phase3-policy-starter-packet-test",
    "      - name: Run current Phase 3 policy unsafe replay\n        run: zig build phase3-policy-unsafe-test --build-file zigux/tests/phase3_policy_unsafe_build.zig",
    "      - name: Run current Phase 3 policy unsafe make route\n        run: make -C zigux phase3-policy-unsafe-test",
    "      - name: Run current Phase 3 policy dump replay\n        run: zig build phase3-policy-dump --build-file zigux/tests/phase3_policy_dump_build.zig",
    "      - name: Run current Phase 3 policy dump make wrapper\n        run: make -C zigux phase3-policy-dump",
};

const phase3_low_level_markers = [_][]const u8{
    "      - name: Self-test current Phase 3 low-level wrapper survey validator\n        run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py --self-test",
    "      - name: Check current Phase 3 low-level wrapper survey packet\n        run: python3 scripts/zigux/validate-phase3-low-level-wrapper-survey.py",
    "      - name: Run current Phase 3 low-level wrapper replay\n        run: zig build phase3-low-level-wrappers-test --build-file zigux/tests/phase3_low_level_wrappers_build.zig",
    "      - name: Run current Phase 3 low-level wrapper make route\n        run: make -C zigux phase3-low-level-wrappers",
    "      - name: Run current Phase 3 focused low-level wrapper make route\n        run: make -C zigux phase3-low-level-wrappers-test",
};

const phase3_shared_test_markers = [_][]const u8{
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

const phase4_route_markers = [_][]const u8{
    "      - name: Validate Phase 4 rollback routes\n        run: make -C zigux phase4-validate",
    "      - name: Run Phase 4 rollback tests\n        run: make -C zigux phase4-test",
    "      - name: Run Phase 4 artifact-diff contract make route\n        run: make -C zigux phase4-artifact-diff-contract",
    "      - name: Self-test current Phase 4 artifact-diff helper\n        run: python3 scripts/zigux/artifact_diff.py --self-test",
    "      - name: Self-test current Phase 4 artifact-diff contract checker\n        run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
    "      - name: Check current Phase 4 artifact-diff contract packet\n        run: python3 scripts/zigux/check-artifact-diff-contract.py",
};

const phase4_tail_markers = [_][]const u8{
    "      - name: Self-test current Phase 4 artifact-diff determinism checker\n        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
    "      - name: Check current Phase 4 artifact-diff determinism packet\n        run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
    "      - name: Self-test current Phase 4 artifact-diff validator replay checker\n        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
    "      - name: Check current Phase 4 artifact-diff validator replay packet\n        run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
};

const phase6_entry_marker =
    "      - name: Validate current Phase 6 helper packet\n        run: make -C zigux phase6-validate";

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

test "phase3 workflow block keeps interop, policy, low-level, and shared routes ordered" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase3_entry_markers);
    try expectOrdered(workflow_source, &phase3_policy_markers);
    try expectOrdered(workflow_source, &phase3_low_level_markers);
    try expectOrdered(workflow_source, &phase3_shared_test_markers);

    const entry_end = try markerIndex(workflow_source, phase3_entry_markers[phase3_entry_markers.len - 1]);
    const policy_start = try markerIndex(workflow_source, phase3_policy_markers[0]);
    const policy_end = try markerIndex(workflow_source, phase3_policy_markers[phase3_policy_markers.len - 1]);
    const low_level_start = try markerIndex(workflow_source, phase3_low_level_markers[0]);
    const low_level_end = try markerIndex(workflow_source, phase3_low_level_markers[phase3_low_level_markers.len - 1]);
    const shared_start = try markerIndex(workflow_source, phase3_shared_test_markers[0]);

    try std.testing.expect(entry_end < policy_start);
    try std.testing.expect(policy_end < low_level_start);
    try std.testing.expect(low_level_end < shared_start);
}

test "phase3 shared smoke hands off to phase4 repo-reality and reversible-delivery gates" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase3_shared_test_markers);
    try expectOrdered(workflow_source, &phase4_entry_markers);

    const phase3_shared_end = try markerIndex(workflow_source, phase3_shared_test_markers[phase3_shared_test_markers.len - 1]);
    const phase4_entry_start = try markerIndex(workflow_source, phase4_entry_markers[0]);

    try std.testing.expect(phase3_shared_end < phase4_entry_start);
}

test "phase4 workflow block keeps rollback, artifact-diff, and determinism gates before phase6" {
    const workflow_source = try readWorkflowSource(std.testing.allocator);
    defer std.testing.allocator.free(workflow_source);

    try expectOrdered(workflow_source, &phase4_entry_markers);
    try expectOrdered(workflow_source, &phase4_route_markers);
    try expectOrdered(workflow_source, &phase4_tail_markers);

    const entry_end = try markerIndex(workflow_source, phase4_entry_markers[phase4_entry_markers.len - 1]);
    const route_start = try markerIndex(workflow_source, phase4_route_markers[0]);
    const route_end = try markerIndex(workflow_source, phase4_route_markers[phase4_route_markers.len - 1]);
    const tail_start = try markerIndex(workflow_source, phase4_tail_markers[0]);
    const tail_end = try markerIndex(workflow_source, phase4_tail_markers[phase4_tail_markers.len - 1]);
    const phase6_start = try markerIndex(workflow_source, phase6_entry_marker);

    try std.testing.expect(entry_end < route_start);
    try std.testing.expect(route_end < tail_start);
    try std.testing.expect(tail_end < phase6_start);
}
