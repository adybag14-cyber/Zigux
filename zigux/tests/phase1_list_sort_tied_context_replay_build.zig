const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_list_sort_tied_context_replay.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("../../tools/lib/list_sort.zig", list_sort_module);

    const run_tests = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-list-sort-tied-context-replay",
        "Run the standalone Lane 07 list_sort tied-context replay.",
    );
    step.dependOn(&run_tests.step);
}
