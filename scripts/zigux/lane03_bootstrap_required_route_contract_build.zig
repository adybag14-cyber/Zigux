const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests = b.addTest(.{
        .name = "lane03-bootstrap-required-route-contract-tests",
        .root_module = b.createModule(.{
            .root_source_file = b.path("lane03_bootstrap_required_route_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane03-bootstrap-required-route-contract",
        "Run the Lane 03 bootstrap required-route contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 03 bootstrap required-route contract");
    test_step.dependOn(&run_tests.step);
}
