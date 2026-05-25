const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_empty_singleton_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("list_sort", list_sort_module);

    const tests = b.addTest(.{
        .name = "phase1-list-sort-empty-singleton-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-list-sort-empty-singleton-replay",
        "Run the Lane 12 list_sort empty and singleton replay",
    );
    step.dependOn(&run.step);
}
