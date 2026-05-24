const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const err_ptr_module = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xa_value_module = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value_module.addImport("err_ptr", err_ptr_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xa_value_band_partition.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr_module);
    root_module.addImport("xa_value", xa_value_module);

    const tests = b.addTest(.{
        .name = "phase3-errptr-xa-value-band-partition-test",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step(
        "phase3-errptr-xa-value-band-partition",
        "Run the focused Phase 3 err_ptr xa_value band-partition replay",
    );
    test_step.dependOn(&run_tests.step);
}
