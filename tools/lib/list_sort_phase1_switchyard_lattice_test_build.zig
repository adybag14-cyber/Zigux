const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.graph.host;

    const list_sort_mod = b.createModule(.{
        .root_source_file = b.path("list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });

    const test_mod = b.createModule(.{
        .root_source_file = b.path("list_sort_phase1_switchyard_lattice_test.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "list_sort", .module = list_sort_mod },
        },
    });

    const unit_tests = b.addTest(.{
        .root_module = test_mod,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const named = b.step(
        "list-sort-phase1-switchyard-lattice-test",
        "Run the Lane 12 list_sort switchyard lattice proof",
    );
    named.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Lane 12 list_sort switchyard lattice proof");
    test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}
