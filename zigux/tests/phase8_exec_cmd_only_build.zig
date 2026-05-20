const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const exec_cmd_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/subcmd/exec-cmd.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase8_exec_cmd.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("exec_cmd", exec_cmd_module);

    const unit_tests = b.addTest(.{
        .name = "phase8-exec-cmd-tests",
        .root_module = root_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    // Legacy validator marker: Run the phase 8 exec-cmd review witness tests.
    const test_step = b.step("test", "Run focused Phase 8 exec-cmd tests");
    test_step.dependOn(&run_unit_tests.step);
}
