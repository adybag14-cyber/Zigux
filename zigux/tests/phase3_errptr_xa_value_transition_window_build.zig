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
        .root_source_file = b.path("phase3_errptr_xa_value_transition_window.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);

    const tests = b.addTest(.{
        .name = "phase3-errptr-xa-value-transition-window",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase3-errptr-xa-value-transition-window",
        "Run the Lane 29 err_ptr/xa_value transition-window replay",
    );
    step.dependOn(&run.step);
}
