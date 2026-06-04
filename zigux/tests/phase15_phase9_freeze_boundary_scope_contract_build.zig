const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_phase9_freeze_boundary_scope_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-phase9-freeze-boundary-scope-contract",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract_step = b.step(
        "phase15-phase9-freeze-boundary-scope-contract",
        "Run the Phase 15 Phase 9 freeze-boundary scope contract",
    );
    contract_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Phase 15 Phase 9 freeze-boundary scope contract");
    test_step.dependOn(&run_unit_tests.step);
}
