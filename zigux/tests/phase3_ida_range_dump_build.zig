const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const ida_alloc_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_alloc_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_alloc_view.addImport("ida_bitmap_view", ida_bitmap_view);

    const ida_range_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_range_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_range_view.addImport("ida_bitmap_view", ida_bitmap_view);
    ida_range_view.addImport("ida_alloc_view", ida_alloc_view);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_range_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("ida_bitmap_view", ida_bitmap_view);
    root_module.addImport("ida_range_view", ida_range_view);

    const exe = b.addExecutable(.{
        .name = "phase3-ida-range-dump",
        .root_module = root_module,
    });
    const run_dump = b.addRunArtifact(exe);

    const dump_step = b.step(
        "phase3-ida-range-dump",
        "Run the Phase 3 ida range interop dump",
    );
    dump_step.dependOn(&run_dump.step);
}
