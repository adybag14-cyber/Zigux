const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_sort = b.addModule("list_sort", .{
        .root_source_file = b.path("list_sort.zig"),
    });

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("list_sort_phase1_braid_stability_test.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "list_sort", .module = list_sort },
            },
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const named_step = b.step(
        "list-sort-phase1-braid-stability-test",
        "Run the Phase 1 list_sort braid stability helper-local test",
    );
    named_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
