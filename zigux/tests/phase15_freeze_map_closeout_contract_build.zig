const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("phase15_freeze_map_closeout_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase15-freeze-map-closeout-contract",
        .root_module = module,
    });
    const run_tests = b.addRunArtifact(tests);

    const step = b.step("phase15-freeze-map-closeout-contract", "Run the Phase 15 freeze-map closeout contract");
    step.dependOn(&run_tests.step);

    b.default_step.dependOn(step);
}
