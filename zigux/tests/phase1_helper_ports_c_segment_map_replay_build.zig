const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const slab_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    });
    const str_error_r_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    });
    const vsprintf_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    });
    const zalloc_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_c_segment_map_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("slab", slab_module);
    root_module.addImport("str_error_r", str_error_r_module);
    root_module.addImport("vsprintf", vsprintf_module);
    root_module.addImport("zalloc", zalloc_module);

    const segment_map_tests = b.addTest(.{
        .name = "phase1-helper-ports-c-segment-map-replay",
        .root_module = root_module,
    });
    const run_segment_map_tests = b.addRunArtifact(segment_map_tests);

    const segment_map_step = b.step(
        "phase1-helper-ports-c-segment-map-replay",
        "Run Lane 10 Phase 1 helper ports C segment-map replay",
    );
    segment_map_step.dependOn(&run_segment_map_tests.step);

    const test_step = b.step("test", "Run Lane 10 Phase 1 helper ports C segment-map replay");
    test_step.dependOn(&run_segment_map_tests.step);
    b.default_step.dependOn(test_step);
}
