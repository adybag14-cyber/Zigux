const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("check_zig_toolchain_resolution_order_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "check-zig-toolchain-resolution-order-contract",
        "Validate check-zig-toolchain resolver-order source markers",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run check-zig-toolchain resolver-order contract tests");
    test_step.dependOn(&run_tests.step);
}
