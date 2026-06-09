const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane02_phase12_docs_root_release_packet_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "lane02-phase12-docs-root-release-packet-contract-tests",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "lane02-phase12-docs-root-release-packet-contract",
        "Run the Lane 02 Phase 12 docs-root release packet contract.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 02 Phase 12 docs-root release packet contract tests.",
    );
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
