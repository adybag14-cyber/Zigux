const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_cross_makefile_toolchain_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase2-cross-makefile-toolchain-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "phase2-cross-makefile-toolchain-contract",
        "Run the Phase 2 cross Makefile/toolchain contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 cross Makefile/toolchain contract");
    test_step.dependOn(&run_tests.step);
}
