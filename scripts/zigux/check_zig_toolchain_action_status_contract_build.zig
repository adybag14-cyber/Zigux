const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const contract_path = "check_zig_toolchain_action_status_contract.zig";

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path(contract_path),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "check-zig-toolchain-action-status-contract",
        "Run the Lane 18 check-zig-toolchain action-status contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 18 check-zig-toolchain action-status contract tests.");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
