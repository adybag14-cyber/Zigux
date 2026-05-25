const std = @import("std");

fn addPhase3Mmio(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    narrow.addImport("abi_bindings", abi_bindings);

    const root_module = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);
    root_module.addImport("unsafe_policy", narrow);
    root_module.addImport("narrow", narrow);
    root_module.addImport("narrow_unsafe", narrow);

    const tests = b.addTest(.{
        .name = "phase3-mmio-test",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

fn addPhase3Narrow(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);

    const tests = b.addTest(.{
        .name = "phase3-narrow-test",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const phase3_mmio = addPhase3Mmio(b, target, optimize);
    const phase3_narrow = addPhase3Narrow(b, target, optimize);

    const step = b.step(
        "phase3-mmio-narrow-test",
        "Run the focused Phase 3 mmio helper and raw-pointer boundary packets through a standalone combined build shard",
    );
    step.dependOn(&phase3_mmio.step);
    step.dependOn(&phase3_narrow.step);
}
