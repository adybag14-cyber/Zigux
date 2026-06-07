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
        .root_source_file = b.path("list_sort_phase1_delta_fan_test.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "list_sort", .module = list_sort_module },
        },
    });

    const unit_tests = b.addTest(.{
        .root_module = test_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);
    const named = b.step("list-sort-phase1-delta-fan-test", "Run the Lane 12 list_sort delta fan proof");
    named.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}
