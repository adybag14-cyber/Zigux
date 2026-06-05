const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_aggregate_validator_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const named_step = b.step(
        "phase2-aggregate-validator-contract",
        "Run the Phase 2 aggregate validator contract",
    );
    named_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Phase 2 aggregate validator contract");
    test_step.dependOn(&run_unit_tests.step);
}
