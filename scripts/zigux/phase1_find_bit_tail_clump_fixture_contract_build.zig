const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_find_bit_tail_clump_fixture_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-find-bit-tail-clump-fixture-contract",
        "Run the Lane 09 find_bit tail-clump fixture contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 09 find_bit tail-clump fixture contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
