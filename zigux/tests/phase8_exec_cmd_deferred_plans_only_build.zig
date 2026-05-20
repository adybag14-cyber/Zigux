const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exec_cmd_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/subcmd/exec-cmd.zig"),
        .target = target,
        .optimize = optimize,
    });

    const deferred_plans_root = b.createModule(.{
        .root_source_file = b.path("phase8_exec_cmd_deferred_plans.zig"),
        .target = target,
        .optimize = optimize,
    });
    deferred_plans_root.addImport("exec_cmd", exec_cmd_module);

    const deferred_plan_tests = b.addTest(.{
        .name = "phase8-exec-cmd-deferred-plan-tests",
        .root_module = deferred_plans_root,
    });

    const run_deferred_plan_tests = b.addRunArtifact(deferred_plan_tests);
    const test_step = b.step("test", "Run focused Phase 8 exec-cmd deferred planning tests.");
    test_step.dependOn(&run_deferred_plan_tests.step);
}
