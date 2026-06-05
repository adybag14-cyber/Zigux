const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const direct_anchor_gate_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_closure_direct_anchor_manifest_gate_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_direct_anchor_gate_tests = b.addRunArtifact(direct_anchor_gate_tests);

    const contract_step = b.step(
        "phase1-closure-direct-anchor-manifest-gate-contract",
        "Run the Phase 1 closure direct-anchor manifest gate contract",
    );
    contract_step.dependOn(&run_direct_anchor_gate_tests.step);

    const test_step = b.step("test", "Run the Phase 1 closure direct-anchor manifest gate contract");
    test_step.dependOn(&run_direct_anchor_gate_tests.step);
}
