const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });

    const test_module = b.createModule(.{
        .root_source_file = b.path("list_sort_phase1_pendulum_lattice_test.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("list_sort", list_sort_module);

    const unit_tests = b.addTest(.{
        .root_module = test_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const named_step = b.step("list-sort-phase1-pendulum-lattice-test", "Run the list_sort Phase 1 pendulum lattice test");
    named_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run list_sort Phase 1 pendulum lattice tests");
    test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}
