const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "install-zig-policy-channel-override-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("install_zig_policy_channel_override_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "install-zig-policy-channel-override-contract",
        "Run the Lane 18 install-zig policy channel override contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 18 install-zig policy channel override contract tests.");
    test_step.dependOn(&run_tests.step);
}
