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

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);

    const exe = b.addExecutable(.{
        .name = "phase3-errptr-xarray-dump",
        .root_module = root_module,
    });
    const run_dump = b.addRunArtifact(exe);

    const dump_step = b.step(
        "phase3-errptr-xarray-dump",
        "Run the Phase 3 err_ptr/xarray interop dump",
    );
    dump_step.dependOn(&run_dump.step);

    const test_step = b.step(
        "test",
        "Run the Phase 3 err_ptr/xarray interop dump",
    );
    test_step.dependOn(&run_dump.step);

    b.default_step.dependOn(test_step);
}
