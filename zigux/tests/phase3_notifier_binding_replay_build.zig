const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_notifier_binding_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("notifier_abi", notifier_abi);

    const unit_tests = b.addTest(.{
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase3-notifier-binding-replay",
        "Run the Phase 3 notifier binding replay",
    );
    test_step.dependOn(&run_unit_tests.step);
}
