const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane05_bootstrap_install_order_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    const run = b.addRunArtifact(tests);
    run.setCwd(b.path("../.."));

    const contract_step = b.step(
        "lane05-bootstrap-install-order-contract",
        "Validate the Lane 05 bootstrap install-order workflow contract",
    );
    contract_step.dependOn(&run.step);

    const test_step = b.step("test", "Run the Lane 05 bootstrap install-order contract");
    test_step.dependOn(&run.step);
}
