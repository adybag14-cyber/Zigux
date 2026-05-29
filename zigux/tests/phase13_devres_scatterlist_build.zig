const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const devres_scatterlist_module = b.createModule(.{
        .root_source_file = b.path("../../lib/devres_scatterlist.zig"),
        .target = target,
        .optimize = optimize,
    });
    const phase13_devres_scatterlist_module = b.createModule(.{
        .root_source_file = b.path("phase13_devres_scatterlist.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_devres_scatterlist_module.addImport("devres_scatterlist", devres_scatterlist_module);

    const tests = b.addTest(.{
        .name = "phase13-devres-scatterlist-tests",
        .root_module = phase13_devres_scatterlist_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const phase13_devres_scatterlist_empty_table_module = b.createModule(.{
        .root_source_file = b.path("phase13_devres_scatterlist_empty_table.zig"),
        .target = target,
        .optimize = optimize,
    });
    phase13_devres_scatterlist_empty_table_module.addImport("devres_scatterlist", devres_scatterlist_module);

    const empty_table_tests = b.addTest(.{
        .name = "phase13-devres-scatterlist-empty-table-tests",
        .root_module = phase13_devres_scatterlist_empty_table_module,
    });
    const run_empty_table_tests = b.addRunArtifact(empty_table_tests);

    const test_step = b.step("test", "Run Phase 13 devres scatterlist helper tests");
    test_step.dependOn(&run_tests.step);
    test_step.dependOn(&run_empty_table_tests.step);
}
