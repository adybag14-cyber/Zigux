const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const err_ptr = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xa_value = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value.addImport("err_ptr", err_ptr);

    const starter_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    starter_module.addImport("err_ptr", err_ptr);
    starter_module.addImport("xa_value", xa_value);

    const starter_tests = b.addTest(.{
        .root_module = starter_module,
    });
    const run_starter_tests = b.addRunArtifact(starter_tests);

    const dump_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    dump_module.addImport("err_ptr", err_ptr);
    dump_module.addImport("xa_value", xa_value);

    const dump_exe = b.addExecutable(.{
        .name = "phase3-errptr-xarray-dump",
        .root_module = dump_module,
    });
    const run_dump = b.addRunArtifact(dump_exe);

    const test_step = b.step(
        "phase3-errptr-xarray-test",
        "Run the Phase 3 err_ptr/xarray starter packet and dump replay",
    );
    test_step.dependOn(&run_starter_tests.step);
    test_step.dependOn(&run_dump.step);
}
