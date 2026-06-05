const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to the zigux-bootstrap workflow under the current working directory.",
    ) orelse ".github/workflows/zigux-bootstrap.yml";
    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", workflow_path);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase14_throughput_tail_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addOptions("lane17_phase14_tail_options", options);

    const contract_tests = b.addTest(.{
        .name = "lane17-phase14-throughput-tail-contract-tests",
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane17-phase14-throughput-tail-contract",
        "Run the Lane 17 Phase 14 throughput-tail workflow contract.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 17 Phase 14 throughput-tail workflow contract.");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}
