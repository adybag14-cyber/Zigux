const std = @import("std");
const build_options = @import("build_options");

const workflow = @embedFile(build_options.workflow_path);

fn requireContains(haystack: []const u8, needle: []const u8) !usize {
    return std.mem.indexOf(u8, haystack, needle) orelse error.MissingWorkflowMarker;
}

fn requireSingle(needle: []const u8) !void {
    const first = requireContains(workflow, needle) catch |err| {
        std.debug.print("missing workflow marker: {s}\n", .{needle});
        return err;
    };
    if (std.mem.indexOf(u8, workflow[first + needle.len ..], needle) != null) {
        std.debug.print("duplicate workflow marker: {s}\n", .{needle});
        return error.DuplicateWorkflowMarker;
    }
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

test "phase4 artifact diff ladder starts after rollback and make contract" {
    try requireOrdered(&.{
        "Validate Phase 4 rollback routes",
        "make -C zigux phase4-validate",
        "Run Phase 4 rollback tests",
        "make -C zigux phase4-test",
        "Run Phase 4 artifact-diff contract make route",
        "make -C zigux phase4-artifact-diff-contract",
        "Self-test current Phase 4 artifact-diff helper",
        "python3 scripts/zigux/artifact_diff.py --self-test",
    });
}

test "phase4 artifact diff checker pairs remain complete and ordered" {
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
    });
}

test "phase4 artifact diff ladder completes before phase6 handoff" {
    try requireOrdered(&.{
        "Check current Phase 4 artifact-diff validator replay packet",
        "python3 scripts/zigux/check-phase4-artifact-diff-validator-replays.py",
        "Validate current Phase 6 helper packet",
        "make -C zigux phase6-validate",
    });
}

test "phase4 artifact diff ladder markers are not duplicated" {
    const duplicate_markers = [_][]const u8{
        "Run Phase 4 artifact-diff contract make route",
        "Self-test current Phase 4 artifact-diff helper",
        "Self-test current Phase 4 artifact-diff contract checker",
        "Check current Phase 4 artifact-diff contract packet",
        "Self-test current Phase 4 artifact-diff determinism checker",
        "Check current Phase 4 artifact-diff determinism packet",
        "Self-test current Phase 4 artifact-diff validator replay checker",
        "Check current Phase 4 artifact-diff validator replay packet",
    };
    for (&duplicate_markers) |marker| {
        try requireSingle(marker);
    }
}
