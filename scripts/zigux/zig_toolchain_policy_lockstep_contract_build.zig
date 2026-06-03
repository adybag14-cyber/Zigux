const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("zig_toolchain_policy_lockstep_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const tests = b.addTest(.{
        .name = "zig-toolchain-policy-lockstep-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "zig-toolchain-policy-lockstep-contract",
        "Run the Zigux pinned Zig toolchain policy lockstep contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Zigux pinned Zig toolchain policy lockstep contract.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(contract_step);
}
