const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const libfs_module = b.createModule(.{
        .root_source_file = b.path("../../fs/libfs.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase13_libfs_module = b.createModule(.{
        .root_source_file = b.path("phase13_libfs.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_libfs_module.addImport("libfs", libfs_module);

    const phase13_libfs_tests = b.addTest(.{
        .name = "phase13-libfs-tests",
        .root_module = phase13_libfs_module,
    });
    const run_phase13_libfs_tests = b.addRunArtifact(phase13_libfs_tests);

    const test_step = b.step("test", "Run Phase 13 filesystem helper tests");
    test_step.dependOn(&run_phase13_libfs_tests.step);
}
