const std = @import("std");

const workflow_path = ".github/workflows/zigux-bootstrap.yml";

const WorkflowError = error{
    MissingMarker,
    DuplicateMarker,
    ReorderedMarker,
    StaleHistoricalMarker,
};

const Step = struct {
    name: []const u8,
    run: []const u8,
};

const lane05_archive_steps = [_]Step{
    .{
        .name = "      - name: Self-test current Lane 05 local-first archive checker\n",
        .run = "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test\n",
    },
    .{
        .name = "      - name: Check current Lane 05 local-first archive packet\n",
        .run = "        run: python3 scripts/zigux/check-lane05-local-first-archive-workflow.py\n",
    },
    .{
        .name = "      - name: Self-test current Lane 05 local archive README checker\n",
        .run = "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test\n",
    },
    .{
        .name = "      - name: Check current Lane 05 local archive README packet\n",
        .run = "        run: python3 scripts/zigux/check-lane05-local-archive-readme.py\n",
    },
    .{
        .name = "      - name: Self-test current Lane 05 install-zig archive verification checker\n",
        .run = "        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test\n",
    },
    .{
        .name = "      - name: Check current Lane 05 install-zig archive verification packet\n",
        .run = "        run: python3 scripts/zigux/check-lane05-install-zig-archive-verification.py\n",
    },
    .{
        .name = "      - name: Self-test current staged pinned Zig archive helper\n",
        .run = "        run: python3 scripts/zigux/stage-pinned-zig-archive.py --self-test\n",
    },
    .{
        .name = "      - name: Self-test current Zig installer helper\n",
        .run = "        run: python3 scripts/zigux/install-zig.py --self-test\n",
    },
    .{
        .name = "      - name: Self-test current Lane 05 stage helper contract checker\n",
        .run = "        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test\n",
    },
    .{
        .name = "      - name: Check current Lane 05 stage helper contract packet\n",
        .run = "        run: python3 scripts/zigux/check-lane05-stage-helper-contract.py\n",
    },
    .{
        .name = "      - name: Self-test current Lane 05 stage helper selftest checker\n",
        .run = "        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test\n",
    },
    .{
        .name = "      - name: Check current Lane 05 stage helper selftest packet\n",
        .run = "        run: python3 scripts/zigux/check-lane05-stage-helper-selftest.py\n",
    },
};

const phase2_handoff_step = Step{
    .name = "      - name: Self-test current Phase 2 fixdep gate checker\n",
    .run = "        run: python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test\n",
};

fn readWorkflow(allocator: std.mem.Allocator) ![]u8 {
    var io_instance: std.Io.Threaded = .init(allocator, .{});
    defer io_instance.deinit();
    return try std.Io.Dir.cwd().readFileAlloc(
        io_instance.io(),
        workflow_path,
        allocator,
        .limited(512 * 1024),
    );
}

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var offset: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, offset, needle)) |pos| {
        count += 1;
        offset = pos + needle.len;
    }
    return count;
}

fn requireOnce(haystack: []const u8, marker: []const u8) WorkflowError!usize {
    const pos = std.mem.indexOf(u8, haystack, marker) orelse return error.MissingMarker;
    if (countOccurrences(haystack, marker) != 1) return error.DuplicateMarker;
    return pos;
}

fn requireAfter(haystack: []const u8, marker: []const u8, previous: usize) WorkflowError!usize {
    const pos = try requireOnce(haystack, marker);
    if (pos <= previous) return error.ReorderedMarker;
    return pos;
}

fn requireAbsent(haystack: []const u8, marker: []const u8) WorkflowError!void {
    if (std.mem.indexOf(u8, haystack, marker) != null) return error.StaleHistoricalMarker;
}

fn checkStep(haystack: []const u8, step: Step, previous: usize) WorkflowError!usize {
    const name_pos = try requireAfter(haystack, step.name, previous);
    return try requireAfter(haystack, step.run, name_pos);
}

fn checkLane05ArchiveCluster(haystack: []const u8) WorkflowError!void {
    var cursor = try requireOnce(haystack, "      - name: Check current pinned Zig archive packet\n");

    inline for (lane05_archive_steps) |step| {
        cursor = try checkStep(haystack, step, cursor);
    }

    _ = try checkStep(haystack, phase2_handoff_step, cursor);

    try requireAbsent(haystack, "make -C zigux lane05");
    try requireAbsent(haystack, "make -C zigux phase1");
    try requireAbsent(haystack, "python3 scripts/zigux/validate-phase1.py");
}

test "lane 17 guards the lane 05 archive-helper workflow cluster before phase 2 gates" {
    const workflow = try readWorkflow(std.testing.allocator);
    defer std.testing.allocator.free(workflow);

    try checkLane05ArchiveCluster(workflow);
}

test "lane 05 archive-helper cluster rejects a missing checker handoff" {
    const workflow =
        "      - name: Check current pinned Zig archive packet\n" ++
        lane05_archive_steps[0].name ++ lane05_archive_steps[0].run ++
        lane05_archive_steps[1].name ++ lane05_archive_steps[1].run ++
        phase2_handoff_step.name ++ phase2_handoff_step.run;

    try std.testing.expectError(error.MissingMarker, checkLane05ArchiveCluster(workflow));
}

test "lane 05 archive-helper cluster rejects duplicate selftest markers" {
    const workflow =
        "      - name: Check current pinned Zig archive packet\n" ++
        lane05_archive_steps[0].name ++
        lane05_archive_steps[0].name ++
        lane05_archive_steps[0].run;

    try std.testing.expectError(error.DuplicateMarker, checkLane05ArchiveCluster(workflow));
}

test "lane 05 archive-helper cluster rejects reordered archive checks" {
    const workflow =
        "      - name: Check current pinned Zig archive packet\n" ++
        lane05_archive_steps[1].name ++
        lane05_archive_steps[0].name ++ lane05_archive_steps[0].run ++
        lane05_archive_steps[1].run;

    try std.testing.expectError(error.ReorderedMarker, checkLane05ArchiveCluster(workflow));
}

test "lane 05 archive-helper cluster rejects stale broad phase routes" {
    const workflow =
        "      - name: Check current pinned Zig archive packet\n" ++
        "make -C zigux phase1\n" ++
        lane05_archive_steps[0].name ++ lane05_archive_steps[0].run ++
        lane05_archive_steps[1].name ++ lane05_archive_steps[1].run ++
        lane05_archive_steps[2].name ++ lane05_archive_steps[2].run ++
        lane05_archive_steps[3].name ++ lane05_archive_steps[3].run ++
        lane05_archive_steps[4].name ++ lane05_archive_steps[4].run ++
        lane05_archive_steps[5].name ++ lane05_archive_steps[5].run ++
        lane05_archive_steps[6].name ++ lane05_archive_steps[6].run ++
        lane05_archive_steps[7].name ++ lane05_archive_steps[7].run ++
        lane05_archive_steps[8].name ++ lane05_archive_steps[8].run ++
        lane05_archive_steps[9].name ++ lane05_archive_steps[9].run ++
        lane05_archive_steps[10].name ++ lane05_archive_steps[10].run ++
        lane05_archive_steps[11].name ++ lane05_archive_steps[11].run ++
        phase2_handoff_step.name ++ phase2_handoff_step.run;

    try std.testing.expectError(error.StaleHistoricalMarker, checkLane05ArchiveCluster(workflow));
}
