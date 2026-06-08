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
        .root_source_file = b.path("phase1_helper_ports_c_stride_latch_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("slab", slab_module);
    root_module.addImport("str_error_r", str_error_r_module);
    root_module.addImport("vsprintf", vsprintf_module);
    root_module.addImport("zalloc", zalloc_module);

    const stride_latch_tests = b.addTest(.{
        .name = "phase1-helper-ports-c-stride-latch-replay-tests",
        .root_module = root_module,
    });
    const run_stride_latch_tests = b.addRunArtifact(stride_latch_tests);

    const replay_step = b.step(
        "phase1-helper-ports-c-stride-latch-replay",
        "Run the Lane 10 stride-latch replay.",
    );
    replay_step.dependOn(&run_stride_latch_tests.step);

    const test_step = b.step("test", "Run the Lane 10 stride-latch replay tests.");
    test_step.dependOn(&run_stride_latch_tests.step);

    b.default_step.dependOn(test_step);
}
