const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane03_install_zig_policy_lockstep_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .name = "lane03-install-zig-policy-lockstep-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane03-install-zig-policy-lockstep-contract",
        "Run Lane 03 install-zig policy lockstep contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 03 install-zig policy lockstep contract");
    test_step.dependOn(&run_tests.step);
}
