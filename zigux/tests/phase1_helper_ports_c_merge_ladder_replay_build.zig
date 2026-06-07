const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const slab_mod = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    });
    const str_error_r_mod = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    });
    const vsprintf_mod = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    });
    const zalloc_mod = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_mod = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_c_merge_ladder_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_mod.addImport("slab", slab_mod);
    root_mod.addImport("str_error_r", str_error_r_mod);
    root_mod.addImport("vsprintf", vsprintf_mod);
    root_mod.addImport("zalloc", zalloc_mod);

    const tests = b.addTest(.{
        .name = "phase1-helper-ports-c-merge-ladder-replay-tests",
        .root_module = root_mod,
    });

    const run_tests = b.addRunArtifact(tests);
    const named = b.step("phase1-helper-ports-c-merge-ladder-replay", "Run the Lane 10 Phase 1 helper ports C merge-ladder replay");
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
