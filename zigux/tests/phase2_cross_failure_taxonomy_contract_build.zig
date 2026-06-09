const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_failure_taxonomy_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(contract_tests);
    const route = b.step("phase2-cross-failure-taxonomy-contract", "Run the Lane 21 direct cross failure taxonomy contract");
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 21 direct cross failure taxonomy contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
