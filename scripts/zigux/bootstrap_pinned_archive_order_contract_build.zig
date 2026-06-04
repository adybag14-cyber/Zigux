const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "bootstrap-pinned-archive-order-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("bootstrap_pinned_archive_order_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run_tests = b.addRunArtifact(tests);
    run_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "bootstrap-pinned-archive-order-contract",
        "Run the Lane 03 pinned archive setup ordering contract tests",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 03 pinned archive setup ordering contract tests");
    test_step.dependOn(&run_tests.step);
}
