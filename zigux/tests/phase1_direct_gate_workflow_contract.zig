const std = @import("std");

const DirectGate = struct {
    name: []const u8,
    command: []const u8,
};

const direct_gates = [_]DirectGate{
    .{
        .name = "- name: Self-test current Phase 1 direct-owner checker",
        .command = "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test\n",
    },
    .{
        .name = "- name: Check current Phase 1 direct-owner markers",
        .command = "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py\n",
    },
    .{
        .name = "- name: Self-test current Phase 1 direct-anchor manifest gate",
        .command = "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test\n",
    },
    .{
        .name = "- name: Check current Phase 1 direct-anchor manifest gate",
        .command = "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\n",
    },
};

test "phase1 direct gates keep exact workflow commands" {
    const workflow = try loadWorkflow();
    defer std.testing.allocator.free(workflow);

    for (direct_gates) |gate| {
        const name_index = try requireSingle(workflow, gate.name);
        const command_index = try requireSingle(workflow, gate.command);
        try std.testing.expect(name_index < command_index);
        try std.testing.expect(command_index - name_index < 120);
    }
}

test "phase1 direct gates stay ordered between closure and review gates" {
    const workflow = try loadWorkflow();
    defer std.testing.allocator.free(workflow);

    try expectBefore(
        workflow,
        "        run: python3 scripts/zigux/validate-phase2-closure.py\n",
        "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test\n",
    );
    try expectBefore(
        workflow,
        "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test\n",
        "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py\n",
    );
    try expectBefore(
        workflow,
        "        run: python3 scripts/zigux/check-phase1-direct-owner-markers.py\n",
        "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test\n",
    );
    try expectBefore(
        workflow,
        "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py --self-test\n",
        "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\n",
    );
    try expectBefore(
        workflow,
        "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\n",
        "        run: python3 scripts/zigux/check-phase1-string-review-packet.py --self-test\n",
    );
    try expectBefore(
        workflow,
        "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\n",
        "        run: python3 scripts/zigux/check-phase1-route-summary-counts.py --self-test\n",
    );
    try expectBefore(
        workflow,
        "        run: python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py\n",
        "        run: python3 scripts/zigux/check-phase1-shared-reminder-packet.py --self-test\n",
    );
}

test "phase1 direct workflow gates stay strict" {
    const workflow = try loadWorkflow();
    defer std.testing.allocator.free(workflow);

    try requireAbsent(workflow, "check-phase1-direct-owner-markers.py --root");
    try requireAbsent(workflow, "check-phase1-direct-owner-markers.py --allow-missing");
    try requireAbsent(workflow, "check-phase1-direct-anchor-manifest-gate.py --root");
    try requireAbsent(workflow, "check-phase1-direct-anchor-manifest-gate.py --allow-missing");
    try requireAbsent(workflow, "check-phase1-direct-anchor-manifest-gate.py --write-sample-root");
}

fn loadWorkflow() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        ".github/workflows/zigux-bootstrap.yml",
        std.testing.allocator,
        .limited(256 * 1024),
    );
}

fn expectBefore(workflow: []const u8, before: []const u8, after: []const u8) !void {
    const before_index = try requireSingle(workflow, before);
    const after_index = try requireSingle(workflow, after);
    try std.testing.expect(before_index < after_index);
}

fn requireSingle(haystack: []const u8, needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, haystack, needle) orelse return error.MissingWorkflowMarker;
    const next_start = first + needle.len;
    if (std.mem.indexOf(u8, haystack[next_start..], needle) != null) {
        return error.DuplicateWorkflowMarker;
    }
    return first;
}

fn requireAbsent(workflow: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, workflow, needle) == null);
}
