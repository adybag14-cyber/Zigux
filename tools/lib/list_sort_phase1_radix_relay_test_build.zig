const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("list_sort_phase1_radix_relay_test.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "list_sort", .module = list_sort_module },
            },
        }),
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step("list-sort-phase1-radix-relay-test", "Run the Lane 12 list_sort radix relay proof");
    test_step.dependOn(&run_unit_tests.step);

    const default_test_step = b.step("test", "Run tests");
    default_test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}
