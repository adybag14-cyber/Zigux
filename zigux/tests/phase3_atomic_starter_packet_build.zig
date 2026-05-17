const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const atomic = b.createModule(.{
        .root_source_file = b.path("../helpers/atomic.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_atomic_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("atomic", atomic);

    const unit_tests = b.addTest(.{
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase3-atomic-starter-packet-test",
        "Run the Phase 3 atomic starter-packet self-check",
    );
    test_step.dependOn(&run_unit_tests.step);
}
