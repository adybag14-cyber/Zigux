const std = @import("std");

fn addErrPtrTests(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase3-errptr-helper-root",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addXaValueTests(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const err_ptr = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    const tests = b.addTest(.{
        .name = "phase3-xa-value-helper-root",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addDumpRoute(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
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
    return b.addRunArtifact(exe);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const err_ptr_tests = addErrPtrTests(b, target, optimize);
    const xa_value_tests = addXaValueTests(b, target, optimize);
    const dump_route = addDumpRoute(b, target, optimize);

    const step = b.step(
        "phase3-errptr-xarray-dump-slice-test",
        "Run the Lane 29 err_ptr and xa_value helper roots together with the current err_ptr/xarray dump route",
    );
    step.dependOn(&err_ptr_tests.step);
    step.dependOn(&xa_value_tests.step);
    step.dependOn(&dump_route.step);
}