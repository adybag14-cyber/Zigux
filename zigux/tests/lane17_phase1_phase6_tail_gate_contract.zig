const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

fn loadWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(std.testing.io, workflow_path, allocator, .limited(1024 * 1024));
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var start: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, start, needle)) |index| {
        count += 1;
        start = index + needle.len;
    }
    return count;
}

fn requireOnce(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expectEqual(@as(usize, 0), countOccurrences(haystack, needle));
}

fn requireOrdered(haystack: []const u8, needles: []const []const u8) !void {
    var cursor: usize = 0;
    for (needles) |needle| {
        const found = std.mem.indexOfPos(u8, haystack, cursor, needle) orelse return error.MissingWorkflowMarker;
        cursor = found + needle.len;
    }
}

fn workflowTailMarkersStayOrdered(workflow: []const u8) !void {
    const ordered_markers = [_][]const u8{
        "- name: Run current Phase 1 shared tests-root smoke",
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
        "- name: Self-test current Phase 4 artifact-diff helper",
        "run: python3 scripts/zigux/artifact_diff.py --self-test",
        "- name: Self-test current Phase 4 artifact-diff contract checker",
        "run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
        "- name: Check current Phase 4 artifact-diff contract packet",
        "run: python3 scripts/zigux/check-artifact-diff-contract.py\n",
        "- name: Self-test current Phase 4 artifact-diff determinism checker",
        "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
        "- name: Check current Phase 4 artifact-diff determinism packet",
        "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py\n",
        "- name: Self-test current Phase 4 artifact-diff validator replay checker",
        "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
        "- name: Check current Phase 4 artifact-diff validator replay packet",
        "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py\n",
        "- name: Validate current Phase 6 helper packet",
        "run: make -C zigux phase6-validate",
        "- name: Run current Phase 6 leaf helper tests",
        "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
        "- name: Run current Phase 6 shared perf route",
        "run: make -C zigux phase6-perf",
    };

    try requireOrdered(workflow, &ordered_markers);
}

test "Lane 17 Phase 1 tail reaches Phase 6 only after the Phase 4 artifact-diff packet" {
    const workflow = try loadWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try workflowTailMarkersStayOrdered(workflow);
}

test "Lane 17 Phase 6 tail keeps exact workflow command surfaces unique" {
    const workflow = try loadWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    const required_once = [_][]const u8{
        "run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
        "run: make -C zigux phase4-validate",
        "run: make -C zigux phase4-test",
        "run: make -C zigux phase4-artifact-diff-contract",
        "run: python3 scripts/zigux/artifact_diff.py --self-test",
        "run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
        "run: python3 scripts/zigux/check-artifact-diff-contract.py\n",
        "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
        "run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py\n",
        "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
        "run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py\n",
        "run: make -C zigux phase6-validate",
        "run: zig build test --build-file zigux/tests/phase6_build.zig --summary all",
        "run: make -C zigux phase6-perf",
    };
    for (required_once) |needle| {
        try requireOnce(workflow, needle);
    }

    try requireAbsent(workflow, "run: make -C zigux phase1-validate");
    try requireAbsent(workflow, "run: make -C zigux phase1-test");
    try requireAbsent(workflow, "run: make -C zigux phase1-bench");
}

test "Lane 17 Phase 6 tail contract rejects missing duplicate and reordered gates" {
    const good =
        \\- name: Run current Phase 1 shared tests-root smoke
        \\  run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig
        \\- name: Self-test current Phase 4 artifact-diff helper
        \\  run: python3 scripts/zigux/artifact_diff.py --self-test
        \\- name: Self-test current Phase 4 artifact-diff contract checker
        \\  run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test
        \\- name: Check current Phase 4 artifact-diff contract packet
        \\  run: python3 scripts/zigux/check-artifact-diff-contract.py
        \\- name: Self-test current Phase 4 artifact-diff determinism checker
        \\  run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test
        \\- name: Check current Phase 4 artifact-diff determinism packet
        \\  run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py
        \\- name: Self-test current Phase 4 artifact-diff validator replay checker
        \\  run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test
        \\- name: Check current Phase 4 artifact-diff validator replay packet
        \\  run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py
        \\- name: Validate current Phase 6 helper packet
        \\  run: make -C zigux phase6-validate
        \\- name: Run current Phase 6 leaf helper tests
        \\  run: zig build test --build-file zigux/tests/phase6_build.zig --summary all
        \\- name: Run current Phase 6 shared perf route
        \\  run: make -C zigux phase6-perf
        \\
    ;
    try workflowTailMarkersStayOrdered(good);

    const missing_phase6 = std.mem.replaceOwned(
        u8,
        std.testing.allocator,
        good,
        "- name: Validate current Phase 6 helper packet\n  run: make -C zigux phase6-validate\n",
        "",
    ) catch unreachable;
    defer std.testing.allocator.free(missing_phase6);
    try std.testing.expectError(error.MissingWorkflowMarker, workflowTailMarkersStayOrdered(missing_phase6));

    const duplicate_phase6 = try std.mem.concat(std.testing.allocator, u8, &.{
        good,
        "- name: Validate current Phase 6 helper packet\n  run: make -C zigux phase6-validate\n",
    });
    defer std.testing.allocator.free(duplicate_phase6);
    try std.testing.expectEqual(@as(usize, 2), countOccurrences(duplicate_phase6, "run: make -C zigux phase6-validate"));

    const reordered =
        \\- name: Validate current Phase 6 helper packet
        \\  run: make -C zigux phase6-validate
        \\- name: Run current Phase 1 shared tests-root smoke
        \\  run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig
        \\- name: Self-test current Phase 4 artifact-diff helper
        \\  run: python3 scripts/zigux/artifact_diff.py --self-test
        \\- name: Self-test current Phase 4 artifact-diff contract checker
        \\  run: python3 scripts/zigux/check-artifact-diff-contract.py --self-test
        \\- name: Check current Phase 4 artifact-diff contract packet
        \\  run: python3 scripts/zigux/check-artifact-diff-contract.py
        \\- name: Self-test current Phase 4 artifact-diff determinism checker
        \\  run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test
        \\- name: Check current Phase 4 artifact-diff determinism packet
        \\  run: python3 scripts/zigux/check-phase4-artifact-diff-determinism.py
        \\- name: Self-test current Phase 4 artifact-diff validator replay checker
        \\  run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test
        \\- name: Check current Phase 4 artifact-diff validator replay packet
        \\  run: python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py
        \\- name: Run current Phase 6 leaf helper tests
        \\  run: zig build test --build-file zigux/tests/phase6_build.zig --summary all
        \\- name: Run current Phase 6 shared perf route
        \\  run: make -C zigux phase6-perf
        \\
    ;
    try std.testing.expectError(error.MissingWorkflowMarker, workflowTailMarkersStayOrdered(reordered));
}
