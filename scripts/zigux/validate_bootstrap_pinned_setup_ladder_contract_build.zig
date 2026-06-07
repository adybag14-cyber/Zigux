const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("validate_bootstrap_pinned_setup_ladder_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    const contract_step = b.step("validate-bootstrap-pinned-setup-ladder-contract", "Run the pinned Zig setup ladder contract");
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the pinned Zig setup ladder contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
