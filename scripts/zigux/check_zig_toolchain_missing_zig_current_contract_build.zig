const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .name = "check-zig-toolchain-missing-zig-current-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("check_zig_toolchain_missing_zig_current_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "check-zig-toolchain-missing-zig-current-contract",
        "Run the Lane 03 missing Zig diagnostic contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the default Lane 03 missing Zig diagnostic contract tests");
    test_step.dependOn(&run_contract_tests.step);
}
