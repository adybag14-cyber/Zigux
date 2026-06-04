const std = @import("std");

fn addIdaAllocErrptrXarrayTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step {
    const ida_bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const ida_alloc_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_alloc_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_alloc_view.addImport("ida_bitmap_view", ida_bitmap_view);

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

    const ida_root = b.createModule(.{
        .root_source_file = b.path("phase3_ida_alloc_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_root.addImport("ida_alloc_view", ida_alloc_view);
    ida_root.addImport("ida_bitmap_view", ida_bitmap_view);

    const errptr_xarray_root = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_root.addImport("err_ptr", err_ptr);
    errptr_xarray_root.addImport("xa_value", xa_value);

    const ida_tests = b.addTest(.{
        .name = "phase3-ida-alloc-starter-packet",
        .root_module = ida_root,
    });
    const errptr_xarray_tests = b.addTest(.{
        .name = "phase3-errptr-xarray-starter-packet",
        .root_module = errptr_xarray_root,
    });

    const step = b.step(
        "phase3-ida-alloc-errptr-xarray-test",
        "Run the Phase 3 IDA allocation and err_ptr/xarray starter packets together",
    );
    const ida_run = b.addRunArtifact(ida_tests);
    const errptr_xarray_run = b.addRunArtifact(errptr_xarray_tests);
    step.dependOn(&ida_run.step);
    step.dependOn(&errptr_xarray_run.step);
    return step;
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const tests = addIdaAllocErrptrXarrayTest(b, target, optimize);

    const test_step = b.step("test", "Run the Phase 3 IDA allocation plus err_ptr/xarray harness");
    test_step.dependOn(tests);
}
