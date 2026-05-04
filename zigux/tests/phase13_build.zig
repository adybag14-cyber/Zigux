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
    const devres_dma_coherent_module = b.createModule(.{
        .root_source_file = b.path("../../lib/devres_dma_coherent.zig"),
        .target = target,
        .optimize = optimize,
    });
    const devres_scatterlist_module = b.createModule(.{
        .root_source_file = b.path("../../lib/devres_scatterlist.zig"),
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
    const phase13_devres_dma_coherent_module = b.createModule(.{
        .root_source_file = b.path("phase13_devres_dma_coherent.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_devres_dma_coherent_module.addImport("devres_dma_coherent", devres_dma_coherent_module);
    const phase13_devres_scatterlist_module = b.createModule(.{
        .root_source_file = b.path("phase13_devres_scatterlist.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_devres_scatterlist_module.addImport("devres_scatterlist", devres_scatterlist_module);
    const phase13_devres_iounmap_reviewability_module = b.createModule(.{
        .root_source_file = b.path("phase13_devres_iounmap_reviewability.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_devres_iounmap_reviewability_module.addImport("devres", devres_module);
    const phase13_devres_iomap_reviewability_module = b.createModule(.{
        .root_source_file = b.path("phase13_devres_iomap_reviewability.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_devres_iomap_reviewability_module.addImport("devres", devres_module);
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
    const phase13_landlock_syscalls_reviewability_module = b.createModule(.{
        .root_source_file = b.path("phase13_landlock_syscalls_reviewability.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_landlock_syscalls_reviewability_module.addImport("landlock_syscalls", landlock_syscalls_module);
    const phase13_landlock_ruleset_fops_sync_module = b.createModule(.{
        .root_source_file = b.path("phase13_landlock_ruleset_fops_sync.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_landlock_ruleset_fops_sync_module.addImport("landlock_syscalls", landlock_syscalls_module);
    const phase13_libfs_reviewability_module = b.createModule(.{
        .root_source_file = b.path("phase13_libfs_reviewability.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_libfs_reviewability_module.addImport("libfs", libfs_module);
    const phase13_devres_reviewability_module = b.createModule(.{
        .root_source_file = b.path("phase13_devres_reviewability.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_devres_reviewability_module.addImport("devres", devres_module);
    const phase13_devres_wrapper_reviewability_module = b.createModule(.{
        .root_source_file = b.path("phase13_devres_wrapper_reviewability.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase13_notifier_list_reviewability_module = b.createModule(.{
        .root_source_file = b.path("phase13_notifier_list_reviewability.zig"),
        .target = target,
        .optimize = optimize,
    });
    const notifier_abi_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow_unsafe_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    const notifier_chain_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/notifier_chain_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    notifier_chain_view_module.addImport("notifier_abi_bindings", notifier_abi_module);
    notifier_chain_view_module.addImport("narrow_unsafe", narrow_unsafe_module);

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
    const phase13_devres_dma_coherent_tests = b.addTest(.{
        .name = "phase13-devres-dma-coherent-tests",
        .root_module = phase13_devres_dma_coherent_module,
    });
    const run_phase13_devres_dma_coherent_tests = b.addRunArtifact(phase13_devres_dma_coherent_tests);
    const phase13_devres_scatterlist_tests = b.addTest(.{
        .name = "phase13-devres-scatterlist-tests",
        .root_module = phase13_devres_scatterlist_module,
    });
    const run_phase13_devres_scatterlist_tests = b.addRunArtifact(phase13_devres_scatterlist_tests);
    const phase13_devres_iounmap_reviewability_tests = b.addTest(.{
        .name = "phase13-devres-iounmap-reviewability-tests",
        .root_module = phase13_devres_iounmap_reviewability_module,
    });
    const run_phase13_devres_iounmap_reviewability_tests = b.addRunArtifact(phase13_devres_iounmap_reviewability_tests);
    const phase13_devres_iomap_reviewability_tests = b.addTest(.{
        .name = "phase13-devres-iomap-reviewability-tests",
        .root_module = phase13_devres_iomap_reviewability_module,
    });
    const run_phase13_devres_iomap_reviewability_tests = b.addRunArtifact(phase13_devres_iomap_reviewability_tests);
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
    const phase13_landlock_syscalls_reviewability_tests = b.addTest(.{
        .name = "phase13-landlock-syscalls-reviewability-tests",
        .root_module = phase13_landlock_syscalls_reviewability_module,
    });
    const run_phase13_landlock_syscalls_reviewability_tests = b.addRunArtifact(phase13_landlock_syscalls_reviewability_tests);
    const phase13_landlock_ruleset_fops_sync_tests = b.addTest(.{
        .name = "phase13-landlock-ruleset-fops-sync-tests",
        .root_module = phase13_landlock_ruleset_fops_sync_module,
    });
    const run_phase13_landlock_ruleset_fops_sync_tests = b.addRunArtifact(phase13_landlock_ruleset_fops_sync_tests);
    const phase13_libfs_reviewability_tests = b.addTest(.{
        .name = "phase13-libfs-reviewability-tests",
        .root_module = phase13_libfs_reviewability_module,
    });
    const run_phase13_libfs_reviewability_tests = b.addRunArtifact(phase13_libfs_reviewability_tests);
    const phase13_devres_reviewability_tests = b.addTest(.{
        .name = "phase13-devres-reviewability-tests",
        .root_module = phase13_devres_reviewability_module,
    });
    const run_phase13_devres_reviewability_tests = b.addRunArtifact(phase13_devres_reviewability_tests);
    const phase13_devres_wrapper_reviewability_tests = b.addTest(.{
        .name = "phase13-devres-wrapper-reviewability-tests",
        .root_module = phase13_devres_wrapper_reviewability_module,
    });
    const run_phase13_devres_wrapper_reviewability_tests = b.addRunArtifact(phase13_devres_wrapper_reviewability_tests);
    const phase13_notifier_list_reviewability_tests = b.addTest(.{
        .name = "phase13-notifier-list-reviewability-tests",
        .root_module = phase13_notifier_list_reviewability_module,
    });
    const run_phase13_notifier_list_reviewability_tests = b.addRunArtifact(phase13_notifier_list_reviewability_tests);
    const phase13_notifier_chain_view_tests = b.addTest(.{
        .name = "phase13-notifier-chain-view-tests",
        .root_module = notifier_chain_view_module,
    });
    const run_phase13_notifier_chain_view_tests = b.addRunArtifact(phase13_notifier_chain_view_tests);

    const test_step = b.step("test", "Run Phase 13 shared helper tests");
    test_step.dependOn(&run_phase13_libfs_tests.step);
    test_step.dependOn(&run_phase13_devres_tests.step);
    test_step.dependOn(&run_phase13_devres_dma_coherent_tests.step);
    test_step.dependOn(&run_phase13_devres_scatterlist_tests.step);
    test_step.dependOn(&run_phase13_devres_iounmap_reviewability_tests.step);
    test_step.dependOn(&run_phase13_devres_iomap_reviewability_tests.step);
    test_step.dependOn(&run_phase13_landlock_ruleset_tests.step);
    test_step.dependOn(&run_phase13_landlock_ruleset_reviewability_tests.step);
    test_step.dependOn(&run_phase13_landlock_syscalls_tests.step);
    test_step.dependOn(&run_phase13_landlock_syscalls_reviewability_tests.step);
    test_step.dependOn(&run_phase13_landlock_ruleset_fops_sync_tests.step);
    test_step.dependOn(&run_phase13_libfs_reviewability_tests.step);
    test_step.dependOn(&run_phase13_devres_reviewability_tests.step);
    test_step.dependOn(&run_phase13_devres_wrapper_reviewability_tests.step);
    test_step.dependOn(&run_phase13_notifier_list_reviewability_tests.step);
    test_step.dependOn(&run_phase13_notifier_chain_view_tests.step);
}
