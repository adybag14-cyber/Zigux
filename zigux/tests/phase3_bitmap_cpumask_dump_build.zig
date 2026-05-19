const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const uapi_bitmap_cpumask = b.createModule(.{
        .root_source_file = b.path("../uapi/bitmap_cpumask.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_cpumask_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/bitmap_cpumask.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_cpumask_binding.addImport("uapi_bitmap_cpumask", uapi_bitmap_cpumask);

    const bitmap_view_helper = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_view_helper.addImport("bitmap_cpumask_binding", bitmap_cpumask_binding);

    const cpumask_view_helper = b.createModule(.{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpumask_view_helper.addImport("bitmap_cpumask_binding", bitmap_cpumask_binding);
    cpumask_view_helper.addImport("bitmap_view_helper", bitmap_view_helper);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap_cpumask_binding", bitmap_cpumask_binding);
    root_module.addImport("bitmap_view_helper", bitmap_view_helper);
    root_module.addImport("cpumask_view_helper", cpumask_view_helper);

    const exe = b.addExecutable(.{
        .name = "phase3-bitmap-cpumask-dump",
        .root_module = root_module,
    });
    const run_dump = b.addRunArtifact(exe);

    const dump_step = b.step(
        "phase3-bitmap-cpumask-dump",
        "Run the Phase 3 bitmap/cpumask interop dump",
    );
    dump_step.dependOn(&run_dump.step);
}
