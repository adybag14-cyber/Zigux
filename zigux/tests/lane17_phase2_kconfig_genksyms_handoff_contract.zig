const std = @import("std");
const options = @import("lane17_options");

const WorkflowError = error{
    MissingMarker,
    OutOfOrderMarker,
    DuplicateMarker,
};

const Marker = struct {
    name: []const u8,
    needle: []const u8,
};

const phase2_handoff_markers = [_]Marker{
    .{
        .name = "kconfig allconfig helper self-test",
        .needle = "Self-test current Phase 2 kconfig allconfig helper checker",
    },
    .{
        .name = "kconfig allconfig helper packet",
        .needle = "Check current Phase 2 kconfig allconfig helper packet",
    },
    .{
        .name = "kbuild routes self-test",
        .needle = "Self-test current Phase 2 kbuild routes checker",
    },
    .{
        .name = "kbuild routes packet",
        .needle = "Check current Phase 2 kbuild packet",
    },
    .{
        .name = "cross-route direct packet",
        .needle = "Check current Phase 2 direct cross-route packet",
    },
    .{
        .name = "toolchain pin-scope packet",
        .needle = "Check current Phase 2 toolchain pin-scope packet",
    },
    .{
        .name = "bootstrap workflow routes packet",
        .needle = "Check current Phase 2 bootstrap workflow routes packet",
    },
    .{
        .name = "phase2 required make routes packet",
        .needle = "Check current Phase 2 required-make-routes packet",
    },
    .{
        .name = "phase2 tool manifest packet",
        .needle = "Check current Phase 2 tool manifest packet",
    },
    .{
        .name = "genksyms bridge packet",
        .needle = "Check current Phase 2 genksyms bridge packet",
    },
    .{
        .name = "genksyms make route",
        .needle = "Run current Phase 2 genksyms make route",
    },
    .{
        .name = "phase2 aggregate make route",
        .needle = "Run current Phase 2 aggregate make route",
    },
    .{
        .name = "phase2 closure packet",
        .needle = "Check current Phase 2 closure packet",
    },
    .{
        .name = "phase1 direct-owner self-test",
        .needle = "Self-test current Phase 1 direct-owner checker",
    },
};

fn requireOrderedMarkers(workflow: []const u8, markers: []const Marker) !void {
    var cursor: usize = 0;
    for (markers) |marker| {
        const relative_index = std.mem.indexOf(u8, workflow[cursor..], marker.needle) orelse {
            return WorkflowError.MissingMarker;
        };
        const absolute_index = cursor + relative_index;
        if (std.mem.indexOf(u8, workflow[absolute_index + marker.needle.len ..], marker.needle) != null) {
            return WorkflowError.DuplicateMarker;
        }
        if (absolute_index < cursor) {
            return WorkflowError.OutOfOrderMarker;
        }
        cursor = absolute_index + marker.needle.len;
    }
}

fn requirePhase2Handoff(workflow: []const u8) !void {
    try requireOrderedMarkers(workflow, phase2_handoff_markers[0..]);
}

fn loadWorkflow(allocator: std.mem.Allocator) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        options.workflow_path,
        allocator,
        .limited(2 * 1024 * 1024),
    );
}

test "current workflow preserves the Phase 2 handoff into Phase 1 closure" {
    const allocator = std.testing.allocator;
    const workflow = try loadWorkflow(allocator);
    defer allocator.free(workflow);

    try requirePhase2Handoff(workflow);
}

test "missing Phase 2 closure packet fails closed before Phase 1 starts" {
    const workflow =
        \\- name: Check current Phase 2 aggregate make route
        \\  run: make -C zigux phase2
        \\- name: Self-test current Phase 1 direct-owner checker
        \\  run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
    ;

    try std.testing.expectError(WorkflowError.MissingMarker, requirePhase2Handoff(workflow));
}

test "Phase 1 direct-owner marker may not precede the Phase 2 closure packet" {
    const workflow =
        \\- name: Check current Phase 2 aggregate make route
        \\  run: make -C zigux phase2
        \\- name: Self-test current Phase 1 direct-owner checker
        \\  run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test
        \\- name: Check current Phase 2 closure packet
        \\  run: python3 scripts/zigux/validate-phase2-closure.py
    ;

    try std.testing.expectError(WorkflowError.MissingMarker, requirePhase2Handoff(workflow));
}

test "duplicate Phase 2 closure packet marker is rejected" {
    const workflow =
        \\- name: Self-test current Phase 2 kconfig allconfig helper checker
        \\- name: Check current Phase 2 kconfig allconfig helper packet
        \\- name: Self-test current Phase 2 kbuild routes checker
        \\- name: Check current Phase 2 kbuild packet
        \\- name: Check current Phase 2 direct cross-route packet
        \\- name: Check current Phase 2 toolchain pin-scope packet
        \\- name: Check current Phase 2 bootstrap workflow routes packet
        \\- name: Check current Phase 2 required-make-routes packet
        \\- name: Check current Phase 2 tool manifest packet
        \\- name: Check current Phase 2 genksyms bridge packet
        \\- name: Run current Phase 2 genksyms make route
        \\- name: Run current Phase 2 aggregate make route
        \\- name: Check current Phase 2 closure packet
        \\- name: Check current Phase 2 closure packet
        \\- name: Self-test current Phase 1 direct-owner checker
    ;

    try std.testing.expectError(WorkflowError.DuplicateMarker, requirePhase2Handoff(workflow));
}
