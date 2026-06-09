const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("lane01_phase8_userspace_adjacent_tooling_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "lane01-phase8-userspace-adjacent-tooling-contract",
        .root_module = module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract_step = b.step(
        "lane01-phase8-userspace-adjacent-tooling-contract",
        "Run the Lane 01 Phase 8 userspace-adjacent tooling roadmap contract",
    );
    contract_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Lane 01 Phase 8 userspace-adjacent tooling roadmap contract");
    test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}
