const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("check_zig_toolchain_archive_allow_missing_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "check-zig-toolchain-archive-allow-missing-contract-tests",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "check-zig-toolchain-archive-allow-missing-contract",
        "Run the Zig toolchain archive allow-missing contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Zig toolchain archive allow-missing contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(contract_step);
}
