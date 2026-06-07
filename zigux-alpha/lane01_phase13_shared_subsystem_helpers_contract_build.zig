const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("lane01_phase13_shared_subsystem_helpers_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "lane01-phase13-shared-subsystem-helpers-contract",
        .root_module = module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract_step = b.step(
        "lane01-phase13-shared-subsystem-helpers-contract",
        "Run the Lane 01 Phase 13 shared subsystem helpers roadmap contract",
    );
    contract_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Lane 01 Phase 13 shared subsystem helpers roadmap contract");
    test_step.dependOn(&run_unit_tests.step);
    b.default_step.dependOn(&run_unit_tests.step);
}
