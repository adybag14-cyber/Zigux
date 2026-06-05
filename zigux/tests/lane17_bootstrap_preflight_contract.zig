const std = @import("std");
const build_options = @import("build_options");

const workflow_path = build_options.workflow_path;

fn readWorkflow() ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(
        std.testing.io,
        workflow_path,
        std.testing.allocator,
        .limited(512 * 1024),
    );
}

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn expectOrdered(haystack: []const u8, earlier: []const u8, later: []const u8) !void {
    const earlier_index = std.mem.indexOf(u8, haystack, earlier) orelse return error.MissingEarlierMarker;
    const later_tail = haystack[earlier_index + earlier.len ..];
    _ = std.mem.indexOf(u8, later_tail, later) orelse return error.MissingLaterMarker;
}

fn expectOccursOnce(haystack: []const u8, needle: []const u8) !void {
    var count: usize = 0;
    var rest = haystack;
    while (std.mem.indexOf(u8, rest, needle)) |index| {
        count += 1;
        rest = rest[index + needle.len ..];
    }
    try std.testing.expectEqual(@as(usize, 1), count);
}

const early_step_names = [_][]const u8{
    "- name: Compile current scripts",
    "- name: Self-test current Zig toolchain checker",
    "- name: Check current Zig toolchain policy packet",
    "- name: Check current pinned Zig archive packet",
    "- name: Self-test current Lane 05 local-first archive checker",
    "- name: Check current Lane 05 local-first archive packet",
    "- name: Self-test current Lane 05 local archive README checker",
    "- name: Check current Lane 05 local archive README packet",
    "- name: Self-test current Lane 05 install-zig archive verification checker",
    "- name: Check current Lane 05 install-zig archive verification packet",
    "- name: Self-test current staged pinned Zig archive helper",
    "- name: Self-test current Zig installer helper",
    "- name: Self-test current Lane 05 stage helper contract checker",
    "- name: Check current Lane 05 stage helper contract packet",
    "- name: Self-test current Lane 05 stage helper selftest checker",
    "- name: Check current Lane 05 stage helper selftest packet",
    "- name: Self-test current Phase 2 fixdep gate checker",
    "- name: Check current Phase 2 fixdep gate packet",
};

const early_commands = [_][]const u8{
    "python3 -m py_compile \"${scripts[@]}\"",
    "python3 scripts/zigux/check-zig-toolchain.py --self-test",
    "python3 scripts/zigux/check-zig-toolchain.py --policy-only",
    "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test",
    "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test",
    "python3 scripts/zigux/check-lane05-local-archive-readme.py",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test",
    "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py",
    "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test",
    "python3 scripts/zigux/install-zig.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-contract.py",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test",
    "python3 scripts/zigux/check-lane05-stage-helper-selftest.py",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test",
    "python3 scripts/zigux/check-phase2-fixdep-gate.py",
};

test "bootstrap preflight keeps script compilation ahead of toolchain health gates" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    try expectContains(workflow, "find scripts/zigux -maxdepth 1 -type f -name '*.py' | sort");
    try expectContains(workflow, "if [ \"${#scripts[@]}\" -eq 0 ]; then");

    inline for (early_step_names) |step_name| {
        try expectOccursOnce(workflow, step_name);
    }

    inline for (early_commands) |command| {
        try expectContains(workflow, command);
    }

    try expectOrdered(workflow, "- name: Compile current scripts", "- name: Self-test current Zig toolchain checker");
    try expectOrdered(workflow, "python3 -m py_compile \"${scripts[@]}\"", "python3 scripts/zigux/check-zig-toolchain.py --self-test");
    try expectOrdered(workflow, "python3 scripts/zigux/check-zig-toolchain.py --self-test", "python3 scripts/zigux/check-zig-toolchain.py --policy-only");
    try expectOrdered(workflow, "python3 scripts/zigux/check-zig-toolchain.py --policy-only", "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing");
}

test "bootstrap preflight preserves local-first archive checks before stage and install helpers" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    try expectOrdered(workflow, "python3 scripts/zigux/check-zig-toolchain.py --archive-only --allow-missing", "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test");
    try expectOrdered(workflow, "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py --self-test", "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py");
    try expectOrdered(workflow, "python3 scripts/zigux/check-lane05-local-first-archive-workflow.py", "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test");
    try expectOrdered(workflow, "python3 scripts/zigux/check-lane05-local-archive-readme.py --self-test", "python3 scripts/zigux/check-lane05-local-archive-readme.py");
    try expectOrdered(workflow, "python3 scripts/zigux/check-lane05-local-archive-readme.py", "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py --self-test");
    try expectOrdered(workflow, "python3 scripts/zigux/check-lane05-install-zig-archive-verification.py", "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test");
    try expectOrdered(workflow, "python3 scripts/zigux/stage-pinned-zig-archive.py --self-test", "python3 scripts/zigux/install-zig.py --self-test");
}

test "bootstrap preflight reaches stage helper contracts before the phase2 fixdep entry" {
    const workflow = try readWorkflow();
    defer std.testing.allocator.free(workflow);

    try expectOrdered(workflow, "python3 scripts/zigux/install-zig.py --self-test", "python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test");
    try expectOrdered(workflow, "python3 scripts/zigux/check-lane05-stage-helper-contract.py --self-test", "python3 scripts/zigux/check-lane05-stage-helper-contract.py");
    try expectOrdered(workflow, "python3 scripts/zigux/check-lane05-stage-helper-contract.py", "python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test");
    try expectOrdered(workflow, "python3 scripts/zigux/check-lane05-stage-helper-selftest.py --self-test", "python3 scripts/zigux/check-lane05-stage-helper-selftest.py");
    try expectOrdered(workflow, "python3 scripts/zigux/check-lane05-stage-helper-selftest.py", "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test");
    try expectOrdered(workflow, "python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test", "python3 scripts/zigux/check-phase2-fixdep-gate.py");
    try expectOrdered(workflow, "python3 scripts/zigux/check-phase2-fixdep-gate.py", "python3 scripts/zigux/check-fixdep-diff.py --self-test");
}
