const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase2-cross-target-scope-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_target_scope_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const phase2_cross_target_scope = b.step(
        "phase2-cross-target-scope-contract",
        "Run the Phase 2 cross-target scope fixture contract",
    );
    phase2_cross_target_scope.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 cross-target scope fixture contract");
    test_step.dependOn(&run_tests.step);
}
