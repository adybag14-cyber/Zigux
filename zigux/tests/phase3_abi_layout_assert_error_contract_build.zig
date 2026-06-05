const std = @import("std");

fn addContractTest(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_layout_assert_error_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "phase3-abi-layout-assert-error-contract",
        .root_module = root_module,
    });
    return b.addRunArtifact(tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const run_contract = addContractTest(b, target, optimize);
    const contract_step = b.step(
        "phase3-abi-layout-assert-error-contract",
        "Run the Phase 3 ABI layout_assert error contract",
    );
    contract_step.dependOn(&run_contract.step);

    const run_tests = addContractTest(b, target, optimize);
    const test_step = b.step("test", "Run the Phase 3 ABI layout_assert error contract tests");
    test_step.dependOn(&run_tests.step);
}
