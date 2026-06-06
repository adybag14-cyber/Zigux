const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const slab = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    });
    const str_error_r = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    });
    const vsprintf = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    });
    const zalloc = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_c_overlay_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("slab", slab);
    root_module.addImport("str_error_r", str_error_r);
    root_module.addImport("vsprintf", vsprintf);
    root_module.addImport("zalloc", zalloc);

    const tests = b.addTest(.{
        .name = "phase1-helper-ports-c-overlay-replay-tests",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const named = b.step("phase1-helper-ports-c-overlay-replay", "Run the Lane 10 helper ports C overlay replay");
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 10 helper ports C overlay replay");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
