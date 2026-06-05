const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase2_bootstrap_note_current_packet_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const contract_tests = b.addTest(.{
        .name = "phase2-bootstrap-note-current-packet-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "phase2-bootstrap-note-current-packet-contract",
        "Run the Phase 2 bootstrap note current-packet documentation contract.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 2 bootstrap note current-packet contract tests.");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}
