const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_context_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_sort", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    }));

    const unit_tests = b.addTest(.{
        .root_module = root_module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const step = b.step(
        "phase1-list-sort-context-replay",
        "Run the Phase 1 list_sort context replay.",
    );
    step.dependOn(&run_unit_tests.step);
}
