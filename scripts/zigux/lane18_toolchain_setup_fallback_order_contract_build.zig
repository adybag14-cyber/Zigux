const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane18_toolchain_setup_fallback_order_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract = b.addRunArtifact(contract_tests);
    const contract_step = b.step(
        "lane18-toolchain-setup-fallback-order-contract",
        "Run the Lane 18 pinned Zig setup fallback-order contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Lane 18 fallback-order contract tests");
    test_step.dependOn(&run_contract.step);
}
