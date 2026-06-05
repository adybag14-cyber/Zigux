const std = @import("std");
const build_options = @import("build_options");

const workflow = @embedFile(build_options.workflow_path);

fn requireContains(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingWorkflowMarker;
}

fn requireOrdered(markers: []const []const u8) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const found = requireContains(workflow[cursor..], marker) catch |err| {
            std.debug.print("missing workflow marker: {s}\n", .{marker});
            return err;
        };
        cursor += found + marker.len;
    }
}

test "phase4 rollback routes stay ordered before artifact diff contract" {
    try requireOrdered(&.{
        "Self-test current Phase 4 repo-reality warning checker",
        "python3 scripts/zigux/check-phase4-repo-reality-warning.py --self-test",
        "Check current Phase 4 repo-reality warning packet",
        "python3 scripts/zigux/check-phase4-repo-reality-warning.py",
        "Self-test current Phase 4 reversible-delivery pin checker",
        "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py --self-test",
        "Check current Phase 4 reversible-delivery pin packet",
        "python3 scripts/zigux/check-phase4-reversible-delivery-pins.py",
        "Self-test current Phase 4 tests README checker",
        "python3 scripts/zigux/check-phase4-tests-readme-packet.py --self-test",
        "Check current Phase 4 tests README packet",
        "python3 scripts/zigux/check-phase4-tests-readme-packet.py",
        "Validate Phase 4 rollback routes",
        "make -C zigux phase4-validate",
        "Run Phase 4 rollback tests",
        "make -C zigux phase4-test",
        "Run Phase 4 artifact-diff contract make route",
        "make -C zigux phase4-artifact-diff-contract",
    });
}

test "phase4 artifact diff checkers complete before phase6 handoff" {
    try requireOrdered(&.{
        "Self-test current Phase 4 artifact-diff helper",
        "python3 scripts/zigux/artifact_diff.py --self-test",
        "Self-test current Phase 4 artifact-diff contract checker",
        "python3 scripts/zigux/check-artifact-diff-contract.py --self-test",
        "Check current Phase 4 artifact-diff contract packet",
        "python3 scripts/zigux/check-artifact-diff-contract.py",
        "Self-test current Phase 4 artifact-diff determinism checker",
        "python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test",
        "Check current Phase 4 artifact-diff determinism packet",
        "python3 scripts/zigux/check-phase4-artifact-diff-determinism.py",
        "Self-test current Phase 4 artifact-diff validator replay checker",
        "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py --self-test",
        "Check current Phase 4 artifact-diff validator replay packet",
        "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
        "Validate current Phase 6 helper packet",
        "make -C zigux phase6-validate",
    });
}

test "phase6 validate test and perf routes stay together before phase8" {
    try requireOrdered(&.{
        "Validate current Phase 6 helper packet",
        "make -C zigux phase6-validate",
        "Run current Phase 6 leaf helper tests",
        "zig build test --build-file zigux/tests/phase6_build.zig --summary all",
        "Run current Phase 6 shared perf route",
        "make -C zigux phase6-perf",
        "Validate Phase 8 tooling routes",
        "make -C zigux phase8-validate",
    });
}

test "phase8 focused tooling routes stay after phase8 validation and before phase9" {
    try requireOrdered(&.{
        "Validate Phase 8 tooling routes",
        "make -C zigux phase8-validate",
        "Run focused Phase 8 exec-cmd tests",
        "make -C zigux phase8-exec-cmd-test",
        "Run focused Phase 8 libbpf segment tests",
        "make -C zigux phase8-libbpf-segments-test",
        "Run Phase 8 tooling tests",
        "make -C zigux phase8-test",
        "Self-test current Phase 9 review-checklist boundaries checker",
        "python3 scripts/zigux/check-phase9-review-checklist-phase-boundaries.py --self-test",
    });
}
