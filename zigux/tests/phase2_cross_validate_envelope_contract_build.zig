const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_cross_validate_envelope_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const route = b.step(
        "phase2-cross-validate-envelope-contract",
        "Run the Phase 2 cross validate-envelope contract",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 cross validate-envelope contract");
    test_step.dependOn(&run_tests.step);
}
