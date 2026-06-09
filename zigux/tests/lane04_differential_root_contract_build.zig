const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane04_differential_root_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const contract_tests = b.addTest(.{
        .name = "lane04-differential-root-contract",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const lane04_step = b.step(
        "lane04-differential-root-contract",
        "Run the Lane 04 differential-test root contract",
    );
    lane04_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 04 differential-test root contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
