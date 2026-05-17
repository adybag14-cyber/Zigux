const std = @import("std");

fn addDevTStarterModules(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) struct {
    root_module: *std.Build.Module,
    uapi_dev_t: *std.Build.Module,
    uapi_version: *std.Build.Module,
    dev_t_binding: *std.Build.Module,
} {
    const uapi_dev_t = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const uapi_version = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    const dev_t_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_dev_t_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("dev_t_binding", dev_t_binding);
    root_module.addImport("uapi_version", uapi_version);

    return .{
        .root_module = root_module,
        .uapi_dev_t = uapi_dev_t,
        .uapi_version = uapi_version,
        .dev_t_binding = dev_t_binding,
    };
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const modules = addDevTStarterModules(b, target, optimize);
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

    const dev_t_unit_tests = b.addTest(.{
        .root_module = modules.root_module,
    });
    const run_dev_t_unit_tests = b.addRunArtifact(dev_t_unit_tests);

    const errptr_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_root_module.addImport("err_ptr", err_ptr);
    errptr_root_module.addImport("xa_value", xa_value);

    const errptr_unit_tests = b.addTest(.{
        .root_module = errptr_root_module,
    });
    const run_errptr_unit_tests = b.addRunArtifact(errptr_unit_tests);

    const phase3_test_step = b.step(
        "phase3-test",
        "Run the current shared Phase 3 starter-packet self-checks",
    );
    phase3_test_step.dependOn(&run_dev_t_unit_tests.step);
    phase3_test_step.dependOn(&run_errptr_unit_tests.step);

    const dev_t_starter_step = b.step(
        "phase3-dev-t-starter-packet-test",
        "Run the Phase 3 dev_t starter-packet ABI self-check",
    );
    dev_t_starter_step.dependOn(&run_dev_t_unit_tests.step);

    const errptr_xarray_starter_step = b.step(
        "phase3-errptr-xarray-starter-packet-test",
        "Run the Phase 3 err_ptr/xarray starter-packet self-check",
    );
    errptr_xarray_starter_step.dependOn(&run_errptr_unit_tests.step);
}
