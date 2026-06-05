const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane02_phase13_docs_root_packet_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(contract);
    run_contract.setCwd(b.path("../../"));

    const named = b.step(
        "lane02-phase13-docs-root-packet-contract",
        "Run the Lane 02 Phase 13 docs-root packet contract",
    );
    named.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Lane 02 Phase 13 docs-root packet contract");
    test_step.dependOn(&run_contract.step);
}
