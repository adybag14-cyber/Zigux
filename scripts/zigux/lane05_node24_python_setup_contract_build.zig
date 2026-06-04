const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_text = std.Io.Dir.cwd().readFileAlloc(
        b.graph.io,
        ".github/workflows/zigux-bootstrap.yml",
        b.allocator,
        .limited(1024 * 1024),
    ) catch @panic("failed to read zigux-bootstrap workflow");
    const options = b.addOptions();
    options.addOption([]const u8, "workflow_text", workflow_text);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane05_node24_python_setup_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addOptions("build_options", options);

    const contract_tests = b.addTest(.{
        .name = "lane05-node24-python-setup-contract-tests",
        .root_module = contract_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "lane05-node24-python-setup-contract",
        "Run the Lane 05 Node24/setup-python workflow contract.",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 05 Node24/setup-python workflow contract.");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(test_step);
}
