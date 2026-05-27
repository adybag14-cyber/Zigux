const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const landlock_ruleset_module = b.createModule(.{
        .root_source_file = b.path("../../security/landlock/ruleset.zig"),
        .target = target,
        .optimize = optimize,
    });
    const landlock_syscalls_module = b.createModule(.{
        .root_source_file = b.path("../../security/landlock/syscalls.zig"),
        .target = target,
        .optimize = optimize,
    });
    landlock_syscalls_module.addImport("ruleset.zig", landlock_ruleset_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase13_landlock_syscalls.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("syscalls", landlock_syscalls_module);
    root_module.addImport("ruleset", landlock_ruleset_module);

    const tests = b.addTest(.{
        .name = "phase13-landlock-syscalls-tests",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase13-landlock-syscalls-test",
        "Run the Phase 13 Landlock syscalls helper tests",
    );
    step.dependOn(&run.step);

    const test_step = b.step("test", "Run the Phase 13 Landlock syscalls helper tests");
    test_step.dependOn(&run.step);
}
