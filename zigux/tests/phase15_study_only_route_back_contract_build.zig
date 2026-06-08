const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_study_only_route_back_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-study-only-route-back-contract",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const focused = b.step(
        "phase15-study-only-route-back-contract",
        "Run the Phase 15 study-only route-back contract",
    );
    focused.dependOn(&run_unit_tests.step);

    const aggregate = b.step("test", "Run the Phase 15 study-only route-back contract");
    aggregate.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}
