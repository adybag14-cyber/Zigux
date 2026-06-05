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

test "phase12 libbpf checks start after release readiness" {
    try requireOrdered(&.{
        "Self-test current Phase 12 release-readiness packet checker",
        "python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test",
        "Check current Phase 12 release-readiness packet",
        "python3 scripts/zigux/check-phase12-release-readiness-packet.py",
        "Self-test current Phase 12 libbpf snapshot checker",
        "python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test",
        "Check current Phase 12 libbpf snapshot packet",
        "python3 scripts/zigux/check-phase12-libbpf-snapshot.py",
    });
}

test "phase12 libbpf snapshot and heavy-consumer pairs remain adjacent" {
    try requireOrdered(&.{
        "Self-test current Phase 12 libbpf snapshot checker",
        "python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test",
        "Check current Phase 12 libbpf snapshot packet",
        "python3 scripts/zigux/check-phase12-libbpf-snapshot.py",
        "Self-test current Phase 12 libbpf heavy-consumer packet checker",
        "python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py --self-test",
        "Check current Phase 12 libbpf heavy-consumer packet",
        "python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py",
    });
}

test "phase12 libbpf checks complete before validate and smoke routes" {
    try requireOrdered(&.{
        "Check current Phase 12 libbpf heavy-consumer packet",
        "python3 scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py",
        "Validate current Phase 12 support bundle",
        "python3 scripts/zigux/validate-phase12.py",
        "Run current Phase 12 smoke packet",
        "make -C zigux phase12-smoke",
        "Run current Phase 12 shared test packet",
        "make -C zigux phase12-test",
        "Run current Phase 12 aggregate route",
        "make -C zigux phase12",
    });
}

test "phase12 libbpf workflow markers are not duplicated" {
    const duplicate_markers = [_][]const u8{
        "Self-test current Phase 12 libbpf snapshot checker",
        "Check current Phase 12 libbpf snapshot packet",
        "Self-test current Phase 12 libbpf heavy-consumer packet checker",
        "Check current Phase 12 libbpf heavy-consumer packet",
    };
    for (&duplicate_markers) |marker| {
        try requireSingle(marker);
    }
}
