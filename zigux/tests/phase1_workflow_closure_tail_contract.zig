const std = @import("std");
const testing = std.testing;
const build_options = @import("build_options");

const workflow_text = build_options.workflow_text;

const RequiredStep = struct {
    name: []const u8,
    run: []const u8,
};

const phase1_tail_steps = [_]RequiredStep{
    .{
        .name = "- name: Self-test current Phase 1 bench checker",
        .run = "\n        run: zig run scripts/zigux/check_phase1_bench.zig -- --self-test\n",
    },
    .{
        .name = "- name: Check current Phase 1 bench packet",
        .run = "\n        run: zig run scripts/zigux/check_phase1_bench.zig\n",
    },
    .{
        .name = "- name: Self-test current Phase 1 bench live-check workflow guard",
        .run = "\n        run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig -- --self-test\n",
    },
    .{
        .name = "- name: Check current Phase 1 bench live-check workflow guard packet",
        .run = "\n        run: zig run scripts/zigux/check_phase1_bench_live_check_workflow.zig\n",
    },
    .{
        .name = "- name: Self-test current Phase 1 find-bit bench anchor checker",
        .run = "\n        run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig -- --self-test\n",
    },
    .{
        .name = "- name: Check current Phase 1 find-bit bench anchor packet",
        .run = "\n        run: zig run scripts/zigux/check_phase1_find_bit_bench_anchors.zig\n",
    },
    .{
        .name = "- name: Self-test current Phase 1 shared reminder checker",
        .run = "\n        run: zig run scripts/zigux/check_phase1_shared_reminder_packet.zig -- --self-test\n",
    },
    .{
        .name = "- name: Check current Phase 1 shared reminder packet",
        .run = "\n        run: zig run scripts/zigux/check_phase1_shared_reminder_packet.zig\n",
    },
    .{
        .name = "- name: Self-test current Phase 1 closure validator",
        .run = "\n        run: zig run scripts/zigux/validate_phase1_closure.zig -- --self-test\n",
    },
    .{
        .name = "- name: Check current Phase 1 closure packet",
        .run = "\n        run: zig run scripts/zigux/validate_phase1_closure.zig\n",
    },
};

const handoff_steps = [_]RequiredStep{
    .{
        .name = "- name: Self-test current Phase 3 interop packet",
        .run = "\n        run: zig run scripts/zigux/validate_phase3_selftest.zig\n",
    },
    .{
        .name = "- name: Check current Phase 3 interop packet",
        .run = "\n        run: zig run scripts/zigux/run_phase3_checks.zig\n",
    },
    .{
        .name = "- name: Run current Phase 3 shared tests-root packet",
        .run = "\n        run: zig build phase3-test --build-file zigux/tests/build.zig\n",
    },
    .{
        .name = "- name: Run current Phase 3 ABI dump replay",
        .run = "\n        run: zig build phase3-dump --build-file zigux/tests/build.zig\n",
    },
    .{
        .name = "- name: Run current Phase 1 shared tests-root smoke",
        .run = "\n        run: zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig\n",
    },
};

fn countOccurrences(haystack: []const u8, needle: []const u8) usize {
    var count: usize = 0;
    var index: usize = 0;
    while (std.mem.indexOfPos(u8, haystack, index, needle)) |match| {
        count += 1;
        index = match + needle.len;
    }
    return count;
}

fn requireOnce(haystack: []const u8, needle: []const u8) !usize {
    try testing.expectEqual(@as(usize, 1), countOccurrences(haystack, needle));
    return std.mem.indexOf(u8, haystack, needle).?;
}

fn requireAbsent(haystack: []const u8, needle: []const u8) !void {
    try testing.expectEqual(@as(usize, 0), countOccurrences(haystack, needle));
}

fn requireStep(step: RequiredStep) !usize {
    const name_index = try requireOnce(workflow_text, step.name);
    const run_index = try requireOnce(workflow_text, step.run);
    try testing.expect(name_index < run_index);
    return name_index;
}

fn requireOrderedSteps(steps: []const RequiredStep) !void {
    var previous: usize = 0;
    for (steps, 0..) |step, ordinal| {
        const current = try requireStep(step);
        if (ordinal != 0) {
            try testing.expect(previous < current);
        }
        previous = current;
    }
}

test "phase1 closure workflow tail keeps the current gate order" {
    try requireOrderedSteps(phase1_tail_steps[0..]);
}

test "phase1 closure packet hands off through phase3 before shared phase1 smoke" {
    const closure_index = try requireStep(phase1_tail_steps[phase1_tail_steps.len - 1]);
    var previous = closure_index;
    for (handoff_steps) |step| {
        const current = try requireStep(step);
        try testing.expect(previous < current);
        previous = current;
    }
}

test "phase1 closure workflow tail keeps stale route spellings out" {
    try requireAbsent(workflow_text, "run: zig run validate_phase1.zig");
    try requireAbsent(workflow_text, "\n        run: make -C zigux phase1\n");
    try requireAbsent(workflow_text, "run: zig build phase1-bench --build-file zigux/tests/build.zig");
}
