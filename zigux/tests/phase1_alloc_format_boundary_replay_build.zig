const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_alloc_format_boundary_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("slab", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    }));
    root_module.addImport("str_error_r", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    }));
    root_module.addImport("vsprintf", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    }));
    root_module.addImport("zalloc", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    }));

    const tests = b.addTest(.{
        .name = "phase1-alloc-format-boundary-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-alloc-format-boundary-replay",
        "Run the Phase 1 alloc/format boundary replay from zigux/tests",
    );
    step.dependOn(&run.step);
}
