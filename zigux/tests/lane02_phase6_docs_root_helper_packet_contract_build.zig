const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane02_phase6_docs_root_helper_packet_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.skip_foreign_checks = true;

    const contract_step = b.step(
        "lane02-phase6-docs-root-helper-packet-contract",
        "Run the Lane 02 Phase 6 docs-root helper packet contract.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 02 Phase 6 docs-root helper packet contract tests.",
    );
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
