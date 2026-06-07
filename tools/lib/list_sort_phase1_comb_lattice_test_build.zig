const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("list_sort_phase1_comb_lattice_test.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "list_sort", .module = list_sort_module },
            },
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const proof_step = b.step("list-sort-phase1-comb-lattice-test", "Run the Lane 12 list_sort comb lattice proof");
    proof_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
