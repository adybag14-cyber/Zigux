const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addTest(.{
        .name = "phase1-default-gate-exclusion-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_default_gate_exclusion_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract = b.addRunArtifact(contract);

    const contract_step = b.step(
        "phase1-default-gate-exclusion-contract",
        "Run the Phase 1 default-gate exclusion contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step(
        "test",
        "Run the Phase 1 default-gate exclusion contract",
    );
    test_step.dependOn(&run_contract.step);
}
