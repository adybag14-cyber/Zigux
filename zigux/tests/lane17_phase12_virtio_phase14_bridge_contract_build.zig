const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to the zigux-bootstrap workflow",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", workflow_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase12_virtio_phase14_bridge_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("build_options", options);

    const contract_tests = b.addTest(.{
        .name = "lane17-phase12-virtio-phase14-bridge-contract",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "lane17-phase12-virtio-phase14-bridge-contract",
        "Validate the Lane 17 Phase 12 virtio_net to Phase 14 workflow bridge",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 12 virtio_net to Phase 14 workflow bridge contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}
