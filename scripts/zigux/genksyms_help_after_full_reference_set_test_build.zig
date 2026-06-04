const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("genksyms_help_after_full_reference_set_test.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "genksyms-help-after-full-reference-set-tests",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route = b.step(
        "genksyms-help-after-full-reference-set",
        "Run genksyms help after full reference-set tests",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run genksyms help after full reference-set tests");
    test_step.dependOn(&run_tests.step);
}
