const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_step = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane01_phase13_shared_subsystem_helpers_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(test_step);
    run_tests.setCwd(b.path("."));

    const contract_step = b.step("lane01-phase13-shared-subsystem-helpers-contract", "Run the Lane 01 Phase 13 shared subsystem helpers roadmap contract");
    contract_step.dependOn(&run_tests.step);

    const default_test_step = b.step("test", "Run the Lane 01 Phase 13 shared subsystem helpers roadmap contract");
    default_test_step.dependOn(&run_tests.step);
}
