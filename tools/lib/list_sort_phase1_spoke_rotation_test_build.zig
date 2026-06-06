const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_sort = b.createModule(.{
        .root_source_file = b.path("list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });
    const test_module = b.createModule(.{
        .root_source_file = b.path("list_sort_phase1_spoke_rotation_test.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "list_sort", .module = list_sort },
        },
    });
    const tests = b.addTest(.{
        .root_module = test_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step("list-sort-phase1-spoke-rotation-test", "Run the Phase 1 list_sort spoke rotation proof");
    test_step.dependOn(&run_tests.step);

    const default_test_step = b.step("test", "Run tests");
    default_test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}
