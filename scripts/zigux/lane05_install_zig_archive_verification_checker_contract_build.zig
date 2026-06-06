const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane05_install_zig_archive_verification_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane05-install-zig-archive-verification-checker-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_exe = b.addExecutable(.{
        .name = "lane05-install-zig-archive-verification-checker-contract",
        .root_module = contract_module,
    });
    const run_contract_exe = b.addRunArtifact(contract_exe);

    const contract_step = b.step(
        "lane05-install-zig-archive-verification-checker-contract",
        "Run Lane 05 install-zig archive verification checker contract",
    );
    contract_step.dependOn(&run_contract_tests.step);
    contract_step.dependOn(&run_contract_exe.step);

    const test_step = b.step("test", "Run Lane 05 install-zig archive verification checker contract tests");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(contract_step);
}
