const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "phase1-closure-makefile-boundary-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_closure_makefile_boundary_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "phase1-closure-makefile-boundary-contract",
        "Run the Lane 16 Phase 1 closure Makefile boundary contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 16 Phase 1 closure Makefile boundary contract tests.",
    );
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
