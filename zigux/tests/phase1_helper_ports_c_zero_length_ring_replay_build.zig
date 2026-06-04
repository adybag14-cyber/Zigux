const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_c_zero_length_ring_replay.zig"),
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
        .name = "phase1-helper-ports-c-zero-length-ring-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-helper-ports-c-zero-length-ring-replay",
        "Run the Phase 1 helper ports C zero-length/ring replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 helper ports C zero-length/ring replay");
    test_step.dependOn(&run_tests.step);
}
