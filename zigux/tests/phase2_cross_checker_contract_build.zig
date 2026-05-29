const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_checker_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "phase2-cross-checker-contract",
        "Validate the Lane 21 direct cross checker Zig contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 21 direct cross checker contract tests");
    test_step.dependOn(&run_tests.step);
}
