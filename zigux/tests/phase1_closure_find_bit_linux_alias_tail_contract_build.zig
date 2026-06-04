const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_closure_find_bit_linux_alias_tail_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase1-closure-find-bit-linux-alias-tail-contract",
        "Run the Phase 1 closure find_bit Linux alias-tail marker contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 1 closure find_bit Linux alias-tail marker contract");
    test_step.dependOn(&run_contract_tests.step);
}
