const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("list_sort_phase1_bucket_reshaping_test.zig"),
        .target = target,
        .optimize = optimize,
    });
    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_sort", list_sort_module);

    const tests = b.addTest(.{
        .name = "list-sort-phase1-bucket-reshaping-test",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const phase1_step = b.step(
        "list-sort-phase1-bucket-reshaping-test",
        "Run the Phase 1 list_sort repeated bucket reshaping helper test",
    );
    phase1_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the helper-local list_sort bucket reshaping test");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
