const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_docs_root_shared_tooling_packet_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase2-docs-root-shared-tooling-packet-contract",
        "Validate the Phase 2 docs-root shared tooling packet remains aligned with current direct owner surfaces",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 2 docs-root shared tooling packet contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
