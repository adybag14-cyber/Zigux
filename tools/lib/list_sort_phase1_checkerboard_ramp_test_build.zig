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
        .root_source_file = b.path("list_sort_phase1_checkerboard_ramp_test.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_sort", list_sort_module);

    const unit_tests = b.addTest(.{
        .name = "list-sort-phase1-checkerboard-ramp-test",
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step("list-sort-phase1-checkerboard-ramp-test", "Run the Lane 12 list_sort checkerboard ramp proof");
    test_step.dependOn(&run_unit_tests.step);

    const default_test_step = b.step("test", "Run the Lane 12 list_sort checkerboard ramp proof");
    default_test_step.dependOn(&run_unit_tests.step);
    b.default_step.dependOn(&run_unit_tests.step);
}
