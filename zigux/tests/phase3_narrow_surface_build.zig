const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow_surface = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow_surface.addImport("abi_bindings", abi_bindings);

    const unit_tests = b.addTest(.{
        .root_module = narrow_surface,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase3-narrow-surface-test",
        "Run the Phase 3 narrow unsafe-surface self-check",
    );
    test_step.dependOn(&run_unit_tests.step);
}
