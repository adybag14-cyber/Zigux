const std = @import("std");

fn addBarrierTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("../helpers/barrier.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "phase3-barrier-test",
        .root_module = root_module,
    });

    return b.addRunArtifact(tests);
}

fn addNarrowTest(
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

    const barrier = addBarrierTest(b, target, optimize);
    const narrow = addNarrowTest(b, target, optimize);

    const step = b.step(
        "phase3-barrier-narrow-test",
        "Run the focused Phase 3 barrier helper and raw-pointer boundary packets through a standalone combined build shard",
    );
    step.dependOn(&barrier.step);
    step.dependOn(&narrow.step);
}
