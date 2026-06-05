const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_tests_readme_toolchain_bootstrap_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const named_step = b.step(
        "phase2-tests-readme-toolchain-bootstrap-contract",
        "Run the Phase 2 tests README toolchain bootstrap contract",
    );
    named_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Phase 2 tests README toolchain bootstrap contract");
    test_step.dependOn(&run_unit_tests.step);
}
