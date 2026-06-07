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
        .root_source_file = b.path("list_sort_phase1_carry_cascade_test.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_sort", list_sort_module);

    const unit_tests = b.addTest(.{
        .root_module = root_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    const carry_cascade_step = b.step(
        "list-sort-phase1-carry-cascade-test",
        "Run the Phase 1 list_sort carry-cascade helper proof",
    );
    carry_cascade_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run unit tests");
    test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}
