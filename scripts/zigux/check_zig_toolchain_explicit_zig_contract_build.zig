const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("check_zig_toolchain_explicit_zig_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "check-zig-toolchain-explicit-zig-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "check-zig-toolchain-explicit-zig-contract",
        "Run the check-zig-toolchain explicit zig contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the check-zig-toolchain explicit zig contract");
    test_step.dependOn(&run_contract_tests.step);
}
