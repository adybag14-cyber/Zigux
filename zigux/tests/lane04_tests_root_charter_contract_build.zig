const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "lane04-tests-root-charter-contract",
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane04_tests_root_charter_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane04-tests-root-charter-contract",
        "Run the Lane 04 tests-root charter contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 04 tests-root charter contract");
    test_step.dependOn(&run_tests.step);
}
