const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("install_zig_canonical_release_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "install-zig-canonical-release-contract",
        "Run the install-zig canonical release contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run install-zig canonical release contract tests");
    test_step.dependOn(&run_contract_tests.step);
}
