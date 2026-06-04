const std = @import("std");

fn addHListTailAbiTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("../bindings/hlist_tail_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("notifier_abi", notifier_abi);

    const tests = b.addTest(.{
        .name = "phase3-hlist-tail-abi",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const hlist_tail_abi = addHListTailAbiTest(b, target, optimize);

    const hlist_tail_step = b.step(
        "phase3-hlist-tail-abi",
        "Run the Phase 3 hlist tail ABI binding relay contract",
    );
    hlist_tail_step.dependOn(&hlist_tail_abi.step);

    const test_step = b.step(
        "test",
        "Run the Phase 3 hlist tail ABI binding relay contract",
    );
    test_step.dependOn(&hlist_tail_abi.step);
}
