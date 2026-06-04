const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const test_mod = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_c_reentrant_reuse_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_mod.addImport("slab", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    }));
    test_mod.addImport("str_error_r", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    }));
    test_mod.addImport("vsprintf", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    }));
    test_mod.addImport("zalloc", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    }));

    const tests = b.addTest(.{ .root_module = test_mod });
    const run_tests = b.addRunArtifact(tests);

    const named = b.step("phase1-helper-ports-c-reentrant-reuse-replay", "Run the Phase 1 helper ports C reentrant reuse replay");
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_tests.step);
}
