const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("list_sort_phase1_ring_fold_test.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_sort", list_sort_module);

    const tests = b.addTest(.{
        .name = "list-sort-phase1-ring-fold-test",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step("list-sort-phase1-ring-fold-test", "Run the Lane 12 list_sort ring-fold helper proof");
    test_step.dependOn(&run_tests.step);

    const alias_step = b.step("test", "Run the Lane 12 list_sort ring-fold helper proof");
    alias_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
