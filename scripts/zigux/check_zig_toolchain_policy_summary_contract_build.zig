const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("check_zig_toolchain_policy_summary_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(contract);

    const named_step = b.step(
        "check-zig-toolchain-policy-summary-contract",
        "Run the check-zig-toolchain policy summary contract",
    );
    named_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the check-zig-toolchain policy summary contract");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(test_step);
}
