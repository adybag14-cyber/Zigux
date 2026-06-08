const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("check_zig_toolchain_min_version_override_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "check-zig-toolchain-min-version-override-contract-tests",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "check-zig-toolchain-min-version-override-contract",
        "Run the Zig toolchain min-version override contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Zig toolchain min-version override contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(contract_step);
}
