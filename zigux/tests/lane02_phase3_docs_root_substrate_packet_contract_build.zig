const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane02_phase3_docs_root_substrate_packet_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .root_module = contract_module,
    });

    const run_tests = b.addRunArtifact(contract_tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "lane02-phase3-docs-root-substrate-packet-contract",
        "Run the Lane 02 Phase 3 docs-root substrate packet contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 02 Phase 3 docs-root substrate packet contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
