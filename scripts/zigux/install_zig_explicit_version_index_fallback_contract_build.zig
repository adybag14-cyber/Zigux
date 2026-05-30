const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "install-zig-explicit-version-index-fallback-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("install_zig_explicit_version_index_fallback_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "install-zig-explicit-version-index-fallback-contract",
        "Run the install-zig explicit version index fallback contract tests",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the install-zig explicit version index fallback contract tests");
    test_step.dependOn(&run_tests.step);
}
