const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_step = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_closure_shared_tooling_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(test_step);

    const named_step = b.step(
        "phase2-closure-shared-tooling-contract",
        "Run the Phase 2 shared tooling closure contract",
    );
    named_step.dependOn(&run_tests.step);

    const default_test_step = b.step("test", "Run the Phase 2 shared tooling closure contract tests");
    default_test_step.dependOn(&run_tests.step);
}
