const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const libfs_module = b.createModule(.{
        .root_source_file = b.path("../../fs/libfs.zig"),
        .target = target,
        .optimize = optimize,
    });
    const devres_module = b.createModule(.{
        .root_source_file = b.path("../../lib/devres.zig"),
        .target = target,
        .optimize = optimize,
    });
    const landlock_ruleset_module = b.createModule(.{
        .root_source_file = b.path("../../security/landlock/ruleset.zig"),
        .target = target,
        .optimize = optimize,
    });
    const landlock_syscalls_module = b.createModule(.{
        .root_source_file = b.path("../../security/landlock/syscalls.zig"),
        .target = target,
        .optimize = optimize,
    });

    const phase13_libfs_module = b.createModule(.{
        .root_source_file = b.path("phase13_libfs.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_libfs_module.addImport("libfs", libfs_module);

    const phase13_devres_module = b.createModule(.{
        .root_source_file = b.path("phase13_devres.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_devres_module.addImport("devres", devres_module);

    const phase13_landlock_ruleset_module = b.createModule(.{
        .root_source_file = b.path("phase13_landlock_ruleset.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_landlock_ruleset_module.addImport("landlock_ruleset", landlock_ruleset_module);

    const phase13_landlock_ruleset_reviewability_module = b.createModule(.{
        .root_source_file = b.path("phase13_landlock_ruleset_reviewability.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_landlock_ruleset_reviewability_module.addImport("landlock_ruleset", landlock_ruleset_module);

    const phase13_landlock_syscalls_module = b.createModule(.{
        .root_source_file = b.path("phase13_landlock_syscalls.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_landlock_syscalls_module.addImport("landlock_syscalls", landlock_syscalls_module);

    const phase13_libfs_reviewability_module = b.createModule(.{
        .root_source_file = b.path("phase13_libfs_reviewability.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_libfs_reviewability_module.addImport("libfs", libfs_module);

    const phase13_libfs_tests = b.addTest(.{
        .name = "phase13-libfs-tests",
        .root_module = phase13_libfs_module,
    });
    const run_phase13_libfs_tests = b.addRunArtifact(phase13_libfs_tests);

    const phase13_devres_tests = b.addTest(.{
        .name = "phase13-devres-tests",
        .root_module = phase13_devres_module,
    });
    const run_phase13_devres_tests = b.addRunArtifact(phase13_devres_tests);

    const phase13_landlock_ruleset_tests = b.addTest(.{
        .name = "phase13-landlock-ruleset-tests",
        .root_module = phase13_landlock_ruleset_module,
    });
    const run_phase13_landlock_ruleset_tests = b.addRunArtifact(phase13_landlock_ruleset_tests);

    const phase13_landlock_ruleset_reviewability_tests = b.addTest(.{
        .name = "phase13-landlock-ruleset-reviewability-tests",
        .root_module = phase13_landlock_ruleset_reviewability_module,
    });
    const run_phase13_landlock_ruleset_reviewability_tests = b.addRunArtifact(phase13_landlock_ruleset_reviewability_tests);

    const phase13_landlock_syscalls_tests = b.addTest(.{
        .name = "phase13-landlock-syscalls-tests",
        .root_module = phase13_landlock_syscalls_module,
    });
    const run_phase13_landlock_syscalls_tests = b.addRunArtifact(phase13_landlock_syscalls_tests);

    const phase13_libfs_reviewability_tests = b.addTest(.{
        .name = "phase13-libfs-reviewability-tests",
        .root_module = phase13_libfs_reviewability_module,
    });
    const run_phase13_libfs_reviewability_tests = b.addRunArtifact(phase13_libfs_reviewability_tests);

    const test_step = b.step("test", "Run Phase 13 shared helper tests");
    test_step.dependOn(&run_phase13_libfs_tests.step);
    test_step.dependOn(&run_phase13_devres_tests.step);
    test_step.dependOn(&run_phase13_landlock_ruleset_tests.step);
    test_step.dependOn(&run_phase13_landlock_ruleset_reviewability_tests.step);
    test_step.dependOn(&run_phase13_landlock_syscalls_tests.step);
    test_step.dependOn(&run_phase13_libfs_reviewability_tests.step);
}
