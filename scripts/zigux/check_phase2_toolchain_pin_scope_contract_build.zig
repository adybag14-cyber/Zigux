const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .name = "check-phase2-toolchain-pin-scope-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("check_phase2_toolchain_pin_scope_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step("check-phase2-toolchain-pin-scope-contract", "Run the Phase 2 toolchain pin-scope source contract");
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 2 toolchain pin-scope source contract");
    test_step.dependOn(&run_contract_tests.step);
}
