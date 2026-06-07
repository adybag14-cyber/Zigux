const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .name = "lane02-phase5-docs-root-sample-packet-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane02_phase5_docs_root_sample_packet_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane02-phase5-docs-root-sample-packet-contract",
        "Run the Lane 02 Phase 5 docs-root sample-packet contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 02 Phase 5 docs-root sample-packet contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
