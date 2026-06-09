const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_exe = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_rbtree_fixture_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(test_exe);
    const contract_step = b.step(
        "phase1-rbtree-fixture-contract",
        "Validate the Phase 1 rbtree helper fixture contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Phase 1 rbtree fixture contract tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
