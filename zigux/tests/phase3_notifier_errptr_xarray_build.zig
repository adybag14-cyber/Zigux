const std = @import("std");

fn addNotifierErrptrXarrayTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step {
    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const notifier_view = b.createModule(.{
        .root_source_file = b.path("../helpers/notifier_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    notifier_view.addImport("notifier_abi", notifier_abi);

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

    const notifier_root = b.createModule(.{
        .root_source_file = b.path("phase3_notifier_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    notifier_root.addImport("notifier_abi", notifier_abi);
    notifier_root.addImport("notifier_view", notifier_view);

    const errptr_xarray_root = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_root.addImport("err_ptr", err_ptr);
    errptr_xarray_root.addImport("xa_value", xa_value);

    const notifier_tests = b.addTest(.{
        .name = "phase3-notifier-starter-packet",
        .root_module = notifier_root,
    });
    const errptr_xarray_tests = b.addTest(.{
        .name = "phase3-errptr-xarray-starter-packet",
        .root_module = errptr_xarray_root,
    });

    const step = b.step(
        "phase3-notifier-errptr-xarray-test",
        "Run the Phase 3 notifier and err_ptr/xarray starter packets together",
    );
    const notifier_run = b.addRunArtifact(notifier_tests);
    const errptr_xarray_run = b.addRunArtifact(errptr_xarray_tests);
    step.dependOn(&notifier_run.step);
    step.dependOn(&errptr_xarray_run.step);
    return step;
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const tests = addNotifierErrptrXarrayTest(b, target, optimize);

    const test_step = b.step("test", "Run the Phase 3 notifier plus err_ptr/xarray harness");
    test_step.dependOn(tests);
}
