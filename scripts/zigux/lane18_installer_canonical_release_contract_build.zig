const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .name = "lane18-installer-canonical-release-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane18_installer_canonical_release_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane18-installer-canonical-release-contract",
        "Run the Lane 18 install-zig canonical release contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 18 install-zig canonical release contract tests.",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
