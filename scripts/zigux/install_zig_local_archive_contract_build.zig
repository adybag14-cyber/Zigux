const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("install_zig_local_archive_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "install-zig-local-archive-contract-tests",
        .root_module = contract_module,
    });

    const run_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "install-zig-local-archive-contract",
        "Validate install-zig local archive install action-path source markers",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run install-zig local archive contract tests");
    test_step.dependOn(&run_tests.step);
}
