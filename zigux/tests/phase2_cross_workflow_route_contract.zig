const std = @import("std");

const Step = struct {
    name: []const u8,
    run: []const u8,
};

const cross_workflow_steps = [_]Step{
    .{
        .name = "      - name: Self-test current Phase 2 cross checker\n",
        .run = "        run: python3 scripts/zigux/check-phase2-cross.py --self-test\n",
    },
    .{
        .name = "      - name: Check current Phase 2 direct cross-route packet\n",
        .run = "        run: python3 scripts/zigux/check-phase2-cross.py\n",
    },
    .{
        .name = "      - name: Self-test current Phase 2 cross selftest alignment checker\n",
        .run = "        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py --self-test\n",
    },
    .{
        .name = "      - name: Check current Phase 2 cross alignment packet\n",
        .run = "        run: python3 scripts/zigux/check-phase2-cross-selftest-alignment.py\n",
    },
    .{
        .name = "      - name: Run current Phase 2 cross make route\n",
        .run = "        run: make -C zigux phase2-cross\n",
    },
};

test "Phase 2 cross workflow route keeps direct checker pair and make route ordered" {
    const workflow = try std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        ".github/workflows/zigux-bootstrap.yml",
        std.testing.allocator,
        .limited(1024 * 1024),
    );
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "      - 'scripts/zigux/**'\n");
    try expectContains(workflow, "      - 'zigux/**'\n");
    try expectContains(workflow, "      - '.github/workflows/zigux-bootstrap.yml'\n");

    var previous_run_end: usize = 0;
    for (cross_workflow_steps) |step| {
        const name_index = try expectOnce(workflow, step.name);
        const run_index = try expectOnce(workflow, step.run);
        try std.testing.expect(name_index < run_index);
        try std.testing.expect(previous_run_end <= name_index);
        previous_run_end = run_index + step.run.len;
    }

    const required_routes_index = try expectOnce(workflow, "      - name: Self-test current Phase 2 required-make-routes checker\n");
    const tool_manifest_index = try expectOnce(workflow, "      - name: Self-test current Phase 2 tool manifest checker\n");
    try std.testing.expect(previous_run_end <= required_routes_index);
    try std.testing.expect(required_routes_index < tool_manifest_index);
}

fn expectContains(workflow: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, workflow, needle) != null);
}

fn expectOnce(workflow: []const u8, needle: []const u8) !usize {
    const first = std.mem.indexOf(u8, workflow, needle) orelse return error.MissingWorkflowNeedle;
    const second_start = first + needle.len;
    try std.testing.expect(std.mem.indexOfPos(u8, workflow, second_start, needle) == null);
    return first;
}
