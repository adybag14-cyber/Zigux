const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_c_overflow_value_replay.zig"),
        .target = target,
        .optimize = optimize,
    });

    root.addImport("slab", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    }));
    root.addImport("str_error_r", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    }));
    root.addImport("vsprintf", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    }));
    root.addImport("zalloc", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    }));

    const tests = b.addTest(.{
        .root_module = root,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step("phase1-helper-ports-c-overflow-value-replay", "Run the Lane 10 helper ports C overflow/value replay");
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 10 helper ports C overflow/value replay");
    test_step.dependOn(&run_tests.step);
}
