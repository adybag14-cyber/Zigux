const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_cross_makefile_route_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase2-cross-makefile-route-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const route_step = b.step(
        "phase2-cross-makefile-route-contract",
        "Validate the Phase 2 cross Makefile route contract",
    );
    route_step.dependOn(&run_tests.step);

    const all_tests = b.step("test", "Run the Phase 2 cross Makefile route contract");
    all_tests.dependOn(&run_tests.step);
}
