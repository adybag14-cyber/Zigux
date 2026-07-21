const std = @import("std");
const testing = std.testing;
const build_options = @import("build_options");

const workflow_text = build_options.workflow_text;

const Step = struct {
    name: []const u8,
    run: []const u8,
};

const expected_tail = [_]Step{
    .{
        .name = "Check current Phase 1 closure packet",
        .run = "zig run scripts/zigux/validate_phase1_closure.zig",
    },
    .{
        .name = "Self-test current Phase 3 interop packet",
        .run = "zig run scripts/zigux/validate_phase3_selftest.zig",
    },
    .{
        .name = "Check current Phase 3 interop packet",
        .run = "zig run scripts/zigux/run_phase3_checks.zig",
    },
    .{
        .name = "Run current Phase 3 shared tests-root packet",
        .run = "zig build phase3-test --build-file zigux/tests/build.zig",
    },
    .{
        .name = "Run current Phase 3 ABI dump replay",
        .run = "zig build phase3-dump --build-file zigux/tests/build.zig",
    },
    .{
        .name = "Run current Phase 1 shared tests-root smoke",
        .run = "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig",
    },
    .{
        .name = "Self-test current Phase 4 repo-reality warning checker",
        .run = "zig run scripts/zigux/check_phase4_repo_reality_warning.zig -- --self-test",
    },
    .{
        .name = "Check current Phase 4 repo-reality warning packet",
        .run = "zig run scripts/zigux/check_phase4_repo_reality_warning.zig",
    },
};

fn countNeedle(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |found| {
        count += 1;
        index = found + needle.len;
    }
    return count;
}

fn stepPosition(workflow: []const u8, step: Step) !usize {
    const name_needle = try std.fmt.allocPrint(testing.allocator, "      - name: {s}", .{step.name});
    defer testing.allocator.free(name_needle);
    const run_needle = try std.fmt.allocPrint(testing.allocator, "        run: {s}", .{step.run});
    defer testing.allocator.free(run_needle);

    try testing.expectEqual(@as(usize, 1), countNeedle(workflow, name_needle));
    const name_pos = std.mem.indexOf(u8, workflow, name_needle) orelse return error.MissingStepName;
    const next_step = std.mem.indexOfPos(u8, workflow, name_pos + name_needle.len, "\n      - name: ") orelse workflow.len;
    const step_block = workflow[name_pos..next_step];
    try testing.expectEqual(@as(usize, 1), countNeedle(step_block, run_needle));
    return name_pos;
}

test "Phase 1 shared smoke tail keeps exact steps unique and ordered" {
    var previous: usize = 0;
    for (expected_tail, 0..) |step, index| {
        const current = try stepPosition(workflow_text, step);
        if (index != 0) {
            try testing.expect(current > previous);
        }
        previous = current;
    }
}

test "Phase 1 shared smoke stays after shared Phase 3 routes and before Phase 4 warning checks" {
    const phase3_tests = try stepPosition(workflow_text, expected_tail[3]);
    const phase3_dump = try stepPosition(workflow_text, expected_tail[4]);
    const phase1_smoke = try stepPosition(workflow_text, expected_tail[5]);
    const phase4_self_test = try stepPosition(workflow_text, expected_tail[6]);

    try testing.expect(phase3_tests < phase3_dump);
    try testing.expect(phase3_dump < phase1_smoke);
    try testing.expect(phase1_smoke < phase4_self_test);
}

test "Phase 1 shared smoke route does not regress to aggregate or permissive variants" {
    try testing.expectEqual(@as(usize, 1), countNeedle(workflow_text, "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig"));
    try testing.expectEqual(@as(usize, 0), countNeedle(workflow_text, "zig build test --build-file zigux/tests/build.zig"));
    try testing.expectEqual(@as(usize, 0), countNeedle(workflow_text, "zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig --summary all"));
    try testing.expectEqual(@as(usize, 0), countNeedle(workflow_text, "make -C zigux phase1-host-tools-smoke"));
}
