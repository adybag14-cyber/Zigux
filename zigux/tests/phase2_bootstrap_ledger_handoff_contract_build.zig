const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase2_bootstrap_ledger_handoff_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase2-bootstrap-ledger-handoff-contract",
        "Run the Lane 25 Phase 2 bootstrap ledger handoff contract.",
    );
    contract_step.dependOn(&run.step);

    const test_step = b.step(
        "test",
        "Run the Lane 25 Phase 2 bootstrap ledger handoff contract tests.",
    );
    test_step.dependOn(&run.step);

    b.default_step.dependOn(&run.step);
}
