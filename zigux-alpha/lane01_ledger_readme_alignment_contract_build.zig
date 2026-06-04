const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "lane01-ledger-readme-alignment-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane01_ledger_readme_alignment_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane01-ledger-readme-alignment-contract",
        "Run the Lane 01 bootstrap ledger and README alignment contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 01 ledger/README alignment contract");
    test_step.dependOn(&run_tests.step);
}
