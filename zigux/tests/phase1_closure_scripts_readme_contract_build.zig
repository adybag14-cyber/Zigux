const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_closure_scripts_readme_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "phase1-closure-scripts-readme-contract",
        "Validate Phase 1 closure scripts README reminder alignment",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Phase 1 closure scripts README contract tests");
    test_step.dependOn(&run_tests.step);
}
