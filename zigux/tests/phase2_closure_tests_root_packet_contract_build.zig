const std = @import("std");

fn addContract(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase2_closure_tests_root_packet_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase2-closure-tests-root-packet-contract",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = addContract(b, target, optimize);

    const contract_step = b.step(
        "phase2-closure-tests-root-packet-contract",
        "Run the Phase 2 closure tests-root packet contract",
    );
    contract_step.dependOn(&contract.step);

    const test_step = b.step(
        "test",
        "Run the Phase 2 closure tests-root packet contract",
    );
    test_step.dependOn(&contract.step);
}
