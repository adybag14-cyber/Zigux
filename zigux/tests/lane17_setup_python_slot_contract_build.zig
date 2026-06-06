const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to .github/workflows/zigux-bootstrap.yml",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", workflow_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane17_setup_python_slot_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("lane17_setup_python_slot_options", options);

    const tests = b.addTest(.{
        .name = "lane17-setup-python-slot-contract",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "lane17-setup-python-slot-contract",
        "Validate the setup-python slot in the Zigux bootstrap workflow",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 17 setup-python slot contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}
