const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_closure_stage_helper_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase2-closure-stage-helper-contract",
        "Run the Lane 22 Phase 2 staged archive helper closure contract.",
    );
    contract_step.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the Lane 22 Phase 2 staged archive helper closure contract tests.",
    );
    test_step.dependOn(&run.step);
}
