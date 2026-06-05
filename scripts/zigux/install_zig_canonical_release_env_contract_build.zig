const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("install_zig_canonical_release_env_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .root_module = module,
    });

    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step("install-zig-canonical-release-env-contract", "Run the Lane 18 install-zig canonical release environment contract");
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run contract tests");
    test_step.dependOn(&run_tests.step);
}
