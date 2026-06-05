const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_phase14_exact_readback_boundary_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-phase14-exact-readback-boundary-contract",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const contract = b.step(
        "phase15-phase14-exact-readback-boundary-contract",
        "Run the Phase 14 exact-readback boundary contract",
    );
    contract.dependOn(&run_unit_tests.step);

    const aggregate = b.step("test", "Run the Phase 14 exact-readback boundary contract");
    aggregate.dependOn(&run_unit_tests.step);
}
