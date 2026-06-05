const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("check_zig_toolchain_policy_archive_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(contract);
    const contract_step = b.step(
        "check-zig-toolchain-policy-archive-contract",
        "Run the Zigux toolchain policy/archive source contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run all tests");
    test_step.dependOn(&run_contract.step);
}
