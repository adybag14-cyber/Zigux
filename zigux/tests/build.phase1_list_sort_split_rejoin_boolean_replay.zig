const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_split_rejoin_boolean_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_sort", list_sort_module);

    const tests = b.addTest(.{
        .name = "phase1-list-sort-split-rejoin-boolean-replay",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase1-list-sort-split-rejoin-boolean-replay",
        "Run the Phase 1 list_sort split/rejoin boolean replay",
    );
    test_step.dependOn(&run_tests.step);

    const all_step = b.step("test", "Run this focused Phase 1 list_sort replay");
    all_step.dependOn(&run_tests.step);
}
