const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const kallsyms_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/symbol/kallsyms.zig"),
        .target = target,
        .optimize = optimize,
    });

    const kallsyms_tests = b.addTest(.{
        .name = "phase8-kallsyms-only-tests",
        .root_module = kallsyms_module,
    });

    const run_kallsyms_tests = b.addRunArtifact(kallsyms_tests);

    const test_step = b.step("test", "Run the focused Phase 8 kallsyms-only tests.");
    test_step.dependOn(&run_kallsyms_tests.step);

    b.default_step.dependOn(test_step);
}
