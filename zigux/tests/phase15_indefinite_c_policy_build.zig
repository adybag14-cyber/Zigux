const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_indefinite_c_policy.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase15-indefinite-c-policy",
        .root_module = module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);
    run_unit_tests.setCwd(b.path("../.."));

    const test_step = b.step("test", "Run the Phase 15 indefinite-C policy test");
    test_step.dependOn(&run_unit_tests.step);

    const named_step = b.step("phase15-indefinite-c-policy", "Run the focused Phase 15 indefinite-C policy test");
    named_step.dependOn(&run_unit_tests.step);
}
